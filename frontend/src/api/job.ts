import request from '@/utils/request'

// ==================== 岗位需求 API ====================

/**
 * 从岗位描述(JD)创建岗位需求
 */
export const createJobRequirementsFromJD = (data: {
  job_id: number
  jd_text: string
  role_category: string
}) => {
  return request.post('/jobs/requirements/create-from-jd', data)
}

/**
 * 更新岗位需求
 */
export const updateJobRequirements = (data: {
  job_id: number
  skills: any[]
  requirement_tags: any[]
  personality_framework: any
}) => {
  return request.post('/jobs/requirements/update', data)
}

/**
 * 获取岗位需求详情
 */
export const getJobRequirements = (jobId: number) => {
  return request.get(`/jobs/requirements/${jobId}`)
}

// ==================== 候选人应聘 API ====================

/**
 * 候选人应聘岗位
 */
export const applyForJob = (data: {
  candidate_id: number
  job_id: number
  notes?: string
}) => {
  return request.post('/jobs/apply', data)
}

/**
 * 获取候选人应聘记录
 */
export const getCandidateApplications = (candidateId: number) => {
  return request.get(`/jobs/applications/${candidateId}`)
}

/**
 * 获取岗位和候选人的匹配度
 */
export const getJobMatch = (candidateId: number, jobId: number) => {
  return request.get(`/jobs/match/${candidateId}/${jobId}`)
}

// ==================== 岗位列表 API ====================

/**
 * 获取所有岗位
 */
export const getAllJobs = () => {
  return request.get('/jobs')
}

/**
 * 获取单个岗位详情
 */
export const getJobDetail = (jobId: number) => {
  return request.get(`/jobs/${jobId}`)
}

/**
 * 搜索岗位
 */
export const searchJobs = (query: string) => {
  return request.get('/jobs/search', { params: { q: query } })
}
