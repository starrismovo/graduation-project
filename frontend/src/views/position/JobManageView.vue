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
          <div class="stat-trend positive">
            <svg class="trend-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd" />
            </svg>
            <span>较上周 +{{ stats.openJobsChange }}</span>
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
          <div class="stat-trend positive">
            <svg class="trend-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd" />
            </svg>
            <span>较上周 +{{ stats.applicationsChange }}%</span>
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
          <div class="stat-trend positive">
            <svg class="trend-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd" />
            </svg>
            <span>较上周 +{{ stats.matchRateChange }}%</span>
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

      <div class="jobs-table">
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
                <div class="job-title">{{ job.title }}</div>
                <div class="job-meta">
                  <span class="job-department">{{ job.department }}</span>
                  <span class="job-separator">·</span>
                  <span class="job-location">{{ job.location }}</span>
                  <span class="job-separator">·</span>
                  <span class="job-date">发布于 {{ job.publishedDate }}</span>
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
                    :style="{ width: job.avgMatchRate + '%' }"
                    :class="getMatchClass(job.avgMatchRate)"
                  ></div>
                </div>
                <span class="match-percentage">{{ job.avgMatchRate }}%</span>
              </div>
            </div>

            <div class="col-reports">
              <div class="reports-count" :class="{ highlight: job.pendingReports > 0 }">
                <svg class="reports-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <span>{{ job.pendingReports }}</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

function handleEditJob(job) {
  router.push(`/views/position/${job.id}/edit`)
}
// 统计数据
const stats = ref({
  openJobs: 24,
  openJobsChange: 3,
  totalApplications: 1248,
  applicationsChange: 12,
  avgMatchRate: 78,
  matchRateChange: 5,
  pendingReports: 18
})

// 搜索和排序
const searchQuery = ref('')
const sortBy = ref('latest')

// 岗位数据
const jobs = ref([
  {
    id: 1,
    title: '高级前端工程师',
    department: '技术部',
    location: '北京',
    publishedDate: '2024-01-15',
    status: 'active',
    applications: 142,
    avgMatchRate: 85,
    pendingReports: 5
  },
  {
    id: 2,
    title: 'AI 算法工程师',
    department: '研发中心',
    location: '上海',
    publishedDate: '2024-01-18',
    status: 'active',
    applications: 98,
    avgMatchRate: 82,
    pendingReports: 3
  },
  {
    id: 3,
    title: '产品经理',
    department: '产品部',
    location: '深圳',
    publishedDate: '2024-01-20',
    status: 'active',
    applications: 156,
    avgMatchRate: 76,
    pendingReports: 8
  },
  {
    id: 4,
    title: 'Java 后端工程师',
    department: '技术部',
    location: '杭州',
    publishedDate: '2024-01-12',
    status: 'active',
    applications: 187,
    avgMatchRate: 79,
    pendingReports: 2
  },
  {
    id: 5,
    title: 'UI/UX 设计师',
    department: '设计部',
    location: '北京',
    publishedDate: '2024-01-22',
    status: 'paused',
    applications: 65,
    avgMatchRate: 71,
    pendingReports: 0
  }
])

// 筛选后的岗位列表
const filteredJobs = computed(() => {
  let result = jobs.value

  // 搜索过滤
  if (searchQuery.value) {
    result = result.filter(job => 
      job.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // 排序
  if (sortBy.value === 'applications') {
    result = [...result].sort((a, b) => b.applications - a.applications)
  } else if (sortBy.value === 'match') {
    result = [...result].sort((a, b) => b.avgMatchRate - a.avgMatchRate)
  }

  return result
})

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '招聘中',
    paused: '已暂停',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

// 获取匹配度样式类
const getMatchClass = (rate: number) => {
  if (rate >= 80) return 'high'
  if (rate >= 60) return 'medium'
  return 'low'
}

// 事件处理
const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleCreateJob = () => {
  ElMessage.info('创建岗位功能开发中')
}

const handleJobClick = (job: any) => {
  console.log('查看岗位详情:', job)
}

const handleViewReports = (job: any) => {
  ElMessage.info(`查看 ${job.title} 的报告`)
}

// const handleEditJob = (job: any) => {
//   ElMessage.info(`编辑岗位: ${job.title}`)
// }

const handleDeleteJob = (job: any) => {
  ElMessage.warning(`删除岗位: ${job.title}`)
}
</script>

<style scoped>
.job-management-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* ========== 页面头部 ========== */
.dashboard-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-section {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.btn-primary:hover {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transform: translateY(-1px);
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* ========== 统计卡片 ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  animation: fadeInUp 0.4s ease;
}

.stat-card:nth-child(1) { animation-delay: 0.05s; }
.stat-card:nth-child(2) { animation-delay: 0.1s; }
.stat-card:nth-child(3) { animation-delay: 0.15s; }
.stat-card:nth-child(4) { animation-delay: 0.2s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrapper.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon-wrapper.info {
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
}

.stat-icon-wrapper.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon-wrapper.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon {
  width: 28px;
  height: 28px;
  color: white;
  stroke-width: 2;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.negative {
  color: #ef4444;
}

.trend-icon {
  width: 16px;
  height: 16px;
}

.stat-meta {
  font-size: 13px;
  color: #f59e0b;
  font-weight: 500;
}

/* ========== 岗位列表 ========== */
.jobs-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  animation: fadeInUp 0.4s ease 0.25s both;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.section-controls {
  display: flex;
  gap: 12px;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: #1a1a1a;
  background: #fafbfc;
  transition: all 0.2s ease;
  outline: none;
}

.search-input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-input::placeholder {
  color: #9ca3af;
}

.sort-select {
  width: 140px;
}

:deep(.sort-select .el-input__wrapper) {
  border-radius: 8px;
  background: #fafbfc;
  border: 1px solid #e5e7eb;
}

/* ========== 表格 ========== */
.jobs-table {
  margin-top: 20px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr 1fr 1fr;
  gap: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
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
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
  align-items: center;
}

.table-row:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.job-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.job-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.job-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.job-separator {
  color: #d1d5db;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
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
  width: 18px;
  height: 18px;
  color: #667eea;
}

.count-number {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.match-rate {
  display: flex;
  align-items: center;
  gap: 12px;
}

.match-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.match-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.match-fill.high {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.match-fill.medium {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.match-fill.low {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

.match-percentage {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  min-width: 40px;
}

.reports-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #6b7280;
}

.reports-count.highlight {
  color: #f59e0b;
  font-weight: 600;
}

.reports-icon {
  width: 18px;
  height: 18px;
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
  border-radius: 6px;
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
  background: #f9fafb;
  border-color: #667eea;
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
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .table-header,
  .table-row {
    grid-template-columns: 2fr 1fr 1fr 1fr 0.8fr 1fr;
  }

  .job-meta {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
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
    gap: 16px;
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
    font-size: 13px;
  }

  .col-applications::before {
    content: '投递数：';
    color: #6b7280;
    font-size: 13px;
  }

  .col-match::before {
    content: '匹配度：';
    color: #6b7280;
    font-size: 13px;
  }

  .col-reports::before {
    content: '待处理：';
    color: #6b7280;
    font-size: 13px;
  }

  .col-actions {
    justify-content: flex-start;
    padding-top: 8px;
    border-top: 1px solid #e5e7eb;
  }
}
</style>
