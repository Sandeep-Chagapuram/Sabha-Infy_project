from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_workspace_member
from app.models.user import User, WorkspaceMember
from app.models.task import Task, TaskComment, TaskStatus, TaskPriority, ValidationStatus
from app.schemas.task import TaskResponse, TaskUpdate, TaskCommentCreate, TaskCommentResponse

router = APIRouter()

@router.get("/workspaces/{workspace_id}/tasks", response_model=List[TaskResponse])
def list_tasks(
    workspace_id: str,
    meeting_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    unassigned_only: bool = False,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    query = db.query(Task).filter(Task.workspace_id == workspace_id)
    if meeting_id:
        query = query.filter(Task.meeting_id == meeting_id)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if unassigned_only:
        query = query.filter((Task.assignee_name == None) | (Task.assignee_name == ""))

    return query.order_by(Task.created_at.desc()).all()

@router.get("/workspaces/{workspace_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    workspace_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    task = db.query(Task).filter(Task.id == task_id, Task.workspace_id == workspace_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task

@router.patch("/workspaces/{workspace_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    workspace_id: str,
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    task = db.query(Task).filter(Task.id == task_id, Task.workspace_id == workspace_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    if task_in.title is not None:
        task.title = task_in.title
    if task_in.description is not None:
        task.description = task_in.description
    if task_in.assignee_id is not None:
        task.assignee_id = task_in.assignee_id
    if task_in.assignee_name is not None:
        task.assignee_name = task_in.assignee_name
        task.is_ownership_confirmed = True
    if task_in.status is not None:
        task.status = task_in.status
        if task_in.status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
        elif task.status != TaskStatus.COMPLETED:
            task.completed_at = None
    if task_in.priority is not None:
        task.priority = task_in.priority
    if task_in.blocker_reason is not None:
        task.blocker_reason = task_in.blocker_reason
        if task_in.blocker_reason.strip():
            task.status = TaskStatus.BLOCKED
    if task_in.deadline is not None:
        task.deadline = task_in.deadline
    if task_in.validation_status is not None:
        task.validation_status = task_in.validation_status

    db.commit()
    db.refresh(task)
    return task

@router.post("/workspaces/{workspace_id}/tasks/{task_id}/comments", response_model=TaskCommentResponse)
def add_comment(
    workspace_id: str,
    task_id: str,
    comment_in: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    task = db.query(Task).filter(Task.id == task_id, Task.workspace_id == workspace_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    comment = TaskComment(
        task_id=task.id,
        user_id=current_user.id,
        author_name=current_user.full_name,
        content=comment_in.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
