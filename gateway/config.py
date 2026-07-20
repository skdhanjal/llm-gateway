
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    default_model: str = "gpt-5-mini"
    request_timeout_s: float = 60.0
    
    class Config:
        env_file = ".env"
        
settings = Settings()