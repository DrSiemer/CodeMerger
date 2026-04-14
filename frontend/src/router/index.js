import { createRouter, createWebHashHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import CompactView from '../views/CompactView.vue'

const routes = [
  {
    path: '/',
    name: 'main',
    component: MainView
  },
  {
    path: '/compact',
    name: 'compact',
    component: CompactView
  }
]

const router = createRouter({
  // Use Hash history for compatibility with local filesystem loading (file://)
  history: createWebHashHistory(),
  routes
})

export default router