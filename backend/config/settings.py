import os
from pydantic_settings import BaseSettings

# Compute absolute path to the .env file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")

print("LOADING ENV FROM:", ENV_PATH)  # Debug line, remove later

class Settings(BaseSettings):
    APP_NAME: str = "Multi-Agent Repo Analyzer"

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    DATABASE_URL: str

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
