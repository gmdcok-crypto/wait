import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from app.api import stores, tickets
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import CallLog, Store, Ticket  # noqa: F401 — register metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wait")
settings = get_settings()


def seed_default_store() -> None:
    db = SessionLocal()
    try:
        exists = db.scalar(select(Store).where(Store.slug == settings.default_store_slug))
        if not exists:
            db.add(
                Store(
                    name=settings.default_store_name,
                    slug=settings.default_store_slug,
                )
            )
            db.commit()
            logger.info("Seeded default store slug=%s", settings.default_store_slug)
    finally:
        db.close()


def init_db(retries: int = 15, delay_sec: float = 2.0) -> None:
    last_error = None  # type: Optional[Exception]
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            seed_default_store()
            logger.info("Database ready (attempt %s)", attempt)
            return
        except Exception as exc:  # noqa: BLE001 — startup retry
            last_error = exc
            logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                retries,
                exc,
            )
            time.sleep(delay_sec)
    raise RuntimeError("Database connection failed after retries: {0}".format(last_error))


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stores.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }
