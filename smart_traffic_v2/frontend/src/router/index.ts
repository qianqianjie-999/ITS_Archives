import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/intersections',
    name: 'IntersectionList',
    component: () => import('@/views/IntersectionList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/intersections/:id',
    name: 'IntersectionDetail',
    component: () => import('@/views/IntersectionDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/points',
    name: 'PointList',
    component: () => import('@/views/PointList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: () => import('@/views/ProjectList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/logs',
    name: 'LogList',
    component: () => import('@/views/LogList.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (!userStore.token && localStorage.getItem('token')) {
    userStore.initFromStorage()
    await userStore.fetchCurrentUser()
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router