from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_workspace_member
from app.models.user import User, WorkspaceMember
from app.models.meeting import Meeting
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.intelligence import Decision, Risk, DecisionStatus
from app.schemas.task import TaskResponse

router = APIRouter()

@router.get("/workspaces/{workspace_id}/dashboard/personal")
def get_personal_dashboard(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    """
    Deterministic personal task metrics calculated using standard SQL queries.
    """
    my_tasks = (
        db.query(Task)
        .filter(
            Task.workspace_id == workspace_id,
            (Task.assignee_id == current_user.id) | (Task.assignee_name == current_user.full_name)
        )
        .all()
    )

    pending = [t for t in my_tasks if t.status == TaskStatus.PENDING]
    in_progress = [t for t in my_tasks if t.status == TaskStatus.IN_PROGRESS]
    blocked = [t for t in my_tasks if t.status == TaskStatus.BLOCKED]
    completed = [t for t in my_tasks if t.status == TaskStatus.COMPLETED]

    return {
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "total_assigned": len(my_tasks),
        "pending_count": len(pending),
        "in_progress_count": len(in_progress),
        "blocked_count": len(blocked),
        "completed_count": len(completed),
        "tasks": [TaskResponse.from_orm(t) for t in my_tasks]
    }

@router.get("/workspaces/{workspace_id}/dashboard/team")
def get_team_dashboard(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    """
    Deterministic team-wide dashboard metrics calculated with SQL queries.
    Zero hallucination risk.
    """
    all_tasks = db.query(Task).filter(Task.workspace_id == workspace_id).all()
    all_meetings = db.query(Meeting).filter(Meeting.workspace_id == workspace_id).all()
    all_decisions = db.query(Decision).filter(Decision.workspace_id == workspace_id).all()
    all_risks = db.query(Risk).filter(Risk.workspace_id == workspace_id).all()

    # Status counts
    pending_count = sum(1 for t in all_tasks if t.status == TaskStatus.PENDING)
    in_progress_count = sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS)
    blocked_count = sum(1 for t in all_tasks if t.status == TaskStatus.BLOCKED)
    completed_count = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
    unassigned_count = sum(1 for t in all_tasks if not t.assignee_name)

    # Workload by participant
    workload_map: Dict[str, Dict[str, int]] = {}
    for t in all_tasks:
        assignee = t.assignee_name or "Unassigned"
        if assignee not in workload_map:
            workload_map[assignee] = {"pending": 0, "in_progress": 0, "blocked": 0, "completed": 0, "total": 0}
        st_key = t.status.value
        if st_key in workload_map[assignee]:
            workload_map[assignee][st_key] += 1
        workload_map[assignee]["total"] += 1

    # Active blockers
    blocked_items = [
        {
            "id": t.id,
            "title": t.title,
            "assignee": t.assignee_name or "Unassigned",
            "blocker_reason": t.blocker_reason or "Reason unspecified",
            "meeting_id": t.meeting_id
        }
        for t in all_tasks
        if t.status == TaskStatus.BLOCKED
    ]

    # Decisions breakdown
    confirmed_decisions = sum(1 for d in all_decisions if d.status == DecisionStatus.CONFIRMED)
    proposed_decisions = sum(1 for d in all_decisions if d.status == DecisionStatus.PROPOSED)
    disputed_decisions = sum(1 for d in all_decisions if d.status == DecisionStatus.DISPUTED)

    # Risk breakdown
    critical_risks = sum(1 for r in all_risks if r.severity.value == "critical")
    high_risks = sum(1 for r in all_risks if r.severity.value == "high")

    return {
        "workspace_id": workspace_id,
        "meeting_count": len(all_meetings),
        "task_metrics": {
            "total": len(all_tasks),
            "pending": pending_count,
            "in_progress": in_progress_count,
            "blocked": blocked_count,
            "completed": completed_count,
            "unassigned": unassigned_count,
            "completion_rate_percent": round((completed_count / max(1, len(all_tasks))) * 100.0, 1)
        },
        "workload_by_member": workload_map,
        "active_blockers": blocked_items,
        "decision_metrics": {
            "total": len(all_decisions),
            "confirmed": confirmed_decisions,
            "proposed_awaiting_review": proposed_decisions,
            "disputed": disputed_decisions
        },
        "risk_metrics": {
            "total": len(all_risks),
            "critical": critical_risks,
            "high": high_risks
        }
    }
