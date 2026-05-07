<script setup lang="ts">
import { ref, computed, onMounted, watchEffect } from 'vue'
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

const heroStats = computed(() => [
  {
    label: 'TraitScores',
    value: portraitData.value?.length ? `${portraitData.value.length} 项` : '--',
    hint: '当前心理画像维度'
  },
  {
    label: 'AssessmentSession',
    value: history.value.length ? `${history.value.length} 次` : '0 次',
    hint: '累计评估会话'
  },
  {
    label: 'Person-Job Matching',
    value: latestReport.value?.match_score != null ? `${Math.round(latestReport.value.match_score)}%` : '--',
    hint: '最近一次匹配结果'
  }
])

const quickUpdates = computed(() => {
  const items = history.value.slice(0, 3)
  if (items.length === 0) {
    return [
      {
        title: '尚未生成 EvaluationResult',
        content: '完成一次多Agent面试后，这里将展示最新评估结果与可解释性摘要。',
        meta: '等待首次评估'
      }
    ]
  }

  return items.map((item: any, index: number) => ({
    title: item.job_title || `评估记录 ${index + 1}`,
    content: item.match_score != null
      ? `最近 Person-Job Matching 为 ${Math.round(item.match_score)}%，可进入报告中心查看详细解释。`
      : '评估记录已生成，可进入报告中心查看详细内容。',
    meta: formatTime(item.created_at)
  }))
})

const activityItems = computed(() => {
  if (history.value.length === 0) {
    return [
      {
        title: '等待启动首个 AssessmentSession',
        action: '开始评估',
        time: '立即开始',
        type: 'empty'
      }
    ]
  }

  return history.value.slice(0, 4).map((item: any, index: number) => ({
    title: item.job_title || `评估记录 ${index + 1}`,
    action: item.match_score != null ? `匹配度 ${Math.round(item.match_score)}%` : '查看评估结果',
    time: formatTime(item.created_at),
    type: getMatchLevel(item.match_score)
  }))
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

function getMatchLevel(score?: number) {
  if (score == null) return 'neutral'
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

function formatTime(value?: string) {
  if (!value) return '暂无时间'
  try {
    return new Date(value).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return value
  }
}

async function loadData() {
  loading.value = true
  try {
    const candidateId = user.value?.id || userStore.userId
    if (!candidateId) {
      console.warn('未获取到候选人ID')
      return
    }

    const [portrait, historyData, jobs] = await Promise.all([
      fetchPortrait(candidateId).catch(() => null),
      fetchHistory(candidateId).catch(() => []),
      fetchJobs(candidateId).catch(() => [])
    ])

    portraitData.value = portrait
    history.value = historyData || []
    recommendedJobs.value = jobs || []
  } catch (error) {
    console.error('加载首页数据失败:', error)
    ElMessage.error('加载数据失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

function startNewAssessment() {
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

function goToReportCenter() {
  router.push('/home/reports')
}

onMounted(() => {
  if (userStore.isHR) {
    return
  }
  loadData()
})

watchEffect(() => {
  if (assessmentStore.completionTimestamp > 0) {
    loadData().then(() => {
      ElMessage.success('评估已完成，首页数据已更新')
      assessmentStore.clearCompletionMark()
    })
  }
})
</script>

<template>
  <div class="candidate-home" v-loading="loading">
    <section class="hero-grid">
      <article class="hero-card">
        <div class="hero-copy">
          <span class="hero-eyebrow">AI 人岗匹配首页</span>
          <h2>欢迎回来，{{ user.name || user.username || '候选人' }}</h2>
          <p class="hero-subtitle">
            通过多Agent协同评估，持续沉淀你的 Basic Personality、Scenario Personality 与岗位匹配证据链。
          </p>

          <div class="hero-actions">
            <el-button type="primary" size="large" @click="startNewAssessment">
              <el-icon>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" />
                  <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="2" />
                </svg>
              </el-icon>
              开始新评估
            </el-button>
            <el-button size="large" :disabled="!latestReport" @click="viewLatestReport">
              查看最新报告
            </el-button>
            <el-button size="large" :loading="loading" @click="loadData">
              刷新数据
            </el-button>
          </div>

          <div class="hero-stats">
            <div v-for="item in heroStats" :key="item.label" class="hero-stat-card">
              <div class="hero-stat-label">{{ item.label }}</div>
              <div class="hero-stat-value">{{ item.value }}</div>
              <div class="hero-stat-hint">{{ item.hint }}</div>
            </div>
          </div>
        </div>
      </article>

      <aside class="summary-card">
        <div class="section-head compact">
          <div>
            <h3>最新动态</h3>
            <p>基于现有 EvaluationResult 与 AssessmentSession 自动汇总。</p>
          </div>
          <button class="text-link" type="button" @click="goToReportCenter">全部报告</button>
        </div>

        <div class="summary-list">
          <article v-for="(item, index) in quickUpdates" :key="`${item.title}-${index}`" class="summary-item">
            <div class="summary-index">{{ index + 1 }}</div>
            <div class="summary-content">
              <h4>{{ item.title }}</h4>
              <p>{{ item.content }}</p>
              <span>{{ item.meta }}</span>
            </div>
          </article>
        </div>
      </aside>
    </section>

    <section class="dashboard-grid">
      <div class="main-column">
        <article class="dashboard-card portrait-card">
          <div class="section-head">
            <div>
              <h3>我的心理画像</h3>
              <p>汇总展示当前 TraitScores，用于支持后续 Person-Job Matching 解释。</p>
            </div>
            <span v-if="portraitData && portraitData.length > 0" class="section-badge">
              {{ portraitData.length }} 项特质
            </span>
          </div>

          <EmptyState
            v-if="!portraitData || portraitData.length === 0"
            :image="null"
            title="还没有评估数据"
            text="完成一次多Agent面试评估后，系统将生成你的 TraitScores 与心理画像。"
            buttonText="开始评估"
            @action="startNewAssessment"
          />

          <div v-else class="portrait-layout">
            <div class="portrait-block radar-block">
              <RadarChart :data="portraitData" :size="320" />
              <div class="block-footnote">悬停雷达图可查看各维度分数</div>
            </div>

            <div class="portrait-block score-block">
              <div class="score-overview">
                <div class="avg-score-ring">
                  <svg viewBox="0 0 80 80" class="score-svg">
                    <circle cx="40" cy="40" r="34" fill="none" stroke="#e2e8f0" stroke-width="5" />
                    <circle
                      cx="40"
                      cy="40"
                      r="34"
                      fill="none"
                      :stroke="avgScoreColor"
                      stroke-width="5"
                      stroke-linecap="round"
                      :stroke-dasharray="avgScoreDash"
                      transform="rotate(-90 40 40)"
                      class="score-ring-progress"
                    />
                  </svg>
                  <div class="avg-score-text">
                    <span class="avg-num">{{ avgScore }}</span>
                    <span class="avg-label">综合得分</span>
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
                    <span class="tag-values muted">当前各维度表现相对均衡</span>
                  </div>
                </div>
              </div>

              <div class="trait-bars">
                <div
                  v-for="(trait, idx) in sortedTraits"
                  :key="trait.name"
                  class="trait-bar-item"
                  :style="{ animationDelay: idx * 80 + 'ms' }"
                >
                  <div class="trait-bar-header">
                    <span class="trait-name">{{ trait.name }}</span>
                    <span class="trait-score" :style="{ color: getScoreColor(trait.score) }">
                      {{ trait.score.toFixed(1) }}
                    </span>
                  </div>
                  <div class="trait-bar-track">
                    <div
                      class="trait-bar-fill"
                      :style="{
                        width: `${trait.score / 10 * 100}%`,
                        background: getBarGradient(trait.score)
                      }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="portrait-block video-block">
              <MiniVideoPlayer
                videoUrl="/lv_0_20260407225241.mp4"
                title="心理特质解读"
                @click="goToPsychologyDetail"
              />
            </div>
          </div>
        </article>

        <section v-if="!isNewUser && history.length > 0" class="history-wrap">
          <AssessmentHistory :data="history" @view="viewRecord" />
        </section>

        <article class="dashboard-card recommend-card">
          <div class="section-head">
            <div>
              <h3>为你推荐的岗位</h3>
              <p>根据现有 TraitScores 与历史 EvaluationResult 展示优先关注的岗位实例。</p>
            </div>
            <button class="text-link" type="button" @click="startNewAssessment">查看更多岗位</button>
          </div>

          <EmptyState
            v-if="isNewUser || recommendedJobs.length === 0"
            :image="null"
            title="暂未生成岗位推荐"
            text="完成评估后，系统将基于 Personality 与岗位需求生成推荐岗位。"
            buttonText="开始评估"
            @action="startNewAssessment"
          />

          <div v-else class="job-grid">
            <JobCard
              v-for="job in recommendedJobs.slice(0, 3)"
              :key="job.id"
              :job="job"
              @assess="goToJobDetail"
              @click="goToJobDetail(job.id)"
            />
          </div>
        </article>
      </div>

      <aside class="side-column">
        <article class="dashboard-card side-card">
          <div class="section-head compact">
            <div>
              <h3>心理解读入口</h3>
              <p>进入心理解读中心查看 TraitScores 的详细说明。</p>
            </div>
          </div>

          <div class="side-cta">
            <div class="side-cta-copy">
              <h4>TraitScores 深度解读</h4>
              <p>查看人格维度结构、解释链路与岗位适配含义。</p>
            </div>
            <el-button type="primary" @click="goToPsychologyDetail">进入解读页</el-button>
          </div>
        </article>

        <article class="dashboard-card side-card">
          <div class="section-head compact">
            <div>
              <h3>最近活动</h3>
              <p>保留现有业务逻辑，仅以新布局呈现最近记录。</p>
            </div>
          </div>

          <div class="activity-list">
            <div
              v-for="(item, index) in activityItems"
              :key="`${item.title}-${index}`"
              class="activity-item"
            >
              <span :class="['activity-dot', item.type]"></span>
              <div class="activity-copy">
                <h4>{{ item.title }}</h4>
                <p>{{ item.action }}</p>
              </div>
              <span class="activity-time">{{ item.time }}</span>
            </div>
          </div>
        </article>

        <article class="dashboard-card side-card info-card">
          <div class="section-head compact">
            <div>
              <h3>系统说明</h3>
              <p>首页仅展示前端结果视图，不改变后端计算链路。</p>
            </div>
          </div>

          <div class="info-copy">
            <p>评估会话以 AssessmentSession 为隔离单元，TraitScores 与人岗匹配计算均保留在后端服务层。</p>
            <p>当前页面改版仅重构布局比例、卡片网格与留白层级，不修改接口、字段名、路由逻辑与业务流程。</p>
          </div>
        </article>
      </aside>
    </section>
  </div>
</template>

<style scoped>
.candidate-home {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0 0 36px;
  min-height: calc(100vh - 120px);
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(340px, 0.95fr);
  gap: 24px;
  align-items: stretch;
  margin-bottom: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(320px, 0.9fr);
  gap: 24px;
  align-items: start;
}

.main-column,
.side-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-card,
.dashboard-card,
.summary-card {
  border-radius: 28px;
  border: 1px solid rgba(226, 232, 255, 0.95);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.hero-card {
  min-height: 320px;
  padding: 30px 32px;
  display: flex;
  align-items: stretch;
}

.hero-copy {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.1);
  color: #5b67ff;
  font-size: 12px;
  font-weight: 700;
}

.hero-copy h2 {
  margin: 0;
  font-size: 40px;
  line-height: 1.15;
  color: #172133;
  letter-spacing: -0.05em;
}

.hero-subtitle {
  max-width: 760px;
  margin: 0;
  color: #6f7c93;
  font-size: 15px;
  line-height: 1.9;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions :deep(.el-button) {
  min-width: 144px;
  height: 44px;
  border-radius: 14px;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: auto;
}

.hero-stat-card {
  min-height: 108px;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(248, 250, 255, 0.95), rgba(242, 246, 255, 0.95));
  border: 1px solid rgba(230, 235, 255, 0.95);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hero-stat-label {
  color: #7a87a2;
  font-size: 12px;
  font-weight: 700;
}

.hero-stat-value {
  color: #172133;
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.hero-stat-hint {
  color: #7a87a2;
  font-size: 12px;
  line-height: 1.6;
}

.summary-card,
.dashboard-card {
  padding: 24px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.section-head.compact {
  margin-bottom: 18px;
}

.section-head h3 {
  margin: 0 0 6px;
  font-size: 24px;
  color: #172133;
  letter-spacing: -0.04em;
}

.section-head p {
  margin: 0;
  color: #73809a;
  font-size: 13px;
  line-height: 1.8;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.1);
  color: #5b67ff;
  font-size: 12px;
  font-weight: 700;
}

.text-link {
  border: none;
  padding: 0;
  background: transparent;
  color: #5b67ff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.summary-list {
  display: grid;
  gap: 14px;
}

.summary-item {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(234, 238, 251, 0.95);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(247, 249, 255, 0.96));
  min-height: 116px;
}

.summary-index {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  background: rgba(91, 103, 255, 0.1);
  color: #5b67ff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.summary-content h4 {
  margin: 0 0 8px;
  font-size: 15px;
  color: #1f2937;
}

.summary-content p {
  margin: 0 0 10px;
  color: #6f7c93;
  font-size: 13px;
  line-height: 1.7;
}

.summary-content span {
  color: #94a3b8;
  font-size: 12px;
}

.portrait-layout {
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(320px, 1.1fr) minmax(280px, 0.95fr);
  gap: 0;
  align-items: stretch;
}

.portrait-block {
  min-width: 0;
}

.radar-block,
.score-block {
  border-right: 1px solid #edf2ff;
}

.radar-block {
  padding: 8px 24px 8px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 440px;
}

.block-footnote {
  color: #94a3b8;
  font-size: 12px;
  margin-top: -4px;
}

.score-block {
  padding: 8px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 440px;
}

.video-block {
  padding-left: 24px;
}

.score-overview {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 18px;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid #edf2ff;
  background: linear-gradient(180deg, #fafbff 0%, #f8fbff 100%);
}

.avg-score-ring {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto;
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
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
  margin-top: 4px;
}

.score-summary {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.summary-line {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.tag-label {
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  white-space: nowrap;
}

.tag-green {
  color: #059669;
  background: rgba(16, 185, 129, 0.1);
}

.tag-orange {
  color: #d97706;
  background: rgba(245, 158, 11, 0.1);
}

.tag-values {
  font-size: 13px;
  color: #475569;
  line-height: 1.7;
}

.tag-values.muted {
  color: #94a3b8;
}

.trait-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  margin-bottom: 6px;
}

.trait-name {
  font-size: 13px;
  font-weight: 600;
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
  border-radius: 999px;
  overflow: hidden;
}

.trait-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.history-wrap {
  margin-top: -2px;
}

.job-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.side-card {
  min-height: 220px;
}

.side-cta {
  min-height: 170px;
  border-radius: 22px;
  border: 1px solid rgba(236, 240, 255, 0.95);
  background: linear-gradient(180deg, rgba(249, 251, 255, 0.96), rgba(244, 247, 255, 0.96));
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
}

.side-cta-copy h4,
.activity-copy h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #1f2937;
}

.side-cta-copy p,
.activity-copy p,
.info-copy p {
  margin: 0;
  color: #6f7c93;
  font-size: 13px;
  line-height: 1.8;
}

.activity-list {
  display: grid;
  gap: 14px;
}

.activity-item {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: start;
  padding: 14px 0;
  border-bottom: 1px solid #edf2ff;
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
  background: #cbd5e1;
}

.activity-dot.high {
  background: #10b981;
}

.activity-dot.medium {
  background: #6366f1;
}

.activity-dot.low {
  background: #f59e0b;
}

.activity-copy p {
  margin-top: 2px;
}

.activity-time {
  color: #94a3b8;
  font-size: 12px;
  white-space: nowrap;
}

.info-card {
  min-height: 0;
}

.info-copy {
  display: grid;
  gap: 12px;
}

@media (max-width: 1280px) {
  .hero-grid,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .job-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .portrait-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .radar-block,
  .score-block {
    border-right: none;
    border-bottom: 1px solid #edf2ff;
  }

  .radar-block,
  .score-block,
  .video-block {
    min-height: 0;
    padding: 0 0 20px;
  }

  .video-block {
    padding: 0;
  }

  .side-column {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .candidate-home {
    padding-bottom: 24px;
  }

  .hero-card,
  .summary-card,
  .dashboard-card {
    border-radius: 22px;
    padding: 18px;
  }

  .hero-copy h2 {
    font-size: 28px;
  }

  .hero-stats,
  .job-grid {
    grid-template-columns: 1fr;
  }

  .score-overview {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .summary-line {
    flex-direction: column;
  }

  .hero-actions :deep(.el-button) {
    width: 100%;
  }

  .section-head {
    flex-direction: column;
  }

  .activity-item {
    grid-template-columns: 12px minmax(0, 1fr);
  }

  .activity-time {
    grid-column: 2;
  }
}
</style>
