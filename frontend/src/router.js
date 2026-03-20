import { createRouter, createWebHistory } from 'vue-router'

// Lazy-loaded routes
const LoginPage = () => import('./components/AuthLogin.vue')
const PatientTabs = () => import('./components/PatientTabs.vue')
const PatientManagementPage = () => import('./components/MainLayout.vue')
const Dashboard = () => import('./components/DoctorDashboard.vue')

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginPage },
  {
    path: '/patient',
    name: 'patient',
    component: PatientTabs,
    meta: { requiresAuth: true, roles: ['patient'] },
  },
  {
    path: '/doctor',
    name: 'doctor',
    component: PatientManagementPage,
    meta: { requiresAuth: true, roles: ['doctor'] },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  // Catch all - redirect to login
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  let user;
  try {
    user = JSON.parse(localStorage.getItem('user'))
  } catch {
    user = null
  }

  const isAuthenticated = !!token && !!user

  // 1. If route requires auth and not logged in
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login' })
  }

  // 2. If logged in and trying to go to login page, redirect to appropriate dashboard
  if (to.name === 'login' && isAuthenticated) {
    if (user.role === 'doctor') {
      return next({ name: 'doctor' })
    } else {
      return next({ name: 'patient' })
    }
  }

  // 3. Role check
  if (to.meta.roles && isAuthenticated) {
    if (!to.meta.roles.includes(user.role)) {
      // User does not have permission for this route
      if (user.role === 'doctor') {
        return next({ name: 'doctor' })
      } else {
        return next({ name: 'patient' })
      }
    }
  }

  next()
})

export default router
