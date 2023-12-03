from pydantic import BaseModel, Field, EmailStr
from pydantic_settings import SettingsConfigDict
from utils.security import get_uuid4, gen_acct_number, get_utc_timestamp
from enum import StrEnum
from datetime import datetime


class TxTypes(StrEnum):
    credit = "credit"
    debit = "debit"


class TxCategory(StrEnum):
    received = "received"
    transfer = "transfer"


class UserIn(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, alias="firstName")
    last_name: str = Field(min_length=2, max_length=50, alias="lastName")
    email:  EmailStr
    password: str
    password2: str


class User(BaseModel):
    uid: str = Field(default_factory=get_uuid4)
    email: EmailStr
    password_hash: str = Field(min_length=8, alias="passwordHash")
    first_name: str = Field(min_length=2, max_length=50, alias="firstName")
    last_name: str = Field(min_length=2, max_length=50, alias="lastName")
    is_active: bool = Field(default=True, alias="isActive")
    is_admin: bool = Field(default=False, alias="isAdmin")
    account_number: str = Field(
        default_factory=gen_acct_number, alias="accountNumber")
    balance: float = Field(default=0, alias="balance")
    ledger_balance: float = Field(default=0, alias="ledgerBalance")
    credit_balance: float = Field(default=0, alias="creditBalance")
    reward_balance: float = Field(default=0, alias="rewardBalance")
    created:  float = Field(default_factory=get_utc_timestamp)
    last_login:  float = Field(default_factory=get_utc_timestamp)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_joined(self):
        return datetime.fromtimestamp(self.created).strftime("%d %B %Y, %H:%M")

    def get_last_login(self):
        return datetime.fromtimestamp(self.last_login).strftime("%d %B %Y, %H:%M")

    model_config = SettingsConfigDict(populate_by_name=True)


class ChangePasswordModel(BaseModel):
    current_password:  str
    password1:  str
    password2:  str


class LogInModel(BaseModel):
    email: EmailStr
    password: str


class InternalTransfer(BaseModel):
    account_number:  str = Field(min_length=10)
    amount:  float
    description:  str | None = None
    pin: str = Field(min_length=3)
    approved: bool = False

    model_config = SettingsConfigDict(populate_by_name=True)


class TransferMethods(StrEnum):
    bank = "bank"
    cashapp = "cashapp"
    paypal = "paypal"
    bitcoin = "bitcoin"


class ExternalTransfer(BaseModel):
    method: TransferMethods
    account_number:  str | None = None
    swift:  str | None = None
    iban:  str | None = None
    tag:  str | None = None
    paypal_email:  EmailStr | None = None
    bitcoin_address:  str | None = None
    amount:  float = Field(gt=0)
    description:  str | None = None
    pin: str = Field(min_length=3)
    approved: bool = False

    model_config = SettingsConfigDict(populate_by_name=True)


class TX(BaseModel):
    uid:  str = Field(default_factory=get_uuid4)
    created:  float = Field(default_factory=get_utc_timestamp)
    user:  str = Field(min_length=8)
    user_email:  EmailStr | None = Field(default=None)
    user_name:  str = Field(min_length=3)
    description: str | None = Field(min_length=3, default=None)
    amount:  float = Field(gt=0)
    type:  TxTypes
    category: TxCategory
    data: InternalTransfer | ExternalTransfer | None = None

    def get_email(self):
        return self.user_email or "N/A"

    def format_date_in_words(self):

        return datetime.fromtimestamp(self.created).strftime("%d %B %Y")

    def format_date_and_time_in_words(self):
        return datetime.fromtimestamp(self.created).strftime("%d %B %Y, %H:%M")


class UserUpdate(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, alias="firstName")
    last_name: str = Field(min_length=2, max_length=50, alias="lastName")

    model_config = SettingsConfigDict(populate_by_name=True)
