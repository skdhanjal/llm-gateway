
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    default_model: str = "gpt-5-mini"
    request_timeout_s: float = 60.0
    
    class Config:
        env_file = ".env"
        
settings = Settings()

MODEL_PRICES: dict[str, dict[str, float]] = {
    "gpt-4o-mini":    {"input": 0.15, "output": 0.60},   # Per 1 million tokens
    "gpt-4o":         {"input": 2.50, "output": 10.00},  # Per 1 million tokens
    "gpt-4-turbo":    {"input": 10.00, "output": 30.00}, # Per 1 million tokens
    "gpt-4.1":        {"input": 2.00, "output": 8.00},   # Per 1 million tokens
    "gpt-4.1-mini":   {"input": 0.40, "output": 1.60},   # Per 1 million tokens
    "o3-mini":        {"input": 1.10, "output": 4.40},   # Per 1 million tokens
    "o4-mini":        {"input": 1.10, "output": 4.40},   # Per 1 million tokens
    "gpt-5.4":        {"input": 2.50, "output": 15.00},  # Per 1 million tokens
    "gpt-5.4-mini":   {"input": 0.75, "output": 4.50},   # Per 1 million tokens
    "gpt-5.5":        {"input": 5.00, "output": 30.00},  # Per 1 million tokens
}

PRICES_AS_OF: str = "2026-07-21"