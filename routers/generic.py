from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from utils.render_template import template_to_response

router = APIRouter()


@router.get("/")
async def index(request: Request):

    return RedirectResponse(url=request.url_for("dashboard"))


@router.get("/log-in")
async def log_in(request: Request):
    return template_to_response("login.html", {"request": request})


@router.get("/dashboard")
async def dashboard(request: Request):
    return template_to_response("dashboard.html", {"request": request})


@router.get("/history")
async def history(request: Request):
    return template_to_response("history.html", {"request": request})


@router.get("/account")
async def account(request: Request):
    return template_to_response("account.html", {"request": request})


@router.get("/logout")
async def logout(request: Request):
    return template_to_response("logout.html", {"request": request})


@router.get("/settings")
async def settings(request: Request):
    return template_to_response("settings.html", {"request": request})


@router.get("/transfer")
async def history(request: Request):
    return template_to_response("transfer.html", {"request": request})


@router.get("/transactions")
async def transactions(request: Request):
    return template_to_response("transactions.html", {"request": request})


@router.get("/profile/edit")
async def edit_profile(request: Request):
    return template_to_response("edit-profile.html", {"request": request})


@router.get("/forgot-password")
async def forgot_password(request: Request):
    return template_to_response("forgot-password.html", {"request": request})


@router.get("/change-password")
async def change_password(request: Request):
    return template_to_response("change-password.html", {"request": request})
