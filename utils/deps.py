from fastapi import Cookie, Response, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from models.settings import Settings
from typing import Optional
from .database import db, Collections
from models.generic import User


settings = Settings()


async def get_auth_user_middleware(request, call_next):

    session_key = request.cookies.get(settings.session_cookie_name, None)

    msg = ""

    if session_key is None:
        msg = "Sign in required."

        print("Sign in required. ", session_key)

        return RedirectResponse(url="/log-in")

    u = await db[Collections.users].find_one({"uid": session_key})

    if not u:
        msg = "Unauthorized, please sign in."

        print("Unauthorized, please sign in.")

        return RedirectResponse(url="/log-in")

    response = await call_next(request)

    if msg:
        _info = request.cookies.get("info", "")

        _info += f":{msg}"

        response.set_cookie("info", _info)

        response.set_cookie("info", response)

    return response


async def propagate_info(response:  Response, request:  Request, ):

    _info = request.cookies.get("info", "")

    response.set_cookie("info", _info)


async def get_msgs(request:  Request, ):

    _info = request.cookies.get("info", None)

    if _info:
        return _info.split(":")

    return []


async def get_auth_user(response:  Response, request:  Request,  session_key: Optional[str] = Cookie(default=None, alias=settings.session_cookie_name)):
    msg = ""

    if session_key is None:
        msg = "Sign in required."
        return None

    u = await db[Collections.users].find_one({"uid": session_key})

    if not u:
        msg = "Unauthorized, please sign in."

        return None

    if msg:
        _info = request.cookies.get("info", "")

        _info += f":{msg}"

        response.set_cookie("info", _info)

        response.set_cookie("info", response)

    return User(**u)


async def get_admin_user(response:  Response, request:  Request,  session_key: Optional[str] = Cookie(default=None, alias=settings.session_cookie_name)):
    msg = ""

    if session_key is None:
        msg = "Sign in required."
        return None

    u = await db[Collections.users].find_one({"uid": session_key})

    if not u:
        msg = "Unauthorized, please sign in."

        return None

    if msg:
        _info = request.cookies.get("info", "")

        _info += f":{msg}"

        response.set_cookie("info", _info)

        response.set_cookie("info", response)

    if not u["is_admin"]:
        msg = "You are not authorized to access this resource."

        return None

    return User(**u)


def enforce_is_admin(auth=Depends(get_auth_user)):

    if auth is None:
        return None

    user, _ = auth

    if not user.is_admin:
        raise HTTPException(
            401, "You are not authorized to access this resource.")

    return auth
