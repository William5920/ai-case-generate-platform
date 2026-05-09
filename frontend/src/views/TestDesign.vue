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
                class="block px-4 py-3 bg-blue-50 text-blue-600 rounded-lg font-medium"
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
          <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-800">测试设计（脑图）</h2>
              <div class="flex items-center space-x-4">
                <label class="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    v-model="knowledgeBaseEnabled"
                    class="w-4 h-4 text-blue-600 rounded"
                  />
                  <span class="text-sm text-gray-600">启用知识库</span>
                </label>
                <button 
                  @click="handleQuickGenerate"
                  :disabled="isGenerating"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {{ isGenerating ? '生成中...' : '快速生成' }}
                </button>
                <button @click="handleExport" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  导出Excel
                </button>
              </div>
            </div>
            
            <div v-if="progress > 0" class="mt-4">
              <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>生成进度</span>
                <span>{{ progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: progress + '%' }"
                ></div>
              </div>
              <p class="mt-2 text-sm text-gray-500">{{ progressText }}</p>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="mind-map-container h-96 bg-gray-50 rounded-lg p-4 overflow-auto">
              <div class="mind-map" ref="mindMapRef">
                <div v-for="(node, index) in mindMapData" :key="index" class="mind-map-node">
                  <div 
                    class="node-header flex items-center space-x-2 p-3 bg-blue-500 text-white rounded-lg cursor-pointer"
                    @click="toggleNode(index)"
                    @contextmenu.prevent="showContextMenu($event, node, index, 'root')"
                  >
                    <svg class="w-5 h-5" :class="node.expanded ? 'rotate-90' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                    <span class="font-medium">{{ node.name }}</span>
                    <span class="ml-auto text-xs" :class="getStatusClass(node.status)">{{ getStatusText(node.status) }}</span>
                  </div>
                  
                  <div v-if="node.expanded" class="ml-6 mt-2 space-y-2">
                    <div 
                      v-for="(req, reqIndex) in node.children" 
                      :key="reqIndex"
                      class="mind-map-node"
                    >
                      <div 
                        class="node-header flex items-center space-x-2 p-2 bg-blue-100 text-blue-800 rounded-lg cursor-pointer"
                        @click="toggleReqNode(index, reqIndex)"
                        @contextmenu.prevent="showContextMenu($event, req, reqIndex, 'requirement')"
                      >
                        <svg class="w-4 h-4" :class="req.expanded ? 'rotate-90' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        <span>{{ req.name }}</span>
                        <span class="ml-auto text-xs" :class="getStatusClass(req.status)">{{ getStatusText(req.status) }}</span>
                      </div>
                      
                      <div v-if="req.expanded" class="ml-6 mt-2 space-y-2">
                        <div 
                          v-for="(point, pointIndex) in req.children" 
                          :key="pointIndex"
                          class="mind-map-node"
                        >
                          <div 
                            class="node-header flex items-center space-x-2 p-2 bg-green-100 text-green-800 rounded-lg cursor-pointer"
                            @click="togglePointNode(index, reqIndex, pointIndex)"
                            @contextmenu.prevent="showContextMenu($event, point, pointIndex, 'testPoint')"
                          >
                            <svg class="w-4 h-4" :class="point.expanded ? 'rotate-90' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                            <span>{{ point.name }}</span>
                            <span v-if="point.source === 'AI'" class="ml-2 px-2 py-0.5 bg-yellow-200 text-yellow-800 text-xs rounded">AI</span>
                            <span v-else class="ml-2 px-2 py-0.5 bg-purple-200 text-purple-800 text-xs rounded">人工</span>
                            <span v-if="point.marked" class="ml-1">📌</span>
                          </div>
                          
                          <div v-if="point.expanded" class="ml-6 mt-2 space-y-2">
                            <div 
                              v-for="(caseItem, caseIndex) in point.children" 
                              :key="caseIndex"
                              class="p-2 bg-gray-100 text-gray-800 rounded-lg"
                              @contextmenu.prevent="showContextMenu($event, caseItem, caseIndex, 'testCase')"
                              @dblclick="editTestCase(index, reqIndex, pointIndex, caseIndex)"
                            >
                              <div class="flex items-center justify-between">
                                <span class="font-medium">{{ caseItem.caseName }}</span>
                                <span v-if="caseItem.source === 'AI'" class="px-2 py-0.5 bg-yellow-200 text-yellow-800 text-xs rounded">AI</span>
                                <span v-else class="px-2 py-0.5 bg-purple-200 text-purple-800 text-xs rounded">人工</span>
                              </div>
                              <div class="mt-1 text-sm text-gray-500">类型：{{ caseItem.caseProperty }}</div>
                              <div class="mt-1 text-sm text-gray-500">前置条件：{{ caseItem.preCondition }}</div>
                              <div class="mt-2 space-y-1">
                                <div v-for="(step, stepIndex) in caseItem.steps" :key="stepIndex" class="text-xs text-gray-600">
                                  <span class="font-medium">{{ step.name }}：</span>{{ step.description }} → {{ step.stepExpectedResult }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div 
            v-if="contextMenu.visible"
            class="fixed bg-white rounded-lg shadow-lg border py-2 z-50"
            :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
          >
            <button 
              v-if="contextMenu.type === 'requirement'"
              @click="addTestPoint"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm"
            >
              添加测试点
            </button>
            <button 
              v-if="contextMenu.type === 'requirement'"
              @click="aiAdjust"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm"
            >
              AI调整
            </button>
            <button 
              v-if="contextMenu.type === 'testPoint'"
              @click="editTestPoint"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm"
            >
              编辑
            </button>
            <button 
              v-if="contextMenu.type === 'testPoint'"
              @click="deleteTestPoint"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm text-red-600"
            >
              删除
            </button>
            <button 
              v-if="contextMenu.type === 'testPoint'"
              @click="addTestCase"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm"
            >
              添加测试用例
            </button>
            <button 
              v-if="contextMenu.type === 'testPoint'"
              @click="toggleMark"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm"
            >
              {{ contextMenu.node.marked ? '取消标记保留' : '标记保留' }}
            </button>
            <button 
              v-if="contextMenu.type === 'testCase'"
              @click="editTestCaseDialog"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm"
            >
              编辑
            </button>
            <button 
              v-if="contextMenu.type === 'testCase'"
              @click="deleteTestCase"
              class="w-full px-4 py-2 text-left hover:bg-gray-100 text-sm text-red-600"
            >
              删除
            </button>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestDesign',
  data() {
    return {
      knowledgeBaseEnabled: false,
      isGenerating: false,
      progress: 0,
      progressText: '',
      mindMapData: [
        {
          id: 'root-1',
          name: '用户登录系统需求',
          status: 'completed',
          expanded: true,
          children: [
            {
              id: 'req-1',
              name: '实现用户登录功能，支持用户名密码验证',
              status: 'completed',
              expanded: true,
              children: [
                {
                  id: 'point-1',
                  name: '用户名输入验证',
                  source: 'AI',
                  marked: false,
                  expanded: true,
                  children: [
                    {
                      id: 'case-1',
                      caseName: '用户正常登录系统',
                      caseProperty: '正例',
                      preCondition: '用户已注册并拥有有效的账号和密码',
                      source: 'AI',
                      steps: [
                        { name: '输入用户名', description: '在登录页输入正确的用户名', stepExpectedResult: '用户名输入框显示输入的用户名' },
                        { name: '输入密码', description: '在登录页输入正确的密码', stepExpectedResult: '密码输入框显示输入的密码' },
                        { name: '点击登录按钮', description: '点击登录按钮', stepExpectedResult: '系统跳转至用户主页' }
                      ]
                    },
                    {
                      id: 'case-2',
                      caseName: '用户登录失败-密码错误',
                      caseProperty: '反例',
                      preCondition: '用户已注册但密码错误',
                      source: 'AI',
                      steps: [
                        { name: '输入用户名', description: '在登录页输入用户名', stepExpectedResult: '用户名输入框显示输入的用户名' },
                        { name: '输入错误密码', description: '在登录页输入错误的密码', stepExpectedResult: '密码输入框显示输入的密码' },
                        { name: '点击登录按钮', description: '点击登录按钮', stepExpectedResult: '系统提示密码错误' }
                      ]
                    }
                  ]
                },
                {
                  id: 'point-2',
                  name: '密码输入验证',
                  source: '人工',
                  marked: true,
                  expanded: false,
                  children: []
                }
              ]
            }
          ]
        }
      ],
      contextMenu: {
        visible: false,
        x: 0,
        y: 0,
        type: '',
        node: null,
        indices: {}
      }
    }
  },
  methods: {
    toggleNode(index) {
      this.mindMapData[index].expanded = !this.mindMapData[index].expanded
    },
    toggleReqNode(rootIndex, reqIndex) {
      this.mindMapData[rootIndex].children[reqIndex].expanded = !this.mindMapData[rootIndex].children[reqIndex].expanded
    },
    togglePointNode(rootIndex, reqIndex, pointIndex) {
      this.mindMapData[rootIndex].children[reqIndex].children[pointIndex].expanded = !this.mindMapData[rootIndex].children[reqIndex].children[pointIndex].expanded
    },
    showContextMenu(event, node, index, type) {
      this.contextMenu = {
        visible: true,
        x: event.clientX,
        y: event.clientY,
        type,
        node,
        indices: { root: index }
      }
      document.addEventListener('click', this.hideContextMenu)
    },
    hideContextMenu() {
      this.contextMenu.visible = false
      document.removeEventListener('click', this.hideContextMenu)
    },
    getStatusClass(status) {
      switch (status) {
        case 'pending': return 'text-gray-500'
        case 'generating': return 'text-yellow-500'
        case 'completed': return 'text-green-500'
        default: return 'text-gray-500'
      }
    },
    getStatusText(status) {
      switch (status) {
        case 'pending': return '待生成'
        case 'generating': return '生成中'
        case 'completed': return '已完成'
        default: return '待生成'
      }
    },
    async handleQuickGenerate() {
      this.isGenerating = true
      this.progress = 0
      this.progressText = '正在初始化...'
      
      const totalSteps = 10
      for (let i = 0; i <= totalSteps; i++) {
        await new Promise(resolve => setTimeout(resolve, 500))
        this.progress = Math.round((i / totalSteps) * 100)
        this.progressText = `正在处理需求 ${Math.min(i, 5)}/5，已完成 ${this.progress}%`
      }
      
      this.progressText = '生成完成！'
      this.isGenerating = false
    },
    handleExport() {
      alert('Excel导出功能即将实现')
    },
    addTestPoint() {
      alert('添加测试点功能')
      this.hideContextMenu()
    },
    aiAdjust() {
      alert('AI调整功能')
      this.hideContextMenu()
    },
    editTestPoint() {
      alert('编辑测试点功能')
      this.hideContextMenu()
    },
    deleteTestPoint() {
      alert('删除测试点功能')
      this.hideContextMenu()
    },
    addTestCase() {
      alert('添加测试用例功能')
      this.hideContextMenu()
    },
    toggleMark() {
      this.contextMenu.node.marked = !this.contextMenu.node.marked
      this.hideContextMenu()
    },
    editTestCaseDialog() {
      alert('编辑测试用例功能')
      this.hideContextMenu()
    },
    deleteTestCase() {
      alert('删除测试用例功能')
      this.hideContextMenu()
    },
    editTestCase() {
      alert('双击编辑测试用例')
    },
    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.mind-map-container {
  position: relative;
}

.node-header:hover {
  filter: brightness(0.95);
}
</style>
