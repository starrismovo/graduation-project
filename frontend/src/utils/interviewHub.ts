import { ref, computed } from 'vue'
import { 
  addSavedJob as apiAddSavedJob, 
  removeSavedJob as apiRemoveSavedJob,
  getSavedJobs as apiGetSavedJobs,
  checkSavedJob as apiCheckSavedJob,
  type SavedJobItem
} from '@/api/saved-job'

/**
 * 获取当前候选人 ID（从用户信息或 token 中获取）
 * TODO: 从 useUserStore 或认证上下文获取
 */
function getCurrentCandidateId(): number {
  const candidates = [
    localStorage.getItem('candidateId'),
    localStorage.getItem('user_id'),
  ]

  try {
    const profile = JSON.parse(localStorage.getItem('user_profile') || 'null')
    if (profile?.id) {
      candidates.push(String(profile.id))
    }
  } catch {
    // ignore invalid cached profile
  }

  for (const raw of candidates) {
    const id = Number(raw)
    if (Number.isInteger(id) && id > 0) {
      return id
    }
  }

  return 0
}

/**
 * 内存缓存，避免频繁的 API 调用
 */
const savedJobsCache = ref<SavedJobItem[]>([])
const cacheLoading = ref(false)
const lastFetch = ref<number>(0)
const CACHE_TTL = 5 * 60 * 1000 // 5 分钟缓存

export interface InterviewHubJob {
  jobId: number
  title: string
  company: string
  city?: string
  salary?: string
  category?: string
  addedAt: string
}

/**
 * 读取所有心动岗位
 */
export async function readHubJobs(): Promise<InterviewHubJob[]> {
  const candidateId = getCurrentCandidateId()
  if (!candidateId) {
    console.warn('未获取到候选人 ID，使用本地存储回退')
    return readFromLocalStorage()
  }

  try {
    // 检查缓存是否有效
    if (savedJobsCache.value.length > 0 && Date.now() - lastFetch.value < CACHE_TTL) {
      return normalizeApiResponse(savedJobsCache.value)
    }

    cacheLoading.value = true
    const response = await apiGetSavedJobs(candidateId, 'latest')
    const items = response.items || []
    
    savedJobsCache.value = items
    lastFetch.value = Date.now()
    
    return mergeHubJobs(normalizeApiResponse(items), readFromLocalStorage())
  } catch (error) {
    console.error('获取心动岗位失败，使用本地存储:', error)
    return readFromLocalStorage()
  } finally {
    cacheLoading.value = false
  }
}

/**
 * 添加心动岗位
 */
export async function addHubJob(job: any): Promise<boolean> {
  const candidateId = getCurrentCandidateId()
  const jobId = Number(job.jobId ?? job.id)
  
  if (!jobId) {
    console.warn('无效的岗位 ID')
    return false
  }

  // 如果没有候选人 ID，使用本地存储
  if (!candidateId) {
    return addToLocalStorage(job)
  }

  try {
    await apiAddSavedJob(candidateId, jobId)
    addToLocalStorage(job)
    
    // 清除缓存以便下次重新获取
    invalidateCache()
    return true
  } catch (error) {
    console.error('添加心动岗位失败，尝试本地存储:', error)
    return addToLocalStorage(job)
  }
}

/**
 * 移除心动岗位
 */
export async function removeHubJob(jobId: number): Promise<boolean> {
  const candidateId = getCurrentCandidateId()
  
  if (!candidateId) {
    return removeFromLocalStorage(jobId)
  }

  try {
    await apiRemoveSavedJob(candidateId, jobId)
    removeFromLocalStorage(jobId)
    
    // 从内存缓存中移除
    savedJobsCache.value = savedJobsCache.value.filter(j => j.job_id !== jobId)
    lastFetch.value = Date.now()
    
    return true
  } catch (error) {
    console.error('移除心动岗位失败，尝试本地存储:', error)
    return removeFromLocalStorage(jobId)
  }
}

/**
 * 检查岗位是否已收藏
 */
export async function hasHubJob(jobId: number): Promise<boolean> {
  const candidateId = getCurrentCandidateId()
  
  // 先检查内存缓存
  const inCache = savedJobsCache.value.some(j => j.job_id === jobId)
  if (inCache && Date.now() - lastFetch.value < CACHE_TTL) {
    return true
  }

  if (!candidateId) {
    return checkLocalStorage(jobId)
  }

  try {
    return await apiCheckSavedJob(candidateId, jobId)
  } catch (error) {
    console.warn('检查心动岗位失败，使用本地存储:', error)
    return checkLocalStorage(jobId)
  }
}

/**
 * 清除缓存，强制下次重新获取
 */
export function invalidateCache(): void {
  savedJobsCache.value = []
  lastFetch.value = 0
}

/**
 * 设置候选人 ID（用于初始化）
 */
export function setCandidateId(id: number): void {
  localStorage.setItem('candidateId', id.toString())
  invalidateCache()
}

/**
 * 清除候选人 ID（登出或无效用户时）
 */
export function clearCandidateId(): void {
  localStorage.removeItem('candidateId')
  invalidateCache()
}

// ============ 本地存储回退机制 ============

const HUB_STORAGE_KEY = 'interview_hub_jobs'

function readFromLocalStorage(): InterviewHubJob[] {
  try {
    const raw = localStorage.getItem(HUB_STORAGE_KEY)
    if (!raw) return []
    
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function addToLocalStorage(job: any): boolean {
  try {
    const normalized = normalizeJob(job)
    if (!normalized) return false
    
    const current = readFromLocalStorage()
    const existingIndex = current.findIndex(j => j.jobId === normalized.jobId)
    
    if (existingIndex >= 0) {
      current[existingIndex] = { ...current[existingIndex], ...normalized, addedAt: current[existingIndex].addedAt }
    } else {
      current.unshift(normalized)
    }
    
    localStorage.setItem(HUB_STORAGE_KEY, JSON.stringify(current))
    invalidateCache()
    return true
  } catch (error) {
    console.error('本地存储失败:', error)
    return false
  }
}

function removeFromLocalStorage(jobId: number): boolean {
  try {
    const current = readFromLocalStorage()
    const filtered = current.filter(j => j.jobId !== jobId)
    localStorage.setItem(HUB_STORAGE_KEY, JSON.stringify(filtered))
    invalidateCache()
    return true
  } catch (error) {
    console.error('本地存储移除失败:', error)
    return false
  }
}

function checkLocalStorage(jobId: number): boolean {
  const jobs = readFromLocalStorage()
  return jobs.some(j => j.jobId === jobId)
}

// ============ 辅助函数 ============

function normalizeJob(job: any): InterviewHubJob | null {
  const jobId = Number(job.jobId ?? job.id)
  if (!jobId) return null
  
  const salary = job.salary || (
    job.salary_min && job.salary_max 
      ? `${Math.round(job.salary_min)}k-${Math.round(job.salary_max)}k`
      : ''
  )
  
  return {
    jobId,
    title: job.title || job.name || '未命名岗位',
    company: job.company || '未知公司',
    city: job.city,
    salary,
    category: job.category,
    addedAt: new Date().toISOString()
  }
}

function normalizeApiResponse(items: SavedJobItem[]): InterviewHubJob[] {
  return items.map(item => ({
    jobId: item.job_id,
    title: item.job_name,
    company: item.company,
    city: item.city,
    salary: item.salary,
    category: undefined,
    addedAt: item.saved_at
  }))
}

function mergeHubJobs(primary: InterviewHubJob[], fallback: InterviewHubJob[]): InterviewHubJob[] {
  const merged = new Map<number, InterviewHubJob>()
  for (const job of fallback) {
    merged.set(Number(job.jobId), job)
  }
  for (const job of primary) {
    merged.set(Number(job.jobId), job)
  }
  return Array.from(merged.values()).sort(
    (a, b) => new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime(),
  )
}
