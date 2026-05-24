<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900"></div>
    
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-1/2 -right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-1/2 -left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-3xl"></div>
    </div>
    
    <div class="absolute inset-0" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0); background-size: 40px 40px;"></div>
    
    <div class="relative z-10 bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-8 w-full max-w-md mx-4 border border-white/20">
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto mb-4 relative">
          <div class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-2xl opacity-80 blur-lg"></div>
          <div class="relative w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
            </svg>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2 tracking-tight">智能测试用例平台</h1>
        <p class="text-white/70">创建新账户</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">用户名</label>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-white/50 group-focus-within:text-cyan-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              class="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all outline-none text-white placeholder-white/40"
              :class="{ 'border-red-400': errors.username }"
              required
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none"></div>
          </div>
          <p v-if="errors.username" class="mt-1 text-sm text-red-400">{{ errors.username }}</p>
        </div>
        

        
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">密码</label>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-white/50 group-focus-within:text-cyan-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码（至少6位）"
              class="w-full pl-12 pr-12 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all outline-none text-white placeholder-white/40"
              :class="{ 'border-red-400': errors.password }"
              required
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-0 pr-4 flex items-center"
            >
              <svg v-if="!showPassword" class="h-5 w-5 text-white/50 hover:text-white/80 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              <svg v-else class="h-5 w-5 text-white/50 hover:text-white/80 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
              </svg>
            </button>
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none"></div>
          </div>
          <p v-if="errors.password" class="mt-1 text-sm text-red-400">{{ errors.password }}</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">确认密码</label>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-white/50 group-focus-within:text-cyan-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
              </svg>
            </div>
            <input
              v-model="confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请再次输入密码"
              class="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all outline-none text-white placeholder-white/40"
              :class="{ 'border-red-400': errors.confirmPassword }"
              required
            />
            <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none"></div>
          </div>
          <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-400">{{ errors.confirmPassword }}</p>
        </div>
        

        
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl hover:from-cyan-600 hover:to-blue-700 focus:ring-4 focus:ring-cyan-400/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl relative overflow-hidden group"
        >
          <span class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 group-hover:opacity-100 transition-opacity"></span>
          <span class="relative flex items-center justify-center">
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '注册中...' : '注 册' }}
          </span>
        </button>
      </form>
      
      <div class="mt-6 text-center">
        <p class="text-white/70">
          已有账号？
          <router-link to="/login" class="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">立即登录</router-link>
        </p>
      </div>
      
      <div v-if="error" class="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
        <p class="text-red-400 text-sm flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          {{ error }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../api'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      showPassword: false,
      loading: false,
      error: '',
      errors: {
        username: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    validateForm() {
      let isValid = true
      this.errors = { username: '', password: '', confirmPassword: '' }
      
      if (!this.username.trim()) {
        this.errors.username = '请输入用户名'
        isValid = false
      } else if (this.username.trim().length < 3) {
        this.errors.username = '用户名长度不能少于3位'
        isValid = false
      } else if (this.username.trim().length > 20) {
        this.errors.username = '用户名长度不能超过20位'
        isValid = false
      } else if (!/^[a-zA-Z0-9_]+$/.test(this.username.trim())) {
        this.errors.username = '用户名只能包含字母、数字和下划线'
        isValid = false
      }
      
      if (!this.password) {
        this.errors.password = '请输入密码'
        isValid = false
      } else if (this.password.length < 6) {
        this.errors.password = '密码长度至少6位'
        isValid = false
      }
      
      if (!this.confirmPassword) {
        this.errors.confirmPassword = '请确认密码'
        isValid = false
      } else if (this.password !== this.confirmPassword) {
        this.errors.confirmPassword = '两次输入的密码不一致'
        isValid = false
      }
      
      return isValid
    },
    async handleRegister() {
      this.error = ''
      
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      
      try {
        const response = await authAPI.register({
          username: this.username.trim(),
          password: this.password
        })
        
        const { token, refreshToken, user } = response.data
        
        if (token) {
          await this.$store.dispatch('login', {
            user,
            token,
            refreshToken
          })
          this.$router.push('/standardization')
        }
      } catch (err) {
        this.error = err.message || '注册失败，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
