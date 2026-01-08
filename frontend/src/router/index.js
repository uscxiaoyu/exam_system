import { createRouter, createWebHistory } from 'vue-router'
import SettingsView from '../views/SettingsView.vue'
import StudentUploadView from '../views/StudentUploadView.vue'
import ObjectiveMarkingView from '../views/ObjectiveMarkingView.vue'
import ResultsView from '../views/ResultsView.vue'
import HistoryView from '../views/HistoryView.vue'
import SubjectiveView from '../views/SubjectiveView.vue'
import LoginView from '../views/LoginView.vue'
import ClassManagementView from '../views/ClassManagementView.vue'
import TaskAssignmentView from '../views/TaskAssignmentView.vue'
import ExamManagementView from '../views/ExamManagementView.vue'
import StudentDashboard from '../views/student/StudentDashboard.vue'
import ExamTakingView from '../views/student/ExamTakingView.vue'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/classes',
      name: 'classes',
      component: ClassManagementView,
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: TaskAssignmentView,
      meta: { requiresAuth: true }
    },
    {
      path: '/exams',
      name: 'exams',
      component: ExamManagementView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/dashboard',
      name: 'student-dashboard',
      component: StudentDashboard,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/exam/:id',
      name: 'student-exam-taking',
      component: ExamTakingView,
      meta: { requiresAuth: true }
    },
    {
      path: '/',
      redirect: '/settings',
      meta: { requiresAuth: true }
    },
    {
      path: '/subjective',
      name: 'subjective',
      component: SubjectiveView,
      meta: { requiresAuth: true }
    },
    {
      path: '/upload',
      name: 'upload',
      component: StudentUploadView,
      meta: { requiresAuth: true }
    },
    {
      path: '/objective',
      name: 'objective',
      component: ObjectiveMarkingView,
      meta: { requiresAuth: true }
    },
    {
      path: '/results',
      name: 'results',
      component: ResultsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
