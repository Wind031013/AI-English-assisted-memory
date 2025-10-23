import { createRouter, createWebHistory } from 'vue-router'
import BookSelection from '../components/BookSelection.vue'
import MemoryAssist from '../components/MemoryAssist.vue'
const routes = [
  {
    path: '/',
    name: 'BookSelection',
    component: BookSelection
  },
  {
    path: '/memory/:bookId',
    name: 'MemoryAssist',
    component: MemoryAssist,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router