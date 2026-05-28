# 智能测试用例平台 - 前端开发计划

## 1. 项目概述

根据需求文档 `requirements_spec_v1.md`，本项目是一个 AI 驱动的测试用例生成平台，采用前后端分离架构。前端技术栈为 Vue 2 + Vue Router + Vuex + Webpack。

## 2. 核心功能模块

| 模块 | 主要功能 | 状态 |
|------|----------|------|
| 登录模块 | 用户注册、登录、数据隔离 | 待开发 |
| 需求标准化模块 | 需求录入、文档标准化、需求拆分、历史记录 | 待开发 |
| 测试设计模块（脑图） | 脑图展示、节点操作、AI调整、异步任务管理、导出 | 待开发 |
| 知识库模块 | 文档管理、知识召回设置 | 待开发 |

## 3. 前端技术架构

```
├── src/
│   ├── components/          # 通用组件
│   ├── views/              # 页面视图
│   ├── router/             # 路由配置
│   ├── store/              # Vuex状态管理
│   ├── api/                # API接口封装
│   ├── utils/              # 工具函数
│   ├── assets/             # 静态资源
│   └── App.vue
├── static/                 # 静态文件
├── index.html              # 入口HTML
├── package.json            # 依赖配置
├── webpack.config.js       # Webpack配置
└── vue.config.js           # Vue配置
```

## 4. 开发计划

### 阶段一：项目初始化与基础配置

| 序号 | 任务 | 描述 | 预计耗时 |
|------|------|------|----------|
| 1 | 初始化 Vue 2 项目 | 使用 Vue CLI 创建项目，配置基础依赖 | 2h |
| 2 | 安装核心依赖 | Vue Router、Vuex、Axios、Element UI、脑图组件、Excel导出库 | 1h |
| 3 | 配置 Webpack/Vue | 配置开发环境、代理、路径别名 | 1h |
| 4 | 创建项目目录结构 | 创建完整的目录结构和基础文件 | 1h |

**核心依赖清单：**
- vue@2.7.x
- vue-router@3.x
- vuex@3.x
- axios@1.x
- element-ui@2.x
- xmind-sdk或其他脑图库
- xlsx/exceljs (Excel导出)
- sass-loader (样式)

### 阶段二：登录模块开发

| 序号 | 任务 | 描述 | 预计耗时 |
|------|------|------|----------|
| 5 | 创建登录页面 | 用户名密码登录表单 | 2h |
| 6 | 创建注册页面 | 用户名密码注册表单 | 2h |
| 7 | 配置路由守卫 | 未登录用户重定向到登录页 | 1h |
| 8 | 用户状态管理 | Vuex存储用户信息、Token | 2h |

### 阶段三：需求标准化模块开发

| 序号 | 任务 | 描述 | 预计耗时 |
|------|------|------|----------|
| 9 | 创建需求标准化页面 | 主页面布局 | 2h |
| 10 | 需求录入组件 | 文本输入、文档上传（docx/xlsx） | 3h |
| 11 | 文档标准化助手 | 调用AI生成标准文档、预览编辑 | 3h |
| 12 | 多轮对话组件 | 嵌入页面的对话框，支持多轮调整 | 3h |
| 13 | 需求拆分功能 | 自动拆分、手动编辑/删除/新增需求 | 3h |
| 14 | 历史记录组件 | 列表展示、查看详情、数据维护 | 2h |

### 阶段四：测试设计模块（脑图展示）开发

| 序号 | 任务 | 描述 | 预计耗时 |
|------|------|------|----------|
| 15 | 脑图组件集成 | 选择并集成脑图组件（4级结构） | 4h |
| 16 | 脑图基础操作 | 展开/折叠、缩放、拖拽移动、双击编辑 | 3h |
| 17 | 右键菜单功能 | 根据节点类型显示不同操作菜单 | 3h |
| 18 | AI调整功能 | 图钉标记、多轮对话调整 | 3h |
| 19 | 异步任务管理 | 快速生成、串行执行、进度条、状态图标 | 4h |
| 20 | 操作栏组件 | 快速生成按钮、知识库开关、导出按钮 | 2h |
| 21 | 批量操作功能 | 批量删除、批量标记 | 2h |
| 22 | Excel导出功能 | 导出测试用例，支持单元格合并 | 3h |
| 23 | 节点来源标识 | AI/人工标签显示 | 1h |

### 阶段五：知识库模块开发

| 序号 | 任务 | 描述 | 预计耗时 |
|------|------|------|----------|
| 24 | 创建知识库页面 | 主页面布局 | 2h |
| 25 | 文档管理功能 | 上传、删除、查看文档 | 3h |
| 26 | 知识召回设置 | 参数调整、召回测试 | 2h |

### 阶段六：公共组件与优化

| 序号 | 任务 | 描述 | 预计耗时 |
|------|------|------|----------|
| 27 | 公共组件封装 | 对话框、进度条、表格等 | 2h |
| 28 | API接口封装 | 统一封装后端API调用 | 2h |
| 29 | 样式优化 | 统一主题、响应式设计 | 3h |
| 30 | 错误处理 | 统一错误处理、异常捕获 | 2h |
| 31 | 测试与验证 | 功能测试、接口联调 | 4h |

## 5. API接口对接清单

| 模块 | API路径 | 方法 | 状态 |
|------|---------|------|------|
| 用户 | /api/auth/login | POST | 待对接 |
| 用户 | /api/auth/register | POST | 待对接 |
| 需求 | /api/requirements | POST/GET | 待对接 |
| 需求 | /api/requirements/{id} | PUT/DELETE | 待对接 |
| 标准化 | /api/standardize | POST | 待对接 |
| 测试点 | /api/test-points/generate | POST | 待对接 |
| 测试点 | /api/test-points/batch-delete | POST | 待对接 |
| 测试用例 | /api/test-cases/generate | POST | 待对接 |
| 测试用例 | /api/test-cases/batch-delete | POST | 待对接 |
| 测试用例 | /api/test-cases/export | GET | 待对接 |
| 任务 | /api/tasks | GET/DELETE | 待对接 |
| 历史记录 | /api/history | GET | 待对接 |
| 历史记录 | /api/history/{id} | GET | 待对接 |
| 知识库 | /api/knowledge/docs | POST/GET/DELETE | 待对接 |

## 6. 数据结构设计

### 6.1 用户状态
```javascript
{
  user: {
    id: '',
    username: '',
    token: ''
  },
  isLoggedIn: false
}
```

### 6.2 需求数据
```javascript
{
  id: '',
  title: '',
  content: '',
  status: 'pending|standardized|split',
  splitRequirements: []
}
```

### 6.3 脑图节点
```javascript
{
  id: '',
  type: 'root|requirement|testPoint|testCase',
  content: '',
  children: [],
  status: 'confirmed|generating|completed',
  marked: false,
  source: 'AI|manual'
}
```

### 6.4 测试用例
```javascript
{
  caseName: '',
  caseProperty: '正例|反例',
  preCondition: '',
  steps: [
    { name: '', description: '', stepExpectedResult: '' }
  ]
}
```

## 7. 关键技术选型

| 分类 | 技术 | 理由 |
|------|------|------|
| 框架 | Vue 2.7 | 需求文档指定，支持Composition API |
| 路由 | Vue Router 3.x | Vue 2 配套版本 |
| 状态管理 | Vuex 3.x | Vue 2 配套版本 |
| UI组件 | Element UI | 成熟稳定，文档完善 |
| 脑图 | 需要选型 | 考虑 xmind-sdk 或自定义实现 |
| Excel导出 | xlsx/exceljs | 功能完善，支持复杂导出 |
| HTTP请求 | Axios | 主流HTTP客户端 |

## 8. 风险与应对

| 风险 | 描述 | 应对方案 |
|------|------|----------|
| 脑图组件选型 | 需找到合适的4级脑图组件 | 备选方案：使用 D3.js 自定义实现 |
| 异步任务管理 | 串行执行、进度追踪复杂 | 使用 Vuex 管理任务状态，配合WebSocket实时更新 |
| Excel导出性能 | 大量数据导出可能卡顿 | 使用流式导出，限制单次导出数量 |
| 后端API未就绪 | 前端开发进度依赖后端 | 使用Mock数据进行开发 |

## 9. 开发环境要求

- Node.js >= 16.x
- npm >= 8.x
- Vue CLI >= 5.x

## 10. 交付物

| 交付物 | 描述 |
|--------|------|
| 前端代码仓库 | 完整的Vue 2项目代码 |
| 构建产物 | dist目录 |
| 开发文档 | 组件说明、API文档 |

---

**文档版本**: v1.0  
**创建日期**: 2026-05-08  
**预计总耗时**: 约 56 小时
