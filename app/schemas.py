from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import UserRole, PostStatus, ReportStatus, CrisisStatus 

class UserBase(BaseModel):
    id : int
    display_name : str
    isanonymous : bool
    role: UserRole
    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    group_id : Optional[int] = None
    content : str

class PostRead(BaseModel):
    id : int
    group_id : Optional[int]
    content : str
    status : PostStatus
    createdat : datetime
    author : UserBase
    class Config:
        orm_mode = True

class ReportCreate(BaseModel):
    reported_user_id : Optional[int] = None
    post_id : Optional[int] = None
    reason : str
    is_crisis : bool = False

class ReportRead(BaseModel):
    id : int
    reporting_user_id : int
    reported_user_id : Optional[int]
    post_id : Optional[int]
    reason : str
    is_crisis : bool
    status : ReportStatus
    resolutionimpact : Optional[str]
    createdat : datetime
    resolvedat : Optional[datetime]

    class Config:
        orm_mode = True

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