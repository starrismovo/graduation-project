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
import MiniVideoPlayer from '@/components/MiniVideoPlayer.vue'
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

const avgScore = computed(() => {
  if (!portraitData.value || !Array.isArray(portraitData.value) || portraitData.value.length === 0) return '0.0'
  const sum = portraitData.value.reduce((acc: number, p: any) => acc + (p.score || 0), 0)
  return (sum / portraitData.value.length).toFixed(1)
})

const avgScoreColor = computed(() => {
  const v = parseFloat(avgScore.value)
  if (v >= 7) return '#10b981'
  if (v >= 4) return '#6366f1'
  return '#f59e0b'
})

const avgScoreDash = computed(() => {
  const v = parseFloat(avgScore.value)
  const circumference = 2 * Math.PI * 34
  const filled = (v / 10) * circumference
  return `${filled} ${circumference - filled}`
})

const sortedTraits = computed(() => {
  if (!portraitData.value || !Array.isArray(portraitData.value)) return []
  return [...portraitData.value].sort((a: any, b: any) => b.score - a.score)
})

function getScoreColor(score: number): string {
  if (score >= 7) return '#10b981'
  if (score >= 4) return '#6366f1'
  return '#f59e0b'
}

function getBarGradient(score: number): string {
  if (score >= 7) return 'linear-gradient(90deg, #10b981, #34d399)'
  if (score >= 4) return 'linear-gradient(90deg, #6366f1, #818cf8)'
  return 'linear-gradient(90deg, #f59e0b, #fbbf24)'
}

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
  // 先去选择岗位
  router.push('/home/jobs')
}

function viewLatestReport() {
  if (latestReport.value) {
    router.push(`/home/report/${latestReport.value.id}`)
  }
}

function viewRecord(record: any) {
  router.push(`/home/report/${record.id}`)
}

function goToJobDetail(jobId: number | string) {
  router.push(`/home/jobs/${jobId}`)
}

function goToPsychologyDetail() {
  router.push('/home/psychology')
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
      <div class="portrait-panel">
        <!-- 面板头部 -->
        <div class="panel-header">
          <div class="panel-title-row">
            <div class="panel-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="none" stroke="currentColor" stroke-width="1.5"/>
                <path d="M12 6a2.5 2.5 0 0 1 0 5 2.5 2.5 0 0 1 0-5zM12 13c3 0 5.5 1.5 5.5 3.5V18h-11v-1.5c0-2 2.5-3.5 5.5-3.5z" fill="currentColor" opacity="0.9"/>
              </svg>
            </div>
            <h3 class="panel-title">我的心理画像</h3>
            <span v-if="portraitData && portraitData.length > 0" class="panel-badge">
              {{ portraitData.length }} 项特质
            </span>
          </div>
          <p class="panel-desc">
            🧠 整体心理特质（所有评估聚合）
            <br/>
            <small>具体岗位匹配度详见历史记录中的评估报告</small>
          </p>
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="!portraitData || portraitData.length === 0"
          :image="null"
          title="还没有评估数据"
          text="完成一次 AI 面试评估，即可生成你的专属心理画像"
          buttonText="开始评估"
          @action="startNewAssessment"
        />

        <!-- 有数据时显示 -->
        <template v-else>
          <div class="portrait-body">
            <!-- 左侧：雷达图 -->
            <div class="radar-area">
              <RadarChart :data="portraitData" :size="360" />
              <div class="radar-caption">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="14" height="14" fill="#94a3b8"><circle cx="8" cy="8" r="7" fill="none" stroke="#94a3b8" stroke-width="1.2"/><path d="M8 4.5v4M8 10.5v1" stroke="#94a3b8" stroke-width="1.3" stroke-linecap="round"/></svg>
                悬停雷达图可查看详细分数
              </div>
            </div>

            <!-- 中间：特质详情 -->
            <div class="trait-details">
              <!-- 综合得分 -->
              <div class="score-overview">
                <div class="avg-score-ring">
                  <svg viewBox="0 0 80 80" class="score-svg">
                    <circle cx="40" cy="40" r="34" fill="none" stroke="#e2e8f0" stroke-width="5"/>
                    <circle cx="40" cy="40" r="34" fill="none"
                      :stroke="avgScoreColor"
                      stroke-width="5"
                      stroke-linecap="round"
                      :stroke-dasharray="avgScoreDash"
                      stroke-dashoffset="0"
                      transform="rotate(-90 40 40)"
                      class="score-ring-progress"
                    />
                  </svg>
                  <div class="avg-score-text">
                    <span class="avg-num">{{ avgScore }}</span>
                    <span class="avg-label">综合</span>
                  </div>
                </div>
                <div class="score-summary">
                  <div class="summary-line" v-if="strengths">
                    <span class="tag-label tag-green">优势</span>
                    <span class="tag-values">{{ strengths }}</span>
                  </div>
                  <div class="summary-line" v-if="weaknesses">
                    <span class="tag-label tag-orange">待提升</span>
                    <span class="tag-values">{{ weaknesses }}</span>
                  </div>
                  <div class="summary-line" v-if="!strengths && !weaknesses">
                    <span class="tag-values muted">各维度表现均衡</span>
                  </div>
                </div>
              </div>

              <!-- 各维度分数条 -->
              <div class="trait-bars">
                <div
                  v-for="(trait, idx) in sortedTraits"
                  :key="trait.name"
                  class="trait-bar-item"
                  :style="{ animationDelay: idx * 80 + 'ms' }"
                >
                  <div class="trait-bar-header">
                    <span class="trait-name">{{ trait.name }}</span>
                    <span class="trait-score" :style="{ color: getScoreColor(trait.score) }">{{ trait.score.toFixed(1) }}</span>
                  </div>
                  <div class="trait-bar-track">
                    <div
                      class="trait-bar-fill"
                      :style="{
                        width: (trait.score / 10 * 100) + '%',
                        background: getBarGradient(trait.score)
                      }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：视频小窗 -->
            <div class="video-area">
              <MiniVideoPlayer
                videoUrl="/lv_0_20260407225241.mp4"
                title="心理特质解读"
                @click="goToPsychologyDetail"
              />
            </div>
          </div>
        </template>
      </div>
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
            @assess="goToJobDetail"
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

/* ==================== 心理画像面板 ==================== */
.portrait-section {
  margin-bottom: 32px;
}

.portrait-panel {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 6px 24px rgba(99,102,241,0.08);
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.portrait-panel:hover {
  box-shadow: 0 2px 6px rgba(0,0,0,0.08), 0 12px 36px rgba(99,102,241,0.12);
}

/* 面板头部 */
.panel-header {
  padding: 24px 28px 16px;
  background: linear-gradient(135deg, #f8f7ff 0%, #eef2ff 50%, #f0f9ff 100%);
  border-bottom: 1px solid rgba(99,102,241,0.08);
}

.panel-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.panel-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  flex-shrink: 0;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.3px;
}

.panel-badge {
  font-size: 12px;
  font-weight: 500;
  color: #6366f1;
  background: rgba(99,102,241,0.1);
  padding: 2px 10px;
  border-radius: 20px;
  margin-left: auto;
}

.panel-desc {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
  padding-left: 46px;
}

/* 面板主体 */
.portrait-body {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0;
  padding: 24px 0;
}

/* portrait-body 内的视频小窗区域 */
.portrait-body > .video-area {
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
}

.portrait-body > .video-area :deep(.mini-video-player) {
  width: 100%;
  max-width: 100%;
}

/* 雷达图区域 */
.radar-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 24px;
  border-right: 1px solid #f1f5f9;
}

.radar-caption {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #94a3b8;
  margin-top: -8px;
}

/* 中间特质详情 */
.trait-details {
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-right: 1px solid #f1f5f9;
}

/* 右侧视频小窗 */
.video-area {
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}

/* 综合评分区 */
.score-overview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #fafafe 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  text-align: center;
}

.avg-score-ring {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.score-svg {
  width: 80px;
  height: 80px;
}

.score-ring-progress {
  transition: stroke-dasharray 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.avg-score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1;
}

.avg-num {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
}

.avg-label {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 3px;
}

.score-summary {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  width: 100%;
}

.summary-line {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
}

.tag-label {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 6px;
  flex-shrink: 0;
}

.tag-green {
  color: #059669;
  background: rgba(16,185,129,0.1);
}

.tag-orange {
  color: #d97706;
  background: rgba(245,158,11,0.1);
}

.tag-values {
  font-size: 12px;
  color: #475569;
  line-height: 1.4;
}

.tag-values.muted {
  color: #94a3b8;
  font-style: italic;
}

/* 各维度分数条 */
.trait-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trait-bar-item {
  animation: slideIn 0.5s ease both;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-12px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.trait-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.trait-name {
  font-size: 12px;
  font-weight: 500;
  color: #334155;
}

.trait-score {
  font-size: 13px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.trait-bar-track {
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.trait-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* ==================== 大五人格解读 ==================== */
.bigfive-section {
  margin-bottom: 32px;
}

.bigfive-panel {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 6px 24px rgba(99,102,241,0.06);
  overflow: hidden;
  padding: 28px;
}

.bigfive-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 32px;
}

/* 视频区域 */
.video-area {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.video-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.video-badge {
  font-size: 12px;
  font-weight: 600;
  color: #6366f1;
  background: rgba(99,102,241,0.08);
  padding: 3px 10px;
  border-radius: 20px;
  align-self: flex-start;
}

.video-title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  border-radius: 12px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.video-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.video-caption {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.7;
  padding: 0 2px;
}

/* 五维度卡片区域 */
.traits-explain {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.traits-explain-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.traits-explain-title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
}

.traits-explain-hint {
  font-size: 12px;
  color: #94a3b8;
}

.trait-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trait-card {
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
  background: #fff;
}

.trait-card:hover {
  border-color: #e2e8f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.trait-card.expanded {
  border-color: #e0e7ff;
  box-shadow: 0 2px 12px rgba(99,102,241,0.08);
}

.trait-card-main {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
}

.trait-card-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.trait-card-info {
  flex: 1;
  min-width: 0;
}

.trait-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.3;
}

.trait-card-brief {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.trait-card-arrow {
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.trait-card-arrow.rotated {
  transform: rotate(180deg);
}

.trait-card-detail {
  padding: 0 14px 14px;
  overflow: hidden;
}

.trait-card-desc {
  margin: 0 0 10px;
  font-size: 13px;
  color: #475569;
  line-height: 1.7;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.trait-card-spectrum {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.spectrum-end {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spectrum-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.spectrum-label {
  font-size: 12px;
  color: #64748b;
}

/* 展开/折叠过渡 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
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
  .portrait-body {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .radar-area {
    border-right: none;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 20px;
  }

  .trait-details {
    border-right: none;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 20px;
  }

  .video-area {
    border: none;
    padding: 0;
  }

  .bigfive-layout {
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

  .panel-header {
    padding: 16px 18px 12px;
  }

  .panel-desc {
    padding-left: 0;
  }

  .trait-details {
    padding: 0 16px;
  }

  .score-overview {
    flex-direction: column;
    text-align: center;
  }

  .bigfive-panel {
    padding: 18px;
  }

  .actions :deep(.el-button) {
    padding: 8px 12px;
    font-size: 14px;
  }
}
</style>