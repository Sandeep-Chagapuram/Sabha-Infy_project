from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from app.models.usage import TaskCategory

class UsageRecordResponse(BaseModel):
    id: str
    workspace_id: str
    meeting_id: Optional[str]
    task_category: TaskCategory
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    is_measured: bool
    estimated_cost_usd: float
    latency_ms: int
    was_escalated: bool
    escalation_reason: Optional[str]
    validation_passed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UsageSummaryResponse(BaseModel):
    workspace_id: str
    total_meetings_analyzed: int
    total_tokens_processed: int
    total_cost_usd: float
    monthly_budget_usd: float
    current_month_spent_usd: float
    budget_remaining_usd: float
    budget_usage_percent: float
    category_breakdown: Dict[str, float]
    model_breakdown: Dict[str, int]
    recent_records: List[UsageRecordResponse] = []

class BudgetLimitUpdate(BaseModel):
    max_meeting_cost_usd: Optional[float] = None
    max_monthly_cost_usd: Optional[float] = None
    is_hard_stop: Optional[bool] = None

class AuditEventResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: Optional[str]
    event_type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
