/**
 * 评估流程 API
 * 包括简历检查、进度检查、自动保存等
 */

const BASE = '/assessment/immersive'

export interface AgentExecutePayload {
  operation: 'next_question' | 'analyze_response' | 'analyze_and_next'
  candidate_id: string | number
  assessment_id?: number
  candidate_name?: string
  role_id?: string
  conversation_depth?: number
  history?: Array<Record<string, any>>
  candidate_response?: string
  target_position?: string
  job_info?: Record<string, any>
  resume_info?: Record<string, any>
}

export async function executeAgent(payload: AgentExecutePayload) {
  const res = await fetch(`${BASE}/agent/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return res.json()
}

export async function getNextQuestion(payload: Omit<AgentExecutePayload, 'operation' | 'candidate_response'>) {
  return executeAgent({
    operation: 'next_question',
    ...payload
  })
}

export async function analyzeInterviewResponse(payload: Omit<AgentExecutePayload, 'operation'> & { candidate_response: string }) {
  return executeAgent({
    operation: 'analyze_response',
    ...payload
  })
}

export async function analyzeAndGetNextQuestion(payload: Omit<AgentExecutePayload, 'operation'> & { candidate_response: string }) {
  return executeAgent({
    operation: 'analyze_and_next',
    ...payload
  })
}

/** 检查候选人是否已有简历/个人信息 */
export async function checkResume(candidateId: string | number) {
  const res = await fetch(`${BASE}/check-resume/${candidateId}`)
  return res.json()
}

/** 检查候选人是否有进行中的评估 */
export async function checkProgress(candidateId: string | number) {
  const res = await fetch(`${BASE}/check-progress/${candidateId}`)
  return res.json()
}

/** 保存/更新评估进度 */
export async function updateProgress(data: {
  candidate_id: string | number
  assessment_id?: number
  job_id?: number
  job_title?: string
  status: 'pending' | 'completed'
  total_rounds?: number
  duration_minutes?: number
  conversation_depth?: number
  conversation_summary?: string
  match_score?: number
}) {
  const res = await fetch(`${BASE}/update-progress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return res.json()
}

/** 保存会话数据 */
export async function saveSession(data: {
  candidate_id: string
  assessment_id?: number
  job_id?: number
  job_title?: string
  messages: any[]
  scores: Record<string, number>
  patterns?: any[]
  duration_seconds?: number
  conversation_depth?: number
  total_rounds?: number
  highlights?: string[]
}) {
  const res = await fetch(`${BASE}/save-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return res.json()
}

/** 保存评估结果并生成报告 */
export async function saveAssessmentResult(data: {
  candidate_id: string
  job_id: number
  assessment_mode?: string
  all_scores?: Record<string, number>
  personality_scores?: Record<string, number>
  situational_scores?: Record<string, number>
  candidate_info?: Record<string, any>
}) {
  const res = await fetch('/assessment/save-result', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  return res.json()
}

/** 获取评估报告 */
export async function fetchReport(recordId: number | string) {
  const res = await fetch(`/assessment/report/${recordId}`)
  return res.json()
}

// ==================== localStorage 进度管理 ====================

const PROGRESS_KEY_PREFIX = 'assessment_progress_'

export interface LocalProgress {
  currentStep: number
  messages: any[]
  scores: Record<string, number>
  patterns: any[]
  respondedCount: number
  candidateInfo: any
  parsedResumeData: any
  selectedJobId: number | null
  assessmentId?: number
  jobTitle?: string
  interviewState?: any
  latestDecision?: any
  startTime: number
  elapsedTime: number
  timestamp: number
}

/** 保存进度到 localStorage */
export function saveLocalProgress(candidateId: string | number, data: LocalProgress) {
  try {
    localStorage.setItem(
      `${PROGRESS_KEY_PREFIX}${candidateId}`,
      JSON.stringify(data)
    )
  } catch (e) {
    console.warn('保存本地进度失败:', e)
  }
}

/** 从 localStorage 加载进度 */
export function loadLocalProgress(candidateId: string | number): LocalProgress | null {
  try {
    const raw = localStorage.getItem(`${PROGRESS_KEY_PREFIX}${candidateId}`)
    if (!raw) return null
    
    const data = JSON.parse(raw) as LocalProgress
    
    // 超过24小时的进度视为过期
    const ONE_DAY = 24 * 60 * 60 * 1000
    if (Date.now() - data.timestamp > ONE_DAY) {
      clearLocalProgress(candidateId)
      return null
    }
    
    return data
  } catch (e) {
    console.warn('加载本地进度失败:', e)
    return null
  }
}

/** 清除 localStorage 中的进度 */
export function clearLocalProgress(candidateId: string | number) {
  localStorage.removeItem(`${PROGRESS_KEY_PREFIX}${candidateId}`)
}
