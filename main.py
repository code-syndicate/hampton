from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models.settings import Settings
from routers.generic import router as generic_router


settings = Settings()


app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,

)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(generic_router, tags=["Generic"], )


app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )
