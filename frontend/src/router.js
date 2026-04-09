import { createRouter, createWebHistory } from 'vue-router'

// Lazy-loaded routes
const LoginPage = () => import('./components/AuthLogin.vue')
const PatientTabs = () => import('./components/PatientTabs.vue')
const PatientManagementPage = () => import('./components/MainLayout.vue')
const Dashboard = () => import('./components/DoctorDashboard.vue')
const AdminDashboard = () => import('./components/AdminDashboard.vue')

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
  {
    path: '/admin',
    name: 'admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  // Catch all - redirect to login
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  console.log(`Navigating to: ${to.path}`)
  const token = localStorage.getItem('token')
  let user
  try {
    const userStr = localStorage.getItem('user')
    user = userStr ? JSON.parse(userStr) : null
  } catch (err) {
    console.error('Router: Failed to parse user from localStorage', err)
    user = null
  }

  const isAuthenticated = !!token && !!user && !!user.role

  // 1. If route requires auth and not logged in
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.warn('Router: Unauthorized access attempt, redirecting to login')
    return next({ name: 'login' })
  }

  // 2. If logged in and trying to go to login page, redirect to appropriate dashboard
  if (to.name === 'login' && isAuthenticated) {
    console.log(`Router: Already authenticated as ${user.role}, redirecting to dashboard`)
    if (user.role === 'doctor') {
      return next({ name: 'doctor' })
    } else if (user.role === 'admin') {
      return next({ name: 'admin' })
    } else {
      return next({ name: 'patient' })
    }
  }

  // 3. Role check
  if (to.meta.roles && isAuthenticated) {
    if (!to.meta.roles.includes(user.role)) {
      console.warn(`Router: Role mismatch. User role ${user.role} not in ${to.meta.roles}`)
      if (user.role === 'doctor') {
        return next({ name: 'doctor' })
      } else if (user.role === 'admin') {
        return next({ name: 'admin' })
      } else {
        return next({ name: 'patient' })
      }
    }
  }

  next()
})

router.onError((error) => {
  const message = String(error?.message || '')
  const isChunkLoadError =
    message.includes('Failed to fetch dynamically imported module') ||
    message.includes('Importing a module script failed') ||
    message.includes('Loading CSS chunk')

  if (!isChunkLoadError) return

  const onceKey = 'router-chunk-reloaded'
  if (sessionStorage.getItem(onceKey) === '1') return

  console.warn('Router chunk load failed, reloading to refresh stale assets', error)
  sessionStorage.setItem(onceKey, '1')
  window.location.reload()
})

export default router
