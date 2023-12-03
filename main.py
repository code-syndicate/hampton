from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models.settings import Settings
from routers.generic import router as generic_router
from utils.deps import get_auth_user_middleware


settings = Settings()


app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,

)


@app.middleware("http")
async def auth_checker(request: Request, call_next):

    auth_urls = [
        "/dashboard",
        "/account",
        "/transactions",
        "/history",
        "/transfer",
        "/transfer/internal",
        "/transfer/external",
        "/settings",
        "/log-out",
        "/logout/now",
        "/profile/edit",
        "/change-password"

    ]

    if request.url.path in auth_urls:
        return await get_auth_user_middleware(request, call_next)

    return await call_next(request)


app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(generic_router, tags=["Generic"], )


app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )
