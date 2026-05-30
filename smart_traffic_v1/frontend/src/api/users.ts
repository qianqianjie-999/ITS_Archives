import apiClient from './index'

export interface User {
  id: number
  username: string
  display_name: string
  role: 'admin' | 'editor' | 'viewer'
  is_active: boolean
  last_login?: string
  created_at?: string
}

export interface UserCreate {
  username: string
  password: string
  display_name?: string
  role?: 'admin' | 'editor' | 'viewer'
}

export interface UserUpdate {
  display_name?: string
  role?: 'admin' | 'editor' | 'viewer'
  is_active?: boolean
  password?: string
}

export const userApi = {
  list(): Promise<User[]> {
    return apiClient.get('/users/')
  },

  get(id: number): Promise<User> {
    return apiClient.get(`/users/${id}`)
  },

  create(data: UserCreate): Promise<User> {
    return apiClient.post('/users/', data)
  },

  update(id: number, data: UserUpdate): Promise<User> {
    return apiClient.put(`/users/${id}`, data)
  },

  delete(id: number): Promise<void> {
    return apiClient.delete(`/users/${id}`)
  }
}