import { createApp } from 'vue'
import { createPinia } from 'pinia'  // If using Pinia
import App from './App.vue'
import router from './router.js'  // Adjust path if in src/router/
import './style.css'  // This loads Tailwind

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')