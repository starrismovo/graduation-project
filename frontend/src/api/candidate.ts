import request from '@/utils/request'

export interface BasicInfo {
  name: string
  age: number
  education: string
  major: string
  desired_job: string
  experience_years: number
  skills: string[]
}

// 保存基本信息
export const saveBasicInfo = (candidateId: string, data: BasicInfo) => {
  return request.post(`/api/candidates/${candidateId}/basic-info`, data)
}

// 获取候选人基本信息
export const getBasicInfo = (candidateId: string) => {
  return request.get(`/api/candidates/${candidateId}/basic-info`)
}