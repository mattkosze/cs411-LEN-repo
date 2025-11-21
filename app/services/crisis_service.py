#using the sqlalchemy model previously made that we went over in person.

from sqlalchemy.orm import Session
from .. import models, schemas

def escalate_crisis(db: Session, data: schemas.CrisisEscalationInput):
    #creates a ticket for the occassion (crisis), and audit log gets recorded.
    
    # Create crisis ticket with optional user_id and report_id
    ticket = models.CrisisTicket(
        user_id=data.user_id,
        report_id=data.report_id
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Create audit log entry with crisis details
    details = data.content_snip or "Crisis escalation without content details"
    audit = models.AuditLogEntry(
        actor_id=None,
        action_type="crisis_escalation",
        target_type="CrisisTicket",
        target_id=ticket.id,
        details=details[:100]
    )
    db.add(audit)
    db.commit()

    #in the future must send notifications to mods

    return ticket