import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "data/images"
    
    # Task Settings
    TASK_MAX_RETRIES: int = 3
    TASK_RETRY_DELAY: int = 60
    
    def __init__(self, **kwargs):
        # Load test environment file if ENVIRONMENT=test
        if kwargs.get("ENVIRONMENT") == "test" or os.getenv("ENVIRONMENT") == "test":
            kwargs["_env_file"] = ".env.test"
        super().__init__(**kwargs)

# Global settings instance
settings = Settings() 