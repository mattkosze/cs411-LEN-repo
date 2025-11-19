from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..db import get_db
from .. import schemas, models
from ..dependencies import get_current_user
from ..services import account_service

router = APIRouter()

class DeleteAccountRequest(BaseModel):
    reason: str

@router.delete("/me", response_model=schemas.DeleteAccountResult)
def delete_my_account(
    req: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return account_service.delete_account(db, current_user, req.reason)