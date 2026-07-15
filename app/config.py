from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_mysql_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    # Railway/MySQL plugins often give mysql:// — SQLAlchemy needs a driver.
    if url.startswith("mysql://"):
        return "mysql+pymysql://" + url[len("mysql://") :]
    if url.startswith("mysql+pymysql://"):
        return url
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Wait Call API"
    debug: bool = False
    cors_origins: str = "*"

    # Prefer DATABASE_URL / MYSQL_URL; else assemble from MYSQL*
    database_url: str = ""
    mysql_url: Optional[str] = None
    mysqlhost: Optional[str] = None
    mysqlport: Optional[str] = None
    mysqluser: Optional[str] = None
    mysqlpassword: Optional[str] = None
    mysqldatabase: Optional[str] = None

    # console | kakao_sms
    notify_mode: str = "console"

    kakao_api_key: str = ""
    kakao_sender_key: str = ""
    kakao_template_waiting: str = "WAITING_REGISTERED"
    kakao_template_call: str = "CALL_CUSTOMER"

    sms_api_key: str = ""
    sms_api_secret: str = ""
    sms_from: str = ""

    default_store_name: str = "데모 매장"
    default_store_slug: str = "demo"

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        if self.database_url:
            self.database_url = _normalize_mysql_url(self.database_url)
            return self

        if self.mysql_url:
            self.database_url = _normalize_mysql_url(self.mysql_url)
            return self

        if self.mysqlhost and self.mysqluser and self.mysqldatabase:
            password = quote_plus(self.mysqlpassword or "")
            user = quote_plus(self.mysqluser)
            host = self.mysqlhost
            port = self.mysqlport or "3306"
            db = self.mysqldatabase
            self.database_url = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
                user=user,
                password=password,
                host=host,
                port=port,
                db=db,
            )
        return self

    @field_validator("notify_mode")
    @classmethod
    def validate_notify_mode(cls, v: str) -> str:
        allowed = {"console", "kakao_sms"}
        if v not in allowed:
            raise ValueError("notify_mode must be one of {0}".format(allowed))
        return v

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
