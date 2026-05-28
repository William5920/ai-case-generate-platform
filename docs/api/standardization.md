# 需求标准化模块接口文档

## 概述

本文档描述智能测试用例平台「需求标准化」模块的接口规范，涵盖需求录入、模板管理、AI需求探索、文档标准化、AI文档调整、版本管理、质量评分、需求拆分、文档导出、知识库上传、历史记录等全部功能。

**核心流程**：用户录入需求 → 选择需求文档模板 → AI需求探索（结构化提问收集信息） → AI生成标准化文档 → AI/手动调整文档 → 需求拆分

**基础路径**：`/api/v1`

**通用规范**：
- 所有接口需携带 `Authorization: Bearer <token>` 请求头
- 请求体统一使用 `application/json`（文件上传除外）
- 响应体统一格式：

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {},
  "traceId": "uuid-string"
}
```

---

## 目录

- [1. 需求管理](#1-需求管理)
  - [1.1 创建需求](#11-创建需求)
  - [1.2 获取需求列表](#12-获取需求列表)
  - [1.3 获取需求详情](#13-获取需求详情)
  - [1.4 更新需求](#14-更新需求)
  - [1.5 删除需求](#15-删除需求)
- [2. 文件上传](#2-文件上传)
  - [2.1 上传需求文档](#21-上传需求文档)
- [3. 模板管理](#3-模板管理)
  - [3.1 获取模板列表](#31-获取模板列表)
  - [3.2 获取模板详情](#32-获取模板详情)
  - [3.3 AI推荐模板](#33-ai推荐模板)
- [4. AI需求探索](#4-ai需求探索)
  - [4.1 启动需求探索](#41-启动需求探索)
  - [4.2 发送探索对话消息](#42-发送探索对话消息)
  - [4.3 获取探索对话历史](#43-获取探索对话历史)
  - [4.4 获取探索状态](#44-获取探索状态)
- [5. 文档标准化](#5-文档标准化)
  - [5.1 执行标准化](#51-执行标准化)
  - [5.2 获取标准化结果](#52-获取标准化结果)
- [6. AI文档调整](#6-ai文档调整)
  - [6.1 发送调整对话消息](#61-发送调整对话消息)
  - [6.2 获取调整对话历史](#62-获取调整对话历史)
  - [6.3 采纳AI建议](#63-采纳ai建议)
  - [6.4 拒绝AI建议](#64-拒绝ai建议)
- [7. 版本管理](#7-版本管理)
  - [7.1 获取版本列表](#71-获取版本列表)
  - [7.2 获取版本详情](#72-获取版本详情)
  - [7.3 恢复版本](#73-恢复版本)
  - [7.4 获取版本差异](#74-获取版本差异)
- [8. 质量评分](#8-质量评分)
  - [8.1 执行质量评分](#81-执行质量评分)
- [9. 需求拆分](#9-需求拆分)
  - [9.1 执行需求拆分](#91-执行需求拆分)
  - [9.2 获取拆分结果列表](#92-获取拆分结果列表)
  - [9.3 更新拆分项](#93-更新拆分项)
  - [9.4 删除拆分项](#94-删除拆分项)
  - [9.5 手动添加拆分项](#95-手动添加拆分项)
  - [9.6 确认并进入测试设计](#96-确认并进入测试设计)
- [10. 文档导出](#10-文档导出)
  - [10.1 导出标准化文档](#101-导出标准化文档)
- [11. 知识库上传](#11-知识库上传)
  - [11.1 上传文档至知识库](#111-上传文档至知识库)
- [12. 历史记录](#12-历史记录)
  - [12.1 获取历史记录列表](#121-获取历史记录列表)
  - [12.2 获取历史记录详情](#122-获取历史记录详情)
- [13. 错误码说明](#13-错误码说明)

---

## 1. 需求管理

### 1.1 创建需求

用户录入新需求（文本或上传文档后），创建需求记录。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 是 | 需求标题，最大长度 200 |
| inputMode | string | 是 | 输入模式：`text`（文本输入）/ `file`（文档上传） |
| rawContent | string | 否 | 原始需求文本内容（inputMode=text 时必填） |
| fileId | string | 否 | 上传文件的ID（inputMode=file 时必填） |
| templateId | string | 否 | 需求文档模板ID：`user-story`（用户故事需求文档）/ `srs`（SRS需求规格说明书），不传则默认 `user-story` |

**请求示例**

```json
{
  "title": "用户登录系统需求",
  "inputMode": "text",
  "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。",
  "templateId": "srs"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 需求ID |
| data.title | string | 需求标题 |
| data.inputMode | string | 输入模式 |
| data.rawContent | string | 原始需求内容 |
| data.templateId | string | 需求文档模板ID |
| data.status | string | 状态：`draft`（草稿）/ `exploring`（探索中）/ `standardized`（已标准化）/ `splitted`（已拆分） |
| data.createdAt | string | 创建时间 |
| data.updatedAt | string | 更新时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "req_001",
    "title": "用户登录系统需求",
    "inputMode": "text",
    "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。",
    "templateId": "srs",
    "status": "draft",
    "createdAt": "2026-05-11T10:00:00.000Z",
    "updatedAt": "2026-05-11T10:00:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 1.2 获取需求列表

获取当前用户的所有需求列表，用于左侧历史记录展示。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements` |
| Method | `GET` |

**请求参数（Query）**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| pageNo | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页条数，默认 20 |
| keyword | string | 否 | 搜索关键词，匹配标题 |
| status | string | 否 | 状态筛选：`draft` / `exploring` / `standardized` / `splitted` |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.items | array | 需求列表 |
| data.items[].id | string | 需求ID |
| data.items[].title | string | 需求标题 |
| data.items[].status | string | 状态 |
| data.items[].createdAt | string | 创建时间 |
| data.items[].updatedAt | string | 更新时间 |
| data.pageNo | number | 当前页码 |
| data.pageSize | number | 每页条数 |
| data.total | number | 总条数 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      {
        "id": "req_001",
        "title": "用户登录系统需求",
        "status": "splitted",
        "createdAt": "2026-05-10T14:30:00.000Z",
        "updatedAt": "2026-05-10T15:00:00.000Z"
      },
      {
        "id": "req_002",
        "title": "数据导出功能需求",
        "status": "standardized",
        "createdAt": "2026-05-09T10:15:00.000Z",
        "updatedAt": "2026-05-09T10:30:00.000Z"
      }
    ],
    "pageNo": 1,
    "pageSize": 20,
    "total": 2
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 1.3 获取需求详情

获取单个需求的完整信息，包含标准化文档、拆分结果等。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 需求ID |
| data.title | string | 需求标题 |
| data.inputMode | string | 输入模式 |
| data.rawContent | string | 原始需求内容 |
| data.templateId | string | 需求文档模板ID |
| data.fileInfo | object | 上传文件信息（inputMode=file 时有值） |
| data.fileInfo.fileName | string | 原始文件名 |
| data.fileInfo.fileSize | number | 文件大小（字节） |
| data.fileInfo.fileType | string | 文件类型 |
| data.exploreData | array | AI需求探索收集的数据 |
| data.exploreData[].dimensionKey | string | 探索维度标识 |
| data.exploreData[].dimensionLabel | string | 探索维度名称 |
| data.exploreData[].content | string | 该维度的探索内容 |
| data.standardizedContent | string | 标准化后的文档内容（Markdown） |
| data.splitRequirements | array | 拆分后的需求列表 |
| data.splitRequirements[].id | string | 拆分项ID |
| data.splitRequirements[].content | string | 拆分项内容 |
| data.splitRequirements[].order | number | 排序序号 |
| data.status | string | 状态 |
| data.createdAt | string | 创建时间 |
| data.updatedAt | string | 更新时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": "req_001",
    "title": "用户登录系统需求",
    "inputMode": "text",
    "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。",
    "templateId": "srs",
    "fileInfo": null,
    "exploreData": [
      { "dimensionKey": "purpose", "dimensionLabel": "编写目的", "content": "本文档旨在明确用户登录系统的功能与非功能需求..." },
      { "dimensionKey": "background", "dimensionLabel": "项目背景", "content": "当前系统缺乏统一的身份认证机制..." },
      { "dimensionKey": "functional", "dimensionLabel": "功能需求", "content": "1. 用户名密码登录 2. 记住密码 3. 登录失败锁定..." }
    ],
    "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
    "splitRequirements": [
      { "id": "split_001", "content": "实现用户名密码登录功能", "order": 1 },
      { "id": "split_002", "content": "实现密码复杂度校验", "order": 2 },
      { "id": "split_003", "content": "实现登录失败锁定机制", "order": 3 }
    ],
    "status": "splitted",
    "createdAt": "2026-05-10T14:30:00.000Z",
    "updatedAt": "2026-05-10T15:00:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 1.4 更新需求

更新需求的基本信息或标准化文档内容。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}` |
| Method | `PUT` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 否 | 需求标题 |
| rawContent | string | 否 | 原始需求内容 |
| templateId | string | 否 | 需求文档模板ID |
| standardizedContent | string | 否 | 标准化文档内容（用户手动编辑后保存） |
| exploreData | array | 否 | AI需求探索收集的数据 |
| status | string | 否 | 状态更新 |

**请求示例**

```json
{
  "title": "用户登录系统需求（修订版）",
  "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n..."
}
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "req_001",
    "title": "用户登录系统需求（修订版）",
    "updatedAt": "2026-05-11T11:00:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 1.5 删除需求

删除指定需求及其关联的所有数据（标准化文档、拆分结果、对话记录、版本记录）。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}` |
| Method | `DELETE` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "删除成功",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 2. 文件上传

### 2.1 上传需求文档

上传需求文档，返回文件ID供创建需求时引用。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/upload` |
| Method | `POST` |
| Content-Type | `multipart/form-data` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 需求文档文件 |
| type | string | 是 | 文件用途类型：`requirement` |

**文件限制**

| 限制项 | 值 |
|--------|-----|
| 允许格式 | .doc, .docx, .pdf, .md, .xlsx |
| 最大大小 | 10MB |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.fileId | string | 文件唯一标识 |
| data.fileName | string | 原始文件名 |
| data.fileSize | number | 文件大小（字节） |
| data.fileType | string | 文件MIME类型 |
| data.uploadedAt | string | 上传时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "上传成功",
  "data": {
    "fileId": "file_001",
    "fileName": "用户登录需求文档.docx",
    "fileSize": 25600,
    "fileType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "uploadedAt": "2026-05-11T10:00:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 3. 模板管理

### 3.1 获取模板列表

获取系统预设的需求文档模板列表，用于步骤1模板选择区域展示。列表按展示顺序返回，用户故事需求文档排在前面。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/templates` |
| Method | `GET` |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.templates | array | 模板列表 |
| data.templates[].id | string | 模板ID：`srs` / `user-story` |
| data.templates[].name | string | 模板名称 |
| data.templates[].description | string | 模板描述 |
| data.templates[].icon | string | 模板图标 |
| data.templates[].tags | array | 模板标签列表 |
| data.templates[].dimensions | array | 模板探索维度列表 |
| data.templates[].dimensions[].key | string | 维度标识 |
| data.templates[].dimensions[].label | string | 维度名称 |
| data.templates[].dimensions[].question | string | 该维度的AI提问内容 |
| data.templates[].sections | array | 模板章节结构列表 |
| data.templates[].sections[].id | string | 章节ID |
| data.templates[].sections[].title | string | 章节标题 |
| data.templates[].sections[].required | boolean | 是否必填章节 |
| data.templates[].sections[].children | array | 子章节列表 |
| data.templates[].sections[].children[].id | string | 子章节ID |
| data.templates[].sections[].children[].title | string | 子章节标题 |
| data.templates[].sections[].children[].placeholder | string | 占位提示文本 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "templates": [
      {
        "id": "srs",
        "name": "SRS 需求规格说明书",
        "description": "适用于瀑布式开发，基于 IEEE 830 标准，文档完整详细",
        "icon": "📋",
        "tags": ["瀑布式", "详细", "完整"],
        "dimensions": [
          { "key": "purpose", "label": "编写目的", "question": "这份需求文档的编写目的是什么？主要面向哪些读者？" },
          { "key": "background", "label": "项目背景", "question": "请描述项目的业务背景和要解决的问题？" },
          { "key": "terms", "label": "术语定义", "question": "项目中是否有需要统一定义的专业术语或缩写？" },
          { "key": "goal", "label": "业务目标", "question": "本需求要达成的核心业务目标是什么？" },
          { "key": "role", "label": "用户角色", "question": "系统涉及哪些用户角色？各角色的职责是什么？" },
          { "key": "flow", "label": "核心业务流程", "question": "请描述核心业务流程的主要步骤？" },
          { "key": "functional", "label": "功能需求", "question": "系统需要实现哪些具体功能？请逐一描述。" },
          { "key": "performance", "label": "性能需求", "question": "对系统性能有什么要求？如响应时间、并发量、吞吐量等。" },
          { "key": "security", "label": "安全性需求", "question": "对数据安全、访问控制、审计日志等有什么要求？" },
          { "key": "availability", "label": "可用性需求", "question": "对系统可用率、故障恢复时间等有什么要求？" },
          { "key": "compatibility", "label": "兼容性需求", "question": "需要兼容哪些浏览器、操作系统或设备？" },
          { "key": "tech_constraint", "label": "技术约束", "question": "是否有技术栈、框架、部署环境等技术限制？" },
          { "key": "business_constraint", "label": "业务约束", "question": "是否有合规要求、行业标准等业务限制？" },
          { "key": "regulatory", "label": "法规约束", "question": "是否需要遵守数据保护法、行业监管等法规？" },
          { "key": "exception", "label": "异常场景", "question": "需要处理哪些异常场景？如网络超时、数据校验失败等。" }
        ],
        "sections": [
          {
            "id": "intro",
            "title": "1. 引言",
            "required": true,
            "children": [
              { "id": "intro-purpose", "title": "1.1 编写目的", "placeholder": "说明本文档的编写目的和预期读者" },
              { "id": "intro-background", "title": "1.2 项目背景", "placeholder": "描述项目背景、业务场景和要解决的问题" },
              { "id": "intro-terms", "title": "1.3 术语定义", "placeholder": "定义文档中使用的专业术语和缩写" }
            ]
          },
          {
            "id": "overview",
            "title": "2. 需求概述",
            "required": true,
            "children": [
              { "id": "overview-goal", "title": "2.1 业务目标", "placeholder": "描述本需求要达成的业务目标" },
              { "id": "overview-role", "title": "2.2 用户角色", "placeholder": "列出涉及的用户角色及其职责" },
              { "id": "overview-flow", "title": "2.3 核心业务流程", "placeholder": "描述核心业务流程的主要步骤" }
            ]
          },
          {
            "id": "functional",
            "title": "3. 功能需求",
            "required": true,
            "children": [
              { "id": "func-module-1", "title": "3.1 功能模块一", "placeholder": "描述第一个功能模块的详细需求" },
              { "id": "func-module-2", "title": "3.2 功能模块二", "placeholder": "描述第二个功能模块的详细需求" }
            ]
          },
          {
            "id": "non-functional",
            "title": "4. 非功能需求",
            "required": true,
            "children": [
              { "id": "nf-performance", "title": "4.1 性能需求", "placeholder": "如响应时间、并发量、吞吐量等指标" },
              { "id": "nf-security", "title": "4.2 安全性需求", "placeholder": "如数据加密、访问控制、审计日志等" },
              { "id": "nf-availability", "title": "4.3 可用性需求", "placeholder": "如系统可用率、故障恢复时间等" },
              { "id": "nf-compatibility", "title": "4.4 兼容性需求", "placeholder": "如浏览器兼容、操作系统兼容等" }
            ]
          },
          {
            "id": "constraints",
            "title": "5. 约束条件",
            "required": true,
            "children": [
              { "id": "const-tech", "title": "5.1 技术约束", "placeholder": "如开发语言、框架、部署环境等技术限制" },
              { "id": "const-business", "title": "5.2 业务约束", "placeholder": "如合规要求、行业标准等业务限制" },
              { "id": "const-regulatory", "title": "5.3 法规约束", "placeholder": "如数据保护法、行业监管要求等法规限制" }
            ]
          },
          {
            "id": "exceptions",
            "title": "6. 异常场景处理",
            "required": true,
            "children": [
              { "id": "exc-1", "title": "6.1 异常场景一", "placeholder": "描述异常场景及处理方式" },
              { "id": "exc-2", "title": "6.2 异常场景二", "placeholder": "描述异常场景及处理方式" }
            ]
          }
        ]
      },
      {
        "id": "user-story",
        "name": "用户故事需求文档",
        "description": "适用于敏捷式开发，以用户故事为核心，文档简洁聚焦",
        "icon": "📝",
        "tags": ["敏捷式", "简洁", "聚焦"],
        "dimensions": [
          { "key": "background", "label": "背景与目标", "question": "请描述项目的背景和要达成的目标？" },
          { "key": "scope", "label": "范围与优先级", "question": "本次需求的范围是什么？哪些功能优先级最高？" },
          { "key": "role", "label": "用户角色", "question": "系统涉及哪些用户角色？请描述各角色的特征。" },
          { "key": "story", "label": "用户故事", "question": "请描述核心的用户故事：作为XX，我希望XX，以便XX。" },
          { "key": "acceptance", "label": "验收标准", "question": "每个用户故事的验收标准是什么？怎样算完成？" },
          { "key": "rule", "label": "业务规则", "question": "有哪些业务规则需要遵守？如计算逻辑、状态流转等。" },
          { "key": "data", "label": "数据需求", "question": "涉及哪些核心数据实体？数据之间的关系是什么？" },
          { "key": "non-functional", "label": "非功能需求", "question": "对性能、安全性、可用性等有什么关键要求？" },
          { "key": "dependency", "label": "依赖与假设", "question": "有哪些外部依赖？做了哪些假设条件？" }
        ],
        "sections": [
          {
            "id": "overview",
            "title": "1. 需求概述",
            "required": true,
            "children": [
              { "id": "ov-background", "title": "1.1 背景与目标", "placeholder": "描述项目背景和要达成的目标" },
              { "id": "ov-scope", "title": "1.2 范围与优先级", "placeholder": "明确需求范围和优先级排序" }
            ]
          },
          {
            "id": "roles",
            "title": "2. 用户角色",
            "required": true,
            "children": [
              { "id": "role-1", "title": "2.1 角色一", "placeholder": "描述用户角色的特征和职责" },
              { "id": "role-2", "title": "2.2 角色二", "placeholder": "描述用户角色的特征和职责" }
            ]
          },
          {
            "id": "stories",
            "title": "3. 用户故事",
            "required": true,
            "children": [
              { "id": "story-1", "title": "3.1 用户故事一", "placeholder": "作为XX，我希望XX，以便XX" },
              { "id": "story-1-acceptance", "title": "3.1.1 验收标准", "placeholder": "列出验收标准，怎样算完成" },
              { "id": "story-2", "title": "3.2 用户故事二", "placeholder": "作为XX，我希望XX，以便XX" },
              { "id": "story-2-acceptance", "title": "3.2.2 验收标准", "placeholder": "列出验收标准，怎样算完成" }
            ]
          },
          {
            "id": "rules",
            "title": "4. 业务规则",
            "required": true,
            "children": [
              { "id": "rule-1", "title": "4.1 业务规则一", "placeholder": "描述业务规则，如计算逻辑、状态流转等" },
              { "id": "rule-2", "title": "4.2 业务规则二", "placeholder": "描述业务规则" }
            ]
          },
          {
            "id": "data",
            "title": "5. 数据需求",
            "required": true,
            "children": [
              { "id": "data-entity", "title": "5.1 核心数据实体", "placeholder": "列出核心数据实体及其属性" },
              { "id": "data-relation", "title": "5.2 数据关系", "placeholder": "描述数据实体之间的关系" }
            ]
          },
          {
            "id": "non-functional",
            "title": "6. 非功能需求",
            "required": false,
            "children": [
              { "id": "nf-key", "title": "6.1 关键非功能需求", "placeholder": "列出关键的性能、安全、可用性要求" }
            ]
          },
          {
            "id": "dependencies",
            "title": "7. 依赖与假设",
            "required": false,
            "children": [
              { "id": "dep-external", "title": "7.1 外部依赖", "placeholder": "列出外部系统或服务依赖" },
              { "id": "dep-assumption", "title": "7.2 假设条件", "placeholder": "列出已做的假设条件" }
            ]
          }
        ]
      }
    ]
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 3.2 获取模板详情

获取指定模板的完整信息，包含维度和章节结构。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/templates/{id}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 模板ID：`srs` / `user-story` |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 模板ID |
| data.name | string | 模板名称 |
| data.description | string | 模板描述 |
| data.icon | string | 模板图标 |
| data.tags | array | 模板标签列表 |
| data.dimensions | array | 模板探索维度列表（同3.1） |
| data.sections | array | 模板章节结构列表（同3.1） |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": "srs",
    "name": "SRS 需求规格说明书",
    "description": "适用于瀑布式开发，基于 IEEE 830 标准，文档完整详细",
    "icon": "📋",
    "tags": ["瀑布式", "详细", "完整"],
    "dimensions": [
      { "key": "purpose", "label": "编写目的", "question": "这份需求文档的编写目的是什么？主要面向哪些读者？" },
      { "key": "background", "label": "项目背景", "question": "请描述项目的业务背景和要解决的问题？" }
    ],
    "sections": [
      {
        "id": "intro",
        "title": "1. 引言",
        "required": true,
        "children": [
          { "id": "intro-purpose", "title": "1.1 编写目的", "placeholder": "说明本文档的编写目的和预期读者" },
          { "id": "intro-background", "title": "1.2 项目背景", "placeholder": "描述项目背景、业务场景和要解决的问题" }
        ]
      }
    ]
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 3.3 AI推荐模板

根据用户输入的需求内容，AI分析并推荐最合适的需求文档模板。文档上传模式下自动调用此接口推荐模板。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/templates/recommend` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 需求文本内容（文本输入模式直接传入；文档上传模式传入解析后的文本） |
| inputMode | string | 是 | 输入模式：`text` / `file` |

**请求示例**

```json
{
  "content": "本项目采用敏捷开发模式，以Sprint迭代方式推进，需要实现用户登录的MVP版本...",
  "inputMode": "text"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.recommendedTemplateId | string | 推荐的模板ID：`srs` / `user-story` |
| data.confidence | number | 推荐置信度（0-1），值越高表示推荐越确定 |
| data.reason | string | 推荐理由说明 |

**推荐规则说明**

系统根据需求内容中的关键词进行匹配分析：
- **敏捷关键词**：迭代、sprint、用户故事、敏捷、scrum、看板、backlog、MVP、增量 → 推荐用户故事模板
- **瀑布关键词**：规格、阶段、里程碑、评审、基线、配置管理、验收测试、SRS → 推荐SRS模板
- 两者得分相同时默认推荐SRS模板

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "推荐成功",
  "data": {
    "recommendedTemplateId": "user-story",
    "confidence": 0.85,
    "reason": "需求内容中包含「敏捷」「Sprint迭代」「MVP」等敏捷开发关键词，建议使用用户故事需求文档模板"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 4. AI需求探索

### 4.1 启动需求探索

用户在步骤2进入需求探索阶段时，启动AI需求探索会话。AI根据所选模板的维度列表，开始结构化提问。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/explore/start` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| templateId | string | 是 | 需求文档模板ID |
| rawContent | string | 否 | 原始需求文本内容（用于AI理解上下文） |
| fileId | string | 否 | 上传文件ID（文档上传模式时传入） |

**请求示例**

```json
{
  "requirementId": "req_001",
  "templateId": "srs",
  "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.sessionId | string | 探索会话ID |
| data.requirementId | string | 需求ID |
| data.templateId | string | 使用的模板ID |
| data.totalDimensions | number | 模板总维度数 |
| data.exploredDimensions | array | 已探索的维度列表（初始为空） |
| data.understandingScore | number | 需求理解度（0-100，初始为0） |
| data.firstQuestion | object | AI的第一个提问 |
| data.firstQuestion.dimensionKey | string | 提问对应的维度标识 |
| data.firstQuestion.dimensionLabel | string | 提问对应的维度名称 |
| data.firstQuestion.content | string | AI提问内容 |
| data.status | string | 探索状态：`active`（进行中） |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "探索会话已启动",
  "data": {
    "sessionId": "exp_001",
    "requirementId": "req_001",
    "templateId": "srs",
    "totalDimensions": 15,
    "exploredDimensions": [],
    "understandingScore": 0,
    "firstQuestion": {
      "dimensionKey": "purpose",
      "dimensionLabel": "编写目的",
      "content": "这份需求文档的编写目的是什么？主要面向哪些读者？"
    },
    "status": "active"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 4.2 发送探索对话消息

在需求探索阶段，用户回复AI的提问或主动提供信息。AI根据用户回复更新探索状态，并继续提出下一个维度的提问。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/explore/chat` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | string | 是 | 探索会话ID |
| requirementId | string | 是 | 需求ID |
| message | string | 是 | 用户发送的消息内容 |
| dimensionKey | string | 否 | 当前回复对应的维度标识（用于追踪探索进度） |

**请求示例**

```json
{
  "sessionId": "exp_001",
  "requirementId": "req_001",
  "message": "这份文档主要是给开发团队和测试团队参考，明确登录系统的功能边界和验收标准。",
  "dimensionKey": "purpose"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.messageId | string | 消息ID |
| data.role | string | 角色：`assistant` |
| data.content | string | AI回复的文本内容 |
| data.type | string | 消息类型：`question`（提问）/ `followup`（追问）/ `summary`（总结） |
| data.dimensionKey | string | 当前提问对应的维度标识（type=question 时有值） |
| data.dimensionLabel | string | 当前提问对应的维度名称 |
| data.exploredDimensions | array | 已探索完成的维度key列表 |
| data.totalDimensions | number | 模板总维度数 |
| data.understandingScore | number | 当前需求理解度（0-100） |
| data.canGenerate | boolean | 是否达到可生成文档的条件（理解度≥80%或所有维度已探索） |
| data.createdAt | string | 消息创建时间 |

**理解度计算规则**

| 条件 | 理解度 |
|------|--------|
| 已探索维度数 / 总维度数 × 80% | 基础分 |
| 用户回复内容丰富度加分 | 0-20% |
| 理解度 ≥ 80% 时 canGenerate = true | - |

**响应示例（提问类型）**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "messageId": "msg_exp_002",
    "role": "assistant",
    "content": "明白了，文档主要面向开发和测试团队。接下来想了解一下项目背景：请描述项目的业务背景和要解决的问题？",
    "type": "question",
    "dimensionKey": "background",
    "dimensionLabel": "项目背景",
    "exploredDimensions": ["purpose"],
    "totalDimensions": 15,
    "understandingScore": 7,
    "canGenerate": false,
    "createdAt": "2026-05-11T10:05:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例（可生成文档）**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "messageId": "msg_exp_012",
    "role": "assistant",
    "content": "感谢您的详细回答！我已经对需求有了充分的理解，现在可以为您生成标准化文档了。您也可以继续补充其他维度的信息，或者点击「生成文档」按钮开始生成。",
    "type": "summary",
    "dimensionKey": null,
    "dimensionLabel": null,
    "exploredDimensions": ["purpose", "background", "terms", "goal", "role", "flow", "functional", "performance", "security", "availability", "compatibility", "tech_constraint"],
    "totalDimensions": 15,
    "understandingScore": 82,
    "canGenerate": true,
    "createdAt": "2026-05-11T10:20:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 4.3 获取探索对话历史

获取指定需求探索会话的对话历史记录。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/explore/chat/{requirementId}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**请求参数（Query）**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | string | 否 | 探索会话ID（不传则获取最新会话） |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.sessionId | string | 探索会话ID |
| data.messages | array | 对话消息列表 |
| data.messages[].messageId | string | 消息ID |
| data.messages[].role | string | 角色：`user` / `assistant` |
| data.messages[].content | string | 消息内容 |
| data.messages[].type | string | 消息类型（仅 assistant）：`question` / `followup` / `summary` |
| data.messages[].dimensionKey | string | 对应维度标识 |
| data.messages[].dimensionLabel | string | 对应维度名称 |
| data.messages[].createdAt | string | 消息时间 |
| data.exploredDimensions | array | 已探索维度列表 |
| data.totalDimensions | number | 总维度数 |
| data.understandingScore | number | 当前理解度 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "sessionId": "exp_001",
    "messages": [
      {
        "messageId": "msg_exp_001",
        "role": "assistant",
        "content": "这份需求文档的编写目的是什么？主要面向哪些读者？",
        "type": "question",
        "dimensionKey": "purpose",
        "dimensionLabel": "编写目的",
        "createdAt": "2026-05-11T10:00:00.000Z"
      },
      {
        "messageId": "msg_exp_001_reply",
        "role": "user",
        "content": "这份文档主要是给开发团队和测试团队参考，明确登录系统的功能边界和验收标准。",
        "dimensionKey": "purpose",
        "dimensionLabel": "编写目的",
        "createdAt": "2026-05-11T10:05:00.000Z"
      },
      {
        "messageId": "msg_exp_002",
        "role": "assistant",
        "content": "明白了，文档主要面向开发和测试团队。接下来想了解一下项目背景：请描述项目的业务背景和要解决的问题？",
        "type": "question",
        "dimensionKey": "background",
        "dimensionLabel": "项目背景",
        "createdAt": "2026-05-11T10:05:00.000Z"
      }
    ],
    "exploredDimensions": ["purpose"],
    "totalDimensions": 15,
    "understandingScore": 7
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 4.4 获取探索状态

获取当前需求探索的实时状态，包括理解度、已探索维度等信息。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/explore/status` |
| Method | `GET` |

**请求参数（Query）**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 探索会话ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.sessionId | string | 探索会话ID |
| data.requirementId | string | 需求ID |
| data.templateId | string | 使用的模板ID |
| data.status | string | 探索状态：`active`（进行中）/ `completed`（已完成）/ `abandoned`（已放弃） |
| data.totalDimensions | number | 模板总维度数 |
| data.exploredDimensions | array | 已探索完成的维度key列表 |
| data.understandingScore | number | 需求理解度（0-100） |
| data.canGenerate | boolean | 是否达到可生成文档的条件 |
| data.exploreData | array | 已收集的探索数据 |
| data.exploreData[].dimensionKey | string | 维度标识 |
| data.exploreData[].dimensionLabel | string | 维度名称 |
| data.exploreData[].content | string | 该维度的探索内容 |
| data.startedAt | string | 探索开始时间 |
| data.updatedAt | string | 最后更新时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "sessionId": "exp_001",
    "requirementId": "req_001",
    "templateId": "srs",
    "status": "active",
    "totalDimensions": 15,
    "exploredDimensions": ["purpose", "background", "goal", "role", "functional", "performance", "security"],
    "understandingScore": 52,
    "canGenerate": false,
    "exploreData": [
      { "dimensionKey": "purpose", "dimensionLabel": "编写目的", "content": "面向开发和测试团队，明确功能边界和验收标准" },
      { "dimensionKey": "background", "dimensionLabel": "项目背景", "content": "当前系统缺乏统一身份认证机制，需建设标准化登录模块" },
      { "dimensionKey": "goal", "dimensionLabel": "业务目标", "content": "实现安全可靠的用户身份认证，支持多端登录" },
      { "dimensionKey": "role", "dimensionLabel": "用户角色", "content": "普通用户、系统管理员" },
      { "dimensionKey": "functional", "dimensionLabel": "功能需求", "content": "用户名密码登录、记住密码、登录失败锁定、退出登录" },
      { "dimensionKey": "performance", "dimensionLabel": "性能需求", "content": "登录响应时间≤2秒，支持1000并发" },
      { "dimensionKey": "security", "dimensionLabel": "安全性需求", "content": "密码bcrypt加密，5次失败锁定30分钟，HTTPS传输" }
    ],
    "startedAt": "2026-05-11T10:00:00.000Z",
    "updatedAt": "2026-05-11T10:15:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 5. 文档标准化

### 5.1 执行标准化

调用大模型将原始需求和探索数据转换为符合所选模板标准的 Markdown 文档。支持AI探索后生成和用户手动触发生成两种方式。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| templateId | string | 是 | 需求文档模板ID：`srs` / `user-story` |
| inputMode | string | 是 | 输入模式：`text` / `file` |
| rawContent | string | 否 | 原始需求文本（inputMode=text 时必填） |
| fileId | string | 否 | 上传文件ID（inputMode=file 时必填） |
| exploreData | array | 否 | AI需求探索收集的数据（探索后生成时传入） |
| exploreData[].dimensionKey | string | 否 | 维度标识 |
| exploreData[].dimensionLabel | string | 否 | 维度名称 |
| exploreData[].content | string | 否 | 该维度的探索内容 |

**请求示例（探索后生成）**

```json
{
  "requirementId": "req_001",
  "templateId": "srs",
  "inputMode": "text",
  "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。",
  "exploreData": [
    { "dimensionKey": "purpose", "dimensionLabel": "编写目的", "content": "面向开发和测试团队，明确功能边界和验收标准" },
    { "dimensionKey": "background", "dimensionLabel": "项目背景", "content": "当前系统缺乏统一身份认证机制" },
    { "dimensionKey": "functional", "dimensionLabel": "功能需求", "content": "用户名密码登录、记住密码、登录失败锁定、退出登录" },
    { "dimensionKey": "security", "dimensionLabel": "安全性需求", "content": "密码bcrypt加密，5次失败锁定30分钟，HTTPS传输" }
  ]
}
```

**请求示例（直接生成，无探索数据）**

```json
{
  "requirementId": "req_001",
  "templateId": "srs",
  "inputMode": "text",
  "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.requirementId | string | 需求ID |
| data.standardizedContent | string | 标准化后的 Markdown 文档内容 |
| data.templateId | string | 使用的模板ID |
| data.versionId | string | 初始版本ID |
| data.versionNumber | number | 版本号（初始为 1） |
| data.completedAt | string | 标准化完成时间 |

**SRS模板文档结构（templateId=srs）**

基于 IEEE 830 标准生成：

```
# <需求标题>需求规格说明书

## 1. 引言
### 1.1 编写目的
### 1.2 项目背景
### 1.3 术语定义

## 2. 需求概述
### 2.1 业务目标
### 2.2 用户角色
### 2.3 核心业务流程

## 3. 功能需求
### 3.1 功能模块一
### 3.2 功能模块二

## 4. 非功能需求
### 4.1 性能需求
### 4.2 安全性需求
### 4.3 可用性需求
### 4.4 兼容性需求

## 5. 约束条件
### 5.1 技术约束
### 5.2 业务约束
### 5.3 法规约束

## 6. 异常场景处理
### 6.1 异常场景一
### 6.2 异常场景二
```

**用户故事模板文档结构（templateId=user-story）**

基于敏捷用户故事格式生成：

```
# <需求标题>需求文档（敏捷版）

## 1. 需求概述
### 1.1 背景与目标
### 1.2 范围与优先级

## 2. 用户角色
### 2.1 角色一
### 2.2 角色二

## 3. 用户故事
### 3.1 用户故事一
### 3.1.1 验收标准
### 3.2 用户故事二
### 3.2.1 验收标准

## 4. 业务规则
### 4.1 业务规则一
### 4.2 业务规则二

## 5. 数据需求
### 5.1 核心数据实体
### 5.2 数据关系

## 6. 非功能需求
### 6.1 关键非功能需求

## 7. 依赖与假设
### 7.1 外部依赖
### 7.2 假设条件
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "标准化完成",
  "data": {
    "requirementId": "req_001",
    "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n### 1.1 编写目的\n...",
    "templateId": "srs",
    "versionId": "ver_001",
    "versionNumber": 1,
    "completedAt": "2026-05-11T10:00:05.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 5.2 获取标准化结果

获取需求当前的标准化文档内容。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/{requirementId}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.requirementId | string | 需求ID |
| data.standardizedContent | string | 标准化文档内容 |
| data.currentVersionId | string | 当前版本ID |
| data.currentVersionNumber | number | 当前版本号 |
| data.updatedAt | string | 最后更新时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "requirementId": "req_001",
    "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
    "currentVersionId": "ver_003",
    "currentVersionNumber": 3,
    "updatedAt": "2026-05-11T10:30:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 6. AI文档调整

### 6.1 发送调整对话消息

在文档编辑阶段，向AI发送对话消息，AI以文档调整模式回复。AI会提出建议但不会直接修改文档，需用户确认后才生效。此接口同时用于编辑阶段的AI助手侧边栏对话。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/chat` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| message | string | 是 | 用户发送的消息内容 |
| currentContent | string | 是 | 当前标准化文档内容（用于AI上下文理解） |
| templateId | string | 否 | 需求文档模板ID（用于模板感知的调整建议） |
| context | object | 否 | 额外上下文信息 |
| context.quickTopic | string | 否 | 快捷话题标识（如 `security`、`performance`、`exception`） |

**请求示例**

```json
{
  "requirementId": "req_001",
  "message": "请帮我完善安全性相关的需求",
  "currentContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
  "context": {
    "quickTopic": "security"
  }
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.messageId | string | 消息ID |
| data.role | string | 角色：`assistant` |
| data.content | string | AI回复的文本内容 |
| data.type | string | 消息类型：`proposal`（建议）/ `discussion`（讨论）/ `clarification`（澄清） |
| data.proposal | object | 建议详情（type=proposal 时有值） |
| data.proposal.pendingContent | string | 建议修改后的完整文档内容（预览用） |
| data.proposal.changeSummary | string | 变更摘要描述 |
| data.createdAt | string | 消息创建时间 |

**响应示例（建议类型）**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "messageId": "msg_005",
    "role": "assistant",
    "content": "我建议在非功能需求中增加以下安全性要求：\n\n- 密码加密存储（bcrypt）\n- 登录失败锁定机制\n- 敏感操作日志审计\n- 数据传输使用 HTTPS\n\n这些是否符合您的实际业务场景？如果有不需要的可以告诉我。",
    "type": "proposal",
    "proposal": {
      "pendingContent": "# 用户登录系统需求规格说明书\n\n...\n\n## 5. 安全性需求\n- 密码加密存储（bcrypt）\n- 登录失败锁定机制\n- 敏感操作日志审计\n- 数据传输使用 HTTPS",
      "changeSummary": "新增「安全性需求」章节，包含4条安全要求"
    },
    "createdAt": "2026-05-11T10:15:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例（讨论类型）**

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "messageId": "msg_006",
    "role": "assistant",
    "content": "好的，我理解您的需求。让我分析一下当前文档，看看哪些地方可以优化。您能具体说说希望调整的方向吗？比如安全性、性能、异常处理等方面？",
    "type": "discussion",
    "proposal": null,
    "createdAt": "2026-05-11T10:16:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 6.2 获取调整对话历史

获取指定需求的AI文档调整对话历史记录。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/chat/{requirementId}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.messages | array | 对话消息列表 |
| data.messages[].messageId | string | 消息ID |
| data.messages[].role | string | 角色：`user` / `assistant` |
| data.messages[].content | string | 消息内容 |
| data.messages[].type | string | 消息类型（仅 assistant） |
| data.messages[].proposal | object | 建议详情（仅 proposal 类型） |
| data.messages[].confirmed | boolean | 用户是否已采纳（仅 proposal 类型） |
| data.messages[].rejected | boolean | 用户是否已拒绝（仅 proposal 类型） |
| data.messages[].createdAt | string | 消息时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "messages": [
      {
        "messageId": "msg_001",
        "role": "user",
        "content": "请帮我完善安全性相关的需求",
        "createdAt": "2026-05-11T10:14:00.000Z"
      },
      {
        "messageId": "msg_002",
        "role": "assistant",
        "content": "我建议在非功能需求中增加以下安全性要求...",
        "type": "proposal",
        "proposal": {
          "pendingContent": "# 用户登录系统需求规格说明书\n\n...",
          "changeSummary": "新增「安全性需求」章节"
        },
        "confirmed": true,
        "rejected": false,
        "createdAt": "2026-05-11T10:15:00.000Z"
      }
    ]
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 6.3 采纳AI建议

用户确认采纳AI的建议，将建议内容应用到标准化文档，并生成新版本。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/chat/{messageId}/confirm` |
| Method | `POST` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| messageId | string | 是 | AI建议消息ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.requirementId | string | 需求ID |
| data.newContent | string | 采纳后的最新文档内容 |
| data.newVersionId | string | 新生成的版本ID |
| data.newVersionNumber | number | 新版本号 |
| data.changeSummary | string | 变更摘要 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "已采纳AI建议",
  "data": {
    "requirementId": "req_001",
    "newContent": "# 用户登录系统需求规格说明书\n\n...\n\n## 5. 安全性需求\n- 密码加密存储（bcrypt）\n...",
    "newVersionId": "ver_002",
    "newVersionNumber": 2,
    "changeSummary": "新增「安全性需求」章节，包含4条安全要求"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 6.4 拒绝AI建议

用户拒绝AI的建议，不修改文档。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/chat/{messageId}/reject` |
| Method | `POST` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| messageId | string | 是 | AI建议消息ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "已拒绝AI建议",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 7. 版本管理

### 7.1 获取版本列表

获取指定需求标准化文档的所有历史版本。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/versions/{requirementId}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.versions | array | 版本列表，按版本号倒序 |
| data.versions[].versionId | string | 版本ID |
| data.versions[].versionNumber | number | 版本号 |
| data.versions[].description | string | 版本描述（如"初始版本"、"采纳AI建议"、"恢复自版本2"） |
| data.versions[].createdAt | string | 版本创建时间 |
| data.currentVersionId | string | 当前生效版本ID |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "versions": [
      {
        "versionId": "ver_003",
        "versionNumber": 3,
        "description": "采纳AI建议：新增异常场景处理",
        "createdAt": "2026-05-11T10:30:00.000Z"
      },
      {
        "versionId": "ver_002",
        "versionNumber": 2,
        "description": "采纳AI建议：新增安全性需求",
        "createdAt": "2026-05-11T10:15:00.000Z"
      },
      {
        "versionId": "ver_001",
        "versionNumber": 1,
        "description": "初始版本",
        "createdAt": "2026-05-11T10:00:05.000Z"
      }
    ],
    "currentVersionId": "ver_003"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 7.2 获取版本详情

获取指定版本的完整文档内容。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/versions/{requirementId}/{versionId}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| versionId | string | 是 | 版本ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.versionId | string | 版本ID |
| data.versionNumber | number | 版本号 |
| data.content | string | 该版本的完整文档内容 |
| data.description | string | 版本描述 |
| data.createdAt | string | 创建时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "versionId": "ver_002",
    "versionNumber": 2,
    "content": "# 用户登录系统需求规格说明书\n\n...\n\n## 5. 安全性需求\n- 密码加密存储（bcrypt）\n...",
    "description": "采纳AI建议：新增安全性需求",
    "createdAt": "2026-05-11T10:15:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 7.3 恢复版本

将指定历史版本恢复为当前生效版本，同时生成一条新的版本记录（标记为恢复操作）。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/versions/{requirementId}/{versionId}/restore` |
| Method | `POST` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| versionId | string | 是 | 要恢复的版本ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.newVersionId | string | 恢复操作生成的新版本ID |
| data.newVersionNumber | number | 新版本号 |
| data.content | string | 恢复后的文档内容 |
| data.description | string | 版本描述（如"恢复自版本 2"） |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "版本恢复成功",
  "data": {
    "newVersionId": "ver_004",
    "newVersionNumber": 4,
    "content": "# 用户登录系统需求规格说明书\n\n...",
    "description": "恢复自版本 2"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 7.4 获取版本差异

获取两个版本之间的文档差异（逐行对比）。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/versions/{requirementId}/diff` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**请求参数（Query）**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fromVersionId | string | 是 | 对比基准版本ID |
| toVersionId | string | 是 | 对比目标版本ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.fromVersionId | string | 基准版本ID |
| data.toVersionId | string | 目标版本ID |
| data.diffLines | array | 逐行差异列表 |
| data.diffLines[].lineNumber | number | 行号 |
| data.diffLines[].text | string | 行文本内容 |
| data.diffLines[].type | string | 差异类型：`unchanged`（无变化）/ `added`（新增）/ `modified`（修改）/ `removed`（删除） |
| data.summary | object | 差异统计 |
| data.summary.addedCount | number | 新增行数 |
| data.summary.modifiedCount | number | 修改行数 |
| data.summary.removedCount | number | 删除行数 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "fromVersionId": "ver_001",
    "toVersionId": "ver_002",
    "diffLines": [
      { "lineNumber": 1, "text": "# 用户登录系统需求规格说明书", "type": "unchanged" },
      { "lineNumber": 2, "text": "", "type": "unchanged" },
      { "lineNumber": 45, "text": "## 5. 安全性需求", "type": "added" },
      { "lineNumber": 46, "text": "- 密码加密存储（bcrypt）", "type": "added" },
      { "lineNumber": 47, "text": "- 登录失败锁定机制", "type": "added" },
      { "lineNumber": 48, "text": "- 敏感操作日志审计", "type": "added" },
      { "lineNumber": 49, "text": "- 数据传输使用 HTTPS", "type": "added" }
    ],
    "summary": {
      "addedCount": 5,
      "modifiedCount": 0,
      "removedCount": 0
    }
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 8. 质量评分

### 8.1 执行质量评分

对标准化文档进行三维度质量评估（完整性、清晰度、一致性）。评分标准根据所选模板类型动态调整。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/standardize/quality` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| content | string | 是 | 待评分的标准化文档内容（Markdown） |
| templateId | string | 否 | 需求文档模板ID（用于模板特定的评分标准），不传则默认 `srs` |

**请求示例**

```json
{
  "requirementId": "req_001",
  "content": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
  "templateId": "srs"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.overall | number | 综合评分（0-100） |
| data.level | string | 评分等级：`good`（≥80）/ `medium`（60-79）/ `poor`（<60）/ `empty`（文档为空） |
| data.completeness | object | 完整性维度（权重 45%） |
| data.completeness.score | number | 完整性得分 |
| data.completeness.details | array | 各章节检查详情 |
| data.completeness.details[].section | string | 章节名称 |
| data.completeness.details[].ok | boolean | 是否通过 |
| data.completeness.details[].suggestion | string | 改进建议（未通过时有值） |
| data.clarity | object | 清晰度维度（权重 35%） |
| data.clarity.score | number | 清晰度得分 |
| data.clarity.issues | array | 清晰度问题列表 |
| data.consistency | object | 一致性维度（权重 20%） |
| data.consistency.score | number | 一致性得分 |
| data.consistency.issues | array | 一致性问题列表 |
| data.suggestions | array | 综合改进建议列表（最多5条） |

**评分维度说明**

| 维度 | 权重 | SRS模板检测内容 | 用户故事模板检测内容 |
|------|------|-----------------|---------------------|
| 完整性 | 45% | 检查6个必填章节（引言、需求概述、功能需求、非功能需求、约束条件、异常场景）是否有实质内容 | 检查5个必填章节（需求概述、用户角色、用户故事、业务规则、数据需求）是否有实质内容 |
| 清晰度 | 35% | 检测模糊词汇、量化指标、示例 | 检测模糊词汇、验收标准可测性、用户故事格式规范性 |
| 一致性 | 20% | 检测术语混用、矛盾描述 | 检测术语混用、用户故事与验收标准一致性 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "评分完成",
  "data": {
    "overall": 72,
    "level": "medium",
    "completeness": {
      "score": 65,
      "details": [
        { "section": "引言", "ok": true },
        { "section": "需求概述", "ok": true },
        { "section": "功能需求", "ok": true },
        { "section": "非功能需求", "ok": true },
        { "section": "约束条件", "ok": false, "suggestion": "「约束条件」章节内容为空或仅有占位提示，建议补充具体内容" },
        { "section": "异常场景处理", "ok": false, "suggestion": "「异常场景处理」章节内容为空或仅有占位提示，建议补充具体内容" }
      ]
    },
    "clarity": {
      "score": 80,
      "issues": [
        "未发现明确的量化指标，建议补充具体的性能、容量等数值指标"
      ]
    },
    "consistency": {
      "score": 90,
      "issues": []
    },
    "suggestions": [
      "「约束条件」章节内容为空或仅有占位提示，建议补充具体内容",
      "「异常场景处理」章节内容为空或仅有占位提示，建议补充具体内容",
      "未发现明确的量化指标，建议补充具体的性能、容量等数值指标"
    ]
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 9. 需求拆分

### 9.1 执行需求拆分

调用AI将标准化文档拆分为单个需求项。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/split` |
| Method | `POST` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| standardizedContent | string | 是 | 标准化文档内容（用于AI分析拆分） |

**请求示例**

```json
{
  "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n..."
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.requirementId | string | 需求ID |
| data.splits | array | 拆分结果列表 |
| data.splits[].id | string | 拆分项ID |
| data.splits[].content | string | 拆分项内容 |
| data.splits[].order | number | 排序序号 |
| data.totalCount | number | 拆分总数 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "拆分完成",
  "data": {
    "requirementId": "req_001",
    "splits": [
      { "id": "split_001", "content": "实现用户名密码登录功能", "order": 1 },
      { "id": "split_002", "content": "实现密码复杂度校验", "order": 2 },
      { "id": "split_003", "content": "实现登录失败锁定机制", "order": 3 }
    ],
    "totalCount": 3
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 9.2 获取拆分结果列表

获取指定需求的拆分结果列表。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/splits` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.splits | array | 拆分结果列表 |
| data.splits[].id | string | 拆分项ID |
| data.splits[].content | string | 拆分项内容 |
| data.splits[].order | number | 排序序号 |
| data.splits[].createdAt | string | 创建时间 |
| data.splits[].updatedAt | string | 更新时间 |
| data.totalCount | number | 总数 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "splits": [
      { "id": "split_001", "content": "实现用户名密码登录功能", "order": 1, "createdAt": "2026-05-11T10:35:00.000Z", "updatedAt": "2026-05-11T10:35:00.000Z" },
      { "id": "split_002", "content": "实现密码复杂度校验", "order": 2, "createdAt": "2026-05-11T10:35:00.000Z", "updatedAt": "2026-05-11T10:35:00.000Z" },
      { "id": "split_003", "content": "实现登录失败锁定机制", "order": 3, "createdAt": "2026-05-11T10:35:00.000Z", "updatedAt": "2026-05-11T10:35:00.000Z" }
    ],
    "totalCount": 3
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 9.3 更新拆分项

编辑单个拆分项的内容。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/splits/{splitId}` |
| Method | `PUT` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |
| splitId | string | 是 | 拆分项ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 拆分项内容 |
| order | number | 否 | 排序序号 |

**请求示例**

```json
{
  "content": "实现用户名密码登录功能（含记住密码）"
}
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "split_001",
    "content": "实现用户名密码登录功能（含记住密码）",
    "order": 1,
    "updatedAt": "2026-05-11T11:00:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 9.4 删除拆分项

删除指定的拆分项。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/splits/{splitId}` |
| Method | `DELETE` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |
| splitId | string | 是 | 拆分项ID |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "删除成功",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 9.5 手动添加拆分项

用户手动添加一条新的拆分需求。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/splits` |
| Method | `POST` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 拆分项内容 |
| order | number | 否 | 排序序号（不传则默认插入到列表最上方，order=1，其余项序号顺延） |

**请求示例**

```json
{
  "content": "实现登录日志记录功能"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 新拆分项ID |
| data.content | string | 拆分项内容 |
| data.order | number | 排序序号 |
| data.createdAt | string | 创建时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": "split_004",
    "content": "实现登录日志记录功能",
    "order": 4,
    "createdAt": "2026-05-11T11:05:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 9.6 确认并进入测试设计

确认拆分后的需求，保存到测试设计模块并生成对应的脑图数据结构，前端随后跳转到测试设计页面。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/confirm-and-test` |
| Method | `POST` |
| Content-Type | `application/json` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 是 | 需求标题 |
| splitRequirements | array | 是 | 拆分后的需求列表 |
| splitRequirements[].content | string | 是 | 拆分项内容 |
| splitRequirements[].selected | boolean | 否 | 是否选中，默认 true |
| standardizedContent | string | 否 | 标准化文档内容（Markdown） |
| templateId | string | 否 | 需求文档模板ID |

**请求示例**

```json
{
  "title": "用户登录系统需求",
  "splitRequirements": [
    { "content": "实现用户名密码登录功能", "selected": true },
    { "content": "实现密码复杂度校验", "selected": true },
    { "content": "实现登录失败锁定机制", "selected": true }
  ],
  "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
  "templateId": "user-story"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 测试设计模块中的需求ID |
| data.title | string | 需求标题 |
| data.status | string | 状态：`confirmed`（待生成） |
| data.mindMapData | object | 生成的脑图数据结构 |
| data.mindMapData.data | object | 根节点（`_level: root`），文本为需求标题 |
| data.mindMapData.children | array | 二级需求节点列表（`_level: requirement`），每条拆分需求对应一个节点 |
| data.mindMapData.children[].data.text | string | 需求节点文本 |
| data.mindMapData.children[].data._level | string | 固定为 `requirement` |
| data.mindMapData.children[].data._status | string | 固定为 `confirmed` |
| data.mindMapData.children[].children | array | 子节点（空数组，后续在测试设计中添加测试点和用例） |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "req-1716000000000",
    "title": "用户登录系统需求",
    "status": "confirmed",
    "statusText": "待生成",
    "date": "2026-05-21 10:30",
    "testPointCount": 0,
    "caseCount": 0,
    "source": "standardization",
    "mindMapData": {
      "data": {
        "text": "用户登录系统需求",
        "note": "",
        "expand": true,
        "_level": "root",
        "_status": "confirmed"
      },
      "children": [
        {
          "data": {
            "text": "实现用户名密码登录功能",
            "note": "",
            "expand": true,
            "_level": "requirement",
            "_status": "confirmed"
          },
          "children": []
        },
        {
          "data": {
            "text": "实现密码复杂度校验",
            "note": "",
            "expand": true,
            "_level": "requirement",
            "_status": "confirmed"
          },
          "children": []
        },
        {
          "data": {
            "text": "实现登录失败锁定机制",
            "note": "",
            "expand": true,
            "_level": "requirement",
            "_status": "confirmed"
          },
          "children": []
        }
      ]
    }
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**说明**：
- 该接口将需求从标准化模块保存到测试设计模块，同时生成脑图数据结构
- 脑图结构为两级：根节点（需求标题）→ 二级需求节点（拆分后的各条需求）
- 二级需求节点的 `children` 为空数组，后续在测试设计模块中通过 AI 生成或手动添加测试点和用例
- 前端调用成功后，使用 `router.push({ path: '/test-design', query: { requirementId: data.id } })` 跳转到测试设计页面并自动选中该需求

---

## 10. 文档导出

### 10.1 导出标准化文档

将标准化文档导出为指定格式的文件。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/requirements/{id}/export` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**请求参数（Query）**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| format | string | 是 | 导出格式：`markdown` / `docx` |

**响应说明**

| 格式 | Content-Type | 说明 |
|------|-------------|------|
| markdown | `text/markdown; charset=utf-8` | 直接返回 Markdown 文本内容 |
| docx | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | 返回二进制文件流 |

**响应头**

```
Content-Disposition: attachment; filename="需求规格说明书_2026-05-11.md"
```

或

```
Content-Disposition: attachment; filename="需求规格说明书_2026-05-11.docx"
```

**DOCX 导出样式规范**

| Markdown 语法 | DOCX 样式 |
|---------------|-----------|
| `# 标题` | Heading 1（36pt 加粗，段前360twips，段后120twips） |
| `## 标题` | Heading 2（28pt 加粗，段前280twips，段后120twips） |
| `### 标题` | Heading 3（24pt 加粗，段前240twips，段后120twips） |
| `> 引用` | 斜体灰色（#666666），左缩进720twips |
| 空行 | 段落间距80twips |
| 普通文本 | 22pt 正文，段前段后60twips |

---

## 11. 知识库上传

### 11.1 上传文档至知识库

将当前版本的标准化文档一键上传至知识库，供后续测试用例生成等模块引用。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/knowledge-base/upload-doc` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| title | string | 是 | 文档标题 |
| content | string | 是 | 标准化文档内容（Markdown格式） |
| templateId | string | 否 | 需求文档模板ID |
| tags | array | 否 | 文档标签列表 |

**请求示例**

```json
{
  "requirementId": "req_001",
  "title": "用户登录系统需求规格说明书",
  "content": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
  "templateId": "srs",
  "tags": ["登录", "认证", "安全"]
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.docId | string | 知识库文档ID |
| data.title | string | 文档标题 |
| data.status | string | 上传状态：`success` / `processing` |
| data.uploadedAt | string | 上传时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "上传成功",
  "data": {
    "docId": "kb_doc_001",
    "title": "用户登录系统需求规格说明书",
    "status": "success",
    "uploadedAt": "2026-05-11T11:30:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 12. 历史记录

### 12.1 获取历史记录列表

获取当前用户的需求历史记录列表（左侧边栏展示）。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/history` |
| Method | `GET` |

**请求参数（Query）**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| pageNo | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页条数，默认 20 |
| keyword | string | 否 | 搜索关键词，匹配标题 |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.items | array | 历史记录列表 |
| data.items[].id | string | 需求ID |
| data.items[].title | string | 需求标题 |
| data.items[].status | string | 状态 |
| data.items[].updatedAt | string | 最后更新时间 |
| data.pageNo | number | 当前页码 |
| data.pageSize | number | 每页条数 |
| data.total | number | 总条数 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      { "id": "req_001", "title": "用户登录系统需求", "status": "splitted", "updatedAt": "2026-05-10T15:00:00.000Z" },
      { "id": "req_002", "title": "数据导出功能需求", "status": "standardized", "updatedAt": "2026-05-09T10:30:00.000Z" },
      { "id": "req_003", "title": "权限管理系统需求", "status": "draft", "updatedAt": "2026-05-08T16:45:00.000Z" }
    ],
    "pageNo": 1,
    "pageSize": 20,
    "total": 3
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 12.2 获取历史记录详情

获取某条历史记录的完整数据，用于加载到当前工作区。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/history/{id}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 需求ID |
| data.title | string | 需求标题 |
| data.inputMode | string | 输入模式 |
| data.rawContent | string | 原始需求内容 |
| data.fileInfo | object | 上传文件信息 |
| data.standardizedContent | string | 标准化文档内容 |
| data.splitRequirements | array | 拆分需求列表 |
| data.testPoints | array | 测试点列表（后续模块数据） |
| data.testCases | array | 测试用例列表（后续模块数据） |
| data.status | string | 状态 |
| data.createdAt | string | 创建时间 |
| data.updatedAt | string | 更新时间 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": "req_001",
    "title": "用户登录系统需求",
    "inputMode": "text",
    "rawContent": "实现用户登录功能，支持用户名密码验证，登录成功后跳转到首页。",
    "fileInfo": null,
    "standardizedContent": "# 用户登录系统需求规格说明书\n\n## 1. 引言\n...",
    "splitRequirements": [
      { "id": "split_001", "content": "实现用户名密码登录功能", "order": 1 },
      { "id": "split_002", "content": "实现密码复杂度校验", "order": 2 },
      { "id": "split_003", "content": "实现登录失败锁定机制", "order": 3 }
    ],
    "testPoints": [],
    "testCases": [],
    "status": "splitted",
    "createdAt": "2026-05-10T14:30:00.000Z",
    "updatedAt": "2026-05-10T15:00:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 13. 错误码说明

### 通用错误码

| 状态码 | code | 说明 |
|--------|------|------|
| 400 | 400 | 请求参数错误 |
| 401 | 401 | 未登录或 Token 过期 |
| 403 | 403 | 无权限访问该资源 |
| 404 | 404 | 资源不存在 |
| 413 | 413 | 上传文件大小超过限制 |
| 415 | 415 | 不支持的文件格式 |
| 429 | 429 | 请求过于频繁 |
| 500 | 500 | 服务器内部错误 |
| 502 | 502 | AI 服务调用失败 |
| 503 | 503 | AI 服务暂时不可用 |

### 业务错误码

| code | 说明 |
|------|------|
| 10001 | 需求不存在 |
| 10002 | 需求状态不允许此操作 |
| 10003 | 标准化文档内容为空 |
| 10004 | AI 标准化处理失败 |
| 10005 | AI 对话生成失败 |
| 10006 | 版本不存在 |
| 10007 | 版本恢复失败 |
| 10008 | 质量评分为空（文档无内容） |
| 10009 | 需求拆分失败 |
| 10010 | 拆分项不存在 |
| 10011 | 导出格式不支持 |
| 10012 | 文件上传失败 |
| 10013 | 文件解析失败 |
| 10014 | 模板不存在 |
| 10015 | 模板推荐失败 |
| 10016 | 探索会话不存在 |
| 10017 | 探索会话已结束 |
| 10018 | AI需求探索处理失败 |
| 10019 | 知识库上传失败 |
| 10020 | 文档已在知识库中（重复上传） |

### 错误响应示例

```json
{
  "success": false,
  "code": 10001,
  "message": "需求不存在",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 附录：接口汇总表

| 序号 | 接口 | 方法 | URL | 说明 |
|------|------|------|-----|------|
| 1 | 创建需求 | POST | `/api/v1/requirements` | 录入新需求（含模板选择） |
| 2 | 需求列表 | GET | `/api/v1/requirements` | 获取需求列表 |
| 3 | 需求详情 | GET | `/api/v1/requirements/{id}` | 获取需求完整信息（含探索数据） |
| 4 | 更新需求 | PUT | `/api/v1/requirements/{id}` | 更新需求信息 |
| 5 | 删除需求 | DELETE | `/api/v1/requirements/{id}` | 删除需求及关联数据 |
| 6 | 上传文档 | POST | `/api/v1/upload` | 上传需求文档文件 |
| 7 | 模板列表 | GET | `/api/v1/templates` | 获取系统预设模板列表 |
| 8 | 模板详情 | GET | `/api/v1/templates/{id}` | 获取模板维度和章节结构 |
| 9 | AI推荐模板 | POST | `/api/v1/templates/recommend` | AI分析推荐合适模板 |
| 10 | 启动需求探索 | POST | `/api/v1/explore/start` | 启动AI需求探索会话 |
| 11 | 发送探索消息 | POST | `/api/v1/explore/chat` | 探索阶段用户回复AI提问 |
| 12 | 探索对话历史 | GET | `/api/v1/explore/chat/{requirementId}` | 获取探索对话记录 |
| 13 | 探索状态 | GET | `/api/v1/explore/status` | 获取探索实时状态 |
| 14 | 执行标准化 | POST | `/api/v1/standardize` | AI生成标准文档（含探索数据） |
| 15 | 获取标准化结果 | GET | `/api/v1/standardize/{requirementId}` | 获取当前标准化文档 |
| 16 | 发送调整消息 | POST | `/api/v1/standardize/chat` | AI文档调整对话 |
| 17 | 获取调整历史 | GET | `/api/v1/standardize/chat/{requirementId}` | 获取调整对话记录 |
| 18 | 采纳AI建议 | POST | `/api/v1/standardize/chat/{messageId}/confirm` | 确认采纳建议 |
| 19 | 拒绝AI建议 | POST | `/api/v1/standardize/chat/{messageId}/reject` | 拒绝AI建议 |
| 20 | 版本列表 | GET | `/api/v1/standardize/versions/{requirementId}` | 获取所有版本 |
| 21 | 版本详情 | GET | `/api/v1/standardize/versions/{requirementId}/{versionId}` | 获取版本内容 |
| 22 | 恢复版本 | POST | `/api/v1/standardize/versions/{requirementId}/{versionId}/restore` | 恢复历史版本 |
| 23 | 版本差异 | GET | `/api/v1/standardize/versions/{requirementId}/diff` | 获取版本间差异 |
| 24 | 质量评分 | POST | `/api/v1/standardize/quality` | 文档质量评估（模板感知） |
| 25 | 执行拆分 | POST | `/api/v1/requirements/{id}/split` | AI拆分需求 |
| 26 | 拆分列表 | GET | `/api/v1/requirements/{id}/splits` | 获取拆分结果 |
| 27 | 更新拆分项 | PUT | `/api/v1/requirements/{id}/splits/{splitId}` | 编辑拆分项 |
| 28 | 删除拆分项 | DELETE | `/api/v1/requirements/{id}/splits/{splitId}` | 删除拆分项 |
| 29 | 添加拆分项 | POST | `/api/v1/requirements/{id}/splits` | 手动添加拆分项（默认插入到最上方） |
| 30 | 确认并进入测试设计 | POST | `/api/v1/requirements/{id}/confirm-and-test` | 保存需求+生成脑图+跳转测试设计 |
| 31 | 导出文档 | GET | `/api/v1/requirements/{id}/export` | 导出Markdown/DOCX |
| 32 | 上传至知识库 | POST | `/api/v1/knowledge-base/upload-doc` | 文档上传至知识库 |
| 33 | 历史列表 | GET | `/api/v1/history` | 获取历史记录列表 |
| 34 | 历史详情 | GET | `/api/v1/history/{id}` | 获取历史记录详情 |

---

**文档版本**：v2.1
**创建日期**：2026-05-11
**更新日期**：2026-05-21
**适用范围**：需求标准化模块 - 后端开发接口参考