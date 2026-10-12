import time
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.config import settings
from app.ai.model_registry import get_model_spec, calculate_estimated_cost

class QualcommInferenceResult(BaseModel):
    model: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    estimated_cost_usd: float
    is_measured: bool

class QualcommInferenceError(Exception):
    """Raised when Qualcomm Cloud AI Playground inference request fails."""
    pass

class QualcommAuthMissingError(QualcommInferenceError):
    """Raised when QUALCOMM_API_KEY is not configured."""
    pass

class QualcommClient:
    """
    Exclusive LLM Inference Provider for Sabha AI: Qualcomm Cloud AI Playground.
    Strictly interfaces with Qualcomm Cloud AI REST endpoints.
    No third-party LLMs (OpenAI, Anthropic, Gemini, Groq, etc.) are implemented or permitted.
    """

    def __init__(self):
        self.endpoint = settings.QUALCOMM_ENDPOINT.rstrip('/')
        self.api_key = settings.QUALCOMM_API_KEY

    def is_configured(self) -> bool:
        """Checks if Qualcomm Cloud AI Playground API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "Llama-3.1-8B",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> QualcommInferenceResult:
        """
        Executes chat completion strictly via Qualcomm Cloud AI Playground endpoint.
        """
        if not self.is_configured():
            raise QualcommAuthMissingError(
                "Qualcomm Cloud AI Playground API key is not configured. "
                "Please configure QUALCOMM_API_KEY in your .env file. "
                "Per architectural policy, no alternative LLM providers are permitted."
            )

        spec = get_model_spec(model)
        if not spec:
            raise QualcommInferenceError(f"Requested model '{model}' is not registered in Qualcomm Cloud AI registry.")

        url = f"{self.endpoint}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        if response_format:
            payload["response_format"] = response_format

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                error_body = response.text
                raise QualcommInferenceError(
                    f"Qualcomm Cloud AI Playground API returned HTTP {response.status_code}: {error_body}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Extract usage metrics directly from Qualcomm response if available
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            is_measured = True

            # If provider doesn't report exact token counts, approximate based on character length
            if input_tokens == 0 and output_tokens == 0:
                is_measured = False
                all_prompt_text = " ".join([m.get("content", "") for m in messages])
                input_tokens = max(1, int(len(all_prompt_text) / 3.8))
                output_tokens = max(1, int(len(content) / 3.8))

            estimated_cost = calculate_estimated_cost(model, input_tokens, output_tokens)

            return QualcommInferenceResult(
                model=model,
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                estimated_cost_usd=estimated_cost,
                is_measured=is_measured
            )

        except httpx.TimeoutException:
            raise QualcommInferenceError(
                f"Qualcomm Cloud AI Playground timed out after 60s while processing model '{model}'."
            )
        except httpx.RequestError as e:
            raise QualcommInferenceError(
                f"Network connection to Qualcomm Cloud AI Playground failed: {str(e)}"
            )

# Global singleton client
qualcomm_client = QualcommClient()
