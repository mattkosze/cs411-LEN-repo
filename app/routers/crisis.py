from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import schemas, models
from ..services import crisis_service
from ..dependencies import get_current_user

#router for specifically a crisis
router = APIRouter()

@router.post("/escalate", response_model=schemas.CrisisEscalationResult)
def escalate_crisis(
    data: schemas.CrisisEscalationInput, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ticket = crisis_service.escalate_crisis(db, data, current_user)
    return schemas.CrisisEscalationResult(
        ticket_id=ticket.id,
        status=ticket.status,
    )