from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus, urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_mysql_url(url: str) -> str:
    url = (url or "").strip().strip('"').strip("'")
    if not url:
        return ""
    if url.startswith("mysql://"):
        return "mysql+pymysql://" + url[len("mysql://") :]
    if url.startswith("mysql+pymysql://"):
        return url
    return url


def _safe_db_host(url: str) -> str:
    try:
        return urlparse(url.replace("mysql+pymysql://", "mysql://", 1)).hostname or "?"
    except Exception:
        return "?"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Wait Call API"
    debug: bool = False
    cors_origins: str = "*"

    database_url: str = ""
    mysql_url: Optional[str] = None
    # Railway common keys (with/without underscores)
    mysqlhost: Optional[str] = None
    mysql_host: Optional[str] = None
    mysqlport: Optional[str] = None
    mysql_port: Optional[str] = None
    mysqluser: Optional[str] = None
    mysql_user: Optional[str] = None
    mysqlpassword: Optional[str] = None
    mysql_password: Optional[str] = None
    mysqldatabase: Optional[str] = None
    mysql_database: Optional[str] = None

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

        host = self.mysqlhost or self.mysql_host
        user = self.mysqluser or self.mysql_user
        password = self.mysqlpassword if self.mysqlpassword is not None else self.mysql_password
        db = self.mysqldatabase or self.mysql_database
        port = self.mysqlport or self.mysql_port or "3306"

        if host and user and db:
            self.database_url = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
                user=quote_plus(user),
                password=quote_plus(password or ""),
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

    @property
    def database_host(self) -> str:
        return _safe_db_host(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
