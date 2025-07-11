import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    # Port Configuration (for Docker Compose)
    WEB_PORT: int = 8000
    REDIS_PORT: int = 6379
    REDIS_TEST_PORT: int = 6380
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Redis Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # Celery Settings
    CELERY_WORKERS: int = 1
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "data/images"
    
    # Task Settings
    TASK_MAX_RETRIES: int = 3
    TASK_RETRY_DELAY: int = 60

# Global settings instance
settings = Settings() 