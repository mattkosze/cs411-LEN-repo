from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
from .db import get_db 
from . import models
from .config import settings

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)  # Keep for backward compatibility with dev switcher
):
    # For development/demo: allow switching user via header (fallback)
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

    # Primary authentication via JWT token
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deleted")
    
    return user

def require_moderator(current_user: models.User):
    if current_user.role not in {models.UserRole.MODERATOR, models.UserRole.ADMIN}:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Moderator access required")
    return current_user