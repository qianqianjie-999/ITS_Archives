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
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue')
      },
      {
        path: 'intersections',
        name: 'IntersectionList',
        component: () => import('@/views/IntersectionList.vue')
      },
      {
        path: 'intersections/create',
        name: 'IntersectionCreate',
        component: () => import('@/views/IntersectionDetail.vue')
      },
      {
        path: 'intersections/:id',
        name: 'IntersectionDetail',
        component: () => import('@/views/IntersectionDetail.vue')
      },
      {
        path: 'points',
        name: 'PointList',
        component: () => import('@/views/PointList.vue')
      },
      {
        path: 'points/create',
        name: 'PointCreate',
        component: () => import('@/views/PointDetail.vue')
      },
      {
        path: 'points/:id',
        name: 'PointDetail',
        component: () => import('@/views/PointDetail.vue')
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/views/ProjectList.vue')
      },
      {
        path: 'logs',
        name: 'LogList',
        component: () => import('@/views/LogList.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
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