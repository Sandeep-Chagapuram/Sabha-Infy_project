from typing import Dict, Any, Optional
from pydantic import BaseModel

class ModelSpec(BaseModel):
    name: str
    provider: str
    task_suitability: list[str]
    input_cost_per_million: float   # USD estimate
    output_cost_per_million: float  # USD estimate
    context_window: int            # tokens
    max_output_tokens: int
    is_reasoning_model: bool = False
    description: str

# Exclusive Qualcomm Cloud AI Model Registry
QUALCOMM_MODEL_REGISTRY: Dict[str, ModelSpec] = {
    "deterministic-python": ModelSpec(
        name="deterministic-python",
        provider="local_engine",
        task_suitability=["cleaning", "counting", "dates", "deduplication", "schema_validation", "budget_check"],
        input_cost_per_million=0.0,
        output_cost_per_million=0.0,
        context_window=1000000,
        max_output_tokens=1000000,
        is_reasoning_model=False,
        description="Deterministic Python/SQL algorithms. Zero LLM cost, zero latency."
    ),
    "Llama-3.1-8B": ModelSpec(
        name="Llama-3.1-8B",
        provider="qualcomm_cloud_ai",
        task_suitability=["routine_extraction", "classification", "summarization", "action_items", "decisions"],
        input_cost_per_million=0.05,
        output_cost_per_million=0.08,
        context_window=128000,
        max_output_tokens=4096,
        is_reasoning_model=False,
        description="Qualcomm Cloud AI high-speed 8B model for routine extraction and summaries."
    ),
    "Llama-3.3-70B": ModelSpec(
        name="Llama-3.3-70B",
        provider="qualcomm_cloud_ai",
        task_suitability=["complex_reasoning", "second_brain_synthesis", "cross_speaker_contradictions"],
        input_cost_per_million=0.35,
        output_cost_per_million=0.40,
        context_window=128000,
        max_output_tokens=8192,
        is_reasoning_model=False,
        description="Qualcomm Cloud AI 70B model for multi-perspective Second Brain synthesis."
    ),
    "deepseek-r1-distill-llama-70b": ModelSpec(
        name="deepseek-r1-distill-llama-70b",
        provider="qualcomm_cloud_ai",
        task_suitability=["flaw_detection", "critical_review", "contradiction_analysis", "escalation"],
        input_cost_per_million=0.50,
        output_cost_per_million=0.80,
        context_window=64000,
        max_output_tokens=4096,
        is_reasoning_model=True,
        description="Qualcomm Cloud AI deep reasoning model for uncovering blind spots and hidden risks."
    ),
    "Qwen-QwQ-32B": ModelSpec(
        name="Qwen-QwQ-32B",
        provider="qualcomm_cloud_ai",
        task_suitability=["creative_solutions", "brainstorming", "alternative_architectures"],
        input_cost_per_million=0.20,
        output_cost_per_million=0.30,
        context_window=32768,
        max_output_tokens=4096,
        is_reasoning_model=True,
        description="Qualcomm Cloud AI exploratory model for creative trade-offs and alternative solutions."
    )
}

def get_model_spec(model_name: str) -> Optional[ModelSpec]:
    return QUALCOMM_MODEL_REGISTRY.get(model_name)

def calculate_estimated_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    spec = get_model_spec(model_name)
    if not spec:
        return 0.0
    input_cost = (input_tokens / 1_000_000.0) * spec.input_cost_per_million
    output_cost = (output_tokens / 1_000_000.0) * spec.output_cost_per_million
    return round(input_cost + output_cost, 6)
