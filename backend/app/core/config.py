import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sabha AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sabha-enterprise-secret-key-production-change-in-prod-88723618")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sabha.db")
    
    # LiveKit Real-Time Audio/Video Infrastructure
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "https://sabha.livekit.cloud")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "devkey")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "secret")
    
    # EXCLUSIVE LLM INFERENCE PROVIDER: Qualcomm Cloud AI Playground
    # Strict Architecture Rule: No third-party LLMs (OpenAI, Anthropic, Gemini, Groq) are permitted.
    QUALCOMM_API_KEY: Optional[str] = os.getenv("QUALCOMM_API_KEY", None)
    QUALCOMM_ENDPOINT: str = os.getenv("QUALCOMM_ENDPOINT", "https://api.cloudai.qualcomm.com/v1")
    
    # Verified Qualcomm Cloud AI Models for Task Routing
    QUALCOMM_ROUTINE_MODEL: str = os.getenv("QUALCOMM_ROUTINE_MODEL", "Llama-3.1-8B")
    QUALCOMM_COMPLEX_MODEL: str = os.getenv("QUALCOMM_COMPLEX_MODEL", "Llama-3.3-70B")
    QUALCOMM_REASONING_MODEL: str = os.getenv("QUALCOMM_REASONING_MODEL", "deepseek-r1-distill-llama-70b")
    QUALCOMM_CREATIVE_MODEL: str = os.getenv("QUALCOMM_CREATIVE_MODEL", "Qwen-QwQ-32B")
    
    # External Web Search Provider (for research assistance; strictly search retrieval, LLM synthesis is Qualcomm)
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY", None)
    
    # Token Budget and Safety Guardrails
    MAX_MEETING_BUDGET_USD: float = float(os.getenv("MAX_MEETING_BUDGET_USD", "2.50"))
    MAX_INPUT_TOKENS_PER_REQ: int = int(os.getenv("MAX_INPUT_TOKENS_PER_REQ", "16000"))
    MAX_OUTPUT_TOKENS_PER_REQ: int = int(os.getenv("MAX_OUTPUT_TOKENS_PER_REQ", "4096"))
    MAX_RESEARCH_CALLS_PER_MEETING: int = int(os.getenv("MAX_RESEARCH_CALLS_PER_MEETING", "5"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = {"case_sensitive": True, "extra": "allow"}

settings = Settings()
