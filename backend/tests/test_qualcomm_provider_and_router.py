import pytest
from app.ai.model_router import QualcommModelRouter
from app.ai.provider import QualcommClient, QualcommAuthMissingError
from app.ai.model_registry import QUALCOMM_MODEL_REGISTRY

def test_model_registry_contains_only_qualcomm_and_local():
    for name, spec in QUALCOMM_MODEL_REGISTRY.items():
        assert spec.provider in ["qualcomm_cloud_ai", "local_engine"], f"Unauthorized provider found: {spec.provider}"

def test_router_selects_qualcomm_models():
    # Routine task -> Qualcomm Llama-3.1-8B
    r1 = QualcommModelRouter.route_task("routine_extraction")
    assert r1.provider == "qualcomm_cloud_ai"
    assert r1.selected_model == "Llama-3.1-8B"

    # Second Brain -> Qualcomm Llama-3.3-70B
    r2 = QualcommModelRouter.route_task("second_brain")
    assert r2.provider == "qualcomm_cloud_ai"
    assert r2.selected_model == "Llama-3.3-70B"

    # Flaw detection -> Qualcomm DeepSeek-R1 Distill
    r3 = QualcommModelRouter.route_task("flaw_detection")
    assert r3.provider == "qualcomm_cloud_ai"
    assert r3.selected_model == "deepseek-r1-distill-llama-70b"

    # Creative solutions -> Qualcomm Qwen-QwQ-32B
    r4 = QualcommModelRouter.route_task("creative_solutions")
    assert r4.provider == "qualcomm_cloud_ai"
    assert r4.selected_model == "Qwen-QwQ-32B"

def test_deterministic_task_spends_zero_llm_tokens():
    r = QualcommModelRouter.route_task("cleaning")
    assert r.is_deterministic is True
    assert r.selected_model == "deterministic-python"
    assert r.estimated_input_tokens == 0

@pytest.mark.asyncio
async def test_unconfigured_qualcomm_raises_honest_auth_error_no_fallback():
    client = QualcommClient()
    client.api_key = None  # Force unconfigured
    assert client.is_configured() is False

    with pytest.raises(QualcommAuthMissingError) as exc_info:
        await client.chat_completion(
            messages=[{"role": "user", "content": "test"}],
            model="Llama-3.1-8B"
        )
    # Check that error explicitly mentions Qualcomm and no third-party fallback
    assert "Qualcomm Cloud AI Playground API key is not configured" in str(exc_info.value)
    assert "no alternative LLM providers are permitted" in str(exc_info.value)
