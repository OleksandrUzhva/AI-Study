from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=str(BASE_DIR / ".env"))

    openai_api_key: str
    anthropic_api_key: str = ""
    model: str = "gpt-4o-mini"
    max_history: int = 20


settings = Settings()
