from fastapi.templating import Jinja2Templates
from models.settings import Settings
from utils.database import db, Collections

settings = Settings()
templates = Jinja2Templates(directory="templates",  autoescape=True,)


async def template_to_response(template_name: str, context: dict = {}):

    context.update({"settings": settings})

    if "user" in context.keys():

        txs = await db[Collections.transactions].find({
            "user":  context["user"].uid
        }).to_list(None)

        context.update({
            "txs":  txs
        })

    return templates.TemplateResponse(template_name, context)
