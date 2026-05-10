# 智能测试用例平台 - 设计规范

## 目录
- [概述](#概述)
- [设计原则](#设计原则)
- [色彩系统](#色彩系统)
- [排版系统](#排版系统)
- [间距系统](#间距系统)
- [组件规范](#组件规范)
- [页面布局规范](#页面布局规范)

---

## 概述

本设计规范旨在统一智能测试用例平台的视觉风格，确保各模块间的设计一致性。平台采用双主题设计：
- **品牌营销页/登录页**：深色科技风格，强调科技感和专业感
- **业务页面**：浅色简洁风格，注重实用性和效率

---

## 设计原则

### 1. 一致性
- 所有页面使用统一的色彩、字体、间距系统
- 相同功能的组件保持相同的交互方式和视觉表现

### 2. 层次清晰
- 通过色彩、大小、位置、间距建立清晰的视觉层次
- 重要信息优先展示，次要信息弱化处理

### 3. 反馈及时
- 所有用户操作都有相应的视觉反馈
- 加载状态、错误状态、成功状态都有明确的提示

### 4. 易用优先
- 保持界面简洁，减少认知负担
- 符合用户的使用习惯和预期

---

## 色彩系统

### 品牌主色（蓝色系）

| 色彩 | 用途 | 代码 |
|------|------|------|
| Primary 50 | 背景、浅色状态 | `#eff6ff` |
| Primary 100 | 浅色背景 | `#dbeafe` |
| Primary 200 | 边框、分割线 | `#bfdbfe` |
| Primary 300 | 次要按钮 | `#93c5fd` |
| Primary 400 | 悬停状态 | `#60a5fa` |
| **Primary 500** | **主按钮、主链接** | `#3b82f6` |
| Primary 600 | 点击状态 | `#2563eb` |
| Primary 700 | 深色按钮 | `#1d4ed8` |
| Primary 800 | 深色文字 | `#1e40af` |
| Primary 900 | 深色背景 | `#1e3a8a` |

### 功能色

| 色彩 | 用途 | 代码 |
|------|------|------|
| Success | 成功状态、确认操作 | `#10b981` |
| Warning | 警告状态、提示信息 | `#f59e0b` |
| Danger | 错误状态、删除操作 | `#ef4444` |
| Info | 信息提示、中性状态 | `#06b6d4` |

### 中性色（浅色主题）

| 色彩 | 用途 | 代码 |
|------|------|------|
| Gray 50 | 页面背景 | `#f9fafb` |
| Gray 100 | 卡片背景 | `#f3f4f6` |
| Gray 200 | 边框、分割线 | `#e5e7eb` |
| Gray 300 | 禁用状态 | `#d1d5db` |
| Gray 400 | 辅助文字 | `#9ca3af` |
| **Gray 500** | **次要文字** | `#6b7280` |
| Gray 600 | 主要文字 | `#4b5563` |
| **Gray 700** | **标题文字** | `#374151` |
| Gray 800 | 深色文字 | `#1f2937` |
| Gray 900 | 最深文字 | `#111827` |

### 深色主题色彩（登录页）

| 用途 | 代码 |
|------|------|
| 背景渐变起始 | `indigo-900` |
| 背景渐变中间 | `purple-900` |
| 背景渐变结束 | `pink-800` |
| 卡片背景 | `bg-white/10` |
| 卡片边框 | `border-white/20` |
| 主文字 | `text-white` |
| 次要文字 | `text-white/70` |
| 占位文字 | `text-white/40` |

### 渐变色规范

#### 蓝色渐变（登录页按钮）
```css
from-blue-500 to-purple-600
```

#### 青色渐变（注册页按钮）
```css
from-cyan-500 to-blue-600
```

---

## 排版系统

### 字体家族

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

### 字号层级

| 层级 | 字号 | 字重 | 用途 | 代码 |
|------|------|------|------|------|
| H1 | 30px | Bold | 页面大标题 | `text-3xl font-bold` |
| H2 | 18px | Semibold | 模块标题 | `text-lg font-semibold` |
| H3 | 16px | Semibold | 卡片标题 | `text-base font-semibold` |
| Body | 14px | Normal | 正文文本 | `text-sm` |
| Small | 12px | Normal | 辅助文字 | `text-xs` |

### 行高

| 元素 | 行高 |
|------|------|
| 标题 | 1.25 |
| 正文 | 1.5 |

---

## 间距系统

### 基础间距单位

使用 4px 为基础间距单位：

| 间距值 | 代码 | 常用场景 |
|--------|------|----------|
| 4px | space-1 | 超小间距 |
| 8px | space-2 | 小间距 |
| 12px | space-3 | 中小间距 |
| 16px | space-4 | 标准间距 |
| 20px | space-5 | 中大间距 |
| 24px | space-6 | 大间距 |
| 32px | space-8 | 超大间距 |

### 常用间距组合

- 卡片内边距：`p-6` (24px)
- 表单元素间距：`space-y-5`
- 导航项间距：`space-y-2`
- 按钮组间距：`space-x-4`

---

## 组件规范

### 按钮 (Button)

#### 主按钮

```html
<button class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
  按钮文字
</button>
```

#### 玻璃态渐变按钮（登录页）

```html
<button class="w-full py-3.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-600 hover:to-purple-700 focus:ring-4 focus:ring-blue-400/30 transition-all shadow-lg hover:shadow-xl">
  按钮文字
</button>
```

#### 次要按钮

```html
<button class="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
  按钮文字
</button>
```

#### 图标按钮

```html
<button class="p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <!-- 图标内容 -->
  </svg>
</button>
```

#### 加载状态

```html
<button class="relative">
  <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
  加载中...
</button>
```

### 输入框 (Input)

#### 标准输入框

```html
<input
  type="text"
  placeholder="请输入..."
  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
/>
```

#### 带图标输入框（浅色主题）

```html
<div class="relative">
  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <!-- 图标内容 -->
    </svg>
  </div>
  <input
    class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
  />
</div>
```

#### 玻璃态输入框（深色主题）

```html
<div class="relative group">
  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
    <svg class="h-5 w-5 text-white/50 group-focus-within:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <!-- 图标内容 -->
    </svg>
  </div>
  <input
    class="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none text-white placeholder-white/40"
  />
  <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none"></div>
</div>
```

#### 错误状态

```html
<input class="border-red-400" />
<p class="mt-1 text-sm text-red-400">错误提示信息</p>
```

### 文本域 (Textarea)

```html
<textarea
  rows="6"
  placeholder="请输入..."
  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
></textarea>
```

### 卡片 (Card)

#### 标准卡片

```html
<div class="bg-white rounded-lg shadow-sm p-6">
  <!-- 卡片内容 -->
</div>
```

#### 玻璃态卡片（深色主题）

```html
<div class="bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
  <!-- 卡片内容 -->
</div>
```

### 导航项 (Nav Item)

#### 激活状态

```html
<router-link class="block px-4 py-3 bg-blue-50 text-blue-600 rounded-lg font-medium">
  导航项
</router-link>
```

#### 默认状态

```html
<router-link class="block px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
  导航项
</router-link>
```

### 提示消息 (Alert)

#### 错误提示

```html
<div class="p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
  <p class="text-red-400 text-sm flex items-center">
    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>
    错误提示信息
  </p>
</div>
```

### 对话框 (Modal)

```html
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4">
    <div class="flex items-center justify-between p-4 border-b">
      <h3 class="text-lg font-semibold">标题</h3>
      <button class="p-2 hover:bg-gray-100 rounded-lg">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
    <div class="p-4">
      <!-- 内容 -->
    </div>
  </div>
</div>
```

### 复选框 (Checkbox)

#### 标准样式

```html
<label class="flex items-center cursor-pointer">
  <input type="checkbox" class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
  <span class="ml-2 text-sm text-gray-600">选项文字</span>
</label>
```

#### 玻璃态样式（深色主题）

```html
<label class="flex items-center cursor-pointer group">
  <div class="relative">
    <input type="checkbox" class="sr-only peer" />
    <div class="w-5 h-5 border border-white/30 rounded-md peer-checked:bg-blue-500 peer-checked:border-transparent transition-all flex items-center justify-center">
      <svg v-if="checked" class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
      </svg>
    </div>
  </div>
  <span class="ml-2 text-sm text-white/70 group-hover:text-white transition-colors">选项文字</span>
</label>
```

---

## 页面布局规范

### 深色主题页面（登录/注册）

#### 背景装饰

```html
<div class="min-h-screen flex items-center justify-center relative overflow-hidden">
  <!-- 渐变背景 -->
  <div class="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800"></div>
  
  <!-- 模糊圆形装饰 -->
  <div class="absolute inset-0 overflow-hidden">
    <div class="absolute -top-1/2 -right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
    <div class="absolute -bottom-1/2 -left-1/4 w-96 h-96 bg-pink-500/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-3xl"></div>
  </div>
  
  <!-- 点阵纹理 -->
  <div class="absolute inset-0" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0); background-size: 40px 40px;"></div>
  
  <!-- 内容卡片 -->
  <div class="relative z-10">
    <!-- 内容 -->
  </div>
</div>
```

### 浅色主题页面（业务页）

#### 侧边栏布局

```html
<div class="min-h-screen bg-gray-50">
  <!-- 顶部导航 -->
  <nav class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo 和标题 -->
        <!-- 用户信息 -->
      </div>
    </div>
  </nav>

  <!-- 主体内容 -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex gap-6">
      <!-- 侧边栏 -->
      <aside class="w-64 flex-shrink-0">
        <div class="bg-white rounded-lg shadow-sm p-4">
          <!-- 导航菜单 -->
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="flex-1">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <!-- 页面内容 -->
        </div>
      </main>
    </div>
  </div>
</div>
```

---

## 动画规范

### 过渡动画

使用 Tailwind 预设的过渡动画：

```css
transition-all        /* 所有属性过渡 */
transition-colors     /* 仅颜色过渡 */
transition-opacity    /* 仅透明度过渡 */
```

### 动画时长

- 快速：150ms
- 标准：300ms
- 慢速：500ms

### 加载动画

使用旋转动画：

```html
<svg class="animate-spin" ...></svg>
```

---

## 图标规范

### 图标来源

使用 Heroicons 风格的 SVG 图标，保持以下一致：
- 描边宽度：2px
- 尺寸：24x24 (w-5 h-5) 或 20x20 (w-4 h-4)
- 风格：线性图标 (stroke icons)

### 图标颜色

- 默认状态：灰色
- 悬停状态：蓝色
- 激活状态：蓝色

---

## 文件命名规范

### 组件命名

- 使用 PascalCase 命名组件文件：`UserProfile.vue`
- 使用 kebab-case 命名 CSS 类：`user-profile-card`

### 样式类名

- 使用 Tailwind CSS 工具类为主
- 如需自定义样式，使用语义化类名前缀：`btn-`, `card-`, `input-`

---

## 总结

本设计规范是智能测试用例平台前端开发的指导文档，所有开发人员应严格遵守。如有新增组件或修改现有组件设计，应及时更新此规范，保持文档的时效性和准确性。

**版本**：v1.0  
**最后更新**：2026-05-10
