from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import schemas, models
from ..dependencies import require_moderator
from ..services import moderation_service

#router specifically for general moderation

router = APIRouter()

@router.post("/determine-action", response_model=schemas.DetermineActionResult)
def determine_action(data, db, moderator):
    report = moderation_service.determine_action(db, moderator, data)
    return schemas.DetermineActionResult(report=report)

@router.post("/delete-post/{post_id}", response_model=schemas.DeletePostResult)
def delete_post(post_id, reason, db, moderator):
    post = moderation_service.delete_post(db, moderator, post_id, reason)
    return schemas.DeletePostResult(
        success=True,
        post_id=post.id,
        status=post.status,
    )