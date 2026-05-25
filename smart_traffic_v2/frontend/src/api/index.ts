import axios from 'axios'
import type { User, ApiResponse } from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post<ApiResponse<{ token: string; user: User }>>('/auth/login', { username, password }),

  logout: () => apiClient.post('/auth/logout'),

  getCurrentUser: () => apiClient.get<ApiResponse<{ user: User }>>('/auth/current_user')
}

export default apiClient