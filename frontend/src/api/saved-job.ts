/**
 * 心动岗位 API 函数
 * 与后端 /api/saved-jobs 端点交互
 */

import request from '@/utils/request'

export interface SavedJobItem {
  id: number
  candidate_id: number
  job_id: number
  job_name: string
  company: string
  salary?: string
  city?: string
  saved_at: string
}

export interface SavedJobListResponse {
  total: number
  items: SavedJobItem[]
}

/**
 * 添加心动岗位
 */
export async function addSavedJob(candidateId: number, jobId: number) {
  return request.post(`/api/saved-jobs/${candidateId}/add/${jobId}`)
}

/**
 * 移除心动岗位
 */
export async function removeSavedJob(candidateId: number, jobId: number) {
  return request.delete(`/api/saved-jobs/${candidateId}/remove/${jobId}`)
}

/**
 * 获取心动岗位列表
 */
export async function getSavedJobs(
  candidateId: number,
  sortBy: 'latest' | 'salary_high' | 'salary_low' = 'latest'
): Promise<SavedJobListResponse> {
  const res = await request.get(`/api/saved-jobs/${candidateId}`, {
    params: { sort_by: sortBy }
  })
  return res.data || res
}

/**
 * 检查岗位是否已收藏
 */
export async function checkSavedJob(candidateId: number, jobId: number) {
  const res = await request.get(`/api/saved-jobs/${candidateId}/check/${jobId}`)
  return res.data?.is_saved ?? false
}

/**
 * 获取收藏岗位统计
 */
export async function getSavedJobsStats(candidateId: number) {
  const res = await request.get(`/api/saved-jobs/${candidateId}/stats`)
  return res.data || res
}
