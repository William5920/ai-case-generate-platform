from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "智能测试用例平台"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000"]
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "knowledge_base"
    UPLOAD_DIR: str = "./uploads"

    DATABASE_URL: str = "sqlite:///./test_case_platform.db"

    JWT_SECRET_KEY: str = "ai-case-platform-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
