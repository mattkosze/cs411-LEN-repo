#using the sqlalchemy model previously made that we went over in person.

from sqlalchemy.orm import Session
from .. import models, schemas

def escalate_crisis(db, data):
    #creates a ticket for the occassion (crisis), and audit log gets recorded.
    ticket = models.CrisisTicket(user_id=data.user_id,report_id=data.report_id)

    db.add(ticket)

    details = data.content_snip or ""
    audit = models.AuditLogEntry(actor_id=None,action_type="crisis_escalation",target_type=None, details=details[:100])
    db.add(audit)
    db.commit()
    db.refresh(ticket)

    audit.target_id = ticket.id
    db.add(audit)
    db.commit()

    #in the future must send notifications to mods

    return ticket