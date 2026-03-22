import { createApp } from 'vue'
import { createPinia } from 'pinia'  // If using Pinia
import App from './App.vue'
import router from './router.js'  // Adjust path if in src/router/
import './style.css'  // This loads Tailwind

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