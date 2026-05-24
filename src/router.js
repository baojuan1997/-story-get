import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import DetailView from './views/DetailView.vue'
import HistoryView from './views/HistoryView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/history', component: HistoryView },
    { path: '/detail/:id', component: DetailView, props: true },
  ],
})

export default router
