import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'  // 引入路由
import { useUserStore } from '@/stores/user'

const app = createApp(App)  // 先创建 app 实例

// 依次使用插件（顺序无所谓，但必须在 mount 之前）
const pinia = createPinia()
app.use(pinia)
app.use(ElementPlus)
app.use(router)

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
// main.ts 或某个初始化文件
window.addEventListener('error', (event) => {
  if (event.message.includes('A listener indicated an asynchronous response')) {
    event.preventDefault()
    event.stopPropagation()
    console.warn('Ignored Vue Devtools async channel error')
  }
})
// 在挂载前恢复用户状态
const userStore = useUserStore()
userStore.restoreFromLocal()

// 最后挂载
app.mount('#app')