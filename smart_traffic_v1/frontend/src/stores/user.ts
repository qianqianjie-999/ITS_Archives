import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token') || sessionStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isEditor = computed(() => user.value?.role === 'editor' || user.value?.role === 'admin')

  async function login(username: string, password: string, rememberMe: boolean = false) {
    const response = await authApi.login(username, password) as any
    if (response.status === 'success' && response.token && response.user) {
      token.value = response.token
      user.value = response.user
      if (rememberMe) {
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
      } else {
        sessionStorage.setItem('token', response.token)
        sessionStorage.setItem('user', JSON.stringify(response.user))
      }
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
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return false
    try {
      const response = await authApi.getCurrentUser() as any
      if (response.status === 'success' && response.user) {
        user.value = response.user
        return true
      }
      return false
    } catch {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
      return false
    }
  }

  function initFromStorage() {
    const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user')
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