import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  timeout: 30000
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

api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data)
}

export const requirementAPI = {
  create: (data) => api.post('/requirements', data),
  list: () => api.get('/requirements'),
  update: (id, data) => api.put(`/requirements/${id}`, data),
  delete: (id) => api.delete(`/requirements/${id}`)
}

export const templateAPI = {
  list: () => api.get('/v1/templates'),
  detail: (id) => api.get(`/v1/templates/${id}`),
  recommend: (data) => api.post('/v1/templates/recommend', data)
}

export const exploreAPI = {
  start: (data) => api.post('/v1/explore/start', data),
  chat: (data) => api.post('/v1/explore/chat', data),
  status: (id) => api.get(`/v1/explore/status`, { params: { id } })
}

export const standardizeAPI = {
  process: (data) => api.post('/standardize', data),
  chat: (data) => api.post('/v1/standardize/chat', data),
  adopt: (data) => api.post('/v1/standardize/adopt', data),
  reject: (data) => api.post('/v1/standardize/reject', data),
  uploadToKnowledgeBase: (data) => api.post('/v1/knowledge-base/upload-doc', data)
}

export const testPointAPI = {
  generate: (data) => api.post('/test-points/generate', data),
  batchDelete: (data) => api.post('/test-points/batch-delete', data)
}

export const testCaseAPI = {
  generate: (data) => api.post('/test-cases/generate', data),
  batchDelete: (data) => api.post('/test-cases/batch-delete', data),
  export: () => api.get('/test-cases/export', { responseType: 'blob' })
}

export const taskAPI = {
  list: () => api.get('/tasks'),
  cancel: (id) => api.delete(`/tasks/${id}`)
}

export const historyAPI = {
  list: () => api.get('/history'),
  detail: (id) => api.get(`/history/${id}`)
}

export const knowledgeAPI = {
  upload: (data) => api.post('/knowledge/docs', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  list: () => api.get('/knowledge/docs'),
  delete: (id) => api.delete(`/knowledge/docs/${id}`),
  get: (id) => api.get(`/knowledge/docs/${id}`)
}

export const testDesignAPI = {
  getRequirementList: (params) => api.get('/test-design/requirements', { params }),
  getMindMapData: (requirementId) => api.get(`/test-design/requirements/${requirementId}/mindmap`),
  addTestPoint: (requirementId, data) => api.post(`/test-design/requirements/${requirementId}/test-points`, data),
  editTestPoint: (testPointId, data) => api.put(`/test-design/test-points/${testPointId}`, data),
  deleteTestPoint: (testPointId) => api.delete(`/test-design/test-points/${testPointId}`),
  batchDeleteTestPoints: (data) => api.post('/test-design/test-points/batch-delete', data),
  markTestPoint: (testPointId, data) => api.put(`/test-design/test-points/${testPointId}/mark`, data),
  addTestCase: (testPointId, data) => api.post(`/test-design/test-points/${testPointId}/test-cases`, data),
  editTestCase: (testCaseId, data) => api.put(`/test-design/test-cases/${testCaseId}`, data),
  deleteTestCase: (testCaseId) => api.delete(`/test-design/test-cases/${testCaseId}`),
  batchDeleteTestCases: (data) => api.post('/test-design/test-cases/batch-delete', data),
  markTestCase: (testCaseId, data) => api.put(`/test-design/test-cases/${testCaseId}/mark`, data),
  createAiSession: (data) => api.post('/test-design/ai-adjust/sessions', data),
  sendAiMessage: (sessionId, data) => api.post(`/test-design/ai-adjust/sessions/${sessionId}/messages`, data),
  getAiHistory: (sessionId) => api.get(`/test-design/ai-adjust/sessions/${sessionId}/messages`),
  generate: (requirementId, data) => api.post(`/test-design/requirements/${requirementId}/generate`, data),
  getTaskStatus: (taskId) => api.get(`/test-design/tasks/${taskId}`),
  cancelTask: (taskId) => api.post(`/test-design/tasks/${taskId}/cancel`),
  exportExcel: (requirementId) => api.get(`/test-design/requirements/${requirementId}/export`, { responseType: 'blob' })
}

export default api
