from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket import TicketStatus
from app.schemas.ticket import TicketCallOut, TicketCreate, TicketOut, TicketStatusUpdate
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketCallOut, status_code=status.HTTP_201_CREATED)
def register_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketCallOut:
    ticket, log = ticket_service.create_ticket(db, payload)
    return TicketCallOut(
        ticket=TicketOut.model_validate(ticket),
        channel=log.channel.value,
        message=log.message,
        success=log.success,
    )


@router.get("", response_model=List[TicketOut])
def list_tickets(
    store_slug: str = Query(default="demo"),
    status_filter: Optional[TicketStatus] = Query(default=None, alias="status"),
    today_only: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> List[TicketOut]:
    tickets = ticket_service.list_tickets(
        db,
        store_slug=store_slug,
        status_filter=status_filter,
        today_only=today_only,
    )
    return [TicketOut.model_validate(t) for t in tickets]


@router.post("/{ticket_id}/call", response_model=TicketCallOut)
def call_ticket(
    ticket_id: int,
    recall: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> TicketCallOut:
    ticket, log = ticket_service.call_ticket(db, ticket_id, recall=recall)
    return TicketCallOut(
        ticket=TicketOut.model_validate(ticket),
        channel=log.channel.value,
        message=log.message,
        success=log.success,
    )


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
) -> TicketOut:
    ticket = ticket_service.update_ticket_status(db, ticket_id, payload.status)
    return TicketOut.model_validate(ticket)
