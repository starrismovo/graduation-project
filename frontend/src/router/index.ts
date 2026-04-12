import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import IndexView from '@/views/IndexView.vue'
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
          path: 'jobs',
          name: 'JobList',
          component: () => import('../views/JobListView.vue'),
          meta: { title: '岗位浏览' }
        },
        {
          path: 'jobs/:jobId',
          name: 'JobDetail',
          component: () => import('../views/JobDetailView.vue'),
          meta: { title: '岗位详情' }
        },
        {
          path: 'immersive',
          redirect: '/home/interviews'
        },
        {
          path: 'interviews',
          name: 'InterviewHub',
          component: () => import('../views/assessment/MyInterviewsPage.vue'),
          meta: { 
            title: '我的面试'
          }
        },
        {
          path: 'interviews/room',
          name: 'ImmersiveAssessment',
          component: () => import('../views/assessment/ImmersiveRoleDialogue.vue'),
          meta: {
            mode: 'immersive',
            title: 'AI面试间'
          }
        },
        {
          path: 'interviews/immersive',
          redirect: '/home/interviews/room'
        },
        {
          path: 'interviews/list',
          name: 'MyInterviews',
          redirect: '/home/interviews'
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
          path: 'reports',
          name: 'ReportList',
          component: () => import('../views/assessment/ReportListPage.vue')
        },
        {
          path: 'report/:recordId',
          name: 'AssessmentReport',
          component: () => import('../views/assessment/ReportPage.vue')
        },
        {
          path: 'psychology',
          name: 'PsychologyDetail',
          component: () => import('../views/assessment/PsychologyDetailPage.vue'),
          meta: { title: '心理解读' }
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