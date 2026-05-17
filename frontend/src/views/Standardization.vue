<template>
  <div class="flex h-full w-full">
    <aside class="w-52 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto">
      <div class="p-4">
            <button
              @click="newRequirement"
              class="w-full mb-3 px-3 py-2 text-sm text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors flex items-center justify-center space-x-1.5"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              <span>新建需求</span>
            </button>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-semibold text-gray-800">历史记录</h3>
              <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{{ historyList.length }}</span>
            </div>
            <div v-if="historyList.length === 0" class="text-center py-8">
              <svg class="w-10 h-10 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <p class="text-xs text-gray-400">暂无历史记录</p>
            </div>
            <div v-else class="space-y-1 max-h-[calc(100vh-220px)] overflow-y-auto">
              <div
                v-for="item in historyList"
                :key="item.id"
                @click="loadHistory(item)"
                class="p-3 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-200"
                :class="{ 'bg-blue-50 border-blue-200': item.id === activeHistoryId }"
              >
                <p class="text-sm text-gray-700 truncate">{{ item.title }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ item.date }}</p>
              </div>
            </div>
          </div>
        </aside>

        <main class="flex-1 overflow-y-auto p-6 space-y-6">
          <div class="flex items-center justify-center space-x-3 py-2">
            <div
              class="flex items-center space-x-2 cursor-pointer group"
              @click="activeStep = 1"
            >
              <div
                class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all"
                :class="activeStep === 1 ? 'bg-blue-600 text-white shadow-md' : (standardizedContent ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-500')"
              >1</div>
              <span
                class="text-sm font-medium transition-colors"
                :class="activeStep === 1 ? 'text-gray-800' : 'text-gray-400'"
              >需求录入</span>
            </div>
            <div class="w-10 h-px bg-gray-300"></div>
            <div
              class="flex items-center space-x-2 cursor-pointer group"
              :class="{ 'pointer-events-none opacity-50': !standardizedContent }"
              @click="activeStep = 2"
            >
              <div
                class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all"
                :class="activeStep === 2 ? 'bg-blue-600 text-white shadow-md' : (standardizedContent ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-400')"
              >2</div>
              <span
                class="text-sm font-medium transition-colors"
                :class="activeStep === 2 ? 'text-gray-800' : (standardizedContent ? 'text-gray-500' : 'text-gray-400')"
              >文档标准化</span>
            </div>
            <div class="w-10 h-px bg-gray-300"></div>
            <div
              class="flex items-center space-x-2 cursor-pointer group"
              :class="{ 'pointer-events-none opacity-50': splitRequirements.length === 0 }"
              @click="activeStep = 3"
            >
              <div
                class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all"
                :class="activeStep === 3 ? 'bg-blue-600 text-white shadow-md' : (splitRequirements.length > 0 ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-400')"
              >3</div>
              <span
                class="text-sm font-medium transition-colors"
                :class="activeStep === 3 ? 'text-gray-800' : (splitRequirements.length > 0 ? 'text-gray-500' : 'text-gray-400')"
              >需求拆分</span>
            </div>
          </div>

          <div v-if="showDraftRestore" class="mb-4 px-4 py-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <svg class="w-5 h-5 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
              <div>
                <span class="text-sm text-amber-800">检测到未完成的草稿</span>
                <span class="text-xs text-amber-600 ml-2">保存于 {{ draftSavedTime }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="dismissDraftRestore"
                class="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                丢弃
              </button>
              <button
                @click="restoreDraft"
                class="px-4 py-1.5 text-xs text-white bg-amber-500 hover:bg-amber-600 rounded-lg transition-colors font-medium"
              >
                恢复草稿
              </button>
            </div>
          </div>

          <div v-show="activeStep === 1" class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-3">
                <h2 class="text-lg font-semibold text-gray-800">需求录入</h2>
                <span v-if="draftStatus === 'unsaved'" class="flex items-center space-x-1 text-xs text-amber-500">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                  <span>未保存</span>
                </span>
                <span v-else-if="draftStatus === 'saved'" class="flex items-center space-x-1 text-xs text-green-500">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <span>已保存</span>
                </span>
                <span v-else-if="draftStatus === 'error'" class="flex items-center space-x-1 text-xs text-red-500">
                  <span>保存失败</span>
                </span>
              </div>
              <div class="flex bg-gray-100 rounded-lg p-1">
                <button
                  @click="switchInputMode('text')"
                  class="px-4 py-2 text-sm font-medium rounded-md transition-all"
                  :class="inputMode === 'text' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                  <svg class="w-4 h-4 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  文本输入
                </button>
                <button
                  @click="switchInputMode('document')"
                  class="px-4 py-2 text-sm font-medium rounded-md transition-all"
                  :class="inputMode === 'document' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                  <svg class="w-4 h-4 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  文档上传
                </button>
              </div>
            </div>

            <div v-if="inputMode === 'text'" class="mb-6">
              <div class="relative">
                <textarea
                  v-model="requirementText"
                  rows="10"
                  placeholder="请输入需求描述，例如：&#10;&#10;用户登录功能需要支持用户名密码登录，登录成功后跳转到首页。&#10;密码需要支持大小写字母、数字和特殊字符的组合。&#10;连续5次登录失败后需要锁定账户30分钟。"
                  class="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm leading-relaxed placeholder-gray-400"
                ></textarea>
                <div class="absolute bottom-3 right-3 text-xs text-gray-400">
                  {{ requirementText.length }} 字
                </div>
              </div>
            </div>

            <div v-else class="mb-6">
              <div
                class="border-2 border-dashed rounded-lg p-10 text-center transition-all cursor-pointer"
                :class="uploadedFile ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'"
                @click="$refs.fileInput.click()"
                @dragover.prevent="dragOver = true"
                @dragleave.prevent="dragOver = false"
                @drop.prevent="handleDrop"
              >
                <input
                  type="file"
                  ref="fileInput"
                  @change="handleFileUpload"
                  accept=".docx,.xlsx"
                  class="hidden"
                />
                <div v-if="!uploadedFile">
                  <div class="w-14 h-14 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg class="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                  </div>
                  <p class="text-sm text-gray-600 font-medium">点击或拖拽文件到此处上传</p>
                  <p class="text-xs text-gray-400 mt-1">支持 .docx、.xlsx 格式，单个文件不超过 10MB</p>
                </div>
                <div v-else class="flex items-center justify-center space-x-3">
                  <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="text-sm text-gray-700 font-medium">{{ uploadedFile.name }}</p>
                    <p class="text-xs text-gray-400">{{ formatFileSize(uploadedFile.size) }}</p>
                  </div>
                  <button
                    @click.stop="uploadedFile = null"
                    class="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-end">
              <p v-if="!canStandardize" class="text-xs text-gray-400 mr-3">请输入需求文本或上传文档后开始</p>
              <button
                @click="handleStandardize"
                :disabled="!canStandardize || standardizing"
                class="px-5 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1.5"
              >
                <svg v-if="standardizing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span>{{ standardizing ? 'AI 标准化处理中...' : '文档标准化助手' }}</span>
              </button>
            </div>
          </div>

          <div v-show="activeStep === 2" class="bg-white rounded-lg shadow-sm p-6">
            <div v-if="!standardizedContent" class="text-center py-16">
              <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-2xl flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <p class="text-sm text-gray-500">请先在「需求录入」步骤中完成需求输入并点击「文档标准化助手」</p>
              <button
                @click="activeStep = 1"
                class="mt-4 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                返回需求录入
              </button>
            </div>
            <template v-else>
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                  <h2 class="text-lg font-semibold text-gray-800">标准文档预览</h2>
                  <span v-if="draftStatus === 'unsaved'" class="flex items-center space-x-1 text-xs text-amber-500">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    <span>未保存</span>
                  </span>
                  <span v-else-if="draftStatus === 'saved'" class="flex items-center space-x-1 text-xs text-green-500">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <span>已保存</span>
                  </span>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="flex items-center space-x-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <span>AI 生成</span>
                  </span>
                </div>
              </div>

              <div class="mb-4 p-4 rounded-xl border" :class="qualityLevel.bg" :style="{ borderColor: qualityLevel.color }">
                <div class="flex items-start gap-6">
                  <div class="flex-shrink-0 flex flex-col items-center">
                    <div class="relative w-16 h-16">
                      <svg class="w-16 h-16 transform -rotate-90" viewBox="0 0 64 64">
                        <circle cx="32" cy="32" r="28" fill="none" stroke="#E5E7EB" stroke-width="5" />
                        <circle
                          cx="32" cy="32" r="28" fill="none"
                          :stroke="qualityLevel.color"
                          stroke-width="5"
                          stroke-linecap="round"
                          :stroke-dasharray="scoreRingDasharray"
                          :stroke-dashoffset="scoreRingDashoffset"
                          class="transition-all duration-700"
                        />
                      </svg>
                      <div class="absolute inset-0 flex items-center justify-center">
                        <span class="text-xl font-bold" :class="qualityLevel.text">{{ qualityReport.overall }}</span>
                      </div>
                    </div>
                    <span class="text-xs mt-1" :class="qualityLevel.text">{{ qualityLevel.label }}</span>
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="grid grid-cols-3 gap-4">
                      <div>
                        <div class="flex items-center justify-between mb-1">
                          <span class="text-xs text-gray-500">完整性</span>
                          <span class="text-xs font-medium" :class="qualityReport.completeness.score >= 60 ? 'text-green-600' : 'text-red-500'">{{ qualityReport.completeness.score }}%</span>
                        </div>
                        <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            class="h-full rounded-full transition-all duration-500"
                            :class="qualityReport.completeness.score >= 60 ? 'bg-green-500' : 'bg-red-400'"
                            :style="{ width: qualityReport.completeness.score + '%' }"
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div class="flex items-center justify-between mb-1">
                          <span class="text-xs text-gray-500">清晰度</span>
                          <span class="text-xs font-medium" :class="qualityReport.clarity.score >= 60 ? 'text-green-600' : 'text-red-500'">{{ qualityReport.clarity.score }}%</span>
                        </div>
                        <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            class="h-full rounded-full transition-all duration-500"
                            :class="qualityReport.clarity.score >= 60 ? 'bg-green-500' : 'bg-red-400'"
                            :style="{ width: Math.max(0, qualityReport.clarity.score) + '%' }"
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div class="flex items-center justify-between mb-1">
                          <span class="text-xs text-gray-500">一致性</span>
                          <span class="text-xs font-medium" :class="qualityReport.consistency.score >= 60 ? 'text-green-600' : 'text-red-500'">{{ qualityReport.consistency.score }}%</span>
                        </div>
                        <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            class="h-full rounded-full transition-all duration-500"
                            :class="qualityReport.consistency.score >= 60 ? 'bg-green-500' : 'bg-red-400'"
                            :style="{ width: Math.max(0, qualityReport.consistency.score) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>

                    <div v-if="qualityReport.suggestions.length > 0" class="mt-3">
                      <div class="flex items-center space-x-1 mb-1.5">
                        <svg class="w-3.5 h-3.5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        <span class="text-xs font-medium text-gray-600">改进建议</span>
                      </div>
                      <ul class="space-y-1">
                        <li v-for="(s, i) in qualityReport.suggestions.slice(0, 3)" :key="i" class="text-xs text-gray-500 flex items-start space-x-1.5">
                          <span class="text-amber-500 flex-shrink-0 mt-0.5">•</span>
                          <span>{{ s }}</span>
                        </li>
                      </ul>
                      <button
                        v-if="qualityReport.suggestions.length > 0"
                        @click="openBrainstormDialog"
                        class="mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
                      >
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                        <span>使用AI头脑风暴改进文档</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center space-x-2">
                  <div class="flex space-x-1.5">
                    <div class="w-3 h-3 rounded-full bg-red-400"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div class="w-3 h-3 rounded-full bg-green-400"></div>
                  </div>
                  <span class="text-xs text-gray-400 ml-2">Markdown 预览 · 可编辑</span>
                </div>
                <textarea
                  v-model="standardizedContent"
                  rows="14"
                  class="w-full px-6 py-4 border-none outline-none resize-none font-mono text-sm leading-relaxed text-gray-700 bg-white"
                ></textarea>
              </div>
              <div class="mt-4 flex items-center justify-between">
                <div class="flex items-center space-x-2 text-xs text-gray-400">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>可直接编辑文档内容，或使用AI头脑风暴与AI进行多轮对话帮您调整</span>
                </div>
                <div class="flex items-center space-x-3">
                  <button @click="openBrainstormDialog" class="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors text-sm font-medium flex items-center space-x-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                    </svg>
                    <span>AI头脑风暴</span>
                  </button>
                  <div class="relative">
                    <button
                      @click="showExportMenu = !showExportMenu"
                      class="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors text-sm font-medium flex items-center space-x-1.5 border border-gray-200"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                      <span>导出</span>
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </button>
                    <div v-if="showExportMenu" class="fixed inset-0 z-10" @click="closeExportMenu"></div>
                    <div v-if="showExportMenu" class="absolute right-0 bottom-full mb-1 w-44 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-20">
                      <button
                        @click="handleExport('markdown')"
                        class="w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                      >
                        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                        </svg>
                        <span>Markdown (.md)</span>
                      </button>
                      <button
                        @click="handleExport('docx')"
                        class="w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                      >
                        <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                        </svg>
                        <span>Word 文档 (.docx)</span>
                      </button>
                    </div>
                  </div>
                  <button @click="handleSplitRequirements" class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center space-x-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7M4 7c0-2 1-3 3-3h10c2 0 3 1 3 3M4 7h16M9 11l3 3 3-3"></path>
                    </svg>
                    <span>需求拆分</span>
                  </button>
                </div>
              </div>
            </template>
          </div>

          <div v-show="activeStep === 3" class="bg-white rounded-lg shadow-sm p-6">
            <div v-if="splitRequirements.length === 0" class="text-center py-16">
              <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-2xl flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7M4 7c0-2 1-3 3-3h10c2 0 3 1 3 3M4 7h16"></path>
                </svg>
              </div>
              <p class="text-sm text-gray-500">请先在「文档标准化」步骤中完成标准化并点击「需求拆分」</p>
              <button
                @click="activeStep = 2"
                class="mt-4 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                返回文档标准化
              </button>
            </div>
            <template v-else>
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-2">
                  <h2 class="text-lg font-semibold text-gray-800">拆分后的需求</h2>
                  <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{{ splitRequirements.length }} 条</span>
                  <span v-if="draftStatus === 'unsaved'" class="flex items-center space-x-1 text-xs text-amber-500">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    <span>未保存</span>
                  </span>
                  <span v-else-if="draftStatus === 'saved'" class="flex items-center space-x-1 text-xs text-green-500">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <span>已保存</span>
                  </span>
                </div>
                <button
                  @click="addRequirement"
                  class="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center space-x-1"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  <span>手动添加</span>
                </button>
              </div>
              <div class="space-y-2">
                <div
                  v-for="(req, index) in splitRequirements"
                  :key="index"
                  class="flex items-center group p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-transparent hover:border-gray-200"
                >
                  <span class="text-xs text-gray-400 w-6 flex-shrink-0">{{ index + 1 }}.</span>
                  <div class="flex-1 mx-3">
                    <input
                      v-model="req.content"
                      class="w-full bg-transparent border-none outline-none text-sm text-gray-700 placeholder-gray-400"
                      :placeholder="'需求 ' + (index + 1) + ' 的描述...'"
                    />
                  </div>
                  <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path>
                      </svg>
                    </button>
                    <button @click="removeRequirement(index)" class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-100 flex justify-end">
                <button class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                  确认并进入测试设计
                </button>
              </div>
            </template>
          </div>
        </main>

    <div v-if="showDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showDialog = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-5xl mx-4 h-[85vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-base font-semibold text-gray-800">AI 头脑风暴</h3>
              <p class="text-xs text-gray-400">AI 将与您讨论确认后再修改文档，不会擅自添加不符合实际的内容</p>
            </div>
          </div>
          <button @click="showDialog = false" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div class="flex-1 flex overflow-hidden">
          <div class="w-1/2 flex flex-col border-r border-gray-100">
            <div class="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
              <div v-if="dialogMessages.length === 0" class="flex flex-col items-center justify-center h-full text-center py-12">
                <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
                  <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                  </svg>
                </div>
                <p class="text-sm text-gray-500 font-medium">开始头脑风暴</p>
                <p class="text-xs text-gray-400 mt-1">AI 会先与您讨论确认，再修改文档</p>
                <div class="mt-4 space-y-2">
                  <button
                    @click="sendQuickMessage('请帮我补充安全性相关的需求')"
                    class="block w-full text-left px-3 py-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors"
                  >
                    💡 请帮我补充安全性相关的需求
                  </button>
                  <button
                    @click="sendQuickMessage('请帮我细化性能指标要求')"
                    class="block w-full text-left px-3 py-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors"
                  >
                    💡 请帮我细化性能指标要求
                  </button>
                  <button
                    @click="sendQuickMessage('请帮我补充异常场景的处理')"
                    class="block w-full text-left px-3 py-2 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors"
                  >
                    💡 请帮我补充异常场景的处理
                  </button>
                </div>
              </div>
              <div
                v-for="(msg, index) in dialogMessages"
                :key="index"
                class="flex"
                :class="msg.isUser ? 'justify-end' : 'justify-start'"
              >
                <div v-if="!msg.isUser" class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0 mr-2">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
                <div
                  class="max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed"
                  :class="msg.isUser ? 'bg-blue-600 text-white rounded-br-md' : 'bg-white text-gray-700 rounded-bl-md shadow-sm border border-gray-100'"
                >
                  <div v-if="msg.type === 'proposal'" class="mb-2">
                    <p class="text-xs text-blue-600 font-medium mb-2">💭 AI 建议：</p>
                    <p>{{ msg.content }}</p>
                    <div v-if="!msg.confirmed && !msg.rejected" class="flex items-center space-x-2 mt-3 pt-2 border-t border-gray-100">
                      <button
                        @click="confirmProposal(index)"
                        class="px-3 py-1 text-xs bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
                      >采纳</button>
                      <button
                        @click="rejectProposal(index)"
                        class="px-3 py-1 text-xs bg-gray-200 text-gray-600 rounded-md hover:bg-gray-300 transition-colors"
                      >不采纳</button>
                    </div>
                    <div v-else class="mt-2 pt-2 border-t border-gray-100">
                      <span v-if="msg.confirmed" class="text-xs text-green-600">✅ 已采纳，文档已更新</span>
                      <span v-else class="text-xs text-gray-400">❌ 未采纳</span>
                    </div>
                  </div>
                  <p v-else>{{ msg.content }}</p>
                </div>
                <div v-if="msg.isUser" class="w-8 h-8 bg-gray-300 rounded-lg flex items-center justify-center flex-shrink-0 ml-2">
                  <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
              </div>
            </div>
            <div class="px-6 py-4 border-t border-gray-100 bg-white flex-shrink-0">
              <div class="flex items-center space-x-2">
                <input
                  v-model="dialogInput"
                  @keyup.enter="sendMessage"
                  type="text"
                  placeholder="描述您想要调整的内容..."
                  class="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
                />
                <button
                  @click="sendMessage"
                  :disabled="!dialogInput.trim()"
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

          <div class="w-1/2 flex flex-col">
            <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium text-gray-700">文档预览</span>
                <span class="text-xs text-gray-400">版本 {{ activeVersionId }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <select
                  v-model="activeVersionId"
                  @change="switchVersion(activeVersionId)"
                  class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-600 outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option
                    v-for="v in docVersions"
                    :key="v.id"
                    :value="v.id"
                  >
                    v{{ v.id }} - {{ v.description }}
                  </option>
                </select>
                <button
                  v-if="docVersions.length > 0 && activeVersionId !== docVersions[docVersions.length - 1].id"
                  @click="restoreVersion(activeVersionId)"
                  class="px-2.5 py-1.5 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors flex items-center space-x-1"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  <span>恢复此版本</span>
                </button>
              </div>
            </div>
            <div class="px-4 py-2 border-b border-gray-100 flex items-center space-x-4 flex-shrink-0">
              <div class="flex items-center space-x-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
                <span class="text-xs text-gray-400">新增</span>
              </div>
              <div class="flex items-center space-x-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
                <span class="text-xs text-gray-400">修改</span>
              </div>
              <div class="flex items-center space-x-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
                <span class="text-xs text-gray-400">删除</span>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto">
              <div class="border border-gray-200 rounded-lg m-4 overflow-hidden">
                <div class="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center space-x-2">
                  <div class="flex space-x-1.5">
                    <div class="w-3 h-3 rounded-full bg-red-400"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div class="w-3 h-3 rounded-full bg-green-400"></div>
                  </div>
                  <span class="text-xs text-gray-400 ml-2">{{ currentVersion ? currentVersion.timestamp : '' }}</span>
                </div>
                <div class="font-mono text-sm leading-relaxed bg-white min-h-[300px]">
                  <div
                    v-for="(line, idx) in highlightedPreviewLines"
                    :key="idx"
                    class="px-6 py-0.5 flex"
                    :class="{
                      'bg-green-50': line.type === 'added',
                      'bg-yellow-50': line.type === 'modified',
                      'bg-red-50 line-through text-gray-400': line.type === 'removed'
                    }"
                  >
                    <span class="w-6 text-xs text-gray-300 flex-shrink-0 select-none text-right mr-3">{{ idx + 1 }}</span>
                    <span class="flex-1 whitespace-pre-wrap">{{ line.text }}</span>
                  </div>
                  <div v-if="highlightedPreviewLines.length === 0" class="px-6 py-4 text-gray-400">
                    暂无内容
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { REQUIREMENT_TEMPLATE } from '@/utils/requirementTemplate'
import { analyzeQuality, getLevelConfig } from '@/utils/qualityScorer'
import { initDraftManager, getDraft, hasDraft, scheduleAutoSave, saveNow, clearDraft, formatSaveTime } from '@/utils/draftManager'
import { exportMarkdown, exportDocx } from '@/utils/exportUtils'

export default {
  name: 'Standardization',
  data() {
    return {
      activeStep: 1,
      inputMode: 'text',
      requirementText: '',
      uploadedFile: null,
      dragOver: false,
      standardizing: false,
      standardizedContent: '',
      splitRequirements: [],
      showDialog: false,
      dialogMessages: [],
      dialogInput: '',
      dialogPreviewContent: '',
      docVersions: [],
      activeVersionId: null,
      versionCounter: 0,
      historyList: [
        { id: '1', title: '用户登录系统需求', date: '2026-05-10 14:30' },
        { id: '2', title: '数据导出功能需求', date: '2026-05-09 10:15' },
        { id: '3', title: '权限管理系统需求', date: '2026-05-08 16:45' }
      ],
      activeHistoryId: null,
      draftStatus: 'idle',
      showDraftRestore: false,
      draftSavedTime: '',
      showExportMenu: false
    }
  },
  computed: {
    canStandardize() {
      if (this.inputMode === 'text') {
        return this.requirementText.trim().length > 0
      }
      return this.uploadedFile !== null
    },
    currentVersion() {
      return this.docVersions.find(v => v.id === this.activeVersionId) || null
    },
    highlightedPreviewLines() {
      if (!this.currentVersion) return []
      const currentIdx = this.docVersions.findIndex(v => v.id === this.activeVersionId)
      if (currentIdx <= 0) {
        return this.currentVersion.content.split('\n').map(line => ({ text: line, type: 'unchanged' }))
      }
      const prevContent = this.docVersions[currentIdx - 1].content
      return this.computeDiff(prevContent, this.currentVersion.content)
    },
    qualityReport() {
      return analyzeQuality(this.standardizedContent)
    },
    qualityLevel() {
      return getLevelConfig(this.qualityReport.level)
    },
    scoreRingDasharray() {
      return 2 * Math.PI * 28
    },
    scoreRingDashoffset() {
      return this.scoreRingDasharray * (1 - this.qualityReport.overall / 100)
    }
  },
  watch: {
    requirementText() {
      this.clearDownstreamSteps()
      this.triggerAutoSave()
    },
    uploadedFile() {
      this.clearDownstreamSteps()
    },
    standardizedContent() {
      this.triggerAutoSave()
    },
    splitRequirements: {
      deep: true,
      handler() {
        this.triggerAutoSave()
      }
    },
    activeStep() {
      saveNow(() => this.draftData())
    }
  },
  mounted() {
    initDraftManager((status) => {
      this.draftStatus = status
    })

    if (hasDraft()) {
      const draft = getDraft()
      this.draftSavedTime = formatSaveTime(draft.savedAt)
      this.showDraftRestore = true
    }
  },
  beforeDestroy() {
    saveNow(() => this.draftData())
  },
  methods: {
    draftData() {
      return {
        activeStep: this.activeStep,
        inputMode: this.inputMode,
        requirementText: this.requirementText,
        standardizedContent: this.standardizedContent,
        splitRequirements: this.splitRequirements,
        dialogMessages: this.dialogMessages,
        docVersions: this.docVersions,
        activeVersionId: this.activeVersionId,
        versionCounter: this.versionCounter
      }
    },
    triggerAutoSave() {
      scheduleAutoSave(() => this.draftData())
    },
    restoreDraft() {
      const draft = getDraft()
      if (!draft) return

      this.activeStep = draft.activeStep || 1
      this.inputMode = draft.inputMode || 'text'
      this.requirementText = draft.requirementText || ''
      this.standardizedContent = draft.standardizedContent || ''
      this.splitRequirements = draft.splitRequirements || []
      this.dialogMessages = draft.dialogMessages || []
      this.docVersions = draft.docVersions || []
      this.activeVersionId = draft.activeVersionId || null
      this.versionCounter = draft.versionCounter || 0
      this.showDraftRestore = false
      this.draftStatus = 'idle'
    },
    dismissDraftRestore() {
      this.showDraftRestore = false
      clearDraft()
    },
    closeExportMenu() {
      this.showExportMenu = false
    },
    async handleExport(format) {
      this.showExportMenu = false
      if (!this.standardizedContent) return

      const timestamp = new Date().toISOString().slice(0, 10)
      const filename = `需求规格说明书_${timestamp}`

      try {
        if (format === 'markdown') {
          exportMarkdown(this.standardizedContent, filename + '.md')
        } else if (format === 'docx') {
          await exportDocx(this.standardizedContent, filename + '.docx')
        }
      } catch (e) {
        console.error('导出失败:', e)
      }
    },
    clearDownstreamSteps() {
      this.standardizedContent = ''
      this.splitRequirements = []
    },
    switchInputMode(mode) {
      this.inputMode = mode
      if (mode === 'text') {
        this.uploadedFile = null
      } else {
        this.requirementText = ''
      }
    },
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.uploadedFile = file
      }
    },
    handleDrop(event) {
      this.dragOver = false
      const file = event.dataTransfer.files[0]
      if (file) {
        this.uploadedFile = file
      }
    },
    formatFileSize(bytes) {
      if (!bytes) return ''
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    },
    async handleStandardize() {
      this.standardizing = true

      await new Promise(resolve => setTimeout(resolve, 1500))

      const userInput = this.requirementText || this.uploadedFile?.name
      this.standardizedContent = REQUIREMENT_TEMPLATE.generateContent(userInput)

      this.standardizing = false
      this.activeStep = 2
    },
    handleSplitRequirements() {
      this.splitRequirements = [
        { content: '实现用户登录功能，支持用户名密码验证' },
        { content: '实现数据查询功能，支持多条件筛选' },
        { content: '实现数据导出功能，支持Excel格式' }
      ]
      this.activeStep = 3
    },
    addRequirement() {
      this.splitRequirements.push({ content: '' })
    },
    removeRequirement(index) {
      this.splitRequirements.splice(index, 1)
    },
    openBrainstormDialog() {
      this.dialogInput = ''
      this.dialogPreviewContent = this.standardizedContent
      this.versionCounter = 1
      this.docVersions = [{
        id: this.versionCounter,
        content: this.standardizedContent,
        timestamp: this.formatTime(new Date()),
        description: '初始版本'
      }]
      this.activeVersionId = this.versionCounter
      this.showDialog = true
    },
    sendQuickMessage(text) {
      this.dialogInput = text
      this.sendMessage()
    },
    sendMessage() {
      if (!this.dialogInput.trim()) return

      const userMsg = this.dialogInput.trim()
      this.dialogMessages.push({ content: userMsg, isUser: true })
      this.dialogInput = ''

      setTimeout(() => {
        const aiResponse = this.generateBrainstormResponse(userMsg)
        this.dialogMessages.push(aiResponse)

        if (aiResponse.type === 'proposal' && aiResponse.pendingChange) {
          this.dialogPreviewContent = aiResponse.pendingChange
        }
      }, 1000)
    },
    generateBrainstormResponse(userMsg) {
      if (userMsg.includes('安全')) {
        return {
          content: '我建议在非功能需求中增加以下安全性要求：\n\n- 密码加密存储（bcrypt）\n- 登录失败锁定机制\n- 敏感操作日志审计\n- 数据传输使用 HTTPS\n\n这些是否符合您的实际业务场景？如果有不需要的可以告诉我。',
          isUser: false,
          type: 'proposal',
          pendingChange: this.standardizedContent + '\n\n## 5. 安全性需求\n- 密码加密存储（bcrypt）\n- 登录失败锁定机制\n- 敏感操作日志审计\n- 数据传输使用 HTTPS',
          confirmed: false,
          rejected: false
        }
      }
      if (userMsg.includes('性能')) {
        return {
          content: '我建议将性能指标细化为：\n\n- 页面加载时间：< 2秒\n- API 响应时间：< 500ms\n- 并发用户支持：1000+\n- 数据库查询优化：添加索引\n\n您觉得这些指标合理吗？是否需要根据实际业务调整？',
          isUser: false,
          type: 'proposal',
          pendingChange: this.standardizedContent.replace('响应时间：< 3秒', '页面加载时间：< 2秒\n- API 响应时间：< 500ms\n- 并发用户支持：1000+'),
          confirmed: false,
          rejected: false
        }
      }
      if (userMsg.includes('异常')) {
        return {
          content: '我建议补充以下异常场景处理：\n\n- 网络超时：显示友好提示并支持重试\n- 服务不可用：降级处理，保证核心功能可用\n- 数据校验失败：明确提示错误原因\n- 并发冲突：乐观锁处理\n\n这些异常场景是否覆盖了您的业务需求？',
          isUser: false,
          type: 'proposal',
          pendingChange: this.standardizedContent + '\n\n## 6. 异常场景处理\n- 网络超时：显示友好提示并支持重试\n- 服务不可用：降级处理，保证核心功能可用\n- 数据校验失败：明确提示错误原因\n- 并发冲突：乐观锁处理',
          confirmed: false,
          rejected: false
        }
      }
      return {
        content: '好的，我理解您的需求。让我分析一下当前文档，看看哪些地方可以优化。您能具体说说希望调整的方向吗？比如安全性、性能、异常处理等方面？',
        isUser: false
      }
    },
    confirmProposal(index) {
      const msg = this.dialogMessages[index]
      msg.confirmed = true
      msg.rejected = false
      this.standardizedContent = this.dialogPreviewContent
      this.versionCounter++
      this.docVersions.push({
        id: this.versionCounter,
        content: this.dialogPreviewContent,
        timestamp: this.formatTime(new Date()),
        description: '采纳AI建议后的版本'
      })
      this.activeVersionId = this.versionCounter
    },
    rejectProposal(index) {
      const msg = this.dialogMessages[index]
      msg.rejected = true
      msg.confirmed = false
      this.dialogPreviewContent = this.standardizedContent
    },
    switchVersion(versionId) {
      this.activeVersionId = versionId
      const version = this.docVersions.find(v => v.id === versionId)
      if (version) {
        this.dialogPreviewContent = version.content
      }
    },
    restoreVersion(versionId) {
      const version = this.docVersions.find(v => v.id === versionId)
      if (!version) return
      this.standardizedContent = version.content
      this.versionCounter++
      this.docVersions.push({
        id: this.versionCounter,
        content: version.content,
        timestamp: this.formatTime(new Date()),
        description: '恢复自版本 ' + versionId
      })
      this.activeVersionId = this.versionCounter
      this.dialogPreviewContent = version.content
    },
    computeDiff(oldText, newText) {
      const oldLines = oldText.split('\n')
      const newLines = newText.split('\n')
      const result = []
      let i = 0
      let j = 0

      while (i < oldLines.length || j < newLines.length) {
        if (i >= oldLines.length) {
          result.push({ text: newLines[j], type: 'added' })
          j++
        } else if (j >= newLines.length) {
          result.push({ text: oldLines[i], type: 'removed' })
          i++
        } else if (oldLines[i] === newLines[j]) {
          result.push({ text: newLines[j], type: 'unchanged' })
          i++
          j++
        } else {
          const nextOldInNew = newLines.indexOf(oldLines[i], j)
          const nextNewInOld = oldLines.indexOf(newLines[j], i)

          if (nextOldInNew === -1 && nextNewInOld === -1) {
            result.push({ text: newLines[j], type: 'modified' })
            i++
            j++
          } else if (nextNewInOld === -1 || (nextOldInNew !== -1 && nextOldInNew <= nextNewInOld)) {
            while (j < nextOldInNew) {
              result.push({ text: newLines[j], type: 'added' })
              j++
            }
          } else {
            while (i < nextNewInOld) {
              result.push({ text: oldLines[i], type: 'removed' })
              i++
            }
          }
        }
      }
      return result
    },
    formatTime(date) {
      const pad = n => String(n).padStart(2, '0')
      return date.getFullYear() + '-' +
        pad(date.getMonth() + 1) + '-' +
        pad(date.getDate()) + ' ' +
        pad(date.getHours()) + ':' +
        pad(date.getMinutes()) + ':' +
        pad(date.getSeconds())
    },
    newRequirement() {
      this.activeHistoryId = null
      this.activeStep = 1
      this.inputMode = 'text'
      this.requirementText = ''
      this.uploadedFile = null
      this.standardizedContent = ''
      this.splitRequirements = []
      this.dialogMessages = []
      this.docVersions = []
      this.activeVersionId = null
      this.versionCounter = 0
      clearDraft()
    },
    loadHistory(item) {
      this.activeHistoryId = item.id
      this.requirementText = '用户登录系统需求描述：支持用户名密码登录，登录成功后跳转到首页。密码需要支持大小写字母、数字和特殊字符的组合。连续5次登录失败后需要锁定账户30分钟。'
      this.standardizedContent = REQUIREMENT_TEMPLATE.generateContent('用户登录系统需求')
      this.splitRequirements = [
        { content: '实现用户名密码登录功能' },
        { content: '实现密码复杂度校验' },
        { content: '实现登录失败锁定机制' }
      ]
      this.dialogMessages = []
      this.docVersions = []
      this.activeVersionId = null
      this.versionCounter = 0
      this.activeStep = 1
      clearDraft()
    },
    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>