from pydantic import BaseModel, Field, EmailStr
from pydantic_settings import SettingsConfigDict
from utils.security import get_uuid4, gen_acct_number, get_utc_timestamp, gen_otp
from .generic import TxCategory, TxTypes


class DeleteUserModel(BaseModel):
    email: EmailStr


class UpdateUserModel(BaseModel):
    uid: str
    balance: float
    ledger_balance: float = Field(alias="ledgerBalance")
    credit_balance: float = Field(alias="creditBalance")
    reward_balance: float = Field(alias="rewardBalance")

    model_config = SettingsConfigDict(populate_by_name=True)


class UserOTP(BaseModel):
    uid: str = Field(default_factory=get_uuid4)
    user: EmailStr
    otp: str = Field(default_factory=gen_otp)
    is_valid:  bool = True


class TickTxModel(BaseModel):
    tx_id: str = Field(alias="txId")


class UpdateTxModel(BaseModel):
    tx_id: str = Field(alias="txId")
    amount:  float
    created: str | None = Field(default=None, alias="created")
    txtype: TxTypes
    category:  TxCategory

    model_config = SettingsConfigDict(populate_by_name=True)
