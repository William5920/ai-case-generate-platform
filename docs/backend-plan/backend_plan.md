# 智能测试用例平台 - 后端开发计划

## 1. 项目概述

根据需求文档 `requirements_spec_v1.md`，本项目是一个 AI 驱动的测试用例生成平台，采用前后端分离架构。后端技术栈为 Python 3.11.9 + FastAPI + LangGraph + Milvus + OpenAI API。

## 2. 当前后端现状

| 模块 | 状态 | 说明 |
|------|------|------|
| 项目骨架 | ✅ 已完成 | FastAPI 应用已初始化，CORS 已配置 |
| 配置管理 | ✅ 已完成 | `pydantic-settings` 管理环境变量 |
| 知识库模块 | ⚠️ 部分完成 | 文档上传/删除/查看/召回测试已实现，但使用内存存储，无持久化 |
| 数据库 | ❌ 未接入 | 当前无数据库，数据存储在内存中 |
| 用户认证 | ❌ 未开发 | 无登录/注册/JWT 认证 |
| 需求管理 | ❌ 未开发 | 无需求 CRUD |
| 需求标准化 | ❌ 未开发 | 无 AI 标准化功能 |
| 需求拆分 | ❌ 未开发 | 无拆分功能 |
| 测试点生成 | ❌ 未开发 | 无 AI 测试点生成 |
| 测试用例生成 | ❌ 未开发 | 无 AI 测试用例生成 |
| 异步任务管理 | ❌ 未开发 | 无任务队列和进度追踪 |
| 历史记录 | ❌ 未开发 | 无历史记录功能 |
| Excel 导出 | ❌ 未开发 | 无导出功能 |
| AI 服务集成 | ❌ 未开发 | 无大模型调用封装 |

## 3. 后端技术架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI 应用                       │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│  认证模块  │ 需求模块  │ 测试设计  │ 知识库   │ 历史记录 │
│  /auth    │ /req     │ /test    │ /know    │ /history │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│                  Service 层                          │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Auth     │ Require  │ AI       │ Knowledge│ Export  │
│ Service  │ Service  │ Service  │ Service  │ Service │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│              AI 编排层 (LangGraph)                    │
├─────────────────────────────────────────────────────┤
│  标准化Agent │ 拆分Agent │ 测试点Agent │ 用例Agent    │
├─────────────────────────────────────────────────────┤
│              基础设施层                               │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ SQLite   │ Milvus   │ OpenAI   │ 文件存储  │ 任务队列 │
│ (ORM)    │ (向量库)  │ (大模型)  │ (本地磁盘) │ (内存)  │
└──────────┴──────────┴──────────┴──────────┴─────────┘
```

### 3.2 项目目录结构（目标）

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理
│   │   ├── security.py            # JWT/密码加密
│   │   ├── database.py            # 数据库连接
│   │   └── dependencies.py        # 依赖注入（获取当前用户等）
│   ├── models/                    # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── requirement.py
│   │   ├── test_point.py
│   │   ├── test_case.py
│   │   ├── history_record.py
│   │   └── knowledge_base.py
│   ├── schemas/                   # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── requirement.py
│   │   ├── test_point.py
│   │   ├── test_case.py
│   │   ├── history.py
│   │   ├── knowledge.py
│   │   └── task.py
│   ├── routers/                   # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── requirement.py
│   │   ├── standardize.py
│   │   ├── test_design.py
│   │   ├── knowledge_base.py
│   │   ├── history.py
│   │   └── export.py
│   ├── services/                  # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── requirement_service.py
│   │   ├── standardize_service.py
│   │   ├── test_design_service.py
│   │   ├── knowledge_base_service.py
│   │   ├── history_service.py
│   │   └── export_service.py
│   ├── ai/                        # AI 编排层
│   │   ├── __init__.py
│   │   ├── llm_client.py          # 大模型客户端封装
│   │   ├── prompts/               # Prompt 模板
│   │   │   ├── standardize.py
│   │   │   ├── split.py
│   │   │   ├── test_point.py
│   │   │   └── test_case.py
│   │   └── agents/                # LangGraph Agent
│   │       ├── __init__.py
│   │       ├── standardize_agent.py
│   │       ├── split_agent.py
│   │       ├── test_point_agent.py
│   │       └── test_case_agent.py
│   └── tasks/                     # 异步任务管理
│       ├── __init__.py
│       └── task_manager.py
├── uploads/                       # 文件上传目录
├── alembic/                       # 数据库迁移
│   └── versions/
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── start.sh
```

## 4. 数据库设计

### 4.1 选型：SQLite

- 轻量级，无需额外部署数据库服务
- 适合个人使用模式，单用户场景
- 后续可平滑迁移至 PostgreSQL

### 4.2 数据表设计

#### users 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| username | VARCHAR(20) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE | 邮箱 |
| hashed_password | VARCHAR(255) | NOT NULL | 加密密码 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### requirements 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| user_id | UUID | FK -> users.id | 关联用户 |
| title | VARCHAR(200) | NOT NULL | 需求标题 |
| input_mode | VARCHAR(10) | NOT NULL | 输入模式：text/file |
| raw_content | TEXT | | 原始需求文本 |
| file_id | UUID | FK -> uploaded_files.id | 关联上传文件 |
| standardized_content | TEXT | | 标准化后的文档内容 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态：draft/standardized/splitted |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### uploaded_files 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| user_id | UUID | FK -> users.id | 关联用户 |
| original_filename | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_path | VARCHAR(500) | NOT NULL | 存储路径 |
| file_size | INTEGER | NOT NULL | 文件大小 |
| file_type | VARCHAR(100) | | 文件MIME类型 |
| purpose | VARCHAR(20) | NOT NULL | 用途：requirement/knowledge |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### split_requirements 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| requirement_id | UUID | FK -> requirements.id | 关联需求 |
| content | TEXT | NOT NULL | 拆分项内容 |
| order_index | INTEGER | NOT NULL | 排序序号 |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态：pending/generating/completed |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### test_points 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| split_requirement_id | UUID | FK -> split_requirements.id | 关联拆分需求 |
| content | TEXT | NOT NULL | 测试点内容 |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态：pending/generating/completed |
| marked | BOOLEAN | DEFAULT FALSE | 是否标记保留 |
| source | VARCHAR(10) | DEFAULT 'AI' | 来源：AI/manual |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### test_cases 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| test_point_id | UUID | FK -> test_points.id | 关联测试点 |
| case_name | VARCHAR(200) | NOT NULL | 测试用例名称 |
| case_property | VARCHAR(10) | NOT NULL | 用例类型：正例/反例 |
| pre_condition | TEXT | | 前置条件 |
| steps | JSON | NOT NULL | 步骤列表 |
| marked | BOOLEAN | DEFAULT FALSE | 是否标记保留 |
| source | VARCHAR(10) | DEFAULT 'AI' | 来源：AI/manual |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### chat_messages 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| requirement_id | UUID | FK -> requirements.id | 关联需求 |
| role | VARCHAR(10) | NOT NULL | 角色：user/assistant |
| content | TEXT | NOT NULL | 消息内容 |
| message_type | VARCHAR(20) | | 消息类型：proposal/discussion/clarification |
| proposal_content | TEXT | | 建议的文档内容 |
| change_summary | TEXT | | 变更摘要 |
| confirmed | BOOLEAN | DEFAULT FALSE | 是否已采纳 |
| rejected | BOOLEAN | DEFAULT FALSE | 是否已拒绝 |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### history_records 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| user_id | UUID | FK -> users.id | 关联用户 |
| requirement_id | UUID | FK -> requirements.id | 关联需求 |
| title | VARCHAR(200) | NOT NULL | 记录标题 |
| original_requirement | TEXT | | 原始需求 |
| standardized_content | TEXT | | 标准化文档 |
| split_requirements | JSON | | 拆分后的需求列表 |
| test_points | JSON | | 测试点列表 |
| test_cases | JSON | | 测试用例列表 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### knowledge_documents 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| user_id | UUID | FK -> users.id | 关联用户 |
| title | VARCHAR(200) | NOT NULL | 文档标题 |
| description | TEXT | | 文档描述 |
| file_path | VARCHAR(500) | NOT NULL | 存储路径 |
| file_size | INTEGER | NOT NULL | 文件大小 |
| file_type | VARCHAR(100) | | 文件类型 |
| chunk_count | INTEGER | DEFAULT 0 | 切片数量 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 4.3 实体关系

```
users 1──N requirements
users 1──N uploaded_files
users 1──N history_records
users 1──N knowledge_documents

requirements 1──1 uploaded_files (file_id, 可选)
requirements 1──N split_requirements
requirements 1──N chat_messages

split_requirements 1──N test_points

test_points 1──N test_cases
```

## 5. 开发计划

### 阶段一：基础设施搭建

> 目标：建立数据库、认证体系、项目骨架，为后续业务开发打好基础

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 1 | 引入 SQLAlchemy + Alembic | 配置 SQLite 数据库连接，创建迁移框架 | 无 |
| 2 | 创建 ORM 模型 | 按上述数据表设计创建所有 SQLAlchemy 模型 | 1 |
| 3 | 执行数据库迁移 | 生成并执行初始迁移脚本，创建所有表 | 2 |
| 4 | 引入 JWT 认证 | 安装 python-jose + passlib，实现 Token 生成/验证 | 1 |
| 5 | 实现密码加密 | 使用 bcrypt 加密存储密码 | 4 |
| 6 | 实现依赖注入 | `get_current_user` 依赖，从 Token 解析当前用户 | 4 |
| 7 | 重构目录结构 | 按目标目录结构重组代码，新增 schemas/、ai/、tasks/ 目录 | 1 |
| 8 | 统一响应格式 | 封装统一响应模型 `ApiResponse<T>` | 无 |
| 9 | 异常处理中间件 | 全局异常捕获，统一错误响应格式 | 无 |
| 10 | 更新 requirements.txt | 新增所有必要依赖 | 无 |

**新增依赖清单：**
```
sqlalchemy==2.0.x
alembic==1.13.x
python-jose[cryptography]==3.3.x
passlib[bcrypt]==1.7.x
openai==1.x
langgraph==0.x
langchain==0.x
langchain-openai==0.x
python-docx==1.x          # docx 文件解析
openpyxl==3.x             # xlsx 文件解析
exceljs 或 openpyxl        # Excel 导出
aiofiles==23.x            # 异步文件操作
sse-starlette==1.x        # Server-Sent Events（流式响应）
```

### 阶段二：用户认证模块

> 目标：实现完整的用户注册、登录、Token 管理功能

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 11 | 用户注册 API | `POST /api/auth/register`，用户名唯一性校验，密码加密存储 | 阶段一 |
| 12 | 用户登录 API | `POST /api/auth/login`，验证密码，返回 JWT Token + RefreshToken | 阶段一 |
| 13 | Token 刷新 API | `POST /api/auth/refresh`，用 RefreshToken 换取新 Token | 阶段一 |
| 14 | 获取用户信息 API | `GET /api/auth/user`，返回当前登录用户信息 | 阶段一 |
| 15 | 登出 API | `POST /api/auth/logout`，使 Token 失效 | 阶段一 |
| 16 | 认证守卫 | 所有 `/api/*` 路由（除注册/登录外）强制 JWT 认证 | 阶段一 |
| 17 | 数据隔离 | 所有查询自动按 `user_id` 过滤，确保用户只能访问自己的数据 | 16 |

### 阶段三：需求管理模块

> 目标：实现需求 CRUD、文件上传、需求标准化、需求拆分

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 18 | 文件上传 API | `POST /api/v1/upload`，支持 docx/xlsx，解析文件内容 | 阶段二 |
| 19 | docx 文件解析 | 使用 python-docx 提取文档文本内容 | 18 |
| 20 | xlsx 文件解析 | 使用 openpyxl 提取表格内容 | 18 |
| 21 | 创建需求 API | `POST /api/v1/requirements`，支持文本/文件两种模式 | 18 |
| 22 | 获取需求列表 API | `GET /api/v1/requirements`，分页、搜索、状态筛选 | 阶段二 |
| 23 | 获取需求详情 API | `GET /api/v1/requirements/{id}`，含标准化文档和拆分结果 | 阶段二 |
| 24 | 更新需求 API | `PUT /api/v1/requirements/{id}`，更新标题/内容/状态 | 阶段二 |
| 25 | 删除需求 API | `DELETE /api/v1/requirements/{id}`，级联删除关联数据 | 阶段二 |

### 阶段四：AI 服务集成与需求标准化

> 目标：封装大模型调用，实现需求标准化和多轮对话

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 26 | LLM 客户端封装 | 统一封装 OpenAI API 调用，支持流式/非流式响应 | 阶段一 |
| 27 | Prompt 模板设计 | 设计标准化、拆分、测试点、用例生成的 Prompt 模板 | 26 |
| 28 | 标准化 Agent | 使用 LangGraph 编排标准化流程，调用大模型生成标准文档 | 26, 27 |
| 29 | 执行标准化 API | `POST /api/v1/standardize`，调用标准化 Agent | 28 |
| 30 | 获取标准化结果 API | `GET /api/v1/standardize/{requirementId}` | 29 |
| 31 | AI 对话 API | `POST /api/v1/standardize/chat`，多轮对话调整标准文档 | 28 |
| 32 | 获取对话历史 API | `GET /api/v1/standardize/chat/{requirementId}` | 31 |
| 33 | 采纳/拒绝建议 API | `POST /api/v1/standardize/chat/{messageId}/confirm` 和 `/reject` | 31 |
| 34 | 知识库召回集成 | 标准化时可检索知识库内容作为参考（开关控制） | 28, 阶段七 |

### 阶段五：需求拆分与测试设计

> 目标：实现需求拆分、测试点生成、测试用例生成

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 35 | 拆分 Agent | 使用 LangGraph 编排需求拆分流程 | 阶段四 |
| 36 | 执行需求拆分 API | `POST /api/v1/split`，将标准化文档拆分为单个需求 | 35 |
| 37 | 获取拆分结果 API | `GET /api/v1/split/{requirementId}` | 36 |
| 38 | 拆分项 CRUD API | 更新/删除/手动添加拆分项 | 36 |
| 39 | 测试点 Agent | 使用 LangGraph 编排测试点生成流程 | 阶段四 |
| 40 | 生成测试点 API | `POST /api/test-points/generate`，根据需求生成测试点 | 39 |
| 41 | 测试点 CRUD API | 编辑/删除测试点，手动添加测试点 | 40 |
| 42 | 批量删除测试点 API | `POST /api/test-points/batch-delete` | 40 |
| 43 | 批量标记测试点 API | `POST /api/test-points/batch-mark` | 40 |
| 44 | 测试用例 Agent | 使用 LangGraph 编排测试用例生成流程 | 阶段四 |
| 45 | 生成测试用例 API | `POST /api/test-cases/generate`，根据测试点生成用例 | 44 |
| 46 | 测试用例 CRUD API | 编辑/删除测试用例，手动添加测试用例 | 45 |
| 47 | 批量删除测试用例 API | `POST /api/test-cases/batch-delete` | 45 |
| 48 | 批量标记测试用例 API | `POST /api/test-cases/batch-mark` | 45 |
| 49 | AI 调整 API | 对测试点/用例进行 AI 调整（多轮对话），支持图钉标记保留 | 39, 44 |
| 50 | 知识库召回集成 | 生成测试点/用例时可检索知识库内容作为参考 | 34, 40, 45 |

### 阶段六：异步任务管理

> 目标：实现快速生成、串行执行、进度追踪、任务取消

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 51 | 任务管理器 | 内存任务队列，管理异步生成任务的生命周期 | 阶段五 |
| 52 | 快速生成 API | `POST /api/tasks/generate`，一键触发所有需求的测试点+用例生成 | 51 |
| 53 | 串行执行引擎 | 按需求顺序串行执行，深度优先（需求→测试点→用例） | 51 |
| 54 | 进度追踪 | 实时计算并存储生成进度（如"需求3/10，已完成30%"） | 51 |
| 55 | SSE 进度推送 | `GET /api/tasks/progress`，Server-Sent Events 实时推送进度 | 54 |
| 56 | 获取任务列表 API | `GET /api/tasks`，返回当前用户的任务列表 | 51 |
| 57 | 取消任务 API | `DELETE /api/tasks/{id}`，取消正在执行的任务 | 51 |
| 58 | 节点状态更新 | 生成过程中实时更新需求节点和测试点节点的状态 | 54 |

### 阶段七：知识库模块重构

> 目标：将现有知识库模块重构为持久化存储，接入用户认证

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 59 | 知识库数据持久化 | 将内存存储迁移至 SQLite，使用 knowledge_documents 表 | 阶段二 |
| 60 | 知识库接入用户认证 | 所有知识库 API 加入用户认证和数据隔离 | 阶段二 |
| 61 | 文档上传重构 | 重构上传 API，关联用户，支持 docx/xlsx/pdf 解析 | 59, 60 |
| 62 | 文档切片优化 | 改进切片策略，支持按段落/标题语义切片 | 61 |
| 63 | Embedding 集成 | 接入 OpenAI Embedding API 替换模拟向量 | 26 |
| 64 | 文档删除重构 | 删除文档时同步清理 Milvus 向量和数据库记录 | 59 |
| 65 | 召回参数持久化 | 将召回参数存储到数据库而非内存 | 59 |
| 66 | 召回测试优化 | 接入真实 Embedding 进行召回测试 | 63 |

### 阶段八：历史记录与导出

> 目标：实现历史记录管理和 Excel 导出

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 67 | 历史记录自动创建 | 每次需求处理完成后自动创建历史记录 | 阶段五 |
| 68 | 获取历史记录列表 API | `GET /api/history`，分页查询 | 阶段二 |
| 69 | 获取历史记录详情 API | `GET /api/history/{id}`，含完整数据 | 阶段二 |
| 70 | 从历史记录恢复 | 支持从历史记录入口进入数据维护 | 68, 69 |
| 71 | Excel 导出服务 | 使用 openpyxl 生成 Excel，支持单元格合并 | 阶段五 |
| 72 | 导出测试用例 API | `GET /api/test-cases/export`，返回 Excel 文件流 | 71 |
| 73 | 导出标准化文档 API | `GET /api/v1/standardize/{requirementId}/export`，导出 Markdown | 阶段四 |

### 阶段九：集成测试与优化

> 目标：全流程联调、性能优化、安全加固

| 序号 | 任务 | 描述 | 依赖 |
|------|------|------|------|
| 74 | 全流程联调 | 登录→录入→标准化→拆分→生成→导出 完整流程测试 | 全部 |
| 75 | API 接口文档 | 确保 FastAPI 自动生成的 Swagger 文档完整准确 | 全部 |
| 76 | 错误处理完善 | 补充所有边界情况的错误处理和友好提示 | 全部 |
| 77 | 性能优化 | 数据库查询优化、AI 调用并发控制、缓存策略 | 全部 |
| 78 | 安全加固 | Token 过期策略、输入校验、SQL 注入防护、文件上传安全 | 全部 |
| 79 | 日志系统 | 引入 logging 模块，记录关键操作和错误日志 | 全部 |
| 80 | Docker 部署验证 | 确保 Dockerfile 和 start.sh 可正常部署 | 全部 |

## 6. API 接口清单

### 6.1 认证模块 `/api/auth`

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/auth/register | POST | 用户注册 | 二 |
| /api/auth/login | POST | 用户登录 | 二 |
| /api/auth/logout | POST | 用户登出 | 二 |
| /api/auth/user | GET | 获取用户信息 | 二 |
| /api/auth/refresh | POST | 刷新 Token | 二 |

### 6.2 需求模块 `/api/v1`

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/v1/upload | POST | 上传需求文档 | 三 |
| /api/v1/requirements | POST | 创建需求 | 三 |
| /api/v1/requirements | GET | 获取需求列表 | 三 |
| /api/v1/requirements/{id} | GET | 获取需求详情 | 三 |
| /api/v1/requirements/{id} | PUT | 更新需求 | 三 |
| /api/v1/requirements/{id} | DELETE | 删除需求 | 三 |

### 6.3 标准化模块 `/api/v1`

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/v1/standardize | POST | 执行标准化 | 四 |
| /api/v1/standardize/{requirementId} | GET | 获取标准化结果 | 四 |
| /api/v1/standardize/{requirementId}/export | GET | 导出标准化文档 | 八 |
| /api/v1/standardize/chat | POST | AI 对话 | 四 |
| /api/v1/standardize/chat/{requirementId} | GET | 获取对话历史 | 四 |
| /api/v1/standardize/chat/{messageId}/confirm | POST | 采纳建议 | 四 |
| /api/v1/standardize/chat/{messageId}/reject | POST | 拒绝建议 | 四 |

### 6.4 需求拆分模块 `/api/v1`

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/v1/split | POST | 执行需求拆分 | 五 |
| /api/v1/split/{requirementId} | GET | 获取拆分结果 | 五 |
| /api/v1/split/items/{id} | PUT | 更新拆分项 | 五 |
| /api/v1/split/items/{id} | DELETE | 删除拆分项 | 五 |
| /api/v1/split/items | POST | 手动添加拆分项 | 五 |

### 6.5 测试设计模块

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/test-points/generate | POST | 生成测试点 | 五 |
| /api/test-points/{id} | PUT | 编辑测试点 | 五 |
| /api/test-points/{id} | DELETE | 删除测试点 | 五 |
| /api/test-points | POST | 手动添加测试点 | 五 |
| /api/test-points/batch-delete | POST | 批量删除测试点 | 五 |
| /api/test-points/batch-mark | POST | 批量标记测试点 | 五 |
| /api/test-points/ai-adjust | POST | AI 调整测试点 | 五 |
| /api/test-cases/generate | POST | 生成测试用例 | 五 |
| /api/test-cases/{id} | PUT | 编辑测试用例 | 五 |
| /api/test-cases/{id} | DELETE | 删除测试用例 | 五 |
| /api/test-cases | POST | 手动添加测试用例 | 五 |
| /api/test-cases/batch-delete | POST | 批量删除测试用例 | 五 |
| /api/test-cases/batch-mark | POST | 批量标记测试用例 | 五 |
| /api/test-cases/ai-adjust | POST | AI 调整测试用例 | 五 |
| /api/test-cases/export | GET | 导出测试用例 Excel | 八 |

### 6.6 任务模块

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/tasks/generate | POST | 快速生成（一键触发） | 六 |
| /api/tasks | GET | 获取任务列表 | 六 |
| /api/tasks/{id} | DELETE | 取消任务 | 六 |
| /api/tasks/progress | GET | SSE 进度推送 | 六 |

### 6.7 历史记录模块

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/history | GET | 获取历史记录列表 | 八 |
| /api/history/{id} | GET | 获取历史记录详情 | 八 |

### 6.8 知识库模块 `/api/knowledge`

| API | 方法 | 说明 | 阶段 |
|-----|------|------|------|
| /api/knowledge/docs | POST | 上传文档 | 七 |
| /api/knowledge/docs | GET | 获取文档列表 | 七 |
| /api/knowledge/docs/{id} | GET | 获取文档详情 | 七 |
| /api/knowledge/docs/{id} | DELETE | 删除文档 | 七 |
| /api/knowledge/docs/{id}/content | GET | 查看文档内容 | 七 |
| /api/knowledge/recall-params | PUT | 调整召回参数 | 七 |
| /api/knowledge/recall-test | POST | 召回测试 | 七 |

## 7. AI 编排设计

### 7.1 LangGraph Agent 架构

```
┌─────────────────────────────────────────────────┐
│              LangGraph 编排层                     │
├─────────┬─────────┬──────────┬─────────────────┤
│标准化Agent│拆分Agent │测试点Agent│ 测试用例Agent    │
├─────────┼─────────┼──────────┼─────────────────┤
│ 输入:    │ 输入:    │ 输入:     │ 输入:           │
│ 原始需求  │ 标准文档  │ 拆分需求  │ 测试点          │
│         │         │          │                 │
│ 输出:    │ 输出:    │ 输出:     │ 输出:           │
│ 标准文档  │ 需求列表  │ 测试点列表│ 测试用例列表     │
│(Markdown)│(JSON)   │(JSON)    │(JSON)           │
├─────────┴─────────┴──────────┴─────────────────┤
│              共享 LLM Client                     │
│         (OpenAI GPT-4, 后端硬编码)                │
├─────────────────────────────────────────────────┤
│         可选: 知识库召回 (Milvus)                  │
└─────────────────────────────────────────────────┘
```

### 7.2 各 Agent 的 Prompt 设计要点

#### 标准化 Agent
- 输入：原始需求文本或文档内容
- 输出：符合 IEEE 830 标准的 Markdown 文档
- 要求：包含引言、需求概述、功能需求、非功能需求、约束条件、异常场景等章节

#### 拆分 Agent
- 输入：标准化后的 Markdown 文档
- 输出：拆分后的需求列表（JSON 数组）
- 要求：每个需求独立、完整、可测试，不遗漏不重复

#### 测试点 Agent
- 输入：单个拆分需求
- 输出：测试点列表（JSON 数组）
- 要求：覆盖功能、边界、异常、性能、安全等维度

#### 测试用例 Agent
- 输入：单个测试点 + 关联需求上下文
- 输出：测试用例列表（JSON 数组，符合模板结构）
- 要求：包含正例和反例，步骤清晰，预期结果可验证

### 7.3 AI 调整流程

```
用户右键节点 → 选择"AI调整"
    ↓
调起对话框 → 用户输入调整指令
    ↓
构建 Prompt（含当前节点内容 + 保留标记的节点 + 用户指令）
    ↓
调用 LLM → 返回调整后的内容
    ↓
用户确认 → 更新节点内容
```

**图钉标记逻辑**：
- 被标记的测试点/用例在 AI 调整时作为"必须保留"的约束写入 Prompt
- 未标记的数据在 AI 调整时可被替换或优化

## 8. 异步任务管理设计

### 8.1 任务执行流程

```
用户点击"快速生成"
    ↓
创建任务记录 → 返回 task_id
    ↓
后台线程启动串行执行:
    ↓
    需求1 → 生成测试点1.1, 1.2... → 生成用例1.1.1, 1.1.2...
    ↓
    需求2 → 生成测试点2.1, 2.2... → 生成用例2.1.1, 2.1.2...
    ↓
    ...（深度优先）
    ↓
    需求N → ...
    ↓
任务完成 → 更新状态
```

### 8.2 进度计算

```python
progress = {
    "total_requirements": 10,
    "current_requirement": 3,
    "current_requirement_name": "用户登录功能",
    "total_test_points": 0,       # 动态累加
    "generated_test_points": 0,   # 动态累加
    "total_test_cases": 0,        # 动态累加
    "generated_test_cases": 0,    # 动态累加
    "percentage": 30,             # 整体百分比
    "status": "running"           # running / completed / cancelled
}
```

### 8.3 SSE 推送格式

```
event: progress
data: {"total_requirements": 10, "current_requirement": 3, "percentage": 30, "status": "running"}

event: node_update
data: {"node_type": "requirement", "node_id": "xxx", "status": "generating"}

event: node_update
data: {"node_type": "test_point", "node_id": "yyy", "status": "completed"}

event: complete
data: {"status": "completed", "percentage": 100}
```

## 9. Excel 导出设计

### 9.1 导出格式

| caseName | caseProperty | preCondition | name | description | stepExpectedResult |
|----------|--------------|---------------|------|-------------|-------------------|
| 用户正常登录系统 | 正例 | 用户已注册并拥有有效的账号和密码 | 输入用户名 | 在登录页输入正确的用户名 | 用户名输入框显示输入的用户名 |
| (合并) | (合并) | (合并) | 输入密码 | 在登录页输入正确的密码 | 密码输入框显示输入的密码 |
| (合并) | (合并) | (合并) | 点击登录按钮 | 点击登录按钮 | 系统跳转至用户主页 |

### 9.2 合并规则

- 同一测试用例的多个步骤，`caseName`、`caseProperty`、`preCondition` 三列合并单元格
- 每个步骤占一行，`name`、`description`、`stepExpectedResult` 各占一列
- 使用 openpyxl 的 `merge_cells` 实现单元格合并

## 10. 关键技术决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 数据库 | SQLite | 轻量级，无需额外部署，适合个人使用模式 |
| ORM | SQLAlchemy 2.0 | Python 生态最成熟的 ORM，异步支持好 |
| 认证 | JWT (python-jose) | 无状态，适合前后端分离架构 |
| 密码加密 | bcrypt (passlib) | 业界标准，安全性高 |
| AI 编排 | LangGraph | 需求文档指定，支持复杂 Agent 流程编排 |
| 大模型 | OpenAI GPT-4 | 需求文档默认指定，后端硬编码配置 |
| 向量数据库 | Milvus | 需求文档指定，已有基础集成 |
| 文件解析 | python-docx + openpyxl | 分别处理 docx 和 xlsx 格式 |
| Excel 导出 | openpyxl | 支持单元格合并，功能完善 |
| 异步任务 | 内存队列 + threading | 轻量级方案，无需引入 Celery/Redis |
| 实时推送 | SSE (sse-starlette) | 比 WebSocket 更轻量，适合单向推送场景 |
| 数据库迁移 | Alembic | SQLAlchemy 配套迁移工具 |

## 11. 风险与应对

| 风险 | 描述 | 应对方案 |
|------|------|----------|
| AI 调用不稳定 | 大模型 API 可能超时或返回异常 | 增加重试机制（最多3次），设置超时时间，失败时返回友好错误提示 |
| 生成质量不达标 | AI 生成的测试点/用例质量参差不齐 | 精心设计 Prompt 模板，支持多轮对话调整，用户可手动编辑 |
| 并发资源占用 | 多用户同时触发快速生成导致资源耗尽 | 串行执行 + 全局任务队列限制，单用户同时只允许一个快速生成任务 |
| Milvus 连接失败 | Milvus 服务不可用时知识库功能不可用 | 知识库功能降级，不影响核心流程；增加连接重试和健康检查 |
| SQLite 并发写入 | SQLite 不支持高并发写入 | 个人使用模式下并发极低，如需扩展可迁移至 PostgreSQL |
| Token 安全 | JWT Token 泄露风险 | 设置合理过期时间（Access Token 2h），HTTPS 传输，HttpOnly Cookie |

## 12. 开发优先级总结

```
阶段一 (基础设施) ──→ 阶段二 (认证) ──→ 阶段三 (需求管理)
                                              │
                                              ↓
阶段七 (知识库重构) ←── 阶段四 (AI+标准化) ←───┘
         │              │
         ↓              ↓
阶段八 (历史+导出) ←── 阶段五 (拆分+测试设计)
                         │
                         ↓
                    阶段六 (异步任务)
                         │
                         ↓
                    阶段九 (集成测试)
```

**核心路径**：阶段一 → 二 → 三 → 四 → 五 → 六 → 九

**可并行**：阶段七（知识库重构）可与阶段四/五并行；阶段八可在阶段五完成后并行

---

**文档版本**: v1.0
**创建日期**: 2026-05-15
