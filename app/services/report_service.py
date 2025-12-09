#handles user report creation on posts
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from datetime import datetime


def create_report(
    db: Session,
    reporter: models.User,
    post_id: int,
    data: schemas.ReportCreate
) -> models.Report:
    """
    Create a report for a post. If the reason is CRISIS, automatically
    sets is_crisis flag and creates a crisis ticket.
    """
    #makes sure the post exists and is active
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.status != models.PostStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot report an inactive post"
        )
    
    #prevents users from reporting their own posts
    if post.author_id == reporter.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report your own post"
        )
    
    #check if user has already reported this post before
    existing_report = db.query(models.Report).filter(
        models.Report.reporting_user_id == reporter.id,
        models.Report.post_id == post_id,
        models.Report.status == models.ReportStatus.OPEN
    ).first()
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reported this post"
        )
    
    # determines if this is a crisis report
    is_crisis = data.reason == models.ReportReason.CRISIS
    
    # creates report
    report = models.Report(
        reporting_user_id=reporter.id,
        reported_user_id=post.author_id,
        post_id=post_id,
        reason=data.reason,
        details=data.details,
        is_crisis=is_crisis,
        created_at=datetime.now().timestamp(),
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    #crisis --> create a crisis ticket for urgent handling
    if is_crisis:
        crisis_ticket = models.CrisisTicket(
            user_id=post.author_id,
            report_id=report.id,
        )
        db.add(crisis_ticket)
        
        #logs the crisis escalation in audit log
        audit = models.AuditLogEntry(
            actor_id=reporter.id,
            action_type="crisis_report_created",
            target_type="Report",
            target_id=report.id,
            details=f"Crisis report created for post {post_id}"
        )
        db.add(audit)
        db.commit()
    
    return report

