from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "智能测试用例平台"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000"]
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "knowledge_base"
    UPLOAD_DIR: str = "./uploads"

    DATABASE_URL: str = "mysql+asyncmy://root:Zjy!2223137@127.0.0.1:3306/ai_case_platform?charset=utf8mb4"

    JWT_SECRET_KEY: str = "ai-case-platform-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.deepseek.com"
    OPENAI_MODEL: str = "deepseek-chat"
    OPENAI_MODEL_ANALYZE: str = "deepseek-chat"
    OPENAI_MODEL_GENERATE: str = "deepseek-chat"
    OPENAI_MAX_RETRIES: int = 3

    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = "https://api.siliconflow.cn/v1"
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DIM: int = 1024

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
