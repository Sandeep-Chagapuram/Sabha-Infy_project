from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.api.deps import get_db, get_current_user, get_current_workspace_member
from app.models.user import User, WorkspaceMember
from app.models.meeting import Meeting
from app.models.usage import AIUsageRecord, BudgetLimit
from app.schemas.usage import UsageSummaryResponse, UsageRecordResponse, BudgetLimitUpdate
from app.core.config import settings

router = APIRouter()

@router.get("/workspaces/{workspace_id}/usage", response_model=UsageSummaryResponse)
def get_usage_summary(
    workspace_id: str,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    records = (
        db.query(AIUsageRecord)
        .filter(AIUsageRecord.workspace_id == workspace_id)
        .order_by(AIUsageRecord.created_at.desc())
        .all()
    )

    total_tokens = sum(r.input_tokens + r.output_tokens for r in records)
    total_cost = sum(r.estimated_cost_usd for r in records)

    cat_breakdown: Dict[str, float] = {}
    model_breakdown: Dict[str, int] = {}

    for r in records:
        cat_key = r.task_category.value
        cat_breakdown[cat_key] = round(cat_breakdown.get(cat_key, 0.0) + r.estimated_cost_usd, 4)
        model_breakdown[r.model] = model_breakdown.get(r.model, 0) + 1

    limit_obj = db.query(BudgetLimit).filter(BudgetLimit.workspace_id == workspace_id).first()
    monthly_budget = limit_obj.max_monthly_cost_usd if limit_obj else 100.0
    spent = round(total_cost, 4)
    remaining = max(0.0, monthly_budget - spent)
    pct = round((spent / max(0.01, monthly_budget)) * 100.0, 1)

    meeting_count = db.query(Meeting).filter(Meeting.workspace_id == workspace_id).count()

    return UsageSummaryResponse(
        workspace_id=workspace_id,
        total_meetings_analyzed=meeting_count,
        total_tokens_processed=total_tokens,
        total_cost_usd=spent,
        monthly_budget_usd=monthly_budget,
        current_month_spent_usd=spent,
        budget_remaining_usd=remaining,
        budget_usage_percent=min(100.0, pct),
        category_breakdown=cat_breakdown,
        model_breakdown=model_breakdown,
        recent_records=[UsageRecordResponse.from_orm(r) for r in records[:15]]
    )

@router.patch("/workspaces/{workspace_id}/budget-limits")
def update_budget_limits(
    workspace_id: str,
    update_in: BudgetLimitUpdate,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(get_current_workspace_member)
):
    limit_obj = db.query(BudgetLimit).filter(BudgetLimit.workspace_id == workspace_id).first()
    if not limit_obj:
        limit_obj = BudgetLimit(workspace_id=workspace_id)
        db.add(limit_obj)

    if update_in.max_meeting_cost_usd is not None:
        limit_obj.max_meeting_cost_usd = update_in.max_meeting_cost_usd
    if update_in.max_monthly_cost_usd is not None:
        limit_obj.max_monthly_cost_usd = update_in.max_monthly_cost_usd
    if update_in.is_hard_stop is not None:
        limit_obj.is_hard_stop = update_in.is_hard_stop

    db.commit()
    return {"message": "Budget limits updated successfully."}
