from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .db import get_db 
from . import models

def get_current_user(db):
    #need to integrate real authentication in the future
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authenticated")
    return user

def require_moderator(current_user):
    if current_user not in {models.UserRole.MODERATOR, models.UserRole.ADMIN}:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Moderator access required")
    return current_user