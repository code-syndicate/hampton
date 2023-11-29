from fastapi import APIRouter, Request

from utils.render_template import template_to_response

router = APIRouter()


@router.get("/")
async def index(request: Request):
    return template_to_response("index.html", {"request": request})


@router.get("/log-in")
async def log_in(request: Request):
    return template_to_response("login.html", {"request": request})


@router.get("/dashboard")
async def dashboard(request: Request):
    return template_to_response("dashboard.html", {"request": request})


@router.get("/history")
async def history(request: Request):
    return template_to_response("history.html", {"request": request})
