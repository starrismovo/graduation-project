import axios from 'axios'


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
    if (error.response) {
      console.error('响应错误:', error.response.status, error.response.data)
    } else if (error.request) {
      console.error('无响应:', error.message)
      // 检查后端是否在运行
      console.warn('💡 提示：后端服务可能未启动。请运行: python main.py')
    } else {
      console.error('请求错误:', error.message)
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

export default request