#uses the db model to store the action taken which may update a user in the user database
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

VALID = {"warn", "ban", "dismiss"}

def determine_action(db, moderator, data):
    # checks if the action reported is valid, and from there applies a given action to user. recorded in audit log
    if data.action not in VALID:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    report = db.query(models.Report).filter(models.Report.id == data.report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Can't find report")
    
    if report.is_crisis:
        raise HTTPException(status_code=400, detail="Crisis report being handled independently")
    
    # applying the action - dismiss goes to DISMISSED, others go to RESOLVED
    if data.action == "dismiss":
        report.status = models.ReportStatus.DISMISSED
    else:
        report.status = models.ReportStatus.RESOLVED
    report.resolution_impact = data.action

    if report.reported_user_id:
        reported_user = db.query(models.User).get(report.reported_user_id)

        if reported_user:
            if data.action == "ban":
                reported_user.is_banned = True

    audit = models.AuditLogEntry(actor_id=moderator.id, action_type=f"moderation_{data.action}", target_type="Report", target_id=report.id, details=data.mod_note or "")
    db.add(audit)
    db.commit()
    db.refresh(report)

    return report

def delete_post(db, moderator, post_id, reason, report_id=None):
    # audit log records post being deleted, with error-handling
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Couldn't find post")
    
    if post.status == models.PostStatus.DELETED:
        raise HTTPException(status_code=400, detail="Post was already deleted")
    
    post.status = models.PostStatus.DELETED

    audit = models.AuditLogEntry(actor_id=moderator.id, action_type="delete_post", target_type="Post", target_id=post.id, details=reason or "")

    db.add(audit)
    
    # Resolve the report if report_id is provided
    if report_id:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if report and report.status == models.ReportStatus.OPEN:
            report.status = models.ReportStatus.RESOLVED
            report.resolution_impact = "post_deleted"
    
    db.commit()
    db.refresh(post)

    return post