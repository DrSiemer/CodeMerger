import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import vInfo from './directives/vInfo'

const app = createApp(App)

// Setup Router
app.use(router)

// Register custom directives
app.directive('info', vInfo)

app.mount('#app')