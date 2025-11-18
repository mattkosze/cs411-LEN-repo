from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    Enum,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .db import Base

class UserRole(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class PostStatus(str, enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    LOCKED = "locked"

class ReportStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class CrisisStatus(str, enum.Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    CLOSED = "closed"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashedpassword = Column(String(50), nullable=True)
    displayname = Column(String(50))
    isanonymous = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    isbanned = Column(Boolean, default=False)

    posts = relationship("Post", back_populates="author")
    reports_made = relationship("Report", back_populates="reporting_user", foreign_keys="Report.reported_user_id")
    reports_received = relationship("Report", back_populates="reported_user", foreign_keys="Report.reported_user_id")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, nullable=True) #group later
    content = Column(Text, nullable=False)
    status = Column(Enum(PostStatus), default=PostStatus.ACTIVE)
    createdat = Column(DateTime, default=datetime.utcnow)
    author = relationship("User", back_populates="posts")
    reports = relationship("Report", back_populates="post")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporting_user_id = Column(Integer, ForeignKey("users.id"))
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    reason = Column(Text, nullable=False)
    is_crisis = Column(Boolean, default=False)
    createdat = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ReportStatus), default=ReportStatus.OPEN)
    resolvedat = Column(DateTime, nullable=True)
    resolutionimpact = Column(String(50), nullable=True)

    reported_user = relationship("User", back_populates="reports_received", foreign_keys=[reported_user_id])
    reporting_user = relationship("User", back_populates="reports_made", foreign_keys=[reporting_user_id])
    post = relationship("Post", back_populates="reports")

class CrisisTicket(Base):
    __tablename__ = "audit_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    status = Column(Enum(CrisisStatus), default=CrisisStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action_type = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
