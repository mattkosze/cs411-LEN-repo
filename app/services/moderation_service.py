#uses the db model to store the action taken which may update a user in the user database
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

VALID = {"warn", "ban", "dismiss", "delete_post", "delete_account"}

def determine_action(db, moderator, data):
    # checks if the action reported is valid, and from there applies a given action to user. recorded in audit log
    if data.action not in VALID:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    report = db.query(models.Report).filter(models.Report.id == data.report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Can't find report")
    
    # Crisis reports can only use delete_post or dismiss, not warn/ban/delete_account
    if report.is_crisis and data.action not in {"delete_post", "dismiss"}:
        raise HTTPException(status_code=400, detail="Crisis reports can only use 'Delete Post' or 'Dismiss'")
    
    # Handle delete_post action - delete the post, warn the user, and resolve the report
    if data.action == "delete_post":
        if not report.post_id:
            raise HTTPException(status_code=400, detail="No post associated with this report")
        post = db.query(models.Post).filter(models.Post.id == report.post_id).first()
        if post:
            post.status = models.PostStatus.DELETED
        # Also warn the user if there's a reported user (non-crisis only)
        if report.reported_user_id and not report.is_crisis:
            reported_user = db.query(models.User).get(report.reported_user_id)
            # User is warned - could track warning count in future
            report.resolution_impact = "post_deleted_user_warned"
        else:
            report.resolution_impact = "post_deleted"
        report.status = models.ReportStatus.RESOLVED
        audit = models.AuditLogEntry(
            actor_id=moderator.id, 
            action_type="moderation_delete_post_warn" if not report.is_crisis else "moderation_delete_post", 
            target_type="Report", 
            target_id=report.id, 
            details=data.mod_note or ""
        )
        db.add(audit)
        db.commit()
        db.refresh(report)
        return report
    
    # Handle delete_account action - ban and delete the account, resolve the report
    if data.action == "delete_account":
        if not report.reported_user_id:
            raise HTTPException(status_code=400, detail="No user associated with this report")
        reported_user = db.query(models.User).get(report.reported_user_id)
        if reported_user:
            # Ban the user first
            reported_user.is_banned = True
            # Then delete their account
            from ..services import account_service
            account_service.delete_account(db, reported_user, data.mod_note or "Banned and deleted by moderator")
        report.status = models.ReportStatus.RESOLVED
        report.resolution_impact = "account_banned_deleted"
        audit = models.AuditLogEntry(
            actor_id=moderator.id, 
            action_type="moderation_ban_delete_account", 
            target_type="Report", 
            target_id=report.id, 
            details=data.mod_note or ""
        )
        db.add(audit)
        db.commit()
        db.refresh(report)
        return report
    
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
        _resolve_report(db, moderator, report_id, "post_deleted", reason)
    
    db.commit()
    db.refresh(post)

    return post

def _resolve_report(db, moderator, report_id, resolution_impact, reason):
    """Helper to resolve a report with the given impact. Internal use only."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if report and report.status == models.ReportStatus.OPEN:
        report.status = models.ReportStatus.RESOLVED
        report.resolution_impact = resolution_impact
        audit = models.AuditLogEntry(
            actor_id=moderator.id,
            action_type=f"moderation_{resolution_impact}",
            target_type="Report",
            target_id=report.id,
            details=reason or ""
        )
        db.add(audit)

def delete_account_as_moderator(db, moderator, user_to_delete, reason, report_id=None):
    """Delete a user account as a moderator action with optional report resolution."""
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Resolve the report if report_id is provided
    if report_id:
        _resolve_report(db, moderator, report_id, "account_deleted", reason)
    
    # Delegate to account service for the actual deletion
    from ..services import account_service
    return account_service.delete_account(db, user_to_delete, reason)