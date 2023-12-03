from fastapi import APIRouter, Request, HTTPException, Response, Depends
from fastapi.responses import RedirectResponse
from models.generic import *
from utils.security import hash_password
from utils.database import db, Collections
from models.settings import Settings
from utils.deps import get_auth_user
from models.admin import UserOTP

from utils.render_template import template_to_response

settings = Settings()
router = APIRouter()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@router.get("/")
async def index(request: Request):

    return RedirectResponse(url=request.url_for("dashboard"))


@router.get("/log-in")
async def log_in(request: Request):
    return await template_to_response("login.html", {"request": request})


@router.post("/log-in")
async def log_in_post(body:  LogInModel, response:  Response):

    user = await db[Collections.users].find_one({"email": body.email})

    if not user:
        raise HTTPException(
            status_code=400,
            detail="User with that email does not exist",
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=400,
            detail="User with that email is not active",
        )

    if not user["password_hash"] == hash_password(body.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials",
        )

    await db[Collections.users].update_one({"uid": user["uid"]}, {"$set": {"last_login": get_utc_timestamp()}})

    response.set_cookie(settings.session_cookie_name,
                        user["uid"], max_age=1800)

    return


@router.get("/sign-up")
async def sign_up(request: Request):

    request.cookies.clear()

    return await template_to_response("signup.html", {"request": request})


@router.post("/sign-up")
async def sign_up_post(request: Request, body:  UserIn):

    exists = await db[Collections.users].find_one({"email": body.email})

    if exists:
        raise HTTPException(
            status_code=400,
            detail="User with that email already exists",
        )

    if not body.password == body.password2:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )

    new_user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
    )

    await db[Collections.users].insert_one(new_user.model_dump())


@router.get("/dashboard")
async def dashboard(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("dashboard.html", {"request": request, "user": user})


@router.get("/history")
async def history(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("history.html", {"request": request, "user": user})


@router.get("/account")
async def account(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("account.html", {"request": request, "user": user})


@router.get("/logout")
async def logout(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("logout.html", {"request": request, "user": user})


@router.get("/logout/now")
async def logout_now(request: Request, response: Response, user:  User = Depends(get_auth_user)):

    request.cookies.clear()

    response.delete_cookie(settings.session_cookie_name)

    return await template_to_response("login.html", {"request": request, "user": user})


@router.get("/settings")
async def settings_endpoint(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("settings.html", {"request": request, "user": user})


@router.get("/transfer")
async def transfer(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("transfer.html", {"request": request, "user": user})


@router.post("/transfer/internal")
async def internal_transfer(request: Request, body:  InternalTransfer, user:  User = Depends(get_auth_user),):

    if body.account_number == user.account_number:
        raise HTTPException(
            status_code=400,
            detail="You cannot transfer to yourself",
        )

    if body.amount > user.balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds",
        )

    if body.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount",
        )

    if not is_number(body.account_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid account number",
        )

    user_with_acct = await db[Collections.users].find_one({"account_number": body.account_number})

    if not user_with_acct:
        raise HTTPException(
            status_code=400,
            detail="Invalid account number",
        )

    otp = await db[Collections.otps].find_one({
        "user": user.email,
        "is_valid": True,
        "otp": body.pin
    })

    if not otp:

        raise HTTPException(
            status_code=400,
            detail="Invalid authorization PIN",
        )

    await db[Collections.otps].delete_one({"otp": body.pin, "user":  user.email})

    # await db[Collections.users].update_one({"uid": user.uid}, {"$inc": {"balance": -body.amount, "ledger_balance": -body.amount}})

    # await db[Collections.users].update_one({"uid": user_with_acct["uid"]}, {"$inc": {"balance": body.amount, "ledger_balance": body.amount}})

    await db[Collections.transactions].insert_one(TX(
        user=user.uid,
        user_name=user.get_full_name(),
        amount=body.amount,
        type=TxTypes.debit,
        category=TxCategory.transfer,
        description=f"Transfer to {user_with_acct['account_number']}",
        created=get_utc_timestamp(),
        data=body
    ).model_dump())

    await db[Collections.transactions].insert_one(TX(
        user=user_with_acct["uid"],
        user_name=user_with_acct["first_name"],
        user_email=user.email,
        amount=body.amount,
        type=TxTypes.credit,
        category=TxCategory.received,
        description=f"Transfer from {user.account_number}",
        created=get_utc_timestamp(),
    ).model_dump())

    return await template_to_response("transfer.html", {"request": request, "user": user})


@router.post("/transfer/external")
async def external_transfer(request: Request, body:  ExternalTransfer, user:  User = Depends(get_auth_user),):

    if body.amount > user.balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds",
        )

    if body.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount",
        )

    if body.method == TransferMethods.bank and not (body.iban and body.swift and body.account_number):

        if not is_number(body.account_number):
            raise HTTPException(
                status_code=400,
                detail="Invalid account number",
            )

        raise HTTPException(
            status_code=400,
            detail="Invalid bank details",
        )

    if body.method == TransferMethods.paypal and not body.paypal_email:

        raise HTTPException(
            status_code=400,
            detail="Invalid paypal details",
        )

    if body.method == TransferMethods.bitcoin and not body.bitcoin_address:

        raise HTTPException(
            status_code=400,
            detail="Invalid bitcoin details",
        )

    if body.method == TransferMethods.cashapp and not body.tag:

        raise HTTPException(
            status_code=400,
            detail="Invalid cashapp details",
        )

    otp = await db[Collections.otps].find_one({
        "user": user.email,
        "is_valid": True,
        "otp": body.pin
    })

    if not otp:

        raise HTTPException(
            status_code=400,
            detail="Invalid authorization PIN",
        )

    await db[Collections.otps].delete_one({"otp": body.pin, "user":  user.email})

    # await db[Collections.users].update_one({"uid": user.uid}, {"$inc": {"balance": -body.amount, "ledger_balance": -body.amount}})

    await db[Collections.transactions].insert_one(TX(
        user=user.uid,
        user_name=user.get_full_name(),
        user_email=user.email,
        amount=body.amount,
        type=TxTypes.debit,
        category=TxCategory.transfer,
        description=f"Transfer to {body.method}",
        created=get_utc_timestamp(),
        data=body
    ).model_dump())

    return await template_to_response("transfer.html", {"request": request, "user": user})


@router.get("/transactions")
async def transactions(request: Request, user:  User = Depends(get_auth_user)):
    return await template_to_response("transactions.html", {"request": request, "user": user})


@router.get("/profile/edit")
async def edit_profile(request: Request,  user:  User = Depends(get_auth_user)):
    return await template_to_response("edit-profile.html", {"request": request, "user": user})


@router.post("/profile/edit")
async def edit_profile_post(request: Request, body: UserUpdate,  user:  User = Depends(get_auth_user)):

    await db[Collections.users].update_one({"uid": user.uid}, {"$set": {"first_name": body.first_name, "last_name": body.last_name}})

    return await template_to_response("settings.html", {"request": request, "user": user})


@router.get("/forgot-password")
async def forgot_password(request: Request):
    return await template_to_response("forgot-password.html", {"request": request})


@router.get("/change-password")
async def change_password(request: Request,  user:  User = Depends(get_auth_user)):
    return await template_to_response("change-password.html", {"request": request, "user": user})


@router.post("/change-password")
async def change_password_post(request: Request, body: ChangePasswordModel, user:  User = Depends(get_auth_user)):

    if not user.password_hash == hash_password(body.current_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password",
        )

    if not body.password1 == body.password2:

        raise HTTPException(
            status_code=400,
            detail="New passwords must match!",
        )

    await db[Collections.users].update_one({
        "uid": user.uid
    }, {
        "$set": {
            "password_hash":  hash_password(body.password1)
        }
    })

    return await template_to_response("change-password.html", {"request": request, "user": user})
