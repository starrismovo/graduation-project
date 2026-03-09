import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import IndexView from '@/views/IndexView.vue'
import AssessmentView from '@/views/ProfileView.vue'
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
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('../views/HomePage.vue')
        },
        {
          path: 'immersive',
          name: 'ImmersiveAssessment',
          component: () => import('../views/assessment/ImmersiveRoleDialogue.vue'),
          meta: { 
            mode: 'immersive',
            title: '沉浸式对话评估'
          }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('../views/ProfileView.vue')
        },
        {
          path: 'job-manage',
          name: 'JobManage',
          component: JobManageView,
          meta: { requiresHR: true }
        },
        {
          path: 'report/:recordId',
          name: 'AssessmentReport',
          component: () => import('../views/assessment/ReportPage.vue')
        }
      ]
    },
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
  
  // 检查子路由的HR权限
  if (to.matched.some(route => route.meta?.requiresHR) && !userStore.isHR) {
    next('/home')
    return
  }
  
  next()
})

export default router