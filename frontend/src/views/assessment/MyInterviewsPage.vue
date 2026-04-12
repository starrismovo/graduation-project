<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { fetchHistory } from '@/utils/request'
import { readHubJobs, removeHubJob, type InterviewHubJob } from '@/utils/interviewHub'
import {
  getCandidateInvitations,
  getPendingInvitationCount,
  respondInvitation,
  type Invitation,
} from '@/api/invitation'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const records = ref<any[]>([])
const hubJobs = ref<InterviewHubJob[]>([])
const invitations = ref<Invitation[]>([])
const pendingInviteCount = ref(0)
const activeTab = ref('invitations')
const highlightJobId = computed(() => Number(route.query.highlightJobId || 0))

/* ---------- computed ---------- */
const pendingRecords = computed(() =>
  records.value.filter((r) => r.assessment_status === 'pending'),
)
const completedRecords = computed(() =>
  records.value.filter((r) => r.assessment_status === 'completed'),
)
const otherRecords = computed(() =>
  records.value.filter((r) => !['pending', 'completed'].includes(r.assessment_status)),
)
const pendingInvitations = computed(() =>
  invitations.value.filter((i) => i.status === 'pending'),
)
const handledInvitations = computed(() =>
  invitations.value.filter((i) => i.status !== 'pending'),
)

/* ---------- helpers ---------- */
function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    completed: '已完成',
    pending: '进行中',
    failed: '失败',
  }
  return map[status] || '未知'
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    completed: 'success',
    pending: 'warning',
    failed: 'danger',
  }
  return map[status] || 'info'
}

function getInviteStatusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待处理',
    accepted: '已接受',
    declined: '已拒绝',
    expired: '已过期',
  }
  return map[status] || status
}

function getInviteStatusType(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    accepted: 'success',
    declined: 'info',
    expired: 'info',
  }
  return map[status] || 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function relativeTime(dateStr: string) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} 天前`
  return formatDate(dateStr)
}

/* ---------- data loading ---------- */
const candidateId = computed(() => userStore.userId || userStore.profile?.id)

async function loadInterviewHistory() {
  if (!candidateId.value) return
  loading.value = true
  try {
    const data = await fetchHistory(candidateId.value)
    records.value = Array.isArray(data) ? data : []
  } catch {
    ElMessage.error('加载面试记录失败')
  } finally {
    loading.value = false
  }
}

async function loadHubJobs() {
  hubJobs.value = await readHubJobs()
}

async function loadInvitations() {
  if (!candidateId.value) return
  try {
    const res = await getCandidateInvitations(candidateId.value)
    invitations.value = res.items ?? []
    pendingInviteCount.value = await getPendingInvitationCount(candidateId.value)
  } catch {
    console.warn('加载邀请列表失败')
  }
}

async function refreshAll() {
  await Promise.all([loadHubJobs(), loadInterviewHistory(), loadInvitations()])
  ElMessage.success('已刷新')
}

/* ---------- actions ---------- */
function goToInterview(record: any) {
  router.push({ path: '/home/interviews/room', query: { jobId: String(record.job_id) } })
}

function startHubInterview(job: InterviewHubJob) {
  router.push({ path: '/home/interviews/room', query: { jobId: String(job.jobId) } })
}

function goToJobDetail(jobId: number) {
  router.push(`/home/jobs/${jobId}`)
}

async function removeSavedJob(jobId: number) {
  const ok = await removeHubJob(jobId)
  if (!ok) {
    ElMessage.error('移除失败，请稍后重试')
    return
  }
  await loadHubJobs()
  ElMessage.success('已移除')
}

function viewReport(recordId: number) {
  router.push(`/home/report/${recordId}`)
}

async function handleInvitation(inv: Invitation, action: 'accepted' | 'declined') {
  const label = action === 'accepted' ? '接受' : '拒绝'
  try {
    await ElMessageBox.confirm(
      `确定${label}来自「${inv.hr_name || 'HR'}」关于「${inv.job_name}」的面试邀请吗？`,
      '确认操作',
      { confirmButtonText: label, cancelButtonText: '取消', type: 'info' },
    )
  } catch {
    return
  }
  try {
    await respondInvitation(candidateId.value!, inv.id, action)
    ElMessage.success(`已${label}邀请`)
    await loadInvitations()
    if (action === 'accepted') {
      router.push({ path: '/home/interviews/room', query: { jobId: String(inv.job_id) } })
    }
  } catch {
    ElMessage.error('操作失败，请重试')
  }
}

/* ---------- lifecycle ---------- */
onMounted(async () => {
  if (route.query.jobId) {
    router.replace({ path: '/home/interviews/room', query: route.query })
    return
  }
  await Promise.all([loadHubJobs(), loadInterviewHistory(), loadInvitations()])
})

watch(
  () => route.query.tab,
  (tab) => {
    if (
      typeof tab === 'string' &&
      ['invitations', 'saved', 'pending', 'completed', 'other'].includes(tab)
    ) {
      activeTab.value = tab
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="interviews-page" v-loading="loading">
    <!-- ============ Hero 区 ============ -->
    <header class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-left">
          <h1>我的面试中心</h1>
          <p class="hero-desc">
            集中管理 HR 邀请、收藏岗位、进行中的 AI 面试以及已完成的评估报告，一站式掌握求职进度。
          </p>
        </div>
        <div class="hero-actions">
          <button class="btn-hero-primary" @click="router.push('/home/jobs')">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M6.5 2a4.5 4.5 0 013.53 7.29l3.09 3.09a.75.75 0 01-1.06 1.06l-3.09-3.09A4.5 4.5 0 116.5 2zm0 1.5a3 3 0 100 6 3 3 0 000-6z" fill="currentColor"/></svg>
            浏览岗位
          </button>
          <button class="btn-hero-ghost" @click="refreshAll">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M13.65 2.35a.5.5 0 01.85.35v4a.5.5 0 01-.5.5h-4a.5.5 0 01-.35-.85l1.48-1.48A5 5 0 003.05 9.5a.75.75 0 01-1.5.1 6.5 6.5 0 0110.72-5.27L13.65 2.35z" fill="currentColor"/><path d="M2.35 13.65a.5.5 0 01-.85-.35v-4a.5.5 0 01.5-.5h4a.5.5 0 01.35.85L4.88 11.1A5 5 0 0012.95 6.5a.75.75 0 011.5-.1 6.5 6.5 0 01-10.72 5.27L2.35 13.65z" fill="currentColor"/></svg>
            刷新
          </button>
        </div>
      </div>
    </header>

    <!-- ============ 统计概览 ============ -->
    <section class="stats-row">
      <button
        class="stat-card"
        :class="{ active: activeTab === 'invitations' }"
        @click="activeTab = 'invitations'"
      >
        <span class="stat-icon invite-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M20 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2z" stroke="currentColor" stroke-width="1.8"/><path d="M22 6l-10 7L2 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </span>
        <div class="stat-body">
          <span class="stat-num">{{ pendingInviteCount }}</span>
          <span class="stat-label">HR 邀请</span>
        </div>
        <span v-if="pendingInviteCount > 0" class="stat-badge">{{ pendingInviteCount }} 条新邀请</span>
      </button>

      <button
        class="stat-card"
        :class="{ active: activeTab === 'saved' }"
        @click="activeTab = 'saved'"
      >
        <span class="stat-icon saved-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </span>
        <div class="stat-body">
          <span class="stat-num">{{ hubJobs.length }}</span>
          <span class="stat-label">待开始</span>
        </div>
      </button>

      <button
        class="stat-card"
        :class="{ active: activeTab === 'pending' }"
        @click="activeTab = 'pending'"
      >
        <span class="stat-icon pending-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </span>
        <div class="stat-body">
          <span class="stat-num">{{ pendingRecords.length }}</span>
          <span class="stat-label">进行中</span>
        </div>
      </button>

      <button
        class="stat-card"
        :class="{ active: activeTab === 'completed' }"
        @click="activeTab = 'completed'"
      >
        <span class="stat-icon done-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <div class="stat-body">
          <span class="stat-num">{{ completedRecords.length }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </button>
    </section>

    <!-- ============ Tab 内容区 ============ -->
    <section class="tab-content">

      <!-- ===== HR 邀请 ===== -->
      <div v-if="activeTab === 'invitations'" class="tab-panel">
        <div class="panel-header">
          <h2>HR 邀请</h2>
          <p class="panel-sub">HR 根据你的简历和画像，邀请你参加特定岗位的 AI 面试评估。</p>
        </div>

        <!-- 待处理邀请 -->
        <div v-if="pendingInvitations.length > 0" class="card-list">
          <div
            v-for="inv in pendingInvitations"
            :key="inv.id"
            class="invite-card pending"
          >
            <div class="invite-badge-row">
              <span class="invite-badge">新邀请</span>
              <span class="invite-time">{{ relativeTime(inv.created_at) }}</span>
            </div>
            <div class="invite-body">
              <h3 @click="goToJobDetail(inv.job_id)">{{ inv.job_name }}</h3>
              <div class="invite-meta">
                <span>{{ inv.company }}</span>
                <span v-if="inv.city">{{ inv.city }}</span>
                <span v-if="inv.salary" class="salary">{{ inv.salary }}</span>
              </div>
              <p v-if="inv.message" class="invite-msg">
                <strong>{{ inv.hr_name || 'HR' }}</strong>：「{{ inv.message }}」
              </p>
              <p v-else class="invite-msg">
                <strong>{{ inv.hr_name || 'HR' }}</strong> 邀请你参加此岗位的面试评估
              </p>
            </div>
            <div class="invite-actions">
              <button class="btn-accept" @click="handleInvitation(inv, 'accepted')">接受邀请</button>
              <button class="btn-decline" @click="handleInvitation(inv, 'declined')">婉拒</button>
              <button class="btn-detail" @click="goToJobDetail(inv.job_id)">查看岗位</button>
            </div>
          </div>
        </div>

        <!-- 已处理邀请 -->
        <div v-if="handledInvitations.length > 0" class="handled-section">
          <p class="handled-title">历史邀请</p>
          <div class="card-list">
            <div v-for="inv in handledInvitations" :key="inv.id" class="invite-card handled">
              <div class="invite-body">
                <div class="invite-handled-row">
                  <h3 @click="goToJobDetail(inv.job_id)">{{ inv.job_name }}</h3>
                  <el-tag size="small" :type="getInviteStatusType(inv.status)">{{ getInviteStatusLabel(inv.status) }}</el-tag>
                </div>
                <div class="invite-meta">
                  <span>{{ inv.company }}</span>
                  <span>{{ inv.hr_name || 'HR' }} 邀请</span>
                  <span>{{ formatDate(inv.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 全空状态 -->
        <div v-if="invitations.length === 0" class="empty-block">
          <div class="empty-illustration">
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
              <rect x="10" y="18" width="60" height="44" rx="6" stroke="#c5cee0" stroke-width="2"/>
              <path d="M10 28l30 18 30-18" stroke="#c5cee0" stroke-width="2"/>
              <circle cx="62" cy="22" r="10" fill="#667eea" opacity="0.15"/>
            </svg>
          </div>
          <h3>暂无 HR 邀请</h3>
          <p>完善你的个人简历和技能标签，让更多 HR 发现你</p>
          <button class="btn-empty" @click="router.push('/home/profile')">完善简历</button>
        </div>
      </div>

      <!-- ===== 待开始 ===== -->
      <div v-if="activeTab === 'saved'" class="tab-panel">
        <div class="panel-header">
          <h2>待开始</h2>
          <p class="panel-sub">你收藏并加入面试列表的岗位，点击即可进入 AI 面试。</p>
        </div>

        <div v-if="hubJobs.length > 0" class="card-list">
          <div
            v-for="job in hubJobs"
            :key="job.jobId"
            class="job-card"
            :class="{ highlighted: highlightJobId === job.jobId }"
          >
            <div class="job-card-body">
              <div class="job-card-top">
                <h3 @click="goToJobDetail(job.jobId)">{{ job.title }}</h3>
                <span class="status-dot waiting">待开始</span>
              </div>
              <div class="job-card-meta">
                <span>{{ job.company || '未知公司' }}</span>
                <span v-if="job.city">{{ job.city }}</span>
                <span v-if="job.salary" class="salary">{{ job.salary }}</span>
              </div>
              <p class="card-date">收藏于 {{ relativeTime(job.addedAt) }}</p>
            </div>
            <div class="job-card-actions">
              <button class="btn-primary-sm" @click="startHubInterview(job)">开始面试</button>
              <button class="btn-ghost-sm" @click="goToJobDetail(job.jobId)">详情</button>
              <button class="btn-text-sm danger" @click="removeSavedJob(job.jobId)">移除</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-block">
          <div class="empty-illustration">
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
              <path d="M40 15l7.5 15.2 16.8 2.4-12.15 11.85 2.87 16.72L40 52.68l-15.02 7.89 2.87-16.72L15.7 32.6l16.8-2.4z" stroke="#c5cee0" stroke-width="2" fill="#667eea" fill-opacity="0.08"/>
            </svg>
          </div>
          <h3>还没有待开始的岗位</h3>
          <p>去岗位广场发现合适的机会，收藏后即出现在这里</p>
          <button class="btn-empty" @click="router.push('/home/jobs')">浏览岗位</button>
        </div>
      </div>

      <!-- ===== 进行中 ===== -->
      <div v-if="activeTab === 'pending'" class="tab-panel">
        <div class="panel-header">
          <h2>进行中</h2>
          <p class="panel-sub">AI 面试评估尚在进行中，可随时继续对话。</p>
        </div>

        <div v-if="pendingRecords.length > 0" class="card-list">
          <div v-for="record in pendingRecords" :key="record.id" class="job-card">
            <div class="job-card-body">
              <div class="job-card-top">
                <h3>{{ record.job_title || '未知岗位' }}</h3>
                <span class="status-dot ongoing">进行中</span>
              </div>
              <div class="job-card-meta">
                <span>{{ record.assessment_mode === 'immersive' ? '沉浸式 AI 面试' : record.assessment_mode }}</span>
                <span>发起于 {{ relativeTime(record.created_at) }}</span>
              </div>
              <div v-if="record.match_score != null" class="progress-row">
                <span class="progress-label">实时匹配度</span>
                <div class="progress-track">
                  <div class="progress-fill" :style="{ width: Math.round(record.match_score) + '%' }"></div>
                </div>
                <span class="progress-val">{{ Math.round(record.match_score) }}%</span>
              </div>
            </div>
            <div class="job-card-actions">
              <button class="btn-primary-sm" @click="goToInterview(record)">继续面试</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-block">
          <div class="empty-illustration">
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
              <circle cx="40" cy="40" r="28" stroke="#c5cee0" stroke-width="2"/>
              <path d="M40 22v18l12 7" stroke="#667eea" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
            </svg>
          </div>
          <h3>当前没有进行中的面试</h3>
          <p>从「待开始」选择一个岗位，开始 AI 面试吧</p>
        </div>
      </div>

      <!-- ===== 已完成 ===== -->
      <div v-if="activeTab === 'completed'" class="tab-panel">
        <div class="panel-header">
          <h2>已完成</h2>
          <p class="panel-sub">AI 评估报告已生成，包含人岗匹配度、性格分析、面试亮点等洞察。</p>
        </div>

        <div v-if="completedRecords.length > 0" class="card-list">
          <div v-for="record in completedRecords" :key="record.id" class="job-card completed-card">
            <div class="job-card-body">
              <div class="job-card-top">
                <h3>{{ record.job_title || '未知岗位' }}</h3>
                <span class="status-dot done">已完成</span>
              </div>
              <div class="job-card-meta">
                <span>完成于 {{ relativeTime(record.updated_at || record.created_at) }}</span>
              </div>
              <div v-if="record.match_score != null" class="score-display">
                <span class="score-ring" :class="record.match_score >= 70 ? 'high' : record.match_score >= 40 ? 'mid' : 'low'">
                  {{ Math.round(record.match_score) }}
                </span>
                <span class="score-unit">匹配度</span>
              </div>
            </div>
            <div class="job-card-actions">
              <button class="btn-primary-sm" @click="viewReport(record.id)">查看报告</button>
              <button class="btn-ghost-sm" @click="goToInterview(record)">重新面试</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-block">
          <div class="empty-illustration">
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
              <rect x="16" y="12" width="48" height="56" rx="6" stroke="#c5cee0" stroke-width="2"/>
              <path d="M28 32h24M28 42h16M28 52h20" stroke="#c5cee0" stroke-width="2" stroke-linecap="round"/>
              <path d="M54 20l8 8-8 8" stroke="#667eea" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
            </svg>
          </div>
          <h3>暂无已完成的评估报告</h3>
          <p>完成一次 AI 面试后即可在此查看详细评估报告</p>
        </div>
      </div>

      <!-- ===== 其他 ===== -->
      <div v-if="activeTab === 'other'" class="tab-panel">
        <div class="panel-header">
          <h2>其他记录</h2>
          <p class="panel-sub">异常终止或失败的面试记录，可重新进入继续。</p>
        </div>

        <div v-if="otherRecords.length > 0" class="card-list">
          <div v-for="record in otherRecords" :key="record.id" class="job-card">
            <div class="job-card-body">
              <div class="job-card-top">
                <h3>{{ record.job_title || '未知岗位' }}</h3>
                <el-tag size="small" :type="getStatusType(record.assessment_status)">{{ getStatusLabel(record.assessment_status) }}</el-tag>
              </div>
              <div class="job-card-meta">
                <span>{{ formatDate(record.updated_at || record.created_at) }}</span>
              </div>
            </div>
            <div class="job-card-actions">
              <button class="btn-ghost-sm" @click="goToInterview(record)">重新进入</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-block">
          <h3>没有异常记录</h3>
          <p>一切顺利，没有失败或异常的面试记录</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ==================== 全局 ==================== */
.interviews-page {
  min-height: calc(100vh - 64px);
  background: #f7f8fc;
}

/* ==================== Hero ==================== */
.hero {
  position: relative;
  padding: 40px 48px 36px;
  overflow: hidden;
}
.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 1;
}
.hero-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1380px;
  margin: 0 auto;
  gap: 24px;
}
.hero-left h1 {
  margin: 0 0 10px;
  font-size: 30px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.3px;
}
.hero-desc {
  margin: 0;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.7;
  max-width: 600px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}
.btn-hero-primary,
.btn-hero-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}
.btn-hero-primary {
  background: #fff;
  color: #667eea;
}
.btn-hero-primary:hover {
  background: #f0f2ff;
  transform: translateY(-1px);
}
.btn-hero-ghost {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.35);
}
.btn-hero-ghost:hover {
  background: rgba(255, 255, 255, 0.28);
}

/* ==================== 统计行 ==================== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  max-width: 1380px;
  margin: -28px auto 0;
  padding: 0 48px;
  position: relative;
  z-index: 2;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 22px;
  background: #fff;
  border: 2px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
  text-align: left;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.12);
}
.stat-card.active {
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.18);
}
.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  flex-shrink: 0;
}
.invite-icon { background: #eef3ff; color: #667eea; }
.saved-icon { background: #fff5e6; color: #f59e0b; }
.pending-icon { background: #f0faf4; color: #10b981; }
.done-icon { background: #f3f0ff; color: #764ba2; }
.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-num {
  font-size: 26px;
  font-weight: 700;
  color: #111827;
  line-height: 1.1;
}
.stat-label {
  font-size: 13px;
  color: #6b7280;
}
.stat-badge {
  position: absolute;
  top: 12px;
  right: 14px;
  padding: 2px 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #f97066, #e74c3c);
  border-radius: 20px;
}

/* ==================== Tab 内容 ==================== */
.tab-content {
  max-width: 1380px;
  margin: 28px auto 0;
  padding: 0 48px 48px;
}
.tab-panel {
  animation: fadeUp 0.3s ease;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.panel-header {
  margin-bottom: 24px;
}
.panel-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
}
.panel-sub {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

/* ==================== 通用卡片列表 ==================== */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ==================== 邀请卡片 ==================== */
.invite-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px;
  border: 1px solid #e7ecf3;
  transition: all 0.2s;
}
.invite-card.pending {
  border-left: 4px solid #667eea;
  box-shadow: 0 2px 16px rgba(102, 126, 234, 0.08);
}
.invite-card.handled {
  opacity: 0.75;
  padding: 18px 28px;
}
.invite-badge-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.invite-badge {
  display: inline-block;
  padding: 2px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  background: #eef3ff;
  border-radius: 20px;
}
.invite-time {
  font-size: 12px;
  color: #94a3b8;
}
.invite-body h3 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  cursor: pointer;
}
.invite-body h3:hover {
  color: #667eea;
}
.invite-handled-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.invite-handled-row h3 {
  margin: 0;
  font-size: 16px;
}
.invite-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #6b7280;
  flex-wrap: wrap;
}
.invite-meta .salary {
  color: #e74c3c;
  font-weight: 600;
}
.invite-msg {
  margin: 10px 0 0;
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  padding: 10px 14px;
  background: #f8f9fc;
  border-radius: 10px;
}
.invite-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
}
.btn-accept {
  padding: 8px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-accept:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35);
}
.btn-decline {
  padding: 8px 20px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  color: #6b7280;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-decline:hover {
  border-color: #d1d5db;
  color: #374151;
}
.btn-detail {
  padding: 8px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #667eea;
  cursor: pointer;
}
.btn-detail:hover {
  text-decoration: underline;
}
.handled-section {
  margin-top: 28px;
}
.handled-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ==================== 岗位卡片 ==================== */
.job-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: #fff;
  border-radius: 16px;
  padding: 22px 28px;
  border: 1px solid #e7ecf3;
  transition: all 0.2s;
}
.job-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}
.job-card.highlighted {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12);
}
.job-card-body {
  flex: 1;
  min-width: 0;
}
.job-card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.job-card-top h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #111827;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.job-card-top h3:hover {
  color: #667eea;
}
.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 12px;
  border-radius: 20px;
  flex-shrink: 0;
}
.status-dot::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.status-dot.waiting { background: #fff5e6; color: #d97706; }
.status-dot.waiting::before { background: #f59e0b; }
.status-dot.ongoing { background: #ecfdf5; color: #059669; }
.status-dot.ongoing::before { background: #10b981; }
.status-dot.done { background: #f3f0ff; color: #7c3aed; }
.status-dot.done::before { background: #764ba2; }

.job-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #6b7280;
  flex-wrap: wrap;
}
.job-card-meta .salary {
  color: #e74c3c;
  font-weight: 600;
}
.card-date {
  margin: 6px 0 0;
  font-size: 12px;
  color: #94a3b8;
}

/* progress bar */
.progress-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}
.progress-label {
  font-size: 12px;
  color: #6b7280;
  flex-shrink: 0;
}
.progress-track {
  flex: 1;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.5s ease;
}
.progress-val {
  font-size: 13px;
  font-weight: 700;
  color: #667eea;
  min-width: 36px;
  text-align: right;
}

/* score ring */
.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}
.score-ring {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 700;
  border: 3px solid;
}
.score-ring.high { border-color: #10b981; color: #059669; background: #ecfdf5; }
.score-ring.mid { border-color: #f59e0b; color: #d97706; background: #fffbeb; }
.score-ring.low { border-color: #ef4444; color: #dc2626; background: #fef2f2; }
.score-unit {
  font-size: 13px;
  color: #6b7280;
}

/* ==================== 卡片操作按钮 ==================== */
.job-card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.btn-primary-sm {
  padding: 8px 20px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary-sm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.3);
}
.btn-ghost-sm {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 13px;
  color: #475569;
  background: #fff;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-ghost-sm:hover {
  border-color: #667eea;
  color: #667eea;
}
.btn-text-sm {
  padding: 8px 12px;
  border: none;
  background: transparent;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
}
.btn-text-sm.danger:hover {
  color: #ef4444;
}

/* ==================== 空状态 ==================== */
.empty-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: #fff;
  border-radius: 20px;
  border: 2px dashed #e5e7eb;
}
.empty-illustration {
  margin-bottom: 16px;
}
.empty-block h3 {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 600;
  color: #374151;
}
.empty-block p {
  margin: 0 0 20px;
  font-size: 14px;
  color: #94a3b8;
  max-width: 320px;
}
.btn-empty {
  padding: 10px 28px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-empty:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.35);
}

/* ==================== 完成卡片特殊样式 ==================== */
.completed-card {
  border-left: 3px solid #764ba2;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .hero { padding: 32px 24px 28px; }
  .stats-row { padding: 0 24px; grid-template-columns: repeat(2, 1fr); }
  .tab-content { padding: 0 24px 36px; }
}

@media (max-width: 768px) {
  .hero-content { flex-direction: column; align-items: flex-start; }
  .hero-actions { width: 100%; }
  .stats-row { grid-template-columns: 1fr 1fr; gap: 10px; }
  .job-card { flex-direction: column; align-items: stretch; }
  .job-card-actions { justify-content: flex-start; flex-wrap: wrap; }
  .invite-actions { flex-wrap: wrap; }
}

@media (max-width: 480px) {
  .hero { padding: 24px 16px 20px; }
  .hero-left h1 { font-size: 24px; }
  .stats-row { padding: 0 16px; grid-template-columns: 1fr; margin-top: -20px; }
  .tab-content { padding: 0 16px 24px; }
  .stat-card { padding: 14px 16px; }
}
</style>