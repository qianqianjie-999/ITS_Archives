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
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/views/ProjectList.vue')
      },
      {
        path: 'parking-enforcements',
        name: 'ParkingEnforcementList',
        component: () => import('@/views/ParkingEnforcementList.vue')
      },
      {
        path: 'parking-enforcements/:id',
        name: 'ParkingEnforcementDetail',
        component: () => import('@/views/ParkingEnforcementDetail.vue')
      },
      {
        path: 'checkpoints',
        name: 'CheckpointList',
        component: () => import('@/views/CheckpointList.vue')
      },
      {
        path: 'checkpoints/:id',
        name: 'CheckpointDetail',
        component: () => import('@/views/CheckpointDetail.vue')
      },
      {
        path: 'backend-devices',
        name: 'BackendDeviceList',
        component: () => import('@/views/BackendDeviceList.vue')
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/Statistics.vue')
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
  } else {
    next()
  }
})

export default router