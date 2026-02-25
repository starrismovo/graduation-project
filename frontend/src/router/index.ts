import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import IndexView from '@/views/IndexView.vue'
import AssessmentView from '@/views/AssessmentView.vue'
import JobManageView from '@/views/position/JobManageView.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      component: LoginView
    },
    { 
      path: '/home', 
      component: IndexView,
      meta: { requiresAuth: true }
    },
    // 候选人首页（重新设计）
    {
      path: '/candidate-home',
      name: 'CandidateHome',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    
    // 沉浸式对话评估（新用户或快速开始）
    {
      path: '/immersive',
      name: 'ImmersiveAssessment',
      component: () => import('../views/assessment/ImmersiveRoleDialogue.vue'),
      meta: { 
        requiresAuth: true,
        mode: 'immersive',
        title: '沉浸式对话评估'
      }
    },
    // 固有的评估流程（带岗位参数）
    {
      path: '/assessment/:id',
      name: 'Assessment',
      component: AssessmentView,
      meta: { requiresAuth: true }
    },
    // 评估集成页面
    {
      path: '/assessment-integration/:id',
      name: 'AssessmentIntegration',
      component: () => import('../views/assessment/AssessmentViewIntegration.vue'),
      meta: { requiresAuth: true }
    },
    // 星际航程（故事评估）- 新的核心页面
    
    // 评估报告页（新增）
    {
      path: '/report/:recordId',
      name: 'AssessmentReport',
      component: () => import('../views/assessment/ReportPage.vue'),
      meta: { requiresAuth: true }
    },
    // 岗位管理（HR）
    {
      path: '/job-manage',
      name: 'JobManage',
      component: JobManageView,
      meta: { 
        requiresAuth: true,
        requiresHR: true
      }
    },
    // 岗位编辑
    {
      path: '/views/position/:id/edit',
      name: 'JobEdit',
      component: () => import('@/views/position/JobEditView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查认证
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
    return
  }
  
  // 检查HR权限
  if (to.meta.requiresHR && !userStore.isHR) {
    // 跳回首页或显示权限不足
    next('/home')
    return
  }
  
  next()
})

export default router