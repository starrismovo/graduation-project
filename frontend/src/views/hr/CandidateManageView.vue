<template>
  <div class="candidate-workbench">
    <div class="page-header">
      <div>
        <h1 class="page-title">候选人工作台</h1>
        <p class="page-subtitle">以 HR 操作为中心：优先处理邀请反馈、快速邀请匹配候选人、直接查看可决策报告。</p>
      </div>
      <div class="header-actions">
        <el-select
          v-model="selectedJobId"
          placeholder="选择岗位"
          style="width: 260px"
          @change="handleJobChange"
        >
          <el-option
            v-for="job in jobOptions"
            :key="job.id"
            :label="job.name"
            :value="job.id"
          />
        </el-select>
        <el-button :icon="Refresh" @click="refreshAll">刷新</el-button>
      </div>
    </div>

    <div v-if="selectedJob" class="focus-banner">
      <div class="focus-copy">
        <span class="focus-kicker">当前岗位</span>
        <h2>{{ selectedJob.name }}</h2>
        <p>{{ selectedJob.company || '未填写公司' }} · {{ selectedJob.city || '未填写城市' }} · {{ selectedJob.salary_min || 0 }}k-{{ selectedJob.salary_max || 0 }}k</p>
      </div>
      <div class="focus-actions">
        <el-button type="primary" @click="goJobManage">管理岗位</el-button>
        <el-button plain @click="goAnalytics">数据分析</el-button>
      </div>
    </div>

    <div v-else class="empty-shell">
      <h3>还没有可管理的岗位</h3>
      <p>先创建岗位，再围绕岗位构建候选评估、邀请和推荐闭环。</p>
      <el-button type="primary" @click="goJobManage">去创建岗位</el-button>
    </div>

    <template v-if="selectedJob">
      <section class="ops-priority-card">
        <div class="ops-priority-head">
          <div>
            <h3>HR 操作优先区</h3>
            <p>先做最影响决策的动作，再看全量数据。</p>
          </div>
          <el-button type="primary" :disabled="!inviteTargets.length" @click="inviteTopCandidate">
            {{ inviteTargets.length ? '邀请首位推荐候选人' : '暂无可邀请候选人' }}
          </el-button>
        </div>

        <div class="ops-kpi-row">
          <article class="ops-kpi">
            <div class="kpi-title">待响应邀请</div>
            <div class="kpi-value warning">{{ pendingInvitations.length }}</div>
            <p>候选人尚未处理的邀请</p>
          </article>
          <article class="ops-kpi">
            <div class="kpi-title">可查看报告</div>
            <div class="kpi-value">{{ readyReportCandidates.length }}</div>
            <p>可立即查看并决策的评估</p>
          </article>
          <article class="ops-kpi">
            <div class="kpi-title">可邀请推荐</div>
            <div class="kpi-value success">{{ inviteTargets.length }}</div>
            <p>可一键发起邀请的候选人</p>
          </article>
        </div>
      </section>

      <div class="layout-grid">
        <div class="main-column">
          <section class="panel-card">
            <div class="panel-header">
              <div>
                <h3>可直接处理的候选人报告</h3>
                <p>优先处理已完成评估的候选人，减少决策堆积。</p>
              </div>
              <el-tag type="success">{{ readyReportCandidates.length }} 份待查看</el-tag>
            </div>

            <el-table :data="paginatedCandidates" border stripe style="width: 100%" empty-text="当前岗位暂无候选评估记录">
              <el-table-column label="候选人" min-width="180">
                <template #default="{ row }">
                  <div class="candidate-cell">
                    <div class="avatar-circle">{{ getInitial(row.candidate_name) }}</div>
                    <div>
                      <div class="candidate-name">{{ row.candidate_name || '未知候选人' }}</div>
                      <div class="candidate-email">{{ row.candidate_email || '--' }}</div>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="匹配度" min-width="160">
                <template #default="{ row }">
                  <div v-if="row.match_score != null" class="score-cell">
                    <div class="score-bar">
                      <div
                        class="score-fill"
                        :class="getScoreClass(row.match_score)"
                        :style="{ width: row.match_score + '%' }"
                      />
                    </div>
                    <span class="score-number" :style="{ color: getScoreColor(row.match_score) }">{{ row.match_score }}%</span>
                  </div>
                  <span v-else class="no-score">待评估</span>
                </template>
              </el-table-column>

              <el-table-column label="状态" min-width="110" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.assessment_status === 'completed' ? 'success' : 'warning'" size="small">
                    {{ row.assessment_status === 'completed' ? '已完成' : '进行中' }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="轮数" min-width="80" align="center">
                <template #default="{ row }">{{ row.total_rounds ?? '--' }}</template>
              </el-table-column>

              <el-table-column label="评估时间" min-width="160">
                <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
              </el-table-column>

              <el-table-column label="操作" min-width="170" fixed="right">
                <template #default="{ row }">
                  <el-button
                    v-if="row.assessment_status === 'completed'"
                    link
                    type="primary"
                    @click="viewReport(row)"
                  >
                    查看报告
                  </el-button>
                  <el-button
                    v-else
                    link
                    type="warning"
                    disabled
                  >
                    等待完成
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-row">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                :total="filteredCandidates.length"
                layout="total, sizes, prev, pager, next"
                @current-change="handlePageChange"
                @size-change="handleSizeChange"
              />
            </div>
          </section>

          <section class="panel-card">
            <div class="panel-header">
              <div>
                <h3>可立即邀请候选人</h3>
                <p>优先展示可以马上执行邀请动作的人选，减少切页操作。</p>
              </div>
              <el-tag type="success">{{ recommendedCandidates.length }} 个推荐</el-tag>
            </div>

            <div v-loading="recommendLoading">
              <div v-if="recommendedCandidates.length > 0" class="recommend-grid">
                <article v-for="candidate in recommendedCandidates" :key="candidate.recommendKey" class="recommend-card">
                  <div class="recommend-top">
                    <div>
                      <h4>{{ candidate.candidate_name || '未知候选人' }}</h4>
                      <p>{{ candidate.candidate_email || '暂无邮箱' }}</p>
                    </div>
                    <span class="recommend-score">{{ candidate.match_score }}%</span>
                  </div>

                  <div class="recommend-body">
                    <div class="recommend-meta">来源岗位：{{ candidate.job_title || '未知岗位' }}</div>
                    <div class="recommend-meta">
                      推荐理由：{{ candidate.recommendation_reasons?.[0] || getRecommendReason(candidate.match_score, candidate.job_title) }}
                    </div>
                  </div>

                  <div class="recommend-actions">
                    <el-button
                      type="primary"
                      plain
                      :disabled="!candidate.candidate_id || isAlreadyInvited(candidate.candidate_id)"
                      @click="openInviteDialog(candidate)"
                    >
                      {{ isAlreadyInvited(candidate.candidate_id) ? '已邀请' : '邀请参加当前岗位评估' }}
                    </el-button>
                    <el-button link type="primary" @click="viewReport(candidate)">查看历史报告</el-button>
                  </div>
                </article>
              </div>

              <div v-else class="inner-empty">
                当前没有适合推荐到该岗位的候选人。可以先等待其它岗位积累更多评估结果。
              </div>
            </div>
          </section>
        </div>

        <div class="side-column">
          <section class="panel-card compact-panel">
            <div class="panel-header">
              <div>
                <h3>待响应邀请</h3>
                <p>这里是当前最需要跟进的邀请状态。</p>
              </div>
            </div>

            <div v-if="pendingInvitations.length > 0" class="invite-list">
              <article v-for="inv in pendingInvitations" :key="inv.id" class="invite-item">
                <div class="invite-row">
                  <strong>{{ inv.candidate_name || '未知候选人' }}</strong>
                  <el-tag size="small" :type="getInviteStatusType(inv.status)">{{ getInviteStatusLabel(inv.status) }}</el-tag>
                </div>
                <div class="invite-sub">{{ inv.candidate_name || '候选人' }} · {{ relativeTime(inv.created_at) }}</div>
                <p class="invite-message">{{ inv.message || '未填写邀请说明' }}</p>
              </article>
            </div>

            <div v-else class="inner-empty">
              当前没有待响应邀请。
            </div>
          </section>

          <section class="panel-card compact-panel">
            <div class="panel-header">
              <div>
                <h3>快速操作</h3>
                <p>把高频动作固定在右侧，少跳页、少切换。</p>
              </div>
            </div>

            <div class="action-stack">
              <button class="action-link" :disabled="!inviteTargets.length" @click="inviteTopCandidate">
                <span>一键邀请首位推荐候选人</span>
                <small>优先推动候选人进入当前岗位评估</small>
              </button>
              <button class="action-link" @click="goReports">
                <span>查看全部评估报告</span>
                <small>集中处理完成评估并给出反馈</small>
              </button>
              <button class="action-link" @click="goAnalytics">
                <span>查看候选漏斗分析</span>
                <small>判断邀请接受率和评估转化</small>
              </button>
            </div>
          </section>
        </div>
      </div>
    </template>

    <el-dialog v-model="showInviteDialog" title="邀请候选人参加岗位评估" width="520px">
      <div v-if="inviteCandidate" class="invite-dialog-body">
        <div class="dialog-summary">
          <div><span>候选人：</span>{{ inviteCandidate.candidate_name || '未知候选人' }}</div>
          <div><span>目标岗位：</span>{{ selectedJob?.name || '--' }}</div>
          <div><span>推荐依据：</span>{{ inviteCandidate.job_title || '已有历史评估' }} · {{ inviteCandidate.match_score ?? 0 }}%</div>
        </div>
        <el-input
          v-model="inviteMessage"
          type="textarea"
          :rows="5"
          placeholder="给候选人写一段邀请说明，例如说明岗位亮点、面试形式和适合他的原因。"
        />
      </div>
      <template #footer>
        <el-button @click="showInviteDialog = false">取消</el-button>
        <el-button type="primary" :loading="inviteLoading" @click="submitInvitation">发送邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getHRJobList, getHRRecommendedCandidates } from '@/api/job'
import { getHRInvitations, sendInvitation } from '@/api/invitation'
import request from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()

const candidateLoading = ref(false)
const recommendLoading = ref(false)
const allCandidates = ref<any[]>([])
const invitations = ref<any[]>([])
const jobOptions = ref<any[]>([])
const remoteRecommendedCandidates = ref<any[]>([])
const recommendedRequestSucceeded = ref(false)
const selectedJobId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)

const showInviteDialog = ref(false)
const inviteCandidate = ref<any | null>(null)
const inviteMessage = ref('')
const inviteLoading = ref(false)

const hrId = computed(() => userStore.userId || userStore.profile?.id || '')

const selectedJob = computed(() => {
  return jobOptions.value.find(job => job.id === selectedJobId.value) || null
})

const filteredCandidates = computed(() => {
  if (!selectedJobId.value) return []
  return allCandidates.value.filter(candidate => Number(candidate.job_id) === selectedJobId.value)
})

const paginatedCandidates = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredCandidates.value.slice(start, start + pageSize.value)
})

const selectedInvitations = computed(() => {
  if (!selectedJobId.value) return []
  return invitations.value
    .filter(inv => Number(inv.job_id) === selectedJobId.value)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

const pendingInvitations = computed(() => {
  return selectedInvitations.value.filter(inv => inv.status === 'pending')
})

const readyReportCandidates = computed(() => {
  return filteredCandidates.value
    .filter(candidate => candidate.assessment_status === 'completed')
    .sort((a, b) => {
      const scoreDiff = Number(b.match_score || 0) - Number(a.match_score || 0)
      if (scoreDiff !== 0) return scoreDiff
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
    })
})

const currentJobCandidateIds = computed(() => {
  const ids = new Set<number>()
  filteredCandidates.value.forEach(candidate => {
    const id = Number(candidate.candidate_id)
    if (!Number.isNaN(id) && id > 0) {
      ids.add(id)
    }
  })
  return ids
})

const fallbackRecommendedCandidates = computed(() => {
  if (!selectedJobId.value) return []

  const uniqueMap = new Map<number, any>()

  allCandidates.value
    .filter(candidate => Number(candidate.job_id) !== selectedJobId.value)
    .filter(candidate => candidate.assessment_status === 'completed')
    .filter(candidate => candidate.match_score != null)
    .forEach(candidate => {
      const candidateId = Number(candidate.candidate_id)
      if (Number.isNaN(candidateId) || candidateId <= 0) return
      if (currentJobCandidateIds.value.has(candidateId)) return

      const existing = uniqueMap.get(candidateId)
      if (!existing || Number(candidate.match_score) > Number(existing.match_score)) {
        uniqueMap.set(candidateId, {
          ...candidate,
          recommendKey: `${candidateId}-${candidate.record_id}`,
          recommendation_score: Number(candidate.match_score || 0),
          source_job_title: candidate.job_title,
          recommendation_reasons: [getRecommendReason(Number(candidate.match_score || 0), candidate.job_title)],
        })
      }
    })

  return Array.from(uniqueMap.values())
    .sort((a, b) => Number(b.match_score) - Number(a.match_score))
    .slice(0, 6)
})

const recommendedCandidates = computed(() => {
  if (recommendedRequestSucceeded.value) {
    return remoteRecommendedCandidates.value
  }
  return fallbackRecommendedCandidates.value
})

const inviteTargets = computed(() => {
  return recommendedCandidates.value.filter(candidate => !isAlreadyInvited(candidate.candidate_id))
})

const jobMetrics = computed(() => {
  const completed = filteredCandidates.value.filter(item => item.assessment_status === 'completed')
  const avgMatch = completed.length
    ? Math.round(completed.reduce((sum, item) => sum + (item.match_score || 0), 0) / completed.length)
    : 0

  return {
    assessed: filteredCandidates.value.length,
    completed: completed.length,
    avgMatch,
    pendingInvites: selectedInvitations.value.filter(inv => inv.status === 'pending').length,
  }
})

onMounted(async () => {
  await loadJobOptions()
  await refreshAll(false)
})

function getErrorMessage(error: any, fallback = '未知错误') {
  const detail = error?.response?.data?.detail ?? error?.response?.data?.message ?? error?.message ?? fallback

  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail.map(item => {
      if (typeof item === 'string') return item
      if (item?.msg) return item.msg
      return JSON.stringify(item)
    }).join('；')
  }
  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail)
  }
  return String(detail)
}

async function loadJobOptions() {
  try {
    const res = await getHRJobList({ limit: 200 })
    jobOptions.value = res.data?.items || []
    if (!selectedJobId.value && jobOptions.value.length > 0) {
      selectedJobId.value = jobOptions.value[0].id
    }
  } catch (error) {
    console.error('加载岗位失败:', error)
    ElMessage.error('加载岗位列表失败：' + getErrorMessage(error))
  }
}

async function loadCandidates() {
  candidateLoading.value = true
  try {
    const res = await request.get('/assessment/hr/candidates', { params: { limit: 200 } })
    const data = res.data
    if (data?.code === 200 && data?.data) {
      allCandidates.value = data.data.items || []
      return
    }
    allCandidates.value = []
    ElMessage.error('加载候选人列表失败')
  } catch (error: any) {
    allCandidates.value = []
    ElMessage.error('请求失败：' + getErrorMessage(error))
  } finally {
    candidateLoading.value = false
  }
}

async function loadRecommendedCandidates() {
  if (!selectedJobId.value) {
    remoteRecommendedCandidates.value = []
    recommendedRequestSucceeded.value = false
    return
  }

  recommendLoading.value = true
  try {
    const res = await getHRRecommendedCandidates(selectedJobId.value, { limit: 6 })
    const payload = res.data || {}
    remoteRecommendedCandidates.value = (payload.items || []).map((candidate: any) => ({
      ...candidate,
      recommendKey: `${candidate.candidate_id}-${candidate.record_id}`,
      job_title: candidate.source_job_title,
      match_score: candidate.recommendation_score,
    }))
    recommendedRequestSucceeded.value = true
  } catch (error) {
    console.warn('加载推荐候选人失败，回退本地聚合:', error)
    remoteRecommendedCandidates.value = []
    recommendedRequestSucceeded.value = false
  } finally {
    recommendLoading.value = false
  }
}

async function loadInvitations() {
  if (!hrId.value) {
    invitations.value = []
    return
  }
  try {
    const res = await getHRInvitations(hrId.value)
    invitations.value = res.items || []
  } catch (error) {
    console.warn('加载邀请记录失败:', error)
    invitations.value = []
  }
}

async function refreshAll(showMessage = true) {
  await Promise.all([loadCandidates(), loadInvitations(), loadRecommendedCandidates()])
  if (showMessage) {
    ElMessage.success('候选人工作台已刷新')
  }
}

function handleJobChange() {
  currentPage.value = 1
  loadRecommendedCandidates()
}

function handlePageChange(page: number) {
  currentPage.value = page
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
}

function openInviteDialog(candidate: any) {
  inviteCandidate.value = candidate
  inviteMessage.value = `你好，基于你在“${candidate.job_title || '既往岗位'}”评估中的表现，我们希望邀请你参与“${selectedJob.value?.name || ''}”岗位的面试评估。`
  showInviteDialog.value = true
}

function inviteTopCandidate() {
  if (!inviteTargets.value.length) {
    ElMessage.info('当前没有可直接邀请的推荐候选人')
    return
  }
  openInviteDialog(inviteTargets.value[0])
}

async function submitInvitation() {
  if (!inviteCandidate.value || !selectedJobId.value) return
  const candidateId = Number(inviteCandidate.value.candidate_id)
  if (Number.isNaN(candidateId) || candidateId <= 0) {
    ElMessage.warning('当前候选人缺少可用 ID，暂时无法发送邀请')
    return
  }
  if (!hrId.value) {
    ElMessage.warning('当前 HR 身份信息缺失，无法发送邀请')
    return
  }

  inviteLoading.value = true
  try {
    await sendInvitation(hrId.value, candidateId, selectedJobId.value, inviteMessage.value.trim())
    ElMessage.success('邀请已发送，候选人端会在面试中心看到这条邀请')
    showInviteDialog.value = false
    await loadInvitations()
  } catch (error: any) {
    ElMessage.error('发送邀请失败：' + getErrorMessage(error))
  } finally {
    inviteLoading.value = false
  }
}

function isAlreadyInvited(candidateId: number | string) {
  const numericId = Number(candidateId)
  if (Number.isNaN(numericId) || !selectedJobId.value) return false
  return selectedInvitations.value.some(inv => Number(inv.candidate_id) === numericId && ['pending', 'accepted'].includes(inv.status))
}

function viewReport(row: any) {
  if (!row.record_id) {
    ElMessage.warning('该候选人暂时没有可查看的报告')
    return
  }
  router.push(`/home/report/${row.record_id}`)
}

function goJobManage() {
  router.push('/home/job-manage')
}

function goAnalytics() {
  router.push('/home/analytics')
}

function goReports() {
  router.push('/home/reports')
}

function getInitial(name: string) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function getScoreClass(score: number) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

function getScoreColor(score: number) {
  if (score >= 80) return '#16a34a'
  if (score >= 60) return '#2563eb'
  if (score >= 40) return '#d97706'
  return '#dc2626'
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

function formatDate(iso: string | null) {
  if (!iso) return '--'
  const date = new Date(iso)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function relativeTime(dateStr: string) {
  if (!dateStr) return '--'
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

function getRecommendReason(score: number, sourceJobName?: string) {
  if (score >= 85) {
    return `该候选人在“${sourceJobName || '历史岗位'}”中的评估结果非常强，适合优先邀请进入当前岗位。`
  }
  if (score >= 70) {
    return `该候选人已在其它岗位表现出较高匹配度，可低成本复用到当前岗位评估。`
  }
  return `该候选人已有完整评估记录，适合补充进入当前岗位的人才池继续判断。`
}
</script>

<style scoped>
.candidate-workbench {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header,
.panel-card,
.focus-banner,
.empty-shell,
.stat-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  border: 1px solid #eef2f7;
}

.page-header {
  padding: 24px 28px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-title {
  margin: 0 0 8px;
  font-size: 28px;
  color: #0f172a;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #64748b;
  max-width: 720px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.focus-banner {
  padding: 22px 24px;
  background: linear-gradient(135deg, #eff6ff 0%, #f8fbff 60%, #ffffff 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}

.focus-kicker {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 12px;
  margin-bottom: 10px;
}

.focus-copy h2 {
  margin: 0;
  font-size: 24px;
  color: #111827;
}

.focus-copy p {
  margin: 8px 0 0;
  font-size: 13px;
  color: #64748b;
}

.focus-actions {
  display: flex;
  gap: 12px;
}

.empty-shell {
  padding: 48px 24px;
  text-align: center;
}

.empty-shell h3 {
  margin: 0 0 10px;
  color: #111827;
}

.empty-shell p {
  margin: 0 0 18px;
  color: #64748b;
}

.ops-priority-card {
  background: linear-gradient(135deg, #f8fbff 0%, #ffffff 65%);
  border: 1px solid #dbeafe;
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  padding: 20px 22px;
}

.ops-priority-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.ops-priority-head h3 {
  margin: 0;
  font-size: 18px;
  color: #0f172a;
}

.ops-priority-head p {
  margin: 6px 0 0;
  font-size: 13px;
  color: #64748b;
}

.ops-kpi-row {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.ops-kpi {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
}

.kpi-title {
  font-size: 12px;
  color: #64748b;
}

.kpi-value {
  margin-top: 8px;
  font-size: 26px;
  line-height: 1;
  font-weight: 700;
  color: #111827;
}

.kpi-value.warning {
  color: #d97706;
}

.kpi-value.success {
  color: #166534;
}

.ops-kpi p {
  margin: 8px 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: #94a3b8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 18px 20px;
}

.stat-card.emphasis {
  background: linear-gradient(180deg, #fff7ed 0%, #ffffff 100%);
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

.stat-value {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 700;
  color: #111827;
}

.stat-meta {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.5;
  color: #94a3b8;
}

.layout-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.8fr);
  gap: 20px;
}

.main-column,
.side-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-card {
  padding: 22px;
}

.compact-panel {
  padding: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #0f172a;
}

.panel-header p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #64748b;
}

.candidate-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1d4ed8 0%, #38bdf8 100%);
  color: #fff;
  font-weight: 700;
}

.candidate-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.candidate-email {
  margin-top: 4px;
  font-size: 12px;
  color: #94a3b8;
}

.score-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-bar {
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background: #e5e7eb;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 999px;
}

.score-fill.high { background: #16a34a; }
.score-fill.medium { background: #2563eb; }
.score-fill.low { background: #d97706; }

.score-number {
  min-width: 44px;
  text-align: right;
  font-size: 13px;
  font-weight: 700;
}

.no-score {
  font-size: 12px;
  color: #9ca3af;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.recommend-card {
  border: 1px solid #e5eefc;
  border-radius: 14px;
  padding: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.recommend-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.recommend-top h4 {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
}

.recommend-top p {
  margin: 6px 0 0;
  font-size: 12px;
  color: #94a3b8;
}

.recommend-score {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: #dcfce7;
  color: #166534;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.recommend-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recommend-meta {
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
}

.recommend-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.invite-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.invite-item {
  border: 1px solid #edf2f7;
  border-radius: 12px;
  padding: 14px;
  background: #fbfdff;
}

.invite-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.invite-row strong {
  font-size: 14px;
  color: #111827;
}

.invite-sub {
  margin-top: 6px;
  font-size: 12px;
  color: #94a3b8;
}

.invite-message {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
}

.action-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-link {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.action-link:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.action-link span {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.action-link small {
  color: #64748b;
  line-height: 1.5;
}

.inner-empty {
  padding: 20px 0 4px;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.7;
}

.invite-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-summary {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 12px;
  background: #f8fafc;
  font-size: 13px;
  color: #475569;
}

.dialog-summary span {
  color: #64748b;
}

@media (max-width: 1200px) {
  .ops-kpi-row,
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .layout-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .page-header,
  .ops-priority-head,
  .focus-banner {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions,
  .focus-actions {
    width: 100%;
    flex-direction: column;
  }

  .ops-kpi-row,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }

  .recommend-actions,
  .invite-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
