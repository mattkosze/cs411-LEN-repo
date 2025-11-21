from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import schemas
from ..services import crisis_service

#router for specifically a crisis
router = APIRouter()

@router.post("/escalate", response_model=schemas.CrisisEscalationResult)
def escalate_crisis(data: schemas.CrisisEscalationInput, db: Session = Depends(get_db)):
    ticket = crisis_service.escalate_crisis(db, data)
    return schemas.CrisisEscalationResult(
        ticket_id=ticket.id,
        status=ticket.status,
    )