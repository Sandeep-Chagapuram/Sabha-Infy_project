from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority, DeadlineConfidence, ValidationStatus

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    deadline: Optional[datetime] = None
    deadline_text: Optional[str] = None
    deadline_confidence: DeadlineConfidence = DeadlineConfidence.UNSPECIFIED
    priority: TaskPriority = TaskPriority.MEDIUM
    source_segment_id: Optional[str] = None
    source_evidence_quote: str
    validation_status: ValidationStatus = ValidationStatus.EVIDENCE_SUPPORTED

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    is_ownership_confirmed: Optional[bool] = None
    deadline: Optional[datetime] = None
    deadline_text: Optional[str] = None
    deadline_confidence: Optional[DeadlineConfidence] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    blocker_reason: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None

class TaskCommentResponse(BaseModel):
    id: str
    task_id: str
    user_id: Optional[str]
    author_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCommentCreate(BaseModel):
    content: str

class TaskResponse(BaseModel):
    id: str
    meeting_id: str
    workspace_id: str
    title: str
    description: Optional[str]
    assignee_id: Optional[str]
    assignee_name: Optional[str]
    is_ownership_confirmed: bool
    deadline: Optional[datetime]
    deadline_text: Optional[str]
    deadline_confidence: DeadlineConfidence
    status: TaskStatus
    priority: TaskPriority
    priority_origin: str
    blocker_reason: Optional[str]
    source_segment_id: Optional[str]
    source_evidence_quote: str
    validation_status: ValidationStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    comments: List[TaskCommentResponse] = []

    class Config:
        from_attributes = True
