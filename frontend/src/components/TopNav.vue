<template>
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
              :class="{ 'bg-blue-50 text-blue-600': $route.path === '/standardization' }"
            >
              需求标准化
            </router-link>
            <router-link
              to="/test-design"
              class="px-4 py-2 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50 text-blue-600': $route.path === '/test-design' }"
            >
              测试设计
            </router-link>
            <router-link
              to="/knowledge-base"
              class="px-4 py-2 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50 text-blue-600': $route.path === '/knowledge-base' }"
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
</template>

<script>
export default {
  name: 'TopNav',

  methods: {
    handleLogout() {
      this.$store.commit('logout')
      this.$router.push('/login')
    }
  }
}
</script>
