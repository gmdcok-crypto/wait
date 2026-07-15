import logging
import threading
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

_db_ready = False
_db_error: Optional[str] = None


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


def init_db(retries: int = 30, delay_sec: float = 2.0) -> None:
    global _db_ready, _db_error
    last_error: Optional[Exception] = None
    logger.info("Connecting database host=%s", settings.database_host)
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            seed_default_store()
            _db_ready = True
            _db_error = None
            logger.info("Database ready (attempt %s)", attempt)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            _db_error = str(exc)
            logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                retries,
                exc,
            )
            time.sleep(delay_sec)
    logger.error("Database connection failed after retries: %s", last_error)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Listen for healthchecks immediately; init DB in background.
    thread = threading.Thread(target=init_db, daemon=True)
    thread.start()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stores.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")


@app.get("/health")
def health() -> Dict[str, str]:
    # Process liveness for Railway network healthcheck
    return {"status": "ok"}


@app.get("/ready")
def ready() -> Dict[str, object]:
    return {
        "ready": _db_ready,
        "db_host": settings.database_host,
        "error": _db_error,
    }


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }
