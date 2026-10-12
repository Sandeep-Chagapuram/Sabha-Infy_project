from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.core.config import settings

class BudgetCheckResult(BaseModel):
    is_allowed: bool
    budget_exhausted: bool
    current_meeting_spent_usd: float
    max_meeting_budget_usd: float
    remaining_meeting_budget_usd: float
    allowed_analyses: list[str]
    deferred_analyses: list[str]
    alert_message: Optional[str] = None

class TokenBudgetManager:
    """
    Sabha AI Token Budget Manager.
    Enforces cost caps, tracks spend per meeting/workspace, and implements
    graceful degradation (e.g. prioritizing essential tasks/decisions over
    heavy creative ideation or deep research if budget is tight).
    """

    @classmethod
    def check_meeting_budget(
        cls,
        current_meeting_spent_usd: float,
        requested_depth: str = "full",
        max_budget_usd: Optional[float] = None
    ) -> BudgetCheckResult:
        limit = max_budget_usd or settings.MAX_MEETING_BUDGET_USD
        remaining = max(0.0, limit - current_meeting_spent_usd)

        # Analysis hierarchy:
        # 1. Essential: summary, tasks, decisions (inexpensive, core utility)
        # 2. Intelligence: Second Brain, risks, contradictions
        # 3. Creative: alternative solutions
        # 4. Research: web queries and deep synthesis

        if remaining <= 0.05:  # Less than 5 cents remaining
            return BudgetCheckResult(
                is_allowed=False,
                budget_exhausted=True,
                current_meeting_spent_usd=current_meeting_spent_usd,
                max_meeting_budget_usd=limit,
                remaining_meeting_budget_usd=remaining,
                allowed_analyses=["essential"],
                deferred_analyses=["second_brain", "creative_solutions", "flaw_detection", "research"],
                alert_message="Meeting budget limit reached ($2.50 cap). Deferring non-essential analyses to preserve resources."
            )
        elif remaining < 0.30:  # Tight budget
            return BudgetCheckResult(
                is_allowed=True,
                budget_exhausted=False,
                current_meeting_spent_usd=current_meeting_spent_usd,
                max_meeting_budget_usd=limit,
                remaining_meeting_budget_usd=remaining,
                allowed_analyses=["essential", "second_brain"],
                deferred_analyses=["creative_solutions", "research"],
                alert_message="Approaching meeting budget cap. Running essential extraction & Second Brain; deferring creative & web research."
            )
        else:
            return BudgetCheckResult(
                is_allowed=True,
                budget_exhausted=False,
                current_meeting_spent_usd=current_meeting_spent_usd,
                max_meeting_budget_usd=limit,
                remaining_meeting_budget_usd=remaining,
                allowed_analyses=["essential", "second_brain", "creative_solutions", "flaw_detection", "research"],
                deferred_analyses=[]
            )
