from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from .. import schemas, models
from ..dependencies import get_current_user
from ..services import messaging_service, report_service

router = APIRouter()

@router.get("/", response_model=List[schemas.PostRead])
def get_posts(
    group_id: Optional[int] = Query(None, description="Filter posts by condition/board group_id"),
    db: Session = Depends(get_db)
):
    """Get posts, optionally filtered by group_id (condition board)"""
    query = db.query(models.Post).filter(models.Post.status == models.PostStatus.ACTIVE)
    
    if group_id is not None:
        query = query.filter(models.Post.group_id == group_id)
    
    posts = query.order_by(models.Post.createdat.desc()).all()
    return posts

@router.post("/", response_model=schemas.PostRead)
def post_message(
    data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = messaging_service.post_message(db, current_user, data)
    return post

@router.delete("/{post_id}", response_model=schemas.DeletePostResult)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Allow users to delete their own posts"""
    post = messaging_service.delete_post(db, current_user, post_id)
    return schemas.DeletePostResult(
        success=True,
        post_id=post.id,
        status=post.status,
    )

@router.post("/{post_id}/report", response_model=schemas.ReportRead)
def report_post(
    post_id: int,
    data: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Report a post for harassment, spam, inappropriate content, or crisis.
    Crisis reports automatically create a crisis ticket for urgent handling.
    """
    report = report_service.create_report(db, current_user, post_id, data)
    return report