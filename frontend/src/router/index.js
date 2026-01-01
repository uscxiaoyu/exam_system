import { createRouter, createWebHistory } from 'vue-router'
import ConfigView from '../views/ConfigView.vue'
import UploadView from '../views/UploadView.vue'
import ResultsView from '../views/ResultsView.vue'
import HistoryView from '../views/HistoryView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'config',
      component: ConfigView
    },
    {
      path: '/upload',
      name: 'upload',
      component: UploadView
    },
    {
      path: '/results',
      name: 'results',
      component: ResultsView
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    }
  ]
})

export default router
