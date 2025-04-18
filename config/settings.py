# app/config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Backend Developer Evaluation Task for Blockstak"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    FASTAPI_HOST_PORT: int = 8000
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7
    WHITE_LIST: str = "http://localhost:8000"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = None
    MYSQL_USER: str = None
    MYSQL_PASSWORD: str = None
    NEWS_API_KEY: str = None

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
