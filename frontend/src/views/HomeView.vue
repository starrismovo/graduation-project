<script setup lang="ts">
import { ref, computed, onMounted, watch, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAssessmentStore } from '@/stores/assessment'
import { ElMessage } from 'element-plus'
import RadarChart from '@/components/RadarChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import AssessmentHistory from '@/components/AssessmentHistory.vue'
import JobCard from '@/components/JobCard.vue'
import { fetchPortrait, fetchHistory, fetchJobs } from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()
const assessmentStore = useAssessmentStore()

const user = computed(() => userStore.profile || {})
const history = ref<Array<any>>([])
const portraitData = ref<any>(null)
const recommendedJobs = ref<Array<any>>([])
const showWelcome = ref(false)
const loading = ref(false)

const isNewUser = computed(() => history.value.length === 0)
const latestReport = computed(() => history.value[0] || null)

const strengths = computed(() => {
  if (!portraitData.value || !Array.isArray(portraitData.value)) return ''
  return portraitData.value
    .filter((p: any) => p.score > 7)
    .map((p: any) => p.name)
    .join('、')
})

const weaknesses = computed(() => {
  if (!portraitData.value || !Array.isArray(portraitData.value)) return ''
  return portraitData.value
    .filter((p: any) => p.score < 4)
    .map((p: any) => p.name)
    .join('、')
})

async function loadData() {
  loading.value = true
  try {
    const candidateId = user.value?.id || userStore.userId
    if (!candidateId) {
      console.warn('未获取到候选人ID')
      return
    }

    // 并行请求
    const [portrait, historyData, jobs] = await Promise.all([
      fetchPortrait(candidateId).catch(() => null),
      fetchHistory(candidateId).catch(() => []),
      fetchJobs(candidateId).catch(() => [])
    ])

    portraitData.value = portrait
    history.value = historyData || []
    recommendedJobs.value = jobs || []

    if (isNewUser.value) {
      showWelcome.value = true
    }
  } catch (error) {
    console.error('加载首页数据失败:', error)
    ElMessage.error('加载数据失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

function startNewAssessment() {
  showWelcome.value = false
  // 跳转到评估流程（先选择岗位或直接进入对话）
  router.push('/immersive')
}

function viewLatestReport() {
  if (latestReport.value) {
    router.push(`/journey-report/${latestReport.value.job_id}`)
  }
}

function viewRecord(record: any) {
  router.push(`/journey-report/${record.job_id}`)
}

function goToAssessmentWithJob(jobId: number) {
  router.push(`/assessment/${jobId}`)
}

onMounted(() => {
  // 只有非HR用户才显示候选人首页
  if (userStore.isHR) {
    return
  }
  loadData()
})

// 监听评估完成事件，自动刷新数据
watchEffect(() => {
  if (assessmentStore.completionTimestamp > 0) {
    console.log('📊 检测到新的评估完成，自动刷新数据...')
    loadData().then(() => {
      ElMessage.success('✨ 评估完成！数据已更新，请下滑查看最新的心理画像和推荐岗位')
      // 刷新后清除标志
      assessmentStore.clearCompletionMark()
    })
  }
})
</script>

<template>
  <div class="candidate-home" v-loading="loading">
    <!-- 欢迎/操作栏 -->
    <div class="home-header">
      <div class="greeting">
        <h2>欢迎，{{ user.name || user.username || '候选人' }}</h2>
        <p class="subtitle">通过AI智能体对话，发现你的心理特质和岗位潜力</p>
      </div>
      <div class="actions">
        <el-button type="primary" size="large" @click="startNewAssessment">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="2"/></svg></el-icon>
          开始新评估
        </el-button>
        <el-button 
          type="info" 
          size="large"
          :disabled="!latestReport"
          @click="viewLatestReport"
        >
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/></svg></el-icon>
          查看最新报告
        </el-button>
        <el-button 
          size="large"
          :loading="loading"
          @click="loadData"
        >
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" stroke-width="2" fill="none"/><path d="M20.3 4.7A10 10 0 0 0 3.7 20.3" stroke="currentColor" stroke-width="2" fill="none"/></svg></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 心理画像部分 -->
    <div class="portrait-section">
      <el-card class="portrait-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="title">
              <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3.5 3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></el-icon>
              我的心理画像
            </span>
          </div>
        </template>

        <!-- 空状态 -->
        <EmptyState
          v-if="!portraitData || portraitData.length === 0"
          :image="null"
          title="还没有评估"
          text="点击"开始新评估
        />

        <!-- 有数据时显示 -->
        <template v-else>
          <div class="portrait-content">
            <div class="radar-wrapper">
              <RadarChart :data="portraitData" />
            </div>

            <div class="summary-text">
              <div class="summary-item">
                <span class="label">优势特质：</span>
                <span class="value">{{ strengths || '暂无数据' }}</span>
              </div>
              <div class="summary-item">
                <span class="label">改进空间：</span>
                <span class="value">{{ weaknesses || '暂无数据' }}</span>
              </div>
            </div>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 历史评估记录 -->
    <AssessmentHistory
      v-if="!isNewUser && history.length > 0"
      :data="history"
      @view="viewRecord"
    />

    <!-- 推荐岗位 -->
    <div v-if="!isNewUser && recommendedJobs.length > 0" class="recommend-section">
      <h3 class="section-title">
        <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/></svg></el-icon>
        为您高匹配的岗位
      </h3>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="job in recommendedJobs.slice(0, 3)" :key="job.id">
          <JobCard 
            :job="job"
            @assess="goToAssessmentWithJob"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 底部说明卡 -->
    <div class="footer-info">
      <el-card shadow="never" class="info-card">
        <div class="info-content">
          <h4>🤖 系统说明</h4>
          <p>本系统基于 <strong>AI 多智能体对话</strong>，动态评估您的心理特质，生成<strong>可视化画像</strong>并提供<strong>岗位匹配决策支持</strong>。评估过程沉浸感强，约15-20分钟可完成全面评估。</p>
        </div>
      </el-card>
    </div>

    
  </div>
</template>

<style scoped>
/* ==================== 整体布局 ==================== */
.candidate-home {
  padding: 24px;
  background: linear-gradient(135deg, #f9fafc 0%, #e8eef5 100%);
  min-height: calc(100vh - 60px);
}

/* ==================== 顶部栏 ==================== */
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 20px;
}

.greeting {
  flex: 1;
}

.greeting h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.actions :deep(.el-button) {
  min-width: 140px;
  font-weight: 500;
}

/* ==================== 心理画像卡 ==================== */
.portrait-section {
  margin-bottom: 32px;
}

.portrait-card {
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.portrait-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.card-header :deep(.el-icon) {
  font-size: 20px;
  color: #409eff;
}

.portrait-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 40px;
  align-items: center;
}

.radar-wrapper {
  display: flex;
  justify-content: center;
}

.radar-wrapper :deep(.echarts-container) {
  width: 100%;
  height: 350px;
}

.summary-text {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.summary-item .label {
  flex-shrink: 0;
  font-weight: 600;
  color: #2c3e50;
  min-width: 90px;
}

.summary-item .value {
  color: #606266;
  line-height: 1.6;
  flex: 1;
}

/* ==================== 历史评估 ==================== */
.history-section {
  margin-bottom: 32px;
}

/* ==================== 推荐岗位 ==================== */
.recommend-section {
  margin-bottom: 32px;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title :deep(.el-icon) {
  font-size: 20px;
  color: #e6a23c;
}

/* ==================== 底部说明 ==================== */
.footer-info {
  margin-top: 40px;
}

.info-card {
  background: linear-gradient(135deg, #e3f2fd 0%, #f0f7ff 100%);
  border: 1px solid #bbdefb;
}

.info-content {
  padding: 0;
}

.info-content h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1976d2;
  font-weight: 600;
}

.info-content p {
  margin: 0 0 8px 0;
  color: #555;
  line-height: 1.6;
  font-size: 14px;
}

.info-content p:last-child {
  margin-bottom: 0;
}

.info-content strong {
  color: #1976d2;
  font-weight: 600;
}

/* ==================== 欢迎对话框 ==================== */
.welcome-dialog-content {
  padding: 12px 0;
}

.welcome-dialog-content p {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.6;
}

.welcome-dialog-content p:first-child {
  font-size: 15px;
  color: #2c3e50;
  font-weight: 500;
}

.features-list {
  margin: 16px 0;
  padding-left: 20px;
  list-style: none;
}

.features-list li {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.estimate {
  background: #fff7e6;
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 3px solid #e6a23c;
  margin: 16px 0 !important;
  font-size: 13px;
  color: #606266;
}

.estimate strong {
  color: #e6a23c;
}

.note {
  font-size: 13px;
  color: #909399;
  background: #f5f7fa;
  padding: 8px 10px;
  border-radius: 4px;
  margin-top: 12px !important;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .portrait-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .home-header {
    flex-direction: column;
    align-items: stretch;
  }

  .actions {
    width: 100%;
    justify-content: flex-start;
  }

  .actions :deep(.el-button) {
    flex: 1;
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .candidate-home {
    padding: 16px;
  }

  .greeting h2 {
    font-size: 20px;
  }

  .portrait-section :deep(.el-card__body) {
    padding: 16px;
  }

  .portrait-content {
    gap: 16px;
  }

  .summary-text {
    gap: 12px;
  }

  .actions :deep(.el-button) {
    padding: 8px 12px;
    font-size: 14px;
  }
}
</style>