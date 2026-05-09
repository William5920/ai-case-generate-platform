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

export const standardizeAPI = {
  process: (data) => api.post('/standardize', data)
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

export default api
