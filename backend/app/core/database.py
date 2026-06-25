import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 处理已有表新增列的兼容性（SQLite 和 MySQL 语法不同）
        _migrations = []
        if settings.DATABASE_URL.startswith("sqlite"):
            _migrations = [
                "ALTER TABLE requirements ADD COLUMN coverage_data TEXT",
                "ALTER TABLE requirements ADD COLUMN max_understanding_score INTEGER DEFAULT 0",
            ]
        elif "mysql" in settings.DATABASE_URL:
            _migrations = [
                "ALTER TABLE requirements ADD COLUMN coverage_data JSON NULL",
                "ALTER TABLE requirements ADD COLUMN max_understanding_score INTEGER DEFAULT 0",
            ]
        for sql in _migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass  # 列已存在时忽略
        await conn.commit()
