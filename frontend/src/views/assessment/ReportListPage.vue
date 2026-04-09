<template>
  <div class="report-list-container">
    <!-- 头部 -->
    <div class="report-header">
      <h2>📊 我的评估报告</h2>
      <p class="subtitle">查看并管理您的所有评估报告</p>
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
          :key="report.id"
          class="report-card"
          :body-style="{ padding: '20px' }"
          shadow="hover"
        >
          <template #header>
            <div class="card-header">
              <div class="title-section">
                <h3>{{ report.job_title || '未知岗位' }}</h3>
                <el-tag :type="getModeTagType(report.assessment_mode)">
                  {{ getModeLabel(report.assessment_mode) }}
                </el-tag>
              </div>
              <span class="date">{{ formatDate(report.created_at) }}</span>
            </div>
          </template>

          <div class="card-content">
            <!-- 匹配度 -->
            <div class="match-score-section">
              <div class="score-circle">
                <div class="score-value">{{ Math.round(report.match_score || 0) }}%</div>
                <div class="score-label">匹配度</div>
              </div>
              <el-progress
                :percentage="report.match_score || 0"
                :color="getScoreColor(report.match_score || 0)"
              />
            </div>

            <!-- 五大人格（简化显示） -->
            <div v-if="report.personality_trait && report.personality_trait.length > 0" class="traits-preview">
              <div class="traits-title">五大人格维度</div>
              <div class="traits-grid">
                <div
                  v-for="trait in report.personality_trait.slice(0, 5)"
                  :key="trait.name"
                  class="trait-item"
                >
                  <div class="trait-name">{{ trait.name }}</div>
                  <div class="trait-value">{{ Math.round(trait.score * 10) || 0 }}/10</div>
                  <el-progress
                    :percentage="Math.min((trait.score * 10 || 0) / 10 * 100, 100)"
                    :color="getTraitColor(trait.score)"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>

            <!-- 概要信息 -->
            <div v-if="report.conversation_summary" class="summary-section">
              <div class="summary-title">📝 对话总结</div>
              <p class="summary-text">
                {{ truncateText(report.conversation_summary, 100) }}
              </p>
            </div>

            <!-- 优势和改进 -->
            <div v-if="report.match_analysis" class="analysis-section">
              <div class="analysis-row">
                <div class="analysis-item strengths">
                  <div class="analysis-label">✅ 优势</div>
                  <ul>
                    <li v-for="(str, idx) in report.match_analysis.strengths?.slice(0, 2)" :key="`str-${idx}`">
                      {{ str }}
                    </li>
                  </ul>
                </div>
                <div class="analysis-item gaps">
                  <div class="analysis-label">📈 改进空间</div>
                  <ul>
                    <li v-for="(gap, idx) in report.match_analysis.gaps?.slice(0, 2)" :key="`gap-${idx}`">
                      {{ gap }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="card-actions">
              <el-button type="primary" link @click="viewReport(report.id)">
                查看详细报告 →
              </el-button>
              <el-button type="default" link @click="downloadReport(report.id)">
                📥 导出PDF
              </el-button>
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
import { Search } from '@element-plus/icons-vue'
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

// 查看详细报告
const viewReport = (recordId: number) => {
  router.push(`/home/report/${recordId}`)
}

// 下载报告
const downloadReport = (recordId: number) => {
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

// 获取评估模式标签文本
const getModeLabel = (mode: string) => {
  return mode === 'immersive' ? '沉浸式对话' : '标准评估'
}

// 获取匹配度颜色
const getScoreColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
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
  padding: 24px;
  background: linear-gradient(135deg, #f9fafc 0%, #e8eef5 100%);
  min-height: 100vh;
}

.report-header {
  margin-bottom: 24px;
  animation: slideDown 0.3s ease-out;
}

.report-header h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.filter-select {
  width: 150px;
}

/* 报告卡片 */
.report-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 16px;
  animation: fadeIn 0.3s ease-in;
}

.report-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
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
}

.title-section h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
  font-weight: 600;
}

.date {
  color: #95a5a6;
  font-size: 12px;
  white-space: nowrap;
}

/* 卡片内容 */
.card-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 匹配度部分 */
.match-score-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
}

.score-label {
  font-size: 12px;
  opacity: 0.9;
}

/* 特质预览 */
.traits-preview {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.traits-title {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.traits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 8px;
}

.trait-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trait-name {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
}

.trait-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

/* 概要部分 */
.summary-section {
  padding: 12px;
  background: #fff9e6;
  border-radius: 8px;
  border-left: 3px solid #e6a23c;
}

.summary-title {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 6px;
}

.summary-text {
  margin: 0;
  font-size: 13px;
  color: #7f8c8d;
  line-height: 1.5;
}

/* 分析部分 */
.analysis-section {
  padding: 12px;
  background: #f0f2f5;
  border-radius: 8px;
}

.analysis-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.analysis-item {
  font-size: 12px;
}

.analysis-item ul {
  margin: 0;
  padding-left: 16px;
  list-style: none;
}

.analysis-item li {
  color: #7f8c8d;
  padding: 2px 0;
  font-size: 12px;
}

.analysis-item.strengths .analysis-label {
  color: #67c23a;
  font-weight: 600;
  margin-bottom: 4px;
}

.analysis-item.gaps .analysis-label {
  color: #e6a23c;
  font-weight: 600;
  margin-bottom: 4px;
}

/* 操作按钮 */
.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #ecf0f1;
  justify-content: flex-end;
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
@media (max-width: 768px) {
  .report-cards {
    grid-template-columns: 1fr;
  }

  .analysis-row {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    gap: 8px;
  }

  .search-input {
    min-width: auto;
  }
}
</style>
