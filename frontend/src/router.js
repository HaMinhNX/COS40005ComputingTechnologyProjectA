import { createRouter, createWebHistory } from 'vue-router'

// Lazy-loaded routes
const LoginPage = () => import('./components/Login.vue')
const PatientTabs = () => import('./components/PatientTabs.vue')
const PatientManagementPage = () => import('./components/index.vue')
const Dashboard = () => import('./components/Dashboard.vue')

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/patient', name: 'patient', component: PatientTabs },
  { path: '/doctor', name: 'doctor', component: PatientManagementPage },
  { path: '/dashboard', name: 'dashboard', component: Dashboard },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router