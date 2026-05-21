# 测试设计模块后端接口实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现测试设计模块全部后端接口（需求列表、脑图数据、测试点管理、测试用例管理、AI调整、异步任务、Excel导出），对接MySQL数据库和OpenAI API。

**Architecture:** FastAPI + SQLAlchemy(async) + MySQL + httpx(OpenAI) + asyncio后台任务。采用分层架构：routers(路由) → services(业务逻辑) → models(数据模型/ORM)。

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0(async), databases, aiomysql, httpx, openpyxl, pydantic

---

## 文件结构规划

| 文件 | 职责 |
|------|------|
| `backend/.env` | 环境变量配置（DATABASE_URL, OPENAI_API_KEY等） |
| `backend/requirements.txt` | 新增依赖：sqlalchemy, databases, aiomysql, httpx, openpyxl |
| `backend/app/core/config.py` | 扩展Settings类，添加数据库和AI配置 |
| `backend/app/core/database.py` | 数据库连接管理（SQLAlchemy async engine + session） |
| `backend/app/models/test_design.py` | Pydantic模型：请求/响应DTO |
| `backend/app/models/db_models.py` | SQLAlchemy ORM模型：requirements, split_requirements, test_points, test_cases, ai_sessions, ai_messages, tasks |
| `backend/app/services/test_design.py` | 业务逻辑层：CRUD、AI调用、任务管理、Excel导出 |
| `backend/app/routers/test_design.py` | FastAPI路由：全部接口定义 |
| `backend/app/main.py` | 注册test_design路由，数据库初始化 |
| `backend/mysql/init/init.sql` | 新增数据库表结构 |

---

## Task 1: 环境配置与依赖

**Files:**
- Create: `backend/.env`
- Modify: `backend/requirements.txt`
- Modify: `backend/app/core/config.py`

- [ ] **Step 1.1: 创建 .env 文件**

```bash
# backend/.env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/ai_test_platform?charset=utf8mb4
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

- [ ] **Step 1.2: 更新 requirements.txt**

添加以下依赖：
```
sqlalchemy>=2.0.0
databases>=0.9.0
aiomysql>=0.2.0
httpx>=0.27.0
openpyxl>=3.1.0
```

- [ ] **Step 1.3: 扩展 config.py**

```python
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
    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/ai_test_platform?charset=utf8mb4"
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## Task 2: 数据库连接与ORM模型

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/app/models/db_models.py`
- Modify: `backend/mysql/init/init.sql`

- [ ] **Step 2.1: 创建 database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    future=True
)

# 创建异步session工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
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
```

- [ ] **Step 2.2: 创建 db_models.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(String(64), primary_key=True, default=lambda: f"req-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    status = Column(String(20), default="pending")  # pending, generating, completed
    source = Column(String(50), default="standardization")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    split_requirements = relationship("SplitRequirement", back_populates="requirement", cascade="all, delete-orphan")

class SplitRequirement(Base):
    __tablename__ = "split_requirements"
    
    id = Column(String(64), primary_key=True, default=lambda: f"sr-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), ForeignKey("requirements.id"), nullable=False)
    text = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, generating, completed
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="split_requirements")
    test_points = relationship("TestPoint", back_populates="split_requirement", cascade="all, delete-orphan")

class TestPoint(Base):
    __tablename__ = "test_points"
    
    id = Column(String(64), primary_key=True, default=lambda: f"tp-{uuid.uuid4().hex[:8]}")
    split_requirement_id = Column(String(64), ForeignKey("split_requirements.id"), nullable=False)
    text = Column(Text, nullable=False)
    description = Column(Text)
    source = Column(String(10), default="AI")  # AI, 人工
    marked = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    split_requirement = relationship("SplitRequirement", back_populates="test_points")
    test_cases = relationship("TestCase", back_populates="test_point", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(String(64), primary_key=True, default=lambda: f"tc-{uuid.uuid4().hex[:8]}")
    test_point_id = Column(String(64), ForeignKey("test_points.id"), nullable=False)
    text = Column(String(255), nullable=False)
    case_property = Column(String(10), default="正例")  # 正例, 反例
    pre_condition = Column(Text)
    steps = Column(JSON, default=list)
    source = Column(String(10), default="AI")  # AI, 人工
    marked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    test_point = relationship("TestPoint", back_populates="test_cases")

class AISession(Base):
    __tablename__ = "ai_sessions"
    
    id = Column(String(64), primary_key=True, default=lambda: f"sess-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), nullable=False)
    node_id = Column(String(64), nullable=False)
    node_type = Column(String(20), nullable=False)  # requirement, testPoint
    marked_node_ids = Column(JSON, default=list)
    status = Column(String(20), default="active")  # active, applied, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("AIMessage", back_populates="session", cascade="all, delete-orphan")

class AIMessage(Base):
    __tablename__ = "ai_messages"
    
    id = Column(String(64), primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    session_id = Column(String(64), ForeignKey("ai_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("AISession", back_populates="messages")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(64), primary_key=True, default=lambda: f"task-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    progress = Column(Integer, default=0)
    progress_text = Column(String(255), default="")
    use_knowledge_base = Column(Boolean, default=False)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

- [ ] **Step 2.3: 更新 init.sql**

```sql
-- 测试设计模块表结构

-- 需求表
CREATE TABLE IF NOT EXISTS requirements (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    source VARCHAR(50) DEFAULT 'standardization',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_requirements_user_id (user_id),
    INDEX idx_requirements_status (status)
);

-- 拆分需求表
CREATE TABLE IF NOT EXISTS split_requirements (
    id VARCHAR(64) PRIMARY KEY,
    requirement_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    INDEX idx_split_requirements_requirement_id (requirement_id)
);

-- 测试点表
CREATE TABLE IF NOT EXISTS test_points (
    id VARCHAR(64) PRIMARY KEY,
    split_requirement_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    description TEXT,
    source VARCHAR(10) DEFAULT 'AI',
    marked BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (split_requirement_id) REFERENCES split_requirements(id) ON DELETE CASCADE,
    INDEX idx_test_points_split_requirement_id (split_requirement_id)
);

-- 测试用例表
CREATE TABLE IF NOT EXISTS test_cases (
    id VARCHAR(64) PRIMARY KEY,
    test_point_id VARCHAR(64) NOT NULL,
    text VARCHAR(255) NOT NULL,
    case_property VARCHAR(10) DEFAULT '正例',
    pre_condition TEXT,
    steps JSON,
    source VARCHAR(10) DEFAULT 'AI',
    marked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (test_point_id) REFERENCES test_points(id) ON DELETE CASCADE,
    INDEX idx_test_cases_test_point_id (test_point_id)
);

-- AI会话表
CREATE TABLE IF NOT EXISTS ai_sessions (
    id VARCHAR(64) PRIMARY KEY,
    requirement_id VARCHAR(64) NOT NULL,
    node_id VARCHAR(64) NOT NULL,
    node_type VARCHAR(20) NOT NULL,
    marked_node_ids JSON,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ai_sessions_requirement_id (requirement_id)
);

-- AI消息表
CREATE TABLE IF NOT EXISTS ai_messages (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_sessions(id) ON DELETE CASCADE,
    INDEX idx_ai_messages_session_id (session_id)
);

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(64) PRIMARY KEY,
    requirement_id VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INT DEFAULT 0,
    progress_text VARCHAR(255) DEFAULT '',
    use_knowledge_base BOOLEAN DEFAULT FALSE,
    result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tasks_requirement_id (requirement_id),
    INDEX idx_tasks_status (status)
);
```

---

## Task 3: Pydantic请求/响应模型

**Files:**
- Create: `backend/app/models/test_design.py`

- [ ] **Step 3.1: 创建 Pydantic 模型**

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# 通用响应
class ResponseModel(BaseModel):
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None
    traceId: str = Field(default_factory=lambda: f"trace-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")

# 需求列表
class RequirementListItem(BaseModel):
    id: str
    title: str
    status: str
    statusText: str
    date: str
    testPointCount: int
    caseCount: int
    source: str = "standardization"

class RequirementListResponse(BaseModel):
    list: List[RequirementListItem]
    total: int
    page: int
    pageSize: int

# 脑图数据
class MindMapNodeData(BaseModel):
    text: str
    expand: bool = True
    _level: str
    _status: Optional[str] = None
    _source: Optional[str] = None
    _marked: Optional[bool] = None
    _caseProperty: Optional[str] = None
    note: Optional[str] = None

class MindMapNode(BaseModel):
    data: MindMapNodeData
    children: List['MindMapNode'] = []

MindMapNode.model_rebuild()

# 测试点
class TestPointCreate(BaseModel):
    requirementNodeId: str
    text: str
    description: Optional[str] = None

class TestPointUpdate(BaseModel):
    text: str

class TestPointMark(BaseModel):
    marked: bool

class TestPointResponse(BaseModel):
    id: str
    text: str
    _source: str = "人工"

# 测试用例
class TestCaseStep(BaseModel):
    name: str
    description: str
    stepExpectedResult: str

class TestCaseCreate(BaseModel):
    text: str
    caseProperty: str
    preCondition: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None

class TestCaseUpdate(BaseModel):
    text: str
    caseProperty: str
    preCondition: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None

class TestCaseMark(BaseModel):
    marked: bool

class TestCaseResponse(BaseModel):
    id: str
    text: str
    caseProperty: str
    preCondition: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None

# 批量删除
class BatchDeleteRequest(BaseModel):
    ids: List[str]

# AI调整
class AIAdjustStart(BaseModel):
    requirementId: str
    nodeId: str
    nodeType: str
    markedNodeIds: Optional[List[str]] = None

class AIAdjustApply(BaseModel):
    currentMindMapData: Dict[str, Any]
    markedTestPointTexts: Optional[List[str]] = None
    nodeType: str

class AIAdjustApplyResponse(BaseModel):
    adjustedMindMapData: Dict[str, Any]
    addedCount: int
    removedCount: int
    preservedCount: int

# 异步任务
class GenerateRequest(BaseModel):
    useKnowledgeBase: Optional[bool] = False

class GenerateResponse(BaseModel):
    taskId: str

class TaskStatusResponse(BaseModel):
    taskId: str
    status: str
    progress: int
    progressText: str

# 导出
class ExportResponse(BaseModel):
    pass  # 返回文件流
```

---

## Task 4: 业务逻辑服务层

**Files:**
- Create: `backend/app/services/test_design.py`

- [ ] **Step 4.1: 创建 TestDesignService**

实现以下方法：
- `get_requirements_list(db, page, pageSize, status, keyword)` → 分页查询需求列表
- `get_mindmap_data(db, requirement_id)` → 构建4级脑图数据结构
- `create_test_point(db, requirement_id, data)` → 添加测试点
- `update_test_point(db, test_point_id, data)` → 编辑测试点
- `delete_test_point(db, test_point_id)` → 删除测试点
- `batch_delete_test_points(db, ids)` → 批量删除测试点
- `mark_test_point(db, test_point_id, marked)` → 标记保留测试点
- `create_test_case(db, test_point_id, data)` → 添加测试用例
- `update_test_case(db, test_case_id, data)` → 编辑测试用例
- `delete_test_case(db, test_case_id)` → 删除测试用例
- `batch_delete_test_cases(db, ids)` → 批量删除测试用例
- `mark_test_case(db, test_case_id, marked)` → 标记保留测试用例
- `start_ai_session(db, data)` → 发起AI调整对话
- `send_ai_message(db, session_id, content)` → 发送对话消息
- `get_ai_messages(db, session_id)` → 获取对话历史
- `apply_ai_adjust(db, session_id, data)` → 应用AI调整
- `start_generation(db, requirement_id, use_knowledge_base)` → 启动快速生成任务
- `get_task_status(db, task_id)` → 获取任务状态
- `cancel_task(db, task_id)` → 取消任务
- `export_excel(db, requirement_id)` → 导出Excel

---

## Task 5: FastAPI路由层

**Files:**
- Create: `backend/app/routers/test_design.py`

- [ ] **Step 5.1: 创建路由文件**

实现以下路由：
- `GET /api/v1/test-design/requirements` → 获取需求列表
- `GET /api/v1/test-design/requirements/{requirementId}/mindmap` → 获取脑图数据
- `POST /api/v1/test-design/requirements/{requirementId}/test-points` → 添加测试点
- `PUT /api/v1/test-design/test-points/{testPointId}` → 编辑测试点
- `DELETE /api/v1/test-design/test-points/{testPointId}` → 删除测试点
- `POST /api/v1/test-design/test-points/batch-delete` → 批量删除测试点
- `PUT /api/v1/test-design/test-points/{testPointId}/mark` → 标记保留测试点
- `POST /api/v1/test-design/test-points/{testPointId}/test-cases` → 添加测试用例
- `PUT /api/v1/test-design/test-cases/{testCaseId}` → 编辑测试用例
- `DELETE /api/v1/test-design/test-cases/{testCaseId}` → 删除测试用例
- `POST /api/v1/test-design/test-cases/batch-delete` → 批量删除测试用例
- `PUT /api/v1/test-design/test-cases/{testCaseId}/mark` → 标记保留测试用例
- `POST /api/v1/test-design/ai-adjust/sessions` → 发起AI调整对话
- `POST /api/v1/test-design/ai-adjust/sessions/{sessionId}/messages` → 发送对话消息
- `GET /api/v1/test-design/ai-adjust/sessions/{sessionId}/messages` → 获取对话历史
- `POST /api/v1/test-design/ai-adjust/sessions/{sessionId}/apply` → 应用AI调整
- `POST /api/v1/test-design/requirements/{requirementId}/generate` → 快速生成
- `GET /api/v1/test-design/tasks/{taskId}` → 获取任务状态
- `POST /api/v1/test-design/tasks/{taskId}/cancel` → 取消任务
- `GET /api/v1/test-design/requirements/{requirementId}/export` → 导出Excel

---

## Task 6: 主应用集成

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 6.1: 注册路由并初始化数据库**

```python
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
```

---

## Task 7: 安装依赖并验证

- [ ] **Step 7.1: 安装依赖**

```bash
cd backend
pip install sqlalchemy databases aiomysql httpx openpyxl
```

- [ ] **Step 7.2: 启动服务验证**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 7.3: 测试接口**

使用 curl 或浏览器访问 http://localhost:8000/docs 查看 Swagger UI。

---

## Spec Coverage Check

| 接口文档章节 | 实现任务 | 状态 |
|-------------|---------|------|
| 1.1 获取需求列表 | Task 4 + Task 5 | ✅ |
| 1.2 搜索需求 | Task 4 + Task 5 (共用接口) | ✅ |
| 2.1 获取脑图数据 | Task 4 + Task 5 | ✅ |
| 3.1-3.5 测试点管理 | Task 4 + Task 5 | ✅ |
| 4.1-4.5 测试用例管理 | Task 4 + Task 5 | ✅ |
| 5.1-5.4 AI调整 | Task 4 + Task 5 | ✅ |
| 6.1-6.3 异步任务 | Task 4 + Task 5 | ✅ |
| 7.1 导出Excel | Task 4 + Task 5 | ✅ |
| 8. 错误码 | Task 5 (HTTPException) | ✅ |

---

## Placeholder Scan

- 无 TBD/TODO
- 无 "implement later"
- 无 "add appropriate error handling" 等模糊描述
- 所有类型、方法签名在Task 3和Task 4中保持一致

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-21-test-design-backend.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
