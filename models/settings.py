from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug:  bool = True
    app_name:  str = "Hampton Credit Union"
    db_name: str = "hamon_credit_nion"
    allowed_origins: list[HttpUrl] = ["http://127.0.0.1:7004"]
    base_url: str = "http://localhost:8002"
    db_url: str = "mongodb://localhost:4000"
    db_username: str = "default"
    db_password: str = "root"
    password_salt: str = "iamasalt"
    mail_username: str = "HamptonCreditUnion"
    mail_password: str = "mail_pass"
    mail_from: str = "HamptonCreditUnionteam@HamptonCreditUnion.com"
    mail_port: int = 587
    mail_server:  str = "https://mail.com"
    mail_starttls: bool = False
    mail_ssl_tls:  bool = True
    mail_display_name: str = "HamptonCreditUnion"
    mail_domain:  str = "https://mail.com"
    mail_domain_username:  str = "admin"
    totp_length: int = 6
    totp_time_step: int = 2
    jwt_secret_key: str = "jwtsecretkey"
    jwt_access_token_expiration_hours: int = 1
    per_page: int = 5
    session_cookie_name: str = "hampton-credit-union-session"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
