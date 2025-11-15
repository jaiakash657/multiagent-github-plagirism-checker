from pydantic import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Multi-Agent Repo Analyzer"

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Database
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
