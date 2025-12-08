from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .models import UserRole, PostStatus, ReportStatus, CrisisStatus, ReportReason, ConditionBoard 

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id : int
    displayname : str
    isanonymous : bool
    role: UserRole

class PostCreate(BaseModel):
    group_id : Optional[int] = None
    content : str
    posttime : float

class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id : int
    group_id : Optional[int]
    content : str
    status : PostStatus
    createdat : float
    author : UserBase

class ReportCreate(BaseModel):
    reported_user_id : Optional[int] = None
    post_id : Optional[int] = None
    reason : ReportReason
    details : Optional[str] = None  # Optional additional details from reporter

class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id : int
    reporting_user_id : int
    reported_user_id : Optional[int]
    post_id : Optional[int]
    reason : ReportReason
    details : Optional[str]
    is_crisis : bool
    status : ReportStatus
    resolutionimpact : Optional[str]
    createdat : float
    resolvedat : Optional[float]

class DetermineActionInput(BaseModel):
    report_id : int
    action : str
    mod_note : Optional[str] = None

class DetermineActionResult(BaseModel):
    report : ReportRead

class DeleteAccountResult(BaseModel):
    success : bool
    message : str

class CrisisEscalationInput(BaseModel):
    user_id : Optional[int] = None
    report_id : Optional[int] = None
    content_snip : Optional[str] = None

class CrisisEscalationResult(BaseModel):
    ticket_id : int
    status : CrisisStatus

class DeletePostResult(BaseModel):
    success : bool
    post_id : int
    status : PostStatus

class ConditionBoardBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]

class ConditionBoardCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class ConditionBoardRead(ConditionBoardBase):
    pass

class UserRegister(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    displayname: str = Field(..., max_length=50)

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None