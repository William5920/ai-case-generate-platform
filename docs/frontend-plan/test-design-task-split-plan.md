# 测试设计模块 - 任务拆分与状态流转改造方案

> **For agentic workers:** 按 Task 顺序逐个实现，每个 Task 内的 Step 使用 checkbox (`- [ ]`) 语法跟踪进度。

**Goal:** 将测试设计模块的"一把梭"生成任务拆分为「生成测试点」和「生成用例」两个独立异步任务，引入 XMind 导入导出支持线下评审流程，重新设计完整状态流转机。

**Architecture:** 以 `Requirement.status` 作为单一业务状态来源，`Task` 表仅记录异步任务执行情况。引入 `task_type` 字段区分任务类型，取消/失败时完全回滚该批次数据。

**Tech Stack:** Python/FastAPI/Vue 2/simple-mind-map/SQLAlchemy Async

---

## 一、核心链路

```
生成测试点 → 导出XMind → 线下评审+本地调整 → 导入XMind更新测试点 → 生成用例
```

---

## 二、Requirement.status 状态机

```
                            ┌── 用户取消 ────────────────────────────────┐
                            │  → 删除该需求下所有测试点                     │
                            │  → 回退                                     │
                            ↓                                             │
confirmed ──────→ generating_points ──────→ points_generated ──────→ generating_cases ──────→ completed
  │                    │  失败                  │   用户取消                │  失败                  │
  │                    │  → 删除所有测试点      │   → 删除所有用例          │  → 删除所有用例        │
  │                    ↓                       │   → 回退                 ↓                       │
  │                  failed                    ↓                     failed                     │
  │                    │                  points_generated             │                         │
  │                    │                       │                       │                         │
  │                    └── 重试 ──→ generating_points                   └── 重试 ──→ generating_cases
  │                                              │
  │                                  导入XMind（全量同步）
  │                                  不改变 status
  │
  └── 可发起 Task 1
```

### 各状态详情

| status | 需求列表显示 | 工具栏按钮 | 脑图内容 |
|--------|-------------|-----------|---------|
| `confirmed` | 待生成测试点 | `[生成测试点]` | 需求→拆分需求树 |
| `generating_points` | 测试点生成中... + 进度% | 进度条 + `[取消]` | 只读 |
| `points_generated` | 测试点已生成 | `[导出XMind]` `[导入XMind]` `[生成用例 ▾]` | 需求→拆分需求→测试点 |
| `generating_cases` | 用例生成中... + 进度% | 进度条 + `[取消]` | 测试点，用例逐步追加 |
| `completed` | 已完成 | `[导出Excel]` `[重新生成 ▾]` | 完整脑图 |
| `failed` | 生成失败 | `[重试]` + 失败原因 | 已回滚数据 |

### 取消/失败时的数据回滚

| 场景 | 数据操作 | Requirement.status 变迁 |
|------|---------|------------------------|
| 取消 Task 1 | 删除该需求下所有测试点（级联删除用例） | `generating_points` → `confirmed` |
| 取消 Task 2 | 删除该需求下所有用例 | `generating_cases` → `points_generated` |
| Task 1 失败 | 同取消 | `generating_points` → `failed` |
| Task 2 失败 | 同取消 | `generating_cases` → `failed` |

---

## 三、数据库变更

### 3.1 Task 表新增字段

```sql
ALTER TABLE tasks ADD COLUMN task_type VARCHAR(30) DEFAULT NULL;
```

| task_type 值 | 说明 |
|-------------|------|
| `points_generation` | 测试点生成任务 |
| `cases_generation` | 用例生成任务 |

### 3.2 TestCase 表新增字段（可选，用于增量判断）

不需要新增字段。判断"测试点是否已有用例"用 `select count(TestCase.id).where(TestCase.test_point_id == tp_id)` 即可。

---

## 四、后端改动

### 文件影响范围

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/models/db_models.py` | 修改 | Task 新增 task_type 字段 |
| `backend/app/models/test_design.py` | 修改 | 新增请求/响应模型 |
| `backend/app/agents/orchestrator.py` | 修改 | 拆分 run 为 run_points / run_cases |
| `backend/app/services/test_design.py` | 修改 | 核心改造：拆分任务、XMind导入导出、回滚、状态管理 |
| `backend/app/routers/test_design.py` | 修改 | 新增路由、调整已有路由 |
| `backend/app/services/xmind_service.py` | **新建** | XMind 导入导出逻辑 |

---

### Task 1: 数据库模型变更

**Files:**
- Modify: `backend/app/models/db_models.py`

**Step 1: Task 表添加 task_type 字段**

在 Task 类中 `use_knowledge_base` 字段之后添加：

```python
class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, default=lambda: f"task-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), nullable=False)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    progress_text = Column(String(255), default="")
    use_knowledge_base = Column(Boolean, default=False)
    task_type = Column(String(30), nullable=True)   # 新增：points_generation / cases_generation
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### Task 2: Pydantic 模型变更

**Files:**
- Modify: `backend/app/models/test_design.py`

**Step 1: GenerateRequest 增加 taskType**

```python
class GenerateRequest(BaseModel):
    useKnowledgeBase: Optional[bool] = False
    taskType: Optional[str] = "points_generation"  # points_generation / cases_generation / cases_regeneration
```

**Step 2: GenerateResponse 增加 taskType**

```python
class GenerateResponse(BaseModel):
    taskId: str
    taskType: str  # 新增
```

**Step 3: TaskStatusResponse 增加 taskType**

```python
class TaskStatusResponse(BaseModel):
    taskId: str
    requirementId: str = ""
    status: str
    progress: int
    progressText: str
    taskType: Optional[str] = None  # 新增
```

**Step 4: 新增 XMind 导入相关模型**

```python
class XMindImportRequest(BaseModel):
    pass  # 由文件上传处理

class XMindImportPreview(BaseModel):
    """导入前预览变更摘要"""
    addedCount: int
    updatedCount: int
    deletedCount: int
    addedItems: List[Dict[str, Any]]    # 新增的测试点简要信息
    updatedItems: List[Dict[str, Any]]  # 更新的测试点简要信息
    deletedItems: List[Dict[str, Any]]  # 待删除的测试点简要信息
    hasCasesConflict: bool = False      # 是否有待删除测试点已关联用例
    conflictTestPointIds: List[str] = [] # 有冲突的测试点ID
```

---

### Task 3: Orchestrator 拆分

**Files:**
- Modify: `backend/app/agents/orchestrator.py`

**Step 1: 将现有 `run()` 拆分为 `run_points()` + `run_cases()`**

```python
class TestDesignOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.kb_service = KnowledgeBaseService()
        self.rag_service = RAGService(self.kb_service, self.llm_client)

    async def run_points(
        self,
        db: AsyncSession,
        requirement_id: str,
        use_knowledge_base: bool,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        """仅生成测试点，不生成用例"""
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        split_reqs = result.scalars().all()
        total = len(split_reqs)

        if total == 0:
            if progress_callback:
                await progress_callback(100, "无需生成: 没有拆分需求")
            await db.execute(
                update(Requirement)
                .where(Requirement.id == requirement_id)
                .values(status="points_generated")
            )
            await db.commit()
            return

        for i, sr in enumerate(split_reqs):
            progress = int((i / total) * 100)
            if progress_callback:
                await progress_callback(progress, f"正在生成测试点：{sr.text[:20]}...")

            test_points_data = await run_test_point_agent(
                requirement_text=sr.text,
                use_knowledge_base=use_knowledge_base,
                llm_client=self.llm_client,
                rag_service=self.rag_service,
            )

            if not test_points_data:
                test_points_data = [
                    {"text": "功能验证", "category": "功能验证", "rationale": "默认测试点"},
                    {"text": "边界条件验证", "category": "边界条件", "rationale": "默认测试点"},
                    {"text": "异常处理验证", "category": "异常处理", "rationale": "默认测试点"},
                ]

            for tp_data in test_points_data:
                tp = TestPoint(
                    split_requirement_id=sr.id,
                    text=tp_data.get("text", "未命名测试点"),
                    description=tp_data.get("rationale", ""),
                    source="AI",
                    status="completed",
                )
                db.add(tp)
                await db.commit()
            # 不再生成用例

        if progress_callback:
            await progress_callback(100, "测试点生成完成")

        await db.execute(
            update(Requirement)
            .where(Requirement.id == requirement_id)
            .values(status="points_generated")
        )
        await db.commit()

    async def run_cases(
        self,
        db: AsyncSession,
        requirement_id: str,
        use_knowledge_base: bool,
        regenerate_all: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        """生成测试用例。默认增量模式，仅对无子用例的测试点生成"""
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .options(selectinload(SplitRequirement.test_points))
        )
        split_reqs = result.scalars().all()

        # 收集所有需要生成用例的测试点
        tp_to_generate = []
        for sr in split_reqs:
            for tp in sr.test_points:
                if regenerate_all:
                    tp_to_generate.append((sr, tp))
                else:
                    # 增量模式：检查是否已有用例
                    case_count = await db.execute(
                        select(func.count(TestCase.id))
                        .where(TestCase.test_point_id == tp.id)
                    )
                    if case_count.scalar() == 0:
                        tp_to_generate.append((sr, tp))

        total = len(tp_to_generate)
        if total == 0:
            if progress_callback:
                await progress_callback(100, "所有测试点已存在用例，无需生成")
            await db.execute(
                update(Requirement)
                .where(Requirement.id == requirement_id)
                .values(status="completed")
            )
            await db.commit()
            return

        for i, (sr, tp) in enumerate(tp_to_generate):
            progress = int((i / total) * 100)
            if progress_callback:
                await progress_callback(progress, f"正在生成用例：{tp.text[:20]}...")

            # 如果 regenerate_all，先清理已有用例
            if regenerate_all:
                await db.execute(
                    delete(TestCase).where(TestCase.test_point_id == tp.id)
                )

            # 从 TestPoint 表中查询 description 作为 category
            test_cases_data = await run_test_case_agent(
                test_point_text=tp.text,
                test_point_category=tp.description or "功能验证",
                requirement_context=sr.text,
                use_knowledge_base=use_knowledge_base,
                llm_client=self.llm_client,
                rag_service=self.rag_service,
            )

            if not test_cases_data:
                test_cases_data = [
                    {
                        "name": f"{tp.text}-正例",
                        "property": "正例",
                        "pre_condition": "系统正常运行",
                        "steps": [{"name": "执行操作", "description": "按正常流程执行", "stepExpectedResult": "操作成功"}],
                    },
                    {
                        "name": f"{tp.text}-反例",
                        "property": "反例",
                        "pre_condition": "系统正常运行",
                        "steps": [{"name": "异常操作", "description": "输入异常数据", "stepExpectedResult": "系统提示错误"}],
                    },
                ]

            for case_data in test_cases_data:
                steps = case_data.get("steps", [])
                tc = TestCase(
                    test_point_id=tp.id,
                    text=case_data.get("name", "未命名用例"),
                    case_property=case_data.get("property", "正例"),
                    pre_condition=case_data.get("pre_condition", ""),
                    steps=steps,
                    source="AI",
                )
                db.add(tc)
                await db.commit()

        if progress_callback:
            await progress_callback(100, "用例生成完成")

        await db.execute(
            update(Requirement)
            .where(Requirement.id == requirement_id)
            .values(status="completed")
        )
        await db.commit()

    async def close(self):
        await self.llm_client.close()
```

---

### Task 4: test_design_service.py 核心改造

**Files:**
- Modify: `backend/app/services/test_design.py`

**Step 1: get_requirements_list - 改用 Requirement.status 直读，不再关联 Task 表**

将现有的 base_filters 和状态映射逻辑改为：

```python
async def get_requirements_list(
    self, db: AsyncSession, page: int, pageSize: int, status: Optional[str], keyword: Optional[str]
) -> RequirementListResponse:
    # 基础过滤：直接使用 Requirement.status
    base_filters = [
        Requirement.status.in_(["confirmed", "generating_points", "points_generated", "generating_cases", "completed", "failed"]),
    ]
    if keyword:
        base_filters.append(Requirement.title.contains(keyword))

    # status 筛选映射
    status_mapping = {
        "pending": "confirmed",
        "generating": ["generating_points", "generating_cases"],
        "completed": "completed",
        "failed": "failed",
        "cancelled": "failed",  # 取消现在回退到稳定状态，不再有 cancelled
    }
    if status and status in status_mapping:
        mapped = status_mapping[status]
        if isinstance(mapped, list):
            base_filters.append(Requirement.status.in_(mapped))
        else:
            base_filters.append(Requirement.status == mapped)

    base_query = select(Requirement).where(and_(*base_filters)).order_by(Requirement.updated_at.desc())
    result = await db.execute(base_query)
    all_requirements = result.scalars().all()

    # 对于 generating_points / generating_cases 状态，批量查询对应 running task 的进度
    req_ids = [r.id for r in all_requirements]
    req_task_progress = {}
    if req_ids:
        task_subq = (
            select(
                Task.requirement_id,
                Task.progress,
                func.row_number().over(
                    partition_by=Task.requirement_id,
                    order_by=Task.created_at.desc()
                ).label('rn')
            ).where(
                and_(
                    Task.requirement_id.in_(req_ids),
                    Task.status.in_(["running", "pending"])
                )
            )
        ).subquery()
        task_query = select(task_subq.c.requirement_id, task_subq.c.progress).where(task_subq.c.rn == 1)
        task_result = await db.execute(task_query)
        for row in task_result:
            req_task_progress[row[0]] = row[1]

    # status -> statusText 映射
    status_text_map = {
        "confirmed": "待生成测试点",
        "generating_points": "测试点生成中",
        "points_generated": "测试点已生成",
        "generating_cases": "用例生成中",
        "completed": "已完成",
        "failed": "生成失败",
    }

    items = []
    for r in all_requirements:
        progress = req_task_progress.get(r.id, 0)
        st = r.status or "confirmed"
        status_text = status_text_map.get(st, "待生成测试点")
        if st in ("generating_points", "generating_cases") and progress > 0:
            status_text += f" {progress}%"

        items.append(RequirementListItem(
            id=r.id,
            title=r.title,
            status=st,
            statusText=status_text,
            date=r.updated_at.strftime("%Y-%m-%d %H:%M") if r.updated_at else "",
            testPointCount=await self._get_test_point_count(db, r.id),
            caseCount=await self._get_case_count(db, r.id),
            source=r.source or "standardization",
        ))

    # 分页
    total = len(items)
    start = (page - 1) * pageSize
    end = start + pageSize
    page_items = items[start:end]

    return RequirementListResponse(
        list=page_items,
        total=total,
        page=page,
        pageSize=pageSize,
    )
```

**Step 2: 删除 generate 状态映射中的 cancelled 项**

```python
# 不再需要 cancelled 映射，因为取消现在回退到上一个稳定状态
```

**Step 3: 拆分 start_generation**

```python
async def start_generation(
    self, db: AsyncSession, requirement_id: str, 
    use_knowledge_base: bool, task_type: str = "points_generation"
) -> GenerateResponse:
    """启动生成任务。task_type: points_generation / cases_generation / cases_regeneration"""
    
    # 根据 task_type 设置目标状态
    target_status_map = {
        "points_generation": "generating_points",
        "cases_generation": "generating_cases",
        "cases_regeneration": "generating_cases",
    }
    target_status = target_status_map.get(task_type, "generating_points")
    
    await db.execute(
        update(Requirement).where(Requirement.id == requirement_id).values(status=target_status)
    )

    task = Task(
        requirement_id=requirement_id,
        status="pending",
        progress=0,
        progress_text="准备生成...",
        use_knowledge_base=use_knowledge_base,
        task_type=task_type,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    bg_task = asyncio.create_task(
        self._run_generation(task.id, requirement_id, use_knowledge_base, task_type)
    )
    self.tasks[task.id] = bg_task

    return GenerateResponse(taskId=task.id, taskType=task_type)
```

**Step 4: 改造 _run_generation**

将现有 `_run_generation` 改为根据 `task_type` 调用不同的 orchestrator 方法：

```python
async def _run_generation(
    self, task_id: str, requirement_id: str, 
    use_knowledge_base: bool, task_type: str = "points_generation"
):
    from app.agents.orchestrator import TestDesignOrchestrator
    from app.core.database import AsyncSessionLocal

    orchestrator = TestDesignOrchestrator()
    async with AsyncSessionLocal() as db:
        try:
            # 检查任务是否已被取消
            result = await db.execute(
                select(Task.status).where(Task.id == task_id)
            )
            current_status = result.scalar()
            if current_status and current_status not in ("pending", "running"):
                logger.info(f"Task {task_id} was cancelled before execution, skipping")
                return

            await db.execute(
                update(Task).where(Task.id == task_id).values(
                    status="running", progress=5, 
                    progress_text="正在分析需求结构..."
                )
            )
            await db.commit()

            async def progress_callback(progress: int, text: str):
                check = await db.execute(select(Task.status).where(Task.id == task_id))
                if check.scalar() not in ("running", "pending"):
                    raise Exception("TASK_CANCELLED")
                await db.execute(
                    update(Task).where(Task.id == task_id).values(
                        progress=progress, progress_text=text
                    )
                )
                await db.commit()

            # 根据 task_type 调用不同的方法
            is_cases = task_type in ("cases_generation", "cases_regeneration")
            if is_cases:
                regenerate_all = (task_type == "cases_regeneration")
                await orchestrator.run_cases(
                    db=db,
                    requirement_id=requirement_id,
                    use_knowledge_base=use_knowledge_base,
                    regenerate_all=regenerate_all,
                    progress_callback=progress_callback,
                )
            else:
                await orchestrator.run_points(
                    db=db,
                    requirement_id=requirement_id,
                    use_knowledge_base=use_knowledge_base,
                    progress_callback=progress_callback,
                )

            # 完成前检查
            final_check = await db.execute(select(Task.status).where(Task.id == task_id))
            if final_check.scalar() == "running":
                await db.execute(
                    update(Task).where(Task.id == task_id).values(
                        status="completed",
                        progress=100,
                        progress_text="生成完成"
                    )
                )
                await db.commit()

        except asyncio.CancelledError:
            logger.info(f"Task {task_id} was cancelled via asyncio cancel")
            await db.execute(
                update(Task).where(Task.id == task_id).values(
                    status="cancelled",
                    progress_text="任务已取消"
                )
            )
            await db.commit()
        except Exception as e:
            error_msg = str(e)
            if error_msg == "TASK_CANCELLED":
                logger.info(f"Task {task_id} was cancelled during generation")
                return
            # 失败时保存错误信息
            await db.execute(
                update(Task).where(Task.id == task_id).values(
                    status="failed",
                    progress_text=f"生成失败: {error_msg}",
                    result={"error": error_msg}
                )
            )
            # 回退 Requirement 状态
            if is_cases:
                await db.execute(
                    update(Requirement).where(Requirement.id == requirement_id).values(status="failed")
                )
            else:
                await db.execute(
                    update(Requirement).where(Requirement.id == requirement_id).values(status="failed")
                )
            await db.commit()
        finally:
            self.tasks.pop(task_id, None)
            await orchestrator.close()
```

**Step 5: 改造 cancel_task - 加入数据回滚**

```python
async def cancel_task(self, db: AsyncSession, task_id: str) -> bool:
    # 先获取任务信息，确定 task_type
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return False

    is_cases = task.task_type in ("cases_generation", "cases_regeneration") if task.task_type else False
    requirement_id = task.requirement_id

    # 更新 Task 状态
    await db.execute(
        update(Task).where(Task.id == task_id).values(
            status="cancelled",
            progress_text="任务已取消"
        )
    )

    # 数据回滚
    if is_cases:
        # 删除该需求下所有用例
        tp_subquery = (
            select(TestPoint.id)
            .join(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        ).subquery()
        await db.execute(
            delete(TestCase).where(TestCase.test_point_id.in_(select(tp_subquery)))
        )
        # 恢复状态
        await db.execute(
            update(Requirement).where(Requirement.id == requirement_id).values(status="points_generated")
        )
    else:
        # 删除该需求下所有测试点（级联删除用例）
        tp_ids = (
            select(TestPoint.id)
            .join(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        ).subquery()
        await db.execute(delete(TestCase).where(TestCase.test_point_id.in_(select(tp_ids))))
        await db.execute(
            delete(TestPoint).where(
                TestPoint.id.in_(select(tp_ids))
            )
        )
        # 恢复状态
        await db.execute(
            update(Requirement).where(Requirement.id == requirement_id).values(status="confirmed")
        )

    await db.commit()

    # 取消后台 asyncio 协程
    bg_task = self.tasks.pop(task_id, None)
    if bg_task and not bg_task.done():
        bg_task.cancel()
        try:
            await bg_task
        except asyncio.CancelledError:
            pass

    return True
```

---

### Task 5: XMind 导出服务

**Files:**
- Create: `backend/app/services/xmind_service.py`

XMind 文件本质是 ZIP 包，包含 `content.xml` 和 `META-INF/manifest.xml`。以下是完整的导出实现：

```python
import json
import zipfile
import io
import uuid
from typing import List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.db_models import SplitRequirement, TestPoint, Requirement


class XMindService:
    """XMind 导入导出服务"""

    XMIND_NS = "urn:xmind:xmap:xmlns:content:2.0"
    FO_NS = "http://www.w3.org/1999/XSL/Format"

    async def export_test_points(
        self, db: AsyncSession, requirement_id: str
    ) -> bytes:
        """导出测试点为 XMind 文件"""
        # 查询需求
        req_result = await db.execute(
            select(Requirement).where(Requirement.id == requirement_id)
        )
        requirement = req_result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        # 查询拆分需求和测试点
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .options(selectinload(SplitRequirement.test_points))
            .order_by(SplitRequirement.sort_order)
        )
        split_reqs = result.scalars().all()

        # 构建 content.xml
        xmap_content = self._build_content_xml(
            requirement_title=requirement.title,
            split_requirements=split_reqs,
        )

        # 构建 ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('content.xml', xmap_content)
            zf.writestr('META-INF/manifest.xml', self._build_manifest_xml())
            # content.xml 必须作为第一个条目或放在根目录

        return zip_buffer.getvalue()

    def _build_content_xml(
        self, requirement_title: str, split_requirements: List[SplitRequirement]
    ) -> str:
        """构建 content.xml"""
        # 创建工作簿
        workbook = Element('xmap-content', {
            'xmlns': self.XMIND_NS,
            'xmlns:fo': self.FO_NS,
            'version': '2.0',
        })

        # 第一个 sheet
        sheet = SubElement(workbook, 'sheet', {'id': self._gen_id(), 'timestamp': '0'})

        # 中心主题（根需求）
        root_topic = SubElement(sheet, 'topic', {
            'id': self._gen_id(),
            'structure-class': 'org.xmind.ui.map.unbalanced',
            'timestamp': '0',
        })
        root_title = SubElement(root_topic, 'title')
        root_title.text = requirement_title

        children_elem = SubElement(root_topic, 'children')
        topics_elem = SubElement(children_elem, 'topics', {'type': 'attached'})

        # 拆分需求 → 一级子主题
        for sr in split_requirements:
            sr_topic = SubElement(topics_elem, 'topic', {
                'id': self._gen_id(),
                'timestamp': '0',
            })
            sr_title = SubElement(sr_topic, 'title')
            sr_title.text = sr.text

            # 测试点 → 二级子主题
            tp_list = sorted(sr.test_points, key=lambda tp: tp.created_at or 0)
            if tp_list:
                sr_children = SubElement(sr_topic, 'children')
                sr_topics = SubElement(sr_children, 'topics', {'type': 'attached'})
                for tp in tp_list:
                    tp_topic = SubElement(sr_topics, 'topic', {
                        'id': self._gen_id(),
                        'timestamp': '0',
                    })
                    tp_title = SubElement(tp_topic, 'title')
                    tp_title.text = tp.text

                    # 将数据库 ID 写入 notes（用于导入时匹配）
                    if tp.id:
                        notes_elem = SubElement(tp_topic, 'notes')
                        plain_notes = SubElement(notes_elem, 'plain')
                        # 使用 JSON 格式嵌入元数据，便于未来扩展
                        meta = {"db_id": tp.id, "description": tp.description or ""}
                        plain_notes.text = json.dumps(meta, ensure_ascii=False)

        # 格式化 XML
        xml_str = tostring(workbook, encoding='unicode')
        return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + xml_str

    def _build_manifest_xml(self) -> str:
        """构建 manifest.xml"""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
</manifest>'''

    def _gen_id(self) -> str:
        """生成 XMind 风格的 ID"""
        return str(uuid.uuid4()).replace('-', '')[:26]


# 单例
xmind_service = XMindService()
```

---

### Task 6: XMind 导入服务

**Files:**
- Modify: `backend/app/services/xmind_service.py`（续 Task 5）

```python
    async def parse_xmind(self, file_content: bytes) -> dict:
        """解析 XMind 文件，返回结构化的测试点数据"""
        zip_buffer = io.BytesIO(file_content)
        try:
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                content_xml = zf.read('content.xml')
        except zipfile.BadZipFile:
            raise ValueError("无效的 XMind 文件")
        except KeyError:
            raise ValueError("XMind 文件中未找到 content.xml")

        import xml.etree.ElementTree as ET
        root = ET.fromstring(content_xml)

        # 遍历主题树
        split_requirements = []
        ns = self.XMIND_NS
        sheets = root.findall(f'{{{ns}}}sheet')
        if not sheets:
            return {"split_requirements": []}

        sheet = sheets[0]
        root_topic = sheet.find(f'{{{ns}}}topic')
        if root_topic is None:
            return {"split_requirements": []}

        # 一级子主题 = 拆分需求
        children_elem = root_topic.find(f'{{{ns}}}children')
        if children_elem is None:
            return {"split_requirements": []}

        topics_elem = children_elem.find(f'{{{ns}}}topics')
        if topics_elem is None:
            return {"split_requirements": []}

        for sr_topic in topics_elem.findall(f'{{{ns}}}topic'):
            sr_title_elem = sr_topic.find(f'{{{ns}}}title')
            sr_text = sr_title_elem.text or "" if sr_title_elem is not None else ""

            # 二级子主题 = 测试点
            test_points = []
            sr_children = sr_topic.find(f'{{{ns}}}children')
            if sr_children is not None:
                sr_topics = sr_children.find(f'{{{ns}}}topics')
                if sr_topics is not None:
                    for tp_topic in sr_topics.findall(f'{{{ns}}}topic'):
                        tp_title_elem = tp_topic.find(f'{{{ns}}}title')
                        tp_text = tp_title_elem.text or "" if tp_title_elem is not None else ""

                        # 解析备注中的元数据
                        db_id = None
                        description = ""
                        notes_elem = tp_topic.find(f'{{{ns}}}notes')
                        if notes_elem is not None:
                            plain_elem = notes_elem.find(f'{{{ns}}}plain')
                            if plain_elem is not None and plain_elem.text:
                                try:
                                    meta = json.loads(plain_elem.text)
                                    db_id = meta.get("db_id")
                                    description = meta.get("description", "")
                                except json.JSONDecodeError:
                                    pass

                        test_points.append({
                            "db_id": db_id,
                            "text": tp_text,
                            "description": description,
                        })

            split_requirements.append({
                "text": sr_text,
                "test_points": test_points,
            })

        return {"split_requirements": split_requirements}

    async def preview_import(
        self, db: AsyncSession, requirement_id: str, file_content: bytes
    ) -> dict:
        """预览导入变更"""
        parsed = await self.parse_xmind(file_content)

        # 获取数据库中现有的测试点
        tp_result = await db.execute(
            select(TestPoint)
            .join(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        existing_tps = {tp.id: tp for tp in tp_result.scalars().all()}

        # 从 XMind 解析的所有测试点 ID 集合
        xmind_tp_ids = set()
        xmind_tp_items = []
        for sr in parsed["split_requirements"]:
            for tp in sr["test_points"]:
                xmind_tp_items.append(tp)
                if tp["db_id"]:
                    xmind_tp_ids.add(tp["db_id"])

        added_items = []
        updated_items = []
        deleted_items = []
        conflict_ids = []

        for tp in xmind_tp_items:
            if tp["db_id"] and tp["db_id"] in existing_tps:
                # 更新
                existing = existing_tps[tp["db_id"]]
                if tp["text"] != existing.text or tp.get("description") != (existing.description or ""):
                    updated_items.append({
                        "id": tp["db_id"],
                        "oldText": existing.text,
                        "newText": tp["text"],
                    })
            else:
                # 新增
                added_items.append({
                    "text": tp["text"],
                    "description": tp.get("description", ""),
                })

        # 数据库中有但 XMind 中没有的 = 待删除
        existing_ids = set(existing_tps.keys())
        for tp_id in existing_ids - xmind_tp_ids:
            tp = existing_tps[tp_id]
            # 检查是否有关联用例
            case_count = await db.execute(
                select(func.count(TestCase.id)).where(TestCase.test_point_id == tp_id)
            )
            case_cnt = case_count.scalar() or 0
            deleted_items.append({
                "id": tp_id,
                "text": tp.text,
                "hasCases": case_cnt > 0,
            })
            if case_cnt > 0:
                conflict_ids.append(tp_id)

        return {
            "addedCount": len(added_items),
            "updatedCount": len(updated_items),
            "deletedCount": len(deleted_items),
            "addedItems": added_items,
            "updatedItems": updated_items,
            "deletedItems": deleted_items,
            "hasCasesConflict": len(conflict_ids) > 0,
            "conflictTestPointIds": conflict_ids,
        }

    async def apply_import(
        self, db: AsyncSession, requirement_id: str, file_content: bytes
    ) -> dict:
        """执行导入：全量同步测试点"""
        parsed = await self.parse_xmind(file_content)

        # 获取数据库现有测试点
        tp_result = await db.execute(
            select(TestPoint)
            .join(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        existing_tps = {tp.id: tp for tp in tp_result.scalars().all()}

        xmind_tp_ids = set()
        now = datetime.utcnow()
        added = 0
        updated = 0
        deleted = 0

        # 获取第一个拆分需求（用于新增测试点的默认挂载）
        # 注意：导入时按 XMind 中的顺序匹配拆分需求
        sr_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .order_by(SplitRequirement.sort_order)
        )
        db_split_reqs = sr_result.scalars().all()
        db_sr_map = {sr.text: sr for sr in db_split_reqs}

        sr_index = 0
        for sr in parsed["split_requirements"]:
            # 匹配拆分需求
            matched_sr = db_sr_map.get(sr["text"])
            if not matched_sr and sr_index < len(db_split_reqs):
                matched_sr = db_split_reqs[sr_index]
            if not matched_sr:
                sr_index += 1
                continue

            for tp in sr["test_points"]:
                if tp["db_id"] and tp["db_id"] in existing_tps:
                    xmind_tp_ids.add(tp["db_id"])
                    # 更新
                    await db.execute(
                        update(TestPoint)
                        .where(TestPoint.id == tp["db_id"])
                        .values(
                            text=tp["text"],
                            description=tp.get("description", ""),
                            updated_at=now,
                        )
                    )
                    updated += 1
                else:
                    # 新增
                    tp_id = tp.get("db_id") or f"tp-{uuid.uuid4().hex[:8]}"
                    xmind_tp_ids.add(tp_id)
                    new_tp = TestPoint(
                        id=tp_id,
                        split_requirement_id=matched_sr.id,
                        text=tp["text"],
                        description=tp.get("description", ""),
                        source="AI",
                        status="completed",
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(new_tp)
                    added += 1

            sr_index += 1

        # 删除不在 XMind 中的测试点
        existing_ids = set(existing_tps.keys())
        removed_ids = existing_ids - xmind_tp_ids
        if removed_ids:
            # 先删除关联的用例
            await db.execute(
                delete(TestCase).where(TestCase.test_point_id.in_(list(removed_ids)))
            )
            await db.execute(
                delete(TestPoint).where(TestPoint.id.in_(list(removed_ids)))
            )
            deleted = len(removed_ids)

        await db.commit()

        return {
            "addedCount": added,
            "updatedCount": updated,
            "deletedCount": deleted,
        }
```

> 需要在 xmind_service.py 文件顶部添加 `import uuid`、`from datetime import datetime`、`from sqlalchemy import update, delete, func` 以及 `from app.models.db_models import TestPoint, TestCase, SplitRequirement`。

---

### Task 7: 路由层变更

**Files:**
- Modify: `backend/app/routers/test_design.py`

**Step 1: 修改 generate 路由，支持 taskType 参数**

```python
@router.post("/requirements/{requirementId}/generate", response_model=ResponseModel)
async def start_generation(
    requirementId: str,
    data: GenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.start_generation(
            db, requirementId,
            data.useKnowledgeBase or False,
            data.taskType or "points_generation"
        )
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 2: 新增 XMind 导出路由**

```python
# ========== XMind 导入导出 ==========
@router.get("/requirements/{requirementId}/export-xmind")
async def export_xmind(
    requirementId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.services.xmind_service import xmind_service
        xmind_bytes = await xmind_service.export_test_points(db, requirementId)
        from urllib.parse import quote
        # 获取需求标题用于文件名
        from app.models.db_models import Requirement
        result = await db.execute(select(Requirement).where(Requirement.id == requirementId))
        req = result.scalar_one_or_none()
        title = req.title if req else requirementId
        filename = f"测试点_{title}.xmind"
        encoded_filename = quote(filename)
        return Response(
            content=xmind_bytes,
            media_type="application/vnd.xmind.workbook",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Content-Type": "application/vnd.xmind.workbook",
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 3: 新增 XMind 导入预览路由**

```python
@router.post("/requirements/{requirementId}/import-xmind/preview", response_model=ResponseModel)
async def preview_xmind_import(
    requirementId: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await file.read()
        from app.services.xmind_service import xmind_service
        preview = await xmind_service.preview_import(db, requirementId, content)
        return ResponseModel(data=preview)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 4: 新增 XMind 导入确认路由**

```python
@router.post("/requirements/{requirementId}/import-xmind/apply", response_model=ResponseModel)
async def apply_xmind_import(
    requirementId: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await file.read()
        from app.services.xmind_service import xmind_service
        result = await xmind_service.apply_import(db, requirementId, content)
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

> 需要在文件顶部添加导入：`from fastapi import File, UploadFile`，`from sqlalchemy import select`。

**Step 5: 移除旧的 cancelled 状态过滤**

`get_requirements_list` 中的状态映射由 service 层处理，路由层无需改动。

---

### Task 8: 前端 API 层变更

**Files:**
- Modify: `frontend/src/api/index.js`

**Step 1: 修改 generate 调用，增加 taskType**

```javascript
export const testDesignAPI = {
  // ... 现有方法保持不变 ...
  
  // 修改：生成接口增加 taskType
  generate: (requirementId, data) => api.post(`/v1/test-design/requirements/${requirementId}/generate`, data),
  
  // 新增：XMind 导出
  exportXMind: (requirementId) => api.get(`/v1/test-design/requirements/${requirementId}/export-xmind`, { 
    responseType: 'blob' 
  }),
  
  // 新增：XMind 导入预览
  previewXMindImport: (requirementId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/v1/test-design/requirements/${requirementId}/import-xmind/preview`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000
    })
  },

  // 新增：XMind 导入确认
  applyXMindImport: (requirementId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/v1/test-design/requirements/${requirementId}/import-xmind/apply`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000
    })
  },
  
  // 其他现有方法保持不变...
}
```

---

### Task 9: 前端 TestDesign.vue 状态管理 & 工具栏改造

**Files:**
- Modify: `frontend/src/views/TestDesign.vue`

**Step 1: data() 中新增字段**

在 `data()` 中新增：

```javascript
data() {
  return {
    // ... 现有字段 ...
    isGenerating: false,
    isExportingXMind: false,
    currentTaskId: null,
    currentTaskType: null,          // 新增：当前任务类型
    requirementStatus: '',           // 新增：当前需求的 status
    showGenerateCasesMenu: false,    // 新增：生成用例下拉菜单
    // ... 其他字段保持不变 ...
  }
},
```

**Step 2: 状态映射 computed**

```javascript
computed: {
  filteredHistoryList() {
    return this.historyList
  },
  
  // 新增：根据 requirement.status 判断工具栏状态
  toolbarState() {
    const st = this.requirementStatus
    return {
      showGeneratePoints: st === 'confirmed' || st === 'pending',
      showGenerating: st === 'generating_points' || st === 'generating_cases',
      showPointsActions: st === 'points_generated',
      showCompletedActions: st === 'completed',
      showFailed: st === 'failed',
      isGeneratingPoints: st === 'generating_points',
      isGeneratingCases: st === 'generating_cases',
    }
  }
},
```

**Step 3: 工具栏 HTML 改造**

将现有工具栏（约 line 130-166）替换为：

```html
<!-- 工具栏 -->
<div class="bg-white border-b border-gray-200 px-6 py-3">
  <div class="flex items-center justify-between">
    <!-- 左侧：需求标题 -->
    <div class="flex items-center space-x-3">
      <h2 class="text-lg font-semibold text-gray-800 truncate max-w-md">
        {{ activeRequirement ? activeRequirement.title : '请选择需求' }}
      </h2>
    </div>

    <!-- 右侧：操作按钮 -->
    <div class="flex items-center space-x-2">

      <!-- confirmed：生成测试点 -->
      <button
        v-if="toolbarState.showGeneratePoints"
        @click="startGeneratePoints"
        class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        :disabled="!activeRequirement"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
        <span>生成测试点</span>
      </button>

      <!-- generating_points / generating_cases：进度条 + 取消 -->
      <template v-if="toolbarState.showGenerating">
        <div class="flex items-center space-x-3 min-w-[300px]">
          <span class="text-sm text-gray-600">{{ progressText }}</span>
          <div class="flex-1 bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
          <span class="text-xs text-gray-500 w-10 text-right">{{ progress }}%</span>
        </div>
        <button
          @click="cancelGenerate"
          class="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          取消
        </button>
      </template>

      <!-- points_generated：导出XMind / 导入XMind / 生成用例 -->
      <template v-if="toolbarState.showPointsActions">
        <button
          @click="exportXMind"
          :disabled="isExportingXMind"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <span>{{ isExportingXMind ? '导出中...' : '导出XMind' }}</span>
        </button>
        
        <button
          @click="triggerXMindImport"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
          </svg>
          <span>导入XMind</span>
        </button>

        <!-- 生成用例下拉 -->
        <div class="relative">
          <button
            @click="showGenerateCasesMenu = !showGenerateCasesMenu"
            class="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            <span>生成用例</span>
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
          <div
            v-if="showGenerateCasesMenu"
            class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
          >
            <button
              @click="startGenerateCases('incremental'); showGenerateCasesMenu = false"
              class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              增量生成用例
            </button>
            <button
              @click="startGenerateCases('regenerate'); showGenerateCasesMenu = false"
              class="w-full text-left px-4 py-2.5 text-sm text-orange-600 hover:bg-orange-50 transition-colors border-t border-gray-100"
            >
              重新生成全部用例
            </button>
          </div>
        </div>
      </template>

      <!-- completed：导出Excel / 重新生成 -->
      <template v-if="toolbarState.showCompletedActions">
        <button
          @click="exportExcel"
          :disabled="isExporting"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <span>{{ isExporting ? '导出中...' : '导出Excel' }}</span>
        </button>
        
        <div class="relative">
          <button
            @click="showGenerateCasesMenu = !showGenerateCasesMenu"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
          >
            <span>重新生成</span>
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
          <div
            v-if="showGenerateCasesMenu"
            class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
          >
            <button
              @click="startGeneratePoints(); showGenerateCasesMenu = false"
              class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              重新生成测试点
            </button>
            <button
              @click="startGenerateCases('regenerate'); showGenerateCasesMenu = false"
              class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors border-t border-gray-100"
            >
              重新生成用例
            </button>
          </div>
        </div>
      </template>

      <!-- failed：重试 + 错误信息 -->
      <template v-if="toolbarState.showFailed">
        <span class="text-sm text-red-600 mr-2">生成失败，请重试</span>
        <button
          @click="retryFailedTask"
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          重试
        </button>
      </template>

    </div>
  </div>

  <!-- 隐藏的 input 用于 XMind 导入 -->
  <input
    ref="xmindFileInput"
    type="file"
    accept=".xmind"
    style="display: none"
    @change="handleXMindFileSelected"
  />
</div>
```

**Step 4: 移除原有进度条区域**

原有 `<div v-if="isGenerating" class="mt-3">...</div>` 进度条区域不再需要，因为进度条已整合到工具栏中。

---

### Task 10: 前端 TestDesign.vue 方法改造

**Files:**
- Modify: `frontend/src/views/TestDesign.vue`

**Step 1: 进入需求时同步 status**

在 `selectRequirement` 方法中：

```javascript
async selectRequirement(req) {
  this.activeRequirementId = req.id
  this.activeRequirement = req
  this.requirementStatus = req.status || 'confirmed'
  
  // 如果正在生成中，检查是否有活跃任务
  if (['generating_points', 'generating_cases'].includes(this.requirementStatus)) {
    await this.checkActiveTask()
  }
  
  // 加载脑图数据
  await this.fetchMindMapData()
}
```

**Step 2: 启动生成测试点**

```javascript
async startGeneratePoints() {
  if (this.isGenerating || !this.activeRequirementId) return

  this.isGenerating = true
  this.progress = 0
  this.progressText = '正在初始化测试点生成...'
  this.requirementStatus = 'generating_points'
  this.currentTaskType = 'points_generation'

  try {
    const res = await testDesignAPI.generate(this.activeRequirementId, {
      useKnowledgeBase: this.knowledgeBaseEnabled,
      taskType: 'points_generation'
    })

    if (res.success) {
      this.currentTaskId = res.data.taskId
      this.progressText = '正在生成测试点...'
      this.startPolling()
    } else {
      this.resetGenerationState()
      alert(res.message || '生成任务启动失败，请重试')
    }
  } catch (e) {
    this.resetGenerationState()
    alert('网络异常，请稍后重试')
  }
},
```

**Step 3: 启动生成用例**

```javascript
async startGenerateCases(mode) {
  // mode: 'incremental' | 'regenerate'
  if (this.isGenerating || !this.activeRequirementId) return

  this.isGenerating = true
  this.progress = 0
  this.progressText = mode === 'regenerate' ? '正在重新生成用例...' : '正在生成用例...'
  this.requirementStatus = 'generating_cases'
  this.currentTaskType = mode === 'regenerate' ? 'cases_regeneration' : 'cases_generation'

  try {
    const res = await testDesignAPI.generate(this.activeRequirementId, {
      useKnowledgeBase: this.knowledgeBaseEnabled,
      taskType: mode === 'regenerate' ? 'cases_regeneration' : 'cases_generation'
    })

    if (res.success) {
      this.currentTaskId = res.data.taskId
      this.startPolling()
    } else {
      this.resetGenerationState()
      alert(res.message || '生成任务启动失败，请重试')
    }
  } catch (e) {
    this.resetGenerationState()
    alert('网络异常，请稍后重试')
  }
},
```

**Step 4: 轮询完成时更新状态**

修改 `startPolling` 中的完成逻辑：

```javascript
startPolling() {
  if (this.pollTimer) clearInterval(this.pollTimer)
  
  this.pollTimer = setInterval(async () => {
    if (!this.currentTaskId) {
      clearInterval(this.pollTimer)
      this.pollTimer = null
      return
    }

    try {
      const res = await testDesignAPI.getTaskStatus(this.currentTaskId)
      if (!res.success || !res.data) return

      const task = res.data
      this.progress = task.progress
      this.progressText = task.progressText

      if (task.status === 'completed') {
        clearInterval(this.pollTimer)
        this.pollTimer = null
        this.isGenerating = false
        
        // 刷新需求获取最新状态
        await this.refreshActiveRequirement()
        // 重新加载脑图
        await this.fetchMindMapData()
      } else if (task.status === 'failed') {
        clearInterval(this.pollTimer)
        this.pollTimer = null
        this.isGenerating = false
        this.progressText = task.progressText
        this.requirementStatus = 'failed'
      } else if (task.status === 'cancelled') {
        clearInterval(this.pollTimer)
        this.pollTimer = null
        this.isGenerating = false
        // 刷新需求状态（被回退到 confirmed 或 points_generated）
        await this.refreshActiveRequirement()
        await this.fetchMindMapData()
      }
    } catch (e) {
      // ignore
    }
  }, 1000)
},

async refreshActiveRequirement() {
  try {
    const res = await testDesignAPI.getRequirementList({
      page: 1, pageSize: 1, keyword: ''
    })
    // 在完整列表中查找当前需求
    const allRes = await testDesignAPI.getRequirementList({
      page: 1, pageSize: 100, keyword: ''
    })
    if (allRes.success && allRes.data) {
      const found = allRes.data.list.find(r => r.id === this.activeRequirementId)
      if (found) {
        this.activeRequirement = found
        this.requirementStatus = found.status
      }
    }
  } catch (e) {
    // ignore
  }
},
```

**Step 5: 取消生成**

```javascript
async cancelGenerate() {
  if (!this.currentTaskId) return

  try {
    await testDesignAPI.cancelTask(this.currentTaskId)
    // cancel 后数据会回滚，轮询会收到 cancelled 状态
  } catch (e) {
    alert('取消失败，请重试')
  }
},
```

**Step 6: 重试失败任务**

```javascript
async retryFailedTask() {
  // 需要知道上次失败的是哪个任务类型
  if (!this.currentTaskType && this.requirementStatus === 'failed') {
    // 从上一个失败的任务获取 taskType
    try {
      const res = await testDesignAPI.getRequirementTask(this.activeRequirementId)
      // 如果还有活跃任务就不重试
      if (res.data) return
    } catch (e) {}
    // 默认重试测试点生成
    this.currentTaskType = 'points_generation'
  }
  
  if (this.currentTaskType && this.currentTaskType.includes('cases')) {
    await this.startGenerateCases(
      this.currentTaskType === 'cases_regeneration' ? 'regenerate' : 'incremental'
    )
  } else {
    await this.startGeneratePoints()
  }
},
```

**Step 7: 导出 XMind**

```javascript
async exportXMind() {
  if (!this.activeRequirementId || this.isExportingXMind) return
  this.isExportingXMind = true

  try {
    const blob = await testDesignAPI.exportXMind(this.activeRequirementId)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    const title = (this.activeRequirement && this.activeRequirement.title) || '测试点'
    link.download = `测试点_${title}.xmind`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败，请重试')
  } finally {
    this.isExportingXMind = false
  }
},
```

**Step 8: XMind 导入**

```javascript
triggerXMindImport() {
  this.$refs.xmindFileInput.click()
},

async handleXMindFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return

  try {
    // 先预览变更
    const previewRes = await testDesignAPI.previewXMindImport(this.activeRequirementId, file)
    if (!previewRes.success) {
      alert(previewRes.message || '解析失败')
      return
    }

    const preview = previewRes.data
    const { addedCount, updatedCount, deletedCount, hasCasesConflict, conflictTestPointIds } = preview

    // 构建确认消息
    let confirmMsg = `导入预览：\n`
    if (addedCount > 0) confirmMsg += `新增 ${addedCount} 个测试点\n`
    if (updatedCount > 0) confirmMsg += `更新 ${updatedCount} 个测试点\n`
    if (deletedCount > 0) {
      confirmMsg += `删除 ${deletedCount} 个测试点\n`
      if (hasCasesConflict) {
        confirmMsg += `\n⚠️ 警告：${conflictTestPointIds.length} 个待删除测试点已关联用例，将一并删除！\n`
      }
    }
    if (addedCount === 0 && updatedCount === 0 && deletedCount === 0) {
      confirmMsg += '\n没有检测到变更。'
      this.$refs.xmindFileInput.value = ''
      return
    }
    
    confirmMsg += '\n是否确认导入？'

    if (!confirm(confirmMsg)) {
      this.$refs.xmindFileInput.value = ''
      return
    }

    // 执行导入
    const applyRes = await testDesignAPI.applyXMindImport(this.activeRequirementId, file)
    if (applyRes.success) {
      alert(`导入成功！新增 ${applyRes.data.addedCount}，更新 ${applyRes.data.updatedCount}，删除 ${applyRes.data.deletedCount}`)
      await this.fetchMindMapData()
    } else {
      alert(applyRes.message || '导入失败')
    }
  } catch (e) {
    alert('导入失败：' + (e.message || '请重试'))
  } finally {
    this.$refs.xmindFileInput.value = ''
  }
},
```

**Step 9: 修改 statusTabs**

更新左侧的状态筛选标签：

```javascript
statusTabs: [
  { label: '全部', value: '' },
  { label: '待生成', value: 'pending' },
  { label: '生成中', value: 'generating' },
  { label: '已生成测试点', value: 'points_generated' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
],
```

> 对应后端 `get_requirements_list` 中新增 `points_generated` 状态筛选支持。

**Step 10: 重置方法**

```javascript
resetGenerationState() {
  this.isGenerating = false
  this.progress = 0
  this.progressText = ''
  this.currentTaskId = null
  this.currentTaskType = null
},
```

---

## 五、前端状态筛选补充

后端 `get_requirements_list` 需补充 `points_generated` 状态映射以支持前端的 `已生成测试点` 筛选标签：

```python
status_mapping = {
    "pending": "confirmed",
    "generating": ["generating_points", "generating_cases"],
    "points_generated": "points_generated",  # 新增
    "completed": "completed",
    "failed": "failed",
}
```

---

## 六、实施顺序

| 顺序 | Task | 依赖 | 预计影响 |
|------|------|------|---------|
| 1 | Task 1: DB 模型 | 无 | Task 表加字段 |
| 2 | Task 2: Pydantic 模型 | Task 1 | 请求/响应模型 |
| 3 | Task 3: Orchestrator 拆分 | Task 1 | 核心生成逻辑 |
| 4 | Task 4: test_design_service 改造 | Task 2, 3 | 状态管理、回滚 |
| 5 | Task 5: XMind 导出 | 无 | 新增文件 |
| 6 | Task 6: XMind 导入 | Task 5 | 同一文件追加 |
| 7 | Task 7: 路由层 | Task 4, 5, 6 | API 端点 |
| 8 | Task 8: 前端 API 层 | Task 7 | API 调用 |
| 9 | Task 9: 前端工具栏 HTML | Task 8 | Vue 模板 |
| 10 | Task 10: 前端方法 | Task 9 | Vue 方法 |

---

## 七、注意事项

1. **向后兼容**：旧的 `Task` 记录没有 `task_type` 字段，默认值为 `NULL`。代码中需兼容 `task_type is None` 的情况，此时按旧逻辑处理（不区分）。
2. **数据库迁移**：`task_type` 字段应在代码上线前通过 SQL 或 Alembic 添加。
3. **XMind 兼容性**：导出的 `.xmind` 文件遵循 XMind 8+ 格式（纯 XML + ZIP），可在 XMind 8/2020/2022 等版本中打开。
4. **导入健壮性**：导入时如果 XMind 文件结构不符合预期（如没有拆分需求层级），应给出明确错误提示而不是静默失败。
5. **并发安全**：同一需求不应同时进行两个生成任务。在 `start_generation` 中检查是否已有 running 状态的 Task，有则拒绝新请求。
6. **XMind 导入的拆分需求匹配**：导入时按 XMind 中一级主题的顺序对应数据库中的 `SplitRequirement`（按 `sort_order` 排序）。如果 XMind 中拆分需求的文本和数据库中的不完全一致，使用顺序匹配作为兜底。
7. **现有需求状态迁移**：已用旧流程生成过的需求可能处于 `confirmed` 或 `completed` 状态，这些状态仍然有效。`points_generated` 和 `generating_points`/`generating_cases` 等新状态仅对新任务生效。