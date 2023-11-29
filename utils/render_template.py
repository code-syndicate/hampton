from fastapi.templating import Jinja2Templates
from models.settings import Settings

settings = Settings()
templates = Jinja2Templates(directory="templates",  autoescape=True,)


def template_to_response(template_name: str, context: dict = {}):

    context.update({"settings": settings})

    return templates.TemplateResponse(template_name, context)
