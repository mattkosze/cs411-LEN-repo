#using the sqlalchemy model previously made that we went over in person.

from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime

def escalate_crisis(db: Session, data: schemas.CrisisEscalationInput, current_user: models.User):
    """
    Creates a crisis ticket and an associated report for moderator review.
    The report will appear in the moderation dashboard with is_crisis=True.
    Links to the post that triggered the crisis for moderator review.
    """
    
    # Create a crisis report that will show in the moderation dashboard
    report = models.Report(
        reporting_user_id=current_user.id,  # The user who triggered the crisis detection
        reported_user_id=current_user.id,   # The user who posted the crisis content (same user)
        post_id=data.post_id,  # Link to the post that triggered the crisis
        reason=models.ReportReason.CRISIS,
        details=data.content_snip[:200] if data.content_snip else "Crisis detected in content",
        is_crisis=True,
        status=models.ReportStatus.OPEN,
        created_at=datetime.now().timestamp(),
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Create crisis ticket linked to the report
    ticket = models.CrisisTicket(
        user_id=current_user.id,
        report_id=report.id
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Create audit log entry with crisis details
    details = data.content_snip[:100] if data.content_snip else "Crisis escalation without content details"
    audit = models.AuditLogEntry(
        actor_id=current_user.id,
        action_type="crisis_escalation",
        target_type="CrisisTicket",
        target_id=ticket.id,
        details=details
    )
    db.add(audit)
    db.commit()

    return ticket