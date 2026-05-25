# 用户认证模块 - 后端开发规划文档

## 1. 模块概述

### 1.1 模块定位
用户认证模块是智能测试用例平台的基础安全模块，负责用户注册、登录、Token 管理、用户信息获取和登出功能，为其他业务模块提供身份认证和数据隔离支持。

### 1.2 核心目标
- 实现完整的用户注册/登录/登出流程
- 基于 JWT 的 Token 认证机制（Access Token + Refresh Token）
- 密码 bcrypt 加密存储
- 统一响应格式，与前端接口契约一致
- 为后续业务模块提供 `get_current_user` 依赖注入

---

## 2. 技术方案

### 2.1 技术选型

| 技术 | 版本 | 用途 |
|------|------|------|
| SQLAlchemy | 2.0.x | ORM 框架，数据库操作 |
| SQLite | - | 轻量级数据库，单文件存储 |
| python-jose | 3.3.x | JWT Token 生成与验证 |
| passlib[bcrypt] | 1.7.x | 密码加密（bcrypt 算法） |
| Pydantic | 2.5.x | 请求/响应数据模型 |

### 2.2 JWT Token 设计

| 属性 | Access Token | Refresh Token |
|------|-------------|---------------|
| 有效期 | 2 小时 | 7 天 |
| 载荷 | sub(user_id), exp | sub(user_id), exp, type=refresh |
| 用途 | API 请求认证 | 刷新 Access Token |
| 存储 | 前端 localStorage | 前端 localStorage |

### 2.3 登出策略
采用简单模式：登出时不维护 Token 黑名单，仅由前端清除本地存储的 Token，Token 自然过期失效。

### 2.4 统一响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

---

## 3. 数据库设计

### 3.1 users 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| username | VARCHAR(20) | UNIQUE, NOT NULL | 用户名 |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt 加密密码 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.2 SQLAlchemy 模型

```python
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(20), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 4. API 接口设计

### 4.1 接口列表

| 接口 | 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|------|
| 用户注册 | POST | /api/auth/register | 否 | 注册新用户，返回 Token |
| 用户登录 | POST | /api/auth/login | 否 | 验证身份，返回 Token |
| 用户登出 | POST | /api/auth/logout | 是 | 登出（前端清除 Token） |
| 获取用户信息 | GET | /api/auth/user | 是 | 获取当前登录用户信息 |
| 刷新 Token | POST | /api/auth/refresh | 否 | 用 RefreshToken 换取新 Token |

### 4.2 接口详细设计

#### POST /api/auth/register

**请求体：**
```json
{
  "username": "newuser",
  "password": "password123"
}
```

**成功响应（200）：**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJ...",
    "refreshToken": "eyJ...",
    "user": {
      "id": "uuid-string",
      "username": "newuser",
      "createdAt": "2026-05-20T00:00:00.000Z"
    }
  }
}
```

**失败响应（400）：**
```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

#### POST /api/auth/login

**请求体：**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**成功响应（200）：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJ...",
    "refreshToken": "eyJ...",
    "user": {
      "id": "uuid-string",
      "username": "admin",
      "createdAt": "2026-05-01T00:00:00.000Z"
    }
  }
}
```

**失败响应（401）：**
```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null
}
```

#### POST /api/auth/logout

**请求头：** `Authorization: Bearer {token}`

**请求体：**
```json
{
  "refreshToken": "eyJ..."
}
```

**成功响应（200）：**
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

#### GET /api/auth/user

**请求头：** `Authorization: Bearer {token}`

**成功响应（200）：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "uuid-string",
    "username": "admin",
    "createdAt": "2026-05-01T00:00:00.000Z",
    "updatedAt": "2026-05-20T00:00:00.000Z"
  }
}
```

#### POST /api/auth/refresh

**请求体：**
```json
{
  "refreshToken": "eyJ..."
}
```

**成功响应（200）：**
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "eyJ...(新Token)",
    "refreshToken": "eyJ...(新RefreshToken)"
  }
}
```

---

## 5. 项目文件结构

```
backend/app/
├── core/
│   ├── config.py              # 修改: 新增 JWT_SECRET_KEY、ACCESS_TOKEN_EXPIRE、REFRESH_TOKEN_EXPIRE
│   ├── database.py            # 新增: SQLAlchemy 引擎、会话管理、Base
│   ├── security.py            # 新增: JWT 生成/验证、密码加密/验证
│   └── dependencies.py        # 新增: get_db、get_current_user 依赖注入
├── models/
│   └── user.py                # 新增: User ORM 模型
├── schemas/
│   └── auth.py                # 新增: 请求/响应 Pydantic 模型
├── routers/
│   └── auth.py                # 新增: 认证路由（5个接口）
├── services/
│   └── auth_service.py        # 新增: 认证业务逻辑
└── main.py                    # 修改: 注册 auth 路由、启动时创建数据库表
```

---

## 6. 核心模块设计

### 6.1 database.py — 数据库连接

- 使用 SQLAlchemy 的 `create_engine` 连接 SQLite
- `sessionlocal` 作为会话工厂
- `Base` 作为 ORM 模型基类
- `get_db` 依赖注入函数，提供数据库会话

### 6.2 security.py — 安全工具

- `hash_password(password)` — bcrypt 加密密码
- `verify_password(plain, hashed)` — 验证密码
- `create_access_token(user_id)` — 生成 Access Token（2h）
- `create_refresh_token(user_id)` — 生成 Refresh Token（7d）
- `decode_token(token)` — 解码验证 Token

### 6.3 dependencies.py — 依赖注入

- `get_db()` — 获取数据库会话
- `get_current_user(token, db)` — 从 Bearer Token 解析当前用户

### 6.4 auth_service.py — 业务逻辑

- `register_user(db, username, password)` — 注册用户
- `authenticate_user(db, username, password)` — 验证用户身份
- `get_user_by_id(db, user_id)` — 获取用户信息
- `refresh_tokens(db, refresh_token)` — 刷新 Token

### 6.5 auth.py (router) — 路由

- `POST /register` → auth_service.register_user
- `POST /login` → auth_service.authenticate_user
- `POST /logout` → 返回成功（简单模式）
- `GET /user` → auth_service.get_user_by_id（需认证）
- `POST /refresh` → auth_service.refresh_tokens

---

## 7. 错误码设计

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权或 Token 无效 |
| 1001 | 用户名不存在 |
| 1002 | 密码错误 |
| 1003 | 用户名已存在 |
| 1004 | Token 已过期 |
| 1005 | refreshToken 已过期 |

---

## 8. 开发任务清单

### 任务 1：基础设施搭建
- [ ] 更新 requirements.txt，新增依赖
- [ ] 创建 database.py，配置 SQLite 连接
- [ ] 更新 config.py，新增 JWT 配置项

### 任务 2：安全模块
- [ ] 创建 security.py，实现密码加密和 JWT 工具函数

### 任务 3：数据模型
- [ ] 创建 models/user.py，定义 User ORM 模型
- [ ] 创建 schemas/auth.py，定义请求/响应 Pydantic 模型

### 任务 4：依赖注入
- [ ] 创建 dependencies.py，实现 get_db 和 get_current_user

### 任务 5：业务逻辑
- [ ] 创建 services/auth_service.py，实现认证业务逻辑

### 任务 6：路由层
- [ ] 创建 routers/auth.py，实现 5 个 API 接口

### 任务 7：应用集成
- [ ] 更新 main.py，注册 auth 路由、启动时创建数据库表
- [ ] 创建必要的 __init__.py 文件

### 任务 8：验证测试
- [ ] 启动后端服务，验证所有接口正常工作

---

**文档版本**：v1.0
**创建日期**：2026-05-20
**维护者**：后端开发团队
