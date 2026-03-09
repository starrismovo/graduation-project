import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',  // 后端地址
  timeout: 30000,  // 增加到30秒
  withCredentials: false  // 禁用跨域 cookie
})

// 请求拦截器：自动添加 token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('user_token') || ''
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一处理错误和重试
request.interceptors.response.use(
  response => response,
  error => {
    const userStore = useUserStore()
    
    if (error.response) {
      const status = error.response.status
      
      // 401 Unauthorized - token过期或无效
      if (status === 401) {
        console.warn('Token已过期或无效，自动登出')
        userStore.logout()
        ElMessage.warning('登录已过期，请重新登录')
        router.push('/login')
      }
      
      // 403 Forbidden - 权限不足
      if (status === 403) {
        ElMessage.error('没有访问权限')
      }
      
      // 404 Not Found
      if (status === 404) {
        console.error('请求的资源不存在:', error.response.data)
      }
      
      // 500 Server Error
      if (status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
      }
      
      console.error('API错误:', status, error.response.data)
    } else if (error.request) {
      console.error('无响应:', error.message)
      ElMessage.error('网络连接失败，请检查后端服务')
      console.warn('💡 提示：后端服务可能未启动。请运行: uvicorn main:app --reload')
    } else {
      console.error('请求错误:', error.message)
      ElMessage.error(error.message)
    }
    return Promise.reject(error)
  }
)

// ============ API 接口函数 ============

// 获取主页数据（推荐方式）
export const getHomePageData = (params?: {
  category?: string
  city?: string
  salary_range?: string
}) => {
  return request.get('/jobs/home/data', { params })
}

// 获取推荐岗位卡片
export const getRecommendedJobs = (params?: {
  category?: string
  city?: string
  salary_range?: string
}) => {
  return request.get('/jobs/recommended/cards', { params })
}

// 获取热门岗位表格数据
export const getHotJobsTable = (params?: {
  category?: string
  city?: string
  salary_range?: string
  limit?: number
}) => {
  return request.get('/jobs/hot/table', { params })
}


// 获取面试统计信息
export const getInterviewStats = () => {
  return request.get('/jobs/stats/candidate')
}

// 开始面试
export const startInterview = (jobId: number) => {
  return request.post('/interviews/', { job_id: jobId })
}

// 获取面试详情
export const getInterviewDetail = (interviewId: number) => {
  return request.get(`/interviews/${interviewId}`)
}

// 获取候选人的所有面试记录
export const getCandidateInterviews = (candidateId: number, status?: string) => {
  return request.get(`/interviews/candidate/${candidateId}`, { params: { status } })
}

// 更新面试记录（提交结果）
export const updateInterview = (
  interviewId: number,
  data: {
    status?: string
    personality_traits?: Record<string, number>
    match_score?: number
    notes?: string
  }
) => {
  return request.put(`/interviews/${interviewId}`, data)
}

// 删除面试记录
export const deleteInterview = (interviewId: number) => {
  return request.delete(`/interviews/${interviewId}`)
}

// 获取岗位列表（支持筛选）
export const getJobs = (params?: {
  category?: string
  city?: string
  salary_min?: number
  salary_max?: number
}) => {
  return request.get('/jobs/', { params })
}

// 获取单个岗位详情
export const getJobDetail = (jobId: number) => {
  return request.get(`/jobs/${jobId}`)
}

// ============ 候选人首页专用 API ============

/**
 * 获取候选人的心理画像
 * @param candidateId 候选人ID
 * @returns 五大人格评分数据 [{name: '外向性', score: 8}, ...]
 */
export const fetchPortrait = async (candidateId: string | number) => {
  try {
    const response = await request.get(`/assessment/portrait/${candidateId}`)
    return response.data?.data || response.data || []
  } catch (error) {
    console.warn('获取心理画像失败，返回空数组:', error)
    return []
  }
}

/**
 * 获取候选人的历史评估记录
 * @param candidateId 候选人ID
 * @returns 评估记录列表 [{id, job_id, job_title, match_score, created_at}, ...]
 */
export const fetchHistory = async (candidateId: string | number) => {
  try {
    const response = await request.get(`/assessment/history/${candidateId}`)
    return response.data?.data || response.data || []
  } catch (error) {
    console.warn('获取评估历史失败，返回空数组:', error)
    return []
  }
}

/**
 * 获取推荐岗位
 * @param candidateId 候选人ID
 * @returns 推荐岗位列表 [{id, title, match_score, description}, ...]
 */
export const fetchJobs = async (candidateId: string | number) => {
  try {
    const response = await request.get(`/assessment/recommended-jobs/${candidateId}`)
    return response.data?.data || response.data || []
  } catch (error) {
    console.warn('获取推荐岗位失败，返回空数组:', error)
    return []
  }
}

/**
 * 获取最新的评估报告详情
 * @param recordId 评估记录ID
 */
export const fetchReportDetail = async (recordId: string | number) => {
  try {
    const response = await request.get(`/assessment/report/${recordId}`)
    return response.data?.data || response.data || {}
  } catch (error) {
    console.error('获取报告详情失败:', error)
    throw error
  }
}

// 获取故事模板
export function getStoryTemplate(jobId: string) {
  return request({
    url: `/api/story/${jobId}`,
    method: 'get'
  })
}

// 保存探索进度
export function saveJourneyProgress(data: any) {
  return request({
    url: '/api/journey/progress',
    method: 'post',
    data
  })
}

// 生成报告
export function generateJourneyReport(journeyId: string) {
  return request({
    url: `/api/journey/${journeyId}/report`,
    method: 'get'
  })
}

export default request