import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginResponse, ApiResponse } from '@/types'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isEditor = computed(() => user.value?.role === 'editor' || user.value?.role === 'admin')

  async function login(username: string, password: string) {
    const response = await authApi.login(username, password) as unknown as LoginResponse
    if (response.status === 'success' && response.token && response.user) {
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return true
    }
    return false
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return false
    try {
      const response = await authApi.getCurrentUser() as unknown as ApiResponse<{ user: User }>
      if (response.status === 'success' && response.data?.user) {
        user.value = response.data.user
        return true
      }
      return false
    } catch {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      return false
    }
  }

  function initFromStorage() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    isEditor,
    login,
    logout,
    fetchCurrentUser,
    initFromStorage
  }
})