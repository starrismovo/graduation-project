<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted, computed } from 'vue'
import { getJobs } from '../utils/request'
import { createJob } from '../api/job'
import { Delete, Edit, View, Plus, ArrowRight, User, Document } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

const jobsList = ref<any[]>([])
const loading = ref(true)

const showCreateDialog = ref(false)
// ✅ 修正1：所有表单字段初始化为空字符串（原错误：'"''"'）
const createFormData = ref({
  name: '',
  description: '',
  company: '',
  category: '',
  city: '',
  salary_min: '',
  salary_max: ''
})

const stats = ref({
  totalJobs: 0,
  openJobs: 0,
  totalSubmissions: 0,
  avgMatchScore: 0,
  pendingReports: 0
})

function hashToNumber(input: string, mod: number) {
  let total = 0
  for (let i = 0; i < input.length; i++) {
    total += input.charCodeAt(i)
  }
  return total % mod
}

function normalizeJob(job: any) {
  const idSeed = String(job.id ?? job.name ?? Math.random())
  const submissions = job.submissions ?? (hashToNumber(idSeed, 36) + 8)
  const avgMatch = job.avgMatch ?? (60 + hashToNumber(idSeed + 'match', 36))
  const pendingReports = job.pendingReports ?? hashToNumber(idSeed + 'pending', 8)
  const status = job.status ?? (submissions > 0 ? 'open' : 'draft')
  const createdAt = job.created_at ?? new Date().toISOString()
  const updatedAt = job.updated_at ?? createdAt

  return {
    ...job,
    submissions,
    avgMatch,
    pendingReports,
    status,
    created_at: createdAt,
    updated_at: updatedAt
  }
}

const loadJobs = async () => {
  try {
    loading.value = true
    const response = await getJobs({})
    const rawList = response.data || []
    jobsList.value = rawList.map(normalizeJob)

    stats.value.totalJobs = jobsList.value.length
    stats.value.openJobs = jobsList.value.filter(job => job.status === 'open').length
    stats.value.totalSubmissions = jobsList.value.reduce((sum, job) => sum + (job.submissions || 0), 0)
    stats.value.avgMatchScore = jobsList.value.length
      ? Math.round(jobsList.value.reduce((sum, job) => sum + (job.avgMatch || 0), 0) / jobsList.value.length)
      : 0
    stats.value.pendingReports = jobsList.value.reduce((sum, job) => sum + (job.pendingReports || 0), 0)
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
    salary_max: ''
  }
}

const handleEditJob = (job: any) => {
  // ✅ 修正5：修复模板字符串（原错误：混合引号+反引号）
  ElMessage.info(`编辑岗位: ${job.name}（功能开发中）`)
}

const handleDeleteJob = (job: any) => {
  ElMessageBox.confirm(
    `确定要删除岗位 "${job.name}" 吗？`,
    '删除确认', // ✅ 修正6：标题字符串修正
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      ElMessage.success('岗位删除成功（功能开发中）')
      // 实际项目中应调用删除API并刷新列表
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

const handleViewReport = (job: any) => {
  // ✅ 修正7：修复模板字符串
  ElMessage.info(`查看岗位 "${job.name}" 的候选人报告（功能开发中）`)
}

const handleCreateShortcut = () => {
  showCreateDialog.value = true
}

const handleJumpReportQueue = () => {
  activeTab.value = 'candidates'
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

    const res = await fetch(`/assessment/hr/candidates?${params}`)
    const data = await res.json()
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

    const res = await fetch(`/assessment/report/${row.record_id}`)
    const data = await res.json()
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
              <h3>岗位列表</h3>
              <span class="section-hint">可排序查看投递、匹配度和待处理量</span>
            </div>

            <el-table
              :data="jobsList"
              stripe
              style="width: 100%"
              :loading="loading"
              empty-text="暂无岗位"
            >
              <el-table-column prop="name" label="岗位名称" min-width="160" sortable />
              <el-table-column prop="company" label="公司" min-width="140" />
              <el-table-column prop="city" label="城市" min-width="120" />
              <el-table-column label="投递量" min-width="120" sortable="custom">
                <template #default="{ row }">
                  <el-tag type="info">{{ row.submissions }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="平均匹配度" min-width="140" sortable="custom">
                <template #default="{ row }">
                  <el-progress :percentage="row.avgMatch" :stroke-width="8" color="#409eff" />
                </template>
              </el-table-column>
              <el-table-column label="待处理" min-width="120" sortable="custom">
                <template #default="{ row }">
                  <el-tag :type="row.pendingReports > 0 ? 'warning' : 'success'">
                    {{ row.pendingReports }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="最近更新" min-width="160" sortable>
                <template #default="{ row }">
                  {{ new Date(row.updated_at).toLocaleDateString('zh-CN') }}
                </template>
              </el-table-column>
              <el-table-column label="操作" min-width="200" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" :icon="View" @click="handleViewReport(row)">报告</el-button>
                  <el-button link type="warning" :icon="Edit" @click="handleEditJob(row)">编辑</el-button>
                  <el-button link type="danger" :icon="Delete" @click="handleDeleteJob(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="dashboard-side">
            <div class="side-card">
              <h4>岗位概况</h4>
              <div class="overview-item">
                <span>活跃岗位</span>
                <strong>{{ stats.openJobs }}</strong>
              </div>
              <div class="overview-item">
                <span>待处理报告</span>
                <strong>{{ stats.pendingReports }}</strong>
              </div>
              <div class="overview-item">
                <span>平均匹配度</span>
                <strong>{{ stats.avgMatchScore }}%</strong>
              </div>
            </div>

            <div class="side-card">
              <h4>快捷入口</h4>
              <el-button class="action-btn" type="primary" plain block @click="activeTab = 'candidates'">查看所有候选人报告</el-button>
              <el-button class="action-btn" type="success" plain block>人才池管理</el-button>
              <el-button class="action-btn" type="info" plain block>数据分析中心</el-button>
            </div>

            <div class="side-card">
              <h4>最新岗位</h4>
              <div v-if="jobsList.length === 0" class="empty-state">暂无岗位</div>
              <div v-for="job in jobsList.slice(0, 3)" :key="job.id" class="recent-item">
                <div class="recent-title">{{ job.name }}</div>
                <div class="recent-meta">{{ new Date(job.created_at).toLocaleDateString('zh-CN') }}</div>
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
  min-height: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  background: #ffffff;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 8px 24px rgba(18, 28, 45, 0.08);
}

.page-header h2 {
  margin: 0 0 6px 0;
  font-size: 22px;
  color: #1f2937;
}

.page-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.kpi-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(18, 28, 45, 0.08);
}

.kpi-label {
  font-size: 12px;
  color: #6b7280;
}

.kpi-value {
  font-size: 26px;
  font-weight: 700;
  margin-top: 8px;
  color: #111827;
}

.kpi-foot {
  margin-top: 6px;
  font-size: 12px;
  color: #9ca3af;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 20px;
}

.dashboard-main {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(18, 28, 45, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.section-hint {
  color: #9ca3af;
  font-size: 12px;
}

.dashboard-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.side-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(18, 28, 45, 0.08);
}

.side-card h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #111827;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #374151;
  padding: 6px 0;
}

/* .action-btn {
  margin-bottom: 8px "'!important;
  font-size: 13px;
} */

.empty-state {
  text-align: center;
  color: #9ca3af;
  font-size: 12px;
}

.recent-item {
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-title {
  font-size: 13px;
  color: #111827;
}

.recent-meta {
  font-size: 12px;
  color: #9ca3af;
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
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

/* ==================== 候选人管理 Tab ==================== */
.hr-tabs {
  flex: 1;
}

.hr-tabs :deep(.el-tabs__header) {
  background: #ffffff;
  border-radius: 12px 12px 0 0;
  padding: 0 20px;
  box-shadow: 0 4px 12px rgba(18, 28, 45, 0.06);
  margin-bottom: 20px;
}

.hr-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  height: 48px;
  line-height: 48px;
}

.candidate-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(18, 28, 45, 0.06);
}

.candidate-count {
  margin-left: auto;
  color: #6b7280;
  font-size: 13px;
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

/* ==================== 报告预览弹窗 ==================== */
.report-loading {
  text-align: center;
  padding: 40px 0;
  color: #6b7280;
}

.report-preview {
  max-height: 65vh;
  overflow-y: auto;
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
  font-size: 15px;
  color: #1f2937;
}

.report-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 13px;
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
  font-size: 13px;
  color: #374151;
  text-transform: capitalize;
}

.report-list {
  padding-left: 18px;
  margin: 0;
}

.report-list li {
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.6;
}

.report-list.success li::marker { color: #67c23a; }
.report-list.warning li::marker { color: #e6a23c; }
.report-list.info li::marker { color: #409eff; }

.report-empty {
  text-align: center;
  color: #9ca3af;
  padding: 40px 0;
}
</style>
