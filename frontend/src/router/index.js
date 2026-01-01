import { createRouter, createWebHistory } from 'vue-router'
import SettingsView from '../views/SettingsView.vue'
import StudentUploadView from '../views/StudentUploadView.vue'
import ObjectiveMarkingView from '../views/ObjectiveMarkingView.vue'
import ResultsView from '../views/ResultsView.vue'
import HistoryView from '../views/HistoryView.vue'
import SubjectiveView from '../views/SubjectiveView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/settings'
    },
    {
      path: '/subjective',
      name: 'subjective',
      component: SubjectiveView
    },
    {
      path: '/upload',
      name: 'upload',
      component: StudentUploadView
    },
    {
      path: '/objective',
      name: 'objective',
      component: ObjectiveMarkingView
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
