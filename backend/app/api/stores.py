from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreOut

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db)) -> List[Store]:
    return list(db.scalars(select(Store).order_by(Store.id.asc())).all())


@router.get("/{slug}", response_model=StoreOut)
def get_store(slug: str, db: Session = Depends(get_db)) -> Store:
    store = db.scalar(select(Store).where(Store.slug == slug))
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="매장을 찾을 수 없습니다")
    return store


@router.post("", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
def create_store(payload: StoreCreate, db: Session = Depends(get_db)) -> Store:
    exists = db.scalar(select(Store).where(Store.slug == payload.slug))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 slug입니다")
    store = Store(name=payload.name, slug=payload.slug)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store
