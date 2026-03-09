<template>
  <div class="login-wrapper">
    <!-- 左侧品牌区 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="logo-area">
          <div class="logo-icon">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea"/>
                  <stop offset="100%" style="stop-color:#764ba2"/>
                </linearGradient>
                <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#8b5cf6"/>
                  <stop offset="100%" style="stop-color:#6366f1"/>
                </linearGradient>
                <linearGradient id="pulse" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#8b5cf6">
                    <animate attributeName="stop-color" values="#8b5cf6;#a78bfa;#8b5cf6" dur="3s" repeatCount="indefinite"/>
                  </stop>
                  <stop offset="100%" stop-color="#a78bfa">
                    <animate attributeName="stop-color" values="#a78bfa;#8b5cf6;#a78bfa" dur="3s" repeatCount="indefinite"/>
                  </stop>
                </linearGradient>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="1.5" result="blur"/>
                  <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
                <linearGradient id="data-flow" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="transparent" stop-opacity="0.3">
                    <animate attributeName="offset" values="0;1;0" dur="2s" repeatCount="indefinite"/>
                  </stop>
                  <stop offset="50%" stop-color="#c4b5fd" stop-opacity="0.8">
                    <animate attributeName="offset" values="0.2;1.2;0.2" dur="2s" repeatCount="indefinite"/>
                  </stop>
                  <stop offset="100%" stop-color="transparent" stop-opacity="0.3">
                    <animate attributeName="offset" values="0.5;1.5;0.5" dur="2s" repeatCount="indefinite"/>
                  </stop>
                </linearGradient>
              </defs>
              <rect x="5" y="5" width="90" height="90" rx="20" fill="url(#bg)" stroke="rgba(255,255,255,0.3)" stroke-width="2.5" filter="url(#glow)"/>
              <path d="M50 18 L70 32 L66 56 L50 68 L34 56 L30 32 Z" fill="none" stroke="rgba(255,255,255,0.8)" stroke-width="3.5" stroke-linejoin="round"/>
              <circle cx="44" cy="42" r="5" fill="#c4b5fd">
                <animate attributeName="r" values="5;6;5" dur="2s" repeatCount="indefinite"/>
              </circle>
              <circle cx="56" cy="42" r="5" fill="#e0e7ff">
                <animate attributeName="r" values="5;6;5" dur="2s" repeatCount="indefinite" begin="0.5s"/>
              </circle>
              <path d="M38 62 Q50 72 62 62" fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="3" stroke-linecap="round">
                <animate attributeName="stroke-width" values="3;4;3" dur="1.5s" repeatCount="indefinite"/>
              </path>
              <line x1="18" y1="50" x2="34" y2="42" stroke="url(#pulse)" stroke-width="2.5" opacity="0.7"/>
              <line x1="82" y1="50" x2="66" y2="42" stroke="url(#pulse)" stroke-width="2.5" opacity="0.7"/>
              <line x1="50" y1="82" x2="50" y2="68" stroke="url(#pulse)" stroke-width="2.5" opacity="0.7"/>
              <line x1="18" y1="50" x2="34" y2="42" stroke="url(#data-flow)" stroke-width="1.5" opacity="0.5"/>
              <line x1="82" y1="50" x2="66" y2="42" stroke="url(#data-flow)" stroke-width="1.5" opacity="0.5"/>
              <line x1="50" y1="82" x2="50" y2="68" stroke="url(#data-flow)" stroke-width="1.5" opacity="0.5"/>
              <circle cx="18" cy="50" r="3.5" fill="rgba(255,255,255,0.85)">
                <animate attributeName="r" values="3.5;4.5;3.5" dur="1.8s" repeatCount="indefinite"/>
              </circle>
              <circle cx="82" cy="50" r="3.5" fill="rgba(255,255,255,0.85)">
                <animate attributeName="r" values="3.5;4.5;3.5" dur="1.8s" repeatCount="indefinite" begin="0.3s"/>
              </circle>
              <circle cx="50" cy="82" r="3.5" fill="rgba(255,255,255,0.85)">
                <animate attributeName="r" values="3.5;4.5;3.5" dur="1.8s" repeatCount="indefinite" begin="0.6s"/>
              </circle>
              <circle cx="25" cy="25" r="0.8" fill="rgba(255,255,255,0.6)" opacity="0.6">
                <animate attributeName="opacity" values="0.2;0.6;0.2" dur="3s" repeatCount="indefinite"/>
                <animate attributeName="cx" values="22;28;22" dur="4s" repeatCount="indefinite"/>
              </circle>
              <circle cx="75" cy="75" r="0.8" fill="rgba(255,255,255,0.6)" opacity="0.6">
                <animate attributeName="opacity" values="0.2;0.6;0.2" dur="3s" repeatCount="indefinite" begin="1s"/>
                <animate attributeName="cy" values="72;78;72" dur="4s" repeatCount="indefinite" begin="1s"/>
              </circle>
            </svg>
          </div>
          <h1 class="system-title">AI 人岗匹配系统</h1>
          <p class="system-subtitle">Psychological Assessment & Job Matching Platform</p>
        </div>
        
        <div class="features-list">
          <div class="feature-item" v-for="(feature, index) in features" :key="index">
            <div class="feature-icon">
              <component :is="feature.icon" />
            </div>
            <div class="feature-text">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.desc }}</p>
            </div>
          </div>
        </div>
        
        <div class="brand-footer">
          <p class="copyright">© 2026 AI 心理特质评估系统 </p>
        </div>
      </div>
    </div>
    
    <!-- 右侧登录区 -->
    <div class="form-section">
      <div class="login-card">
        <!-- 卡片标题区 -->
        <div class="card-header">
          <h2 class="main-title">{{ activeTab === 'login' ? '欢迎回来' : '创建账户' }}</h2>
          <p class="sub-title">AI 人岗匹配系统 · 企业管理入口</p>
        </div>

        <!-- Segmented Control 切换 -->
        <div class="segmented-control">
          <button 
            :class="['segment-btn', { active: activeTab === 'login' }]"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button 
            :class="['segment-btn', { active: activeTab === 'register' }]"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <div v-show="activeTab === 'login'" class="form-area">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef" @submit.prevent="handleLogin">
            <el-form-item prop="username">
              <div class="form-label">用户名</div>
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名" 
                size="large"
                class="custom-input"
              >
                <template #prefix>
                  <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <div class="form-label">密码</div>
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码" 
                size="large"
                show-password
                class="custom-input"
              >
                <template #prefix>
                  <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                </template>
              </el-input>
            </el-form-item>

            <!-- 辅助操作行 -->
            <div class="form-options">
              <el-checkbox v-model="rememberMe" class="remember-checkbox">
                记住我
              </el-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>
            
            <!-- 登录按钮 -->
            <el-form-item class="submit-area">
              <button 
                type="button"
                @click="handleLogin" 
                :disabled="loading"
                class="submit-button"
              >
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 注册表单 -->
        <div v-show="activeTab === 'register'" class="form-area">
          <el-form :model="registerForm" :rules="rules" ref="registerFormRef" @submit.prevent="handleRegister">
            <el-form-item prop="username">
              <div class="form-label">用户名</div>
              <el-input 
                v-model="registerForm.username" 
                placeholder="至少 3 个字符" 
                size="large"
                class="custom-input"
              >
                <template #prefix>
                  <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="email">
              <div class="form-label">邮箱地址</div>
              <el-input 
                v-model="registerForm.email" 
                placeholder="example@company.com" 
                size="large"
                class="custom-input"
              >
                <template #prefix>
                  <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                    <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                  </svg>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <div class="form-label">密码</div>
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="至少 6 个字符" 
                size="large"
                show-password
                class="custom-input"
              >
                <template #prefix>
                  <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                </template>
              </el-input>
            </el-form-item>

            <!-- 注册提示 -->
            <div class="register-notice">
              <svg class="notice-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              <div class="notice-content">
                <div class="notice-title">注册须知</div>
                <ul class="notice-list">
                  <li>用户名至少 3 个字符</li>
                  <li>请使用有效的企业邮箱</li>
                  <li>密码长度至少 6 个字符</li>
                </ul>
              </div>
            </div>
            
            <!-- 注册按钮 -->
            <el-form-item class="submit-area">
              <button 
                type="button"
                @click="handleRegister" 
                :disabled="loading"
                class="submit-button"
              >
                {{ loading ? '注册中...' : '立即注册' }}
              </button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const activeTab = ref('login')
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  is_hr: false
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }]
}

// 功能特性数据
const features = [
  {
    icon: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
      h('path', { d: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z' })
    ]),
    title: '智能评估',
    desc: '基于大数据的心理特质精准分析'
  },
  {
    icon: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
      h('path', { d: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z' })
    ]),
    title: '人岗匹配',
    desc: 'AI 驱动的职位推荐与适配度分析'
  },
  {
    icon: () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
      h('path', { d: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z' })
    ]),
    title: '数据洞察',
    desc: '可视化报告与专业解读'
  }
]

const API_BASE = 'http://127.0.0.1:8000'
const router = useRouter()
const userStore = useUserStore()

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await axios.post(`${API_BASE}/auth/login`, {
      username: loginForm.username,
      password: loginForm.password
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      transformRequest: [data => new URLSearchParams(data).toString()]
    })
    
    // 保存登录信息到store
    userStore.login({
      access_token: res.data.access_token,
      is_hr: res.data.is_hr,
      username: res.data.username,
      user_id: res.data.user_id,
      email: res.data.email
    })
    
    ElMessage.success('登录成功！')
    
    // 所有用户都跳转到 /home（IndexView），由内部根据角色显示不同页面
    router.push('/home')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  try {
    if (!registerForm.username || registerForm.username.length < 3) {
      ElMessage.warning('用户名至少3个字符')
      loading.value = false
      return
    }
    if (!registerForm.email || !registerForm.email.includes('@')) {
      ElMessage.warning('邮箱格式不正确')
      loading.value = false
      return
    }
    if (!registerForm.password || registerForm.password.length < 6) {
      ElMessage.warning('密码至少6个字符')
      loading.value = false
      return
    }

    const formData = new FormData()
    formData.append('username', registerForm.username)
    formData.append('email', registerForm.email)
    formData.append('password', registerForm.password)
    formData.append('is_hr', registerForm.is_hr.toString())

    await axios.post(`${API_BASE}/auth/register`, formData, {
      withCredentials: false
    })

    ElMessage.success('注册成功！请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
    registerForm.is_hr = false
  } catch (err: any) {
    console.error('注册错误:', err)
    const detail = err.response?.data?.detail
    let errorMessage = '注册失败，请重试'
    
    if (typeof detail === 'string') {
      if (detail.includes('用户名')) {
        errorMessage = `❌ ${detail}`
      } else if (detail.includes('邮箱')) {
        errorMessage = `📧 ${detail}`
      } else if (detail.includes('密码')) {
        errorMessage = `🔐 ${detail}`
      } else {
        errorMessage = detail
      }
    } else if (err.response?.status === 500) {
      errorMessage = '服务器错误，请检查后端是否运行正常'
    } else if (err.message === 'Network Error') {
      errorMessage = '网络错误，无法连接到服务器，请检查后端是否启动'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-wrapper {
  display: flex;
  min-height: 100vh;
  background: #fafbfc;
}

/* ========== 左侧品牌区 ========== */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  filter: blur(80px);
}

.brand-content {
  position: relative;
  z-index: 1;
  color: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.logo-area {
  margin-bottom: 60px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.system-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.system-subtitle {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 300;
  letter-spacing: 0.5px;
}

.features-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 32px;
  margin: 40px 0;
}

.feature-item {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding: 24px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(8px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.feature-text h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.feature-text p {
  font-size: 14px;
  opacity: 0.85;
  line-height: 1.6;
}

.brand-footer {
  margin-top: auto;
  padding-top: 40px;
}

.copyright {
  font-size: 13px;
  opacity: 0.7;
}

/* ========== 右侧登录卡片区 ========== */
.form-section {
  flex: 0 0 560px;
  background: #fafbfc;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  border-radius: 12px;
  padding: 48px 40px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 
              0 8px 24px rgba(0, 0, 0, 0.06);
}

/* 卡片标题区 */
.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.main-title {
  font-size: 26px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.sub-title {
  font-size: 14px;
  color: #6b7280;
  font-weight: 400;
}

/* Segmented Control */
.segmented-control {
  display: flex;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 32px;
}

.segment-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.segment-btn.active {
  background: #ffffff;
  color: #1a1a1a;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05),
              0 1px 3px rgba(0, 0, 0, 0.1);
}

.segment-btn:hover:not(.active) {
  color: #374151;
}

/* 表单区域 */
.form-area {
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(8px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

/* 自定义输入框样式 */
:deep(.custom-input .el-input__wrapper) {
  border-radius: 8px;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  box-shadow: none;
  background: #fafbfc;
  transition: all 0.2s ease;
}

:deep(.custom-input .el-input__wrapper:hover) {
  border-color: #d1d5db;
  background: #ffffff;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  border-color: #6366f1;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

:deep(.custom-input .el-input__inner) {
  color: #1a1a1a;
  font-size: 14px;
}

:deep(.custom-input .el-input__inner::placeholder) {
  color: #9ca3af;
}

.input-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
}

/* 辅助操作行 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 28px;
}

:deep(.remember-checkbox) {
  font-size: 14px;
  color: #6b7280;
}

:deep(.remember-checkbox .el-checkbox__label) {
  color: #6b7280;
  font-size: 14px;
}

:deep(.remember-checkbox .el-checkbox__inner) {
  border-radius: 4px;
  border-color: #d1d5db;
}

:deep(.remember-checkbox .el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #6366f1;
  border-color: #6366f1;
}

.forgot-link {
  font-size: 14px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.forgot-link:hover {
  color: #4f46e5;
}

/* 注册提示 */
.register-notice {
  display: flex;
  gap: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0 28px;
}

.notice-icon {
  width: 20px;
  height: 20px;
  color: #6366f1;
  flex-shrink: 0;
  margin-top: 2px;
}

.notice-content {
  flex: 1;
}

.notice-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.notice-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.notice-list li {
  font-size: 13px;
  color: #6b7280;
  padding: 3px 0 3px 16px;
  position: relative;
  line-height: 1.5;
}

.notice-list li::before {
  content: '·';
  position: absolute;
  left: 6px;
  color: #9ca3af;
  font-weight: bold;
  font-size: 16px;
}

/* 提交按钮 */
.submit-area {
  margin-bottom: 0;
  margin-top: 4px;
}

.submit-button {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  letter-spacing: 0.3px;
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transform: translateY(-1px);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .brand-section {
    display: none;
  }
  
  .form-section {
    flex: 1;
  }
}

@media (max-width: 640px) {
  .form-section {
    padding: 20px;
  }
  
  .login-card {
    padding: 32px 24px;
  }
  
  .main-title {
    font-size: 22px;
  }
}
</style>
