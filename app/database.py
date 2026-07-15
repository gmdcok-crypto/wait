from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

if not settings.database_url:
    raise RuntimeError(
        "DATABASE_URL / MYSQL_URL / MYSQL* 환경변수가 없습니다. "
        "Railway에서 MySQL 서비스를 이 API 서비스에 Variable Reference로 연결하세요."
    )

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=280,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
