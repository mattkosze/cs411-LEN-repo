from sqlalchemy.orm import Session
from .. import models, schemas

def delete_account(db, user, reason):
    user.displayname = "Deleted User"
    user.email = None
    user.hashedpassword = None
    user.isanonymous = True
    user.is_active = False

    db.add(user)

    audit = models.AuditLogEntry(actor_id=user.id,action_type="delete_account",target_type="User",target_id=user.id, details=reason or "")
    db.add(audit)
    db.commit()

    return schemas.DeleteAccountResult(success=True,message="Account deleted and content anonymized")