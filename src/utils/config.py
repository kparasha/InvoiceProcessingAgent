from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from functools import lru_cache
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: Optional[str] = None
    senso_api_key: Optional[str] = None
    apify_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/invoice_processing.log"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": "",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 