from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.ticket import TicketStatus


class TicketCreate(BaseModel):
    store_slug: str = "demo"
    phone: str = Field(min_length=10, max_length=20)
    party_size: int = Field(default=1, ge=1, le=50)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) < 10:
            raise ValueError("유효한 전화번호를 입력하세요")
        return digits


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    number: int
    phone: str
    party_size: int
    status: TicketStatus
    service_date: str
    created_at: datetime
    called_at: Optional[datetime]
    completed_at: Optional[datetime]


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketCallOut(BaseModel):
    ticket: TicketOut
    channel: str
    message: str
    success: bool
