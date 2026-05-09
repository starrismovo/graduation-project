<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useAssessmentStore } from '@/stores/assessment'
import RadarChart from '@/components/RadarChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import JobCard from '@/components/JobCard.vue'
import { fetchPortrait, fetchHistory, fetchJobs } from '@/utils/request'

type PortraitTrait = {
  name: string
  score: number
}

type HistoryRecord = {
  id: number | string
  created_at: string
  job_title: string
  match_score: number
}

type JobRecord = {
  id: number | string
  title?: string
  job_title?: string
}

const router = useRouter()
const userStore = useUserStore()
const assessmentStore = useAssessmentStore()

const user = computed(() => userStore.profile || {})
const history = ref<HistoryRecord[]>([])
const portraitData = ref<PortraitTrait[] | null>(null)
const recommendedJobs = ref<JobRecord[]>([])
const loading = ref(false)

const isNewUser = computed(() => history.value.length === 0)
const latestReport = computed(() => history.value[0] || null)

const strengths = computed(() => {
  if (!Array.isArray(portraitData.value)) return []
  return portraitData.value.filter((item) => item.score >= 7).map((item) => item.name)
})

const weaknesses = computed(() => {
  if (!Array.isArray(portraitData.value)) return []
  return portraitData.value.filter((item) => item.score < 4.5).map((item) => item.name)
})

const avgScore = computed(() => {
  if (!Array.isArray(portraitData.value) || portraitData.value.length === 0) return '0.0'
  const total = portraitData.value.reduce((sum, item) => sum + (item.score || 0), 0)
  return (total / portraitData.value.length).toFixed(1)
})

const avgScoreColor = computed(() => {
  const value = Number(avgScore.value)
  if (value >= 7) return '#10b981'
  if (value >= 4) return '#6366f1'
  return '#f59e0b'
})

const avgScoreDash = computed(() => {
  const value = Number(avgScore.value)
  const circumference = 2 * Math.PI * 34
  const filled = (value / 10) * circumference
  return `${filled} ${circumference - filled}`
})

const sortedTraits = computed(() => {
  if (!Array.isArray(portraitData.value)) return []
  return [...portraitData.value].sort((a, b) => b.score - a.score)
})

const quickUpdates = computed(() => {
  const latest = latestReport.value
  const reportTime = latest?.created_at ? formatTime(latest.created_at) : '刚刚'
  const topJob = recommendedJobs.value[0]
  const topJobTitle = topJob?.job_title || topJob?.title || '推荐岗位'

  return [
    {
      title: '评估报告已生成',
      badge: latest ? '优先处理' : '等待评估',
      accent: 'red',
      content: latest
        ? `岗位“${latest.job_title || '当前岗位'}”的 EvaluationResult 已可查看，建议优先阅读匹配解释。`
        : '完成一次多Agent协同评估后，这里会自动同步最新 EvaluationResult。',
      meta: latest ? reportTime : '刚刚'
    },
    {
      title: '最近评估已完成',
      badge: history.value.length > 0 ? '建议查看' : '暂无记录',
      accent: 'violet',
      content:
        history.value.length > 0
          ? '系统已完成最近一次 AssessmentSession，可回顾基础人格与场景人格的评估结论。'
          : '当前尚未生成 AssessmentSession，完成首轮评估后将自动汇总最近过程。',
      meta: history.value.length > 0 ? '2 小时前' : '待开始'
    },
    {
      title: '岗位推荐已更新',
      badge: recommendedJobs.value.length > 0 ? '可浏览' : '等待生成',
      accent: 'blue',
      content:
        recommendedJobs.value.length > 0
          ? `系统已结合 Basic Personality 与 Scenario Personality 生成“${topJobTitle}”等岗位建议。`
          : '完成评估后，系统将依据 TraitScores 与岗位需求自动生成岗位实例推荐。',
      meta: recommendedJobs.value.length > 0 ? '昨天 10:24' : '待评估'
    }
  ]
})

const insightItems = computed(() => {
  const topStrengths = strengths.value.slice(0, 3)
  const topWeaknesses = weaknesses.value.slice(0, 2)
  const topDirections = recommendedJobs.value
    .slice(0, 4)
    .map((job) => job.job_title || job.title)
    .filter(Boolean) as string[]

  return [
    {
      title: '优势特质',
      type: 'violet',
      content: topStrengths.length > 0 ? topStrengths.join('、') : '当前 TraitScores 维度较为均衡，建议继续积累评估样本。'
    },
    {
      title: '发展建议',
      type: 'rose',
      content: topWeaknesses.length > 0 ? `建议重点关注 ${topWeaknesses.join('、')} 相关情境表现。` : '当前没有明显短板维度，可继续完善情境化评估证据。'
    },
    {
      title: '适配方向',
      type: 'blue',
      content: topDirections.length > 0 ? topDirections.join('、') : '用户研究、产品运营、品牌策划、培训发展等方向可作为后续观察样本。'
    },
    {
      title: '潜力亮点',
      type: 'green',
      content: Number(avgScore.value) >= 7 ? '学习能力与协作稳定性较好，具备持续成长潜力。' : '建议结合更多 AssessmentSession，进一步观察稳定特质与岗位适配趋势。'
    }
  ]
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
    if (!candidateId) return

    const [portrait, historyData, jobs] = await Promise.all([
      fetchPortrait(candidateId).catch(() => null),
      fetchHistory(candidateId).catch(() => []),
      fetchJobs(candidateId).catch(() => [])
    ])

    portraitData.value = portrait
    history.value = (historyData || []).map((item: any) => ({
      ...item,
      id: item.id,
      job_title: item.job_title || '评估记录',
      match_score: typeof item.match_score === 'number' ? item.match_score : Number(item.match_score || 0),
      created_at: item.created_at || ''
    }))
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

function goToJobDetail(jobId: number | string) {
  router.push(`/home/jobs/${jobId}`)
}

function startJobAssessment(jobId: number | string) {
  router.push({
    path: '/home/interviews/room',
    query: {
      jobId: String(jobId)
    }
  })
}

function goToPsychologyDetail() {
  router.push('/home/psychology')
}

function goToReportCenter() {
  router.push('/home/reports')
}

onMounted(() => {
  if (!userStore.isHR) {
    loadData()
  }
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
            <el-button type="primary" size="large" @click="startNewAssessment">开始新评估</el-button>
            <el-button size="large" :disabled="!latestReport" @click="viewLatestReport">查看最新报告</el-button>
          </div>
        </div>

        <div class="hero-visual" aria-hidden="true">
          <div class="hero-orbit hero-orbit-one"></div>
          <div class="hero-orbit hero-orbit-two"></div>
          <div class="hero-device">
            <div class="hero-device-card primary"></div>
            <div class="hero-device-card secondary"></div>
          </div>
          <span class="hero-dot dot-a"></span>
          <span class="hero-dot dot-b"></span>
          <span class="hero-dot dot-c"></span>
        </div>
      </article>

      <aside class="summary-card">
        <div class="section-head compact">
          <div>
            <h3>最新动态</h3>
            
          </div>
          <button class="text-link" type="button" @click="goToReportCenter">全部</button>
        </div>

        <div class="summary-list">
          <article v-for="item in quickUpdates" :key="item.title" class="summary-item">
            <div :class="['summary-badge', item.accent]">{{ item.badge }}</div>
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
              
            </div>
            <span v-if="portraitData && portraitData.length > 0" class="section-badge">{{ portraitData.length }} 项特质</span>
          </div>

          <EmptyState
            v-if="!portraitData || portraitData.length === 0"
            :image="null"
            title="还没有评估数据"
            text="完成一次面试评估后，系统将生成你的特质分数与心理画像。"
            buttonText="开始评估"
            @action="startNewAssessment"
          />

          <div v-else class="portrait-layout">
            <div class="portrait-block radar-block">
              <RadarChart :data="portraitData" :size="336" />
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
                  <div class="summary-line">
                    <span class="tag-label tag-green">优势</span>
                    <span class="tag-values">{{ strengths.length > 0 ? strengths.join('、') : '当前维度表现较为均衡' }}</span>
                  </div>
                  <div class="summary-line">
                    <span class="tag-label tag-violet">说明</span>
                    <span class="tag-values">
                      支撑人岗匹配报告生成。
                    </span>
                  </div>
                </div>
              </div>

              <div class="trait-bars">
                <div v-for="trait in sortedTraits" :key="trait.name" class="trait-bar-item">
                  <div class="trait-bar-header">
                    <span class="trait-name">{{ trait.name }}</span>
                    <span class="trait-score" :style="{ color: getScoreColor(trait.score) }">{{ trait.score.toFixed(1) }}</span>
                  </div>
                  <div class="trait-bar-track">
                    <div
                      class="trait-bar-fill"
                      :style="{ width: `${(trait.score / 10) * 100}%`, background: getBarGradient(trait.score) }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>

      <aside class="side-column">
        <article class="dashboard-card side-card side-card-primary">
          <div class="section-head compact">
            <div>
              <h3>AI 解读与建议</h3>
      
            </div>
            <button class="text-link" type="button" @click="goToPsychologyDetail">查看详情</button>
          </div>

          <div class="insight-panel">
            <div class="insight-visual">
              <div class="insight-core"></div>
            </div>

            <div class="insight-list">
              <div v-for="item in insightItems" :key="item.title" class="insight-item">
                <span :class="['insight-icon', item.type]"></span>
                <div class="insight-copy">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </article>
      </aside>
    </section>

    <section class="recommend-grid">
      <article class="dashboard-card recommend-card recommend-row">
        <div class="section-head">
          <div>
            <h3>为你推荐的岗位</h3>
            
          </div>
          <button class="text-link" type="button" @click="startNewAssessment">查看更多岗位</button>
        </div>

        <EmptyState
          v-if="isNewUser || recommendedJobs.length === 0"
          :image="null"
          title="暂未生成岗位推荐"
          text="完成评估后，系统将依据人格结果与岗位需求生成岗位实例推荐。"
          buttonText="开始评估"
          @action="startNewAssessment"
        />

        <div v-else class="job-grid">
          <JobCard
            v-for="job in recommendedJobs.slice(0, 4)"
            :key="job.id"
            :job="job"
            @assess="startJobAssessment"
            @click="goToJobDetail(job.id)"
          />
        </div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.candidate-home {
  width: 100%;
  margin: 0;
  padding: 0 0 36px;
  min-height: calc(100vh - 120px);
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.62fr) minmax(380px, 0.9fr);
  gap: 24px;
  align-items: stretch;
  margin-bottom: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.68fr) minmax(340px, 0.82fr);
  gap: 24px;
  align-items: stretch;
  margin-bottom: 24px;
}

.main-column,
.side-column {
  display: flex;
  flex-direction: column;
}

.hero-card,
.dashboard-card,
.summary-card {
  border-radius: 28px;
  border: 1px solid rgba(226, 232, 255, 0.95);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
}

.hero-card {
  position: relative;
  min-height: 236px;
  padding: 24px 30px;
  display: grid;
  grid-template-columns: minmax(0, 1.06fr) minmax(240px, 0.86fr);
  gap: 12px;
  overflow: hidden;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
  min-width: 0;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.12);
  color: #5b67ff;
  font-size: 13px;
  font-weight: 700;
}

.hero-copy h2 {
  margin: 0;
  font-size: 30px;
  line-height: 1.12;
  color: #172133;
  letter-spacing: -0.05em;
}

.hero-subtitle {
  margin: 0;
  max-width: 500px;
  color: #6f7c93;
  font-size: 14px;
  line-height: 1.72;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 2px;
}

.hero-actions :deep(.el-button) {
  min-width: 164px;
  height: 44px;
  border-radius: 16px;
}

.hero-visual {
  position: relative;
  border-radius: 34px;
  background:
    radial-gradient(circle at 22% 56%, rgba(99, 102, 241, 0.24) 0 10px, transparent 11px),
    radial-gradient(circle at 76% 25%, rgba(129, 140, 248, 0.16) 0 8px, transparent 9px),
    radial-gradient(circle at 82% 76%, rgba(99, 102, 241, 0.16) 0 7px, transparent 8px),
    linear-gradient(145deg, rgba(239, 243, 255, 0.9), rgba(249, 250, 255, 0.58));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
  min-height: 184px;
  overflow: hidden;
}

.hero-device {
  position: absolute;
  inset: 18% 16% 12% 20%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-device-card {
  position: absolute;
  border-radius: 24px;
  border: 1px solid rgba(205, 216, 255, 0.85);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.66), rgba(223, 231, 255, 0.32));
  box-shadow: 0 18px 38px rgba(99, 102, 241, 0.12);
}

.hero-device-card.primary {
  width: 150px;
  height: 176px;
  transform: rotate(8deg);
}

.hero-device-card.secondary {
  width: 88px;
  height: 88px;
  left: 26%;
  bottom: 10%;
  background: linear-gradient(180deg, rgba(97, 92, 255, 0.92), rgba(140, 102, 255, 0.85));
}

.hero-orbit {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(137, 150, 255, 0.32);
}

.hero-orbit-one {
  width: 210px;
  height: 110px;
  top: 30%;
  left: 12%;
  transform: rotate(-12deg);
}

.hero-orbit-two {
  width: 244px;
  height: 132px;
  bottom: 12%;
  right: 10%;
  opacity: 0.55;
}

.hero-dot {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(101, 114, 255, 0.92), rgba(136, 92, 246, 0.8));
  box-shadow: 0 10px 18px rgba(99, 102, 241, 0.2);
}

.dot-a {
  width: 13px;
  height: 13px;
  top: 26%;
  right: 16%;
}

.dot-b {
  width: 10px;
  height: 10px;
  top: 58%;
  left: 16%;
}

.dot-c {
  width: 8px;
  height: 8px;
  bottom: 19%;
  right: 23%;
}

.summary-card,
.dashboard-card {
  padding: 24px;
}

.summary-card {
  min-height: 236px;
  padding: 22px;
  display: flex;
  flex-direction: column;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.section-head.compact {
  margin-bottom: 10px;
}

.section-head h3 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #172133;
  letter-spacing: -0.04em;
}

.section-head p {
  margin: 0;
  color: #73809a;
  font-size: 13px;
  line-height: 1.65;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  flex: 1;
}

.summary-item {
  min-height: 132px;
  padding: 15px;
  border-radius: 22px;
  border: 1px solid rgba(234, 238, 251, 0.95);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 249, 255, 0.98));
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-badge {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.summary-badge.red {
  color: #ef4444;
  background: rgba(254, 226, 226, 0.88);
}

.summary-badge.violet {
  color: #7c3aed;
  background: rgba(237, 233, 254, 0.92);
}

.summary-badge.blue {
  color: #2563eb;
  background: rgba(219, 234, 254, 0.92);
}

.summary-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.summary-content h4 {
  margin: 0 0 8px;
  font-size: 15px;
  color: #1f2937;
}

.summary-content p {
  margin: 0;
  flex: 1;
  color: #6f7c93;
  font-size: 12px;
  line-height: 1.66;
}

.summary-content span {
  margin-top: 8px;
  color: #94a3b8;
  font-size: 12px;
}

.portrait-card,
.side-card-primary {
  height: 100%;
}

.portrait-layout {
  display: grid;
  grid-template-columns: minmax(380px, 1.08fr) minmax(390px, 0.92fr);
  align-items: stretch;
  height: calc(100% - 54px);
}

.portrait-block {
  min-width: 0;
}

.radar-block {
  min-height: 440px;
  padding: 8px 26px 8px 10px;
  border-right: 1px solid #edf2ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-block {
  min-height: 440px;
  padding: 12px 0 8px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-overview {
  display: grid;
  grid-template-columns: 116px minmax(0, 1fr);
  gap: 18px;
  padding: 18px;
  border-radius: 22px;
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
  margin-top: 4px;
  font-size: 11px;
  color: #94a3b8;
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

.tag-violet {
  color: #5b67ff;
  background: rgba(91, 103, 255, 0.1);
}

.tag-values {
  font-size: 13px;
  color: #475569;
  line-height: 1.75;
}

.trait-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.job-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.recommend-card {
  padding: 22px 22px 24px;
}

.recommend-card .section-head {
  margin-bottom: 18px;
}

.recommend-card .section-head h3 {
  margin-bottom: 6px;
}

.recommend-card .section-head p {
  max-width: 640px;
}

.recommend-row {
  grid-column: 1 / -1;
  max-width: calc(100% - 24px);
  margin-right: auto;
  min-width: 0;
}

.recommend-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.68fr) minmax(340px, 0.82fr);
  gap: 24px;
}

.side-card {
  min-height: 0;
}

.insight-panel {
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  min-height: 440px;
}

.insight-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 198px;
}

.insight-core {
  width: 132px;
  height: 132px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 42% 38%, rgba(255, 255, 255, 0.82) 0 12px, transparent 13px),
    radial-gradient(circle at 60% 50%, rgba(137, 92, 246, 0.8), rgba(99, 102, 241, 0.2) 58%, rgba(255, 255, 255, 0) 72%),
    radial-gradient(circle at 50% 50%, rgba(194, 205, 255, 0.42), rgba(91, 103, 255, 0.1) 68%, rgba(255, 255, 255, 0) 72%);
  box-shadow: 0 22px 48px rgba(99, 102, 241, 0.14);
}

.insight-list {
  display: grid;
  gap: 14px;
}

.insight-item {
  display: grid;
  grid-template-columns: 14px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.insight-icon {
  width: 14px;
  height: 14px;
  margin-top: 4px;
  border-radius: 50%;
}

.insight-icon.violet {
  background: #8b5cf6;
}

.insight-icon.rose {
  background: #fb7185;
}

.insight-icon.blue {
  background: #60a5fa;
}

.insight-icon.green {
  background: #34d399;
}

.insight-copy h4 {
  margin: 0 0 6px;
  font-size: 14px;
  color: #1f2937;
}

.insight-copy p {
  margin: 0;
  color: #6f7c93;
  font-size: 12px;
  line-height: 1.8;
}

@media (max-width: 1380px) {
  .hero-grid,
  .dashboard-grid,
  .recommend-grid {
    grid-template-columns: 1fr;
  }

  .summary-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .job-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1180px) {
  .hero-card {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    min-height: 220px;
  }

  .portrait-layout {
    grid-template-columns: 1fr;
    height: auto;
  }

  .radar-block {
    border-right: none;
    border-bottom: 1px solid #edf2ff;
  }

  .score-block {
    padding: 24px 0 0;
    min-height: 0;
  }

  .insight-panel {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .insight-visual {
    min-height: 124px;
  }
}

@media (max-width: 900px) {
  .summary-list,
  .job-grid {
    grid-template-columns: 1fr;
  }

  .score-overview {
    grid-template-columns: 1fr;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .candidate-home {
    padding-bottom: 24px;
  }

  .hero-card,
  .summary-card,
  .dashboard-card {
    padding: 18px;
    border-radius: 22px;
  }

  .recommend-card {
    padding: 18px;
  }

  .hero-copy h2 {
    font-size: 28px;
  }

  .hero-actions :deep(.el-button) {
    width: 100%;
  }

  .section-head {
    flex-direction: column;
  }

  .summary-line {
    flex-direction: column;
  }
}
</style>
