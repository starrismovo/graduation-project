<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref } from 'vue'
import HomeView from './HomeView.vue'
import HRHomeView from './HRHomeView.vue'

const userStore = useUserStore()
const router = useRouter()

const activeMenu = ref('home')

// 菜单点击处理
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  
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
      router.push('/job-manage')
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

// 用户菜单命令处理
const handleUserMenuCommand = (command: string) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中')
  } else if (command === 'settings') {
    ElMessage.info('账号设置功能开发中')
  }
}
</script>

<template>
  <el-container class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-container">
        <!-- 左侧Logo -->
        <div class="header-left">
          <div class="app-logo" @click="activeMenu = 'home'">
            <svg class="logo-icon" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea"/>
                  <stop offset="100%" style="stop-color:#764ba2"/>
                </linearGradient>
              </defs>
              <rect width="32" height="32" rx="8" fill="url(#logoGrad)"/>
              <path d="M16 8L24 13L23 19L16 23L9 19L8 13Z" fill="none" stroke="white" stroke-width="2"/>
              <circle cx="14" cy="15" r="2" fill="white"/>
              <circle cx="18" cy="15" r="2" fill="white"/>
              <path d="M12 21Q16 24 20 21" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round"/>
            </svg>
            <span class="logo-text">AI 人岗匹配</span>
          </div>
        </div>

        <!-- 中间导航菜单 -->
        <div class="header-center">
          <nav class="main-nav">
            <button 
              :class="['nav-item', { active: activeMenu === 'home' }]"
              @click="handleMenuSelect('home')"
            >
              <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              <span>首页</span>
            </button>
            
            <!-- 候选人菜单 -->
            <template v-if="!userStore.isHR">
              <button 
                :class="['nav-item', { active: activeMenu === 'jobs' }]"
                @click="handleMenuSelect('jobs')"
              >
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd" />
                  <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
                </svg>
                <span>浏览岗位</span>
              </button>
              
              <button 
                :class="['nav-item', { active: activeMenu === 'interviews' }]"
                @click="handleMenuSelect('interviews')"
              >
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                </svg>
                <span>我的面试</span>
              </button>
              
              <button 
                :class="['nav-item', { active: activeMenu === 'reports' }]"
                @click="handleMenuSelect('reports')"
              >
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
                </svg>
                <span>报告中心</span>
              </button>
            </template>

            <!-- HR菜单 -->
            <template v-else>
              <button 
                :class="['nav-item', { active: activeMenu === 'jobs-manage' }]"
                @click="handleMenuSelect('jobs-manage')"
              >
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                </svg>
                <span>岗位管理</span>
              </button>
              
              <button 
                :class="['nav-item', { active: activeMenu === 'candidates' }]"
                @click="handleMenuSelect('candidates')"
              >
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                </svg>
                <span>候选人</span>
              </button>
              
              <button 
                :class="['nav-item', { active: activeMenu === 'reports-manage' }]"
                @click="handleMenuSelect('reports-manage')"
              >
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
                <span>数据分析</span>
              </button>
            </template>
          </nav>
        </div>

        <!-- 右侧用户区域 -->
        <div class="header-right">
          <el-dropdown @command="handleUserMenuCommand" trigger="click">
            <div class="user-profile">
              <div class="user-avatar">
                <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="avatarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#667eea"/>
                      <stop offset="100%" style="stop-color:#764ba2"/>
                    </linearGradient>
                  </defs>
                  <circle cx="16" cy="16" r="16" fill="url(#avatarGrad)"/>
                  <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
                  <path d="M6 28c0-5.5 4.5-10 10-10s10 4.5 10 10" fill="white" opacity="0.9"/>
                </svg>
              </div>
              <div class="user-info">
                <div class="user-name">{{ userStore.username }}</div>
                <div class="user-role">{{ userStore.isHR ? 'HR 管理员' : '候选人' }}</div>
              </div>
              <svg class="dropdown-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </div>
            
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown-menu">
                <el-dropdown-item command="profile">
                  <svg class="menu-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
                  <span>个人信息</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <svg class="menu-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                  </svg>
                  <span>账号设置</span>
                </el-dropdown-item>
                <div class="dropdown-divider"></div>
                <el-dropdown-item command="logout">
                  <svg class="menu-icon logout-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
                  </svg>
                  <span>退出登录</span>
                </el-dropdown-item>
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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.main-layout {
  height: 100vh;
  background: #f5f7fa;
}

/* ========== 顶部导航栏 ========== */
.app-header {
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  padding: 0;
  height: 64px;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 40px;
}

/* ========== Logo区域 ========== */
.header-left {
  flex-shrink: 0;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
  transition: transform 0.2s ease;
}

.app-logo:hover {
  transform: scale(1.02);
}

.logo-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.3px;
}

/* ========== 中间导航菜单 ========== */
.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.main-nav {
  display: flex;
  gap: 4px;
  background: #f9fafb;
  padding: 4px;
  border-radius: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  outline: none;
}

.nav-item:hover {
  color: #374151;
  background: rgba(255, 255, 255, 0.6);
}

.nav-item.active {
  color: #667eea;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1),
              0 1px 2px rgba(0, 0, 0, 0.06);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* ========== 右侧用户区域 ========== */
.header-right {
  flex-shrink: 0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px 8px 8px;
  background: #f9fafb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.user-profile:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.user-avatar svg {
  width: 100%;
  height: 100%;
  display: block;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 100px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.3;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  color: #9ca3af;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.user-profile:hover .dropdown-arrow {
  color: #6b7280;
  transform: translateY(1px);
}

/* ========== 用户下拉菜单样式 ========== */
:deep(.user-dropdown-menu) {
  margin-top: 8px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 6px;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s ease;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item:hover) {
  background: #f3f4f6;
  color: #1a1a1a;
}

.menu-icon {
  width: 18px;
  height: 18px;
  color: #6b7280;
  flex-shrink: 0;
}

.logout-icon {
  color: #ef4444;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item:hover .logout-icon) {
  color: #dc2626;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 6px 0;
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
  min-height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

/* ========== 响应式设计 ========== */
@media (max-width: 1200px) {
  .header-container {
    gap: 24px;
  }

  .nav-item span {
    display: none;
  }

  .nav-item {
    padding: 10px 12px;
  }

  .user-info {
    display: none;
  }

  .user-profile {
    padding: 8px;
  }
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
    gap: 16px;
  }

  .logo-text {
    font-size: 16px;
  }

  .main-nav {
    gap: 2px;
    padding: 3px;
  }

  .nav-item {
    padding: 8px 10px;
  }

  .nav-icon {
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 480px) {
  .logo-text {
    display: none;
  }

  .logo-icon {
    width: 32px;
    height: 32px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
  }

  .dropdown-arrow {
    display: none;
  }
}
</style>
