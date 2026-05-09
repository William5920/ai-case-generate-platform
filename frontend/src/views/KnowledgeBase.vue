<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-800">智能测试用例平台</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-600">{{ $store.getters.user?.username }}</span>
            <button @click="handleLogout" class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex gap-6">
        <aside class="w-64 flex-shrink-0">
          <div class="bg-white rounded-lg shadow-sm p-4">
            <nav class="space-y-2">
              <router-link 
                to="/standardization" 
                class="block px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              >
                需求标准化
              </router-link>
              <router-link 
                to="/test-design" 
                class="block px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              >
                测试设计
              </router-link>
              <router-link 
                to="/knowledge-base" 
                class="block px-4 py-3 bg-blue-50 text-blue-600 rounded-lg font-medium"
              >
                知识库
              </router-link>
            </nav>
          </div>
        </aside>

        <main class="flex-1">
          <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-800">文档管理</h2>
              <button @click="showUploadDialog = true" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                上传文档
              </button>
            </div>
            
            <div class="mt-6">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div 
                  v-for="doc in documents" 
                  :key="doc.id"
                  class="p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex items-center space-x-3">
                      <svg class="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                      <div>
                        <h3 class="font-medium text-gray-800">{{ doc.name }}</h3>
                        <p class="text-sm text-gray-500">{{ doc.size }}</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-2">
                      <button @click="viewDocument(doc)" class="p-2 text-blue-500 hover:bg-blue-50 rounded-lg">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                      </button>
                      <button @click="deleteDocument(doc.id)" class="p-2 text-red-500 hover:bg-red-50 rounded-lg">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div class="mt-3 text-sm text-gray-500">
                    上传时间：{{ doc.uploadTime }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-6">知识召回设置</h2>
            
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">召回数量</label>
                <input 
                  v-model="recallSettings.count"
                  type="number"
                  min="1"
                  max="50"
                  class="w-48 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">相似度阈值</label>
                <input 
                  v-model="recallSettings.threshold"
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  class="w-full"
                />
                <p class="mt-1 text-sm text-gray-500">{{ recallSettings.threshold }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">是否启用知识召回</label>
                <label class="inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="recallSettings.enabled"
                    class="w-5 h-5 text-blue-600 rounded"
                  />
                  <span class="ml-2 text-gray-700">启用</span>
                </label>
              </div>
              
              <div class="flex space-x-4">
                <button 
                  @click="saveSettings"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  保存设置
                </button>
                <button 
                  @click="testRecall"
                  :disabled="testingRecall"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {{ testingRecall ? '测试中...' : '召回测试' }}
                </button>
              </div>
              
              <div v-if="recallResult" class="mt-4 p-4 bg-gray-50 rounded-lg">
                <h3 class="font-medium text-gray-800 mb-2">测试结果</h3>
                <p class="text-sm text-gray-600">召回准确率：{{ recallResult.accuracy }}%</p>
                <p class="text-sm text-gray-600">召回数量：{{ recallResult.count }}</p>
              </div>
            </div>
          </div>

          <div v-if="showUploadDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
              <div class="flex items-center justify-between p-4 border-b">
                <h3 class="text-lg font-semibold">上传文档</h3>
                <button @click="showUploadDialog = false" class="p-2 hover:bg-gray-100 rounded-lg">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              <div class="p-6">
                <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
                  <input 
                    type="file" 
                    ref="uploadFileInput"
                    @change="handleFileSelect"
                    accept=".docx,.xlsx,.pdf,.txt"
                    class="hidden"
                    id="upload-file"
                  />
                  <label for="upload-file" class="cursor-pointer">
                    <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                    </svg>
                    <p class="mt-2 text-sm text-gray-600">点击上传文档</p>
                    <p class="text-xs text-gray-400">支持 .docx, .xlsx, .pdf, .txt 格式</p>
                  </label>
                </div>
                
                <div v-if="selectedFile" class="mt-4 p-2 bg-green-50 rounded-lg">
                  <span class="text-green-600 text-sm">{{ selectedFile.name }}</span>
                </div>
                
                <button 
                  @click="uploadDocument"
                  :disabled="!selectedFile || uploading"
                  class="mt-6 w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {{ uploading ? '上传中...' : '确认上传' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="showViewDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden">
              <div class="flex items-center justify-between p-4 border-b">
                <h3 class="text-lg font-semibold">{{ viewingDocument?.name }}</h3>
                <button @click="showViewDialog = false" class="p-2 hover:bg-gray-100 rounded-lg">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              <div class="p-6 overflow-y-auto max-h-[60vh]">
                <p class="text-gray-800 whitespace-pre-wrap">{{ viewingDocument?.content }}</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KnowledgeBase',
  data() {
    return {
      documents: [
        {
          id: '1',
          name: '测试用例编写规范.docx',
          size: '256 KB',
          uploadTime: '2024-01-15 10:30',
          content: '本文档描述了测试用例编写的标准规范...'
        },
        {
          id: '2',
          name: '系统需求文档.pdf',
          size: '1.2 MB',
          uploadTime: '2024-01-14 14:20',
          content: '系统需求文档内容...'
        },
        {
          id: '3',
          name: '接口测试指南.txt',
          size: '12 KB',
          uploadTime: '2024-01-13 09:15',
          content: '接口测试指南内容...'
        }
      ],
      showUploadDialog: false,
      showViewDialog: false,
      selectedFile: null,
      uploading: false,
      viewingDocument: null,
      recallSettings: {
        count: 10,
        threshold: 0.8,
        enabled: true
      },
      testingRecall: false,
      recallResult: null
    }
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.selectedFile = file
      }
    },
    async uploadDocument() {
      this.uploading = true
      
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const newDoc = {
        id: Date.now().toString(),
        name: this.selectedFile.name,
        size: this.formatFileSize(this.selectedFile.size),
        uploadTime: new Date().toLocaleString('zh-CN'),
        content: `文档内容预览：${this.selectedFile.name}`
      }
      
      this.documents.unshift(newDoc)
      this.selectedFile = null
      this.showUploadDialog = false
      this.uploading = false
    },
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    },
    viewDocument(doc) {
      this.viewingDocument = doc
      this.showViewDialog = true
    },
    deleteDocument(id) {
      if (confirm('确定要删除这个文档吗？')) {
        this.documents = this.documents.filter(doc => doc.id !== id)
      }
    },
    saveSettings() {
      alert('设置已保存')
    },
    async testRecall() {
      this.testingRecall = true
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      this.recallResult = {
        accuracy: 85,
        count: 8
      }
      
      this.testingRecall = false
    },
    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>
