import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TestPlayground from '../views/TestPlayground.vue'
import MustDoView from '../views/MustDoView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/playground',
      name: 'playground',
      component: TestPlayground
    },
    {
      path: '/mustdo',
      name: 'mustdo',
      component: MustDoView
    }
  ]
})

export default router
