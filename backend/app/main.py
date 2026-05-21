from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import knowledge_base, auth
from app.core.config import settings
from app.core.database import engine, Base
from app.models import user

Base.metadata.create_all(bind=engine)

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
app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["knowledge_base"])

@app.get("/")
async def root():
    return {"message": "智能测试用例平台API"}
