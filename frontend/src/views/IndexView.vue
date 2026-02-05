<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref } from 'vue'
import { LogOut, User, Home } from '@element-plus/icons-vue'
import HomeView from './HomeView.vue'
import HRHomeView from './HRHomeView.vue'

const userStore = useUserStore()
const router = useRouter()

const activeMenu = ref('home')

// 菜单项配置
const getMenuItems = () => {
  const commonItems = [
    { index: 'home', label: '首页', icon: 'Home' }
  ]
  
  const candidateItems = [
    { index: 'jobs', label: '浏览岗位' },
    { index: 'interviews', label: '我的面试' },
    { index: 'reports', label: '报告中心' }
  ]
  
  const hrItems = [
    { index: 'jobs-manage', label: '岗位管理' },
    { index: 'candidates', label: '候选人' },
    { index: 'reports-manage', label: '数据分析' }
  ]
  
  const items = [...commonItems]
  if (userStore.isHR) {
    items.push(...hrItems)
  } else {
    items.push(...candidateItems)
  }
  return items
}

// 菜单点击处理
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  
  // 后续可以根据不同的菜单项进行路由导航
  switch(index) {
    case 'home':
      activeMenu.value = 'home'
      break
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'jobs':
      ElMessage.info('浏览岗位功能开发中')
      break
    case 'interviews':
      ElMessage.info('我的面试功能开发中')
      break
    case 'reports':
      ElMessage.info('报告中心功能开发中')
      break
    case 'jobs-manage':
      ElMessage.info('岗位管理功能开发中')
      break
    case 'candidates':
      ElMessage.info('候选人管理功能开发中')
      break
    case 'reports-manage':
      ElMessage.info('数据分析功能开发中')
      break
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    })
    .catch(() => {})
}

// 用户信息菜单
const userMenuItems = [
  { label: '个人信息', command: 'profile' },
  { label: '账号设置', command: 'settings' },
  { label: '退出登录', command: 'logout' }
]

const handleUserMenuCommand = (command: string) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中')
  } else if (command === 'settings') {
    ElMessage.info('账号设置功能开发中')
  }
}

// 获取角色标签样式
const getRoleTagStyle = () => {
  return userStore.isHR ? 'danger' : 'primary'
}

const getRoleLabel = () => {
  return userStore.isHR ? 'HR管理员' : '候选人'
}
</script>

<template>
  <el-container class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-left">
        <div class="app-logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">人岗匹配系统</span>
        </div>
      </div>

      <!-- 中间菜单 -->
      <div class="header-center">
        <el-menu 
          :default-active="activeMenu"
          mode="horizontal"
          @select="handleMenuSelect"
          class="header-menu"
        >
          <el-menu-item index="home">首页</el-menu-item>
          
          <!-- 候选人菜单 -->
          <template v-if="!userStore.isHR">
            <el-menu-item index="jobs">浏览岗位</el-menu-item>
            <el-menu-item index="interviews">我的面试</el-menu-item>
            <el-menu-item index="reports">报告中心</el-menu-item>
          </template>

          <!-- HR菜单 -->
          <template v-else>
            <el-menu-item index="jobs-manage">岗位管理</el-menu-item>
            <el-menu-item index="candidates">候选人</el-menu-item>
            <el-menu-item index="reports-manage">数据分析</el-menu-item>
          </template>
        </el-menu>
      </div>

      <!-- 右侧用户信息 -->
      <div class="header-right">
        <div class="user-info">
          <!-- 用户头像 -->
          <div class="user-avatar">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='12' fill='%234a90e2'/%3E%3Ccircle cx='12' cy='8' r='4' fill='%23fff'/%3E%3Cpath d='M4 20c0-4.418 3.582-8 8-8s8 3.582 8 8' fill='%23fff'/%3E%3C/svg%3E" alt="avatar" />
          </div>

          <!-- 用户名和角色 -->
          <div class="user-details">
            <span class="username">{{ userStore.username }}</span>
            <el-tag :type="getRoleTagStyle()" size="small" class="role-tag">
              {{ getRoleLabel() }}
            </el-tag>
          </div>

          <!-- 用户菜单下拉 -->
          <el-dropdown @command="handleUserMenuCommand" trigger="click">
            <span class="dropdown-icon">⋮</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">账号设置</el-dropdown-item>
                <el-dropdown-divider />
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="app-main">
      <!-- 候选人主页 -->
      <HomeView v-if="!userStore.isHR && activeMenu === 'home'" />
      
      <!-- HR主页 -->
      <HRHomeView v-else-if="userStore.isHR && activeMenu === 'home'" />

      <!-- 其他功能占位符 -->
      <div v-else class="feature-placeholder">
        <el-empty description="功能开发中，敬请期待" />
      </div>
    </el-main>
  </el-container>
</template>

<style scoped>
.main-layout {
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* ========== 头部导航栏 ========== */
.app-header {
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #eaeef4;
  position: relative;
  z-index: 100;
}

.header-left {
  flex-shrink: 0;
  margin-right: 40px;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
  color: #1f2937;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.app-logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ========== 中间菜单 ========== */
.header-center {
  flex: 1;
}

:deep(.header-menu) {
  border-bottom: none;
  background: transparent;
}

:deep(.header-menu .el-menu-item) {
  height: 60px;
  line-height: 60px;
  font-size: 14px;
  color: #666;
  transition: all 0.3s ease;
}

:deep(.header-menu .el-menu-item:hover) {
  color: #667eea;
  background: transparent !important;
}

:deep(.header-menu .el-menu-item.is-active) {
  color: #667eea;
  border-bottom: 3px solid #667eea;
}

/* ========== 右侧用户信息 ========== */
.header-right {
  flex-shrink: 0;
  margin-left: 40px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.user-info:hover {
  background: #eaeef4;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #667eea;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 80px;
}

.username {
  font-size: 13px;
  font-weight: 500;
  color: #1f2937;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100px;
}

.role-tag {
  margin-top: 2px;
  font-size: 11px;
}

.dropdown-icon {
  font-size: 18px;
  color: #999;
  transition: color 0.3s ease;
  cursor: pointer;
}

.dropdown-icon:hover {
  color: #667eea;
}

/* ========== 主内容区 ========== */
.app-main {
  background: transparent;
  padding: 24px;
  overflow-y: auto;
}

.feature-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* ========== 响应式设计 ========== */
@media (max-width: 1200px) {
  .header-left {
    margin-right: 20px;
  }

  .header-right {
    margin-left: 20px;
  }

  .user-details {
    display: none;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }

  .header-left {
    margin-right: 12px;
  }

  :deep(.header-menu .el-menu-item) {
    padding: 0 8px;
    font-size: 12px;
  }

  .logo-text {
    display: none;
  }

  .header-right {
    margin-left: 0;
  }

  .user-info {
    gap: 8px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }
}
</style>
