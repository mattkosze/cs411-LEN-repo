from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from .db import get_db 
from . import models

def get_current_user(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    # For development/demo: allow switching user via header
    if x_user_id:
        try:
            user_id = int(x_user_id)
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                if not user.is_active:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deleted")
                return user
        except ValueError:
            pass

    # Fallback to first user if no header or invalid user
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authenticated")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deleted")
        
    return user

def require_moderator(current_user: models.User):
    if current_user.role not in {models.UserRole.MODERATOR, models.UserRole.ADMIN}:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Moderator access required")
    return current_user