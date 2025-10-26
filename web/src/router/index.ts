import { createRouter, createWebHistory } from 'vue-router'
import BookSelection from '@/view/BookSelection.vue'
import StudyView from '@/view/StudyView.vue'
import StudyComplete from '../components/StudyComplete.vue'
const routes = [
  {
    path: '/',
    name: 'BookSelection',
    component: BookSelection
  },
  {
    path: '/memory/:bookId',
    name: 'MemoryAssist',
    component: StudyView,
    props: true
  },
  {
    path: '/study-complete',
    name: 'StudyComplete',
    component: StudyComplete
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router