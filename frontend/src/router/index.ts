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
      meta: { requiresAuth: true }  // 统一主页
      ,
    }
    ,
    // 虚拟形象创建页
    {
      path: '/avatar-creator',
      name: 'AvatarCreator',
      component: () => import('../views/AvatarCreatorView.vue'),
      meta: { requiresAuth: true }
    },
    // 自我发现测试页
    // {
    //   path: '/self-discovery',
    //   name: 'SelfDiscovery',
    //   component: () => import('../views/SelfDiscoveryView.vue'),
    //   meta: { requiresAuth: true }
    // },
    // 星际航程（故事评估）- 新的核心页面
    {
      path: '/journey/:id',
      name: 'Journey',
      component: () => import('../views/JourneyView.vue'),
      meta: { requiresAuth: true }
    },
    // 航行日志（报告页）
    {
      path: '/journey-report/:jobId',
      name: 'JourneyReport',
      component: () => import('../views/JourneyReportView.vue'),
      meta: { requiresAuth: true }
    },
    // 我的星图（个人中心）
    // {
    //   path: '/constellation-map',
    //   name: 'ConstellationMap',
    //   component: () => import('../views/ConstellationMapView.vue'),
    //   meta: { requiresAuth: true }
    // },
    {
      path: '/assessment/:id',
      component: AssessmentView,
      meta: { requiresAuth: true }
    }
    ,
    {
      path: '/job-manage',
      component: JobManageView,
      meta: { 
        requiresHR: true,
      }
    }
    ,
    {
  path: '/views/position/:id/edit',
  component: () => import('@/views/position/JobEditView.vue')
}

  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router