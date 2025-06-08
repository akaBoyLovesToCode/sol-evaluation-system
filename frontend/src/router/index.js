import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: '/evaluations',
        name: 'Evaluations',
        component: () => import('../views/Evaluations.vue')
      },
      {
        path: '/evaluations/new',
        name: 'NewEvaluation',
        component: () => import('../views/NewEvaluation.vue')
      },
      {
        path: '/evaluations/:id',
        name: 'EvaluationDetail',
        component: () => import('../views/EvaluationDetail.vue'),
        props: true
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { requiresRole: ['admin', 'group_leader'] }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('../views/Reports.vue')
      },
      {
        path: '/messages',
        name: 'Messages',
        component: () => import('../views/Messages.vue')
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果有token但没有用户信息，尝试获取用户信息
  if (authStore.token && !authStore.user) {
    try {
      await authStore.checkAuth()
    } catch (error) {
      console.error('Failed to check auth:', error)
    }
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 检查是否需要游客状态（如登录页）
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  // 检查角色权限
  if (to.meta.requiresRole && authStore.user) {
    const hasRole = to.meta.requiresRole.includes(authStore.user.role)
    if (!hasRole) {
      next('/')
      return
    }
  }
  
  next()
})

export default router 