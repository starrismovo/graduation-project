<template>
  <div class="job-management-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">岗位管理</h1>
          <p class="page-subtitle">管理招聘岗位，监控投递数据，优化招聘流程</p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" @click="handleRefresh">
            <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span>刷新数据</span>
          </button>
          <button class="btn-primary" @click="handleCreateJob">
            <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
            <span>创建岗位</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <!-- 开放岗位数 -->
      <div class="stat-card stat-primary">
        <div class="stat-icon-wrapper primary">
          <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">开放岗位</div>
          <div class="stat-value">{{ stats.openJobs }}</div>
          <div class="stat-meta">
            <span>我发布的岗位</span>
          </div>
        </div>
      </div>

      <!-- 总投递数 -->
      <div class="stat-card stat-info">
        <div class="stat-icon-wrapper info">
          <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">总投递数</div>
          <div class="stat-value">{{ stats.totalApplications }}</div>
          <div class="stat-meta">
            <span>面试总场次</span>
          </div>
        </div>
      </div>

      <!-- 平均匹配度 -->
      <div class="stat-card stat-success">
        <div class="stat-icon-wrapper success">
          <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">平均匹配度</div>
          <div class="stat-value">{{ stats.avgMatchRate }}%</div>
          <div class="stat-meta">
            <span>已完成评估均值</span>
          </div>
        </div>
      </div>

      <!-- 待处理报告 -->
      <div class="stat-card stat-warning">
        <div class="stat-icon-wrapper warning">
          <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">待处理报告</div>
          <div class="stat-value">{{ stats.pendingReports }}</div>
          <div class="stat-meta">
            <span>需要尽快处理</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 岗位列表区域 -->
    <div class="jobs-section">
      <div class="section-header">
        <h2 class="section-title">岗位列表</h2>
        <div class="section-controls">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
            <input 
              type="text" 
              placeholder="搜索岗位名称..." 
              v-model="searchQuery"
              class="search-input"
            />
          </div>
          <el-select v-model="sortBy" placeholder="排序方式" class="sort-select" size="default">
            <el-option label="最新发布" value="latest" />
            <el-option label="投递最多" value="applications" />
            <el-option label="匹配度最高" value="match" />
          </el-select>
        </div>
      </div>

      <div class="jobs-table" v-loading="loading">
        <div class="table-header">
          <div class="col-job">岗位信息</div>
          <div class="col-status">状态</div>
          <div class="col-applications">投递数</div>
          <div class="col-match">平均匹配度</div>
          <div class="col-reports">待处理报告</div>
          <div class="col-actions">操作</div>
        </div>

        <div class="table-body">
          <div 
            v-for="job in filteredJobs" 
            :key="job.id" 
            class="table-row"
            @click="handleJobClick(job)"
          >
            <div class="col-job">
              <div class="job-info">
                <div class="job-title">{{ job.name }}</div>
                <div class="job-meta">
                  <span class="job-department">{{ job.category }}</span>
                  <span class="job-separator">·</span>
                  <span class="job-location">{{ job.city }}</span>
                  <span class="job-separator">·</span>
                  <span class="job-date">{{ job.salary_min }}k - {{ job.salary_max }}k</span>
                </div>
              </div>
            </div>

            <div class="col-status">
              <span :class="['status-badge', job.status]">
                {{ getStatusText(job.status) }}
              </span>
            </div>

            <div class="col-applications">
              <div class="applications-count">
                <svg class="count-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                </svg>
                <span class="count-number">{{ job.applications }}</span>
              </div>
            </div>

            <div class="col-match">
              <div class="match-rate">
                <div class="match-bar">
                  <div 
                    class="match-fill" 
                    :style="{ width: job.avg_match_rate + '%' }"
                    :class="getMatchClass(job.avg_match_rate)"
                  ></div>
                </div>
                <span class="match-percentage">{{ job.avg_match_rate }}%</span>
              </div>
            </div>

            <div class="col-reports">
              <div class="reports-count" :class="{ highlight: job.pending_reports > 0 }">
                <svg class="reports-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <span>{{ job.pending_reports }}</span>
              </div>
            </div>

            <div class="col-actions">
              <button class="action-btn" @click.stop="handleViewReports(job)">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                </svg>
              </button>
              <button class="action-btn" @click.stop="handleEditJob(job)">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
              <button class="action-btn danger" @click.stop="handleDeleteJob(job)">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑岗位弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑岗位" width="500px" @close="showEditDialog = false">
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="岗位名称" required>
          <el-input v-model="editForm.name" placeholder="请输入岗位名称" />
        </el-form-item>
        <el-form-item label="岗位描述">
          <el-input v-model="editForm.description" type="textarea" rows="3" placeholder="岗位描述" />
        </el-form-item>
        <el-form-item label="所属公司">
          <el-input v-model="editForm.company" placeholder="公司名称" />
        </el-form-item>
        <el-form-item label="岗位类别">
          <el-select v-model="editForm.category" placeholder="请选择">
            <el-option label="技术" value="技术" />
            <el-option label="产品" value="产品" />
            <el-option label="设计" value="设计" />
            <el-option label="运营" value="运营" />
            <el-option label="销售" value="销售" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作城市">
          <el-select v-model="editForm.city" placeholder="请选择">
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="深圳" value="深圳" />
            <el-option label="杭州" value="杭州" />
            <el-option label="南京" value="南京" />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资范围(k)">
          <el-input-number v-model.number="editForm.salary_min" :min="0" placeholder="最低" />
          <span style="margin: 0 8px">-</span>
          <el-input-number v-model.number="editForm.salary_max" :min="0" placeholder="最高" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getHRJobList, deleteJob, updateJob } from '@/api/job'

const router = useRouter()

// ==================== 数据状态 ====================
const loading = ref(false)
const jobs = ref<any[]>([])
const totalJobs = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const stats = ref({
  openJobs: 0,
  totalApplications: 0,
  avgMatchRate: 0,
  pendingReports: 0,
})

// ==================== 搜索与排序 ====================
const searchQuery = ref('')
const sortBy = ref('latest')

const filteredJobs = computed(() => {
  let result = [...jobs.value]
  if (searchQuery.value) {
    result = result.filter(job =>
      job.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  if (sortBy.value === 'applications') {
    result.sort((a, b) => b.applications - a.applications)
  } else if (sortBy.value === 'match') {
    result.sort((a, b) => b.avg_match_rate - a.avg_match_rate)
  }
  return result
})

// ==================== 数据加载 ====================
const loadJobs = async () => {
  loading.value = true
  try {
    const res = await getHRJobList({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    })
    const data = res.data
    jobs.value = data.items || []
    totalJobs.value = data.total || 0
    const s = data.summary || {}
    stats.value = {
      openJobs: s.open_jobs ?? jobs.value.length,
      totalApplications: s.total_applications ?? 0,
      avgMatchRate: s.avg_match_rate ?? 0,
      pendingReports: s.pending_reports ?? 0,
    }
  } catch (e: any) {
    ElMessage.error('加载岗位数据失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

onMounted(loadJobs)

// ==================== 操作事件 ====================
const handleRefresh = () => loadJobs()

const handleCreateJob = () => {
  router.push('/home/job-manage')
  ElMessage.info('请在右上角"一键创建岗位"中新建')
}

const handleJobClick = (job: any) => {
  router.push(`/views/position/${job.id}/edit`)
}

const handleViewReports = (job: any) => {
  router.push(`/home/job-manage`)
  ElMessage.info(`筛选 "${job.name}" 的候选人`)
}

const handleEditJob = (job: any) => {
  editForm.value = {
    id: job.id,
    name: job.name,
    company: job.company,
    category: job.category,
    city: job.city,
    salary_min: job.salary_min,
    salary_max: job.salary_max,
    description: job.description,
  }
  showEditDialog.value = true
}

const handleDeleteJob = async (job: any) => {
  try {
    await ElMessageBox.confirm(
      `确定删除岗位"${job.name}"？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteJob(job.id)
    ElMessage.success('岗位已删除')
    await loadJobs()
  } catch (e: any) {
    if (e === 'cancel' || e?.toString() === 'cancel') return
    ElMessage.error('删除失败：' + (e.response?.data?.detail || e.message || '未知错误'))
  }
}

// ==================== 编辑弹窗 ====================
const showEditDialog = ref(false)
const editLoading = ref(false)
const editForm = ref<any>({})

const submitEdit = async () => {
  if (!editForm.value.name?.trim()) {
    ElMessage.warning('岗位名称不能为空')
    return
  }
  editLoading.value = true
  try {
    await updateJob(editForm.value.id, {
      name: editForm.value.name,
      description: editForm.value.description,
      company: editForm.value.company,
      category: editForm.value.category,
      city: editForm.value.city,
      salary_min: Number(editForm.value.salary_min) || 0,
      salary_max: Number(editForm.value.salary_max) || 0,
    })
    ElMessage.success('岗位信息已更新')
    showEditDialog.value = false
    await loadJobs()
  } catch (e: any) {
    ElMessage.error('保存失败：' + (e.response?.data?.detail || e.message))
  } finally {
    editLoading.value = false
  }
}

// ==================== 工具方法 ====================
const getStatusText = (status: string) => {
  const map: Record<string, string> = { active: '招聘中', paused: '已暂停', closed: '已关闭' }
  return map[status] || status
}

const getMatchClass = (rate: number) => {
  if (rate >= 80) return 'high'
  if (rate >= 60) return 'medium'
  return 'low'
}
</script>



<style scoped>
.job-management-dashboard {
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ========== 页面头部 ========== */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  width: 100%;
}

.title-section {
  flex: 1;
}

.page-title {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.03em;
}

.page-subtitle {
  margin: 0;
  max-width: 620px;
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 16px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: white;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
}

.btn-primary:hover {
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.26);
  transform: translateY(-1px);
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #f8fbff;
  border-color: #bfdbfe;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* ========== 统计卡片 ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 18px 20px;
  display: flex;
  gap: 14px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
  transition: all 0.2s ease;
  align-items: flex-start;
}

.stat-card:hover {
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
  transform: translateY(-1px);
}

.stat-card.stat-primary { border-left: 4px solid #667eea; }
.stat-card.stat-info { border-left: 4px solid #06b6d4; }
.stat-card.stat-success { border-left: 4px solid #10b981; }
.stat-card.stat-warning { border-left: 4px solid #f59e0b; }

.stat-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrapper.primary { background: rgba(102, 126, 234, 0.1); }
.stat-icon-wrapper.info { background: rgba(6, 182, 212, 0.1); }
.stat-icon-wrapper.success { background: rgba(16, 185, 129, 0.1); }
.stat-icon-wrapper.warning { background: rgba(245, 158, 11, 0.1); }

.stat-icon {
  width: 24px;
  height: 24px;
  stroke-width: 2;
}

.stat-card.stat-primary .stat-icon { stroke: #667eea; }
.stat-card.stat-info .stat-icon { stroke: #06b6d4; }
.stat-card.stat-success .stat-icon { stroke: #10b981; }
.stat-card.stat-warning .stat-icon { stroke: #f59e0b; }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
  font-weight: 600;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
  letter-spacing: -0.03em;
}

.stat-meta {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

/* ========== 岗位列表 ========== */
.jobs-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.section-controls {
  display: flex;
  gap: 12px;
}

.search-box {
  position: relative;
  width: 260px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 38px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 13px;
  color: #1a1a1a;
  background: white;
  transition: all 0.2s ease;
  outline: none;
}

.search-input:focus {
  border-color: #60a5fa;
  background: white;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
}

.search-input::placeholder {
  color: #9ca3af;
}

.sort-select {
  width: 140px;
}

:deep(.sort-select .el-input__wrapper) {
  border-radius: 12px;
  background: #f8fbff;
  border: 1px solid rgba(214, 223, 240, 0.96);
}

/* ========== 表格 ========== */
.jobs-table {
  margin-top: 16px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr 1fr 1fr;
  gap: 16px;
  padding: 12px 16px;
  background: #f8fbff;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 8px;
}

.table-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr 1fr 1fr;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  transition: all 0.2s ease;
  cursor: pointer;
  align-items: center;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02);
}

.table-row:hover {
  border-color: #bfdbfe;
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.06);
  transform: translateY(-1px);
}

.job-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.job-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.job-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
}

.job-separator {
  color: #e5e7eb;
}

.status-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-badge.active {
  background: #dcfce7;
  color: #15803d;
}

.status-badge.paused {
  background: #fef3c7;
  color: #b45309;
}

.status-badge.closed {
  background: #f3f4f6;
  color: #6b7280;
}

.applications-count {
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
}

.count-number {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.match-rate {
  display: flex;
  align-items: center;
  gap: 10px;
}

.match-bar {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.match-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.match-fill.high {
  background: #10b981;
}

.match-fill.medium {
  background: #f59e0b;
}

.match-fill.low {
  background: #ef4444;
}

.match-percentage {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  min-width: 40px;
}

.reports-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
}

.reports-count.highlight {
  color: #f59e0b;
  font-weight: 700;
}

.reports-icon {
  width: 16px;
  height: 16px;
}

.col-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.action-btn svg {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.action-btn:hover {
  background: #f8fbff;
  border-color: #bfdbfe;
}

.action-btn:hover svg {
  color: #667eea;
}

.action-btn.danger:hover {
  background: #fef2f2;
  border-color: #ef4444;
}

.action-btn.danger:hover svg {
  color: #ef4444;
}

/* ========== 响应式设计 ========== */
.job-management-dashboard {
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0;
}

@media (max-width: 1300px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1000px) {
  .table-header,
  .table-row {
    grid-template-columns: 1.5fr 1fr 1fr 1fr 0.8fr 0.8fr;
  }

  .job-meta {
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    flex: 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .section-controls {
    width: 100%;
    flex-direction: column;
  }

  .search-box {
    width: 100%;
  }

  .sort-select {
    width: 100%;
  }

  .table-header {
    display: none;
  }

  .table-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .col-status,
  .col-applications,
  .col-match,
  .col-reports {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .col-status::before {
    content: '状态：';
    color: #6b7280;
    font-size: 12px;
  }

  .col-applications::before {
    content: '投递数：';
    color: #6b7280;
    font-size: 12px;
  }

  .col-match::before {
    content: '匹配度：';
    color: #6b7280;
    font-size: 12px;
  }

  .col-reports::before {
    content: '待处理：';
    color: #6b7280;
    font-size: 12px;
  }

  .col-actions {
    justify-content: flex-start;
    padding-top: 8px;
    border-top: 1px solid #e5e7eb;
  }
}
</style>
