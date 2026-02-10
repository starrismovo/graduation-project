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