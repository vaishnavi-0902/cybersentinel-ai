from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "CyberSentinel AI"
    app_env: str = "development"
    database_url: str = "sqlite:///./cybersentinel.db"
    secret_key: str = "super-secret-key-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    frontend_url: str = "http://localhost:8501"
    backend_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")


settings = Settings()
