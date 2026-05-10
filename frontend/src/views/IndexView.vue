<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ArrowLeftBold, ArrowRightBold } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request, { fetchNotificationSummary } from '../utils/request'
import { useAssessmentStore } from '@/stores/assessment'

const userStore = useUserStore()
const router = useRouter()
const assessmentStore = useAssessmentStore()

const activeMenu = ref('home')
const isSidebarCollapsed = ref(false)
const notificationSummary = ref<{ unread_count: number; items: any[] }>({
  unread_count: 0,
  items: []
})

const candidateMenus = [
  { key: 'home', label: '首页', icon: 'home' },
  { key: 'jobs', label: '岗位浏览', icon: 'jobs' },
  { key: 'interviews', label: '我的面试', icon: 'interviews' },
  { key: 'reports', label: '报告中心', icon: 'reports' },
  { key: 'psychology', label: '心理解读', icon: 'psychology' },
  { key: 'profile', label: '设置中心', icon: 'settings' }
]

const hrMenus = [
  { key: 'home', label: '首页', icon: 'home' },
  { key: 'jobs-manage', label: '岗位管理', icon: 'jobs' },
  { key: 'candidates', label: '候选人', icon: 'users' },
  { key: 'reports-manage', label: '数据分析', icon: 'analytics' },
  { key: 'profile', label: '设置中心', icon: 'settings' }
]

const sideMenus = computed(() => (userStore.isHR ? hrMenus : candidateMenus))
const assistantTitle = computed(() => (userStore.isHR ? 'AI 招聘助理' : 'AI 职业咨询师'))

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const collapseSidebarOnHover = () => {
  if (!isSidebarCollapsed.value) {
    isSidebarCollapsed.value = true
  }
}

const updateActiveMenu = () => {
  const path = router.currentRoute.value.path
  if (path === '/home') {
    activeMenu.value = 'home'
  } else if (path.startsWith('/home/profile') || path.startsWith('/home/settings')) {
    activeMenu.value = 'profile'
  } else if (path.startsWith('/home/jobs')) {
    activeMenu.value = 'jobs'
  } else if (path.startsWith('/home/interviews') || path.startsWith('/home/immersive')) {
    activeMenu.value = 'interviews'
  } else if (path.startsWith('/home/job-manage')) {
    activeMenu.value = 'jobs-manage'
  } else if (path.startsWith('/home/candidates')) {
    activeMenu.value = 'candidates'
  } else if (path.startsWith('/home/analytics')) {
    activeMenu.value = 'reports-manage'
  } else if (path.startsWith('/home/reports') || path.startsWith('/home/report')) {
    activeMenu.value = 'reports'
  } else if (path.startsWith('/home/psychology')) {
    activeMenu.value = 'psychology'
  } else {
    activeMenu.value = 'home'
  }
}

router.afterEach(() => {
  updateActiveMenu()
})

onMounted(async () => {
  updateActiveMenu()
  try {
    const response = await request.get('/user/profile')
    if (response.data?.code === 200 && response.data?.data) {
      const userData = response.data.data
      const profileData = {
        ...userData,
        avatar: userData.avatar || userData.head_photo || userData.avatar_url || null,
        realName: userData.real_name || userData.realName || null,
        deliveryPrivacy: userData.delivery_privacy || userData.deliveryPrivacy || 2
      }
      userStore.updateUserInfo(profileData)
    }
  } catch (error) {
    console.warn('获取用户信息失败:', error)
  }

  await refreshNotifications()
})

const getFullAvatarUrl = (url: string | null | undefined) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('data:')) return url
  return `http://localhost:8000${url}`
}

const refreshNotifications = async () => {
  notificationSummary.value = await fetchNotificationSummary()
}

const normalizeNotificationText = (text: string) => {
  if (!text) return ''
  return text
    .replace(/AssessmentSession/g, '面试流程')
    .replace(/EvaluationResult/g, '评估报告')
    .replace(/TraitScores/g, '人格画像')
}

const getNotificationTitle = (item: any) => {
  const title = normalizeNotificationText(item?.title || '')
  if (title) return title

  switch (item?.type) {
    case 'interview_reminder':
      return '面试流程提醒'
    case 'assessment_completed':
      return '评估已完成'
    case 'report_ready':
      return '评估报告已生成'
    case 'job_recommendation':
      return '岗位推荐已更新'
    case 'candidate_delivery':
      return '候选人投递提醒'
    default:
      return '业务提醒'
  }
}

const getNotificationContent = (item: any) => normalizeNotificationText(item?.content || '')

const handleNotificationClick = (item: any) => {
  if (!item?.action_path) return
  router.push(item.action_path)
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index

  switch (index) {
    case 'home':
      router.push('/home')
      break
    case 'profile':
      router.push('/home/profile')
      break
    case 'jobs':
      router.push('/home/jobs')
      break
    case 'interviews':
      router.push('/home/interviews')
      break
    case 'reports':
      router.push('/home/reports')
      break
    case 'psychology':
      router.push('/home/psychology')
      break
    case 'jobs-manage':
      router.push('/home/job-manage')
      break
    case 'candidates':
      router.push('/home/candidates')
      break
    case 'reports-manage':
      router.push('/home/analytics')
      break
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    customClass: 'logout-confirm-box',
    confirmButtonClass: 'logout-confirm-button',
    cancelButtonClass: 'logout-cancel-button'
  })
    .then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    })
    .catch(() => {})
}

const handleUserMenuCommand = (command: string) => {
  switch (command) {
    case 'logout':
      handleLogout()
      break
    case 'profile':
      router.push('/home/profile')
      break
    case 'settings':
      router.push('/home/settings')
      break
    default:
      ElMessage.warning('未知操作')
  }
}

watch(
  () => router.currentRoute.value.fullPath,
  () => {
    refreshNotifications()
  }
)

watch(
  () => assessmentStore.completionTimestamp,
  (value) => {
    if (value > 0) {
      refreshNotifications()
    }
  }
)
</script>

<template>
  <el-container class="main-layout">
    <el-header class="app-header">
      <div class="header-container">
        <div class="header-left">
          <div class="app-logo" @click="handleMenuSelect('home')">
            <svg class="logo-icon" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea" />
                  <stop offset="100%" style="stop-color:#764ba2" />
                </linearGradient>
              </defs>
              <rect width="32" height="32" rx="8" fill="url(#logoGrad)" />
              <path d="M16 8L24 13L23 19L16 23L9 19L8 13Z" fill="none" stroke="white" stroke-width="2" />
              <circle cx="14" cy="15" r="2" fill="white" />
              <circle cx="18" cy="15" r="2" fill="white" />
              <path d="M12 21Q16 24 20 21" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" />
            </svg>
            <div class="logo-copy">
              <span class="logo-text">AI 人岗匹配</span>
              <span class="logo-subtitle">智能评估 · 精准匹配</span>
            </div>
          </div>
        </div>

        <div class="header-center">
          <nav class="main-nav">
            <button :class="['nav-item', { active: activeMenu === 'home' }]" @click="handleMenuSelect('home')">
              <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              <span>首页</span>
            </button>

            <template v-if="!userStore.isHR">
              <button :class="['nav-item', { active: activeMenu === 'jobs' }]" @click="handleMenuSelect('jobs')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd" />
                  <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
                </svg>
                <span>岗位浏览</span>
              </button>

              <button :class="['nav-item', { active: activeMenu === 'interviews' }]" @click="handleMenuSelect('interviews')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                </svg>
                <span>我的面试</span>
              </button>

              <button :class="['nav-item', { active: activeMenu === 'reports' }]" @click="handleMenuSelect('reports')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
                </svg>
                <span>报告中心</span>
              </button>

              <button :class="['nav-item', { active: activeMenu === 'psychology' }]" @click="handleMenuSelect('psychology')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.5 1.5H4.75A2.25 2.25 0 002.5 3.75v12.5A2.25 2.25 0 004.75 18.5h10.5a2.25 2.25 0 002.25-2.25V8" stroke="currentColor" stroke-width="1.5" fill="none" />
                  <path d="M10 10l3-3m0 0l3 3m-3-3v8" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" />
                  <circle cx="12" cy="5" r="1.5" fill="currentColor" />
                </svg>
                <span>心理解读</span>
              </button>
            </template>

            <template v-else>
              <button :class="['nav-item', { active: activeMenu === 'jobs-manage' }]" @click="handleMenuSelect('jobs-manage')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                </svg>
                <span>岗位管理</span>
              </button>

              <button :class="['nav-item', { active: activeMenu === 'candidates' }]" @click="handleMenuSelect('candidates')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                </svg>
                <span>候选人</span>
              </button>

              <button :class="['nav-item', { active: activeMenu === 'reports-manage' }]" @click="handleMenuSelect('reports-manage')">
                <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
                <span>数据分析</span>
              </button>
            </template>
          </nav>
        </div>

        <div class="header-right">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8.5 3a5.5 5.5 0 014.356 8.86l3.642 3.641a1 1 0 01-1.414 1.415l-3.642-3.642A5.5 5.5 0 118.5 3zm0 2a3.5 3.5 0 100 7 3.5 3.5 0 000-7z" clip-rule="evenodd" />
            </svg>
            <span>搜索岗位、报告、百科...</span>
          </div>

          <el-popover placement="bottom-end" :width="360" trigger="click" popper-class="notification-popover">
            <template #reference>
              <button class="notification-trigger" type="button">
                <svg class="notification-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 2a4 4 0 00-4 4v1.13c0 .72-.2 1.42-.58 2.03L4.3 11.1A1.5 1.5 0 005.58 13h8.84a1.5 1.5 0 001.28-1.9l-1.12-1.94A3.88 3.88 0 0114 7.13V6a4 4 0 00-4-4zm0 16a2.5 2.5 0 002.45-2h-4.9A2.5 2.5 0 0010 18z" />
                </svg>
                <span class="notification-label">通知</span>
                <span v-if="notificationSummary.unread_count > 0" class="notification-badge">
                  {{ notificationSummary.unread_count > 9 ? '9+' : notificationSummary.unread_count }}
                </span>
              </button>
            </template>

            <div class="notification-panel">
              <div class="notification-panel-header">
                <div>
                  <h4>通知中心</h4>
                  
                </div>
                <el-button text type="primary" @click="refreshNotifications">刷新</el-button>
              </div>

              <div v-if="notificationSummary.items.length === 0" class="notification-empty">
                当前暂无新的系统提醒
              </div>

              <div v-else class="notification-list">
                <button
                  v-for="item in notificationSummary.items"
                  :key="item.id"
                  type="button"
                  class="notification-item"
                  @click="handleNotificationClick(item)"
                >
                  <div class="notification-item-top">
                    <span class="notification-type">{{ getNotificationTitle(item) }}</span>
                    <span :class="['notification-priority', item.priority]">
                      {{ item.priority === 'high' ? '高优先' : item.priority === 'medium' ? '处理中' : '一般' }}
                    </span>
                  </div>
                  <p>{{ getNotificationContent(item) }}</p>
                  <div class="notification-action">{{ item.action_label || '立即查看' }}</div>
                </button>
              </div>
            </div>
          </el-popover>

          <el-dropdown @command="handleUserMenuCommand" trigger="click" popper-class="user-dropdown-popper">
            <div class="user-profile">
              <div class="user-avatar">
                <img v-if="userStore.profile?.avatar" :src="getFullAvatarUrl(userStore.profile.avatar)" alt="用户头像" class="avatar-img" />
                <svg v-else viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="avatarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#667eea" />
                      <stop offset="100%" style="stop-color:#764ba2" />
                    </linearGradient>
                  </defs>
                  <circle cx="16" cy="16" r="16" fill="url(#avatarGrad)" />
                  <circle cx="16" cy="12" r="5" fill="white" opacity="0.9" />
                  <path d="M6 28c0-5.5 4.5-10 10-10s10 4.5 10 10" fill="white" opacity="0.9" />
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
                  <span class="menu-icon-shell">
                    <svg class="menu-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                    </svg>
                  </span>
                  <span>个人信息</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <span class="menu-icon-shell">
                    <svg class="menu-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                    </svg>
                  </span>
                  <span>账号设置</span>
                </el-dropdown-item>
                <div class="dropdown-divider"></div>
                <el-dropdown-item command="logout" class="logout-menu-item">
                  <span class="menu-icon-shell logout-shell">
                    <svg class="menu-icon logout-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
                    </svg>
                  </span>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <el-main class="app-main">
      <div :class="['content-shell', { 'sidebar-collapsed': isSidebarCollapsed }]">
        <aside :class="['left-rail', { collapsed: isSidebarCollapsed }]">
          <div class="side-menu-card">
            <div class="side-menu-top">
              <span v-if="!isSidebarCollapsed" class="side-menu-title">功能导航</span>
              <button
                type="button"
                class="sidebar-toggle"
                :aria-label="isSidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'"
                @click="toggleSidebar"
                @mouseenter="collapseSidebarOnHover"
              >
                <el-icon>
                  <ArrowLeftBold v-if="!isSidebarCollapsed" />
                  <ArrowRightBold v-else />
                </el-icon>
              </button>
            </div>

            <button
              v-for="item in sideMenus"
              :key="item.key"
              type="button"
              :class="['side-menu-item', { active: activeMenu === item.key, collapsed: isSidebarCollapsed }]"
              :title="isSidebarCollapsed ? item.label : ''"
              @click="handleMenuSelect(item.key)"
            >
              <svg v-if="item.icon === 'home'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              <svg v-else-if="item.icon === 'jobs'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd" />
                <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
              </svg>
              <svg v-else-if="item.icon === 'interviews'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
              </svg>
              <svg v-else-if="item.icon === 'reports'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
              </svg>
              <svg v-else-if="item.icon === 'psychology'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.5 1.5H4.75A2.25 2.25 0 002.5 3.75v12.5A2.25 2.25 0 004.75 18.5h10.5a2.25 2.25 0 002.25-2.25V8" stroke="currentColor" stroke-width="1.5" fill="none" />
                <path d="M10 10l3-3m0 0l3 3m-3-3v8" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="12" cy="5" r="1.5" fill="currentColor" />
              </svg>
              <svg v-else-if="item.icon === 'users'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
              </svg>
              <svg v-else-if="item.icon === 'analytics'" class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
              <svg v-else class="side-menu-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
              </svg>
              <span class="side-menu-label">{{ item.label }}</span>
            </button>
          </div>

          <div :class="['assistant-card', { collapsed: isSidebarCollapsed }]" :title="isSidebarCollapsed ? assistantTitle : ''">
            <div class="assistant-badge">{{ userStore.isHR ? 'AI 招聘助理' : 'AI 职业咨询师' }}</div>
            <h4>{{ userStore.isHR ? '辅助处理候选人与岗位决策' : '为你提供职业发展建议' }}</h4>
            <p>{{ userStore.isHR ? '围绕岗位实例、候选人报告与待处理事项进行辅助分析。' : '结合人格特质、报告结果与岗位方向，帮助你持续理解自己。' }}</p>
            <button class="assistant-btn" type="button" @click="handleMenuSelect(userStore.isHR ? 'reports-manage' : 'psychology')">
              {{ userStore.isHR ? '查看分析' : '立即咨询' }}
            </button>
            <div class="assistant-bot">
              <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#667eea" />
                    <stop offset="100%" stop-color="#8b5cf6" />
                  </linearGradient>
                </defs>
                <rect x="18" y="22" width="44" height="30" rx="14" fill="url(#botGrad)" />
                <rect x="24" y="28" width="32" height="18" rx="9" fill="white" opacity="0.92" />
                <circle cx="34" cy="37" r="3" fill="#667eea" />
                <circle cx="46" cy="37" r="3" fill="#667eea" />
                <path d="M32 45Q40 50 48 45" stroke="#667eea" stroke-width="2.5" fill="none" stroke-linecap="round" />
                <rect x="34" y="12" width="12" height="8" rx="4" fill="#c7d2fe" />
                <path d="M40 20V14" stroke="#667eea" stroke-width="2.5" stroke-linecap="round" />
                <circle cx="20" cy="57" r="5" fill="#dbeafe" />
                <circle cx="60" cy="57" r="5" fill="#ddd6fe" />
              </svg>
            </div>
          </div>
        </aside>

        <section class="main-content">
          <router-view />
        </section>
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
  --shell-radius: 24px;
  --shell-radius-sm: 18px;
  --shell-border: 1px solid rgba(223, 230, 250, 0.95);
  --shell-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
  --shell-shadow-soft: 0 10px 26px rgba(15, 23, 42, 0.06);
  --primary-gradient: linear-gradient(135deg, #5468ff 0%, #7c4dff 100%);
  --panel-bg: rgba(255, 255, 255, 0.84);
  height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(99, 102, 241, 0.18), transparent 24%),
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 20%),
    linear-gradient(180deg, #f5f7ff 0%, #f7faff 42%, #edf3ff 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(18px);
  box-shadow: 0 12px 36px rgba(15, 23, 42, 0.06);
  padding: 0;
  height: 82px;
  border-bottom: 1px solid rgba(227, 234, 250, 0.88);
  position: sticky;
  top: 0;
  z-index: 120;
}

.header-container {
  max-width: 1560px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 22px;
}

.header-left {
  flex-shrink: 0;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  user-select: none;
  padding: 10px 14px 10px 10px;
  border-radius: 22px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.app-logo:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.66);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
}

.logo-icon {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  filter: drop-shadow(0 8px 20px rgba(99, 102, 241, 0.24));
}

.logo-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  font-size: 25px;
  font-weight: 700;
  line-height: 1;
  background: linear-gradient(135deg, #5b5ff8 0%, #8b5cf6 52%, #4f9cf9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.6px;
}

.logo-subtitle {
  font-size: 12px;
  color: #8b93a7;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 0;
}

.main-nav {
  display: flex;
  gap: 10px;
  background: rgba(255, 255, 255, 0.78);
  padding: 8px 10px;
  border-radius: var(--shell-radius);
  border: var(--shell-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85), 0 8px 28px rgba(99, 102, 241, 0.08);
  overflow-x: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 12px 18px;
  border: none;
  background: transparent;
  color: #667085;
  font-size: 14px;
  font-weight: 600;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.22s ease;
  white-space: nowrap;
  outline: none;
}

.nav-item:hover {
  color: #334155;
  background: rgba(255, 255, 255, 0.82);
  transform: translateY(-1px);
}

.nav-item.active {
  color: #ffffff;
  background: var(--primary-gradient);
  box-shadow: 0 10px 28px rgba(92, 101, 255, 0.3);
}

.nav-icon,
.side-menu-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.header-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  min-width: 260px;
  height: 46px;
  padding: 0 16px;
  border-radius: var(--shell-radius-sm);
  border: var(--shell-border);
  background: rgba(255, 255, 255, 0.82);
  color: #98a2b3;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.06);
}

.search-box span {
  font-size: 13px;
  white-space: nowrap;
}

.search-icon {
  width: 18px;
  height: 18px;
}

.notification-trigger {
  position: relative;
  min-width: 46px;
  width: 46px;
  height: 46px;
  border: var(--shell-border);
  border-radius: var(--shell-radius-sm);
  background: rgba(255, 255, 255, 0.82);
  color: #4b5563;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08);
}

.notification-trigger:hover {
  background: #ffffff;
  border-color: #c7d2fe;
  color: #667eea;
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.16);
}

.notification-icon {
  width: 20px;
  height: 20px;
}

.notification-label {
  display: none;
}

.notification-badge {
  position: absolute;
  top: -6px;
  right: -3px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ef4444, #f97316);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px 8px 8px;
  background: rgba(255, 255, 255, 0.86);
  border-radius: 22px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: var(--shell-border);
  box-shadow: var(--shell-shadow-soft);
}

.user-profile:hover {
  background: #ffffff;
  border-color: #dbe2ff;
  box-shadow: 0 14px 30px rgba(99, 102, 241, 0.14);
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 8px 18px rgba(102, 126, 234, 0.2);
}

.user-avatar svg,
.user-avatar .avatar-img {
  width: 100%;
  height: 100%;
  display: block;
}

.user-avatar .avatar-img {
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 92px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
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

:global(.user-dropdown-popper.el-popper) {
  border: 1px solid rgba(226, 232, 240, 0.96);
  border-radius: 18px;
  box-shadow: 0 22px 48px rgba(15, 23, 42, 0.15);
  overflow: hidden;
}

:global(.user-dropdown-popper.el-popper .el-popper__arrow::before) {
  border-color: rgba(226, 232, 240, 0.96);
  background: #ffffff;
}

:deep(.user-dropdown-menu) {
  min-width: 178px;
  padding: 8px;
  border: none;
  background:
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

:deep(.notification-popover) {
  border-radius: 18px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 44px rgba(15, 23, 42, 0.14);
  padding: 0;
}

.notification-panel {
  padding: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
}

.notification-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.notification-panel-header h4 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #111827;
}

.notification-panel-header p {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.5;
}

.notification-empty {
  padding: 24px 12px;
  border-radius: 14px;
  background: #f9fafb;
  text-align: center;
  color: #6b7280;
  font-size: 13px;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-item {
  width: 100%;
  border: 1px solid #e8ecf8;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  padding: 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.notification-item:hover {
  border-color: #c7d2fe;
  background: #f8faff;
  box-shadow: 0 10px 24px rgba(99, 102, 241, 0.08);
}

.notification-item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}

.notification-type {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.notification-priority {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

.notification-priority.high {
  color: #dc2626;
  background: #fee2e2;
}

.notification-priority.medium {
  color: #d97706;
  background: #fef3c7;
}

.notification-priority.low {
  color: #2563eb;
  background: #dbeafe;
}

.notification-item p {
  margin: 0;
  color: #6b7280;
  font-size: 12px;
  line-height: 1.6;
}

.notification-action {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #4b5563;
  transition: all 0.22s ease;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item:hover) {
  background: linear-gradient(135deg, rgba(91, 103, 255, 0.1), rgba(124, 77, 255, 0.08));
  color: #4f46e5;
  transform: translateX(2px);
}

:deep(.user-dropdown-menu .el-dropdown-menu__item.logout-menu-item) {
  color: #b91c1c;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item.logout-menu-item:hover) {
  background: #fff1f2;
  color: #dc2626;
}

.menu-icon-shell {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #eef2ff;
  color: #667eea;
  flex-shrink: 0;
}

.logout-shell {
  background: #fee2e2;
  color: #ef4444;
}

.menu-icon {
  width: 17px;
  height: 17px;
  color: currentColor;
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
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
  margin: 8px 4px;
}

:global(.logout-confirm-box) {
  width: 430px;
  padding: 22px 24px 20px;
  border: 1px solid rgba(226, 232, 240, 0.96);
  border-radius: 18px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
}

:global(.logout-confirm-box .el-message-box__header) {
  padding: 0 0 12px;
}

:global(.logout-confirm-box .el-message-box__title) {
  color: #111827;
  font-size: 20px;
  font-weight: 700;
}

:global(.logout-confirm-box .el-message-box__headerbtn) {
  top: 18px;
  right: 18px;
  width: 30px;
  height: 30px;
  border-radius: 10px;
}

:global(.logout-confirm-box .el-message-box__headerbtn:hover) {
  background: #f3f4f6;
}

:global(.logout-confirm-box .el-message-box__content) {
  padding: 8px 0 22px;
  color: #4b5563;
}

:global(.logout-confirm-box .el-message-box__status) {
  color: #f59e0b;
  font-size: 24px !important;
}

:global(.logout-confirm-box .el-message-box__message) {
  padding-left: 40px;
}

:global(.logout-confirm-box .el-message-box__message p) {
  font-size: 16px;
  line-height: 1.7;
}

:global(.logout-confirm-box .el-message-box__btns) {
  padding: 0;
  gap: 12px;
}

:global(.logout-confirm-box .el-button) {
  min-width: 88px;
  height: 40px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
}

:global(.logout-confirm-box .logout-cancel-button) {
  border-color: #d9e0ec;
  color: #667085;
  background: #ffffff;
}

:global(.logout-confirm-box .logout-cancel-button:hover) {
  border-color: #c7d2fe;
  color: #4f46e5;
  background: #f8faff;
}

:global(.logout-confirm-box .logout-confirm-button) {
  border: none;
  background: linear-gradient(135deg, #5468ff 0%, #7c4dff 100%);
  box-shadow: 0 10px 22px rgba(84, 104, 255, 0.24);
}

:global(.logout-confirm-box .logout-confirm-button:hover) {
  background: linear-gradient(135deg, #4b5ff5 0%, #7144f0 100%);
}

.app-main {
  background: transparent;
  padding: 24px 24px 28px;
  overflow-y: auto;
}

.content-shell {
  --sidebar-width: 220px;
  max-width: 1560px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  gap: 28px;
  align-items: start;
  transition: grid-template-columns 0.26s ease;
}

.content-shell.sidebar-collapsed {
  --sidebar-width: 60px;
}

.left-rail {
  position: sticky;
  top: 102px;
  width: 220px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: width 0.26s ease;
}

.left-rail.collapsed {
  width: 60px;
}

.side-menu-card,
.assistant-card {
  border-radius: var(--shell-radius);
  border: var(--shell-border);
  background: var(--panel-bg);
  box-shadow: var(--shell-shadow);
}

.side-menu-card {
  padding: 18px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: padding 0.26s ease, border-radius 0.26s ease;
}

.left-rail.collapsed .side-menu-card {
  padding: 14px 8px;
}

.side-menu-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 36px;
  margin-bottom: 6px;
}

.side-menu-title {
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.sidebar-toggle {
  width: 34px;
  height: 34px;
  border: 1px solid rgba(211, 220, 255, 0.95);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.92);
  color: #5b67ff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.24s ease;
}

.sidebar-toggle:hover {
  background: #ffffff;
  border-color: #c9d5ff;
  box-shadow: 0 10px 24px rgba(91, 103, 255, 0.14);
}

.left-rail.collapsed .sidebar-toggle {
  margin: 0 auto;
}

.side-menu-item {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: none;
  border-radius: 14px;
  background: transparent;
  color: #667085;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.26s ease;
  text-align: left;
  overflow: hidden;
}

.side-menu-item:hover {
  background: rgba(244, 247, 255, 0.95);
  color: #334155;
}

.side-menu-item.active {
  background: linear-gradient(135deg, rgba(84, 104, 255, 0.12), rgba(124, 77, 255, 0.14));
  color: #5468ff;
  box-shadow: inset 0 0 0 1px rgba(124, 77, 255, 0.06);
}

.side-menu-label {
  white-space: nowrap;
  opacity: 1;
  transform: translateX(0);
  transition: opacity 0.18s ease, transform 0.22s ease, width 0.22s ease;
}

.left-rail.collapsed .side-menu-item {
  justify-content: center;
  padding: 0;
  gap: 0;
}

.left-rail.collapsed .side-menu-label {
  width: 0;
  opacity: 0;
  transform: translateX(-8px);
}

.assistant-card {
  padding: 22px 18px 18px;
  position: relative;
  overflow: hidden;
  min-height: 300px;
  transition:
    min-height 0.26s ease,
    padding 0.26s ease,
    border-radius 0.26s ease;
}

.assistant-card::before {
  content: '';
  position: absolute;
  inset: auto -30px -40px auto;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.16), rgba(99, 102, 241, 0));
}

.assistant-badge {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.12);
  color: #5b67ff;
  font-size: 12px;
  font-weight: 700;
  transition: opacity 0.2s ease, transform 0.22s ease;
}

.assistant-card h4 {
  position: relative;
  z-index: 1;
  margin: 16px 0 12px;
  font-size: 19px;
  line-height: 1.45;
  color: #172133;
  transition: opacity 0.2s ease, transform 0.22s ease;
}

.assistant-card p {
  position: relative;
  z-index: 1;
  margin: 0;
  color: #6f7c93;
  font-size: 13px;
  line-height: 1.85;
  transition: opacity 0.2s ease, transform 0.22s ease;
}

.assistant-btn {
  position: relative;
  z-index: 1;
  margin-top: 24px;
  width: 100%;
  height: 46px;
  border: none;
  border-radius: 14px;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(92, 101, 255, 0.2);
  transition: opacity 0.2s ease, transform 0.22s ease;
}

.assistant-bot {
  position: absolute;
  right: 10px;
  bottom: 8px;
  width: 76px;
  height: 76px;
  z-index: 1;
  transition: all 0.26s ease;
}

.assistant-bot svg {
  width: 100%;
  height: 100%;
}

.left-rail.collapsed .assistant-card {
  min-height: 84px;
  padding: 10px 8px;
}

.left-rail.collapsed .assistant-card > :not(.assistant-bot) {
  display: none;
}

.left-rail.collapsed .assistant-bot {
  position: relative;
  right: auto;
  bottom: auto;
  width: 44px;
  height: 44px;
  margin: 0 auto;
}

.main-content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

@media (max-width: 1360px) {
  .search-box {
    display: none;
  }

  .content-shell {
    grid-template-columns: 208px minmax(0, 1fr);
  }
}

@media (max-width: 1100px) {
  .header-container {
    gap: 16px;
    padding: 0 16px;
  }

  .logo-subtitle,
  .user-info {
    display: none;
  }

  .user-profile {
    padding: 8px;
  }

  .content-shell {
    grid-template-columns: 1fr;
  }

  .left-rail {
    position: static;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 280px;
    align-items: stretch;
  }
}

@media (max-width: 768px) {
  .app-header {
    height: 72px;
  }

  .header-center {
    display: none;
  }

  .app-main {
    padding: 14px 10px 16px;
  }

  .left-rail {
    grid-template-columns: 1fr;
  }

  .side-menu-card {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }

  .side-menu-item {
    justify-content: center;
  }
}

@media (max-width: 520px) {
  .logo-text {
    display: none;
  }

  .notification-trigger {
    width: 42px;
    height: 42px;
    border-radius: 16px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
  }

  .dropdown-arrow {
    display: none;
  }

  .side-menu-card {
    grid-template-columns: 1fr;
  }
}
</style>
