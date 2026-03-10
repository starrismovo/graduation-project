import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')  // 强制指定 @ 别名
    }
  },
  server: {
    // 开发服务器代理配置
    proxy: {
      // 代理所有 /assessment 开头的请求到后端
      '/assessment': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path  // 保持原始路径
      },
      // 代理其他后端API路由
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})
