from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.core.config import settings
from app.ai.model_registry import get_model_spec

class RoutingDecision(BaseModel):
    task_category: str
    selected_model: str
    provider: str = "qualcomm_cloud_ai"
    is_deterministic: bool = False
    estimated_input_tokens: int
    rationale: str
    can_escalate: bool = False
    escalation_model: Optional[str] = None

class QualcommModelRouter:
    """
    Sabha AI Qualcomm-Exclusive Model Router.
    Routes tasks intelligently between verified Qualcomm Cloud AI Playground models:
    - Deterministic operations -> Python/SQL (zero token cost)
    - Routine extraction & classification -> Llama-3.1-8B (fast, low cost)
    - Multi-perspective Second Brain synthesis -> Llama-3.3-70B (high nuance)
    - Flaw detection & contradiction analysis -> deepseek-r1-distill-llama-70b (deep reasoning)
    - Creative solutions & trade-offs -> Qwen-QwQ-32B (divergent ideation)
    
    Strict Architecture Rule: No third-party LLMs are ever selected or routed to.
    """

    @classmethod
    def route_task(
        cls,
        task_category: str,
        estimated_tokens: int = 1000,
        complexity_score: float = 0.5,
        user_quality_setting: str = "balanced"
    ) -> RoutingDecision:
        # 1. Deterministic operations: never spend LLM tokens
        if task_category in ["cleaning", "counting", "dates", "deduplication", "schema_validation"]:
            return RoutingDecision(
                task_category=task_category,
                selected_model="deterministic-python",
                provider="local_engine",
                is_deterministic=True,
                estimated_input_tokens=0,
                rationale="Deterministic algorithm in Python/SQL. Zero LLM cost."
            )

        # 2. Routine extraction
        if task_category in ["summary", "tasks", "decisions", "questions", "basic_extraction"]:
            # If user explicitly set 'highest_quality' and complexity is high, select 70B
            if user_quality_setting == "highest_quality" or complexity_score > 0.8:
                selected = settings.QUALCOMM_COMPLEX_MODEL
                rationale = "High complexity transcript or highest-quality setting requested. Selected Qualcomm 70B."
            else:
                selected = settings.QUALCOMM_ROUTINE_MODEL
                rationale = "Routine extraction task. Routed to Qualcomm Llama-3.1-8B for optimal latency and cost."

            return RoutingDecision(
                task_category=task_category,
                selected_model=selected,
                provider="qualcomm_cloud_ai",
                is_deterministic=False,
                estimated_input_tokens=estimated_tokens,
                rationale=rationale,
                can_escalate=True,
                escalation_model=settings.QUALCOMM_REASONING_MODEL
            )

        # 3. Second Brain Review
        if task_category == "second_brain":
            return RoutingDecision(
                task_category=task_category,
                selected_model=settings.QUALCOMM_COMPLEX_MODEL,
                provider="qualcomm_cloud_ai",
                is_deterministic=False,
                estimated_input_tokens=estimated_tokens,
                rationale="Multi-perspective Second Brain synthesis requires Qualcomm 70B parameter reasoning.",
                can_escalate=True,
                escalation_model=settings.QUALCOMM_REASONING_MODEL
            )

        # 4. Flaw Detection & Contradiction Analysis
        if task_category == "flaw_detection":
            return RoutingDecision(
                task_category=task_category,
                selected_model=settings.QUALCOMM_REASONING_MODEL,
                provider="qualcomm_cloud_ai",
                is_deterministic=False,
                estimated_input_tokens=estimated_tokens,
                rationale="Critical review and assumption stress-testing routed to Qualcomm DeepSeek-R1 Distill.",
                can_escalate=False
            )

        # 5. Creative Solutions Engine
        if task_category == "creative_solutions":
            return RoutingDecision(
                task_category=task_category,
                selected_model=settings.QUALCOMM_CREATIVE_MODEL,
                provider="qualcomm_cloud_ai",
                is_deterministic=False,
                estimated_input_tokens=estimated_tokens,
                rationale="Alternative architectural trade-off exploration routed to Qualcomm Qwen-QwQ-32B.",
                can_escalate=False
            )

        # 6. Research Synthesis
        if task_category == "research_synthesis":
            return RoutingDecision(
                task_category=task_category,
                selected_model=settings.QUALCOMM_COMPLEX_MODEL,
                provider="qualcomm_cloud_ai",
                is_deterministic=False,
                estimated_input_tokens=estimated_tokens,
                rationale="Web search evidence synthesis routed to Qualcomm Llama-3.3-70B.",
                can_escalate=False
            )

        # Default fallback within Qualcomm models
        return RoutingDecision(
            task_category=task_category,
            selected_model=settings.QUALCOMM_ROUTINE_MODEL,
            provider="qualcomm_cloud_ai",
            is_deterministic=False,
            estimated_input_tokens=estimated_tokens,
            rationale="Defaulting to Qualcomm Llama-3.1-8B."
        )
