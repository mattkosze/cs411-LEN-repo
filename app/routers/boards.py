from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from .. import schemas, models
from ..services import board_service
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.ConditionBoardRead])
def get_boards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return board_service.list_boards(db)

@router.post("/", response_model=schemas.ConditionBoardRead)
def create_board(
    data: schemas.ConditionBoardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only moderators/admins can create boards
    if current_user.role not in (models.UserRole.MODERATOR, models.UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create boards")
    return board_service.create_board(db, data)