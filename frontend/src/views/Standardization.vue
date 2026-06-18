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
            class="group p-3 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-200"
            :class="{ 'bg-blue-50 border-blue-200': item.id === activeHistoryId }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-700 truncate">{{ item.title }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ item.date }}</p>
              </div>
              <button
                @click.stop="confirmDeleteHistory(item)"
                class="flex-shrink-0 ml-2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-50 transition-all"
                title="删除"
              >
                <svg class="w-3.5 h-3.5 text-gray-400 hover:text-red-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto p-6 space-y-6">
      <div class="flex items-center justify-center space-x-3 py-2">
        <div class="flex items-center space-x-2 cursor-pointer group" @click="goToStep(1)">
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all"
            :class="activeStep === 1 ? 'bg-blue-600 text-white shadow-md' : (step1Completed ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-500')"
          >1</div>
          <span class="text-sm font-medium transition-colors" :class="activeStep === 1 ? 'text-gray-800' : 'text-gray-400'">需求录入</span>
        </div>
        <div class="w-10 h-px bg-gray-300"></div>
        <div class="flex items-center space-x-2 cursor-pointer group" :class="{ 'pointer-events-none opacity-50': !step1Completed }" @click="goToStep(2)">
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all"
            :class="activeStep === 2 ? 'bg-blue-600 text-white shadow-md' : (step2Completed ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-400')"
          >2</div>
          <span class="text-sm font-medium transition-colors" :class="activeStep === 2 ? 'text-gray-800' : (step2Completed ? 'text-gray-500' : 'text-gray-400')">需求探索与标准化</span>
        </div>
        <div class="w-10 h-px bg-gray-300"></div>
        <div class="flex items-center space-x-2 cursor-pointer group" :class="{ 'pointer-events-none opacity-50': !step2Completed }" @click="goToStep(3)">
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all"
            :class="activeStep === 3 ? 'bg-blue-600 text-white shadow-md' : (step3Completed ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-400')"
          >3</div>
          <span class="text-sm font-medium transition-colors" :class="activeStep === 3 ? 'text-gray-800' : (step3Completed ? 'text-gray-500' : 'text-gray-400')">需求拆分</span>
        </div>
      </div>

      <!-- [已注释] 暂时去除草稿恢复功能
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
          <button @click="dismissDraftRestore" class="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">丢弃</button>
          <button @click="restoreDraft" class="px-4 py-1.5 text-xs text-white bg-amber-500 hover:bg-amber-600 rounded-lg transition-colors font-medium">恢复草稿</button>
        </div>
      </div>
      -->

      <div v-show="activeStep === 1" class="space-y-6">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center space-x-3">
              <h2 class="text-lg font-semibold text-gray-800">需求录入</h2>
              <!-- [已注释] 暂时去除草稿状态显示
              <span v-if="draftStatus === 'unsaved'" class="flex items-center space-x-1 text-xs text-amber-500">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span><span>未保存</span>
              </span>
              <span v-else-if="draftStatus === 'saved'" class="flex items-center space-x-1 text-xs text-green-500">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>已保存</span>
              </span>
              -->
            </div>
            <div class="flex bg-gray-100 rounded-lg p-1">
              <button @click="switchInputMode('text')" class="px-4 py-2 text-sm font-medium rounded-md" :class="inputMode === 'text' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                <svg class="w-4 h-4 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>文本输入
              </button>
              <button @click="switchInputMode('document')" class="px-4 py-2 text-sm font-medium rounded-md" :class="inputMode === 'document' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700'">
                <svg class="w-4 h-4 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>文档上传
              </button>
            </div>
          </div>
          <div v-if="inputMode === 'text'" class="mb-6">
            <div class="relative">
              <textarea v-model="requirementText" rows="10" placeholder="请输入需求描述，例如：用户登录功能需要支持用户名密码登录，登录成功后跳转到首页。密码需要支持大小写字母、数字和特殊字符的组合。连续5次登录失败后需要锁定账户30分钟。" class="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm leading-relaxed placeholder-gray-400"></textarea>
              <div class="absolute bottom-3 right-3 text-xs text-gray-400">{{ requirementText.length }} 字</div>
            </div>
          </div>
          <div v-else class="mb-6">
            <div class="border-2 border-dashed rounded-lg text-center transition-colors cursor-pointer flex items-center justify-center" style="min-height: 280px;" :class="uploadedFile ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'" @click="$refs.fileInput.click()" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @drop.prevent="handleDrop">
              <input type="file" ref="fileInput" @change="handleFileUpload" accept=".doc,.docx,.pdf,.md,.xlsx" class="hidden" />
              <div v-if="!uploadedFile">
                <div class="w-14 h-14 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                  <svg class="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                </div>
                <p class="text-sm text-gray-600 font-medium">点击或拖拽文件到此处上传</p>
                <p class="text-xs text-gray-400 mt-1">支持 .doc、.docx、.pdf、.md、.xlsx 格式，单个文件不超过 10MB</p>
              </div>
              <div v-else class="flex items-center justify-center space-x-3">
                <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </div>
                <div class="text-left">
                  <p class="text-sm text-gray-700 font-medium">{{ uploadedFile.name }}</p>
                  <p class="text-xs text-gray-400">{{ formatFileSize(uploadedFile.size) }}</p>
                </div>
                <button @click.stop="uploadedFile = null" class="p-1.5 hover:bg-red-50 rounded-lg transition-colors">
                  <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center space-x-3 mb-4">
            <h2 class="text-lg font-semibold text-gray-800">选择需求文档模板</h2>
            <span v-if="selectedTemplateId && inputMode === 'document' && aiRecommended" class="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full flex items-center space-x-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg><span>AI推荐</span>
            </span>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div v-for="tpl in templates" :key="tpl.id" @click="selectTemplate(tpl.id)" class="p-4 rounded-xl border-2 cursor-pointer transition-all" :class="selectedTemplateId === tpl.id ? 'border-blue-500 bg-blue-50 shadow-sm' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <span class="text-2xl">{{ tpl.icon }}</span>
                  <span class="text-sm font-semibold text-gray-800">{{ tpl.name }}</span>
                </div>
                <div v-if="selectedTemplateId === tpl.id" class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                </div>
              </div>
              <p class="text-xs text-gray-500 mb-3">{{ tpl.description }}</p>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="tag in tpl.tags" :key="tag" class="px-2 py-0.5 text-xs rounded-full" :class="selectedTemplateId === tpl.id ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'">{{ tag }}</span>
              </div>
            </div>
          </div>
          <div v-if="selectedTemplate" class="mt-4 p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center space-x-2 mb-2">
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <span class="text-xs font-medium text-gray-600">模板预览</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div v-for="section in selectedTemplate.sections" :key="section.id" class="px-2 py-1.5 bg-white rounded border border-gray-200">
                <span class="text-xs text-gray-700 font-medium">{{ section.title }}</span>
                <div class="mt-1 space-y-0.5">
                  <div v-for="child in section.children" :key="child.id" class="text-xs text-gray-400 pl-2">{{ child.title }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end mt-6">
            <p v-if="!canStartExplore" class="text-xs text-gray-400 mr-3">请输入需求并选择模板后开始</p>
            <button @click="startExplore" :disabled="!canStartExplore || loading" class="px-5 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1.5">
              <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              <span>{{ loading ? '需求理解中...' : '开始需求探索' }}</span>
            </button>
          </div>
        </div>
      </div>

      <div v-show="activeStep === 2" class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div v-if="step2State === 'exploring'" class="flex flex-col" style="height: calc(100vh - 180px);">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              </div>
              <div>
                <h3 class="text-base font-semibold text-gray-800">AI 需求探索</h3>
                <p class="text-xs text-gray-400">AI 正在通过提问深入了解您的需求</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-500">需求理解度</span>
                <div class="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500" :class="understandingScore >= 80 ? 'bg-green-500' : understandingScore >= 50 ? 'bg-blue-500' : 'bg-amber-500'" :style="{ width: understandingScore + '%' }"></div>
                </div>
                <span class="text-xs font-medium" :class="understandingScore >= 80 ? 'text-green-600' : understandingScore >= 50 ? 'text-blue-600' : 'text-amber-600'">{{ understandingScore }}%</span>
              </div>
              <div class="flex items-center space-x-2 text-xs text-gray-400">
                <span>{{ exploredDimensions.length }}/{{ totalDimensions }} 维度</span>
              </div>
            </div>
          </div>
          <div ref="exploreMessagesContainer" class="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
            <div v-if="exploreMessages.length === 0 && !aiTyping" class="flex flex-col items-center justify-center h-full text-center py-12">
              <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
                <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              </div>
              <p class="text-sm text-gray-500 font-medium">AI 正在分析您的需求...</p>
              <p class="text-xs text-gray-400 mt-1">即将开始提问以深入了解需求细节</p>
            </div>
            <div v-for="(msg, index) in exploreMessages" :key="index" class="flex" :class="msg.isUser ? 'justify-end' : 'justify-start'">
              <div v-if="!msg.isUser" class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0 mr-2">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              </div>
              <div class="max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed" :class="msg.isUser ? 'bg-blue-600 text-white rounded-br-md' : 'bg-white text-gray-700 rounded-bl-md shadow-sm border border-gray-100'">
                <p class="whitespace-pre-wrap">{{ msg.content }}</p>
                <div v-if="msg.quickReplies && msg.quickReplies.length > 0 && !msg.replied" class="mt-2 pt-2 border-t border-gray-100 space-y-1.5">
                  <button v-for="(reply, ri) in msg.quickReplies" :key="ri" @click="sendExploreQuickReply(reply, index)" class="block w-full text-left px-3 py-1.5 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">💡 {{ reply }}</button>
                </div>
              </div>
              <div v-if="msg.isUser" class="w-8 h-8 bg-gray-300 rounded-lg flex items-center justify-center flex-shrink-0 ml-2">
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
              </div>
            </div>
            <div v-if="aiTyping" class="flex justify-start">
              <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0 mr-2">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              </div>
              <div class="px-4 py-3 bg-white rounded-2xl rounded-bl-md shadow-sm border border-gray-100">
                <div class="flex space-x-1.5">
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 bg-white flex-shrink-0">
            <div v-if="understandingScore >= 80 && !userTriggeredGenerate" class="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span class="text-sm text-green-700 font-medium">AI 已充分理解您的需求，可以开始生成标准化文档</span>
              </div>
              <button @click="generateDocument" class="px-4 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>生成文档</span>
              </button>
            </div>
            <div class="flex items-center space-x-2">
              <input v-model="exploreInput" @keyup.enter="sendExploreMessage" type="text" placeholder="输入您的回答或补充信息..." class="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm" />
              <button @click="sendExploreMessage" :disabled="!exploreInput.trim()" class="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg><span class="text-sm">发送</span>
              </button>
              <button v-if="understandingScore < 80" @click="generateDocument" class="px-4 py-2.5 bg-gray-600 text-white rounded-xl hover:bg-gray-700 transition-colors flex items-center space-x-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span class="text-sm">直接生成</span>
              </button>
            </div>
          </div>
        </div>

        <div v-else-if="step2State === 'generating'" class="flex flex-col items-center justify-center" style="height: calc(100vh - 180px);">
          <div class="text-center">
            <div class="w-20 h-20 mx-auto mb-6 relative">
              <div class="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              </div>
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mb-2">正在生成标准化文档</h3>
            <p class="text-sm text-gray-500">AI 正在基于探索对话中确认的信息生成文档...</p>
            <div class="mt-4 flex items-center justify-center space-x-1">
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>
          </div>
        </div>

        <div v-else-if="step2State === 'editing'" class="flex" style="height: calc(100vh - 180px);">
          <div class="flex-1 flex flex-col min-w-0">
            <div class="px-6 py-3 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
              <div class="flex items-center space-x-3">
                <h2 class="text-lg font-semibold text-gray-800">标准文档预览</h2>
                <span v-if="draftStatus === 'unsaved'" class="flex items-center space-x-1 text-xs text-amber-500"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span><span>未保存</span></span>
                <span v-else-if="draftStatus === 'saved'" class="flex items-center space-x-1 text-xs text-green-500"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>已保存</span></span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="flex items-center space-x-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>AI 生成</span></span>
                <select v-model="activeVersionId" @change="switchVersion(activeVersionId)" class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-600 outline-none focus:ring-2 focus:ring-blue-500 max-w-[120px] truncate">
                  <option v-for="v in docVersions" :key="v.id" :value="v.id">v{{ v.id }} - {{ v.description }}</option>
                </select>
                <button v-if="docVersions.length > 0 && activeVersionId !== docVersions[docVersions.length - 1].id" @click="restoreVersion(activeVersionId)" class="px-2.5 py-1.5 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors flex items-center space-x-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg><span>恢复此版本</span>
                </button>
              </div>
            </div>
            <div class="mb-3 px-6 pt-3">
              <div class="p-3 rounded-xl border relative" :class="[qualityLoading ? 'bg-blue-50 border-blue-200' : qualityLevel.bg]" :style="{ borderColor: qualityLoading ? '#93C5FD' : qualityLevel.color }">
                <div v-if="qualityLoading" class="absolute inset-0 bg-white/60 rounded-xl flex items-center justify-center z-10">
                  <div class="flex items-center space-x-2">
                    <svg class="w-4 h-4 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <span class="text-sm text-blue-600 font-medium">评估中...</span>
                  </div>
                </div>
                <div v-else class="flex items-start gap-4">
                  <div class="flex-shrink-0 flex flex-col items-center">
                    <div class="relative w-14 h-14">
                      <svg class="w-14 h-14 transform -rotate-90" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="none" stroke="#E5E7EB" stroke-width="5" /><circle cx="32" cy="32" r="28" fill="none" :stroke="qualityLevel.color" stroke-width="5" stroke-linecap="round" :stroke-dasharray="scoreRingDasharray" :stroke-dashoffset="scoreRingDashoffset" class="transition-all duration-700" /></svg>
                      <div class="absolute inset-0 flex items-center justify-center"><span class="text-lg font-bold" :class="qualityLevel.text">{{ qualityReport.overall }}</span></div>
                    </div>
                    <span class="text-xs mt-0.5" :class="qualityLevel.text">{{ qualityLevel.label }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="grid grid-cols-3 gap-3">
                      <div>
                        <div class="flex items-center justify-between mb-1"><span class="text-xs text-gray-500">完整性</span><span class="text-xs font-medium" :class="qualityReport.completeness.score >= 60 ? 'text-green-600' : 'text-red-500'">{{ qualityReport.completeness.score }}%</span></div>
                        <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full rounded-full transition-all duration-500" :class="qualityReport.completeness.score >= 60 ? 'bg-green-500' : 'bg-red-400'" :style="{ width: qualityReport.completeness.score + '%' }"></div></div>
                      </div>
                      <div>
                        <div class="flex items-center justify-between mb-1"><span class="text-xs text-gray-500">清晰度</span><span class="text-xs font-medium" :class="qualityReport.clarity.score >= 60 ? 'text-green-600' : 'text-red-500'">{{ qualityReport.clarity.score }}%</span></div>
                        <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full rounded-full transition-all duration-500" :class="qualityReport.clarity.score >= 60 ? 'bg-green-500' : 'bg-red-400'" :style="{ width: Math.max(0, qualityReport.clarity.score) + '%' }"></div></div>
                      </div>
                      <div>
                        <div class="flex items-center justify-between mb-1"><span class="text-xs text-gray-500">一致性</span><span class="text-xs font-medium" :class="qualityReport.consistency.score >= 60 ? 'text-green-600' : 'text-red-500'">{{ qualityReport.consistency.score }}%</span></div>
                        <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full rounded-full transition-all duration-500" :class="qualityReport.consistency.score >= 60 ? 'bg-green-500' : 'bg-red-400'" :style="{ width: Math.max(0, qualityReport.consistency.score) + '%' }"></div></div>
                      </div>
                    </div>
                    <div v-if="qualityReport.suggestions.length > 0" class="mt-2">
                      <ul class="space-y-0.5">
                        <li v-for="(s, i) in qualityReport.suggestions.slice(0, 2)" :key="i" class="text-xs text-gray-500 flex items-start space-x-1.5"><span class="text-amber-500 flex-shrink-0 mt-0.5">•</span><span>{{ s }}</span></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto px-6 pb-2">
              <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center space-x-2">
                  <div class="flex space-x-1.5"><div class="w-3 h-3 rounded-full bg-red-400"></div><div class="w-3 h-3 rounded-full bg-yellow-400"></div><div class="w-3 h-3 rounded-full bg-green-400"></div></div>
                  <span class="text-xs text-gray-400 ml-2">Markdown 预览 · 可编辑</span>
                </div>
                <textarea v-model="standardizedContent" rows="12" class="w-full px-6 py-4 border-none outline-none resize-none font-mono text-sm leading-relaxed text-gray-700 bg-white"></textarea>
              </div>
            </div>
            <div class="px-6 py-3 border-t border-gray-100 flex items-center justify-between flex-shrink-0">
              <div class="flex items-center space-x-2 text-xs text-gray-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span>可直接编辑文档，或使用右侧AI助手调整</span>
              </div>
              <div class="flex items-center space-x-3">
                <button @click="uploadToKnowledgeBase" :disabled="uploadingToKB" class="px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors text-sm font-medium flex items-center space-x-1.5 border border-gray-200 disabled:opacity-50">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
                  <span>{{ uploadingToKB ? '上传中...' : '上传知识库' }}</span>
                </button>
                <div class="relative">
                  <button @click="showExportMenu = !showExportMenu" class="px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors text-sm font-medium flex items-center space-x-1.5 border border-gray-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>导出</span>
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </button>
                  <div v-if="showExportMenu" class="fixed inset-0 z-10" @click="showExportMenu = false"></div>
                  <div v-if="showExportMenu" class="absolute right-0 bottom-full mb-1 w-44 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-20">
                    <button @click="handleExport('markdown')" class="w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"><svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg><span>Markdown (.md)</span></button>
                    <button @click="handleExport('docx')" class="w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"><svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg><span>Word 文档 (.docx)</span></button>
                  </div>
                </div>
                <button @click="handleSplitRequirements" :disabled="splitting" class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center space-x-1.5 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg v-if="splitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7M4 7c0-2 1-3 3-3h10c2 0 3 1 3 3M4 7h16M9 11l3 3 3-3"></path></svg>
                  <span>{{ splitting ? '拆分中...' : '需求拆分' }}</span>
                </button>
              </div>
            </div>
          </div>
          <div class="w-80 flex-shrink-0 border-l border-gray-200 flex flex-col bg-white">
            <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-md flex items-center justify-center"><svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg></div>
                <span class="text-sm font-medium text-gray-700">AI 助手</span>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-gray-50">
              <div v-if="editMessages.length === 0" class="text-center py-8">
                <p class="text-xs text-gray-400">告诉AI您想调整的内容</p>
                <div class="mt-3 space-y-1.5">
                  <button @click="sendEditQuickMessage('请帮我补充安全性相关的需求')" class="block w-full text-left px-3 py-1.5 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors">💡 补充安全性需求</button>
                  <button @click="sendEditQuickMessage('请帮我细化性能指标要求')" class="block w-full text-left px-3 py-1.5 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors">💡 细化性能指标</button>
                  <button @click="sendEditQuickMessage('请帮我补充异常场景的处理')" class="block w-full text-left px-3 py-1.5 text-xs text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:text-blue-600 transition-colors">💡 补充异常场景</button>
                </div>
              </div>
              <div v-for="(msg, index) in editMessages" :key="index" class="flex" :class="msg.isUser ? 'justify-end' : 'justify-start'">
                <div class="max-w-[90%] px-3 py-2 rounded-xl text-xs leading-relaxed" :class="msg.isUser ? 'bg-blue-600 text-white rounded-br-sm' : 'bg-white text-gray-700 rounded-bl-sm shadow-sm border border-gray-100'">
                  <div v-if="msg.type === 'proposal'">
                    <p class="text-xs text-blue-600 font-medium mb-1">💭 AI 建议：</p>
                    <p class="whitespace-pre-wrap">{{ msg.content }}</p>
                    <div v-if="!msg.confirmed && !msg.rejected" class="flex items-center space-x-2 mt-2 pt-1.5 border-t border-gray-100">
                      <button @click="confirmEditProposal(index)" class="px-2.5 py-1 text-xs bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors">采纳</button>
                      <button @click="rejectEditProposal(index)" class="px-2.5 py-1 text-xs bg-gray-200 text-gray-600 rounded-md hover:bg-gray-300 transition-colors">不采纳</button>
                    </div>
                    <div v-else class="mt-1.5 pt-1.5 border-t border-gray-100">
                      <span v-if="msg.confirmed" class="text-xs text-green-600">✅ 已采纳</span>
                      <span v-else class="text-xs text-gray-400">❌ 未采纳</span>
                    </div>
                  </div>
                  <p v-else class="whitespace-pre-wrap">{{ msg.content }}</p>
                </div>
              </div>
              <div v-if="aiTyping" class="flex justify-start">
                <div class="px-3 py-2 bg-white rounded-xl rounded-bl-sm shadow-sm border border-gray-100">
                  <div class="flex space-x-1.5">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="px-4 py-3 border-t border-gray-100 flex-shrink-0">
              <div class="flex items-center space-x-2">
                <input v-model="editInput" @keyup.enter="sendEditMessage" type="text" placeholder="描述调整内容..." class="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-xs" />
                <button @click="sendEditMessage" :disabled="!editInput.trim()" class="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeStep === 3" class="bg-white rounded-lg shadow-sm p-6">
        <div v-if="splitRequirements.length === 0" class="text-center py-16">
          <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-2xl flex items-center justify-center"><svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7M4 7c0-2 1-3 3-3h10c2 0 3 1 3 3M4 7h16"></path></svg></div>
          <p class="text-sm text-gray-500">请先在「需求探索与标准化」步骤中完成标准化并点击「需求拆分」</p>
          <button @click="activeStep = 2" class="mt-4 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">返回需求标准化</button>
        </div>
        <template v-else>
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <h2 class="text-lg font-semibold text-gray-800">拆分后的需求</h2>
              <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{{ splitRequirements.length }} 条</span>
              <!-- [已注释] 暂时去除草稿状态显示
              <span v-if="draftStatus === 'unsaved'" class="flex items-center space-x-1 text-xs text-amber-500"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span><span>未保存</span></span>
              <span v-else-if="draftStatus === 'saved'" class="flex items-center space-x-1 text-xs text-green-500"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>已保存</span></span>
              -->
            </div>
            <button @click="addRequirement" class="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center space-x-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg><span>手动添加</span>
            </button>
          </div>
          <div class="space-y-2">
            <div v-for="(req, index) in splitRequirements" :key="index" class="flex items-start group p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-transparent hover:border-gray-200">
              <span class="text-xs text-gray-400 w-6 flex-shrink-0 pt-0.5">{{ index + 1 }}.</span>
              <div class="flex-1 mx-3"><textarea v-model="req.content" ref="splitTextareas" class="w-full bg-transparent border-none outline-none text-sm text-gray-700 placeholder-gray-400 resize-none overflow-hidden" :placeholder="'需求 ' + (index + 1) + ' 的描述...'" rows="1" @input="autoResizeTextarea($event)"></textarea></div>
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity pt-0.5">
                <button class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path></svg></button>
                <button @click="removeRequirement(index)" class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
              </div>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-gray-100 flex justify-end">
            <button @click="confirmAndGoToTestDesign" class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">确认并进入测试设计</button>
          </div>
        </template>
      </div>
    </main>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/40" @click="showDeleteConfirm = false"></div>
      <div class="relative bg-white rounded-xl shadow-2xl w-80 p-6 z-10">
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div>
            <h3 class="text-base font-semibold text-gray-800">确认删除</h3>
            <p class="text-sm text-gray-500 mt-0.5">删除后无法恢复</p>
          </div>
        </div>
        <p class="text-sm text-gray-600 mb-5">确定要删除「{{ deleteTargetTitle }}」吗？</p>
        <div class="flex justify-end space-x-3">
          <button @click="showDeleteConfirm = false" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">取消</button>
          <button @click="deleteHistory" :disabled="deletingHistory" class="px-4 py-2 text-sm text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50">
            {{ deletingHistory ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { TEMPLATES, getTemplateById, recommendTemplate } from '@/utils/requirementTemplate'
import { analyzeQuality, getLevelConfig } from '@/utils/qualityScorer'
// [已注释] 暂时去除保存草稿和加载草稿功能
// import { initDraftManager, getDraft, hasDraft, scheduleAutoSave, saveNow, clearDraft, formatSaveTime } from '@/utils/draftManager'
import { exportMarkdown, exportDocx } from '@/utils/exportUtils'
import { requirementAPI, templateAPI, exploreAPI, standardizeAPI, uploadAPI, historyAPI } from '@/api'

export default {
  name: 'Standardization',
  data() {
    return {
      activeStep: 1,
      inputMode: 'text',
      requirementText: '',
      uploadedFile: null,
      uploadedFileId: null,
      dragOver: false,
      selectedTemplateId: 'user-story',
      aiRecommended: false,
      templates: TEMPLATES,
      step2State: 'exploring',
      exploreMessages: [],
      exploreInput: '',
      understandingScore: 0,
      exploredDimensions: [],
      currentDimensionIndex: 0,
      aiTyping: false,
      userTriggeredGenerate: false,
      standardizedContent: '',
      editMessages: [],
      editInput: '',
      showAiSidebar: true,
      splitRequirements: [],
      docVersions: [],
      activeVersionId: null,
      versionCounter: 0,
      historyList: [],
      activeHistoryId: null,
      draftStatus: 'idle',
      showDraftRestore: false,
      draftSavedTime: '',
      showExportMenu: false,
      uploadingToKB: false,
      currentRequirementId: null,
      exploreSessionId: null,
      loading: false,
      splitting: false,
      qualityReportData: null,
      qualityLoading: false,
      uploadingFile: false,
      templatesLoaded: false,
      maxCompletedStep: 0,
      isLoadingHistory: false,
      showDeleteConfirm: false,
      deleteTargetId: null,
      deleteTargetTitle: '',
      deletingHistory: false
    }
  },
  computed: {
    selectedTemplate() {
      return getTemplateById(this.selectedTemplateId)
    },
    totalDimensions() {
      return this.selectedTemplate ? this.selectedTemplate.dimensions.length : 0
    },
    canStartExplore() {
      if (this.inputMode === 'text') {
        return this.requirementText.trim().length > 0 && this.selectedTemplateId
      }
      return this.uploadedFile !== null && this.selectedTemplateId
    },
    step1Completed() {
      if (this.maxCompletedStep >= 1) return true
      return this.canStartExplore && (this.exploreMessages.length > 0 || this.step2State !== 'exploring')
    },
    step2Completed() {
      if (this.maxCompletedStep >= 2) return true
      return this.standardizedContent.length > 0 && this.step2State === 'editing'
    },
    step3Completed() {
      if (this.maxCompletedStep >= 3) return true
      return this.splitRequirements.length > 0
    },
    qualityReport() {
      if (this.qualityReportData) return this.qualityReportData
      return analyzeQuality('', this.selectedTemplateId)
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
      if (this.isLoadingHistory) return
      this.clearDownstreamSteps()
      // [已注释] 暂时去除草稿保存
      // this.triggerAutoSave()
      // 暂时注释掉需求文档模板推荐接口调用
      // if (this.inputMode === 'text' && this.requirementText.length > 10) {
      //   clearTimeout(this._recommendTimer)
      //   this._recommendTimer = setTimeout(async () => {
      //     try {
      //       const res = await templateAPI.recommend({ content: this.requirementText })
      //       if (res.success && res.data && res.data.templateId && res.data.templateId !== this.selectedTemplateId) {
      //         this.selectedTemplateId = res.data.templateId
      //         this.aiRecommended = true
      //       }
      //     } catch (e) {
      //       const recommended = recommendTemplate(this.requirementText)
      //       if (recommended !== this.selectedTemplateId) {
      //         this.selectedTemplateId = recommended
      //         this.aiRecommended = true
      //       }
      //     }
      //   }, 1000)
      // }
    },
    uploadedFile(val) {
      if (this.isLoadingHistory) return
      this.clearDownstreamSteps()
      if (val && this.inputMode === 'document') {
        this.autoRecommendTemplate()
      }
    },
    standardizedContent() {
      // [已注释] 暂时去除自动保存草稿功能
      // this.triggerAutoSave()
    },
    splitRequirements: {
      deep: true,
      handler() {
        // [已注释] 暂时去除自动保存草稿功能
        // this.triggerAutoSave()
        this.$nextTick(() => { this.resizeAllSplitTextareas() })
      }
    },
    activeStep() {
      // [已注释] 暂时去除自动保存草稿功能
      // this.doSaveNow()
      if (this.activeStep === 3) {
        this.$nextTick(() => { this.resizeAllSplitTextareas() })
      }
    }
  },
  mounted() {
    // [已注释] 暂时去除草稿管理功能
    // initDraftManager((status) => { this.draftStatus = status })
    this.loadTemplates()
    this.loadHistoryList()
    // [已注释] 暂时去除草稿恢复功能
    // if (hasDraft()) {
    //   this.restoreDraft()
    // }
  },
  // [已注释] 暂时去除草稿保存功能
  // beforeDestroy() {
  //   this.doSaveNow()
  // },
  // activated() {
  //   initDraftManager((status) => { this.draftStatus = status })
  // },
  // deactivated() {
  //   this.doSaveNow()
  // },
  methods: {
    extractMessageContent(value) {
      if (typeof value === 'string') {
        if (value.trim().startsWith('{') || value.trim().startsWith('[')) {
          try {
            const parsed = JSON.parse(value)
            return this.extractMessageContent(parsed)
          } catch (e) {
            return value
          }
        }
        return value
      }
      if (typeof value === 'object' && value !== null) {
        return value.content || value.text || value.message || value.question || JSON.stringify(value)
      }
      return String(value)
    },
    scrollToBottomOfExploreMessages() {
      this.$nextTick(() => {
        const container = this.$refs.exploreMessagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    shortDesc(text, maxLen) {
      maxLen = maxLen || 10
      if (!text) return ''
      return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
    },
    normalizeQualityData(data) {
      const d = data
      const overallVal = d.overall ?? d.score ?? 0
      let level = (d.level || '').toLowerCase()
      const VALID_LEVELS = ['good', 'medium', 'poor', 'empty']
      if (!VALID_LEVELS.includes(level)) {
        level = overallVal >= 80 ? 'good' : overallVal >= 60 ? 'medium' : overallVal > 0 ? 'poor' : 'empty'
      }
      return {
        overall: overallVal,
        completeness: typeof d.completeness === 'object' && d.completeness !== null
          ? { score: d.completeness.score ?? 0, details: d.completeness.details || [] }
          : { score: d.completeness ?? 0, details: d.completenessDetails || [] },
        clarity: typeof d.clarity === 'object' && d.clarity !== null
          ? { score: d.clarity.score ?? 0, issues: d.clarity.issues || [] }
          : { score: d.clarity ?? 0, issues: d.clarityIssues || [] },
        consistency: typeof d.consistency === 'object' && d.consistency !== null
          ? { score: d.consistency.score ?? 0, issues: d.consistency.issues || [] }
          : { score: d.consistency ?? 0, issues: d.consistencyIssues || [] },
        suggestions: d.suggestions || d.improvements || [],
        level
      }
    },
    async fetchQualityScore() {
      if (!this.standardizedContent || !this.currentRequirementId) return
      this.qualityLoading = true
      try {
        const res = await standardizeAPI.qualityScore({
          requirementId: this.currentRequirementId,
          content: this.standardizedContent,
          templateId: this.selectedTemplateId
        })
        if (res.success && res.data) {
          this.qualityReportData = this.normalizeQualityData(res.data)
        }
      } catch (e) {
        console.error('获取质量评分失败，使用本地评分:', e)
        this.qualityReportData = analyzeQuality(this.standardizedContent, this.selectedTemplateId)
      } finally {
        this.qualityLoading = false
      }
    },
    // [已注释] 暂时去除草稿保存功能
    // draftData() {
    //   return {
    //     activeStep: this.activeStep,
    //     inputMode: this.inputMode,
    //     requirementText: this.requirementText,
    //     selectedTemplateId: this.selectedTemplateId,
    //     step2State: this.step2State,
    //     exploreMessages: this.exploreMessages,
    //     understandingScore: this.understandingScore,
    //     exploredDimensions: this.exploredDimensions,
    //     currentDimensionIndex: this.currentDimensionIndex,
    //     standardizedContent: this.standardizedContent,
    //     editMessages: this.editMessages,
    //     splitRequirements: this.splitRequirements,
    //     docVersions: this.docVersions,
    //     activeVersionId: this.activeVersionId,
    //     versionCounter: this.versionCounter,
    //     currentRequirementId: this.currentRequirementId,
    //     exploreSessionId: this.exploreSessionId,
    //     uploadedFileId: this.uploadedFileId,
    //     maxCompletedStep: this.maxCompletedStep
    //   }
    // },
    // [已注释] 暂时去除草稿保存功能
    // triggerAutoSave() {
    //   if (!this.hasDraftContent()) {
    //     this.draftStatus = 'idle'
    //     return
    //   }
    //   scheduleAutoSave(() => this.draftData())
    // },
    // doSaveNow() {
    //   if (!this.hasDraftContent()) return
    //   saveNow(() => this.draftData())
    // },
    // hasDraftContent() {
    //   return !!(this.requirementText.trim() ||
    //     this.uploadedFileId ||
    //     this.standardizedContent ||
    //     this.currentRequirementId ||
    //     this.exploreMessages.length > 0)
    // },
    // restoreDraft() {
    //   const draft = getDraft()
    //   if (!draft) return
    //   this.activeStep = draft.activeStep || 1
    //   this.inputMode = draft.inputMode || 'text'
    //   this.requirementText = draft.requirementText || ''
    //   this.selectedTemplateId = draft.selectedTemplateId || 'user-story'
    //   this.step2State = draft.step2State || 'exploring'
    //   this.exploreMessages = draft.exploreMessages || []
    //   this.understandingScore = draft.understandingScore || 0
    //   this.exploredDimensions = draft.exploredDimensions || []
    //   this.currentDimensionIndex = draft.currentDimensionIndex || 0
    //   this.standardizedContent = draft.standardizedContent || ''
    //   this.editMessages = draft.editMessages || []
    //   this.splitRequirements = draft.splitRequirements || []
    //   this.docVersions = draft.docVersions || []
    //   this.activeVersionId = draft.activeVersionId || null
    //   this.versionCounter = draft.versionCounter || 0
    //   this.currentRequirementId = draft.currentRequirementId || null
    //   this.exploreSessionId = draft.exploreSessionId || null
    //   this.uploadedFileId = draft.uploadedFileId || null
    //   this.maxCompletedStep = draft.maxCompletedStep || 0
    //   this.showDraftRestore = false
    //   this.draftStatus = 'idle'
    // },
    // dismissDraftRestore() {
    //   this.showDraftRestore = false
    //   clearDraft()
    // },
    goToStep(step) {
      if (step === 2 && !this.step1Completed) return
      if (step === 3 && !this.step2Completed) return
      if (this.maxCompletedStep > 0 && step > this.maxCompletedStep) return
      this.activeStep = step
    },
    switchInputMode(mode) {
      this.inputMode = mode
      // 切换方式时保留两者的数据，不再清空
      this.aiRecommended = false
    },
    selectTemplate(id) {
      this.selectedTemplateId = id
      this.aiRecommended = false
    },
    async autoRecommendTemplate() {
      // 暂时注释掉需求文档模板推荐接口调用
      // try {
      //   const content = (this.requirementText || '') + ' ' + (this.uploadedFile ? this.uploadedFile.name : '')
      //   const res = await templateAPI.recommend({ content })
      //   if (res.success && res.data && res.data.templateId) {
      //     this.selectedTemplateId = res.data.templateId
      //     this.aiRecommended = true
      //   }
      // } catch (e) {
      //   const content = (this.requirementText || '') + ' ' + (this.uploadedFile ? this.uploadedFile.name : '')
      //   this.selectedTemplateId = recommendTemplate(content)
      //   this.aiRecommended = true
      // }
    },
    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      this.uploadedFile = file
      this.uploadingFile = true
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('type', 'requirement')
        const res = await uploadAPI.uploadFile(formData)
        if (res.success && res.data) {
          this.uploadedFileId = res.data.fileId
        }
      } catch (e) {
        console.error('文件上传失败:', e)
        this.$message?.error?.('文件上传失败，请稍后重试') || alert('文件上传失败，请稍后重试')
        this.uploadedFile = null
        this.uploadedFileId = null
      } finally {
        this.uploadingFile = false
      }
    },
    async handleDrop(event) {
      this.dragOver = false
      const file = event.dataTransfer.files[0]
      if (!file) return
      this.uploadedFile = file
      this.uploadingFile = true
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('type', 'requirement')
        const res = await uploadAPI.uploadFile(formData)
        if (res.success && res.data) {
          this.uploadedFileId = res.data.fileId
        }
      } catch (e) {
        console.error('文件上传失败:', e)
        this.$message?.error?.('文件上传失败，请稍后重试') || alert('文件上传失败，请稍后重试')
        this.uploadedFile = null
        this.uploadedFileId = null
      } finally {
        this.uploadingFile = false
      }
    },
    formatFileSize(bytes) {
      if (!bytes) return ''
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    },
    clearDownstreamSteps() {
      this.exploreMessages = []
      this.understandingScore = 0
      this.exploredDimensions = []
      this.currentDimensionIndex = 0
      this.step2State = 'exploring'
      this.standardizedContent = ''
      this.editMessages = []
      this.splitRequirements = []
      this.docVersions = []
      this.activeVersionId = null
      this.versionCounter = 0
      this.currentRequirementId = null
      this.exploreSessionId = null
      this.maxCompletedStep = 0
    },
    async loadTemplates() {
      if (this.templatesLoaded) return
      try {
        const res = await templateAPI.list()
        if (res.success && res.data && res.data.templates && res.data.templates.length > 0) {
          this.templates = res.data.templates
          this.templatesLoaded = true
        }
      } catch (e) {
        console.error('加载模板失败，使用本地模板:', e)
      }
    },
    async loadHistoryList() {
      try {
        const res = await historyAPI.list({ pageNo: 1, pageSize: 50 })
        if (res.success && res.data) {
          this.historyList = (res.data.items || []).map(item => ({
            id: item.id,
            title: item.title,
            date: this.formatTime(new Date(item.updatedAt || item.createdAt)),
            status: item.status
          }))
        }
      } catch (e) {
        console.error('加载历史记录失败:', e)
      }
    },
    async startExplore() {
      this.loading = true
      try {
        let requirementId = this.currentRequirementId
        if (!requirementId) {
          const createData = {
            title: this.requirementText.trim().slice(0, 200) || (this.uploadedFile ? this.uploadedFile.name : '未命名需求'),
            inputMode: this.inputMode === 'document' ? 'file' : 'text',
            templateId: this.selectedTemplateId
          }
          if (this.inputMode === 'text') {
            createData.rawContent = this.requirementText
          } else if (this.uploadedFileId) {
            createData.fileId = this.uploadedFileId
          }
          const createRes = await requirementAPI.create(createData)
          if (createRes.success && createRes.data) {
            requirementId = createRes.data.id
            this.currentRequirementId = requirementId
          }
        }
        const startRes = await exploreAPI.start({
          requirementId,
          templateId: this.selectedTemplateId
        })
        if (startRes.success && startRes.data) {
          this.exploreSessionId = startRes.data.sessionId
          if (startRes.data.firstQuestion) {
            this.exploreMessages.push({
              content: this.extractMessageContent(startRes.data.firstQuestion),
              isUser: false,
              dimensionKey: startRes.data.firstDimensionKey,
              dimensionLabel: startRes.data.firstDimensionLabel,
              quickReplies: [],
              replied: false
            })
            this.scrollToBottomOfExploreMessages()
          }
          if (startRes.data.understandingScore !== undefined) {
            this.understandingScore = startRes.data.understandingScore
          }
          if (startRes.data.exploredDimensions) {
            this.exploredDimensions = startRes.data.exploredDimensions
          }
        }
        this.activeStep = 2
        this.step2State = 'exploring'
        this.exploreInput = ''
        this.userTriggeredGenerate = false
        this.maxCompletedStep = Math.max(this.maxCompletedStep, 1)
        // 刷新历史记录列表并选中当前需求
        await this.loadHistoryList()
        this.activeHistoryId = requirementId
        if (this.exploreMessages.length === 0) {
          this.askNextDimension()
        }
      } catch (e) {
        console.error('启动需求探索失败:', e)
        this.activeStep = 2
        this.step2State = 'exploring'
        this.exploreMessages = []
        this.understandingScore = 0
        this.exploredDimensions = []
        this.currentDimensionIndex = 0
        this.userTriggeredGenerate = false
        this.maxCompletedStep = Math.max(this.maxCompletedStep, 1)
        this.askNextDimension()
      } finally {
        this.loading = false
      }
    },
    askNextDimension() {
      const template = this.selectedTemplate
      if (!template) return
      if (this.currentDimensionIndex >= template.dimensions.length) {
        this.understandingScore = 100
        return
      }
      const dimension = template.dimensions[this.currentDimensionIndex]
      this.aiTyping = true
      setTimeout(() => {
        this.aiTyping = false
        this.exploreMessages.push({
          content: dimension.question,
          isUser: false,
          dimensionKey: dimension.key,
          dimensionLabel: dimension.label,
          quickReplies: [],
          replied: false
        })
        this.scrollToBottomOfExploreMessages()
      }, 800)
    },
    sendExploreQuickReply(reply, msgIndex) {
      if (msgIndex !== undefined) {
        this.exploreMessages[msgIndex].replied = true
      }
      this.exploreInput = reply
      this.sendExploreMessage()
    },
    async sendExploreMessage() {
      if (!this.exploreInput.trim()) return
      const userMsg = this.exploreInput.trim()
      const template = this.selectedTemplate
      const currentDim = this.currentDimensionIndex < template.dimensions.length
        ? template.dimensions[this.currentDimensionIndex]
        : null
      this.exploreMessages.push({
        content: userMsg,
        isUser: true,
        dimensionKey: currentDim ? currentDim.key : null,
        dimensionLabel: currentDim ? currentDim.label : null
      })
      this.exploreInput = ''
      this.scrollToBottomOfExploreMessages()
      // 不再自动递增维度下标，由后端 AI 响应驱动状态变更
      this.aiTyping = true
      try {
        if (this.exploreSessionId && this.currentRequirementId) {
          const res = await exploreAPI.chat({
            sessionId: this.exploreSessionId,
            requirementId: this.currentRequirementId,
            message: userMsg,
            dimensionKey: currentDim ? currentDim.key : null,
            dimensionLabel: currentDim ? currentDim.label : null
          })
          this.aiTyping = false
          if (res.success && res.data) {
            const aiMsg = res.data
            this.exploreMessages.push({
              content: this.extractMessageContent(aiMsg.content),
              isUser: false,
              dimensionKey: aiMsg.dimensionKey || aiMsg.nextDimensionKey,
              dimensionLabel: aiMsg.dimensionLabel || aiMsg.nextDimensionLabel,
              quickReplies: aiMsg.quickReplies || [],
              replied: false
            })
            this.scrollToBottomOfExploreMessages()
            // 根据 AI 响应同步维度和理解度
            if (aiMsg.exploredDimensions) {
              this.exploredDimensions = aiMsg.exploredDimensions
            }
            if (aiMsg.understandingScore !== undefined) {
              this.understandingScore = aiMsg.understandingScore
            }
            if (aiMsg.canGenerate) {
              this.understandingScore = 100
            }
            // 根据 AI 当前提问的维度更新 currentDimensionIndex
            if (aiMsg.dimensionKey && template.dimensions) {
              const idx = template.dimensions.findIndex(d => d.key === aiMsg.dimensionKey)
              if (idx !== -1) {
                this.currentDimensionIndex = idx
              } else if (template.dimensions.length > 0) {
                this.currentDimensionIndex = template.dimensions.length
              }
            }
          }
        } else {
          // 无后端时，模拟推进逻辑
          this.aiTyping = false
          if (this.currentDimensionIndex < template.dimensions.length) {
            const dimension = template.dimensions[this.currentDimensionIndex]
            if (!this.exploredDimensions.includes(dimension.key)) {
              this.exploredDimensions.push(dimension.key)
            }
            this.currentDimensionIndex++
          }
          if (this.currentDimensionIndex < template.dimensions.length) {
            this.askNextDimension()
          } else {
            this.understandingScore = 100
            this.exploreMessages.push({
              content: '感谢您的详细描述！我已经充分理解了您的需求，现在可以为您生成标准化文档了。请点击「生成文档」按钮开始生成。',
              isUser: false,
              quickReplies: [],
              replied: true
            })
            this.scrollToBottomOfExploreMessages()
          }
        }
      } catch (e) {
        this.aiTyping = false
        console.error('发送探索消息失败:', e)
        this.understandingScore = Math.min(this.understandingScore + 5, Math.round((this.exploredDimensions.length / this.totalDimensions) * 100))
        if (this.currentDimensionIndex < template.dimensions.length) {
          this.askNextDimension()
        } else {
          this.understandingScore = 100
          this.exploreMessages.push({
            content: '感谢您的详细描述！我已经充分理解了您的需求，现在可以为您生成标准化文档了。请点击「生成文档」按钮开始生成。',
            isUser: false,
            quickReplies: [],
            replied: true
          })
          this.scrollToBottomOfExploreMessages()
        }
      }
    },
    async generateDocument() {
      this.userTriggeredGenerate = true
      this.step2State = 'generating'
      const exploreData = this.exploreMessages
        .filter(msg => msg.isUser && msg.dimensionKey)
        .map(msg => ({ dimensionKey: msg.dimensionKey, dimensionLabel: msg.dimensionLabel, content: msg.content }))
      try {
        const reqData = {
          requirementId: this.currentRequirementId,
          templateId: this.selectedTemplateId,
          inputMode: this.inputMode === 'document' ? 'file' : 'text',
          exploreData
        }
        if (this.inputMode === 'text') {
          reqData.rawContent = this.requirementText
        } else if (this.uploadedFileId) {
          reqData.fileId = this.uploadedFileId
        }
        const res = await standardizeAPI.process(reqData)
        if (res.success && res.data) {
          this.standardizedContent = res.data.standardizedContent
          this.versionCounter = res.data.versionNumber || 1
          this.docVersions = [{
            id: res.data.versionId || this.versionCounter,
            content: this.standardizedContent,
            timestamp: this.formatTime(new Date(res.data.completedAt || new Date())),
            description: '初始版本'
          }]
          this.activeVersionId = this.docVersions[0].id
          if (this.currentRequirementId) {
            await requirementAPI.update(this.currentRequirementId, { status: 'standardized' })
          }
        }
      } catch (e) {
        console.error('生成标准化文档失败，使用本地生成:', e)
        const template = this.selectedTemplate
        const userInput = this.requirementText || this.uploadedFile?.name || ''
        this.standardizedContent = template.generateContent(userInput, exploreData)
        this.versionCounter = 1
        this.docVersions = [{
          id: this.versionCounter,
          content: this.standardizedContent,
          timestamp: this.formatTime(new Date()),
          description: '初始版本'
        }]
        this.activeVersionId = this.versionCounter
      }
      this.step2State = 'editing'
      this.editMessages = []
      this.maxCompletedStep = Math.max(this.maxCompletedStep, 2)
      this.fetchQualityScore()
    },
    sendEditQuickMessage(text) {
      this.editInput = text
      this.sendEditMessage()
    },
    async sendEditMessage() {
      if (!this.editInput.trim()) return
      const userMsg = this.editInput.trim()
      this.editMessages.push({ content: userMsg, isUser: true })
      this.editInput = ''
      this.aiTyping = true
      try {
        const chatData = {
          requirementId: this.currentRequirementId,
          message: userMsg,
          currentContent: this.standardizedContent,
          templateId: this.selectedTemplateId
        }
        const res = await standardizeAPI.chat(chatData)
        this.aiTyping = false
        if (res.success && res.data) {
          const aiData = res.data
          this.editMessages.push({
            type: aiData.type || 'proposal',
            content: aiData.content,
            confirmed: false,
            rejected: false,
            isUser: false,
            messageId: aiData.messageId,
            editType: this.detectEditType(userMsg),
            proposal: aiData.proposal || null
          })
        }
      } catch (e) {
        this.aiTyping = false
        console.error('发送调整消息失败，使用本地逻辑:', e)
        const aiResponse = this.generateEditResponse(userMsg)
        this.editMessages.push(aiResponse)
      }
    },
    detectEditType(userMsg) {
      if (userMsg.includes('安全')) return 'security'
      if (userMsg.includes('性能') || userMsg.includes('指标')) return 'performance'
      if (userMsg.includes('异常') || userMsg.includes('错误')) return 'exception'
      return 'general'
    },
    generateEditResponse(userMsg) {
      if (userMsg.includes('安全')) {
        return {
          type: 'proposal',
          content: '我建议在非功能需求中增加以下安全性要求：\n\n- 密码加密存储（使用 bcrypt 或 Argon2）\n- 敏感数据传输使用 HTTPS 加密\n- 实施基于角色的访问控制（RBAC）\n- 操作审计日志记录\n- 登录失败锁定策略（5次失败锁定30分钟）\n\n是否采纳此建议？',
          confirmed: false,
          rejected: false,
          isUser: false,
          editType: 'security'
        }
      }
      if (userMsg.includes('性能') || userMsg.includes('指标')) {
        return {
          type: 'proposal',
          content: '我建议补充以下性能指标：\n\n- 页面首屏加载时间 ≤ 2秒\n- API 接口响应时间 ≤ 500ms（P95）\n- 系统支持 1000 并发用户\n- 数据库查询响应时间 ≤ 200ms\n- 文件上传支持单文件 ≤ 50MB\n\n是否采纳此建议？',
          confirmed: false,
          rejected: false,
          isUser: false,
          editType: 'performance'
        }
      }
      if (userMsg.includes('异常') || userMsg.includes('错误')) {
        return {
          type: 'proposal',
          content: '我建议补充以下异常场景处理：\n\n- 网络超时：显示友好提示并支持重试\n- 数据校验失败：明确提示错误字段和原因\n- 并发冲突：乐观锁机制，提示用户刷新\n- 服务不可用：降级处理或维护页面\n- 文件上传失败：支持断点续传\n\n是否采纳此建议？',
          confirmed: false,
          rejected: false,
          isUser: false,
          editType: 'exception'
        }
      }
      return {
        type: 'proposal',
        content: '我理解您的调整需求。让我根据您的描述来优化文档内容，请问您具体希望调整哪个章节或哪方面的内容？\n\n例如：\n- 补充某个功能模块的细节\n- 调整非功能需求的指标\n- 增加约束条件\n- 修改业务流程描述',
        confirmed: false,
        rejected: false,
        isUser: false,
        editType: 'general'
      }
    },
    async confirmEditProposal(index) {
      const msg = this.editMessages[index]
      if (!msg || msg.type !== 'proposal') return
      try {
        if (msg.messageId && this.currentRequirementId) {
          const res = await standardizeAPI.adopt(msg.messageId, { requirementId: this.currentRequirementId })
          if (res.success && res.data) {
            msg.confirmed = true
            this.standardizedContent = res.data.newContent || this.standardizedContent
            this.versionCounter = res.data.newVersionNumber || (this.versionCounter + 1)
            this.docVersions.push({
              id: res.data.newVersionId || this.versionCounter,
              content: this.standardizedContent,
              timestamp: this.formatTime(new Date()),
              description: this.shortDesc(res.data.changeSummary || (msg.editType === 'security' ? '安全性需求' : msg.editType === 'performance' ? '性能指标' : msg.editType === 'exception' ? '异常场景' : '内容调整'))
            })
            this.activeVersionId = this.docVersions[this.docVersions.length - 1].id
            // [已注释] 暂时去除草稿保存
            // this.triggerAutoSave()
            this.fetchQualityScore()
            return
          }
        }
      } catch (e) {
        console.error('采纳AI建议失败，使用本地逻辑:', e)
      }
      msg.confirmed = true
      this.versionCounter++
      const additions = this.getAdditionsByType(msg.editType)
      this.standardizedContent = this.standardizedContent + '\n\n' + additions
      this.docVersions.push({
        id: this.versionCounter,
        content: this.standardizedContent,
        timestamp: this.formatTime(new Date()),
        description: msg.editType === 'security' ? '安全性需求' : msg.editType === 'performance' ? '性能指标' : msg.editType === 'exception' ? '异常场景' : '内容调整'
      })
      this.activeVersionId = this.versionCounter
      // [已注释] 暂时去除草稿保存
      // this.triggerAutoSave()
      this.fetchQualityScore()
    },
    async rejectEditProposal(index) {
      const msg = this.editMessages[index]
      if (!msg || msg.type !== 'proposal') return
      try {
        if (msg.messageId && this.currentRequirementId) {
          await standardizeAPI.reject(msg.messageId, { requirementId: this.currentRequirementId })
        }
      } catch (e) {
        console.error('拒绝AI建议失败:', e)
      }
      msg.rejected = true
    },
    getAdditionsByType(editType) {
      const additions = {
        security: '### 4.2.1 安全性补充\n\n- 密码加密存储（使用 bcrypt 或 Argon2）\n- 敏感数据传输使用 HTTPS 加密\n- 实施基于角色的访问控制（RBAC）\n- 操作审计日志记录\n- 登录失败锁定策略（5次失败锁定30分钟）',
        performance: '### 4.1.1 性能指标补充\n\n- 页面首屏加载时间 ≤ 2秒\n- API 接口响应时间 ≤ 500ms（P95）\n- 系统支持 1000 并发用户\n- 数据库查询响应时间 ≤ 200ms\n- 文件上传支持单文件 ≤ 50MB',
        exception: '### 6.3 补充异常场景\n\n- 网络超时：显示友好提示并支持重试\n- 数据校验失败：明确提示错误字段和原因\n- 并发冲突：乐观锁机制，提示用户刷新\n- 服务不可用：降级处理或维护页面\n- 文件上传失败：支持断点续传',
        general: '### 补充说明\n\n（根据用户反馈补充的内容）'
      }
      return additions[editType] || additions.general
    },
    async uploadToKnowledgeBase() {
      if (!this.standardizedContent || this.uploadingToKB) return
      this.uploadingToKB = true
      try {
        const template = this.selectedTemplate
        await standardizeAPI.uploadToKnowledgeBase({
          requirementId: this.currentRequirementId,
          title: template.name + ' - ' + new Date().toLocaleDateString(),
          content: this.standardizedContent,
          templateId: this.selectedTemplateId
        })
        this.$message?.success?.('文档已成功上传至知识库') || alert('文档已成功上传至知识库')
      } catch (e) {
        console.error('上传知识库失败:', e)
        this.$message?.error?.('上传知识库失败，请稍后重试') || alert('上传知识库失败，请稍后重试')
      } finally {
        this.uploadingToKB = false
      }
    },
    async handleExport(format) {
      this.showExportMenu = false
      const template = this.selectedTemplate
      const filename = template.name

      if (format === 'docx') {
        exportDocx(this.standardizedContent, filename + '.docx')
        return
      }

      if (format === 'markdown') {
        if (this.currentRequirementId) {
          try {
            const res = await requirementAPI.exportDocument(this.currentRequirementId, { format })
            const content = typeof res === 'string' ? res : this.standardizedContent
            exportMarkdown(content, filename + '.md')
            return
          } catch (e) {
            console.error('导出文档失败，使用本地导出:', e)
          }
        }
        exportMarkdown(this.standardizedContent, filename + '.md')
      }
    },
    normalizeSplitData(res) {
      let items = null
      if (res.data) {
        if (Array.isArray(res.data)) {
          items = res.data
        } else if (res.data.items) {
          items = res.data.items
        } else if (res.data.list) {
          items = res.data.list
        } else if (res.data.records) {
          items = res.data.records
        } else if (res.data.splits) {
          items = res.data.splits
        } else if (res.data.requirements) {
          items = res.data.requirements
        }
      }
      if (!items) {
        if (res.items) items = res.items
        else if (res.list) items = res.list
        else if (res.records) items = res.records
        else if (res.splits) items = res.splits
      }
      if (!Array.isArray(items)) return null
      return items.map((item, index) => {
        if (typeof item === 'string') {
          return { id: `split-${index}`, content: item, selected: true }
        }
        if (typeof item === 'object' && item !== null) {
          return {
            id: item.id || `split-${index}`,
            content: item.content || item.title || item.name || item.text || '',
            selected: true
          }
        }
        return { id: `split-${index}`, content: String(item), selected: true }
      })
    },
    async handleSplitRequirements() {
      if (!this.standardizedContent || this.splitting) return
      this.splitting = true
      try {
        if (this.currentRequirementId) {
          const res = await requirementAPI.split(this.currentRequirementId, {
            standardizedContent: this.standardizedContent,
            templateId: this.selectedTemplateId
          })
          if (res.success) {
            const normalized = this.normalizeSplitData(res)
            if (normalized && normalized.length > 0) {
              this.splitRequirements = normalized
              this.activeStep = 3
              this.maxCompletedStep = Math.max(this.maxCompletedStep, 3)
              // [已注释] 暂时去除草稿保存
              // this.triggerAutoSave()
              this.splitting = false
              return
            }
          }
        }
      } catch (e) {
        console.error('AI需求拆分失败，使用本地拆分:', e)
      }
      const lines = this.standardizedContent.split('\n')
      const requirements = []
      let currentReq = null
      lines.forEach(line => {
        const match = line.match(/^###?\s+(\d+[\.\d]*)\s+(.+)/)
        if (match) {
          if (currentReq) requirements.push(currentReq)
          currentReq = { content: match[2].trim(), selected: true }
        } else if (currentReq && line.trim()) {
          currentReq.content += ' ' + line.trim()
        }
      })
      if (currentReq) requirements.push(currentReq)
      if (requirements.length === 0) {
        const sections = this.standardizedContent.split(/(?=^## )/m)
        sections.forEach(section => {
          const titleMatch = section.match(/^##\s+(.+)/)
          if (titleMatch) {
            requirements.push({ content: titleMatch[1].trim(), selected: true })
          }
        })
      }
      this.splitRequirements = requirements.length > 0 ? requirements : [{ content: '需求1', selected: true }]
      this.activeStep = 3
      this.maxCompletedStep = Math.max(this.maxCompletedStep, 3)
      // [已注释] 暂时去除草稿保存
      // this.triggerAutoSave()
      this.splitting = false
    },
    async addRequirement() {
      const newItem = { content: '', selected: true }
      if (this.currentRequirementId) {
        try {
          const res = await requirementAPI.addSplit(this.currentRequirementId, { content: '' })
          if (res.success && res.data) {
            newItem.id = res.data.id
          }
        } catch (e) {
          console.error('添加拆分项失败:', e)
        }
      }
      this.splitRequirements.unshift(newItem)
    },
    async removeRequirement(index) {
      const item = this.splitRequirements[index]
      if (item.id && this.currentRequirementId) {
        try {
          await requirementAPI.deleteSplit(this.currentRequirementId, item.id)
        } catch (e) {
          console.error('删除拆分项失败:', e)
        }
      }
      this.splitRequirements.splice(index, 1)
    },
    async confirmAndGoToTestDesign() {
      const validRequirements = this.splitRequirements.filter(r => r.content.trim())
      if (validRequirements.length === 0) {
        alert('请至少填写一条需求')
        return
      }
      try {
        const title = this.requirementText.trim().slice(0, 30) || (this.uploadedFile ? this.uploadedFile.name : '') || validRequirements[0].content.trim().slice(0, 30)
        const displayTitle = title + (title.length >= 30 ? '...' : '')
        let requirementId = this.currentRequirementId
        if (!requirementId) {
          const createRes = await requirementAPI.create({
            title: displayTitle,
            inputMode: this.inputMode === 'document' ? 'file' : 'text',
            rawContent: this.inputMode === 'text' ? this.requirementText : undefined,
            fileId: this.inputMode === 'document' ? this.uploadedFileId : undefined,
            templateId: this.selectedTemplateId
          })
          if (createRes.success && createRes.data) {
            requirementId = createRes.data.id
          }
        }
        const res = await requirementAPI.confirmAndEnterTestDesign(requirementId, {
          title: displayTitle,
          splitRequirements: validRequirements,
          standardizedContent: this.standardizedContent,
          templateId: this.selectedTemplateId
        })
        if (res.success) {
          this.draftStatus = 'idle'
          this.$router.push({ path: '/test-design', query: { requirementId: res.data.id || requirementId } })
        }
      } catch (e) {
        console.error('保存需求失败:', e)
        alert('保存需求失败，请稍后重试')
      }
    },
    newRequirement() {
      this.activeStep = 1
      this.inputMode = 'text'
      this.requirementText = ''
      this.uploadedFile = null
      this.uploadedFileId = null
      this.selectedTemplateId = 'user-story'
      this.aiRecommended = false
      this.maxCompletedStep = 0
      this.clearDownstreamSteps()
      this.activeHistoryId = null
      // [已注释] 暂时去除草稿清理
      // clearDraft()
      this.draftStatus = 'idle'
    },
    confirmDeleteHistory(item) {
      this.deleteTargetId = item.id
      this.deleteTargetTitle = item.title
      this.showDeleteConfirm = true
    },
    async deleteHistory() {
      if (!this.deleteTargetId) return
      this.deletingHistory = true
      try {
        const res = await requirementAPI.delete(this.deleteTargetId)
        if (res.success || res.code === 200) {
          if (this.deleteTargetId === this.activeHistoryId) {
            this.newRequirement()
          }
          await this.loadHistoryList()
          this.showDeleteConfirm = false
        }
      } catch (e) {
        console.error('删除历史记录失败:', e)
      } finally {
        this.deletingHistory = false
        this.deleteTargetId = null
        this.deleteTargetTitle = ''
      }
    },
    async loadHistory(item) {
      this.activeHistoryId = item.id
      this.isLoadingHistory = true
      try {
        const res = await historyAPI.detail(item.id)
        if (res.success && res.data) {
          const data = res.data
          this.currentRequirementId = data.id
          this.requirementText = data.rawContent || ''
          this.selectedTemplateId = data.templateId || 'user-story'
          this.inputMode = data.inputMode === 'file' ? 'document' : 'text'
          const fi = data.fileInfo
          this.uploadedFileId = fi ? (fi.fileId || data.id) : null
          this.uploadedFile = fi ? { name: fi.fileName || data.title || '已上传文件', size: fi.fileSize || 0 } : null
          this.standardizedContent = data.standardizedContent || ''
          this.splitRequirements = (data.splitRequirements || []).map(r => ({
            id: r.id,
            content: r.content,
            selected: true
          }))
          this.exploreMessages = []
          this.editMessages = []
          this.exploredDimensions = []
          this.understandingScore = 0
          this.currentDimensionIndex = 0
          this.step2State = 'exploring'
          this.docVersions = []
          this.activeVersionId = null
          this.versionCounter = 0
          this.userTriggeredGenerate = false

          if (data.status === 'split') {
            this.maxCompletedStep = 3
            this.step2State = 'editing'
          } else if (data.status === 'standardized' && this.standardizedContent) {
            this.maxCompletedStep = 2
            this.step2State = 'editing'
          } else if (data.status === 'exploring') {
            this.maxCompletedStep = 1
            this.step2State = 'exploring'
          } else {
            this.maxCompletedStep = 0
          }

          this.activeStep = 1

          if (data.exploreData && data.exploreData.length > 0) {
            this.exploredDimensions = data.exploreData.map(d => d.dimensionKey)
            this.understandingScore = Math.round((this.exploredDimensions.length / this.totalDimensions) * 100)
          }

          if (this.maxCompletedStep >= 1 && this.currentRequirementId) {
            this.loadExploreHistory(this.currentRequirementId)
          }
          if (this.maxCompletedStep >= 2 && this.currentRequirementId) {
            this.loadEditHistory(this.currentRequirementId)
          }

          // [已注释] 暂时去除草稿保存
          // this.triggerAutoSave()
        }
      } catch (e) {
        console.error('加载历史记录详情失败:', e)
      } finally {
        this.isLoadingHistory = false
      }
    },
    async loadExploreHistory(requirementId) {
      try {
        const res = await exploreAPI.history(requirementId)
        if (res.success && res.data) {
          const messages = Array.isArray(res.data) ? res.data : (res.data.messages || res.data.items || [])
          if (messages.length > 0) {
            this.exploreMessages = messages.map(msg => {
              if (typeof msg === 'string') {
                return { content: msg, isUser: false, quickReplies: [], replied: true }
              }
              return {
                content: msg.content || msg.text || msg.message || '',
                isUser: !!msg.isUser || msg.role === 'user',
                dimensionKey: msg.dimensionKey || null,
                dimensionLabel: msg.dimensionLabel || null,
                quickReplies: msg.quickReplies || [],
                replied: msg.replied !== undefined ? msg.replied : true
              }
            })
          }
        }
      } catch (e) {
        console.error('加载探索历史失败:', e)
      }
    },
    async loadEditHistory(requirementId) {
      try {
        const res = await standardizeAPI.getChatHistory(requirementId)
        if (res.success && res.data) {
          const messages = Array.isArray(res.data) ? res.data : (res.data.messages || res.data.items || [])
          if (messages.length > 0) {
            this.editMessages = messages.map(msg => {
              if (typeof msg === 'string') {
                return { content: msg, isUser: true, type: 'text', confirmed: false, rejected: false }
              }
              return {
                content: msg.content || msg.text || msg.message || '',
                isUser: !!msg.isUser || msg.role === 'user',
                type: msg.type || 'text',
                confirmed: msg.confirmed || false,
                rejected: msg.rejected || false,
                messageId: msg.messageId || msg.id || null,
                editType: msg.editType || 'general',
                proposal: msg.proposal || null
              }
            })
          }
        }
      } catch (e) {
        console.error('加载编辑历史失败:', e)
      }
    },
    async switchVersion(versionId) {
      const version = this.docVersions.find(v => v.id === versionId)
      if (version) {
        this.standardizedContent = version.content
        this.activeVersionId = versionId
        this.fetchQualityScore()
      }
    },
    async restoreVersion(versionId) {
      const version = this.docVersions.find(v => v.id === versionId)
      if (!version) return
      try {
        if (this.currentRequirementId) {
          const res = await standardizeAPI.restoreVersion(this.currentRequirementId, versionId)
          if (res.success && res.data) {
            this.versionCounter = res.data.newVersionNumber || (this.versionCounter + 1)
            this.docVersions.push({
              id: res.data.newVersionId || this.versionCounter,
              content: res.data.content || version.content,
              timestamp: this.formatTime(new Date()),
              description: this.shortDesc(res.data.description || ('恢复v' + versionId))
            })
            this.standardizedContent = res.data.content || version.content
            this.activeVersionId = this.docVersions[this.docVersions.length - 1].id
            // [已注释] 暂时去除草稿保存
            // this.triggerAutoSave()
            this.fetchQualityScore()
            return
          }
        }
      } catch (e) {
        console.error('恢复版本失败，使用本地逻辑:', e)
      }
      this.versionCounter++
      this.docVersions.push({
        id: this.versionCounter,
        content: version.content,
        timestamp: this.formatTime(new Date()),
        description: '恢复v' + versionId
      })
      this.standardizedContent = version.content
      this.activeVersionId = this.versionCounter
      // [已注释] 暂时去除草稿保存
      // this.triggerAutoSave()
      this.fetchQualityScore()
    },
    resizeAllSplitTextareas() {
      const refs = this.$refs.splitTextareas
      if (!refs) return
      const list = Array.isArray(refs) ? refs : [refs]
      list.forEach(el => {
        if (el) {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }
      })
    },
    autoResizeTextarea(event) {
      const el = event.target
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    },
    formatTime(date) {
      const pad = n => String(n).padStart(2, '0')
      return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
    }
  }
}
</script>