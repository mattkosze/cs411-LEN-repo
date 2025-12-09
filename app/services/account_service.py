"""
Account service for user registration, authentication, and account management.

This module handles account-related business logic, delegating authentication
operations to auth_service for proper separation of concerns.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from .auth_service import hash_password, verify_password, create_access_token

# Re-export auth functions for backward compatibility
__all__ = ['hash_password', 'verify_password', 'create_access_token', 
           'register_user', 'authenticate_user', 'delete_account', 'update_account']


def register_user(db: Session, user_data: schemas.UserRegister) -> models.User:
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.display_name,
        is_anonymous=False,
        role=models.UserRole.USER,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> models.User:
    """Authenticate a user by email and password"""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deleted"
        )
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    return user

def delete_account(db, user, reason):
    user.display_name = "Deleted User"
    user.email = None
    user.hashed_password = None
    user.is_anonymous = True
    user.is_active = False

    db.add(user)

    audit = models.AuditLogEntry(actor_id=user.id, action_type="delete_account", target_type="User", target_id=user.id, details=reason or "")
    db.add(audit)
    db.commit()

    return schemas.DeleteAccountResult(success=True, message="Account deleted and content anonymized")

def update_account(db, user, update_data: schemas.UserUpdate):
    """Update user account settings"""
    if update_data.display_name is not None:
        user.display_name = update_data.display_name
    if update_data.is_anonymous is not None:
        user.is_anonymous = update_data.is_anonymous
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user