from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str = ""
    model: str = "gpt-4o-mini"
    max_history: int = 20

    class Config:
        env_file = BASE_DIR / ".env"


settings = Settings()
