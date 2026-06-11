# Agent 系统总览

## 系统架构

本平台的 Agent 系统围绕"需求 → 测试"的核心流程设计，包含以下智能体：

```
用户输入需求
    │
    ▼
┌─────────────────────────┐
│  TemplateRecommendAgent │ 模板推荐
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     ExploreAgent        │ 需求探索（多轮对话）
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   StandardizeAgent      │ 需求标准化（生成文档 + 调整）
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      SplitAgent         │ 需求拆分
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       TestDesignOrchestrator            │ 测试设计编排
│  ┌──────────────┐  ┌────────────────┐   │
│  │ TestPointAgent│  │ TestCaseAgent  │   │
│  └──────────────┘  └────────────────┘   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│  TestDesignAdjustAgent  │ AI 调整（对话式修改）
└─────────────────────────┘
```

## Agent 清单

| Agent | 文档 | 源码位置 | 核心功能 |
|-------|------|---------|---------|
| TestPointAgent | [test-point-agent.md](test-point-agent.md) | `backend/app/agents/test_point_agent.py` | 从需求生成测试点 |
| TestCaseAgent | [test-case-agent.md](test-case-agent.md) | `backend/app/agents/test_case_agent.py` | 从测试点生成测试用例 |
| TestDesignOrchestrator | [test-design-orchestrator.md](test-design-orchestrator.md) | `backend/app/agents/orchestrator.py` | 编排测试点和用例生成 |
| ExploreAgent | [explore-agent.md](explore-agent.md) | `backend/app/services/explore_service.py` | 多轮对话探索需求 |
| StandardizeAgent | [standardize-agent.md](standardize-agent.md) | `backend/app/services/standardize_service.py` | 生成标准化需求文档 |
| SplitAgent | [split-agent.md](split-agent.md) | `backend/app/services/split_service.py` | 拆分标准化文档 |
| TemplateRecommendAgent | [template-recommend-agent.md](template-recommend-agent.md) | `backend/app/services/template_service.py` | 推荐文档模板 |
| TestDesignAdjustAgent | [test-design-adjust-agent.md](test-design-adjust-agent.md) | `backend/app/services/test_design.py` | 对话式调整测试设计 |

## 基础设施

| 组件 | 文档 | 源码位置 | 核心功能 |
|------|------|---------|---------|
| LLMClient | [llm-client-and-rag-service.md](llm-client-and-rag-service.md) | `backend/app/agents/llm_client.py` | 大语言模型调用 |
| RAGService | [llm-client-and-rag-service.md](llm-client-and-rag-service.md) | `backend/app/agents/rag_service.py` | 知识库检索增强 |

## 公共模块

| 模块 | 源码位置 | 说明 |
|------|---------|------|
| PromptTemplates | `backend/app/agents/prompts.py` | 所有 Agent 共用的提示词模板集合 |

## 技术栈

- **LangGraph**: TestPointAgent 和 TestCaseAgent 基于 LangGraph 的 StateGraph 构建，支持条件路由和循环
- **AsyncOpenAI**: 所有 LLM 调用基于 OpenAI 兼容接口的异步客户端
- **SQLAlchemy**: 异步 ORM，用于数据持久化
- **RAG**: 基于向量检索 + LLM 重排的检索增强生成

## 设计模式

### 自我迭代模式

TestPointAgent 和 TestCaseAgent 采用"生成 → 评审 → 纠正"的自我迭代模式：
1. 生成初始结果
2. 通过 LLM 进行质量评审
3. 不通过时自动纠正并重新评审
4. 达到最大重试次数后输出最终结果

### 降级策略

所有 Agent 都内置降级策略，当 LLM 不可用时：
- 使用模板化的默认输出
- 返回友好的提示信息
- 保证系统基本可用

### 知识库增强

TestPointAgent 和 TestCaseAgent 支持可选的知识库增强：
- 通过 RAGService 检索相关知识
- LLM 重排确保相关性
- 将知识上下文注入生成提示词
