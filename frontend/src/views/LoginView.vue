<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>人岗匹配心理特质评估系统</h2>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
            <el-form-item prop="username">
              <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" :rules="rules" ref="registerFormRef">
            <el-form-item prop="username">
              <el-input v-model="registerForm.username" placeholder="用户名" prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="email">
              <el-input v-model="registerForm.email" placeholder="邮箱" prefix-icon="Message" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="registerForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <!-- <el-form-item>
              <el-checkbox v-model="registerForm.is_hr">我是 HR（企业用户）</el-checkbox>
            </el-form-item> -->
            <el-form-item>
              <el-button type="success" @click="handleRegister" :loading="loading" style="width: 100%">注册</el-button>
            </el-form-item>
            <div class="form-tips">
              <p>💡 注册提示:</p>
              <ul>
                <li>用户名至少需要3个字符</li>
                <li>邮箱需要是有效的邮箱格式</li>
                <li>密码至少需要6个字符</li>
                <li>如果提示用户名或邮箱已存在，请使用不同的信息重新注册</li>
              </ul>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="tip">提示：首次使用请先注册</div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
const activeTab = ref('login')
const loading = ref(false)

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

const API_BASE = 'http://127.0.0.1:8000'

const router = useRouter()
const userStore = useUserStore()

const handleLogin = async () => {
  
  loading.value = true
  try {
    const res = await axios.post(`http://127.0.0.1:8000/auth/login`, {
      username: loginForm.username,
      password: loginForm.password
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      transformRequest: [data => new URLSearchParams(data).toString()]
    })
    userStore.login({
      access_token: res.data.access_token,
      is_hr: res.data.is_hr,
      username: loginForm.username
    })
    ElMessage.success('登录成功！')
    router.push('/home')  // 跳转主页
    console.log('Token:', res.data.access_token)
    console.log('是否HR:', res.data.is_hr)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  try {
    // 验证输入
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

    // 使用原始 axios，禁用 withCredentials
    const res = await axios.post(`${API_BASE}/auth/register`, formData, {
      withCredentials: false
    })

    ElMessage.success('注册成功！请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    // 清空注册表单
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
    registerForm.is_hr = false
  } catch (err: any) {
    console.error('注册错误:', err)
    
    // 获取具体的错误信息
    const detail = err.response?.data?.detail
    let errorMessage = '注册失败，请重试'
    
    // 解析错误信息，给出更友好的提示
    if (typeof detail === 'string') {
      // 后端返回的字符串错误信息
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
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 420px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.card-header {
  text-align: center;
  padding: 10px 0;
}

.tip {
  text-align: center;
  margin-top: 20px;
  color: #999;
  font-size: 14px;
}

.form-tips {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  padding: 12px 16px;
  margin-top: 16px;
  font-size: 12px;
  color: #0066cc;
}

.form-tips p {
  margin: 0 0 8px 0;
  font-weight: bold;
  color: #1890ff;
}

.form-tips ul {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.form-tips li {
  margin: 4px 0;
  padding-left: 16px;
  position: relative;
}

.form-tips li:before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #52c41a;
  font-weight: bold;
}
</style>