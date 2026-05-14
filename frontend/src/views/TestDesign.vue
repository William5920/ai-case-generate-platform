<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <nav class="bg-white shadow-sm sticky top-0 z-40">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-8">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <h1 class="text-lg font-bold text-gray-800">智能测试用例平台</h1>
            </div>
            <div class="flex items-center space-x-1">
              <router-link
                to="/standardization"
                class="px-4 py-2 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
              >
                需求标准化
              </router-link>
              <router-link
                to="/test-design"
                class="px-4 py-2 text-sm font-medium rounded-lg bg-blue-50 text-blue-600"
              >
                测试设计
              </router-link>
              <router-link
                to="/knowledge-base"
                class="px-4 py-2 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
              >
                知识库
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ $store.getters.user?.username || 'admin' }}</span>
            <button @click="handleLogout" class="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="flex h-[calc(100vh-64px)]">
      <!-- 左侧边栏 -->
      <aside class="w-64 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto flex flex-col">
        <div class="p-4 flex-1">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold text-gray-800">需求列表</h3>
            <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{{ totalCount }}</span>
          </div>

          <!-- 搜索框 -->
          <div class="relative mb-3">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="搜索需求..."
              class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @input="onSearchInput"
            />
          </div>

          <!-- 状态筛选 -->
          <div class="flex items-center space-x-1 mb-3">
            <button
              v-for="tab in statusTabs"
              :key="tab.value"
              @click="filterByStatus(tab.value)"
              class="flex-1 px-2 py-1.5 text-xs font-medium rounded-md transition-colors"
              :class="activeStatusFilter === tab.value
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'"
            >{{ tab.label }}</button>
          </div>

          <!-- 加载状态 -->
          <div v-if="isLoadingList" class="flex items-center justify-center py-12">
            <svg class="w-5 h-5 text-blue-500 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span class="ml-2 text-sm text-gray-400">加载中...</span>
          </div>

          <!-- 加载失败 -->
          <div v-else-if="loadError" class="text-center py-8">
            <svg class="w-10 h-10 text-red-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <p class="text-sm text-red-400 mb-2">{{ loadError }}</p>
            <button @click="fetchRequirementList" class="text-xs text-blue-600 hover:text-blue-700 underline">重新加载</button>
          </div>

          <!-- 空状态 -->
          <div v-else-if="filteredHistoryList.length === 0 && !isLoadingList" class="text-center py-8">
            <svg class="w-10 h-10 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
            </svg>
            <p class="text-xs text-gray-400">{{ searchKeyword ? '未找到匹配的需求' : '暂无需求数据' }}</p>
            <p v-if="!searchKeyword" class="text-xs text-gray-300 mt-1">前往「需求标准化」模块完成需求录入</p>
          </div>

          <!-- 需求列表 -->
          <div v-else class="space-y-1">
            <div
              v-for="item in filteredHistoryList"
              :key="item.id"
              @click="selectRequirement(item)"
              class="p-3 rounded-lg cursor-pointer transition-all group"
              :class="item.id === activeRequirementId ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50 border border-transparent'"
            >
              <div class="flex items-start justify-between">
                <p class="text-sm text-gray-700 truncate flex-1 mr-2">{{ item.title }}</p>
                <span
                  class="flex-shrink-0 px-1.5 py-0.5 text-xs rounded"
                  :class="getRequirementStatusClass(item.status)"
                >{{ item.statusText }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1.5">{{ item.date }}</p>
              <div class="mt-2 flex items-center space-x-3 text-xs text-gray-400">
                <span class="flex items-center space-x-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  <span>{{ item.testPointCount }}测试点</span>
                </span>
                <span class="flex items-center space-x-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <span>{{ item.caseCount }}用例</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="flex-1 flex flex-col overflow-hidden">
        <!-- 工具栏 -->
        <div class="bg-white border-b border-gray-200 px-6 py-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <h2 class="text-base font-semibold text-gray-800">
                {{ activeRequirement ? activeRequirement.title : '测试设计脑图' }}
              </h2>
              <span v-if="activeRequirement" class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                {{ activeRequirement.statusText }}
              </span>
            </div>
            <div class="flex items-center space-x-3">
              <!-- 知识库开关 -->
              <label class="flex items-center space-x-2 cursor-pointer">
                <div class="relative">
                  <input type="checkbox" class="sr-only peer" v-model="knowledgeBaseEnabled" />
                  <div class="w-9 h-5 bg-gray-200 rounded-full peer-checked:bg-blue-600 transition-colors"></div>
                  <div class="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow peer-checked:translate-x-4 transition-transform"></div>
                </div>
                <span class="text-sm text-gray-600">知识库</span>
              </label>

              <div class="w-px h-5 bg-gray-200"></div>

              <!-- 快速生成按钮 -->
              <button
                @click="startGenerate"
                class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="isGenerating || !activeRequirement"
              >
                <svg v-if="!isGenerating" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>{{ isGenerating ? '生成中...' : '快速生成' }}</span>
              </button>

              <!-- 取消生成按钮 -->
              <button
                v-if="isGenerating"
                @click="cancelGenerate"
                class="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                取消
              </button>

              <!-- 导出按钮 -->
              <button
                @click="exportExcel"
                :disabled="!activeRequirement || isExporting"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="!isExporting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>{{ isExporting ? '导出中...' : '导出Excel' }}</span>
              </button>
            </div>
          </div>

          <!-- 进度条 -->
          <div v-if="isGenerating" class="mt-3">
            <div class="flex items-center justify-between text-xs text-gray-500 mb-1.5">
              <span>{{ progressText }}</span>
              <span>{{ progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5">
              <div
                class="bg-blue-600 h-1.5 rounded-full transition-all duration-500 ease-out"
                :style="{ width: progress + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- 脑图画布 -->
        <div class="flex-1 overflow-hidden bg-gray-50 relative">
          <!-- 空状态 -->
          <div v-if="!activeRequirement" class="absolute inset-0 flex items-center justify-center">
            <div class="text-center">
              <svg class="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              <p class="text-gray-400 text-sm mb-4">请从左侧选择一个需求开始测试设计</p>
              <p class="text-gray-300 text-xs">或前往「需求标准化」模块完成需求录入与拆分</p>
            </div>
          </div>

          <!-- simple-mind-map 容器 -->
          <div
            v-show="activeRequirement"
            ref="mindMapContainer"
            class="w-full h-full"
          ></div>
        </div>

        <!-- 底部缩放控制栏 -->
        <div class="bg-white border-t border-gray-200 px-6 py-2 flex items-center justify-between">
          <div class="flex items-center space-x-1 text-xs text-gray-400">
            <span>提示：右键节点打开菜单 | 双击用例编辑 | 滚轮缩放</span>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="zoomOut"
              class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
              title="缩小"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path>
              </svg>
            </button>
            <span class="text-sm text-gray-600 font-medium w-12 text-center">{{ Math.round(zoomLevel * 100) }}%</span>
            <button
              @click="zoomIn"
              class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
              title="放大"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
              </svg>
            </button>
            <div class="w-px h-4 bg-gray-200 mx-1"></div>
            <button
              @click="fitCanvas"
              class="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
              title="适应画布"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- 用例备注弹窗容器 -->
    <div id="custom-note-popover"></div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="fixed bg-white rounded-lg shadow-xl border border-gray-200 py-1.5 z-50 min-w-[180px] context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
    >
      <!-- 需求节点菜单 -->
      <template v-if="contextMenu.type === 'requirement'">
        <button @click="addTestPoint" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          <span>添加测试点</span>
        </button>
        <button @click="aiAdjust" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
          </svg>
          <span>AI调整</span>
        </button>
      </template>

      <!-- 测试点节点菜单 -->
      <template v-if="contextMenu.type === 'testPoint'">
        <button @click="editTestPoint" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          <span>编辑</span>
        </button>
        <button @click="addTestCase" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          <span>添加测试用例</span>
        </button>
        <button @click="aiAdjust" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
          </svg>
          <span>AI调整</span>
        </button>
        <div class="border-t border-gray-100 my-1"></div>
        <button @click="toggleMark" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
          </svg>
          <span>{{ contextMenu.node && contextMenu.node.marked ? '取消标记保留' : '标记保留' }}</span>
        </button>
        <div class="border-t border-gray-100 my-1"></div>
        <button @click="deleteTestPoint" class="context-menu-item text-red-600 hover:bg-red-50">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          <span>删除</span>
        </button>
      </template>

      <!-- 测试用例节点菜单 -->
      <template v-if="contextMenu.type === 'testCase'">
        <button @click="editTestCaseDialog" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          <span>编辑</span>
        </button>
        <button @click="toggleMark" class="context-menu-item">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
          </svg>
          <span>{{ contextMenu.node && contextMenu.node.marked ? '取消标记保留' : '标记保留' }}</span>
        </button>
        <div class="border-t border-gray-100 my-1"></div>
        <button @click="deleteTestCase" class="context-menu-item text-red-600 hover:bg-red-50">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          <span>删除</span>
        </button>
      </template>
    </div>

    <!-- 添加测试点弹窗 -->
    <div v-if="showAddTestPointDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30" @click="closeAddTestPointDialog"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800">添加测试点</h3>
          <p class="text-xs text-gray-400 mt-1">在「{{ contextMenu.node && contextMenu.node.text }}」节点下添加新的测试点</p>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              测试点名称
              <span class="text-red-500">*</span>
            </label>
            <input
              ref="testPointInput"
              v-model="newTestPointName"
              type="text"
              placeholder="请输入测试点名称"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @keyup.enter="confirmAddTestPoint"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">测试点描述</label>
            <textarea
              v-model="newTestPointDescription"
              rows="3"
              placeholder="请输入测试点描述（选填）"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            ></textarea>
          </div>
          <p v-if="addTestPointError" class="text-xs text-red-500">{{ addTestPointError }}</p>
        </div>
        <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3">
          <button
            @click="closeAddTestPointDialog"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >取消</button>
          <button
            @click="confirmAddTestPoint"
            :disabled="isAddingTestPoint"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="isAddingTestPoint" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ isAddingTestPoint ? '添加中...' : '确认添加' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑测试点弹窗 -->
    <div v-if="showEditTestPointDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30" @click="closeEditTestPointDialog"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800">编辑测试点</h3>
          <p class="text-xs text-gray-400 mt-1">修改「{{ contextMenu.node && contextMenu.node.text }}」测试点内容</p>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              测试点名称
              <span class="text-red-500">*</span>
            </label>
            <input
              ref="editTestPointInput"
              v-model="editTestPointName"
              type="text"
              placeholder="请输入测试点名称"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @keyup.enter="confirmEditTestPoint"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">测试点描述</label>
            <textarea
              v-model="editTestPointDescription"
              rows="3"
              placeholder="请输入测试点描述（选填）"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            ></textarea>
          </div>
          <p v-if="editTestPointError" class="text-sm text-red-500">{{ editTestPointError }}</p>
        </div>
        <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3">
          <button
            @click="closeEditTestPointDialog"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >取消</button>
          <button
            @click="confirmEditTestPoint"
            :disabled="isEditingTestPoint"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="isEditingTestPoint" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ isEditingTestPoint ? '保存中...' : '保存' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 删除测试点确认弹窗 -->
    <div v-if="showDeleteTestPointDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30" @click="closeDeleteTestPointDialog"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
        <div class="px-6 py-5 text-center">
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </div>
          <h3 class="text-base font-semibold text-gray-800 mb-2">确认删除测试点</h3>
          <p class="text-sm text-gray-500">
            确定要删除测试点「{{ contextMenu.node && contextMenu.node.text }}」吗？该操作不可撤销，其下的所有测试用例也将一并删除。
          </p>
        </div>
        <div class="px-6 py-4 bg-gray-50 flex justify-center space-x-3">
          <button
            @click="closeDeleteTestPointDialog"
            class="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >取消</button>
          <button
            @click="confirmDeleteTestPoint"
            :disabled="isDeletingTestPoint"
            class="px-6 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="isDeletingTestPoint" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ isDeletingTestPoint ? '删除中...' : '确认删除' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 添加测试用例弹窗 -->
    <div v-if="showAddTestCaseDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30" @click="closeAddTestCaseDialog"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden max-h-[85vh] flex flex-col">
        <div class="px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <h3 class="text-lg font-semibold text-gray-800">添加测试用例</h3>
          <p class="text-xs text-gray-400 mt-1">在「{{ contextMenu.node && contextMenu.node.text }}」测试点下添加新的测试用例</p>
        </div>
        <div class="px-6 py-4 space-y-4 overflow-y-auto flex-1">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用例名称
              <span class="text-red-500">*</span>
            </label>
            <input
              ref="testCaseNameInput"
              v-model="newTestCaseName"
              type="text"
              placeholder="请输入测试用例名称"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用例类型
              <span class="text-red-500">*</span>
            </label>
            <div class="flex items-center space-x-4">
              <label class="flex items-center cursor-pointer">
                <input type="radio" v-model="newTestCaseProperty" value="正例" class="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300" />
                <span class="ml-2 text-sm text-gray-700">正例</span>
              </label>
              <label class="flex items-center cursor-pointer">
                <input type="radio" v-model="newTestCaseProperty" value="反例" class="w-4 h-4 text-red-600 focus:ring-red-500 border-gray-300" />
                <span class="ml-2 text-sm text-gray-700">反例</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">前置条件</label>
            <textarea
              v-model="newTestCasePreCondition"
              rows="2"
              placeholder="请输入前置条件（选填）"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            ></textarea>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="block text-sm font-medium text-gray-700">测试步骤</label>
              <button
                @click="addTestCaseStep"
                type="button"
                class="text-xs text-blue-600 hover:text-blue-700 flex items-center space-x-1"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                <span>添加步骤</span>
              </button>
            </div>
            <div class="space-y-3">
              <div
                v-for="(step, index) in newTestCaseSteps"
                :key="index"
                class="p-3 bg-gray-50 rounded-lg border border-gray-200 relative"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-semibold text-blue-600">步骤 {{ index + 1 }}</span>
                  <button
                    v-if="newTestCaseSteps.length > 1"
                    @click="removeTestCaseStep(index)"
                    type="button"
                    class="text-xs text-red-500 hover:text-red-700"
                  >删除</button>
                </div>
                <div class="space-y-2">
                  <input
                    v-model="step.name"
                    type="text"
                    placeholder="步骤名称"
                    class="w-full px-2.5 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    v-model="step.description"
                    type="text"
                    placeholder="步骤描述"
                    class="w-full px-2.5 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    v-model="step.stepExpectedResult"
                    type="text"
                    placeholder="预期结果"
                    class="w-full px-2.5 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>
          <p v-if="addTestCaseError" class="text-sm text-red-500">{{ addTestCaseError }}</p>
        </div>
        <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3 flex-shrink-0">
          <button
            @click="closeAddTestCaseDialog"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >取消</button>
          <button
            @click="confirmAddTestCase"
            :disabled="isAddingTestCase"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="isAddingTestCase" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ isAddingTestCase ? '添加中...' : '确认添加' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 删除测试用例确认弹窗 -->
    <div v-if="showDeleteTestCaseDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30" @click="closeDeleteTestCaseDialog"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
        <div class="px-6 py-5 text-center">
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </div>
          <h3 class="text-base font-semibold text-gray-800 mb-2">确认删除测试用例</h3>
          <p class="text-sm text-gray-500">
            确定要删除测试用例「{{ contextMenu.node && contextMenu.node.text }}」吗？该操作不可撤销。
          </p>
        </div>
        <div class="px-6 py-4 bg-gray-50 flex justify-center space-x-3">
          <button
            @click="closeDeleteTestCaseDialog"
            class="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >取消</button>
          <button
            @click="confirmDeleteTestCase"
            :disabled="isDeletingTestCase"
            class="px-6 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="isDeletingTestCase" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ isDeletingTestCase ? '删除中...' : '确认删除' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑测试用例弹窗 -->
    <div v-if="showEditTestCaseDialog" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/30" @click="closeEditTestCaseDialog"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden max-h-[85vh] flex flex-col">
        <div class="px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <h3 class="text-lg font-semibold text-gray-800">编辑测试用例</h3>
          <p class="text-xs text-gray-400 mt-1">修改「{{ contextMenu.node && contextMenu.node.text }}」测试用例内容</p>
        </div>
        <div class="px-6 py-4 space-y-4 overflow-y-auto flex-1">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用例名称
              <span class="text-red-500">*</span>
            </label>
            <input
              ref="editTestCaseNameInput"
              v-model="editTestCaseName"
              type="text"
              placeholder="请输入测试用例名称"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用例类型
              <span class="text-red-500">*</span>
            </label>
            <div class="flex items-center space-x-4">
              <label class="flex items-center cursor-pointer">
                <input type="radio" v-model="editTestCaseProperty" value="正例" class="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300" />
                <span class="ml-2 text-sm text-gray-700">正例</span>
              </label>
              <label class="flex items-center cursor-pointer">
                <input type="radio" v-model="editTestCaseProperty" value="反例" class="w-4 h-4 text-red-600 focus:ring-red-500 border-gray-300" />
                <span class="ml-2 text-sm text-gray-700">反例</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">前置条件</label>
            <textarea
              v-model="editTestCasePreCondition"
              rows="2"
              placeholder="请输入前置条件（选填）"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            ></textarea>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="block text-sm font-medium text-gray-700">测试步骤</label>
              <button
                @click="addEditTestCaseStep"
                type="button"
                class="text-xs text-blue-600 hover:text-blue-700 flex items-center space-x-1"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                <span>添加步骤</span>
              </button>
            </div>
            <div class="space-y-3">
              <div
                v-for="(step, index) in editTestCaseSteps"
                :key="index"
                class="p-3 bg-gray-50 rounded-lg border border-gray-200 relative"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-semibold text-blue-600">步骤 {{ index + 1 }}</span>
                  <button
                    v-if="editTestCaseSteps.length > 1"
                    @click="removeEditTestCaseStep(index)"
                    type="button"
                    class="text-xs text-red-500 hover:text-red-700"
                  >删除</button>
                </div>
                <div class="space-y-2">
                  <input
                    v-model="step.name"
                    type="text"
                    placeholder="步骤名称"
                    class="w-full px-2.5 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    v-model="step.description"
                    type="text"
                    placeholder="步骤描述"
                    class="w-full px-2.5 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    v-model="step.stepExpectedResult"
                    type="text"
                    placeholder="预期结果"
                    class="w-full px-2.5 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>
          <p v-if="editTestCaseError" class="text-sm text-red-500">{{ editTestCaseError }}</p>
        </div>
        <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3 flex-shrink-0">
          <button
            @click="closeEditTestCaseDialog"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >取消</button>
          <button
            @click="confirmEditTestCase"
            :disabled="isEditingTestCase"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="isEditingTestCase" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ isEditingTestCase ? '保存中...' : '保存' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- AI调整弹窗 -->
    <div v-if="showAiAdjustDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeAiAdjustDialog">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-6xl mx-4 h-[85vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-base font-semibold text-gray-800">AI 调整</h3>
              <p class="text-xs text-gray-400">
                当前节点：{{ contextMenu.node && contextMenu.node.text }}
                <span class="ml-2 px-1.5 py-0.5 text-xs rounded" :class="aiAdjustNodeType === 'requirement' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">{{ aiAdjustNodeType === 'requirement' ? '需求' : '测试点' }}</span>
              </p>
            </div>
          </div>
          <button @click="closeAiAdjustDialog" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div class="flex-1 flex overflow-hidden">
          <!-- 左侧：对话区 -->
          <div class="w-1/2 flex flex-col border-r border-gray-100">
            <div ref="aiChatContainer" class="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
              <div v-if="aiMessages.length === 0" class="flex flex-col items-center justify-center h-full text-center py-12">
                <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
                  <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                  </svg>
                </div>
                <p class="text-sm text-gray-500 font-medium">开始AI调整</p>
                <p class="text-xs text-gray-400 mt-1">AI 会先与您讨论确认，再调整测试设计</p>
                <div class="mt-4 space-y-2 w-full max-w-xs">
                  <button
                    @click="sendQuickAiMessage('请帮我补充边界值测试用例')"
                    class="block w-full text-left px-3 py-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors"
                  >💡 请帮我补充边界值测试用例</button>
                  <button
                    @click="sendQuickAiMessage('请帮我补充异常场景的测试点')"
                    class="block w-full text-left px-3 py-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors"
                  >💡 请帮我补充异常场景的测试点</button>
                  <button
                    @click="sendQuickAiMessage('请帮我优化测试用例的步骤描述')"
                    class="block w-full text-left px-3 py-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors"
                  >💡 请帮我优化测试用例的步骤描述</button>
                </div>
              </div>
              <div
                v-for="(msg, index) in aiMessages"
                :key="index"
                class="flex"
                :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
              >
                <div v-if="msg.role !== 'user'" class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0 mr-2">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
                <div
                  class="max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed"
                  :class="msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-md' : 'bg-white text-gray-700 rounded-bl-md shadow-sm border border-gray-100'"
                >
                  <div v-if="msg.type === 'proposal'" class="mb-2">
                    <p class="text-xs text-blue-600 font-medium mb-2">💭 AI 建议：</p>
                    <div v-html="formatAiMessage(msg.content)"></div>
                    <div v-if="!msg.confirmed && !msg.rejected" class="flex items-center space-x-2 mt-3 pt-2 border-t border-gray-100">
                      <button
                        @click="confirmAiProposal(index)"
                        class="px-3 py-1 text-xs bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
                      >采纳</button>
                      <button
                        @click="rejectAiProposal(index)"
                        class="px-3 py-1 text-xs bg-gray-200 text-gray-600 rounded-md hover:bg-gray-300 transition-colors"
                      >不采纳</button>
                    </div>
                    <div v-else class="mt-2 pt-2 border-t border-gray-100">
                      <span v-if="msg.confirmed" class="text-xs text-green-600">✅ 已采纳，脑图已更新</span>
                      <span v-else class="text-xs text-gray-400">❌ 未采纳</span>
                    </div>
                  </div>
                  <div v-else v-html="formatAiMessage(msg.content)"></div>
                </div>
                <div v-if="msg.role === 'user'" class="w-8 h-8 bg-gray-300 rounded-lg flex items-center justify-center flex-shrink-0 ml-2">
                  <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
              </div>
              <div v-if="isAiTyping" class="flex justify-start">
                <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0 mr-2">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
                <div class="bg-white rounded-2xl rounded-bl-md shadow-sm border border-gray-100 px-4 py-3">
                  <div class="flex items-center space-x-1.5">
                    <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                    <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                    <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                  </div>
                </div>
              </div>
            </div>
            <div class="px-6 py-4 border-t border-gray-100 bg-white flex-shrink-0">
              <div class="flex items-center space-x-2">
                <input
                  ref="aiInput"
                  v-model="aiInputText"
                  @keyup.enter="sendAiMessage"
                  type="text"
                  placeholder="描述您想要调整的内容..."
                  class="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                  :disabled="isAiTyping"
                />
                <button
                  @click="sendAiMessage"
                  :disabled="!aiInputText.trim() || isAiTyping"
                  class="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1.5"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                  </svg>
                  <span class="text-sm">发送</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 右侧：脑图预览区 -->
          <div class="w-1/2 flex flex-col">
            <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium text-gray-700">脑图预览</span>
                <span class="text-xs text-gray-400">版本 {{ activeMindMapVersionId }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <select
                  v-model="activeMindMapVersionId"
                  @change="switchMindMapVersion(activeMindMapVersionId)"
                  class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-600 outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option
                    v-for="v in mindMapVersions"
                    :key="v.id"
                    :value="v.id"
                  >v{{ v.id }} - {{ v.description }}</option>
                </select>
                <button
                  v-if="mindMapVersions.length > 0 && activeMindMapVersionId !== mindMapVersions[mindMapVersions.length - 1].id"
                  @click="restoreMindMapVersion(activeMindMapVersionId)"
                  class="px-2.5 py-1.5 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors flex items-center space-x-1"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  <span>恢复此版本</span>
                </button>
              </div>
            </div>
            <div class="px-4 py-2 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
              <span class="text-xs text-gray-400">{{ aiAdjustNodeType === 'requirement' ? '提示：右键测试点节点可标记保留' : '提示：右键测试用例节点可标记保留' }}</span>
              <span class="text-xs text-gray-400">
                {{ aiAdjustNodeType === 'requirement' ? `标记保留：${markedTestPointCount} 个测试点` : `标记保留：${markedTestCaseCount} 个测试用例` }}
              </span>
            </div>
            <div
              ref="aiMindMapContainer"
              class="flex-1 overflow-hidden relative bg-[#f0f4f8]"
              @contextmenu.prevent
            >
              <div v-if="!previewMindMapData" class="flex items-center justify-center h-full">
                <p class="text-sm text-gray-400">暂无脑图数据</p>
              </div>
            </div>

            <!-- 预览区右键菜单 -->
            <div
              v-if="previewContextMenu.visible"
              class="fixed bg-white rounded-lg shadow-xl border border-gray-200 py-1.5 z-[60] min-w-[160px] context-menu"
              :style="{ top: previewContextMenu.y + 'px', left: previewContextMenu.x + 'px' }"
            >
              <button @click="togglePreviewMark" class="context-menu-item">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                </svg>
                <span>{{ previewContextMenu.data && previewContextMenu.data._marked ? '取消标记保留' : '标记保留' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MindMap from 'simple-mind-map'
import { mockTestDesignAPI, buildCaseNote } from '../api/mock'

export default {
  name: 'TestDesign',

  data() {
    return {
      mindMap: null,
      searchKeyword: '',
      knowledgeBaseEnabled: false,
      isGenerating: false,
      isExporting: false,
      currentTaskId: null,
      pollTimer: null,
      progress: 0,
      progressText: '',
      zoomLevel: 1,
      activeRequirementId: null,
      activeRequirement: null,
      historyList: [],
      totalCount: 0,
      isLoadingList: false,
      loadError: '',
      activeStatusFilter: '',
      searchTimer: null,
      statusTabs: [
        { label: '全部', value: '' },
        { label: '待生成', value: 'pending' },
        { label: '生成中', value: 'generating' },
        { label: '已完成', value: 'completed' }
      ],
      contextMenu: {
        visible: false,
        x: 0,
        y: 0,
        type: '',
        node: null,
        smmNode: null
      },
      showAddTestPointDialog: false,
      newTestPointName: '',
      newTestPointDescription: '',
      addTestPointError: '',
      isAddingTestPoint: false,
      showEditTestPointDialog: false,
      editTestPointName: '',
      editTestPointDescription: '',
      editTestPointError: '',
      isEditingTestPoint: false,
      showDeleteTestPointDialog: false,
      isDeletingTestPoint: false,
      showAddTestCaseDialog: false,
      newTestCaseName: '',
      newTestCaseProperty: '正例',
      newTestCasePreCondition: '',
      newTestCaseSteps: [{ name: '', description: '', stepExpectedResult: '' }],
      addTestCaseError: '',
      isAddingTestCase: false,
      showDeleteTestCaseDialog: false,
      isDeletingTestCase: false,
      showEditTestCaseDialog: false,
      editTestCaseName: '',
      editTestCaseProperty: '正例',
      editTestCasePreCondition: '',
      editTestCaseSteps: [{ name: '', description: '', stepExpectedResult: '' }],
      editTestCaseError: '',
      isEditingTestCase: false,
      showAiAdjustDialog: false,
      aiSessionId: '',
      aiMessages: [],
      aiInputText: '',
      isAiTyping: false,
      aiAdjustNodeType: '',
      previewMindMap: null,
      previewMindMapData: null,
      mindMapVersions: [],
      activeMindMapVersionId: null,
      mindMapVersionCounter: 0,
      markedTestPointCount: 0,
      markedTestCaseCount: 0,
      previewContextMenu: {
        visible: false,
        x: 0,
        y: 0,
        node: null,
        data: null
      }
    }
  },

  computed: {
    filteredHistoryList() {
      return this.historyList
    }
  },

  mounted() {
    this.fetchRequirementList()
    document.addEventListener('click', this.hideContextMenu)
  },

  beforeDestroy() {
    document.removeEventListener('click', this.hideContextMenu)
    if (this.pollTimer) {
      clearInterval(this.pollTimer)
      this.pollTimer = null
    }
    if (this.mindMap) {
      this.mindMap.destroy()
      this.mindMap = null
    }
    if (this.previewMindMap) {
      this.previewMindMap.destroy()
      this.previewMindMap = null
    }
  },

  methods: {
    // ==================== 需求列表数据获取 ====================
    async fetchRequirementList() {
      this.isLoadingList = true
      this.loadError = ''
      try {
        const params = {
          keyword: this.searchKeyword || undefined,
          status: this.activeStatusFilter || undefined
        }
        const res = await mockTestDesignAPI.getRequirementList(params)
        if (res.success) {
          this.historyList = res.data.list
          this.totalCount = res.data.total
          if (!this.activeRequirementId && this.historyList.length > 0) {
            this.selectRequirement(this.historyList[0])
          }
        } else {
          this.loadError = res.message || '加载失败'
        }
      } catch (e) {
        this.loadError = '网络异常，请稍后重试'
      } finally {
        this.isLoadingList = false
      }
    },

    onSearchInput() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer)
      }
      this.searchTimer = setTimeout(() => {
        this.fetchRequirementList()
      }, 300)
    },

    filterByStatus(status) {
      if (this.activeStatusFilter === status) return
      this.activeStatusFilter = status
      this.fetchRequirementList()
    },

    // ==================== 需求选择 ====================
    async selectRequirement(item) {
      if (this.activeRequirementId === item.id) return
      this.activeRequirementId = item.id
      this.activeRequirement = item

      try {
        const res = await mockTestDesignAPI.getMindMapData(item.id)
        if (res.success) {
          this._mindMapData = res.data
        }
      } catch (e) {
        this._mindMapData = null
      }

      this.$nextTick(() => {
        this.initMindMap()
      })
    },

    // ==================== 脑图初始化 ====================
    initMindMap() {
      if (this.mindMap) {
        this.mindMap.destroy()
        this.mindMap = null
      }

      const container = this.$refs.mindMapContainer
      if (!container) return

      const mindMapData = this.buildMindMapData()

      const noteShow = (content, left, top) => {
        const el = document.getElementById('custom-note-popover')
        if (!el) return null
        el.style.left = `${left}px`
        el.style.top = `${top}px`
        el.innerHTML = content
        el.style.display = 'block'
        return el
      }
      const noteHide = () => {
        const el = document.getElementById('custom-note-popover')
        if (el) el.style.display = 'none'
      }
      this._noteShow = noteShow
      this._noteHide = noteHide

      this.mindMap = new MindMap({
        el: container,
        data: mindMapData,
        layout: 'mindMap',
        readonly: false,
        themeConfig: this.getThemeConfig(),
        initRootNodePosition: ['20%', '50%'],
        textAutoWrapWidth: 500,
        mousewheelAction: 'zoom',
        defaultInsertSecondLevelNodeText: '分支需求',
        defaultInsertBelowSecondLevelNodeText: '分支主题',
        alwaysShowExpandBtn: true,
        isShowCreateChildBtnIcon: false,
        isUseCustomNodeContent: true,
        customCreateNodeContent: (node) => {
          return this.createCustomNodeContent(node)
        },
        customNoteContentShow: {
          show: noteShow,
          hide: noteHide
        },
        beforeShortcutRun: (key, activeNodes) => {
          if (activeNodes && activeNodes.length > 0) {
            const activeNode = activeNodes[0]
            if (this.getNodeLevel(activeNode) === 'testCase') {
              if (key === 'Tab' || key === 'Insert' || key === 'Enter') {
                return true
              }
            }
          }
          return false
        }
      })

      this.patchRootExpandBtn()
      this.bindMindMapEvents()
    },

    patchRootExpandBtn() {
      const rootNode = this.mindMap.renderer.root
      if (!rootNode) return
      const origRender = rootNode.renderExpandBtn
      rootNode.renderExpandBtn = function () {
        if (this.getChildrenLength() <= 0) return
        const wasRoot = this.isRoot
        this.isRoot = false
        origRender.call(this)
        this.isRoot = wasRoot
      }
      rootNode.renderExpandBtn()
    },

    // ==================== 自定义节点内容 ====================
    createCustomNodeContent(node) {
      const data = node.getData()
      const level = this.getNodeLevel(node)
      const wrapper = document.createElement('div')

      switch (level) {
        case 'root':
          return this.createRootNodeContent(wrapper, data)
        case 'requirement':
          return this.createRequirementNodeContent(wrapper, data)
        case 'testPoint':
          return this.createTestPointNodeContent(wrapper, data)
        case 'testCase':
          return this.createTestCaseNodeContent(wrapper, data)
        default:
          wrapper.textContent = data.text || ''
          return wrapper
      }
    },

    createRootNodeContent(wrapper, data) {
      wrapper.style.cssText = `
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 14px 20px;
        border-radius: 12px;
        min-width: 180px;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      `
      const title = document.createElement('div')
      title.style.cssText = 'font-size:15px;font-weight:700;line-height:1.4;margin-bottom:8px;'
      title.textContent = data.text || ''

      const status = document.createElement('span')
      const statusText = data._status === 'completed' ? '已完成' : data._status === 'generating' ? '生成中' : '待生成'
      const statusBg = data._status === 'completed' ? 'rgba(255,255,255,0.25)' : data._status === 'generating' ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.15)'
      status.style.cssText = `
        display:inline-block;font-size:11px;padding:2px 10px;border-radius:10px;
        background:${statusBg};color:#fff;font-weight:500;letter-spacing:0.5px;
      `
      status.textContent = statusText

      wrapper.appendChild(title)
      wrapper.appendChild(status)
      return wrapper
    },

    createRequirementNodeContent(wrapper, data) {
      wrapper.style.cssText = `
        background: #eff6ff;
        padding: 10px 16px 12px 16px;
        border-radius: 10px;
        border: 1.5px solid #bfdbfe;
        min-width: 200px;
        max-width: 320px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 1px 3px rgba(59, 130, 246, 0.08);
      `
      const typeLabel = document.createElement('div')
      typeLabel.style.cssText = `
        display:inline-block;font-size:10px;font-weight:600;color:#3b82f6;
        background:#dbeafe;padding:1px 8px;border-radius:3px;margin-bottom:6px;
        letter-spacing:0.5px;
      `
      typeLabel.textContent = '需求'

      const header = document.createElement('div')
      header.style.cssText = 'display:flex;align-items:flex-start;justify-content:space-between;gap:8px;'

      const text = document.createElement('div')
      text.style.cssText = 'font-size:13px;font-weight:600;color:#1e40af;line-height:1.5;flex:1;word-break:break-all;'
      text.textContent = data.text || ''

      const statusDot = document.createElement('span')
      const dotColor = data._status === 'completed' ? '#22c55e' : data._status === 'generating' ? '#f59e0b' : '#d1d5db'
      statusDot.style.cssText = `
        flex-shrink:0;width:8px;height:8px;border-radius:50%;background:${dotColor};
        margin-top:4px;box-shadow:0 0 0 3px ${dotColor}22;
      `

      header.appendChild(text)
      header.appendChild(statusDot)
      wrapper.appendChild(typeLabel)
      wrapper.appendChild(header)
      return wrapper
    },

    createTestPointNodeContent(wrapper, data) {
      wrapper.style.cssText = `
        position:relative;
        background: #f0fdf4;
        padding: 10px 16px 12px 16px;
        border-radius: 10px;
        border: 1.5px solid #bbf7d0;
        min-width: 180px;
        max-width: 300px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 1px 3px rgba(34, 197, 94, 0.06);
      `

      if (data._marked) {
        const pinIcon = document.createElement('span')
        pinIcon.style.cssText = `
          position:absolute;top:2px;left:2px;font-size:14px;
          filter:drop-shadow(0 1px 2px rgba(245,158,11,0.4));
        `
        pinIcon.textContent = '📌'
        wrapper.appendChild(pinIcon)
      }

      const typeLabel = document.createElement('div')
      typeLabel.style.cssText = `
        display:inline-block;font-size:10px;font-weight:600;color:#16a34a;
        background:#dcfce7;padding:1px 8px;border-radius:3px;margin-bottom:6px;
        letter-spacing:0.5px;
      `
      typeLabel.textContent = '测试点'

      const header = document.createElement('div')
      header.style.cssText = 'display:flex;align-items:flex-start;justify-content:space-between;gap:6px;margin-bottom:8px;'

      const text = document.createElement('div')
      text.style.cssText = 'font-size:13px;font-weight:600;color:#166534;line-height:1.5;flex:1;word-break:break-all;'
      text.textContent = data.text || ''

      const statusDot = document.createElement('span')
      const dotColor = data._status === 'completed' ? '#22c55e' : data._status === 'generating' ? '#f59e0b' : '#d1d5db'
      statusDot.style.cssText = `
        flex-shrink:0;width:8px;height:8px;border-radius:50%;background:${dotColor};
        margin-top:4px;box-shadow:0 0 0 3px ${dotColor}22;
      `

      header.appendChild(text)
      header.appendChild(statusDot)

      const footer = document.createElement('div')
      footer.style.cssText = 'display:flex;align-items:center;gap:6px;'

      const sourceBadge = document.createElement('span')
      const isAI = data._source === 'AI'
      sourceBadge.style.cssText = `
        display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:600;
        padding:2px 8px;border-radius:4px;
        background:${isAI ? '#fef3c7' : '#f3e8ff'};
        color:${isAI ? '#92400e' : '#6b21a8'};
      `
      sourceBadge.innerHTML = `${isAI ? '🤖' : '✍️'} ${data._source || 'AI'}`

      footer.appendChild(sourceBadge)

      wrapper.appendChild(typeLabel)
      wrapper.appendChild(header)
      wrapper.appendChild(footer)
      return wrapper
    },

    createTestCaseNodeContent(wrapper, data) {
      wrapper.style.cssText = `
        position:relative;
        background: #ffffff;
        padding: 10px 16px 12px 16px;
        border-radius: 10px;
        border: 1.5px solid #e5e7eb;
        min-width: 200px;
        max-width: 320px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
      `

      if (data._marked) {
        const pinIcon = document.createElement('span')
        pinIcon.style.cssText = `
          position:absolute;top:2px;left:2px;font-size:14px;
          filter:drop-shadow(0 1px 2px rgba(245,158,11,0.4));
        `
        pinIcon.textContent = '📌'
        wrapper.appendChild(pinIcon)
      }

      const typeLabel = document.createElement('div')
      typeLabel.style.cssText = `
        display:inline-block;font-size:10px;font-weight:600;color:#6b7280;
        background:#f3f4f6;padding:1px 8px;border-radius:3px;margin-bottom:6px;
        letter-spacing:0.5px;
      `
      typeLabel.textContent = '测试用例'

      const header = document.createElement('div')
      header.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:6px;'

      const propBadge = document.createElement('span')
      const isPositive = data._caseProperty === '正例'
      propBadge.style.cssText = `
        flex-shrink:0;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;
        background:${isPositive ? '#dcfce7' : '#fee2e2'};
        color:${isPositive ? '#166534' : '#991b1b'};
      `
      propBadge.textContent = data._caseProperty || '正例'

      const name = document.createElement('span')
      name.style.cssText = 'font-size:13px;font-weight:600;color:#1f2937;line-height:1.4;flex:1;word-break:break-all;'
      name.textContent = data.text || ''

      header.appendChild(propBadge)
      header.appendChild(name)

      const meta = document.createElement('div')
      meta.style.cssText = 'display:flex;align-items:center;gap:6px;'

      const sourceBadge = document.createElement('span')
      const isAI = data._source === 'AI'
      sourceBadge.style.cssText = `
        display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:600;
        padding:2px 8px;border-radius:4px;
        background:${isAI ? '#fef3c7' : '#f3e8ff'};
        color:${isAI ? '#92400e' : '#6b21a8'};
      `
      sourceBadge.innerHTML = `${isAI ? '🤖' : '✍️'} ${data._source || 'AI'}`

      meta.appendChild(sourceBadge)

      if (data.note) {
        const noteBtn = document.createElement('span')
        noteBtn.style.cssText = `
          display:inline-flex;align-items:center;gap:2px;font-size:10px;font-weight:500;
          padding:2px 8px;border-radius:4px;cursor:pointer;
          background:#eff6ff;color:#3b82f6;
          transition:background 0.15s;flex-shrink:0;
        `
        noteBtn.innerHTML = '📋 详情'
        noteBtn.title = '查看用例详情'

        const vm = this
        noteBtn.addEventListener('mouseenter', (e) => {
          e.stopPropagation()
          const rect = wrapper.getBoundingClientRect()
          if (vm._noteShow) {
            vm._noteShow(data.note, rect.right + 8, rect.top)
          }
        })
        noteBtn.addEventListener('mouseleave', (e) => {
          e.stopPropagation()
          if (vm._noteHide) {
            vm._noteHide()
          }
        })

        meta.appendChild(noteBtn)
      }

      wrapper.appendChild(typeLabel)
      wrapper.appendChild(header)
      wrapper.appendChild(meta)
      return wrapper
    },

    buildMindMapData() {
      if (this._mindMapData) {
        return JSON.parse(JSON.stringify(this._mindMapData))
      }

      const req = this.activeRequirement
      if (!req) return { data: { text: '根节点' }, children: [] }

      return {
        data: { text: req.title, expand: true, _level: 'root', _status: req.status },
        children: []
      }
    },

    getThemeConfig() {
      return {
        backgroundColor: '#f9fafb',
        lineColor: '#cbd5e1',
        lineWidth: 2,
        lineStyle: 'straight',
        paddingX: 0,
        paddingY: 0,
        root: {
          fillColor: 'transparent',
          color: '#ffffff',
          fontSize: 14,
          fontWeight: 'bold',
          borderRadius: 0,
          paddingX: 0,
          paddingY: 0,
          borderWidth: 0,
          borderColor: 'transparent'
        },
        second: {
          fillColor: 'transparent',
          color: '#1e40af',
          fontSize: 13,
          fontWeight: '600',
          borderRadius: 0,
          paddingX: 0,
          paddingY: 0,
          borderWidth: 0,
          borderColor: 'transparent'
        },
        node: {
          fillColor: 'transparent',
          color: '#166534',
          fontSize: 13,
          fontWeight: '500',
          borderRadius: 0,
          paddingX: 0,
          paddingY: 0,
          borderWidth: 0,
          borderColor: 'transparent'
        }
      }
    },

    // ==================== 事件绑定 ====================
    bindMindMapEvents() {
      if (!this.mindMap) return

      this.mindMap.on('node_contextmenu', (e, node) => {
        e.preventDefault()
        this.handleNodeContextMenu(e, node)
      })

      this.mindMap.on('node_dblclick', (node) => {
        this.handleNodeDblClick(node)
      })

      this.mindMap.on('scale', (scale) => {
        this.zoomLevel = scale
      })

      this.mindMap.on('draw_click', () => {
        this.hideContextMenu()
      })

      this.mindMap.on('node_click', () => {
        this.hideContextMenu()
      })

      this.mindMap.on('node_tree_render_end', () => {
        this.$nextTick(() => {
          this.patchRootExpandBtn()
        })
      })

      this.mindMap.on('data_change', (data) => {
        this.enforceMaxLevel(data)
      })
    },

    enforceMaxLevel(data) {
      const checkAndRemove = (node, depth = 0) => {
        if (!node || !node.data) return
        const level = node.data._level || this.getLevelByDepth(depth)
        if (level === 'testCase' && node.children && node.children.length > 0) {
          node.children = []
        }
        if (node.children) {
          node.children.forEach(child => checkAndRemove(child, depth + 1))
        }
      }
      checkAndRemove(data, 0)
    },

    getLevelByDepth(depth) {
      if (depth <= 0) return 'root'
      if (depth === 1) return 'requirement'
      if (depth === 2) return 'testPoint'
      return 'testCase'
    },

    handleNodeContextMenu(e, node) {
      const level = this.getNodeLevel(node)
      const customData = this.getNodeCustomData(node)

      this.contextMenu = {
        visible: true,
        x: e.clientX + 5,
        y: e.clientY + 5,
        type: level,
        node: customData,
        smmNode: node
      }
    },

    handleNodeDblClick(node) {
      const level = this.getNodeLevel(node)
      if (level === 'testPoint' || level === 'testCase') {
        const customData = this.getNodeCustomData(node)
        this.contextMenu = {
          visible: false,
          x: 0,
          y: 0,
          type: level,
          node: customData,
          smmNode: node
        }
        if (level === 'testPoint') {
          this.editTestPoint()
        } else {
          this.editTestCaseDialog()
        }
      }
    },

    getNodeLevel(node) {
      if (node.isRoot) return 'root'
      const parent = node.parent
      if (parent && parent.isRoot) return 'requirement'
      if (parent && parent.parent && parent.parent.isRoot) return 'testPoint'
      return 'testCase'
    },

    getNodeCustomData(node) {
      const data = node.getData()
      return {
        text: data.text,
        level: data._level,
        status: data._status,
        source: data._source,
        marked: data._marked,
        caseProperty: data._caseProperty
      }
    },

    // ==================== 缩放控制 ====================
    zoomIn() {
      if (this.mindMap) {
        const current = this.mindMap.view.scale || 1
        this.mindMap.view.setScale(Math.min(current + 0.1, 2))
      }
    },

    zoomOut() {
      if (this.mindMap) {
        const current = this.mindMap.view.scale || 1
        this.mindMap.view.setScale(Math.max(current - 0.1, 0.3))
      }
    },

    fitCanvas() {
      if (this.mindMap) {
        this.mindMap.view.fit()
      }
    },

    // ==================== 右键菜单操作 ====================
    hideContextMenu() {
      this.contextMenu.visible = false
    },

    addTestPoint() {
      this.hideContextMenu()
      this.newTestPointName = ''
      this.addTestPointError = ''
      this.showAddTestPointDialog = true
      this.$nextTick(() => {
        if (this.$refs.testPointInput) {
          this.$refs.testPointInput.focus()
        }
      })
    },

    closeAddTestPointDialog() {
      this.showAddTestPointDialog = false
      this.newTestPointName = ''
      this.addTestPointError = ''
    },

    async confirmAddTestPoint() {
      const name = this.newTestPointName.trim()
      if (!name) {
        this.addTestPointError = '请输入测试点名称'
        return
      }
      if (name.length > 100) {
        this.addTestPointError = '测试点名称不能超过100个字符'
        return
      }

      this.isAddingTestPoint = true
      this.addTestPointError = ''

      try {
        const res = await mockTestDesignAPI.addTestPoint(this.activeRequirementId, {
          requirementNodeId: this.activeRequirementId,
          text: name,
          description: this.newTestPointDescription.trim()
        })

        if (res.success) {
          const smmNode = this.contextMenu.smmNode
          if (smmNode && this.mindMap) {
            const newNodeData = {
              data: {
                text: name,
                expand: true,
                _level: 'testPoint',
                _status: 'completed',
                _source: '人工',
                _marked: false
              },
              children: []
            }
            smmNode.appendChild(newNodeData)
            this.mindMap.render()
            this.mindMap.view.fit()
          }
          this.closeAddTestPointDialog()
        } else {
          this.addTestPointError = res.message || '添加失败，请重试'
        }
      } catch (e) {
        this.addTestPointError = '网络异常，请稍后重试'
      } finally {
        this.isAddingTestPoint = false
      }
    },

    aiAdjust() {
      this.hideContextMenu()
      this.aiAdjustNodeType = this.contextMenu.type
      this.aiMessages = []
      this.aiInputText = ''
      this.isAiTyping = false
      this.showAiAdjustDialog = true
      this.initAiSession()
    },

    async initAiSession() {
      const markedNodeIds = this.collectMarkedNodeIds()
      const nodeId = this.aiAdjustNodeType === 'testPoint' && this.contextMenu.smmNode
        ? this.contextMenu.smmNode.getData().text
        : this.activeRequirementId

      try {
        const res = await mockTestDesignAPI.createAiSession({
          requirementId: this.activeRequirementId,
          nodeId: nodeId,
          nodeType: this.aiAdjustNodeType,
          markedNodeIds
        })

        if (res.success) {
          this.aiSessionId = res.data.sessionId
          this.aiMessages = res.data.messages || []

          this.mindMapVersionCounter = 1
          const snapshot = this.getMindMapSnapshot()
          this.mindMapVersions = [{
            id: this.mindMapVersionCounter,
            data: JSON.parse(JSON.stringify(snapshot)),
            timestamp: this.formatTime(new Date()),
            description: '初始版本'
          }]
          this.activeMindMapVersionId = this.mindMapVersionCounter
          this.previewMindMapData = JSON.parse(JSON.stringify(snapshot))
          this.updateMarkedCount()

          this.$nextTick(() => {
            this.scrollAiChatToBottom()
            this.initPreviewMindMap()
          })
        }
      } catch (e) {
        this.aiMessages = [{
          id: 'error-1',
          role: 'assistant',
          content: '连接AI助手失败，请稍后重试。',
          timestamp: new Date().toISOString()
        }]
      }
    },

    closeAiAdjustDialog() {
      if (this.previewMindMap) {
        this.previewMindMap.destroy()
        this.previewMindMap = null
      }
      this.showAiAdjustDialog = false
      this.aiSessionId = ''
      this.aiMessages = []
      this.aiInputText = ''
      this.isAiTyping = false
      this.aiAdjustNodeType = ''
      this.previewMindMapData = null
      this.mindMapVersions = []
      this.activeMindMapVersionId = null
      this.mindMapVersionCounter = 0
      this.markedTestPointCount = 0
      this.markedTestCaseCount = 0
    },

    async sendAiMessage() {
      const text = this.aiInputText.trim()
      if (!text || this.isAiTyping) return

      const userMsg = {
        id: `msg-user-${Date.now()}`,
        role: 'user',
        content: text,
        timestamp: new Date().toISOString()
      }
      this.aiMessages.push(userMsg)
      this.aiInputText = ''
      this.isAiTyping = true

      this.$nextTick(() => {
        this.scrollAiChatToBottom()
      })

      try {
        const res = await mockTestDesignAPI.sendAiMessage(this.aiSessionId, {
          message: text
        })

        if (res.success) {
          this.aiMessages.push(res.data)
        }
      } catch (e) {
        this.aiMessages.push({
          id: `msg-error-${Date.now()}`,
          role: 'assistant',
          content: '消息发送失败，请重试。',
          timestamp: new Date().toISOString()
        })
      } finally {
        this.isAiTyping = false
        this.$nextTick(() => {
          this.scrollAiChatToBottom()
          if (this.$refs.aiInput) {
            this.$refs.aiInput.focus()
          }
        })
      }
    },

    scrollAiChatToBottom() {
      const container = this.$refs.aiChatContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },

    sendQuickAiMessage(text) {
      this.aiInputText = text
      this.sendAiMessage()
    },

    collectMarkedNodeIds() {
      const ids = []
      const targetLevel = this.aiAdjustNodeType === 'testPoint' ? 'testCase' : 'testPoint'
      const traverse = (node) => {
        if (node.data && node.data._marked && node.data._level === targetLevel) {
          ids.push(node.data.text)
        }
        if (node.children) {
          node.children.forEach(child => traverse(child))
        }
      }
      if (this.mindMap && this.mindMap.getData) {
        traverse(this.mindMap.getData())
      }
      return ids
    },

    getMindMapSnapshot() {
      if (this.mindMap && this.mindMap.getData) {
        return this.mindMap.getData()
      }
      return this.buildMindMapData()
    },

    updateMarkedCount() {
      let tpCount = 0
      let tcCount = 0
      const traverse = (node) => {
        if (node.data && node.data._marked) {
          if (node.data._level === 'testPoint') tpCount++
          if (node.data._level === 'testCase') tcCount++
        }
        if (node.children) {
          node.children.forEach(child => traverse(child))
        }
      }
      const sourceData = (this.previewMindMap && this.previewMindMap.getData)
        ? this.previewMindMap.getData()
        : this.previewMindMapData
      if (sourceData) {
        traverse(sourceData)
      }
      this.markedTestPointCount = tpCount
      this.markedTestCaseCount = tcCount
    },

    initPreviewMindMap() {
      if (this.previewMindMap) {
        this.previewMindMap.destroy()
        this.previewMindMap = null
      }

      const container = this.$refs.aiMindMapContainer
      if (!container || !this.previewMindMapData) return

      const previewData = this.transformPreviewData(
        JSON.parse(JSON.stringify(this.previewMindMapData))
      )

      this.previewMindMap = new MindMap({
        el: container,
        data: previewData,
        layout: 'mindMap',
        readonly: false,
        enableNodeDrag: false,
        beforeShortcutRun: () => true,
        themeConfig: {
          backgroundColor: '#f0f4f8',
          lineColor: '#cbd5e1',
          lineWidth: 2,
          lineStyle: 'straight',
          paddingX: 0,
          paddingY: 0,
          root: {
            fillColor: 'transparent',
            color: '#1e40af',
            fontSize: 13,
            fontWeight: 'bold',
            borderRadius: 0,
            paddingX: 0,
            paddingY: 0,
            borderWidth: 0,
            borderColor: 'transparent'
          },
          second: {
            fillColor: 'transparent',
            color: '#1e40af',
            fontSize: 12,
            fontWeight: '600',
            borderRadius: 0,
            paddingX: 0,
            paddingY: 0,
            borderWidth: 0,
            borderColor: 'transparent'
          },
          node: {
            fillColor: 'transparent',
            color: '#166534',
            fontSize: 12,
            fontWeight: '500',
            borderRadius: 0,
            paddingX: 0,
            paddingY: 0,
            borderWidth: 0,
            borderColor: 'transparent'
          }
        },
        initRootNodePosition: ['15%', '50%'],
        mousewheelAction: 'zoom',
        alwaysShowExpandBtn: true,
        isShowCreateChildBtnIcon: false,
        isUseCustomNodeContent: true,
        customCreateNodeContent: (node) => {
          return this.createPreviewNodeContent(node)
        }
      })

      this.previewMindMap.on('node_contextmenu', (e, node) => {
        e.preventDefault()
        this.handlePreviewContextMenu(e, node)
      })

      this.previewMindMap.on('draw_click', () => {
        this.hidePreviewContextMenu()
      })

      this.previewMindMap.on('node_click', () => {
        this.hidePreviewContextMenu()
      })

      this.$nextTick(() => {
        setTimeout(() => {
          this.hideRootConnections()
        }, 100)
      })
    },

    hideRootConnections() {
      const container = this.$refs.aiMindMapContainer
      if (!container || !this.previewMindMap) return

      const svg = container.querySelector('svg')
      if (!svg) return

      const rootData = this.previewMindMap.getData()
      const reqCount = (rootData && rootData.children) ? rootData.children.length : 0

      const paths = svg.querySelectorAll('path')
      for (let i = 0; i < Math.min(reqCount, paths.length); i++) {
        paths[i].setAttribute('display', 'none')
      }

      const nodeGroups = svg.querySelectorAll('g[data-uid]')
      if (nodeGroups.length > 0) {
        nodeGroups[0].setAttribute('display', 'none')
      }

      this.previewMindMap.view.fit()
    },

    transformPreviewData(rootNode) {
      if (!rootNode) return null

      if (this.aiAdjustNodeType === 'testPoint') {
        const targetTpText = this.contextMenu.node ? this.contextMenu.node.text : ''
        let targetTp = null
        const findTestPoint = (node) => {
          if (node.data && node.data._level === 'testPoint' && node.data.text === targetTpText) {
            targetTp = node
            return
          }
          if (node.children) {
            node.children.forEach(child => findTestPoint(child))
          }
        }
        findTestPoint(rootNode)

        if (!targetTp) {
          return {
            data: { text: '', _level: 'previewRoot' },
            children: []
          }
        }

        return {
          data: {
            text: '',
            _level: 'previewRoot'
          },
          children: [{
            data: { ...targetTp.data },
            children: (targetTp.children || [])
              .filter(child => child.data && child.data._level === 'testCase')
              .map(tc => ({
                data: { ...tc.data },
                children: []
              }))
          }]
        }
      }

      const requirements = (rootNode.children || []).filter(
        child => child.data && child.data._level === 'requirement'
      )

      const newRoot = {
        data: {
          text: '',
          _level: 'previewRoot'
        },
        children: requirements.map(req => ({
          data: { ...req.data },
          children: (req.children || [])
            .filter(child => child.data && child.data._level === 'testPoint')
            .map(tp => ({
              data: { ...tp.data },
              children: []
            }))
        }))
      }

      return newRoot
    },

    stripTestCaseNodes(node) {
      if (!node) return node
      if (node.children && node.children.length > 0) {
        node.children = node.children.map(child => {
          const cloned = this.stripTestCaseNodes(child)
          if (cloned.data && cloned.data._level === 'testPoint') {
            cloned.children = []
          }
          return cloned
        })
      }
      return node
    },

    createPreviewNodeContent(node) {
      const data = node.getData()
      const level = data._level
      const wrapper = document.createElement('div')

      if (level === 'root') {
        wrapper.style.cssText = `
          background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
          color: #fff; padding: 10px 16px; border-radius: 10px;
          min-width: 140px; font-size: 13px; font-weight: 700;
          box-shadow: 0 2px 8px rgba(37,99,235,0.3);
        `
        wrapper.textContent = data.text || ''
      } else if (level === 'previewRoot') {
        wrapper.style.cssText = 'display:none;'
      } else if (level === 'requirement') {
        wrapper.style.cssText = `
          background: #eff6ff; padding: 8px 14px; border-radius: 8px;
          border: 1.5px solid #bfdbfe; min-width: 160px; max-width: 260px;
          font-size: 12px; font-weight: 600; color: #1e40af;
        `
        wrapper.textContent = data.text || ''
      } else if (level === 'testPoint') {
        wrapper.style.cssText = `
          position:relative; background: #f0fdf4; padding: 8px 14px;
          border-radius: 8px; border: 1.5px solid #bbf7d0;
          min-width: 140px; max-width: 240px; font-size: 12px;
          font-weight: 600; color: #166534;
        `
        if (data._marked) {
          const pin = document.createElement('span')
          pin.style.cssText = 'position:absolute;top:2px;left:2px;font-size:12px;'
          pin.textContent = '📌'
          wrapper.appendChild(pin)
        }
        const textEl = document.createElement('span')
        textEl.textContent = data.text || ''
        wrapper.appendChild(textEl)
      } else if (level === 'testCase') {
        wrapper.style.cssText = `
          position:relative; background: #ffffff; padding: 8px 14px;
          border-radius: 8px; border: 1.5px solid #e5e7eb;
          min-width: 140px; max-width: 260px; font-size: 12px;
          font-weight: 600; color: #1f2937;
        `
        if (data._marked) {
          const pin = document.createElement('span')
          pin.style.cssText = 'position:absolute;top:2px;left:2px;font-size:12px;'
          pin.textContent = '📌'
          wrapper.appendChild(pin)
        }
        const propBadge = document.createElement('span')
        const isPositive = data._caseProperty === '正例'
        propBadge.style.cssText = `
          display:inline-block;font-size:10px;font-weight:700;padding:1px 6px;border-radius:3px;
          margin-right:6px;background:${isPositive ? '#dcfce7' : '#fee2e2'};
          color:${isPositive ? '#166534' : '#991b1b'};
        `
        propBadge.textContent = data._caseProperty || '正例'
        wrapper.appendChild(propBadge)
        const textEl = document.createElement('span')
        textEl.textContent = data.text || ''
        wrapper.appendChild(textEl)
      } else {
        wrapper.textContent = data.text || ''
      }

      return wrapper
    },

    handlePreviewContextMenu(e, node) {
      const data = node.getData()
      const allowedLevel = this.aiAdjustNodeType === 'testPoint' ? 'testCase' : 'testPoint'
      if (data._level !== allowedLevel) return

      const rect = this.$refs.aiMindMapContainer.getBoundingClientRect()
      this.previewContextMenu = {
        visible: true,
        x: e.clientX,
        y: e.clientY,
        node: node,
        data: data
      }
    },

    hidePreviewContextMenu() {
      if (this.previewContextMenu) {
        this.previewContextMenu.visible = false
      }
    },

    togglePreviewMark() {
      if (!this.previewContextMenu || !this.previewContextMenu.node) return

      const node = this.previewContextMenu.node
      const data = node.getData()
      data._marked = !data._marked

      if (this.mindMap && this.mindMap.getData) {
        const mainRoot = this.mindMap.getData()
        const previewRoot = this.previewMindMap.getData()
        if (mainRoot && previewRoot) {
          if (this.aiAdjustNodeType === 'testPoint') {
            const targetTpText = this.contextMenu.node ? this.contextMenu.node.text : ''
            const findAndSync = (node) => {
              if (node.data && node.data._level === 'testPoint' && node.data.text === targetTpText && node.children) {
                const previewTp = (previewRoot.children || [])[0]
                if (!previewTp) return
                const previewTcs = previewTp.children || []
                previewTcs.forEach((previewTc) => {
                  const pData = previewTc.data
                  if (pData._level === 'testCase' && pData.text === data.text) {
                    const mainTc = node.children.find(c => c.data && c.data._level === 'testCase' && c.data.text === data.text)
                    if (mainTc) {
                      mainTc.data._marked = data._marked
                    }
                  }
                })
                return
              }
              if (node.children) {
                node.children.forEach(child => findAndSync(child))
              }
            }
            findAndSync(mainRoot)
          } else {
            const mainReqs = mainRoot.children || []
            const previewReqs = previewRoot.children || []
            previewReqs.forEach((previewReq, i) => {
              const mainReq = mainReqs[i]
              if (!mainReq) return
              const previewTps = previewReq.children || []
              const mainTps = mainReq.children || []
              previewTps.forEach((previewTp, j) => {
                const mainTp = mainTps[j]
                if (!mainTp) return
                const pData = previewTp.data
                if (pData._level === 'testPoint' && pData.text === data.text) {
                  mainTp.data._marked = data._marked
                }
              })
            })
          }
        }
        this.mindMap.render()
      }

      this.previewMindMap.render()
      this.updateMarkedCount()
      this.hidePreviewContextMenu()
    },

    saveMindMapVersion(description) {
      this.mindMapVersionCounter++
      const snapshot = this.getMindMapSnapshot()
      this.mindMapVersions.push({
        id: this.mindMapVersionCounter,
        data: JSON.parse(JSON.stringify(snapshot)),
        timestamp: this.formatTime(new Date()),
        description
      })
      this.activeMindMapVersionId = this.mindMapVersionCounter
      this.previewMindMapData = JSON.parse(JSON.stringify(snapshot))
      this.updateMarkedCount()
      this.$nextTick(() => {
        this.initPreviewMindMap()
      })
    },

    switchMindMapVersion(versionId) {
      this.activeMindMapVersionId = versionId
      const version = this.mindMapVersions.find(v => v.id === versionId)
      if (version) {
        this.previewMindMapData = JSON.parse(JSON.stringify(version.data))
        this.updateMarkedCount()
        this.$nextTick(() => {
          this.initPreviewMindMap()
        })
      }
    },

    restoreMindMapVersion(versionId) {
      const version = this.mindMapVersions.find(v => v.id === versionId)
      if (!version) return

      if (this.mindMap) {
        this.mindMap.setData(JSON.parse(JSON.stringify(version.data)))
        this.mindMap.render()
        this.mindMap.view.fit()
      }

      this.saveMindMapVersion(`恢复自版本 ${versionId}`)
    },

    async confirmAiProposal(index) {
      const msg = this.aiMessages[index]
      if (!msg) return
      msg.confirmed = true
      msg.rejected = false

      const markedNodeIds = this.collectMarkedNodeIds()
      const currentMindMapData = this.getMindMapSnapshot()
      const isTestPointLevel = this.aiAdjustNodeType === 'testPoint'
      const markLabel = isTestPointLevel ? '测试用例' : '测试点'

      this.isAiTyping = true
      this.aiMessages.push({
        id: `msg-system-${Date.now()}`,
        role: 'assistant',
        content: `⏳ 正在应用AI调整，保留标记的${markLabel}...`,
        type: 'system',
        timestamp: new Date().toISOString()
      })
      this.$nextTick(() => this.scrollAiChatToBottom())

      try {
        const res = await mockTestDesignAPI.applyAiAdjustment(this.aiSessionId, {
          currentMindMapData,
          markedTestPointTexts: markedNodeIds,
          nodeType: this.aiAdjustNodeType
        })

        if (res.success && res.data.adjustedMindMapData && this.mindMap) {
          this.mindMap.setData(JSON.parse(JSON.stringify(res.data.adjustedMindMapData)))
          this.mindMap.render()
          this.mindMap.view.fit()

          const nodeLabel = isTestPointLevel ? '测试用例' : '测试点'
          this.aiMessages.push({
            id: `msg-result-${Date.now()}`,
            role: 'assistant',
            content: `✅ AI调整已完成！\n\n- 新增${nodeLabel}：${res.data.addedCount} 个\n- 保留标记${nodeLabel}：${res.data.preservedCount} 个\n- 移除${nodeLabel}：${res.data.removedCount} 个\n\n脑图已更新，您可以在右侧预览区查看最新结果。`,
            timestamp: new Date().toISOString()
          })

          this.saveMindMapVersion('采纳AI建议')
        } else {
          this.aiMessages.push({
            id: `msg-error-${Date.now()}`,
            role: 'assistant',
            content: '❌ AI调整失败，请重试。',
            timestamp: new Date().toISOString()
          })
        }
      } catch (e) {
        this.aiMessages.push({
          id: `msg-error-${Date.now()}`,
          role: 'assistant',
          content: '❌ 网络异常，AI调整失败，请重试。',
          timestamp: new Date().toISOString()
        })
      } finally {
        this.isAiTyping = false
        this.$nextTick(() => this.scrollAiChatToBottom())
      }
    },

    rejectAiProposal(index) {
      const msg = this.aiMessages[index]
      if (!msg) return
      msg.rejected = true
      msg.confirmed = false
    },

    formatAiMessage(content) {
      if (!content) return ''
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/^- (.*?)$/gm, '• $1')
    },

    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    },

    editTestPoint() {
      this.hideContextMenu()
      if (this.contextMenu.node) {
        this.editTestPointName = this.contextMenu.node.text || ''
        this.editTestPointDescription = ''
      }
      this.editTestPointError = ''
      this.showEditTestPointDialog = true
      this.$nextTick(() => {
        if (this.$refs.editTestPointInput) {
          this.$refs.editTestPointInput.focus()
        }
      })
    },

    closeEditTestPointDialog() {
      this.showEditTestPointDialog = false
      this.editTestPointName = ''
      this.editTestPointDescription = ''
      this.editTestPointError = ''
    },

    async confirmEditTestPoint() {
      const name = this.editTestPointName.trim()
      if (!name) {
        this.editTestPointError = '请输入测试点名称'
        return
      }
      if (name.length > 100) {
        this.editTestPointError = '测试点名称不能超过100个字符'
        return
      }

      this.isEditingTestPoint = true
      this.editTestPointError = ''

      try {
        const res = await mockTestDesignAPI.editTestPoint(this.activeRequirementId, {
          text: name,
          description: this.editTestPointDescription.trim()
        })

        if (res.success) {
          const smmNode = this.contextMenu.smmNode
          if (smmNode && this.mindMap) {
            const nodeData = smmNode.getData()
            nodeData.text = name
            smmNode.setData(nodeData)
            this.mindMap.render()
            this.mindMap.view.fit()
          }
          this.closeEditTestPointDialog()
        } else {
          this.editTestPointError = res.message || '保存失败，请重试'
        }
      } catch (e) {
        this.editTestPointError = '网络异常，请稍后重试'
      } finally {
        this.isEditingTestPoint = false
      }
    },

    deleteTestPoint() {
      this.hideContextMenu()
      this.showDeleteTestPointDialog = true
    },

    closeDeleteTestPointDialog() {
      this.showDeleteTestPointDialog = false
    },

    async confirmDeleteTestPoint() {
      this.isDeletingTestPoint = true
      try {
        const res = await mockTestDesignAPI.deleteTestPoint(this.activeRequirementId)
        if (res.success) {
          const smmNode = this.contextMenu.smmNode
          if (smmNode && this.mindMap) {
            smmNode.remove()
            this.mindMap.render()
            this.mindMap.view.fit()
          }
          this.closeDeleteTestPointDialog()
        }
      } catch (e) {
        // ignore
      } finally {
        this.isDeletingTestPoint = false
      }
    },

    addTestCase() {
      this.hideContextMenu()
      this.newTestCaseName = ''
      this.newTestCaseProperty = '正例'
      this.newTestCasePreCondition = ''
      this.newTestCaseSteps = [{ name: '', description: '', stepExpectedResult: '' }]
      this.addTestCaseError = ''
      this.showAddTestCaseDialog = true
      this.$nextTick(() => {
        if (this.$refs.testCaseNameInput) {
          this.$refs.testCaseNameInput.focus()
        }
      })
    },

    closeAddTestCaseDialog() {
      this.showAddTestCaseDialog = false
      this.newTestCaseName = ''
      this.newTestCaseProperty = '正例'
      this.newTestCasePreCondition = ''
      this.newTestCaseSteps = [{ name: '', description: '', stepExpectedResult: '' }]
      this.addTestCaseError = ''
    },

    addTestCaseStep() {
      this.newTestCaseSteps.push({ name: '', description: '', stepExpectedResult: '' })
    },

    removeTestCaseStep(index) {
      this.newTestCaseSteps.splice(index, 1)
    },

    async confirmAddTestCase() {
      const name = this.newTestCaseName.trim()
      if (!name) {
        this.addTestCaseError = '请输入测试用例名称'
        return
      }
      if (name.length > 200) {
        this.addTestCaseError = '测试用例名称不能超过200个字符'
        return
      }
      const hasEmptyStep = this.newTestCaseSteps.some(s => !s.name.trim() || !s.description.trim() || !s.stepExpectedResult.trim())
      if (hasEmptyStep) {
        this.addTestCaseError = '请完整填写所有步骤信息'
        return
      }

      this.isAddingTestCase = true
      this.addTestCaseError = ''

      try {
        const steps = this.newTestCaseSteps.map(s => ({
          name: s.name.trim(),
          description: s.description.trim(),
          stepExpectedResult: s.stepExpectedResult.trim()
        }))

        const res = await mockTestDesignAPI.addTestCase(this.activeRequirementId, {
          testPointNodeId: this.contextMenu.node && this.contextMenu.node.text,
          text: name,
          caseProperty: this.newTestCaseProperty,
          preCondition: this.newTestCasePreCondition.trim(),
          steps
        })

        if (res.success) {
          const smmNode = this.contextMenu.smmNode
          if (smmNode && this.mindMap) {
            const caseNote = {
              caseName: name,
              caseProperty: this.newTestCaseProperty,
              preCondition: this.newTestCasePreCondition.trim(),
              source: '人工',
              steps
            }
            const newNodeData = {
              data: {
                text: name,
                note: buildCaseNote(caseNote),
                expand: true,
                _level: 'testCase',
                _caseProperty: this.newTestCaseProperty,
                _source: '人工',
                _marked: false
              },
              children: []
            }
            smmNode.appendChild(newNodeData)
            this.mindMap.render()
            this.mindMap.view.fit()
          }
          this.closeAddTestCaseDialog()
        } else {
          this.addTestCaseError = res.message || '添加失败，请重试'
        }
      } catch (e) {
        this.addTestCaseError = '网络异常，请稍后重试'
      } finally {
        this.isAddingTestCase = false
      }
    },

    editTestCaseDialog() {
      this.hideContextMenu()
      if (this.contextMenu.node) {
        this.editTestCaseName = this.contextMenu.node.text || ''
        this.editTestCaseProperty = this.contextMenu.node.caseProperty || '正例'
        const parsed = this.parseCaseNoteData(this.contextMenu.smmNode)
        this.editTestCasePreCondition = parsed.preCondition
        this.editTestCaseSteps = parsed.steps.length > 0
          ? parsed.steps
          : [{ name: '', description: '', stepExpectedResult: '' }]
      } else {
        this.editTestCaseName = ''
        this.editTestCaseProperty = '正例'
        this.editTestCasePreCondition = ''
        this.editTestCaseSteps = [{ name: '', description: '', stepExpectedResult: '' }]
      }
      this.editTestCaseError = ''
      this.showEditTestCaseDialog = true
      this.$nextTick(() => {
        if (this.$refs.editTestCaseNameInput) {
          this.$refs.editTestCaseNameInput.focus()
        }
      })
    },

    parseCaseNoteData(smmNode) {
      const result = { preCondition: '', steps: [] }
      if (!smmNode) return result
      const nodeData = smmNode.getData()
      const note = nodeData.note || ''
      if (!note) return result

      try {
        const parser = new DOMParser()
        const doc = parser.parseFromString(note, 'text/html')

        const preEl = doc.querySelector('.case-note-precondition')
        if (preEl) {
          let text = preEl.textContent || ''
          text = text.replace(/^前置条件[：:]/, '').trim()
          result.preCondition = text
        }

        const stepItems = doc.querySelectorAll('.step-item')
        stepItems.forEach(item => {
          const nameEl = item.querySelector('.step-name')
          const descEl = item.querySelector('.step-desc')
          const expectEl = item.querySelector('.step-expect')
          result.steps.push({
            name: nameEl ? nameEl.textContent.trim() : '',
            description: descEl ? descEl.textContent.trim() : '',
            stepExpectedResult: expectEl ? expectEl.textContent.trim() : ''
          })
        })
      } catch (e) {
        // ignore parse errors
      }

      return result
    },

    closeEditTestCaseDialog() {
      this.showEditTestCaseDialog = false
      this.editTestCaseName = ''
      this.editTestCaseProperty = '正例'
      this.editTestCasePreCondition = ''
      this.editTestCaseSteps = [{ name: '', description: '', stepExpectedResult: '' }]
      this.editTestCaseError = ''
    },

    addEditTestCaseStep() {
      this.editTestCaseSteps.push({ name: '', description: '', stepExpectedResult: '' })
    },

    removeEditTestCaseStep(index) {
      this.editTestCaseSteps.splice(index, 1)
    },

    async confirmEditTestCase() {
      const name = this.editTestCaseName.trim()
      if (!name) {
        this.editTestCaseError = '请输入测试用例名称'
        return
      }
      if (name.length > 200) {
        this.editTestCaseError = '测试用例名称不能超过200个字符'
        return
      }
      const hasEmptyStep = this.editTestCaseSteps.some(s => !s.name.trim() || !s.description.trim() || !s.stepExpectedResult.trim())
      if (hasEmptyStep) {
        this.editTestCaseError = '请完整填写所有步骤信息'
        return
      }

      this.isEditingTestCase = true
      this.editTestCaseError = ''

      try {
        const steps = this.editTestCaseSteps.map(s => ({
          name: s.name.trim(),
          description: s.description.trim(),
          stepExpectedResult: s.stepExpectedResult.trim()
        }))

        const res = await mockTestDesignAPI.editTestCase(this.activeRequirementId, {
          text: name,
          caseProperty: this.editTestCaseProperty,
          preCondition: this.editTestCasePreCondition.trim(),
          steps
        })

        if (res.success) {
          const smmNode = this.contextMenu.smmNode
          if (smmNode && this.mindMap) {
            const nodeData = smmNode.getData()
            const source = nodeData._source || '人工'
            const caseNote = {
              caseName: name,
              caseProperty: this.editTestCaseProperty,
              preCondition: this.editTestCasePreCondition.trim(),
              source,
              steps
            }
            nodeData.text = name
            nodeData.note = buildCaseNote(caseNote)
            nodeData._caseProperty = this.editTestCaseProperty
            smmNode.setData(nodeData)
            this.mindMap.render()
            this.mindMap.view.fit()
          }
          this.closeEditTestCaseDialog()
        } else {
          this.editTestCaseError = res.message || '保存失败，请重试'
        }
      } catch (e) {
        this.editTestCaseError = '网络异常，请稍后重试'
      } finally {
        this.isEditingTestCase = false
      }
    },

    deleteTestCase() {
      this.hideContextMenu()
      this.showDeleteTestCaseDialog = true
    },

    closeDeleteTestCaseDialog() {
      this.showDeleteTestCaseDialog = false
    },

    async confirmDeleteTestCase() {
      this.isDeletingTestCase = true
      try {
        const res = await mockTestDesignAPI.deleteTestCase(this.activeRequirementId)
        if (res.success) {
          const smmNode = this.contextMenu.smmNode
          if (smmNode && this.mindMap) {
            smmNode.remove()
            this.mindMap.render()
            this.mindMap.view.fit()
          }
          this.closeDeleteTestCaseDialog()
        }
      } catch (e) {
        // ignore
      } finally {
        this.isDeletingTestCase = false
      }
    },

    toggleMark() {
      if (this.contextMenu.node) {
        this.contextMenu.node.marked = !this.contextMenu.node.marked
      }
      if (this.contextMenu.smmNode && this.mindMap) {
        const nodeData = this.contextMenu.smmNode.getData()
        nodeData._marked = !nodeData._marked
        this.contextMenu.smmNode.setData(nodeData)
        this.mindMap.render()
      }
      this.hideContextMenu()
    },

    // ==================== 快速生成 ====================
    async startGenerate() {
      if (this.isGenerating || !this.activeRequirement) return

      this.isGenerating = true
      this.progress = 0
      this.progressText = '正在初始化生成任务...'

      try {
        const res = await mockTestDesignAPI.generate(this.activeRequirementId, {
          useKnowledgeBase: this.knowledgeBaseEnabled
        })

        if (res.success) {
          this.currentTaskId = res.data.taskId
          this.progressText = '正在生成测试点和测试用例...'
          this.startPolling()
        } else {
          this.isGenerating = false
          this.progress = 0
          this.progressText = ''
          this.currentTaskId = null
          alert(res.message || '生成任务启动失败，请重试')
        }
      } catch (e) {
        this.isGenerating = false
        this.progress = 0
        this.progressText = ''
        this.currentTaskId = null
        alert('网络异常，请稍后重试')
      }
    },

    startPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
      }

      this.pollTimer = setInterval(async () => {
        if (!this.currentTaskId) {
          this.stopPolling()
          return
        }

        try {
          const res = await mockTestDesignAPI.getTaskStatus(this.currentTaskId)
          if (res.success) {
            const task = res.data
            this.progress = task.progress || 0
            this.progressText = task.progressText || '正在生成...'

            if (task.status === 'completed') {
              this.stopPolling()
              this.isGenerating = false
              this.progress = 100
              this.progressText = '生成完成'
              this.currentTaskId = null

              this.updateRequirementStatus('completed')

              try {
                const mindMapRes = await mockTestDesignAPI.getMindMapData(this.activeRequirementId)
                if (mindMapRes.success) {
                  this._mindMapData = mindMapRes.data
                  this.$nextTick(() => {
                    this.initMindMap()
                  })
                }
              } catch (e) {
                // ignore
              }

              setTimeout(() => {
                this.progress = 0
                this.progressText = ''
              }, 2000)
            } else if (task.status === 'failed') {
              this.stopPolling()
              this.isGenerating = false
              this.progress = 0
              this.progressText = ''
              this.currentTaskId = null
              alert('生成任务失败，请重试')
            } else if (task.status === 'cancelled') {
              this.stopPolling()
              this.isGenerating = false
              this.progress = 0
              this.progressText = ''
              this.currentTaskId = null
            }
          }
        } catch (e) {
          // ignore polling errors
        }
      }, 2000)
    },

    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    },

    async cancelGenerate() {
      if (!this.currentTaskId) return

      try {
        const res = await mockTestDesignAPI.cancelTask(this.currentTaskId)
        if (res.success) {
          this.stopPolling()
          this.isGenerating = false
          this.progress = 0
          this.progressText = ''
          this.currentTaskId = null
        }
      } catch (e) {
        // ignore
      }
    },

    updateRequirementStatus(status) {
      if (this.activeRequirement) {
        this.activeRequirement.status = status
        this.activeRequirement.statusText = status === 'completed' ? '已完成' : status === 'generating' ? '生成中' : '待生成'
      }
      const item = this.historyList.find(r => r.id === this.activeRequirementId)
      if (item) {
        item.status = status
        item.statusText = status === 'completed' ? '已完成' : status === 'generating' ? '生成中' : '待生成'
      }
    },

    // ==================== 导出Excel ====================
    async exportExcel() {
      if (!this.activeRequirement || this.isExporting) return

      this.isExporting = true

      try {
        const mindMapData = this._mindMapData || (this.mindMap && this.mindMap.getData ? this.mindMap.getData() : null)
        if (!mindMapData) {
          alert('暂无脑图数据可导出')
          return
        }

        const XLSX = await import('xlsx')
        const { rows, caseMergeInfo } = this.buildExportRows(mindMapData)

        const wb = XLSX.utils.book_new()
        const ws = XLSX.utils.json_to_sheet(rows)

        const merges = caseMergeInfo.map(({ startRow, endRow }) => {
          return [
            { s: { r: startRow + 1, c: 0 }, e: { r: endRow + 1, c: 0 } },
            { s: { r: startRow + 1, c: 1 }, e: { r: endRow + 1, c: 1 } },
            { s: { r: startRow + 1, c: 2 }, e: { r: endRow + 1, c: 2 } }
          ]
        }).flat()
        ws['!merges'] = merges

        const colWidths = [
          { wch: 30 },
          { wch: 10 },
          { wch: 30 },
          { wch: 20 },
          { wch: 30 },
          { wch: 30 }
        ]
        ws['!cols'] = colWidths

        XLSX.utils.book_append_sheet(wb, ws, '测试用例')

        const fileName = `${this.activeRequirement.title || '测试用例'}_测试用例.xlsx`
        XLSX.writeFile(wb, fileName)
      } catch (e) {
        alert('导出失败，请重试')
      } finally {
        this.isExporting = false
      }
    },

    buildExportRows(rootNode) {
      const rows = []
      const caseMergeInfo = []
      const rootData = rootNode.data || rootNode

      const requirements = rootNode.children || []
      requirements.forEach(req => {
        const testPoints = req.children || []
        testPoints.forEach(tp => {
          const testCases = tp.children || []

          if (testCases.length === 0) {
            rows.push({
              caseName: '',
              caseProperty: '',
              preCondition: '',
              name: '',
              description: '',
              stepExpectedResult: ''
            })
            return
          }

          testCases.forEach(tc => {
            const tcData = tc.data || {}
            const caseName = tcData.text || ''
            const caseProperty = tcData._caseProperty || ''
            const preCondition = this.parseCaseNotePreCondition(tcData.note || '')
            const steps = this.parseCaseNoteSteps(tcData.note || '')

            const startRow = rows.length

            if (steps.length === 0) {
              rows.push({
                caseName,
                caseProperty,
                preCondition,
                name: '',
                description: '',
                stepExpectedResult: ''
              })
            } else {
              steps.forEach(step => {
                rows.push({
                  caseName,
                  caseProperty,
                  preCondition,
                  name: step.name,
                  description: step.description,
                  stepExpectedResult: step.stepExpectedResult
                })
              })
            }

            const endRow = rows.length - 1
            if (endRow > startRow) {
              caseMergeInfo.push({ startRow, endRow })
            }
          })
        })
      })

      if (rows.length === 0) {
        rows.push({
          caseName: rootData.text || '',
          caseProperty: '',
          preCondition: '',
          name: '',
          description: '',
          stepExpectedResult: ''
        })
      }

      return { rows, caseMergeInfo }
    },

    parseCaseNotePreCondition(note) {
      if (!note) return ''
      try {
        const parser = new DOMParser()
        const doc = parser.parseFromString(note, 'text/html')
        const preEl = doc.querySelector('.case-note-precondition')
        if (preEl) {
          let text = preEl.textContent || ''
          text = text.replace(/^前置条件[：:]/, '').trim()
          return text
        }
      } catch (e) {
        // ignore
      }
      return ''
    },

    parseCaseNoteSteps(note) {
      const result = []
      if (!note) return result
      try {
        const parser = new DOMParser()
        const doc = parser.parseFromString(note, 'text/html')
        const stepItems = doc.querySelectorAll('.step-item')
        stepItems.forEach(item => {
          const nameEl = item.querySelector('.step-name')
          const descEl = item.querySelector('.step-desc')
          const expectEl = item.querySelector('.step-expect')
          result.push({
            name: nameEl ? nameEl.textContent.trim() : '',
            description: descEl ? descEl.textContent.trim() : '',
            stepExpectedResult: expectEl ? expectEl.textContent.trim() : ''
          })
        })
      } catch (e) {
        // ignore
      }
      return result
    },

    // ==================== 状态工具方法 ====================
    getRequirementStatusClass(status) {
      switch (status) {
        case 'completed': return 'bg-green-100 text-green-700'
        case 'generating': return 'bg-yellow-100 text-yellow-700'
        case 'pending': return 'bg-gray-100 text-gray-500'
        default: return 'bg-gray-100 text-gray-500'
      }
    },

    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>

<style>
/* ========== 右键菜单动画 ========== */
.context-menu {
  animation: menu-appear 0.15s ease-out;
}

@keyframes menu-appear {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.context-menu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 14px;
  text-align: left;
  font-size: 13px;
  color: #374151;
  transition: background-color 0.15s;
  gap: 8px;
}

.context-menu-item:hover {
  background-color: #f3f4f6;
}

/* ========== 用例备注弹窗 ========== */
#custom-note-popover {
  display: none;
  position: fixed;
  z-index: 1000;
  pointer-events: none;
}

.case-note-popover {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  padding: 16px;
  min-width: 320px;
  max-width: 420px;
  font-size: 13px;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.case-note-name {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
  line-height: 1.4;
  word-break: break-all;
}

.case-note-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.case-property-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.tag-positive {
  background: #dcfce7;
  color: #166534;
}

.tag-negative {
  background: #fee2e2;
  color: #991b1b;
}

.case-source-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.tag-ai {
  background: #fef3c7;
  color: #92400e;
}

.tag-manual {
  background: #f3e8ff;
  color: #6b21a8;
}

.case-note-precondition {
  margin-bottom: 12px;
  padding: 8px 10px;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.6;
}

.case-note-precondition .label,
.case-note-steps .label {
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 6px;
}

.case-note-steps {
  border-top: 1px solid #f3f4f6;
  padding-top: 10px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 6px 0;
  font-size: 12px;
  line-height: 1.6;
  border-bottom: 1px dashed #f3f4f6;
}

.step-item:last-child {
  border-bottom: none;
}

.step-num {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  margin-top: 1px;
}

.step-name {
  font-weight: 600;
  color: #374151;
  flex-shrink: 0;
}

.step-desc {
  color: #6b7280;
}

.step-arrow {
  color: #d1d5db;
  flex-shrink: 0;
}

.step-expect {
  color: #059669;
}
</style>