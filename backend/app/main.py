from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import knowledge_base, test_design
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(
    title="智能测试用例平台API",
    version="1.0.0",
    description="银行软件测试人员AI驱动的测试用例生成平台"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["knowledge_base"])
app.include_router(test_design.router, prefix="/api/v1/test-design", tags=["test_design"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "智能测试用例平台API"}
