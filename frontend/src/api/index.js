import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

function handleAuthExpired() {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user')
  window.__authRedirect = true
  window.location.href = '/login?expired=1'
}

api.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code && res.code !== 200 && res.code !== 0) {
      const error = new Error(res.message || '请求失败')
      error.code = res.code
      error.response = res
      if (res.code === 401) {
        handleAuthExpired()
      }
      return Promise.reject(error)
    }
    return { ...res, success: true }
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          handleAuthExpired()
          break
        case 403:
          error.message = '没有权限访问该资源'
          break
        case 404:
          error.message = '请求的资源不存在'
          break
        case 429:
          error.message = '请求过于频繁，请稍后再试'
          break
        case 500:
          error.message = '服务器内部错误'
          break
        case 502:
          error.message = '网关错误'
          break
        case 503:
          error.message = '服务不可用'
          break
        default:
          error.message = data?.message || `请求失败(${status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      error.message = '请求超时，请稍后重试'
    } else if (!window.navigator.onLine) {
      error.message = '网络连接已断开，请检查网络'
    } else {
      error.message = '网络异常，请稍后重试'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: (data) => api.post('/auth/logout', data),
  getUser: () => api.get('/auth/user'),
  refreshToken: (data) => api.post('/auth/refresh', data)
}

export const uploadAPI = {
  uploadFile: (data) => api.post('/v1/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  })
}

export const requirementAPI = {
  create: (data) => api.post('/v1/requirements', data),
  list: (params) => api.get('/v1/requirements', { params }),
  detail: (id) => api.get(`/v1/requirements/${id}`),
  update: (id, data) => api.put(`/v1/requirements/${id}`, data),
  delete: (id) => api.delete(`/v1/requirements/${id}`),
  split: (id, data) => api.post(`/v1/requirements/${id}/split`, data),
  getSplits: (id) => api.get(`/v1/requirements/${id}/splits`),
  updateSplit: (requirementId, splitId, data) => api.put(`/v1/requirements/${requirementId}/splits/${splitId}`, data),
  deleteSplit: (requirementId, splitId) => api.delete(`/v1/requirements/${requirementId}/splits/${splitId}`),
  addSplit: (requirementId, data) => api.post(`/v1/requirements/${requirementId}/splits`, data),
  confirmAndEnterTestDesign: (id, data) => api.post(`/v1/requirements/${id}/confirm-and-test`, data),
  exportDocument: (id, params) => api.get(`/v1/requirements/${id}/export`, { params, responseType: params.format === 'docx' ? 'blob' : 'text' })
}

export const historyAPI = {
  list: (params) => api.get('/v1/history', { params }),
  detail: (id) => api.get(`/v1/history/${id}`)
}

export const templateAPI = {
  list: () => api.get('/v1/templates'),
  detail: (id) => api.get(`/v1/templates/${id}`),
  recommend: (data) => api.post('/v1/templates/recommend', data)
}

export const exploreAPI = {
  start: (data) => api.post('/v1/explore/start', data),
  chat: (data) => api.post('/v1/explore/chat', data),
  history: (requirementId, params) => api.get(`/v1/explore/chat/${requirementId}`, { params }),
  status: (params) => api.get('/v1/explore/status', { params })
}

export const standardizeAPI = {
  process: (data) => api.post('/v1/standardize', data),
  getResult: (requirementId) => api.get(`/v1/standardize/${requirementId}`),
  chat: (data) => api.post('/v1/standardize/chat', data),
  getChatHistory: (requirementId) => api.get(`/v1/standardize/chat/${requirementId}`),
  adopt: (messageId, data) => api.post(`/v1/standardize/chat/${messageId}/confirm`, data),
  reject: (messageId, data) => api.post(`/v1/standardize/chat/${messageId}/reject`, data),
  getVersions: (requirementId) => api.get(`/v1/standardize/versions/${requirementId}`),
  getVersionDetail: (requirementId, versionId) => api.get(`/v1/standardize/versions/${requirementId}/${versionId}`),
  restoreVersion: (requirementId, versionId) => api.post(`/v1/standardize/versions/${requirementId}/${versionId}/restore`),
  getVersionDiff: (requirementId, params) => api.get(`/v1/standardize/versions/${requirementId}/diff`, { params }),
  qualityScore: (data) => api.post('/v1/standardize/quality', data),
  uploadToKnowledgeBase: (data) => api.post('/v1/knowledge-base/upload-doc', data)
}

export const knowledgeAPI = {
  upload: (data) => api.post('/v1/knowledge/documents/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  }),
  list: (params) => api.get('/v1/knowledge/documents', { params }),
  detail: (id) => api.get(`/v1/knowledge/documents/${id}`),
  delete: (id, data) => api.delete(`/v1/knowledge/documents/${id}`, { data }),
  retry: (id, data) => api.post(`/v1/knowledge/documents/${id}/retry`, data),
  getChunks: (id, params) => api.get(`/v1/knowledge/documents/${id}/chunks`, { params }),
  getContent: (id) => api.get(`/v1/knowledge/documents/${id}/content`),
  getStorageInfo: () => api.get('/v1/knowledge/storage'),
  getProcessingStatus: (id) => api.get(`/v1/knowledge/documents/${id}/status`),
  batchGetStatus: (data) => api.post('/v1/knowledge/documents/status/batch', data),
  getRecallSettings: () => api.get('/v1/knowledge/recall/settings'),
  updateRecallSettings: (data) => api.put('/v1/knowledge/recall/settings', data),
  reprocess: (data) => api.post('/v1/knowledge/documents/reprocess', data),
  testRecall: (data) => api.post('/v1/knowledge/recall/test', data),
  getRecallHistory: (params) => api.get('/v1/knowledge/recall/test/history', { params }),
  getStats: () => api.get('/v1/knowledge/statistics/documents'),
  getStatusStats: () => api.get('/v1/knowledge/statistics/processing')
}

export const testDesignAPI = {
  getRequirementList: (params) => api.get('/v1/test-design/requirements', { params }),
  importRequirement: (data) => api.post('/v1/test-design/requirements', data),
  getMindMapData: (requirementId) => api.get(`/v1/test-design/requirements/${requirementId}/mindmap`),
  addTestPoint: (requirementId, data) => api.post(`/v1/test-design/requirements/${requirementId}/test-points`, data),
  editTestPoint: (testPointId, data) => api.put(`/v1/test-design/test-points/${testPointId}`, data),
  deleteTestPoint: (testPointId) => api.delete(`/v1/test-design/test-points/${testPointId}`),
  batchDeleteTestPoints: (data) => api.post('/v1/test-design/test-points/batch-delete', data),
  markTestPoint: (testPointId, data) => api.put(`/v1/test-design/test-points/${testPointId}/mark`, data),
  addTestCase: (testPointId, data) => api.post(`/v1/test-design/test-points/${testPointId}/test-cases`, data),
  editTestCase: (testCaseId, data) => api.put(`/v1/test-design/test-cases/${testCaseId}`, data),
  deleteTestCase: (testCaseId) => api.delete(`/v1/test-design/test-cases/${testCaseId}`),
  batchDeleteTestCases: (data) => api.post('/v1/test-design/test-cases/batch-delete', data),
  markTestCase: (testCaseId, data) => api.put(`/v1/test-design/test-cases/${testCaseId}/mark`, data),
  createAiSession: (data) => api.post('/v1/test-design/ai-adjust/sessions', data),
  sendAiMessage: (sessionId, data) => api.post(`/v1/test-design/ai-adjust/sessions/${sessionId}/messages`, data),
  getAiHistory: (sessionId) => api.get(`/v1/test-design/ai-adjust/sessions/${sessionId}/messages`),
  adoptAiProposal: (sessionId, messageId, data) => api.post(`/v1/test-design/ai-adjust/sessions/${sessionId}/messages/${messageId}/adopt`, data),
  rejectAiProposal: (sessionId, messageId, data) => api.post(`/v1/test-design/ai-adjust/sessions/${sessionId}/messages/${messageId}/reject`, data),
  applyAiAdjustment: (sessionId, data) => api.post(`/v1/test-design/ai-adjust/sessions/${sessionId}/apply`, data),
  generate: (requirementId, data) => api.post(`/v1/test-design/requirements/${requirementId}/generate`, data),
  getTaskStatus: (taskId) => api.get(`/v1/test-design/tasks/${taskId}`),
  cancelTask: (taskId) => api.post(`/v1/test-design/tasks/${taskId}/cancel`),
  getRequirementTask: (requirementId) => api.get(`/v1/test-design/requirements/${requirementId}/task`),
  exportExcel: (requirementId) => api.get(`/v1/test-design/requirements/${requirementId}/export`, { responseType: 'blob' })
}

export default api
