from enum import Enum
from models.settings import Settings
import motor.motor_asyncio

settings = Settings()


class Collections(str, Enum):
    users = "users"
    transactions = "transactions"
    otps = "otps"
    password_reset_stores = "password_reset_stores"


client = motor.motor_asyncio.AsyncIOMotorClient(settings.db_url)

db = client[settings.db_name]
