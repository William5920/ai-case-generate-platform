# TemplateRecommendAgent - 模板推荐 Agent

## 概述

TemplateRecommendAgent 是文档模板推荐智能体，根据用户的需求内容自动推荐最合适的需求文档模板。目前支持两种模板：SRS 需求规格说明书和用户故事需求文档。

**源码位置**: `backend/app/services/template_service.py`（`TemplateService.recommend_template()` 方法）

## 架构设计

### 类定义

```python
class TemplateService:
    def __init__(self):
        self._templates = {t["id"]: t for t in TEMPLATES_DATA}
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)
```

### 支持的模板

| 模板 ID | 名称 | 适用场景 |
|---------|------|---------|
| `srs` | SRS 需求规格说明书 | 瀑布式开发，基于 IEEE 830 标准，文档完整详细 |
| `user-story` | 用户故事需求文档 | 敏捷式开发，以用户故事为核心，文档简洁聚焦 |

## 核心方法

### recommend_template（推荐模板）

```python
async def recommend_template(self, content: str, input_mode: str = "text") -> dict
```

**功能**: 根据需求内容推荐最合适的文档模板

**推荐规则**:
- 敏捷关键词（迭代、sprint、用户故事、敏捷、scrum、看板、backlog、MVP、增量）→ 推荐用户故事模板
- 瀑布关键词（规格、阶段、里程碑、评审、基线、配置管理、验收测试、SRS）→ 推荐 SRS 模板
- 两者得分相同时默认推荐 SRS 模板

**返回值**:
```json
{
  "recommendedTemplateId": "srs 或 user-story",
  "confidence": 0.0-1.0,
  "reason": "推荐理由"
}
```

## 提示词模板

### TEMPLATE_RECOMMEND

指导 LLM 分析需求内容并推荐模板，输出格式：

```json
{
  "recommended_template_id": "srs或user-story",
  "confidence": 0.85,
  "reason": "推荐理由"
}
```

## 降级策略

- LLM 不可用时，默认推荐 SRS 模板，置信度 0.5

## 其他方法

| 方法 | 说明 |
|------|------|
| `get_template_list()` | 获取所有模板列表 |
| `get_template_detail(template_id)` | 获取模板详情 |
| `get_template_dimensions(template_id)` | 获取模板的探索维度列表 |
| `get_template_sections_text(template_id)` | 获取模板章节结构的文本表示 |

## 模板维度定义

### SRS 模板（15 个维度）

编写目的、项目背景、术语定义、业务目标、用户角色、核心业务流程、功能需求、性能需求、安全性需求、可用性需求、兼容性需求、技术约束、业务约束、法规约束、异常场景

### 用户故事模板（9 个维度）

背景与目标、范围与优先级、用户角色、用户故事、验收标准、业务规则、数据需求、非功能需求、依赖与假设

## 与其他模块的关系

- **ExploreService**: 使用模板维度定义引导用户探索
- **StandardizeService**: 使用模板章节结构生成标准化文档
