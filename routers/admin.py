from fastapi import APIRouter, Request, HTTPException, Response, Depends, Query
from typing import Union
from fastapi.responses import RedirectResponse
from models.generic import *
from models.admin import *
from utils.security import hash_password
from utils.database import db, Collections
from models.settings import Settings
from utils.deps import get_auth_user, get_admin_user
import math

from utils.render_template import template_to_response

settings = Settings()
router = APIRouter(
    prefix="/admin", dependencies=[Depends(get_auth_user), Depends(get_admin_user)])


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@router.get("/overview")
async def overview(request: Request, user:  User = Depends(get_admin_user), view: str = Query(alias="ui", default="main"), page:  Union[int, None] = Query(default=1)):

    views = ["main", "overview", "users",
             "transfers", "transactions", "settings"]

    if not view.lower() in views:
        view = views[0]

    l_users = await db[Collections.users].count_documents({})
    l_txs = await db[Collections.transactions].count_documents({})

    # print(l_users, l_txs)

    max_users_pages = math.ceil(l_users / settings.per_page)
    max_tx_pages = math.ceil(l_txs / settings.per_page)

    start, stop = 0, 0

    if view == "users":
        page = min(max_users_pages, page)
        start = (settings.per_page * page) - settings.per_page
        stop = start + settings.per_page

    if view == "transfers":
        page = min(max_tx_pages, page)
        start = (settings.per_page * page) - settings.per_page
        stop = start + settings.per_page

    # get all users
    users = await db[Collections.users].find({}).sort("email", -1).skip(start).to_list(length=settings.per_page)

    # get all transfers
    transfers = await db[Collections.transactions].find({}).sort("created", -1).skip(start).to_list(length=settings.per_page)

    return await template_to_response("admin/overview.html", {"dt":  datetime.now(),  "users": users, "transfers": transfers, "settings":  settings, "ui": view, "user": user, "request":  request, "up": [x for x in range(1, max_users_pages + 1)], "tp": [x for x in range(1, max_tx_pages + 1)], "page": page, "lup": max_users_pages, "ltp": max_tx_pages})


@router.post("/update-user")
async def update_user_data(form: UpdateUserModel, user:  User = Depends(get_admin_user)):
    data = form.model_dump()

    # get a user
    p_user = await db[Collections.users].find_one({"uid": form.uid})

    p_user.update(data)

    updated_user = User(**p_user)

    await db[Collections.users].update_one({"uid": form.uid}, {"$set": updated_user.model_dump()})


@router.post("/delete-user")
async def delete_user(form: DeleteUserModel, user:  User = Depends(get_admin_user)):

    # delete user
    await db[Collections.users].delete_one({"email": form.email})


@router.post("/otps/{uid}")
async def add_otp(uid: str, user:  User = Depends(get_admin_user)):

    my_user = await db[Collections.users].find_one({"uid": uid})

    if my_user is None:
        raise HTTPException(401, "User not found")

    new_otp = UserOTP(user=my_user["email"])

    await db[Collections.otps].insert_one(new_otp.model_dump())

    return new_otp


@router.get("/otps/{uid}")
async def get_otp(uid: str, user:  User = Depends(get_admin_user)):

    my_user = await db[Collections.users].find_one({"uid": uid})

    if my_user is None:
        raise HTTPException(401, "User not found")

    otps = await db[Collections.otps].find({"user": my_user["email"], "is_valid": True}).to_list(length=None)
    _l = []
    for p in otps:
        _l.append({
            "otp": p["otp"],
            "is_valid": p["is_valid"]
        })

    return _l


@router.post("/delete-tx")
async def delete_tx(form: TickTxModel, user:  User = Depends(get_admin_user)):

    await db[Collections.transactions].delete_one({"uid": form.tx_id})


@router.post("/update-tx")
async def update_tx(form: UpdateTxModel, user:  User = Depends(get_admin_user)):

    tx = await db[Collections.transactions].find_one({"uid": form.tx_id})

    update = form.model_dump(exclude_unset=True, exclude_none=True, )

    if form.created:
        ts = datetime.fromisoformat(
            form.created).timestamp()

        update.update({"created": ts})

    else:
        update = form.model_dump(exclude={"created", })

    tx.update(update)

    if tx is None:
        raise HTTPException(401, "Record not found")

    await db[Collections.transactions].update_one({"uid": form.tx_id}, {"$set": tx})


@router.post("/tick-tx")
async def tick_tx(form: TickTxModel, user:  User = Depends(get_admin_user)):

    tx = await db[Collections.transactions].find_one({"uid": form.tx_id})

    if tx is None:
        raise HTTPException(401, "Record not found")

    await db[Collections.transactions].update_one({"uid": form.tx_id}, {"$set":  {"approved": True, }})
