from fastapi.templating import Jinja2Templates
from models.settings import Settings
from utils.database import db, Collections
from models.generic import TX

settings = Settings()
templates = Jinja2Templates(directory="templates",  autoescape=True,)


async def template_to_response(template_name: str, context: dict = {}):

    context.update({"settings": settings})

    if "user" in context.keys():

        txs = await db[Collections.transactions].find({
            "user":  context["user"].uid
        }).sort("created", -1).to_list(None)

        txs = [TX(**tx) for tx in txs]

        context.update({
            "txs":  txs
        })

    return templates.TemplateResponse(template_name, context)
