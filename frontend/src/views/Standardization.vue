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
                class="block px-4 py-3 bg-blue-50 text-blue-600 rounded-lg font-medium"
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
                class="block px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              >
                知识库
              </router-link>
            </nav>
          </div>
        </aside>

        <main class="flex-1">
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-6">需求录入</h2>
            
            <div class="mb-6">
              <label class="flex items-center space-x-4">
                <input 
                  type="radio" 
                  v-model="inputMode" 
                  value="text" 
                  class="w-4 h-4 text-blue-600"
                />
                <span class="text-gray-700">文本输入</span>
              </label>
              <label class="flex items-center space-x-4 ml-8">
                <input 
                  type="radio" 
                  v-model="inputMode" 
                  value="document" 
                  class="w-4 h-4 text-blue-600"
                />
                <span class="text-gray-700">文档上传</span>
              </label>
            </div>

            <div v-if="inputMode === 'text'" class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">需求文本</label>
              <textarea 
                v-model="requirementText"
                rows="6"
                placeholder="请输入需求描述..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              ></textarea>
            </div>

            <div v-else class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">上传文档</label>
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
                <input 
                  type="file" 
                  ref="fileInput"
                  @change="handleFileUpload"
                  accept=".docx,.xlsx"
                  class="hidden"
                  id="document-upload"
                />
                <label for="document-upload" class="cursor-pointer">
                  <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                  </svg>
                  <p class="mt-2 text-sm text-gray-600">点击上传文档</p>
                  <p class="text-xs text-gray-400">支持 .docx, .xlsx 格式</p>
                </label>
                <div v-if="uploadedFile" class="mt-4 p-2 bg-green-50 rounded-lg inline-block">
                  <span class="text-green-600 text-sm">{{ uploadedFile.name }}</span>
                </div>
              </div>
            </div>

            <button 
              @click="handleStandardize"
              :disabled="!canStandardize"
              class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ standardizing ? '标准化处理中...' : '文档标准化助手' }}
            </button>

            <div v-if="standardizedContent" class="mt-8">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">标准文档预览</h3>
              <textarea 
                v-model="standardizedContent"
                rows="10"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
              ></textarea>
              <div class="mt-4 flex justify-end space-x-4">
                <button @click="showDialog = true" class="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                  多轮对话调整
                </button>
                <button @click="handleSplitRequirements" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  需求拆分
                </button>
              </div>
            </div>

            <div v-if="splitRequirements.length > 0" class="mt-8">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">拆分后的需求</h3>
              <div class="space-y-3">
                <div 
                  v-for="(req, index) in splitRequirements" 
                  :key="index"
                  class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div class="flex-1">
                    <input 
                      v-model="req.content"
                      class="w-full bg-transparent border-none outline-none"
                    />
                  </div>
                  <div class="flex items-center space-x-2">
                    <button @click="removeRequirement(index)" class="p-2 text-red-500 hover:bg-red-50 rounded-lg">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
              <button 
                @click="addRequirement" 
                class="mt-4 px-4 py-2 border border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500 transition-colors"
              >
                + 添加需求
              </button>
            </div>
          </div>

          <div v-if="showDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4">
              <div class="flex items-center justify-between p-4 border-b">
                <h3 class="text-lg font-semibold">多轮对话</h3>
                <button @click="showDialog = false" class="p-2 hover:bg-gray-100 rounded-lg">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              <div class="p-4 h-80 overflow-y-auto space-y-4">
                <div 
                  v-for="(msg, index) in dialogMessages" 
                  :key="index"
                  :class="['p-3 rounded-lg', msg.isUser ? 'bg-blue-100 ml-8' : 'bg-gray-100 mr-8']"
                >
                  {{ msg.content }}
                </div>
              </div>
              <div class="p-4 border-t">
                <div class="flex space-x-2">
                  <input 
                    v-model="dialogInput"
                    @keyup.enter="sendMessage"
                    type="text"
                    placeholder="输入消息..."
                    class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button @click="sendMessage" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    发送
                  </button>
                </div>
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
  name: 'Standardization',
  data() {
    return {
      inputMode: 'text',
      requirementText: '',
      uploadedFile: null,
      standardizing: false,
      standardizedContent: '',
      splitRequirements: [],
      showDialog: false,
      dialogMessages: [],
      dialogInput: ''
    }
  },
  computed: {
    canStandardize() {
      if (this.inputMode === 'text') {
        return this.requirementText.trim().length > 0
      }
      return this.uploadedFile !== null
    }
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.uploadedFile = file
      }
    },
    async handleStandardize() {
      this.standardizing = true
      
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      this.standardizedContent = `# 需求文档

## 1. 需求概述
${this.requirementText || this.uploadedFile?.name}

## 2. 功能需求

### 2.1 核心功能
- 用户登录功能
- 数据查询功能
- 数据导出功能

## 3. 非功能需求
- 响应时间：< 3秒
- 可用性：99.5%

## 4. 约束条件
- 仅支持已注册用户访问`
      
      this.standardizing = false
    },
    handleSplitRequirements() {
      this.splitRequirements = [
        { content: '实现用户登录功能，支持用户名密码验证' },
        { content: '实现数据查询功能，支持多条件筛选' },
        { content: '实现数据导出功能，支持Excel格式' }
      ]
    },
    addRequirement() {
      this.splitRequirements.push({ content: '' })
    },
    removeRequirement(index) {
      this.splitRequirements.splice(index, 1)
    },
    sendMessage() {
      if (!this.dialogInput.trim()) return
      
      this.dialogMessages.push({ content: this.dialogInput, isUser: true })
      this.dialogInput = ''
      
      setTimeout(() => {
        this.dialogMessages.push({ content: '好的，我已经理解您的需求，正在为您调整...', isUser: false })
      }, 500)
    },
    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>
