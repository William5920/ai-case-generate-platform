from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "智能测试用例平台"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000"]
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "knowledge_base"
    UPLOAD_DIR: str = "./uploads"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+asyncmy://root:root123456@127.0.0.1:3306/ai_case_platform?charset=utf8mb4"
    
    # JWT配置
    JWT_SECRET_KEY: str = "ai-case-platform-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MODEL_ANALYZE: str = "gpt-4o-mini"
    OPENAI_MODEL_GENERATE: str = "gpt-4o"
    OPENAI_MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
