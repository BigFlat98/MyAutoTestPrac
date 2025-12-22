import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // 추가됨

const app = createApp(App)

app.use(router) // 추가됨
app.mount('#app')