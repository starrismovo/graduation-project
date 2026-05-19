<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted, computed } from 'vue'
import { createJob, deleteJob, getHRJobList } from '../api/job'
import { Delete, Edit, View, Plus, ArrowRight, User, Document } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()

const jobsList = ref<any[]>([])
const loading = ref(true)
const jobsTotal = ref(0)
const jobsPage = ref(1)
const jobsPageSize = ref(20)

const showCreateDialog = ref(false)
// ✅ 修正1：所有表单字段初始化为空字符串（原错误：'"''"'）
const createFormData = ref({
  name: '',
  description: '',
  company: '',
  category: '',
  city: '',
  salary_min: '',
  salary_max: '',
  psychological_focus: [] as string[]
})

const psychologicalFocusOptions = [
  { value: 'communication', label: '频繁沟通协作', hint: '适合客户交流、团队推动、跨部门协同' },
  { value: 'self_drive', label: '自驱与目标管理', hint: '适合目标导向、独立推进、结果负责' },
  { value: 'pressure', label: '高压力与稳定应对', hint: '适合节奏快、任务压力高、变化较多' },
  { value: 'innovation', label: '创新探索与快速学习', hint: '适合新业务、复杂问题、快速学习' },
  { value: 'detail', label: '细致稳定与低失误', hint: '适合流程规范、质量控制、细节敏感' },
  { value: 'empathy', label: '服务意识与共情能力', hint: '适合用户服务、组织协作、冲突处理' },
  { value: 'analysis', label: '独立分析与理性决策', hint: '适合数据分析、策略判断、理性决策' },
]

const stats = ref({
  totalJobs: 0,
  openJobs: 0,
  totalSubmissions: 0,
  avgMatchScore: 0,
  pendingReports: 0
})

const featuredJobs = computed(() => {
  return [...jobsList.value]
    .sort((a, b) => {
      const pendingDiff = (b.pendingReports || 0) - (a.pendingReports || 0)
      if (pendingDiff !== 0) return pendingDiff
      return (b.submissions || 0) - (a.submissions || 0)
    })
    .slice(0, 4)
})

const priorityJobs = computed(() => {
  return [...jobsList.value]
    .filter(job => (job.pendingReports || 0) > 0)
    .sort((a, b) => {
      const pendingDiff = (b.pendingReports || 0) - (a.pendingReports || 0)
      if (pendingDiff !== 0) return pendingDiff
      return (b.submissions || 0) - (a.submissions || 0)
    })
    .slice(0, 4)
})

const recentJobs = computed(() => {
  return [...jobsList.value]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 3)
})

const topApplicationJob = computed(() => {
  return [...jobsList.value].sort((a, b) => (b.submissions || 0) - (a.submissions || 0))[0] || null
})

const topMatchJob = computed(() => {
  return [...jobsList.value].sort((a, b) => (b.avgMatch || 0) - (a.avgMatch || 0))[0] || null
})

const loadJobs = async () => {
  try {
    loading.value = true
    const response = await getHRJobList({
      skip: (jobsPage.value - 1) * jobsPageSize.value,
      limit: jobsPageSize.value
    })
    const payload = response.data || {}
    const items = payload.items || []
    const summary = payload.summary || {}

    jobsList.value = items.map((job: any) => ({
      ...job,
      submissions: job.applications ?? 0,
      avgMatch: job.avg_match_rate ?? 0,
      pendingReports: job.pending_reports ?? 0,
      status: job.status === 'active' ? 'open' : (job.status || 'draft'),
      created_at: job.created_at ?? new Date().toISOString(),
      updated_at: job.updated_at ?? job.created_at ?? new Date().toISOString()
    }))

    jobsTotal.value = payload.total || items.length
    stats.value.totalJobs = jobsTotal.value
    stats.value.openJobs = summary.open_jobs ?? jobsList.value.length
    stats.value.totalSubmissions = summary.total_applications ?? 0
    stats.value.avgMatchScore = Math.round(summary.avg_match_rate ?? 0)
    stats.value.pendingReports = summary.pending_reports ?? 0
  } catch (error) {
    console.error('加载岗位列表失败:', error)
    ElMessage.error('加载岗位列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleCreateJob = async () => {
  // ✅ 修正2：修复条件判断语法（原错误："'!..."）
  if (!createFormData.value.name?.trim() || !createFormData.value.description?.trim()) {
    ElMessage.warning('请填写岗位名称和描述')
    return
  }
  // ✅ 修正3：增强校验（可选但推荐）
  if (Number(createFormData.value.salary_min) > Number(createFormData.value.salary_max)) {
    ElMessage.warning('最低薪资不能高于最高薪资')
    return
  }
  
  try {
    const response = await createJob({
      name: createFormData.value.name.trim(),
      description: createFormData.value.description.trim(),
      company: createFormData.value.company?.trim() || '未填写',
      category: createFormData.value.category?.trim() || '其他',
      city: createFormData.value.city?.trim() || '未填写',
      salary_min: Number(createFormData.value.salary_min) || 0,
      salary_max: Number(createFormData.value.salary_max) || 0,
      personality_requirements: {
        psychological_focus: createFormData.value.psychological_focus,
      },
      required_traits: {}
    })
    
    if (response.data) {
      ElMessage.success('岗位创建成功！')
      showCreateDialog.value = false
      resetCreateForm()
      // 重新加载岗位列表
      await loadJobs()
    }
  } catch (error: any) {
    console.error('创建岗位失败:', error)
    const detail = error.response?.data?.detail || error.message || '未知错误'
    ElMessage.error(`创建岗位失败: ${detail}`)
  }
}

const resetCreateForm = () => {
  // ✅ 修正4：重置为纯净空字符串
  createFormData.value = {
    name: '',
    description: '',
    company: '',
    category: '',
    city: '',
    salary_min: '',
    salary_max: '',
    psychological_focus: []
  }
}

const handleEditJob = (job: any) => {
  // ✅ 修正5：修复模板字符串（原错误：混合引号+反引号）
  ElMessage.info(`编辑岗位: ${job.name}（功能开发中）`)
}

const handleDeleteJob = async (job: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除岗位 "${job.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteJob(job.id)
    ElMessage.success('岗位已删除')
    await loadJobs()
  } catch (e: any) {
    if (e === 'cancel' || e?.toString() === 'cancel') return
    ElMessage.error('删除失败：' + (e.response?.data?.detail || e.message || '未知错误'))
  }
}

const handleViewReport = (job: any) => {
  router.push({
    path: '/home/candidates',
    query: {
      job_id: String(job.id),
      status: 'completed',
    },
  })
}

const handleCreateShortcut = () => {
  showCreateDialog.value = true
}

const handleOpenJobManage = () => {
  router.push('/home/job-manage')
}

const handleOpenAnalytics = () => {
  router.push('/home/analytics')
}

function getPsychFocusLabels(job: any) {
  const requirements = job?.personality_requirements || {}
  if (Array.isArray(requirements.focus_labels) && requirements.focus_labels.length) {
    return requirements.focus_labels.slice(0, 3)
  }
  if (Array.isArray(requirements.psychological_focus)) {
    return requirements.psychological_focus
      .map((value: string) => psychologicalFocusOptions.find(item => item.value === value)?.label)
      .filter(Boolean)
      .slice(0, 3)
  }
  return []
}

const handleJumpReportQueue = () => {
  activeTab.value = 'candidates'
}

const handleJobsPageChange = (page: number) => {
  jobsPage.value = page
  loadJobs()
}

const handleJobsPageSizeChange = (size: number) => {
  jobsPageSize.value = size
  jobsPage.value = 1
  loadJobs()
}

// ==================== 候选人管理 ====================
const activeTab = ref('jobs')
const candidateList = ref<any[]>([])
const candidateLoading = ref(false)
const candidateTotal = ref(0)
const candidateFilter = ref({ jobId: '', status: '' })
const selectedReport = ref<any>(null)
const showReportDialog = ref(false)
const reportLoading = ref(false)

// 从岗位列表中提取岗位选项
const jobOptions = computed(() => jobsList.value.map(j => ({ label: j.name, value: j.id })))

async function loadCandidates() {
  try {
    candidateLoading.value = true
    const params = new URLSearchParams()
    if (candidateFilter.value.jobId) params.append('job_id', candidateFilter.value.jobId)
    if (candidateFilter.value.status) params.append('status', candidateFilter.value.status)
    params.append('limit', '50')

    const res = await request.get('/assessment/hr/candidates', {
      params: Object.fromEntries(params.entries()),
    })
    const data = res.data
    if (data.code === 200 && data.data) {
      candidateList.value = data.data.items || []
      candidateTotal.value = data.data.total || 0
    }
  } catch (e) {
    console.error('加载候选人列表失败:', e)
    ElMessage.error('加载候选人列表失败')
  } finally {
    candidateLoading.value = false
  }
}

function handleFilterChange() {
  loadCandidates()
}

async function viewCandidateReport(row: any) {
  try {
    reportLoading.value = true
    showReportDialog.value = true
    selectedReport.value = null

    const res = await request.get(`/assessment/report/${row.record_id}`)
    const data = res.data
    if (data.code === 200 && data.data) {
      selectedReport.value = data.data
    } else {
      ElMessage.error('获取报告失败')
    }
  } catch (e) {
    console.error('获取报告失败:', e)
    ElMessage.error('获取报告失败')
  } finally {
    reportLoading.value = false
  }
}

function goToFullReport(recordId: number) {
  showReportDialog.value = false
  router.push(`/home/report/${recordId}`)
}

function getStatusType(status: string) {
  return status === 'completed' ? 'success' : status === 'pending' ? 'warning' : 'info'
}
function getStatusText(status: string) {
  return status === 'completed' ? '已完成' : status === 'pending' ? '进行中' : status
}
function getScoreColor(score: number | null) {
  if (!score) return '#909399'
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

function handleTabChange(tab: string) {
  if (tab === 'candidates' && candidateList.value.length === 0) {
    loadCandidates()
  }
}

onMounted(() => {
  loadJobs()
})
</script>

<template>
  <div class="hr-home">
    <div class="page-header">
      <div>
        <h2>岗位管理仪表盘</h2>
        <p>数据驱动招聘决策，快速掌握岗位与评估进展。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleCreateShortcut">一键创建岗位</el-button>
        <el-button :icon="ArrowRight" @click="handleJumpReportQueue">查看待处理报告</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="hr-tabs" @tab-change="handleTabChange">
      <!-- ==================== 岗位管理 Tab ==================== -->
      <el-tab-pane label="岗位管理" name="jobs">
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-label">在招岗位</div>
            <div class="kpi-value">{{ stats.openJobs }}</div>
            <div class="kpi-foot">总岗位 {{ stats.totalJobs }}</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">投递总量</div>
            <div class="kpi-value">{{ stats.totalSubmissions }}</div>
            <div class="kpi-foot">实时更新</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">平均匹配度</div>
            <div class="kpi-value">{{ stats.avgMatchScore }}%</div>
            <div class="kpi-foot">近30天平均</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">待处理报告</div>
            <div class="kpi-value">{{ stats.pendingReports }}</div>
            <div class="kpi-foot">需重点关注</div>
          </div>
        </div>

        <div class="dashboard-layout">
          <div class="dashboard-main">
            <div class="section-header">
              <div>
                <h3>重点岗位看板</h3>
                <span class="section-hint">首页聚焦优先处理项，完整明细请前往岗位管理页</span>
              </div>
              <el-button type="primary" plain @click="handleOpenJobManage">进入岗位管理</el-button>
            </div>

            <div class="job-spotlight-grid" v-loading="loading">
              <template v-if="featuredJobs.length > 0">
                <article v-for="job in featuredJobs" :key="job.id" class="spotlight-card">
                  <div class="spotlight-header">
                    <div>
                      <h4>{{ job.name }}</h4>
                      <p>{{ job.company || '未填写公司' }} · {{ job.city || '未填写城市' }}</p>
                    </div>
                    <span class="status-pill" :class="job.status">{{ getStatusText(job.status) }}</span>
                  </div>

                  <div class="spotlight-metrics">
                    <div class="spotlight-metric">
                      <span>投递</span>
                      <strong>{{ job.submissions }}</strong>
                    </div>
                    <div class="spotlight-metric">
                      <span>待处理</span>
                      <strong :class="{ warning: job.pendingReports > 0 }">{{ job.pendingReports }}</strong>
                    </div>
                    <div class="spotlight-metric">
                      <span>心理侧重</span>
                      <strong>{{ getPsychFocusLabels(job).length || 0 }}</strong>
                    </div>
                  </div>

                  <div class="match-summary">
                    <div class="match-summary-top">
                      <span>平均匹配度</span>
                      <span>{{ job.avgMatch }}%</span>
                    </div>
                    <el-progress :percentage="job.avgMatch" :stroke-width="8" :show-text="false" color="#1d4ed8" />
                  </div>

                  <div class="psych-tags">
                    <span class="psych-tags-label">心理侧重点</span>
                    <template v-if="getPsychFocusLabels(job).length">
                      <el-tag
                        v-for="label in getPsychFocusLabels(job)"
                        :key="label"
                        size="small"
                        type="info"
                        effect="plain"
                      >
                        {{ label }}
                      </el-tag>
                    </template>
                    <span v-else class="psych-empty">暂未配置</span>
                  </div>

                  <div class="spotlight-actions">
                    <el-button link type="primary" :icon="View" @click="handleViewReport(job)">查看报告</el-button>
                    <el-button link type="warning" :icon="Edit" @click="handleOpenJobManage">管理岗位</el-button>
                  </div>

                  <div class="spotlight-foot">
                    <span>更新日期</span>
                    <strong>{{ new Date(job.updated_at).toLocaleDateString('zh-CN') }}</strong>
                  </div>
                </article>
              </template>

              <div v-else class="empty-state large-empty">暂无岗位</div>
            </div>
          </div>

          <div class="dashboard-side">
            <div class="side-card">
              <h4>待处理优先队列</h4>
              <div v-if="priorityJobs.length === 0" class="empty-state">当前没有需要优先处理的岗位</div>
              <button
                v-for="job in priorityJobs"
                :key="job.id"
                class="priority-item"
                @click="handleViewReport(job)"
              >
                <div>
                  <div class="priority-name">{{ job.name }}</div>
                  <div class="priority-meta">{{ job.pendingReports }} 份待处理 · {{ job.submissions }} 份投递</div>
                </div>
                <span class="priority-badge">{{ job.pendingReports }}</span>
              </button>
            </div>

            <div class="side-card">
              <h4>招聘洞察</h4>
              <div class="insight-item">
                <span>投递最热</span>
                <strong>{{ topApplicationJob?.name || '暂无数据' }}</strong>
              </div>
              <div class="insight-item">
                <span>匹配最佳</span>
                <strong>{{ topMatchJob?.name || '暂无数据' }}</strong>
              </div>
              <div class="insight-item">
                <span>待处理集中</span>
                <strong>{{ priorityJobs[0]?.name || '暂无积压' }}</strong>
              </div>
            </div>

            <div class="side-card">
              <h4>快捷入口</h4>
              <el-button class="action-btn" type="primary" plain block @click="activeTab = 'candidates'">查看所有候选人报告</el-button>
              <el-button class="action-btn" type="warning" plain block @click="handleOpenJobManage">进入岗位管理页</el-button>
              
              <el-button class="action-btn" type="info" plain block @click="handleOpenAnalytics">数据分析中心</el-button>
            </div>

            <div class="side-card">
              <h4>最新岗位</h4>
              <div v-if="jobsList.length === 0" class="empty-state">暂无岗位</div>
              <div v-for="job in recentJobs" :key="job.id" class="recent-item">
                <div class="recent-title">{{ job.name }}</div>
                <div class="recent-meta">{{ new Date(job.updated_at).toLocaleDateString('zh-CN') }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ==================== 候选人管理 Tab ==================== -->
      <el-tab-pane label="候选人管理" name="candidates">
        <div class="candidate-toolbar">
          <el-select v-model="candidateFilter.jobId" placeholder="按岗位筛选" clearable style="width: 200px" @change="handleFilterChange">
            <el-option v-for="opt in jobOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-select v-model="candidateFilter.status" placeholder="按状态筛选" clearable style="width: 160px" @change="handleFilterChange">
            <el-option label="已完成" value="completed" />
            <el-option label="进行中" value="pending" />
          </el-select>
          <el-button :icon="ArrowRight" @click="loadCandidates">刷新</el-button>
          <span class="candidate-count">共 {{ candidateTotal }} 位候选人</span>
        </div>

        <el-table :data="candidateList" v-loading="candidateLoading" stripe style="width: 100%" empty-text="暂无候选人评估记录">
          <el-table-column prop="candidate_name" label="候选人" min-width="120">
            <template #default="{ row }">
              <div class="candidate-name-cell">
                <el-icon :size="16" color="#409eff"><User /></el-icon>
                <span>{{ row.candidate_name || '未知' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="candidate_email" label="邮箱" min-width="180" />
          <el-table-column prop="job_title" label="应聘岗位" min-width="140" />
          <el-table-column label="匹配度" min-width="150" sortable>
            <template #default="{ row }">
              <div v-if="row.match_score != null" class="score-cell">
                <el-progress
                  :percentage="Math.round(row.match_score)"
                  :stroke-width="10"
                  :color="getScoreColor(row.match_score)"
                  style="flex: 1"
                />
                <span class="score-num" :style="{ color: getScoreColor(row.match_score) }">{{ Math.round(row.match_score) }}%</span>
              </div>
              <el-tag v-else type="info" size="small">未评分</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.assessment_status)" size="small">{{ getStatusText(row.assessment_status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="评估时间" min-width="140" sortable>
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleDateString('zh-CN') }}
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" :icon="Document" @click="viewCandidateReport(row)" :disabled="row.assessment_status !== 'completed'">
                查看报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 候选人报告预览弹窗 -->
    <el-dialog v-model="showReportDialog" title="候选人评估报告" width="680px" top="5vh">
      <div v-if="reportLoading" class="report-loading">
        <el-icon class="is-loading" :size="32"><ArrowRight /></el-icon>
        <p>正在加载报告…</p>
      </div>
      <div v-else-if="selectedReport" class="report-preview">
        <div class="report-section">
          <h4>基本信息</h4>
          <div class="report-info-grid">
            <div><span class="label">候选人：</span>{{ selectedReport.candidate_name || '—' }}</div>
            <div><span class="label">应聘岗位：</span>{{ selectedReport.job_title || '—' }}</div>
            <div><span class="label">评估模式：</span>{{ selectedReport.assessment_mode || '—' }}</div>
            <div><span class="label">评估时间：</span>{{ selectedReport.created_at ? new Date(selectedReport.created_at).toLocaleDateString('zh-CN') : '—' }}</div>
          </div>
        </div>

        <div class="report-section" v-if="selectedReport.match_score != null">
          <h4>匹配得分</h4>
          <div class="big-score" :style="{ color: getScoreColor(selectedReport.match_score) }">
            {{ Math.round(selectedReport.match_score) }}<small>%</small>
          </div>
          <el-progress :percentage="Math.round(selectedReport.match_score)" :stroke-width="14" :color="getScoreColor(selectedReport.match_score)" />
        </div>

        <div class="report-section" v-if="selectedReport.personality_traits">
          <h4>性格特质</h4>
          <div class="trait-list">
            <div v-for="(val, key) in selectedReport.personality_traits" :key="key" class="trait-item">
              <span class="trait-label">{{ key }}</span>
              <el-progress :percentage="Math.round(val * 100)" :stroke-width="8" :show-text="true" />
            </div>
          </div>
        </div>

        <div class="report-section" v-if="selectedReport.strengths?.length">
          <h4>优势</h4>
          <ul class="report-list success">
            <li v-for="(s, i) in selectedReport.strengths" :key="i">{{ s }}</li>
          </ul>
        </div>
        <div class="report-section" v-if="selectedReport.gaps?.length">
          <h4>待提升</h4>
          <ul class="report-list warning">
            <li v-for="(g, i) in selectedReport.gaps" :key="i">{{ g }}</li>
          </ul>
        </div>
        <div class="report-section" v-if="selectedReport.recommendations?.length">
          <h4>建议</h4>
          <ul class="report-list info">
            <li v-for="(r, i) in selectedReport.recommendations" :key="i">{{ r }}</li>
          </ul>
        </div>
      </div>
      <div v-else class="report-empty">暂无报告数据</div>
      <template #footer>
        <el-button @click="showReportDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCreateDialog" title="创建新岗位" width="500px">
      <el-form :model="createFormData" label-width="100px">
        <el-form-item label="岗位名称" required>
          <el-input v-model="createFormData.name" placeholder="请输入岗位名称" />
        </el-form-item>
        <el-form-item label="岗位描述" required>
          <el-input
            v-model="createFormData.description"
            placeholder="请输入岗位描述"
            type="textarea"
            rows="3"
          />
        </el-form-item>
        <el-form-item label="所属公司">
          <el-input v-model="createFormData.company" placeholder="请输入公司名称" />
        </el-form-item>
        <el-form-item label="岗位类别">
          <el-select v-model="createFormData.category" placeholder="请选择岗位类别">
            <el-option label="技术" value="技术" />
            <el-option label="产品" value="产品" />
            <el-option label="设计" value="设计" />
            <el-option label="运营" value="运营" />
            <el-option label="销售" value="销售" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作城市">
          <el-select v-model="createFormData.city" placeholder="请选择城市">
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="深圳" value="深圳" />
            <el-option label="杭州" value="杭州" />
            <el-option label="南京" value="南京" />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资范围(k)">
          <el-input-number v-model.number="createFormData.salary_min" placeholder="最低" />
          <span style="margin: 0 10px">-</span>
          <el-input-number v-model.number="createFormData.salary_max" placeholder="最高" />
        </el-form-item>
        <el-form-item label="心理侧重点">
          <div class="psych-focus-panel">
            <p class="psych-focus-tip">
              选择 2-3 个岗位行为特征，系统将在后端转换为岗位心理特质要求。
            </p>
            <el-checkbox-group v-model="createFormData.psychological_focus" class="psych-focus-options">
              <el-checkbox
                v-for="item in psychologicalFocusOptions"
                :key="item.value"
                :label="item.value"
                border
              >
                <span class="psych-focus-title">{{ item.label }}</span>
                <span class="psych-focus-hint">{{ item.hint }}</span>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateJob">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.hr-home {
  --hr-primary: #2563eb;
  --hr-border: rgba(214, 223, 240, 0.92);
  --hr-surface: rgba(255, 255, 255, 0.92);
  --hr-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
  min-height: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 28px 30px;
  border-radius: 24px;
  border: 1px solid var(--hr-border);
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.12), transparent 26%),
    linear-gradient(135deg, rgba(239, 246, 255, 0.96), rgba(255, 255, 255, 0.94));
  box-shadow: var(--hr-shadow);
}

.page-header h2 {
  margin: 0 0 10px 0;
  font-size: 30px;
  line-height: 1.15;
  color: #0f172a;
  letter-spacing: -0.03em;
}

.page-header p {
  margin: 0;
  max-width: 720px;
  color: #526071;
  font-size: 15px;
  line-height: 1.75;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.page-header :deep(.el-button) {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  font-weight: 600;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 15px;
}

.kpi-card {
  position: relative;
  overflow: hidden;
  min-height: 104px;
  padding: 18px 18px 16px;
  border-radius: 16px;
  border: 1px solid var(--hr-border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 251, 255, 0.96));
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.045);
  display: grid;
  grid-template-rows: auto 1fr auto;
}

.kpi-card::before {
  content: '';
  position: absolute;
  left: 24px;
  top: 20px;
  width: 34px;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
}

.kpi-card:nth-child(2)::before {
  background: linear-gradient(90deg, #0f766e, #34d399);
}

.kpi-card:nth-child(3)::before {
  background: linear-gradient(90deg, #1d4ed8, #38bdf8);
}

.kpi-card:nth-child(4)::before {
  background: linear-gradient(90deg, #d97706, #f59e0b);
}

.kpi-label {
  margin-top: 14px;
  font-size: 13px;
  color: #64748b;
  font-weight: 700;
}

.kpi-value {
  margin-top: 10px;
  font-size: 32px;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #0f172a;
}

.kpi-foot {
  margin-top: 12px;
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
}
.kpi-card::after {
  content: '';
  position: absolute;
  right: -36px;
  top: -36px;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.08);
  pointer-events: none;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 22px;
}

.dashboard-main {
  border-radius: 18px;
  border: 1px solid var(--hr-border);
  padding: 20px;
  background: var(--hr-surface);
  box-shadow: var(--hr-shadow);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 18px;
}

.section-header h3 {
  margin: 0;
  font-size: 22px;
  color: #0f172a;
}

.section-hint {
  display: inline-flex;
  margin-top: 8px;
  color: #7c8aa0;
  font-size: 13px;
  line-height: 1.7;
}

.job-spotlight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 14px;
}

.spotlight-card {
  position: relative;
  border: 1px solid rgba(191, 219, 254, 0.95);
  border-radius: 16px;
  padding: 16px 16px 14px;
  background:
    linear-gradient(90deg, rgba(37, 99, 235, 0.08), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #ffffff 58%, #f8fafc 100%);
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
  box-shadow: 0 10px 24px rgba(30, 64, 175, 0.07);
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.spotlight-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  border-radius: 16px 0 0 16px;
  background: linear-gradient(180deg, #2563eb, #38bdf8);
}

.spotlight-card:hover {
  transform: translateY(-2px);
  border-color: rgba(147, 197, 253, 0.95);
  box-shadow: 0 16px 30px rgba(37, 99, 235, 0.1);
}

.spotlight-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.spotlight-header h4 {
  margin: 0;
  font-size: 16px;
  line-height: 1.4;
  color: #0f172a;
}

.spotlight-header p {
  margin: 6px 0 0;
  font-size: 13px;
  color: #64748b;
}

.status-pill {
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #1d4ed8;
  background: #dbeafe;
  white-space: nowrap;
}

.status-pill.draft {
  color: #92400e;
  background: #fef3c7;
}

.spotlight-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.spotlight-metric {
  min-width: 0;
  padding: 10px;
  border-radius: 12px;
  background: rgba(239, 246, 255, 0.74);
  border: 1px solid rgba(219, 234, 254, 0.9);
}

.spotlight-metric span {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
}

.spotlight-metric strong {
  display: block;
  font-size: 16px;
  line-height: 1.25;
  color: #0f172a;
  word-break: keep-all;
  white-space: nowrap;
}

.spotlight-metric strong.warning {
  color: #d97706;
}

.match-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.match-summary-top {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.psych-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 54px;
}

.psych-tags-label {
  width: 100%;
  font-size: 12px;
  color: #64748b;
}

.psych-empty {
  font-size: 12px;
  color: #94a3b8;
}

.spotlight-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding-top: 2px;
  margin-top: auto;
}

.spotlight-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(226, 232, 240, 0.9);
  font-size: 12px;
  color: #64748b;
}

.spotlight-foot strong {
  color: #334155;
  font-weight: 700;
}

.dashboard-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-card {
  border-radius: 16px; /* 稍微收紧圆角，和系统圆角统一 */
  border: none; /* 去掉生硬边框，用阴影和背景区分 */
  padding: 20px; 
  background: linear-gradient(145deg, #f9faff, #eef1ff); /* 轻微渐变，更柔和 */
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.08); /* 蓝紫色系轻柔阴影 */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.side-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.12);
}

.side-card h4 {
  margin: 0 0 16px 0;
  font-size: 17px;
  font-weight: 600;
  color: #1e1e2f; 
}

.side-card .action-btn {
  margin-bottom: 12px; /* 增加按钮间距 */
  font-weight: 500;
  border-radius: 12px; /* 圆角按钮 */
  height: 42px; /* 高度统一 */
  font-size: 14px;
  box-shadow: none; /* 去掉默认阴影 */
  transition: all 0.2s ease;
}

.side-card .action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.1);
}

/* 不同类型按钮渐变色优化 */
.side-card .el-button--primary {
  background: linear-gradient(90deg, #4f46e5, #6366f1);
  color: #fff;
  border: none;
}

.side-card .el-button--warning {
  background: linear-gradient(90deg, #facc15, #fcd34d);
  color: #1f2937;
  border: none;
}


.side-card .el-button--info {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  border: none;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #374151;
  padding: 6px 0;
}

.priority-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 0;
  border: none;
  background: transparent;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  text-align: left;
  transition: transform 0.2s ease;
}

.priority-item:hover {
  transform: translateX(2px);
}

.priority-item:last-child {
  border-bottom: none;
}

.priority-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.priority-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #7c8aa0;
}

.priority-badge {
  min-width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #fff7ed;
  color: #c2410c;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.insight-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  font-size: 13px;
  color: #64748b;
}

.insight-item strong {
  color: #0f172a;
  text-align: right;
  max-width: 55%;
}

/* .action-btn {
  margin-bottom: 8px "'!important;
  font-size: 13px;
} */

.empty-state {
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

.large-empty {
  grid-column: 1 / -1;
  padding: 48px 0;
}

.recent-item {
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-title {
  font-size: 14px;
  color: #0f172a;
}

.recent-meta {
  font-size: 12px;
  color: #7c8aa0;
  margin-top: 4px;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 22px 18px;
  }

  .page-header h2 {
    font-size: 25px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .spotlight-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .job-spotlight-grid {
    grid-template-columns: 1fr;
  }

  .spotlight-actions {
    flex-wrap: wrap;
    justify-content: flex-start;
  }

  .candidate-toolbar {
    padding: 16px;
  }

  .candidate-count {
    margin-left: 0;
  }
}

/* ==================== 候选人管理 Tab ==================== */
.hr-tabs {
  flex: 1;
}

.hr-tabs :deep(.el-tabs__header) {
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--hr-border);
  border-radius: 20px;
  padding: 4px 14px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
  margin-bottom: 20px;
}

.hr-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  height: 46px;
  line-height: 46px;
  font-weight: 600;
}

.hr-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
}

.hr-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.candidate-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--hr-border);
  border-radius: 18px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.candidate-count {
  margin-left: auto;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.candidate-name-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-num {
  font-weight: 700;
  font-size: 14px;
  min-width: 40px;
  text-align: right;
}

.hr-tabs :deep(.el-table) {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--hr-border);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.hr-tabs :deep(.el-table th.el-table__cell) {
  background: #f8fbff;
  color: #526071;
  font-weight: 700;
}

.hr-tabs :deep(.el-table__row:hover > td.el-table__cell) {
  background: #f8fbff !important;
}

/* ==================== 报告预览弹窗 ==================== */
.report-loading {
  text-align: center;
  padding: 40px 0;
  color: #6b7280;
}

.report-preview {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 4px;
}

.report-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.report-section:last-child {
  border-bottom: none;
}

.report-section h4 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #0f172a;
}

.report-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 14px;
  color: #374151;
}

.report-info-grid .label {
  color: #6b7280;
}

.big-score {
  font-size: 48px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 12px;
}

.big-score small {
  font-size: 20px;
  font-weight: 500;
}

.trait-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trait-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trait-label {
  min-width: 80px;
  font-size: 14px;
  color: #374151;
  text-transform: capitalize;
}

.report-list {
  padding-left: 18px;
  margin: 0;
}

.report-list li {
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.6;
}

.report-list.success li::marker { color: #67c23a; }
.report-list.warning li::marker { color: #e6a23c; }
.report-list.info li::marker { color: #409eff; }

.report-empty {
  text-align: center;
  color: #94a3b8;
  padding: 40px 0;
}

.psych-focus-panel {
  width: 100%;
}

.psych-focus-tip {
  margin: 0 0 10px;
  font-size: 12px;
  line-height: 1.6;
  color: #64748b;
}

.psych-focus-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.psych-focus-options :deep(.el-checkbox.is-bordered) {
  height: auto;
  margin-right: 0;
  padding: 9px 12px;
  border-radius: 8px;
}

.psych-focus-options :deep(.el-checkbox__label) {
  display: inline-flex;
  flex-direction: column;
  gap: 3px;
  line-height: 1.4;
}

.psych-focus-title {
  font-size: 13px;
  color: #1f2937;
  font-weight: 600;
}

.psych-focus-hint {
  font-size: 12px;
  color: #94a3b8;
}
</style>
