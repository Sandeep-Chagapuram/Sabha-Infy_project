from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class DeadlineConfidence(str, enum.Enum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    AMBIGUOUS = "ambiguous"
    UNSPECIFIED = "unspecified"

class ValidationStatus(str, enum.Enum):
    EXPLICITLY_STATED = "explicitly_stated"
    EVIDENCE_SUPPORTED = "evidence_supported"
    INFERRED = "inferred"
    CONFLICTING = "conflicting"
    UNVERIFIED = "unverified"
    HUMAN_CONFIRMED = "human_confirmed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Ownership (Never invent owner! Nullable if unassigned)
    assignee_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    assignee_name = Column(String(255), nullable=True)
    is_ownership_confirmed = Column(Boolean, default=False)
    
    # Deadline
    deadline = Column(DateTime, nullable=True)
    deadline_text = Column(String(100), nullable=True)
    deadline_confidence = Column(SQLEnum(DeadlineConfidence), default=DeadlineConfidence.UNSPECIFIED, nullable=False)
    
    # Status & Priority
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    priority_origin = Column(String(100), default="extracted_from_meeting")
    
    # Blocker info
    blocker_reason = Column(Text, nullable=True)
    
    # Evidence Provenance (Every task must be grounded)
    source_segment_id = Column(String(36), ForeignKey("transcript_segments.id"), nullable=True)
    source_evidence_quote = Column(Text, nullable=False)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.EVIDENCE_SUPPORTED, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    meeting = relationship("Meeting", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    source_segment = relationship("TranscriptSegment")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan"
    )

class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    depends_on_task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id])

class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    author_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
