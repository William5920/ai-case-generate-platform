from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.routers import knowledge_base, auth, test_design
from app.routers import template_router, requirement_router, explore_router
from app.routers import standardize_router, version_router, split_router
from app.core.config import settings
from app.core.database import init_db
from app.models import user

app = FastAPI(
    title="智能测试用例平台API",
    version="1.0.0",
    description="银行软件测试人员AI驱动的测试用例生成平台"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge", tags=["knowledge_base"])
app.include_router(test_design.router, prefix="/api/v1/test-design", tags=["test_design"])

app.include_router(template_router.router, prefix="/api/v1", tags=["模板管理"])
app.include_router(requirement_router.router, prefix="/api", tags=["需求管理"])
app.include_router(explore_router.router, prefix="/api/v1", tags=["需求探索"])
app.include_router(standardize_router.router, prefix="/api", tags=["文档标准化"])
app.include_router(standardize_router.router, prefix="/api/v1", tags=["文档标准化"])
app.include_router(version_router.router, prefix="/api/v1", tags=["版本管理"])
app.include_router(split_router.router, prefix="/api/v1", tags=["需求拆分"])

upload_dir = getattr(settings, "UPLOAD_DIR", "uploads")
os.makedirs(upload_dir, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "智能测试用例平台API"}
