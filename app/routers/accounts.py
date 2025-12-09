from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from ..db import get_db
from .. import schemas, models
from ..dependencies import get_current_user
from ..services import account_service

router = APIRouter()

class DeleteAccountRequest(BaseModel):
    reason: str

@router.post("/register", response_model=schemas.Token)
def register(
    user_data: schemas.UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user account"""
    user = account_service.register_user(db, user_data)
    access_token = account_service.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(
    credentials: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """Sign in with email and password"""
    user = account_service.authenticate_user(db, credentials.email, credentials.password)
    access_token = account_service.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    """Sign out (client-side token removal)"""
    return {"message": "Successfully logged out"}

@router.get("/", response_model=List[schemas.UserBase])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all users (requires authentication)"""
    return db.query(models.User).filter(models.User.is_active == True).all()

@router.get("/me/", response_model=schemas.UserBase)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.patch("/me/", response_model=schemas.UserBase)
def update_current_user(
    update_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update current user settings"""
    return account_service.update_account(db, current_user, update_data)

@router.delete("/me/", response_model=schemas.DeleteAccountResult)
def delete_my_account(
    req: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return account_service.delete_account(db, current_user, req.reason)