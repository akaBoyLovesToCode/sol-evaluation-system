import { createRouter, createWebHistory } from 'vue-router'

const routes = [
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

export default router 