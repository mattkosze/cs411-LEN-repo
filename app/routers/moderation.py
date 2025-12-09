from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from .. import schemas, models
from ..dependencies import get_current_user, require_moderator
from ..services import moderation_service

# router specifically for general moderation

router = APIRouter()

@router.get("/reports", response_model=List[schemas.ReportRead])
def get_reports(
    status: Optional[str] = Query(None, description="Filter by report status (open, resolved, dismissed)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all reports for moderation. Only accessible by moderators."""
    moderator = require_moderator(current_user)
    
    query = db.query(models.Report).filter(models.Report.is_crisis == False)
    
    if status:
        try:
            status_enum = models.ReportStatus(status)
            query = query.filter(models.Report.status == status_enum)
        except ValueError:
            pass
    
    reports = query.order_by(models.Report.created_at.desc()).all()
    return reports

@router.post("/determine-action", response_model=schemas.DetermineActionResult)
def determine_action(
    data: schemas.DetermineActionInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Determine action on a report (warn, ban, dismiss). Only accessible by moderators."""
    moderator = require_moderator(current_user)
    report = moderation_service.determine_action(db, moderator, data)
    return schemas.DetermineActionResult(report=report)

@router.post("/delete-post/{post_id}", response_model=schemas.DeletePostResult)
def delete_post(
    post_id: int,
    reason: str = Query(..., description="Reason for deletion"),
    report_id: Optional[int] = Query(None, description="Report ID to resolve"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a post. Only accessible by moderators."""
    moderator = require_moderator(current_user)
    post = moderation_service.delete_post(db, moderator, post_id, reason, report_id)
    return schemas.DeletePostResult(
        success=True,
        post_id=post.id,
        status=post.status,
    )

@router.delete("/delete-account/{user_id}", response_model=schemas.DeleteAccountResult)
def delete_account(
    user_id: int,
    reason: str = Query(..., description="Reason for account deletion"),
    report_id: Optional[int] = Query(None, description="Report ID to resolve"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a user account. Only accessible by moderators."""
    moderator = require_moderator(current_user)
    
    user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
    
    return moderation_service.delete_account_as_moderator(db, moderator, user_to_delete, reason, report_id)