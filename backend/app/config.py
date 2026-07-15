from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Wait Call API"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Railway: MYSQL* 연결 시 자동 조립. 직접 넣으려면 DATABASE_URL 사용.
    database_url: str = ""
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
