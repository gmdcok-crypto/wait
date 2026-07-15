import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api import stores, tickets
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import CallLog, Store, Ticket  # noqa: F401 — register metadata

logging.basicConfig(level=logging.INFO)
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
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_default_store()
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
