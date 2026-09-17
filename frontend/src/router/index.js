import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ResultsView from '../views/ResultsView.vue'
import DataExplorerView from '../views/DataExplorerView.vue'
import AiConfigView from '../views/AiConfigView.vue'
import LabsView from '../views/LabsView.vue'
import VaultView from '../views/VaultView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/results',
      name: 'results',
      component: ResultsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/data-explorer',
      name: 'data-explorer',
      component: DataExplorerView,
      meta: { requiresAuth: true }
    },
    {
      path: '/ai-settings',
      name: 'ai-settings',
      component: AiConfigView,
      meta: { requiresAuth: true }
    },
    {
      path: '/labs',
      name: 'labs',
      component: LabsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/vault',
      name: 'vault',
      component: VaultView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
