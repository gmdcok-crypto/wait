import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotifyChannel(str, enum.Enum):
    kakao = "kakao"
    sms = "sms"
    console = "console"


class NotifyKind(str, enum.Enum):
    waiting = "waiting"
    call = "call"
    recall = "recall"


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
    kind: Mapped[NotifyKind] = mapped_column(Enum(NotifyKind), nullable=False)
    channel: Mapped[NotifyChannel] = mapped_column(Enum(NotifyChannel), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    provider_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    ticket = relationship("Ticket", back_populates="call_logs")
