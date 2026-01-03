import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import TestPlayground from '../views/TestPlayground.vue'
import MustDoView from '../views/MustDoView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/playground',
      name: 'playground',
      component: TestPlayground,
      meta: { requiresAuth: true }
    },
    {
      path: '/mustdo',
      name: 'mustdo',
      component: MustDoView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/Login.vue')
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/auth/Signup.vue')
    },
    // Board Routes
    {
      path: '/board',
      name: 'board-list',
      component: () => import('../views/post/BoardListView.vue'), // Lazy load from views/post
      meta: { requiresAuth: true }
    },
    {
      path: '/board/write',
      name: 'board-write',
      component: () => import('../views/post/BoardWriteView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/board/:id',
      name: 'board-detail',
      component: () => import('../views/post/BoardDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/board/edit/:id',
      name: 'board-edit',
      component: () => import('../views/post/BoardWriteView.vue'), // Reusing WriteView for Edit
      meta: { requiresAuth: true }
    },
    // Chat Route
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/chat/ChatView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // If the route requires auth
  if (to.meta.requiresAuth) {
    // If not authenticated and checking auth hasn't happened yet
    if (!authStore.isAuthenticated && !authStore.isAuthChecked) {
      await authStore.checkAuth()
    }

    // If still not authenticated
    if (!authStore.isAuthenticated) {
      next({ name: 'login', replace: true })
      return
    }
  }
  next()
})

export default router
