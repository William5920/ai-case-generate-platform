# LLMClient & RAGService - AI 基础设施

## 概述

LLMClient 和 RAGService 是 Agent 系统的基础设施组件，分别提供大语言模型调用和知识库检索增强生成（RAG）能力。所有 Agent 都依赖这两个组件完成核心功能。

**源码位置**:
- `backend/app/agents/llm_client.py`
- `backend/app/agents/rag_service.py`

---

## LLMClient - 大语言模型客户端

### 类定义

```python
class LLMClient:
    def __init__(self):
        self._client = None
        self._cached_base_url = None
        self._cached_api_key = None
```

### 特性

- 基于 `AsyncOpenAI` 实现异步调用
- 支持配置热更新（自动检测 API Key 和 Base URL 变化并重建客户端）
- 内置重试机制（速率限制、超时、连接错误）
- 支持 JSON Schema 结构化输出

### 核心方法

#### chat()

```python
async def chat(
    self, messages, model=None, temperature=0.7,
    response_format=None, max_tokens=4096
) -> str
```

**功能**: 基础对话接口，返回文本内容

**错误处理**:
| 错误类型 | 处理策略 |
|---------|---------|
| `RateLimitError` | 等待 2 秒后重试 |
| `APITimeoutError` | 等待 3 秒后重试 |
| `APIConnectionError` | 关闭旧连接，等待 1 秒后重建连接重试 |
| `APIStatusError` | 记录错误日志，抛出异常 |

#### chat_with_schema()

```python
async def chat_with_schema(
    self, messages, schema_description, model=None,
    temperature=0.5, max_tokens=4096
) -> Dict
```

**功能**: 结构化输出接口，返回 JSON 对象

**实现方式**:
1. 将 schema 描述注入系统提示词
2. 使用 `response_format={"type": "json_object"}` 强制 JSON 输出
3. 解析返回的 JSON 内容
4. JSON 解析失败时，尝试正则提取 JSON 片段

#### close()

关闭 OpenAI 客户端连接，释放资源。

### 配置项

| 配置 | 说明 |
|------|------|
| `settings.OPENAI_API_KEY` | API 密钥 |
| `settings.OPENAI_BASE_URL` | API 基础 URL |
| `settings.OPENAI_MODEL` | 默认模型 |
| `settings.OPENAI_MODEL_ANALYZE` | 分析任务模型 |
| `settings.OPENAI_MODEL_GENERATE` | 生成任务模型 |

---

## RAGService - 检索增强生成服务

### 类定义

```python
class RAGService:
    def __init__(self, kb_service: KnowledgeBaseService, llm_client: LLMClient):
        self.kb_service = kb_service
        self.llm_client = llm_client
```

### 数据结构

```python
@dataclass
class RecallResult:
    content: str        # 文档内容
    score: float        # 相关度分数
    document_id: str    # 文档 ID
    chunk_id: int       # 分块 ID
```

### 核心方法

#### recall()

```python
async def recall(self, query, top_k=5, threshold=0.7) -> List[RecallResult]
```

**功能**: 基础检索接口

**执行逻辑**:
1. 调用 `KnowledgeBaseService.test_recall()` 获取原始结果
2. 过滤低于阈值的结果
3. 返回 top_k 个最相关结果

**参数**:
- `query`: 查询文本
- `top_k`: 返回的最大结果数
- `threshold`: 相关度阈值（0-1）

#### recall_and_rerank()

```python
async def recall_and_rerank(
    self, query, top_k=5, threshold=0.7, final_k=3
) -> List[RecallResult]
```

**功能**: 检索 + LLM 重排

**执行逻辑**:
1. 调用 `recall()` 获取候选结果
2. 如果结果数 <= final_k，直接返回
3. 否则调用 `_rerank_with_llm()` 进行 LLM 重排
4. 返回 final_k 个最相关结果

#### _rerank_with_llm()

**功能**: 使用 LLM 对检索结果进行重排

**实现方式**:
1. 将所有候选结果编号列出
2. 让 LLM 按相关性从高到低重新排序
3. 解析 LLM 返回的编号列表
4. 未被 LLM 排序的结果追加到末尾

**降级策略**: LLM 重排失败时，返回原始检索结果

### 在 Agent 中的使用

| Agent | 使用方式 |
|-------|---------|
| TestPointAgent | 检索与需求相关的测试知识 |
| TestCaseAgent | 检索与测试点相关的用例编写规范 |
| TestDesignOrchestrator | 通过 TestPointAgent 和 TestCaseAgent 间接使用 |

### 典型调用参数

| 场景 | top_k | threshold | final_k |
|------|-------|-----------|---------|
| 测试点生成 | 5 | 0.7 | 3 |
| 测试用例生成 | 5 | 0.7 | 3 |
