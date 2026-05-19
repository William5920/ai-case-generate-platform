# 用户认证模块接口文档

## 概述

本文档描述智能测试用例平台用户认证模块的接口规范，包括登录、注册、登出等功能。

**基础路径**：`/api/auth`

---

## 目录

- [登录接口](#登录接口)
- [注册接口](#注册接口)
- [登出接口](#登出接口)
- [获取用户信息](#获取用户信息)
- [刷新Token](#刷新token)
- [错误码说明](#错误码说明)

---

## 登录接口

### 接口信息

| 属性 | 值 |
|------|-----|
| URL | `/api/auth/login` |
| Method | `POST` |
| Content-Type | `application/json` |

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名，长度 3-20 位 |
| password | string | 是 | 密码，长度至少 6 位 |

### 请求示例

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | number | 响应状态码，200 表示成功 |
| message | string | 响应消息 |
| data | object | 响应数据 |
| data.token | string | 访问令牌（JWT） |
| data.refreshToken | string | 刷新令牌 |
| data.user | object | 用户信息 |
| data.user.id | string | 用户ID |
| data.user.username | string | 用户名 |
| data.user.createdAt | string | 创建时间 |

### 响应示例

#### 成功响应

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_001",
      "username": "admin",
      "createdAt": "2026-05-01T00:00:00.000Z"
    }
  }
}
```

#### 失败响应

```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 登录成功 |
| 400 | 请求参数错误 |
| 401 | 用户名或密码错误 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 注册接口

### 接口信息

| 属性 | 值 |
|------|-----|
| URL | `/api/auth/register` |
| Method | `POST` |
| Content-Type | `application/json` |

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名，长度 3-20 位，只能包含字母、数字、下划线 |
| password | string | 是 | 密码，长度至少 6 位 |

### 请求示例

```json
{
  "username": "newuser",
  "password": "password123"
}
```

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | number | 响应状态码，200 表示成功 |
| message | string | 响应消息 |
| data | object | 响应数据 |
| data.token | string | 访问令牌（JWT） |
| data.refreshToken | string | 刷新令牌 |
| data.user | object | 用户信息 |
| data.user.id | string | 用户ID |
| data.user.username | string | 用户名 |
| data.user.createdAt | string | 创建时间 |

### 响应示例

#### 成功响应

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_002",
      "username": "newuser",
      "createdAt": "2026-05-10T00:00:00.000Z"
    }
  }
}
```

#### 失败响应

```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 注册成功 |
| 400 | 请求参数错误（用户名已存在等） |
| 500 | 服务器内部错误 |

---

## 登出接口

### 接口信息

| 属性 | 值 |
|------|-----|
| URL | `/api/auth/logout` |
| Method | `POST` |
| Content-Type | `application/json` |
| 需要认证 | 是 |

### 请求头

```
Authorization: Bearer {token}
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| refreshToken | string | 是 | 刷新令牌 |

### 请求示例

```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | number | 响应状态码，200 表示成功 |
| message | string | 响应消息 |
| data | null | 无数据 |

### 响应示例

#### 成功响应

```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

#### 失败响应

```json
{
  "code": 401,
  "message": "未授权",
  "data": null
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 登出成功 |
| 401 | 未授权或 Token 无效 |
| 500 | 服务器内部错误 |

---

## 获取用户信息

### 接口信息

| 属性 | 值 |
|------|-----|
| URL | `/api/auth/user` |
| Method | `GET` |
| 需要认证 | 是 |

### 请求头

```
Authorization: Bearer {token}
```

### 请求参数

无

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | number | 响应状态码，200 表示成功 |
| message | string | 响应消息 |
| data | object | 用户信息 |
| data.id | string | 用户ID |
| data.username | string | 用户名 |
| data.createdAt | string | 创建时间 |
| data.updatedAt | string | 更新时间 |

### 响应示例

#### 成功响应

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "user_001",
    "username": "admin",
    "createdAt": "2026-05-01T00:00:00.000Z",
    "updatedAt": "2026-05-10T00:00:00.000Z"
  }
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 获取成功 |
| 401 | 未授权或 Token 无效 |
| 500 | 服务器内部错误 |

---

## 刷新Token

### 接口信息

| 属性 | 值 |
|------|-----|
| URL | `/api/auth/refresh` |
| Method | `POST` |
| Content-Type | `application/json` |

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| refreshToken | string | 是 | 刷新令牌 |

### 请求示例

```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | number | 响应状态码，200 表示成功 |
| message | string | 响应消息 |
| data | object | 响应数据 |
| data.token | string | 新的访问令牌 |
| data.refreshToken | string | 新的刷新令牌 |

### 响应示例

#### 成功响应

```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 刷新成功 |
| 400 | refreshToken 无效或已过期 |
| 500 | 服务器内部错误 |

---

## 错误码说明

### 通用错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权或 Token 无效 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户名不存在 |
| 1002 | 密码错误 |
| 1003 | 用户名已存在 |
| 1004 | Token 已过期 |
| 1005 | refreshToken 已过期 |

---

## 数据模型

### User 模型

```typescript
interface User {
  id: string;
  username: string;
  createdAt: string;
  updatedAt: string;
}
```

### AuthResponse 模型

```typescript
interface AuthResponse {
  token: string;
  refreshToken: string;
  user: User;
}
```

### ApiResponse 模型

```typescript
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}
```

---

## 注意事项

1. **Token 有效期**：
   - Access Token 有效期：2小时
   - Refresh Token 有效期：7天

2. **密码要求**：
   - 密码长度至少 6 位
   - 建议包含字母、数字和特殊字符

3. **用户名要求**：
   - 长度 3-20 位
   - 只能包含字母、数字和下划线

4. **安全建议**：
   - 传输过程中使用 HTTPS
   - 密码使用 bcrypt 加密存储
   - Token 使用 JWT 格式，包含过期时间

---

**文档版本**：v1.1  
**最后更新**：2026-05-19  
**维护者**：前端开发团队
