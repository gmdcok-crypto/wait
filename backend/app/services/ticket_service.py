from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.notify import get_notifier
from app.models.call_log import CallLog, NotifyKind
from app.models.store import Store
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate


def _today() -> str:
    return date.today().isoformat()


def get_store_by_slug(db: Session, slug: str) -> Store:
    store = db.scalar(select(Store).where(Store.slug == slug))
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="매장을 찾을 수 없습니다")
    return store


def next_waiting_number(db: Session, store_id: int, service_date: str) -> int:
    current = db.scalar(
        select(func.max(Ticket.number)).where(
            Ticket.store_id == store_id,
            Ticket.service_date == service_date,
        )
    )
    return (current or 0) + 1


def create_ticket(db: Session, payload: TicketCreate) -> Tuple[Ticket, CallLog]:
    store = get_store_by_slug(db, payload.store_slug)
    service_date = _today()
    number = next_waiting_number(db, store.id, service_date)

    ticket = Ticket(
        store_id=store.id,
        number=number,
        phone=payload.phone,
        party_size=payload.party_size,
        status=TicketStatus.waiting,
        service_date=service_date,
    )
    db.add(ticket)
    db.flush()

    notifier = get_notifier()
    result = notifier.send_waiting(ticket.phone, store.name, ticket.number)
    log = CallLog(
        ticket_id=ticket.id,
        kind=NotifyKind.waiting,
        channel=result.channel,
        success=result.success,
        message=result.message,
        provider_ref=result.provider_ref,
    )
    db.add(log)
    db.commit()
    db.refresh(ticket)
    return ticket, log


def list_tickets(
    db: Session,
    store_slug: str,
    status_filter: Optional[TicketStatus] = None,
    today_only: bool = True,
) -> List[Ticket]:
    store = get_store_by_slug(db, store_slug)
    stmt = select(Ticket).where(Ticket.store_id == store.id)
    if today_only:
        stmt = stmt.where(Ticket.service_date == _today())
    if status_filter:
        stmt = stmt.where(Ticket.status == status_filter)
    stmt = stmt.order_by(Ticket.number.asc())
    return list(db.scalars(stmt).all())


def call_ticket(db: Session, ticket_id: int, recall: bool = False) -> Tuple[Ticket, CallLog]:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="대기표를 찾을 수 없습니다")

    if ticket.status in (TicketStatus.completed, TicketStatus.cancelled):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="호출할 수 없는 상태입니다")

    store = db.get(Store, ticket.store_id)
    assert store is not None

    ticket.status = TicketStatus.called
    ticket.called_at = datetime.utcnow()

    notifier = get_notifier()
    result = notifier.send_call(ticket.phone, store.name, ticket.number, recall=recall)
    log = CallLog(
        ticket_id=ticket.id,
        kind=NotifyKind.recall if recall else NotifyKind.call,
        channel=result.channel,
        success=result.success,
        message=result.message,
        provider_ref=result.provider_ref,
    )
    db.add(log)
    db.commit()
    db.refresh(ticket)
    return ticket, log


def update_ticket_status(db: Session, ticket_id: int, new_status: TicketStatus) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="대기표를 찾을 수 없습니다")

    allowed = {
        TicketStatus.waiting,
        TicketStatus.called,
        TicketStatus.completed,
        TicketStatus.no_show,
        TicketStatus.cancelled,
    }
    if new_status not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 상태입니다")

    ticket.status = new_status
    if new_status in (TicketStatus.completed, TicketStatus.no_show, TicketStatus.cancelled):
        ticket.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket
