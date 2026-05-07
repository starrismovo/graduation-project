<template>
  <div class="report-list-container">
    <!-- 头部 -->
    <div class="report-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <div>
          <h2>我的评估报告</h2>
          <p class="subtitle">查看并管理您的所有评估报告</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="5" animated />

    <!-- 空状态 -->
    <el-empty
      v-else-if="reportList.length === 0"
      description="暂无评估报告"
      :image-size="200"
    >
      <el-button type="primary" @click="startNewAssessment">
        <el-icon><Plus /></el-icon>
        开始新的评估
      </el-button>
    </el-empty>

    <!-- 报告列表 -->
    <div v-else class="report-list">
      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索岗位名称或日期..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filterMode" placeholder="筛选评估模式" class="filter-select">
          <el-option label="全部模式" value="" />
          <el-option label="沉浸式对话" value="immersive" />
          <el-option label="标准评估" value="standard" />
        </el-select>
      </div>

      <!-- 报告卡片列表 -->
      <div class="report-cards">
        <el-card
          v-for="report in filteredReports"
          :key="getReportKey(report)"
          class="report-card"
          :body-style="{ padding: '0' }"
          shadow="hover"
        >
          <!-- 卡片头部 -->
          <template #header>
            <div class="card-header">
              <div class="title-section">
                <div class="job-icon">
                  <el-icon><Briefcase /></el-icon>
                </div>
                <div class="title-info">
                  <h3>{{ report.job_title || '未知岗位' }}</h3>
                  <el-tag 
                    :type="getModeTagType(report.assessment_mode)"
                    class="mode-tag"
                  >
                    <el-icon class="tag-icon">
                      <component :is="getModeIcon(report.assessment_mode)" />
                    </el-icon>
                    {{ getModeLabel(report.assessment_mode) }}
                  </el-tag>
                </div>
              </div>
              <span class="date">
                <el-icon><Clock /></el-icon>
                {{ formatDate(report.created_at) }}
              </span>
            </div>
          </template>

          <!-- 卡片内容 -->
          <div class="card-content">
            <!-- 匹配度 - 环形进度 -->
            <div class="match-score-section">
              <div class="score-ring">
                <svg class="ring-svg" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#e4e7ed" stroke-width="8" />
                  <circle 
                    cx="50" 
                    cy="50" 
                    r="40" 
                    fill="none"
                    :stroke="getScoreColor(report.match_score || 0)"
                    stroke-width="8"
                    stroke-linecap="round"
                    :stroke-dasharray="getRingDasharray(report.match_score || 0)"
                    transform="rotate(-90 50 50)"
                    class="ring-progress"
                  />
                </svg>
                <div class="score-center">
                  <div class="score-value">{{ Math.round(report.match_score || 0) }}%</div>
                  <div class="score-label">匹配度</div>
                </div>
              </div>
              <div class="match-info">
                <div class="match-level">{{ getMatchLevel(report.match_score || 0) }}</div>
                <div class="match-desc">与岗位的契合程度</div>
              </div>
            </div>

            <!-- 五大人格维度 -->
            <div v-if="report.personality_trait && report.personality_trait.length > 0" class="traits-section">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                五大人格维度
              </div>
              <div class="traits-grid">
                <div
                  v-for="trait in report.personality_trait.slice(0, 5)"
                  :key="trait.name"
                  class="trait-item"
                  :style="{ '--trait-color': getTraitColor(trait.score) }"
                >
                  <div class="trait-header">
                    <span class="trait-name">{{ trait.name }}</span>
                    <span class="trait-badge">{{ (trait.score * 10).toFixed(1) }}/10</span>
                  </div>
                  <div class="trait-bar">
                    <div class="trait-fill" :style="{ width: (trait.score * 10) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 对话总结 -->
            <div v-if="report.conversation_summary" class="summary-card">
              <div class="section-title">
                <el-icon><ChatDotSquare /></el-icon>
                对话总结
              </div>
              <p class="summary-text">{{ truncateText(report.conversation_summary, 120) }}</p>
            </div>

            <!-- 优势和改进 -->
            <div v-if="report.match_analysis" class="analysis-grid">
              <div class="analysis-card strengths-card">
                <div class="analysis-header">
                  <el-icon><SuccessFilled /></el-icon>
                  <span>核心优势</span>
                </div>
                <ul class="analysis-list">
                  <li v-for="(str, idx) in report.match_analysis.strengths?.slice(0, 2)" :key="`str-${idx}`">
                    {{ str }}
                  </li>
                </ul>
              </div>
              <div class="analysis-card improvements-card">
                <div class="analysis-header">
                  <el-icon><TrendCharts /></el-icon>
                  <span>改进空间</span>
                </div>
                <ul class="analysis-list">
                  <li v-for="(gap, idx) in report.match_analysis.gaps?.slice(0, 2)" :key="`gap-${idx}`">
                    {{ gap }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="card-actions">
              <button 
                class="action-btn primary-btn"
                @click="viewReport(report)"
              >
                <el-icon><ArrowRight /></el-icon>
                查看详细报告
              </button>
              <button 
                class="action-btn secondary-btn"
                @click="downloadReport(getReportId(report))"
              >
                <el-icon><Download /></el-icon>
                导出PDF
              </button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Search,
  DocumentCopy,
  Briefcase,
  Clock,
  Plus,
  ArrowRight,
  Download,
  DataAnalysis,
  ChatDotSquare,
  SuccessFilled,
  TrendCharts,
  Lightning,
  Cpu
} from '@element-plus/icons-vue'
import { fetchHistory } from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 状态
const reportList = ref<any[]>([])
const loading = ref(false)
const searchText = ref('')
const filterMode = ref('')

// 计算属性：筛选后的报告列表
const filteredReports = computed(() => {
  return reportList.value.filter(report => {
    const matchesSearch =
      !searchText.value ||
      (report.job_title?.toLowerCase().includes(searchText.value.toLowerCase())) ||
      (report.created_at?.includes(searchText.value))

    const matchesMode = !filterMode.value || report.assessment_mode === filterMode.value

    return matchesSearch && matchesMode
  })
})

// 加载报告历史
const loadReportHistory = async () => {
  if (!userStore.userId) {
    ElMessage.error('用户信息不完整')
    return
  }

  loading.value = true
  try {
    const data = await fetchHistory(userStore.userId)
    reportList.value = Array.isArray(data) ? data : []
    console.log('📋 已加载报告数量:', reportList.value.length)
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const getReportId = (report: any): number | string | null => {
  return report?.id ?? report?.record_id ?? report?.assessment_id ?? null
}

const getReportKey = (report: any): string => {
  const id = getReportId(report)
  return id !== null ? String(id) : `${report?.job_title || 'unknown'}-${report?.created_at || Date.now()}`
}

// 查看详细报告
const viewReport = (report: any) => {
  const recordId = getReportId(report)
  if (recordId === null) {
    ElMessage.error('报告记录缺少ID，暂时无法查看详情')
    return
  }

  router.push({
    name: 'AssessmentReport',
    params: { recordId: String(recordId) }
  })
}

// 下载报告
const downloadReport = (recordId: number | string | null) => {
  if (recordId == null) {
    ElMessage.warning('当前报告缺少记录ID，暂时无法导出')
    return
  }
  ElMessage.info('报告下载功能开发中，请在详细报告页面导出')
}

// 开始新评估
const startNewAssessment = () => {
  router.push('/home/jobs')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取评估模式标签类型
const getModeTagType = (mode: string) => {
  return mode === 'immersive' ? 'success' : 'info'
}

// 获取评估模式图标
const getModeIcon = (mode: string) => {
  return mode === 'immersive' ? Lightning : Cpu
}

// 获取评估模式标签文本
const getModeLabel = (mode: string) => {
  return mode === 'immersive' ? '沉浸式对话' : '标准评估'
}

// 获取匹配度颜色
const getScoreColor = (score: number) => {
  if (score >= 85) return '#67c23a'
  if (score >= 70) return '#409eff'
  if (score >= 55) return '#e6a23c'
  return '#f56c6c'
}

// 获取匹配度等级
const getMatchLevel = (score: number) => {
  if (score >= 85) return '高度匹配'
  if (score >= 70) return '良好匹配'
  if (score >= 55) return '中等匹配'
  return '待提升'
}

// 获取环形进度条数据
const getRingDasharray = (score: number) => {
  const circumference = 2 * Math.PI * 40
  const filled = (score / 100) * circumference
  return `${filled} ${circumference - filled}`
}

// 获取特质显示颜色
const getTraitColor = (score: number) => {
  const percent = (score * 10 || 0) / 10 * 100
  if (percent >= 80) return '#67c23a'
  if (percent >= 60) return '#e6a23c'
  return '#909399'
}

// 截断文本
const truncateText = (text: string, length: number) => {
  if (!text) return '-'
  return text.length > length ? text.substring(0, length) + '...' : text
}

// 页面加载
onMounted(() => {
  loadReportHistory()
})
</script>

<style scoped>
.report-list-container {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --success-gradient: linear-gradient(135deg, #67c23a 0%, #52b06c 100%);
  --warning-gradient: linear-gradient(135deg, #e6a23c 0%, #f0a853 100%);
  --danger-gradient: linear-gradient(135deg, #f56c6c 0%, #f88780 100%);
  padding: 32px 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  min-height: 100vh;
}

/* 头部样式 */
.report-header {
  margin-bottom: 32px;
  animation: slideDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: 12px;
  color: white;
  font-size: 28px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.report-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1f2937 0%, #4c63a4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
  font-weight: 500;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.filter-select {
  width: 160px;
}

/* 报告卡片网格 */
.report-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(520px, 1fr));
  gap: 20px;
  animation: fadeIn 0.4s ease-out;
}

.report-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
}

.report-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 48px rgba(31, 41, 55, 0.12);
  border-color: #d7e4fb;
}

/* 卡片头部 */
.report-card :deep(.el-card__header) {
  padding: 16px 20px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fc 100%);
  border-bottom: 1px solid #e8edf5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.job-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.title-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  flex: 1;
}

.title-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mode-tag {
  width: fit-content;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-icon {
  font-size: 12px;
}

.date {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 12px;
  white-space: nowrap;
  flex-shrink: 0;
}

.date :deep(.el-icon) {
  font-size: 14px;
}

/* 卡片内容 */
.report-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 匹配度部分 */
.match-score-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5fe 100%);
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

.score-ring {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.ring-svg {
  width: 100%;
  height: 100%;
}

.ring-progress {
  transition: stroke-dasharray 0.6s ease;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.06));
}

.score-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 24px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
}

.score-label {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  font-weight: 500;
}

.match-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.match-level {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.match-desc {
  font-size: 12px;
  color: #94a3b8;
}

/* 部分标题 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
}

.section-title :deep(.el-icon) {
  font-size: 16px;
  color: #667eea;
}

/* 特质网格 */
.traits-section {
  padding: 14px;
  background: #f8fafc;
  border-radius: 8px;
}

.traits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 10px;
}

.trait-item {
  padding: 10px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.trait-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #d7e4fb;
  transform: translateY(-2px);
}

.trait-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.trait-name {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
}

.trait-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--trait-color);
  background: rgba(102, 126, 234, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
}

.trait-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.trait-fill {
  height: 100%;
  background: var(--trait-color);
  border-radius: 2px;
  transition: width 0.4s ease;
}

/* 对话总结 */
.summary-card {
  padding: 14px;
  background: linear-gradient(135deg, #fffbf0 0%, #fff9e6 100%);
  border: 1px solid #ffe58f;
  border-radius: 8px;
}

.summary-text {
  margin: 0;
  font-size: 13px;
  color: #663c00;
  line-height: 1.6;
}

/* 分析网格 */
.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.analysis-card {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.strengths-card {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #86efac;
}

.improvements-card {
  background: linear-gradient(135deg, #fef3c7 0%, #fef08a 100%);
  border-color: #fcd34d;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.strengths-card .analysis-header {
  color: #166534;
}

.improvements-card .analysis-header {
  color: #92400e;
}

.analysis-header :deep(.el-icon) {
  font-size: 14px;
}

.analysis-list {
  margin: 0;
  padding: 0 0 0 16px;
  list-style: none;
}

.analysis-list li {
  font-size: 12px;
  color: #1f2937;
  padding: 3px 0;
  line-height: 1.5;
}

/* 操作按钮 */
.card-actions {
  display: flex;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid #e8edf5;
}

.action-btn {
  flex: 1;
  height: 36px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
  cursor: pointer;
  font-family: inherit;
  outline: none;
}

.primary-btn {
  background: var(--primary-gradient);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.primary-btn:hover {
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.primary-btn:active {
  transform: translateY(0);
}

.secondary-btn {
  background: white;
  color: #667eea;
  border: 1.5px solid #d7e4fb;
}

.secondary-btn:hover {
  background: #f8fafc;
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.secondary-btn:active {
  background: #f0f2f5;
}

.action-btn :deep(.el-icon) {
  font-size: 14px;
  display: flex;
  align-items: center;
}

/* 动画 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 1024px) {
  .report-cards {
    grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  }
}

@media (max-width: 768px) {
  .report-list-container {
    padding: 20px 16px;
  }

  .report-header {
    margin-bottom: 24px;
  }

  .header-content {
    gap: 12px;
  }

  .header-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .report-header h2 {
    font-size: 24px;
  }

  .report-cards {
    grid-template-columns: 1fr;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .match-score-section {
    flex-direction: column;
    text-align: center;
  }

  .filter-bar {
    gap: 8px;
    flex-direction: column;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }

  .card-actions {
    flex-direction: column;
    gap: 8px;
  }

  .action-btn {
    width: 100%;
    height: 40px;
  }

  .traits-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
}

@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .date {
    width: 100%;
  }

  .title-section {
    width: 100%;
  }

  .report-header h2 {
    font-size: 20px;
  }

  .score-ring {
    width: 80px;
    height: 80px;
  }

  .title-info h3 {
    font-size: 15px;
  }
}
</style>
