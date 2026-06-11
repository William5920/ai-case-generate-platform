# SplitAgent - 需求拆分 Agent

## 概述

SplitAgent 是需求拆分阶段的智能体，负责将标准化需求文档拆分为独立的、可执行的单个需求项。拆分后的需求项将作为后续测试点生成和测试用例生成的输入。

**源码位置**: `backend/app/services/split_service.py`（`SplitService` 类）

## 架构设计

### 类定义

```python
class SplitService:
    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)
```

### 核心数据模型

- **SplitRequirement**: 拆分需求实体，包含文本内容、排序、状态等

## 核心方法

### 1. execute_split（执行拆分）

```python
async def execute_split(
    self, db, user_id, requirement_id, standardized_content
) -> dict
```

**功能**: 将标准化文档拆分为独立需求项

**执行逻辑**:
1. 查询需求记录
2. 使用 `REQUIREMENT_SPLIT` 提示词调用 LLM 进行拆分
3. 删除已有的拆分记录
4. 保存新的拆分记录到数据库
5. 更新需求状态为 `split`

**拆分规则**（LLM 遵循）:
1. 每个拆分项应是一个独立的功能需求或非功能需求
2. 拆分项应具有可测试性
3. 拆分粒度适中，不宜过大或过小
4. 保持需求项之间的逻辑关系
5. 按功能模块分组
6. 每个拆分项用简洁的一句话描述

**返回值**:
- `splits`: 拆分项列表（含 id、content、order）
- `totalCount`: 拆分项总数

### 2. get_split_list（获取拆分列表）

获取指定需求的拆分项列表，按 `order_index` 排序。

### 3. update_split（更新拆分项）

更新指定拆分项的内容和排序。

### 4. add_split（新增拆分项）

手动新增一个拆分项，自动计算排序号。

### 5. delete_split（删除拆分项）

删除指定的拆分项。

### 6. confirm_and_test（确认并测试）

```python
async def confirm_and_test(
    self, db, user_id, requirement_id, title,
    split_requirements, standardized_content=None, template_id=None
) -> dict
```

**功能**: 确认拆分结果并准备进入测试设计阶段

**执行逻辑**:
1. 删除已有的拆分记录
2. 保存用户确认的拆分记录（跳过未选中的项）
3. 更新需求状态为 `confirmed`
4. 更新需求标题

## 提示词模板

### REQUIREMENT_SPLIT

用于指导 LLM 拆分标准化文档，输出格式：

```json
{
  "splits": [
    {"content": "拆分项内容描述"}
  ]
}
```

## 降级策略

- LLM 不可用时，按段落拆分标准化文档（以 `\n\n` 分隔，最多 20 段）

## 与其他模块的关系

- **StandardizeService**: 接收标准化文档内容作为输入
- **TestDesignOrchestrator**: 拆分确认后，编排器读取拆分需求进行测试设计
