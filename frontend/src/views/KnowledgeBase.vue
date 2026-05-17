<template>
  <div class="flex h-full w-full overflow-hidden bg-gray-50">
    <main class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto p-6 space-y-6">

        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-gray-900">知识库管理</h1>
            <p class="text-sm text-gray-500 mt-1">管理参考文档，配置知识召回参数，为测试用例生成提供领域知识支持</p>
          </div>
          <button
            @click="showUploadDialog = true"
            class="px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 active:scale-[0.98] transition-all flex items-center space-x-2 shadow-sm shadow-blue-600/20"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            <span>上传文档</span>
          </button>
        </div>

        <div class="grid grid-cols-4 gap-4">
          <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <span class="text-2xl font-bold text-gray-900">{{ documents.length }}</span>
            </div>
            <p class="text-xs text-gray-500 mt-2">文档总数</p>
          </div>
          <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="w-9 h-9 rounded-lg bg-green-50 flex items-center justify-center">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <span class="text-2xl font-bold text-gray-900">{{ readyDocCount }}</span>
            </div>
            <p class="text-xs text-gray-500 mt-2">已就绪</p>
          </div>
          <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-500 animate-spin" style="animation-duration: 3s" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
              </div>
              <span class="text-2xl font-bold text-gray-900">{{ processingDocCount }}</span>
            </div>
            <p class="text-xs text-gray-500 mt-2">处理中</p>
          </div>
          <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="w-9 h-9 rounded-lg bg-gray-50 flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
                </svg>
              </div>
              <div class="text-right">
                <span class="text-sm font-bold text-gray-900">{{ storageInfo.usedText }}</span>
                <span class="text-xs text-gray-400"> / {{ storageInfo.maxText }}</span>
              </div>
            </div>
            <div class="mt-2">
              <div class="w-full bg-gray-100 rounded-full h-1.5">
                <div
                  class="h-1.5 rounded-full transition-all duration-500"
                  :class="storageInfo.usedPercentage > 90 ? 'bg-red-500' : storageInfo.usedPercentage > 70 ? 'bg-amber-500' : 'bg-blue-500'"
                  :style="{ width: storageInfo.usedPercentage + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-400 mt-1">存储空间已用 {{ storageInfo.usedPercentage }}%</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="px-6 py-4 border-b border-gray-100">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <h2 class="text-base font-semibold text-gray-800">文档管理</h2>
              </div>
              <div class="flex items-center space-x-3">
                <div class="relative">
                  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                  </svg>
                  <input
                    v-model="searchKeyword"
                    type="text"
                    placeholder="搜索文档..."
                    class="w-56 pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                  />
                </div>
                <select
                  v-model="filterFormat"
                  class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 bg-white transition-all"
                >
                  <option value="">全部格式</option>
                  <option value="docx">DOCX</option>
                  <option value="xlsx">XLSX</option>
                  <option value="pdf">PDF</option>
                  <option value="txt">TXT</option>
                  <option value="md">MD</option>
                </select>
                <select
                  v-model="filterStatus"
                  class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 bg-white transition-all"
                >
                  <option value="">全部状态</option>
                  <option value="slicing">处理中</option>
                  <option value="ready">已就绪</option>
                  <option value="failed">处理失败</option>
                </select>
              </div>
            </div>
          </div>

          <div class="p-6">
            <div v-if="filteredDocuments.length === 0" class="text-center py-20">
              <div class="w-20 h-20 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
              </div>
              <p class="text-gray-500 text-sm font-medium mb-1">{{ debouncedKeyword || filterFormat || filterStatus ? '未找到匹配的文档' : '暂无文档' }}</p>
              <p v-if="!debouncedKeyword && !filterFormat && !filterStatus" class="text-gray-400 text-xs mb-5">上传参考文档，为测试用例生成提供领域知识支持</p>
              <button
                v-if="!debouncedKeyword && !filterFormat && !filterStatus"
                @click="showUploadDialog = true"
                class="px-5 py-2.5 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                上传第一份文档
              </button>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div
                v-for="doc in filteredDocuments"
                :key="doc.id"
                class="group relative p-4 bg-white border border-gray-150 rounded-xl hover:border-blue-300 hover:shadow-md hover:shadow-blue-50 transition-all duration-200 cursor-default"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-center space-x-3 min-w-0 flex-1">
                    <div
                      class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                      :class="getFileIconBg(doc.format)"
                    >
                      <svg v-if="doc.format === 'docx'" class="w-5 h-5" :class="getFileIconColor(doc.format)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                      <svg v-else-if="doc.format === 'xlsx'" class="w-5 h-5" :class="getFileIconColor(doc.format)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                      </svg>
                      <svg v-else-if="doc.format === 'pdf'" class="w-5 h-5" :class="getFileIconColor(doc.format)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                      </svg>
                      <svg v-else-if="doc.format === 'txt'" class="w-5 h-5" :class="getFileIconColor(doc.format)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                      <svg v-else-if="doc.format === 'md'" class="w-5 h-5" :class="getFileIconColor(doc.format)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
                      </svg>
                    </div>
                    <div class="min-w-0 flex-1">
                      <h3 class="text-sm font-medium text-gray-800 truncate" :title="doc.name">{{ doc.name }}</h3>
                      <p class="text-xs text-gray-400 mt-0.5">{{ formatFileSize(doc.size) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex-shrink-0">
                    <button
                      @click="viewDocument(doc)"
                      class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="查看文档"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                      </svg>
                    </button>
                    <button
                      v-if="doc.status === 'ready'"
                      @click="viewChunks(doc)"
                      class="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="查看切片"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
                      </svg>
                    </button>
                    <button
                      @click="confirmDeleteDocument(doc)"
                      class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="删除"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>

                <div class="mt-3 flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span
                      class="inline-flex items-center px-2 py-0.5 text-xs rounded-full font-medium"
                      :class="getStatusClass(doc.status)"
                    >
                      <span v-if="isProcessing(doc.status)" class="w-1.5 h-1.5 rounded-full bg-current mr-1 animate-pulse"></span>
                      {{ getStatusText(doc.status) }}
                    </span>
                    <span v-if="doc.status === 'ready' && doc.chunkCount" class="text-xs text-gray-400">
                      {{ doc.chunkCount }} 段切片
                    </span>
                  </div>
                  <button
                    v-if="doc.status === 'failed'"
                    @click="retryDocument(doc)"
                    class="text-xs text-blue-600 hover:text-blue-700 font-medium hover:underline"
                  >
                    重试
                  </button>
                </div>

                <div v-if="doc.status === 'failed' && doc.errorMessage" class="mt-2">
                  <p class="text-xs text-red-500 truncate" :title="doc.errorMessage">{{ doc.errorMessage }}</p>
                </div>

                <div v-if="isProcessing(doc.status)" class="mt-3">
                  <div class="w-full bg-gray-100 rounded-full h-1">
                    <div class="h-1 bg-blue-500 rounded-full animate-pulse" style="width: 60%"></div>
                  </div>
                </div>

                <div class="mt-2 text-xs text-gray-400">
                  {{ doc.uploadTime }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="px-6 py-4 border-b border-gray-100">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-gray-800">知识召回设置</h2>
                <p class="text-xs text-gray-400 mt-0.5">配置知识库在生成测试用例时的检索参数</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-400">知识召回</span>
                <label class="flex items-center cursor-pointer">
                  <div class="relative">
                    <input type="checkbox" class="sr-only peer" v-model="recallSettings.enabled" />
                    <div class="w-10 h-5 bg-gray-200 rounded-full peer-checked:bg-blue-600 transition-colors duration-200"></div>
                    <div class="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full shadow-sm peer-checked:translate-x-5 transition-transform duration-200"></div>
                  </div>
                </label>
              </div>
            </div>
            <p class="text-xs text-gray-400 mt-2 leading-relaxed">开启后，AI 生成测试点和测试用例时将自动检索知识库中的相关内容作为参考，提升生成结果的专业性和准确性</p>
          </div>

          <div class="p-6" :class="{ 'opacity-50 pointer-events-none': !recallSettings.enabled }">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

              <div class="p-5 bg-gray-50/80 rounded-xl border border-gray-100">
                <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center space-x-2">
                  <div class="w-6 h-6 rounded-md bg-blue-100 flex items-center justify-center">
                    <svg class="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                  </div>
                  <span>召回参数</span>
                </h3>
                <div class="space-y-5">
                  <div>
                    <div class="flex items-center justify-between mb-1.5">
                      <label class="text-sm font-medium text-gray-600">召回数量 (top_k)</label>
                      <span class="text-xs font-mono text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">{{ recallSettings.topK }}</span>
                    </div>
                    <input
                      v-model.number="recallSettings.topK"
                      type="range"
                      min="1"
                      max="20"
                      step="1"
                      class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>1</span>
                      <span>20</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2 leading-relaxed">每次召回返回的最大切片数量。值越大，提供的参考知识越多，但可能引入不相关内容；值越小，结果越精准但可能遗漏有用信息</p>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-1.5">
                      <label class="text-sm font-medium text-gray-600">相似度阈值</label>
                      <span class="text-xs font-mono text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">{{ recallSettings.scoreThreshold.toFixed(2) }}</span>
                    </div>
                    <input
                      v-model.number="recallSettings.scoreThreshold"
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>0.00</span>
                      <span>1.00</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2 leading-relaxed">仅返回相似度分数 ≥ 此阈值的结果。提高阈值可过滤低相关内容，但可能减少有效召回；降低阈值可获取更多结果，但可能引入噪声</p>
                  </div>
                </div>
              </div>

              <div class="p-5 bg-gray-50/80 rounded-xl border border-gray-100">
                <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center space-x-2">
                  <div class="w-6 h-6 rounded-md bg-purple-100 flex items-center justify-center">
                    <svg class="w-3.5 h-3.5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
                    </svg>
                  </div>
                  <span>切片参数</span>
                </h3>
                <div class="space-y-5">
                  <div>
                    <div class="flex items-center justify-between mb-1.5">
                      <label class="text-sm font-medium text-gray-600">切片大小 (chunk_size)</label>
                      <span class="text-xs font-mono text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded">{{ recallSettings.chunkSize }}</span>
                    </div>
                    <input
                      v-model.number="recallSettings.chunkSize"
                      type="range"
                      min="100"
                      max="2000"
                      step="50"
                      class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                    />
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>100</span>
                      <span>2000</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2 leading-relaxed">每个切片的最大字符数。较大的切片保留更多上下文，但可能降低检索精度；较小的切片检索更精准，但可能丢失上下文关联</p>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-1.5">
                      <label class="text-sm font-medium text-gray-600">切片重叠度 (chunk_overlap)</label>
                      <span class="text-xs font-mono text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded">{{ recallSettings.chunkOverlap }}</span>
                    </div>
                    <input
                      v-model.number="recallSettings.chunkOverlap"
                      type="range"
                      min="0"
                      max="500"
                      step="10"
                      class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                    />
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>0</span>
                      <span>500</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2 leading-relaxed">相邻切片之间重叠的字符数。增大重叠度可避免关键信息被截断在切片边界，但会增加存储和计算开销</p>
                  </div>

                  <div class="p-2.5 bg-amber-50 border border-amber-200/60 rounded-lg">
                    <div class="flex items-start space-x-2">
                      <svg class="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                      </svg>
                      <p class="text-xs text-amber-700 leading-relaxed">修改切片参数后保存，将触发所有文档重新切片和向量化处理</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="p-5 bg-gray-50/80 rounded-xl border border-gray-100">
                <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center space-x-2">
                  <div class="w-6 h-6 rounded-md bg-green-100 flex items-center justify-center">
                    <svg class="w-3.5 h-3.5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                    </svg>
                  </div>
                  <span>召回策略</span>
                </h3>
                <div class="space-y-4">
                  <div class="space-y-2">
                    <label
                      v-for="strategy in strategyOptions"
                      :key="strategy.value"
                      class="flex items-start p-3 rounded-lg border cursor-pointer transition-all duration-200"
                      :class="recallSettings.recallStrategy === strategy.value
                        ? 'border-blue-300 bg-blue-50/50 shadow-sm'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-white'"
                      @click="recallSettings.recallStrategy = strategy.value"
                    >
                      <div class="flex items-center h-4 mt-0.5">
                        <div class="w-3.5 h-3.5 rounded-full border-2 flex items-center justify-center transition-colors"
                          :class="recallSettings.recallStrategy === strategy.value ? 'border-blue-600' : 'border-gray-300'"
                        >
                          <div v-if="recallSettings.recallStrategy === strategy.value" class="w-1.5 h-1.5 rounded-full bg-blue-600"></div>
                        </div>
                      </div>
                      <div class="ml-2.5 flex-1">
                        <div class="flex items-center space-x-2">
                          <span class="text-sm font-medium" :class="recallSettings.recallStrategy === strategy.value ? 'text-blue-700' : 'text-gray-700'">{{ strategy.label }}</span>
                          <span v-if="strategy.recommended" class="text-xs text-blue-600 bg-blue-100 px-1.5 py-0.5 rounded font-medium">推荐</span>
                        </div>
                        <p class="text-xs text-gray-500 mt-0.5">{{ strategy.description }}</p>
                        <p v-if="recallSettings.recallStrategy === strategy.value && strategy.detail" class="text-xs text-blue-500/70 mt-1 leading-relaxed">{{ strategy.detail }}</p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6 pt-5 border-t border-gray-100 flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <button
                  @click="saveSettings"
                  class="px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 active:scale-[0.98] transition-all shadow-sm shadow-blue-600/20"
                >
                  保存设置
                </button>
                <button
                  @click="showRecallTestDialog = true"
                  :disabled="!hasReadyDocs"
                  class="px-5 py-2.5 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  <span>召回测试</span>
                </button>
              </div>
              <span v-if="!hasReadyDocs" class="text-xs text-gray-400">请先上传并处理文档后再进行召回测试</span>
            </div>
          </div>
        </div>

      </div>
    </main>

    <div v-if="showUploadDialog" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showUploadDialog = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800">上传文档</h3>
          <button @click="showUploadDialog = false" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div
            class="border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200"
            :class="isDragOver ? 'border-blue-400 bg-blue-50/50' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50/50'"
            @dragover.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @drop.prevent="handleDrop"
          >
            <input
              type="file"
              ref="uploadFileInput"
              @change="handleFileSelect"
              accept=".docx,.xlsx,.pdf,.txt,.md"
              class="hidden"
              id="upload-file"
            />
            <label for="upload-file" class="cursor-pointer">
              <div class="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-7 h-7 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                </svg>
              </div>
              <p class="text-sm font-medium text-gray-600">点击或拖拽文件到此区域</p>
              <p class="text-xs text-gray-400 mt-1.5">支持 .docx .xlsx .pdf .txt .md 格式，单文件最大 50MB</p>
            </label>
          </div>

          <div v-if="selectedFile" class="mt-4 p-3 bg-blue-50/80 border border-blue-200/60 rounded-xl flex items-center justify-between">
            <div class="flex items-center space-x-2.5 min-w-0 flex-1">
              <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <span class="text-sm text-blue-700 truncate block">{{ selectedFile.name }}</span>
                <span class="text-xs text-blue-500">{{ formatFileSize(selectedFile.size) }}</span>
              </div>
            </div>
            <button @click="selectedFile = null" class="p-1 text-blue-400 hover:text-blue-600 rounded transition-colors flex-shrink-0">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div v-if="uploadError" class="mt-3 p-3 rounded-xl" :class="isDuplicateName ? 'bg-amber-50 border border-amber-200/60' : 'bg-red-50 border border-red-200/60'">
            <div class="flex items-center justify-between">
              <p class="text-sm" :class="isDuplicateName ? 'text-amber-700' : 'text-red-600'">{{ uploadError }}</p>
              <button
                v-if="isDuplicateName"
                @click="overwriteDuplicate"
                class="text-xs font-medium text-amber-700 bg-amber-100 hover:bg-amber-200 px-2.5 py-1 rounded-md transition-colors flex-shrink-0 ml-3"
              >
                覆盖
              </button>
            </div>
          </div>

          <button
            @click="uploadDocument"
            :disabled="!selectedFile || uploading"
            class="mt-5 w-full py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <svg v-if="uploading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>{{ uploading ? '上传中...' : '确认上传' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="showViewDialog" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showViewDialog = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center space-x-2.5">
            <div
              class="w-7 h-7 rounded-lg flex items-center justify-center"
              :class="viewingDocument ? getFileIconBg(viewingDocument.format) : ''"
            >
              <svg class="w-4 h-4" :class="viewingDocument ? getFileIconColor(viewingDocument.format) : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <h3 class="text-base font-semibold text-gray-800">{{ viewingDocument?.name }}</h3>
          </div>
          <button @click="showViewDialog = false" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto flex-1">
          <p class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{{ viewingDocument?.content }}</p>
        </div>
      </div>
    </div>

    <div v-if="showChunksDialog" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showChunksDialog = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-base font-semibold text-gray-800">切片详情</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ chunksDocument?.name }} · 共 {{ chunksDocument?.chunks?.length }} 个切片，平均长度 {{ chunksDocument?.avgChunkLength }} 字</p>
          </div>
          <button @click="showChunksDialog = false" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto flex-1 space-y-3">
          <div
            v-for="chunk in chunksDocument?.chunks"
            :key="chunk.index"
            class="p-4 bg-gray-50 rounded-xl border border-gray-100"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-gray-500 bg-white px-2 py-0.5 rounded-md border border-gray-100">切片 {{ chunk.index }}</span>
              <span class="text-xs text-gray-400">{{ chunk.length }} 字</span>
            </div>
            <p class="text-sm text-gray-700 leading-relaxed">{{ chunk.content }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDeleteDialog" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showDeleteDialog = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4">
        <div class="p-6 text-center">
          <div class="mx-auto w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mb-4">
            <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">确认删除</h3>
          <p class="text-sm text-gray-500 mb-6 leading-relaxed">确定要删除文档「{{ deletingDocument?.name }}」吗？<br/>删除后相关切片和向量数据将一并清除。</p>
          <div class="flex items-center justify-center space-x-3">
            <button
              @click="showDeleteDialog = false"
              class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              @click="deleteDocument"
              class="px-5 py-2.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 active:scale-[0.98] transition-all"
            >
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showRecallTestDialog" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showRecallTestDialog = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[85vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-base font-semibold text-gray-800">召回测试</h3>
            <p class="text-xs text-gray-400 mt-0.5">输入查询文本，验证知识库的召回效果</p>
          </div>
          <button @click="showRecallTestDialog = false" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto flex-1">
          <div class="mb-6">
            <div class="flex items-center space-x-3">
              <div class="relative flex-1">
                <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <input
                  v-model="recallTestQuery"
                  type="text"
                  placeholder="例如：用户登录功能的测试要点"
                  class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all"
                />
              </div>
              <button
                @click="testRecall"
                :disabled="!recallTestQuery.trim() || testingRecall"
                class="px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2 flex-shrink-0"
              >
                <svg v-if="testingRecall" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>{{ testingRecall ? '测试中...' : '开始测试' }}</span>
              </button>
            </div>
          </div>

          <div v-if="recallResults" class="space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-semibold text-gray-700">测试结果</h4>
              <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">召回 {{ recallResults.length }} 条结果 · 耗时 {{ recallTestElapsed }}ms</span>
            </div>

            <div v-if="recallResults.length === 0" class="text-center py-12">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <p class="text-sm text-gray-500 font-medium">未找到相关内容</p>
              <p class="text-xs text-gray-400 mt-1">请尝试调整查询文本或降低相似度阈值</p>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="(result, index) in recallResults"
                :key="index"
                class="p-4 bg-gray-50 rounded-xl border border-gray-100"
              >
                <div class="flex items-center justify-between mb-2.5">
                  <div class="flex items-center space-x-2.5">
                    <span class="text-xs font-semibold text-gray-500 bg-white px-2 py-0.5 rounded-md border border-gray-100">结果 {{ index + 1 }}</span>
                    <div class="flex items-center space-x-1">
                      <div class="w-16 bg-gray-200 rounded-full h-1.5">
                        <div
                          class="h-1.5 rounded-full transition-all duration-500"
                          :class="result.score >= 0.9 ? 'bg-green-500' : result.score >= 0.8 ? 'bg-blue-500' : 'bg-amber-500'"
                          :style="{ width: (result.score * 100) + '%' }"
                        ></div>
                      </div>
                      <span class="text-xs font-medium" :class="result.score >= 0.9 ? 'text-green-600' : result.score >= 0.8 ? 'text-blue-600' : 'text-amber-600'">{{ result.score.toFixed(2) }}</span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-1.5">
                    <div
                      class="w-4 h-4 rounded flex items-center justify-center"
                      :class="getFileIconBg(result.docFormat)"
                    >
                      <svg class="w-2.5 h-2.5" :class="getFileIconColor(result.docFormat)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                    </div>
                    <span class="text-xs text-gray-500">{{ result.docName }}</span>
                  </div>
                </div>
                <p class="text-sm text-gray-700 leading-relaxed">{{ result.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showReprocessDialog" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50" @click.self="showReprocessDialog = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4">
        <div class="p-6 text-center">
          <div class="mx-auto w-14 h-14 rounded-2xl bg-amber-50 flex items-center justify-center mb-4">
            <svg class="w-7 h-7 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">确认修改切片参数</h3>
          <p class="text-sm text-gray-500 mb-6 leading-relaxed">修改切片参数后需要重新处理所有文档，<br/>是否继续？</p>
          <div class="flex items-center justify-center space-x-3">
            <button
              @click="cancelReprocess"
              class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              @click="confirmReprocess"
              class="px-5 py-2.5 text-sm font-medium text-white bg-amber-600 rounded-lg hover:bg-amber-700 active:scale-[0.98] transition-all"
            >
              确认并重新处理
            </button>
          </div>
        </div>
      </div>
    </div>

    <transition name="toast">
      <div v-if="toast.show" class="fixed top-20 right-6 z-[60]">
        <div
          class="flex items-center space-x-2.5 px-4 py-3 rounded-xl shadow-lg border"
          :class="{
            'bg-green-50 border-green-200 text-green-700': toast.type === 'success',
            'bg-red-50 border-red-200 text-red-700': toast.type === 'error',
            'bg-blue-50 border-blue-200 text-blue-700': toast.type === 'info'
          }"
        >
          <svg v-if="toast.type === 'success'" class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <svg v-else-if="toast.type === 'error'" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <svg v-else class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
const MOCK_DOCUMENTS = [
  {
    id: '1',
    name: '银行核心系统测试用例编写规范.docx',
    format: 'docx',
    size: 262144,
    uploadTime: '2026-05-17 10:30',
    status: 'ready',
    chunkCount: 12,
    errorMessage: null,
    retryCount: 0,
    content: '本文档描述了银行核心系统测试用例编写的标准规范，包括用例命名规则、步骤编写要求、预期结果描述规范等内容。\n\n1. 用例命名规则\n用例命名应遵循"功能点+操作+预期结果"的格式，例如"用户登录-输入正确密码-登录成功"。\n\n2. 步骤编写要求\n每个测试步骤应包含：步骤名称、操作描述、预期结果。步骤描述应具体、可操作，避免模糊表述。\n\n3. 预期结果描述规范\n预期结果应可验证、可度量，避免使用"正常"、"正确"等模糊词汇。',
    chunks: [
      { index: 1, content: '本文档描述了银行核心系统测试用例编写的标准规范，包括用例命名规则、步骤编写要求、预期结果描述规范等内容。', length: 52 },
      { index: 2, content: '1. 用例命名规则\n用例命名应遵循"功能点+操作+预期结果"的格式，例如"用户登录-输入正确密码-登录成功"。', length: 56 },
      { index: 3, content: '2. 步骤编写要求\n每个测试步骤应包含：步骤名称、操作描述、预期结果。步骤描述应具体、可操作，避免模糊表述。', length: 56 },
      { index: 4, content: '3. 预期结果描述规范\n预期结果应可验证、可度量，避免使用"正常"、"正确"等模糊词汇。', length: 42 }
    ],
    avgChunkLength: 52
  },
  {
    id: '2',
    name: '系统安全测试指南.pdf',
    format: 'pdf',
    size: 1258291,
    uploadTime: '2026-05-16 14:20',
    status: 'ready',
    chunkCount: 8,
    errorMessage: null,
    retryCount: 0,
    content: '系统安全测试指南\n\n本指南涵盖银行系统安全测试的关键要点，包括身份认证、访问控制、数据加密等方面。\n\n身份认证测试要点：\n- 密码强度校验\n- 多因素认证流程\n- 登录失败锁定机制\n- 会话超时处理',
    chunks: [
      { index: 1, content: '本指南涵盖银行系统安全测试的关键要点，包括身份认证、访问控制、数据加密等方面。', length: 40 },
      { index: 2, content: '身份认证测试要点：密码强度校验、多因素认证流程、登录失败锁定机制、会话超时处理。', length: 42 }
    ],
    avgChunkLength: 41
  },
  {
    id: '3',
    name: '接口测试数据准备模板.xlsx',
    format: 'xlsx',
    size: 45056,
    uploadTime: '2026-05-15 09:15',
    status: 'ready',
    chunkCount: 5,
    errorMessage: null,
    retryCount: 0,
    content: '接口测试数据准备模板\n\n本模板用于规范接口测试的数据准备工作，包含以下字段：\n- 接口名称\n- 请求方法\n- 请求参数\n- 预期响应\n- 测试数据类型（正例/反例/边界值）',
    chunks: [
      { index: 1, content: '本模板用于规范接口测试的数据准备工作，包含接口名称、请求方法、请求参数、预期响应等字段。', length: 42 }
    ],
    avgChunkLength: 42
  },
  {
    id: '4',
    name: '交易流程测试规范.md',
    format: 'md',
    size: 15360,
    uploadTime: '2026-05-14 16:45',
    status: 'slicing',
    chunkCount: 0,
    errorMessage: null,
    retryCount: 0,
    content: '',
    chunks: [],
    avgChunkLength: 0
  },
  {
    id: '5',
    name: '异常场景处理指南.txt',
    format: 'txt',
    size: 8192,
    uploadTime: '2026-05-13 11:30',
    status: 'failed',
    chunkCount: 0,
    errorMessage: '文档内容为空或无法解析',
    retryCount: 3,
    content: '',
    chunks: [],
    avgChunkLength: 0
  },
  {
    id: '6',
    name: '移动端测试要点.docx',
    format: 'docx',
    size: 524288,
    uploadTime: '2026-05-12 08:20',
    status: 'vectorizing',
    chunkCount: 0,
    errorMessage: null,
    retryCount: 0,
    content: '',
    chunks: [],
    avgChunkLength: 0
  }
]

const MOCK_RECALL_RESULTS = [
  {
    content: '用户登录功能应覆盖以下测试要点：1）用户名和密码的输入验证；2）登录按钮的状态控制；3）登录失败处理机制；4）会话管理和超时处理。',
    score: 0.92,
    docName: '银行核心系统测试用例编写规范.docx',
    docFormat: 'docx'
  },
  {
    content: '登录安全测试应包含：密码强度校验、多次失败锁定、验证码机制、会话超时处理等关键测试点。建议每个安全测试点至少设计一个正例和一个反例。',
    score: 0.85,
    docName: '系统安全测试指南.pdf',
    docFormat: 'pdf'
  },
  {
    content: '反例设计原则：对于每个正常流程，至少设计一个异常场景测试用例。异常场景包括：输入为空、输入超长、输入特殊字符、网络异常等。',
    score: 0.78,
    docName: '银行核心系统测试用例编写规范.docx',
    docFormat: 'docx'
  }
]

export default {
  name: 'KnowledgeBase',
  data() {
    return {
      documents: [...MOCK_DOCUMENTS],
      searchKeyword: '',
      debouncedKeyword: '',
      debounceTimer: null,
      filterFormat: '',
      filterStatus: '',
      showUploadDialog: false,
      showViewDialog: false,
      showChunksDialog: false,
      showDeleteDialog: false,
      showRecallTestDialog: false,
      showReprocessDialog: false,
      selectedFile: null,
      uploading: false,
      uploadError: '',
      isDragOver: false,
      viewingDocument: null,
      chunksDocument: null,
      deletingDocument: null,
      testingRecall: false,
      recallTestQuery: '',
      recallResults: null,
      recallTestElapsed: 0,
      recallSettings: {
        topK: 5,
        scoreThreshold: 0.7,
        enabled: true,
        chunkSize: 500,
        chunkOverlap: 50,
        recallStrategy: 'hybrid'
      },
      oldChunkSettings: {
        chunkSize: 500,
        chunkOverlap: 50
      },
      storageInfo: {
        usedBytes: 524288000,
        maxBytes: 2147483648,
        usedText: '500 MB',
        maxText: '2 GB',
        usedPercentage: 24.4
      },
      strategyOptions: [
        { value: 'hybrid', label: '混合召回', description: '结合向量相似度和关键词匹配，兼顾语义理解和精确匹配', recommended: true, detail: '适合大多数场景，特别是包含专业术语、编号规则等需要精确匹配关键词的文档' },
        { value: 'vector', label: '纯向量召回', description: '仅基于语义相似度进行召回，理解意图而非字面匹配', recommended: false, detail: '适合自然语言描述为主的文档，能找到语义相近但用词不同的内容' }
      ],
      toast: {
        show: false,
        type: 'success',
        message: ''
      }
    }
  },
  watch: {
    searchKeyword(val) {
      clearTimeout(this.debounceTimer)
      this.debounceTimer = setTimeout(() => {
        this.debouncedKeyword = val
      }, 300)
    }
  },
  computed: {
    filteredDocuments() {
      let list = [...this.documents]
      if (this.debouncedKeyword) {
        const kw = this.debouncedKeyword.toLowerCase()
        list = list.filter(doc => doc.name.toLowerCase().includes(kw))
      }
      if (this.filterFormat) {
        list = list.filter(doc => doc.format === this.filterFormat)
      }
      if (this.filterStatus) {
        if (this.filterStatus === 'slicing') {
          list = list.filter(doc => ['uploading', 'slicing', 'vectorizing'].includes(doc.status))
        } else {
          list = list.filter(doc => doc.status === this.filterStatus)
        }
      }
      return list
    },
    hasReadyDocs() {
      return this.documents.some(doc => doc.status === 'ready')
    },
    readyDocCount() {
      return this.documents.filter(doc => doc.status === 'ready').length
    },
    processingDocCount() {
      return this.documents.filter(doc => ['uploading', 'slicing', 'vectorizing'].includes(doc.status)).length
    },
    isDuplicateName() {
      return this.uploadError.includes('同名文件')
    }
  },
  methods: {
    getFileIconBg(format) {
      const map = {
        docx: 'bg-blue-50',
        xlsx: 'bg-green-50',
        pdf: 'bg-red-50',
        txt: 'bg-gray-100',
        md: 'bg-purple-50'
      }
      return map[format] || 'bg-gray-100'
    },
    getFileIconColor(format) {
      const map = {
        docx: 'text-blue-500',
        xlsx: 'text-green-500',
        pdf: 'text-red-500',
        txt: 'text-gray-500',
        md: 'text-purple-500'
      }
      return map[format] || 'text-gray-500'
    },
    getStatusClass(status) {
      const map = {
        uploading: 'bg-blue-100 text-blue-700',
        slicing: 'bg-blue-100 text-blue-700',
        vectorizing: 'bg-blue-100 text-blue-700',
        ready: 'bg-green-100 text-green-700',
        failed: 'bg-red-100 text-red-700'
      }
      return map[status] || 'bg-gray-100 text-gray-600'
    },
    getStatusText(status) {
      const map = {
        uploading: '上传中',
        slicing: '切片中',
        vectorizing: '向量化中',
        ready: '已就绪',
        failed: '处理失败'
      }
      return map[status] || status
    },
    isProcessing(status) {
      return ['uploading', 'slicing', 'vectorizing'].includes(status)
    },
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, type, message }
      setTimeout(() => {
        this.toast.show = false
      }, 3000)
    },
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) this.validateAndSelectFile(file)
    },
    handleDrop(event) {
      this.isDragOver = false
      const file = event.dataTransfer.files[0]
      if (file) this.validateAndSelectFile(file)
    },
    validateAndSelectFile(file) {
      this.uploadError = ''
      const validFormats = ['.docx', '.xlsx', '.pdf', '.txt', '.md']
      const ext = '.' + file.name.split('.').pop().toLowerCase()
      if (!validFormats.includes(ext)) {
        this.uploadError = '不支持的文件格式，请上传 docx/xlsx/pdf/txt/md 文件'
        return
      }
      if (file.size > 50 * 1024 * 1024) {
        this.uploadError = '文件大小超过50MB限制'
        return
      }
      if (this.documents.length >= 100) {
        this.uploadError = '文档数量已达上限（100个），请删除后再上传'
        return
      }
      if (this.storageInfo.usedBytes + file.size > this.storageInfo.maxBytes) {
        this.uploadError = '存储空间不足，请删除部分文档后重试'
        return
      }
      const sameNameDoc = this.documents.find(d => d.name === file.name)
      if (sameNameDoc) {
        this.uploadError = '已存在同名文件，是否覆盖？'
        return
      }
      this.selectedFile = file
    },
    overwriteDuplicate() {
      if (this.selectedFile) {
        const idx = this.documents.findIndex(d => d.name === this.selectedFile.name)
        if (idx !== -1) {
          this.documents.splice(idx, 1)
        }
        this.uploadError = ''
      }
    },
    async uploadDocument() {
      this.uploading = true
      await new Promise(resolve => setTimeout(resolve, 1500))
      const newDoc = {
        id: Date.now().toString(),
        name: this.selectedFile.name,
        format: this.selectedFile.name.split('.').pop().toLowerCase(),
        size: this.selectedFile.size,
        uploadTime: new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-'),
        status: 'slicing',
        chunkCount: 0,
        errorMessage: null,
        retryCount: 0,
        content: '',
        chunks: [],
        avgChunkLength: 0
      }
      this.documents.unshift(newDoc)
      this.selectedFile = null
      this.uploadError = ''
      this.showUploadDialog = false
      this.uploading = false
      this.showToast('文档上传成功，正在处理中...', 'success')
    },
    viewDocument(doc) {
      this.viewingDocument = doc
      this.showViewDialog = true
    },
    viewChunks(doc) {
      this.chunksDocument = doc
      this.showChunksDialog = true
    },
    confirmDeleteDocument(doc) {
      this.deletingDocument = doc
      this.showDeleteDialog = true
    },
    deleteDocument() {
      const idx = this.documents.findIndex(d => d.id === this.deletingDocument.id)
      if (idx !== -1) {
        this.documents.splice(idx, 1)
      }
      this.showDeleteDialog = false
      this.deletingDocument = null
      this.showToast('文档已删除', 'success')
    },
    retryDocument(doc) {
      if (doc.retryCount >= 3) {
        this.showToast('重试次数已达上限，请检查文档内容或联系管理员', 'error')
        return
      }
      doc.retryCount++
      doc.status = 'slicing'
      doc.errorMessage = null
      this.showToast('正在重新处理文档...', 'info')
    },
    saveSettings() {
      const chunkChanged = this.recallSettings.chunkSize !== this.oldChunkSettings.chunkSize ||
        this.recallSettings.chunkOverlap !== this.oldChunkSettings.chunkOverlap
      if (chunkChanged) {
        this.showReprocessDialog = true
        return
      }
      this.showToast('设置已保存', 'success')
    },
    cancelReprocess() {
      this.showReprocessDialog = false
      this.recallSettings.chunkSize = this.oldChunkSettings.chunkSize
      this.recallSettings.chunkOverlap = this.oldChunkSettings.chunkOverlap
    },
    confirmReprocess() {
      this.oldChunkSettings.chunkSize = this.recallSettings.chunkSize
      this.oldChunkSettings.chunkOverlap = this.recallSettings.chunkOverlap
      this.documents.forEach(doc => {
        if (doc.status === 'ready') {
          doc.status = 'slicing'
          doc.chunkCount = 0
          doc.chunks = []
        }
      })
      this.showReprocessDialog = false
      this.showToast('切片参数已更新，所有文档正在重新处理...', 'info')
    },
    async testRecall() {
      this.testingRecall = true
      this.recallResults = null
      const start = Date.now()
      await new Promise(resolve => setTimeout(resolve, 800))
      this.recallResults = MOCK_RECALL_RESULTS
      this.recallTestElapsed = Date.now() - start
      this.testingRecall = false
    }
  }
}
</script>

<style>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>