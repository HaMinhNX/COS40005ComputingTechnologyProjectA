import { createApp } from 'vue'
import { createPinia } from 'pinia'  // If using Pinia
import App from './App.vue'
import router from './router.js'  // Adjust path if in src/router/
import './style.css'  // This loads Tailwind

// Recover from stale hashed assets after deployment (e.g. CSS/JS chunk 404).
window.addEventListener('vite:preloadError', (event) => {
  if (event?.preventDefault) event.preventDefault()

  const onceKey = 'vite-preload-reloaded'
  if (sessionStorage.getItem(onceKey) === '1') return

  sessionStorage.setItem(onceKey, '1')
  window.location.reload()
})

const app = createApp(App)

// Global error handler for debugging blank page issues
app.config.errorHandler = (err, instance, info) => {
  console.error('GLOBAL ERROR:', err)
  console.error('Vue Instance:', instance)
  console.error('Error Info:', info)
  // Optionally display a visible alert for the user in development
  if (import.meta.env.DEV) {
    alert(`Frontend Error: ${err.message}\nCheck console for details.`)
  }
}

app.use(createPinia())
app.use(router)
app.mount('#app')