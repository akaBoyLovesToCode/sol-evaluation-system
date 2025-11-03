import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Evaluations',
    component: () => import('../views/Evaluations.vue'),
  },
  {
    path: '/evaluations',
    redirect: '/',
  },
  {
    path: '/evaluations/new',
    name: 'NewEvaluation',
    component: () => import('../views/NewEvaluation.vue'),
  },
  {
    path: '/evaluations/:id',
    name: 'EvaluationDetail',
    component: () => import('../views/EvaluationDetail.vue'),
    props: true,
  },
  {
    path: '/evaluations/:id/edit',
    name: 'EditEvaluation',
    component: () => import('../views/NewEvaluation.vue'),
    props: true,
  },
  {
    path: '/evaluations/:id/processes/edit',
    name: 'NestedProcessEditor',
    component: () => import('../views/ProcessPrototype.vue'),
    props: true,
  },
  {
    path: '/prototypes/process-builder',
    name: 'ProcessPrototype',
    component: () => import('../views/ProcessPrototype.vue'),
  },
  {
    path: '/demo/timeline',
    name: 'TimelineMatrixDemo',
    component: () => import('../pages/demo/TimelineMatrixDemo.vue'),
    meta: { demo: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
