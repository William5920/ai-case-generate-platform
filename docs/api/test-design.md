# 测试设计模块接口文档

## 概述

本文档描述智能测试用例平台「测试设计」模块的接口规范，涵盖需求列表查询、脑图数据获取、测试点管理、测试用例管理、AI调整、异步任务管理、导出等全部功能。

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

- [1. 需求列表](#1-需求列表)
  - [1.1 获取需求列表](#11-获取需求列表)
  - [1.2 搜索需求](#12-搜索需求)
  - [1.3 从标准化模块导入需求](#13-从标准化模块导入需求)
- [2. 脑图数据](#2-脑图数据)
  - [2.1 获取脑图数据](#21-获取脑图数据)
- [3. 测试点管理](#3-测试点管理)
  - [3.1 添加测试点](#31-添加测试点)
  - [3.2 编辑测试点](#32-编辑测试点)
  - [3.3 删除测试点](#33-删除测试点)
  - [3.4 批量删除测试点](#34-批量删除测试点)
  - [3.5 标记保留测试点](#35-标记保留测试点)
- [4. 测试用例管理](#4-测试用例管理)
  - [4.1 添加测试用例](#41-添加测试用例)
  - [4.2 编辑测试用例](#42-编辑测试用例)
  - [4.3 删除测试用例](#43-删除测试用例)
  - [4.4 批量删除测试用例](#44-批量删除测试用例)
  - [4.5 标记保留测试用例](#45-标记保留测试用例)
- [5. AI调整](#5-ai调整)
  - [5.1 发起AI调整对话](#51-发起ai调整对话)
  - [5.2 发送对话消息](#52-发送对话消息)
  - [5.3 获取对话历史](#53-获取对话历史)
- [6. 异步任务管理](#6-异步任务管理)
  - [6.1 快速生成](#61-快速生成)
  - [6.2 获取任务状态](#62-获取任务状态)
  - [6.3 取消任务](#63-取消任务)
  - [6.4 根据需求ID获取活跃任务](#64-根据需求id获取活跃任务)
- [7. 导出](#7-导出)
  - [7.1 导出Excel](#71-导出excel)
- [8. 错误码说明](#8-错误码说明)

---

## 1. 需求列表

### 1.1 获取需求列表

获取当前用户所有已拆分的需求列表，用于测试设计模块左侧面板展示。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements` |
| Method | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 20 |
| status | string | 否 | 状态筛选：`confirmed`（待生成）/ `generating`（生成中）/ `completed`（已完成） |
| keyword | string | 否 | 搜索关键词，匹配需求标题 |

**请求示例**

```
GET /api/v1/test-design/requirements?page=1&pageSize=20&keyword=登录
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.list | array | 需求列表 |
| data.list[].id | string | 需求ID |
| data.list[].title | string | 需求标题 |
| data.list[].status | string | 状态：`confirmed` / `generating` / `completed` |
| data.list[].statusText | string | 状态中文描述 |
| data.list[].date | string | 创建/更新时间 |
| data.list[].testPointCount | integer | 测试点数量 |
| data.list[].caseCount | integer | 测试用例数量 |
| data.list[].source | string | 来源：`standardization`（标准化模块） |
| data.total | integer | 总条数 |
| data.page | integer | 当前页码 |
| data.pageSize | integer | 每页条数 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [
      {
        "id": "req-1",
        "title": "用户登录系统需求",
        "status": "completed",
        "statusText": "已完成",
        "date": "2026-05-12 14:30",
        "testPointCount": 3,
        "caseCount": 5,
        "source": "standardization"
      },
      {
        "id": "req-2",
        "title": "数据导出功能需求",
        "status": "generating",
        "statusText": "生成中",
        "date": "2026-05-12 10:15",
        "testPointCount": 2,
        "caseCount": 3,
        "source": "standardization"
      }
    ],
    "total": 2,
    "page": 1,
    "pageSize": 20
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 1.2 搜索需求

搜索需求与获取需求列表共用同一接口，通过 `keyword` 参数实现搜索功能。

---

### 1.3 从标准化模块导入需求

从需求标准化模块确认拆分需求后，将需求数据导入到测试设计模块，同时生成对应的脑图数据结构（根节点 + 拆分后的二级需求节点）。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements` |
| Method | `POST` |
| Content-Type | `application/json` |

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
| data.id | string | 需求ID |
| data.title | string | 需求标题 |
| data.status | string | 状态：`confirmed`（待生成） |
| data.statusText | string | 状态中文描述 |
| data.date | string | 创建时间 |
| data.testPointCount | integer | 测试点数量（初始为0） |
| data.caseCount | integer | 测试用例数量（初始为0） |
| data.source | string | 来源：`standardization` |

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
    "source": "standardization"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**说明**：
- 该接口在需求标准化模块点击「确认并进入测试设计」时调用
- 后端需同时创建对应的脑图数据，结构为：根节点（需求标题，`_level: root`）→ 二级需求节点（拆分后的各条需求，`_level: requirement`），二级需求节点的 `children` 为空数组
- 前端调用成功后，使用 `router.push({ path: '/test-design', query: { requirementId: data.id } })` 跳转到测试设计页面并自动选中该需求

---

## 2. 脑图数据

### 2.1 获取脑图数据

根据需求ID获取完整的脑图数据结构（4级：根节点 → 需求 → 测试点 → 测试用例）。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements/{requirementId}/mindmap` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object | 脑图数据对象，结构同 simple-mind-map 数据格式 |
| data.data | object | 根节点数据 |
| data.data.text | string | 根节点文本 |
| data.data._level | string | 节点层级：`root` |
| data.data._status | string | 状态 |
| data.children | array | 子节点（需求节点） |
| data.children[].data | object | 需求节点数据 |
| data.children[].data.text | string | 需求文本 |
| data.children[].data._level | string | 节点层级：`requirement` |
| data.children[].data._status | string | 状态 |
| data.children[].children | array | 子节点（测试点节点） |
| data.children[].children[].data | object | 测试点节点数据 |
| data.children[].children[].data.text | string | 测试点文本 |
| data.children[].children[].data._level | string | 节点层级：`testPoint` |
| data.children[].children[].data._source | string | 来源：`AI` / `人工` |
| data.children[].children[].data._marked | boolean | 是否标记保留 |
| data.children[].children[].data.description | string | 测试点描述 |
| data.children[].children[].children | array | 子节点（测试用例节点） |
| data.children[].children[].children[].data | object | 测试用例节点数据 |
| data.children[].children[].children[].data.text | string | 用例名称 |
| data.children[].children[].children[].data._caseProperty | string | 用例属性：`正例` / `反例` |
| data.children[].children[].children[].data._source | string | 来源：`AI` / `人工` |
| data.children[].children[].children[].data._marked | boolean | 是否标记保留 |
| data.children[].children[].children[].data._preCondition | string | 前置条件 |
| data.children[].children[].children[].data.steps | array | 测试步骤列表 |
| data.children[].children[].children[].data.steps[].name | string | 步骤名称 |
| data.children[].children[].children[].data.steps[].description | string | 步骤描述 |
| data.children[].children[].children[].data.steps[].stepExpectedResult | string | 步骤预期结果 |
| data.children[].children[].children[].data.note | string | 用例详情（HTML格式） |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "data": {
      "text": "用户登录系统需求",
      "expand": true,
      "_level": "root",
      "_status": "completed"
    },
    "children": [
      {
        "data": {
          "text": "实现用户登录功能，支持用户名密码验证",
          "expand": true,
          "_level": "requirement",
          "_status": "completed"
        },
        "children": [
          {
            "data": {
              "text": "用户名输入验证",
              "expand": true,
              "_level": "testPoint",
              "_status": "completed",
              "_source": "AI",
              "_marked": false
            },
            "children": [
              {
                "data": {
                  "text": "用户正常登录系统",
                  "note": "<div class=\"case-note-popover\">...</div>",
                  "expand": true,
                  "_level": "testCase",
                  "_caseProperty": "正例",
                  "_source": "AI"
                },
                "children": []
              }
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

## 3. 测试点管理

### 3.1 添加测试点

在指定需求节点下手动添加测试点。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements/{requirementId}/test-points` |
| Method | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementNodeId | string | 是 | 需求节点ID |
| text | string | 是 | 测试点文本内容 |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 测试点ID |
| data.text | string | 测试点文本 |
| data._source | string | 来源：`人工` |

### 3.2 编辑测试点

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-points/{testPointId}` |
| Method | `PUT` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| text | string | 是 | 测试点文本内容 |

### 3.3 删除测试点

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-points/{testPointId}` |
| Method | `DELETE` |

### 3.4 批量删除测试点

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-points/batch-delete` |
| Method | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ids | string[] | 是 | 测试点ID列表 |

### 3.5 标记保留测试点

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-points/{testPointId}/mark` |
| Method | `PUT` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marked | boolean | 是 | 是否标记保留 |

---

## 4. 测试用例管理

### 4.1 添加测试用例

在指定测试点下手动添加测试用例。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-points/{testPointId}/test-cases` |
| Method | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| text | string | 是 | 用例名称 |
| caseProperty | string | 是 | 用例属性：`正例` / `反例` |
| preCondition | string | 否 | 前置条件 |
| steps | array | 否 | 测试步骤 |
| steps[].name | string | 是 | 步骤名称 |
| steps[].description | string | 是 | 步骤描述 |
| steps[].stepExpectedResult | string | 是 | 步骤预期结果 |

### 4.2 编辑测试用例

编辑指定测试用例的名称、属性、前置条件和步骤信息。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-cases/{testCaseId}` |
| Method | `PUT` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| testCaseId | string | 是 | 测试用例ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| text | string | 是 | 用例名称，最长200字符 |
| caseProperty | string | 是 | 用例属性：`正例` / `反例` |
| preCondition | string | 否 | 前置条件 |
| steps | array | 否 | 测试步骤 |
| steps[].name | string | 是 | 步骤名称 |
| steps[].description | string | 是 | 步骤描述 |
| steps[].stepExpectedResult | string | 是 | 步骤预期结果 |

**请求示例**

```json
{
  "text": "用户正常登录系统-编辑后",
  "caseProperty": "正例",
  "preCondition": "用户已注册并拥有有效的账号和密码",
  "steps": [
    {
      "name": "输入用户名",
      "description": "在登录页输入正确的用户名",
      "stepExpectedResult": "用户名输入框显示输入的用户名"
    },
    {
      "name": "输入密码",
      "description": "在登录页输入正确的密码",
      "stepExpectedResult": "密码输入框显示输入的密码"
    },
    {
      "name": "点击登录按钮",
      "description": "点击登录按钮",
      "stepExpectedResult": "系统跳转至用户主页"
    }
  ]
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 测试用例ID |
| data.text | string | 用例名称 |
| data.caseProperty | string | 用例属性 |
| data.preCondition | string | 前置条件 |
| data.steps | array | 测试步骤 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "tc-1716000000000",
    "text": "用户正常登录系统-编辑后",
    "caseProperty": "正例",
    "preCondition": "用户已注册并拥有有效的账号和密码",
    "steps": [
      {
        "name": "输入用户名",
        "description": "在登录页输入正确的用户名",
        "stepExpectedResult": "用户名输入框显示输入的用户名"
      },
      {
        "name": "输入密码",
        "description": "在登录页输入正确的密码",
        "stepExpectedResult": "密码输入框显示输入的密码"
      },
      {
        "name": "点击登录按钮",
        "description": "点击登录按钮",
        "stepExpectedResult": "系统跳转至用户主页"
      }
    ]
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 4.3 删除测试用例

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-cases/{testCaseId}` |
| Method | `DELETE` |

### 4.4 批量删除测试用例

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-cases/batch-delete` |
| Method | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ids | string[] | 是 | 测试用例ID列表 |

### 4.5 标记保留测试用例

标记或取消标记测试用例为保留状态，在AI调整时标记保留的用例不会被替换或删除。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/test-cases/{testCaseId}/mark` |
| Method | `PUT` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| testCaseId | string | 是 | 测试用例ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marked | boolean | 是 | 是否标记保留 |

**请求示例**

```json
{
  "marked": true
}
```

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 5. AI调整

### 5.1 发起AI调整对话

对指定节点发起AI调整多轮对话。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/ai-adjust/sessions` |
| Method | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |
| nodeId | string | 是 | 节点ID |
| nodeType | string | 是 | 节点类型：`requirement`（需求级，调整测试点）/ `testPoint`（测试点级，调整测试用例） |
| markedNodeIds | string[] | 否 | 标记保留的节点ID列表。当 `nodeType=requirement` 时为标记的测试点ID；当 `nodeType=testPoint` 时为标记的测试用例ID |

**说明**

- 当 `nodeType=requirement` 时，AI调整的层级为：需求 → 测试点，标记保留的为测试点节点
- 当 `nodeType=testPoint` 时，AI调整的层级为：测试点 → 测试用例，标记保留的为测试用例节点

### 5.2 发送对话消息

向已创建的AI调整对话发送用户消息。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/ai-adjust/sessions/{sessionId}/messages` |
| Method | `POST` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | string | 是 | 对话ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 用户消息内容 |

**请求示例**

```json
{
  "content": "请补充异常场景的测试点"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.id | string | 消息ID |
| data.role | string | 角色：`user` / `assistant` |
| data.content | string | 消息内容 |
| data.type | string | 消息类型：`text` / `discussion` / `proposal`（调整建议） |
| data.changeSummary | string / null | 变更摘要描述，仅在 type=proposal 时有值 |
| data.pendingMindMapData | object / null | 待应用的调整后节点数据，仅包含当前调整节点及其直接子节点的两层完整数据，仅在 type=proposal 时有值。详见下方 `pendingMindMapData 数据结构` |
| data.timestamp | string | 消息时间戳（ISO 8601） |

**响应示例（普通讨论消息）**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "msg-1716000000000",
    "role": "assistant",
    "content": "好的，我理解你的需求。我会补充异常场景的测试点...",
    "type": "discussion",
    "changeSummary": null,
    "pendingMindMapData": null,
    "timestamp": "2026-05-28T10:30:00.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例（调整建议消息 - 需求级，调整测试点）**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "msg-1716000000001",
    "role": "assistant",
    "content": "已为您新增3个异常场景测试点：空密码、超长密码、SQL注入密码...",
    "type": "proposal",
    "changeSummary": "新增3个异常场景测试点",
    "pendingMindMapData": {
      "data": {
        "id": "sr-abc123",
        "text": "用户登录功能",
        "_level": "requirement",
        "_status": "completed"
      },
      "children": [
        {
          "data": {
            "id": "tp-001",
            "text": "正常登录流程验证",
            "_level": "testPoint",
            "_status": "completed",
            "_source": "AI",
            "_marked": false,
            "description": null
          },
          "children": []
        },
        {
          "data": {
            "id": "tp-002",
            "text": "密码格式校验",
            "_level": "testPoint",
            "_status": "completed",
            "_source": "AI",
            "_marked": true,
            "description": null
          },
          "children": []
        },
        {
          "data": {
            "text": "空密码登录验证",
            "_level": "testPoint",
            "_source": "AI",
            "_marked": false,
            "description": null
          },
          "children": []
        },
        {
          "data": {
            "text": "超长密码登录验证",
            "_level": "testPoint",
            "_source": "AI",
            "_marked": false,
            "description": null
          },
          "children": []
        },
        {
          "data": {
            "text": "SQL注入密码验证",
            "_level": "testPoint",
            "_source": "AI",
            "_marked": false,
            "description": null
          },
          "children": []
        }
      ]
    },
    "timestamp": "2026-05-28T10:30:01.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例（调整建议消息 - 测试点级，调整测试用例）**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "msg-1716000000002",
    "role": "assistant",
    "content": "已为该测试点补充2个异常场景测试用例...",
    "type": "proposal",
    "changeSummary": "补充2个异常场景测试用例",
    "pendingMindMapData": {
      "data": {
        "id": "tp-001",
        "text": "正常登录流程验证",
        "_level": "testPoint",
        "_status": "completed",
        "_source": "AI",
        "_marked": false,
        "description": null
      },
      "children": [
        {
          "data": {
            "id": "tc-001",
            "text": "使用正确账号密码登录",
            "_level": "testCase",
            "_caseProperty": "正例",
            "_source": "AI",
            "_marked": false,
            "note": "<div class='case-note-popover'>...</div>",
            "_preCondition": "系统正常运行",
            "steps": [{"name": "输入正确账号密码", "description": "输入已注册的账号和正确密码", "stepExpectedResult": "登录成功"}]
          },
          "children": []
        },
        {
          "data": {
            "text": "使用空密码登录",
            "_level": "testCase",
            "_caseProperty": "反例",
            "_source": "AI",
            "_marked": false,
            "_preCondition": "系统正常运行",
            "steps": [{"name": "输入账号后密码留空", "description": "输入已注册的账号，密码字段留空", "stepExpectedResult": "提示密码不能为空"}]
          },
          "children": []
        }
      ]
    },
    "timestamp": "2026-05-28T10:30:02.000Z"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**pendingMindMapData 数据结构**

该字段仅包含当前被调整节点及其直接子节点的两层完整数据，而非整个主脑图树。

**需求级（nodeType=requirement）**：返回二级需求节点及调整后的所有测试点

| 字段路径 | 类型 | 说明 |
|----------|------|------|
| data | object | 需求节点数据 |
| data.id | string | 需求节点ID |
| data.text | string | 需求文本 |
| data._level | string | 固定值 `"requirement"` |
| data._status | string | 节点状态 |
| children | array | 调整后的测试点列表 |
| children[].data | object | 测试点节点数据 |
| children[].data.id | string / undefined | 已有测试点有ID，AI新增测试点无ID |
| children[].data.text | string | 测试点文本 |
| children[].data._level | string | 固定值 `"testPoint"` |
| children[].data._source | string | 来源：`"AI"` / `"人工"` |
| children[].data._marked | boolean | 是否标记保留 |
| children[].data._status | string | 节点状态（已有测试点有此字段） |
| children[].data.description | string / null | 测试点描述 |
| children[].children | array | 固定为空数组 `[]` |

**测试点级（nodeType=testPoint）**：返回三级测试点节点及调整后的所有测试用例

| 字段路径 | 类型 | 说明 |
|----------|------|------|
| data | object | 测试点节点数据 |
| data.id | string | 测试点节点ID |
| data.text | string | 测试点文本 |
| data._level | string | 固定值 `"testPoint"` |
| data._status | string | 节点状态 |
| data._source | string | 来源 |
| data._marked | boolean | 是否标记保留 |
| data.description | string / null | 测试点描述 |
| children | array | 调整后的测试用例列表 |
| children[].data | object | 测试用例节点数据 |
| children[].data.id | string / undefined | 已有用例有ID，AI新增用例无ID |
| children[].data.text | string | 用例文本 |
| children[].data._level | string | 固定值 `"testCase"` |
| children[].data._caseProperty | string | 用例属性：`"正例"` / `"反例"` |
| children[].data._source | string | 来源：`"AI"` / `"人工"` |
| children[].data._marked | boolean | 是否标记保留 |
| children[].data._preCondition | string / null | 前置条件 |
| children[].data.steps | array / null | 测试步骤 |
| children[].data.note | string / null | 备注HTML（已有用例有此字段） |
| children[].children | array | 固定为空数组 `[]` |
```

### 5.3 获取对话历史

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/ai-adjust/sessions/{sessionId}/messages` |
| Method | `GET` |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data[].id | string | 消息ID |
| data[].role | string | 角色：`system` / `user` / `assistant` |
| data[].content | string | 消息内容 |
| data[].type | string | 消息类型：`text` / `discussion` / `proposal` |
| data[].changeSummary | string / null | 变更摘要，仅在 type=proposal 时有值 |
| data[].pendingMindMapData | object / null | 待应用的调整后节点数据（两层完整数据，同5.2中的结构） |
| data[].adopted | boolean | 是否已采纳 |
| data[].rejected | boolean | 是否已拒绝 |
| data[].createdAt | string | 消息时间戳（ISO 8601） |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": "msg-1716000000000",
      "role": "assistant",
      "content": "好的，我理解你的需求。",
      "type": "discussion",
      "changeSummary": null,
      "pendingMindMapData": null,
      "adopted": false,
      "rejected": false,
      "createdAt": "2026-05-28T10:30:00.000Z"
    },
    {
      "id": "msg-1716000000001",
      "role": "assistant",
      "content": "已为您新增3个异常场景测试点...",
      "type": "proposal",
      "changeSummary": "新增3个异常场景测试点",
      "pendingMindMapData": {
        "data": { "id": "sr-abc123", "text": "用户登录功能", "_level": "requirement", "_status": "completed" },
        "children": [
          { "data": { "id": "tp-001", "text": "正常登录流程验证", "_level": "testPoint", "_source": "AI", "_marked": false }, "children": [] },
          { "data": { "text": "空密码登录验证", "_level": "testPoint", "_source": "AI", "_marked": false }, "children": [] }
        ]
      },
      "adopted": false,
      "rejected": false,
      "createdAt": "2026-05-28T10:30:01.000Z"
    }
  ],
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 5.4 应用AI调整

确认AI调整方案并应用到脑图数据。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/ai-adjust/sessions/{sessionId}/apply` |
| Method | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| markedTestPointTexts | string[] | 否 | 标记保留的节点文本列表 |
| nodeType | string | 是 | 节点类型：`requirement` / `testPoint` |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.adjustedMindMapData | object | 调整后的两层节点数据（同5.2中 pendingMindMapData 结构） |
| data.addedCount | integer | 新增节点数量 |
| data.removedCount | integer | 移除节点数量 |
| data.preservedCount | integer | 保留标记节点数量 |

### 5.5 采纳AI调整建议

采纳指定的AI调整建议消息，将建议的脑图变更应用到当前数据。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/ai-adjust/sessions/{sessionId}/messages/{messageId}/adopt` |
| Method | `POST` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | string | 是 | 对话ID |
| messageId | string | 是 | 消息ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.messageId | string | 消息ID |
| data.adopted | boolean | 是否已采纳 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "messageId": "msg-1716000000000",
    "adopted": true
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 5.6 拒绝AI调整建议

拒绝指定的AI调整建议消息。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/ai-adjust/sessions/{sessionId}/messages/{messageId}/reject` |
| Method | `POST` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | string | 是 | 对话ID |
| messageId | string | 是 | 消息ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|------|
| data.messageId | string | 消息ID |
| data.rejected | boolean | 是否已拒绝 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "messageId": "msg-1716000000000",
    "rejected": true
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 6. 异步任务管理

### 6.1 快速生成

一键触发指定需求的测试点和测试用例生成任务。该接口为异步操作，调用后立即返回任务ID，前端需通过轮询「获取任务状态」接口获取生成进度。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements/{requirementId}/generate` |
| Method | `POST` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| useKnowledgeBase | boolean | 否 | 是否启用知识库，默认 false。开启后生成时可检索知识库内容作为参考 |

**请求示例**

```json
{
  "useKnowledgeBase": true
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.taskId | string | 任务ID，用于后续轮询任务状态和取消任务 |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "taskId": "task-1716000000000"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**前端轮询机制**：
- 调用成功后，前端每 2 秒调用「获取任务状态」接口
- 根据 `status` 字段判断是否停止轮询：`completed` / `failed` / `cancelled` 时停止
- 任务完成后，前端需重新调用「获取脑图数据」接口刷新脑图

### 6.2 获取任务状态

查询异步任务的当前执行状态和进度。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/tasks/{taskId}` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| taskId | string | 是 | 任务ID，由快速生成接口返回 |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data.taskId | string | 任务ID |
| data.status | string | 任务状态：`pending`（等待中）/ `running`（运行中）/ `completed`（已完成）/ `failed`（失败）/ `cancelled`（已取消） |
| data.progress | integer | 进度百分比 0-100 |
| data.progressText | string | 进度描述文本，如"正在分析需求结构..."、"正在生成测试点：用户名输入验证"、"生成完成"等 |

**响应示例 - 运行中**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "taskId": "task-1716000000000",
    "status": "running",
    "progress": 45,
    "progressText": "正在生成测试点：密码输入验证"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例 - 已完成**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "taskId": "task-1716000000000",
    "status": "completed",
    "progress": 100,
    "progressText": "生成完成"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例 - 已取消**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "taskId": "task-1716000000000",
    "status": "cancelled",
    "progress": 30,
    "progressText": "任务已取消"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 6.3 取消任务

取消正在执行的生成任务。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/tasks/{taskId}/cancel` |
| Method | `POST` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| taskId | string | 是 | 任务ID |

**响应示例**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**说明**：
- 取消成功后，该任务的状态将变为 `cancelled`
- 前端收到取消成功响应后，应停止轮询并重置生成状态
- 若任务已完成或不存在，接口仍返回成功，但任务状态不变

### 6.4 根据需求ID获取活跃任务

根据需求ID查询该需求当前是否有关联的活跃生成任务。用于前端在左侧列表中选中「生成中」状态的需求时，自动恢复轮询状态和进度条展示。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements/{requirementId}/task` |
| Method | `GET` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| data | object / null | 活跃任务信息；若无活跃任务则返回 null |
| data.taskId | string | 任务ID |
| data.requirementId | string | 需求ID |
| data.status | string | 任务状态 |
| data.progress | integer | 进度百分比 0-100 |
| data.progressText | string | 进度描述文本 |

**响应示例 - 存在活跃任务**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "taskId": "task-1716000000000",
    "requirementId": "req-2",
    "status": "running",
    "progress": 45,
    "progressText": "正在生成测试点：密码输入验证"
  },
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例 - 无活跃任务**

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": null,
  "traceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**说明**：
- 该接口仅返回状态为 `running`（运行中）的任务，已完结的任务（`completed` / `failed` / `cancelled`）视为无活跃任务
- 前端在选中「生成中」状态需求时调用此接口：
  - 返回活跃任务 → 恢复轮询和进度条展示
  - 返回 null → 表示任务已失效，前端应将需求状态修正为「待生成」（`confirmed`）
- 若同一需求存在多个活跃任务（异常情况），返回最新创建的那个

---

## 7. 导出

### 7.1 导出Excel

导出当前需求的测试用例为Excel文件。

| 属性 | 值 |
|------|-----|
| URL | `/api/v1/test-design/requirements/{requirementId}/export` |
| Method | `GET` |
| Response-Type | `blob` |

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirementId | string | 是 | 需求ID |

**响应**

返回 Excel 文件流（`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`），浏览器自动下载。

**Excel 表头字段**

| 列序 | 表头名称 | 英文字段 | 说明 |
|------|----------|----------|------|
| A | 测试用例名称 | caseName | 用例的唯一标识名称 |
| B | 用例类型 | caseProperty | 正例 / 反例 |
| C | 前置条件 | preCondition | 执行该用例前需要满足的条件 |
| D | 步骤名字 | name | 步骤的名称 |
| E | 步骤描述 | description | 步骤的具体操作描述 |
| F | 步骤预期结果 | stepExpectedResult | 该步骤执行后期望的结果 |

**数据展示规则**

- steps 的 3 个子字段（name、description、stepExpectedResult）各占一列，每个步骤占一行
- 若用例有多个步骤，则该用例的 caseName / caseProperty / preCondition 单元格纵向合并展示
- 单步骤用例不合并，直接一行展示

**Excel 导出示例**

| caseName | caseProperty | preCondition | name | description | stepExpectedResult |
|----------|--------------|---------------|------|-------------|-------------------|
| 用户正常登录系统 | 正例 | 用户已注册并拥有有效的账号和密码 | 输入用户名 | 在登录页输入正确的用户名 | 用户名输入框显示输入的用户名 |
| (合并) | (合并) | (合并) | 输入密码 | 在登录页输入正确的密码 | 密码输入框显示输入的密码 |
| (合并) | (合并) | (合并) | 点击登录按钮 | 点击登录按钮 | 系统跳转至用户主页 |
| 用户登录失败 | 反例 | 用户已注册但密码错误 | 输入用户名 | 在登录页输入用户名 | 用户名输入框显示输入的用户名 |
| (合并) | (合并) | (合并) | 点击登录按钮 | 点击登录按钮 | 系统提示密码错误 |

**列宽建议**

| 列 | 建议宽度（字符数） |
|----|---------------------|
| A - caseName | 30 |
| B - caseProperty | 10 |
| C - preCondition | 30 |
| D - name | 20 |
| E - description | 30 |
| F - stepExpectedResult | 30 |

---

## 8. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未登录或Token过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复操作） |
| 500 | 服务器内部错误 |

---

**文档版本**：v2.2
**创建日期**：2026-05-11
**更新日期**：2026-05-28
**适用范围**：测试设计模块 - 后端开发接口参考

---

## 变更记录

| 日期 | 版本 | 变更类型 | 变更内容 |
|------|------|------|------|
| 2026-05-28 | v2.3 | **新增+修改** | 1. 新增 [5.5 采纳AI调整建议](#55-采纳ai调整建议) 接口，支持按消息粒度采纳AI提案；2. 新增 [5.6 拒绝AI调整建议](#56-拒绝ai调整建议) 接口，支持按消息粒度拒绝AI提案；3. [5.2 发送对话消息](#52-发送对话消息) 响应参数新增 `changeSummary` 字段，返回变更摘要描述；4. [5.2 发送对话消息](#52-发送对话消息) 响应参数 `pendingMindMapData` 字段说明更新，当 `type=proposal` 时该字段可携带待预览的脑图变更数据 |
| 2026-05-28 | v2.2 | **新增** | 新增 [6.4 根据需求ID获取活跃任务](#64-根据需求id获取活跃任务)，用于前端选中「生成中」状态需求时自动恢复轮询和进度条展示 |
| 2026-05-21 | v2.1 | 修改 | 新增 1.3 从标准化模块导入需求；优化错误码说明 |
| 2026-05-11 | v2.0 | 初始 | 初始版本，覆盖需求列表、脑图数据、测试点管理、测试用例管理、AI调整、异步任务、导出等完整接口 |