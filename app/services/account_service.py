from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..config import settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    if not hashed_password:
        return False
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

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