import request from '@/utils/request'

export interface Invitation {
  id: number
  hr_id: number
  hr_name: string | null
  candidate_id: number
  candidate_name: string | null
  job_id: number
  job_name: string
  company: string
  salary: string | null
  city: string | null
  message: string | null
  status: 'pending' | 'accepted' | 'declined' | 'expired'
  created_at: string
  responded_at: string | null
}

export interface InvitationListResponse {
  total: number
  items: Invitation[]
}

/** 候选人 — 获取收到的邀请列表 */
export async function getCandidateInvitations(
  candidateId: number | string,
  status?: string,
): Promise<InvitationListResponse> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const res = await request.get(`/api/invitations/candidate/${candidateId}/list`, { params })
  return res.data
}

/** 候选人 — 待处理邀请数量 */
export async function getPendingInvitationCount(
  candidateId: number | string,
): Promise<number> {
  const res = await request.get(`/api/invitations/candidate/${candidateId}/pending-count`)
  return res.data?.count ?? 0
}

/** 候选人 — 接受或拒绝邀请 */
export async function respondInvitation(
  candidateId: number | string,
  invitationId: number,
  action: 'accepted' | 'declined',
): Promise<Invitation> {
  const res = await request.put(
    `/api/invitations/candidate/${candidateId}/respond/${invitationId}`,
    null,
    { params: { action } },
  )
  return res.data
}

/** HR — 发送邀请 */
export async function sendInvitation(
  hrId: number | string,
  candidateId: number,
  jobId: number,
  message?: string,
): Promise<Invitation> {
  const res = await request.post(`/api/invitations/hr/${hrId}/send`, {
    candidate_id: candidateId,
    job_id: jobId,
    message,
  })
  return res.data
}

/** HR — 获取已发出邀请列表 */
export async function getHRInvitations(
  hrId: number | string,
  status?: string,
): Promise<InvitationListResponse> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const res = await request.get(`/api/invitations/hr/${hrId}/list`, { params })
  return res.data
}
