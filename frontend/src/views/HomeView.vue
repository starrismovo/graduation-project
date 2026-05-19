<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, MagicStick } from '@element-plus/icons-vue'
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

const portraitConclusion = computed(() => {
  if (!Array.isArray(portraitData.value) || portraitData.value.length === 0) {
    return '完成评估后，系统将结合人格画像生成基础特质分析与岗位适配提示。'
  }

  const topStrengths = strengths.value.slice(0, 2)
  const watchTraits = weaknesses.value.slice(0, 2)
  const strengthText = topStrengths.length > 0 ? topStrengths.join('、') : '各维度表现较为均衡'
  const watchText = watchTraits.length > 0 ? `，可继续关注${watchTraits.join('、')}相关情境证据` : '，当前未出现明显短板维度'

  return `当前基础人格画像显示：${strengthText}，综合得分 ${avgScore.value}${watchText}。`
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
        ? `岗位“${latest.job_title || '当前岗位'}”的评估报告已生成，建议先查看匹配原因和改进建议。`
        : '完成一次智能面试评估后，这里会同步最新报告。',
      meta: latest ? reportTime : '刚刚'
    },
    {
      title: '最近评估已完成',
      badge: history.value.length > 0 ? '建议查看' : '暂无记录',
      accent: 'violet',
      content:
        history.value.length > 0
          ? '最近一次面试评估已完成，可回顾性格特质、岗位适配表现和后续建议。'
          : '完成首轮评估后，这里会展示最近一次评估进展。',
      meta: history.value.length > 0 ? '2 小时前' : '待开始'
    },
    {
      title: '岗位推荐已更新',
      badge: recommendedJobs.value.length > 0 ? '可浏览' : '等待生成',
      accent: 'blue',
      content:
        recommendedJobs.value.length > 0
          ? `系统已根据你的性格特质和岗位适配表现，更新“${topJobTitle}”等岗位建议。`
          : '完成评估后，系统将根据性格特质与岗位需求生成推荐岗位。',
      meta: recommendedJobs.value.length > 0 ? '昨天 10:24' : '待评估'
    }
  ]
})

const counselorTags = computed(() => {
  const topStrengths = strengths.value.slice(0, 3)
  const topWeaknesses = weaknesses.value.slice(0, 2)
  const topDirections = recommendedJobs.value
    .slice(0, 4)
    .map((job) => job.job_title || job.title)
    .filter(Boolean) as string[]

  return [
    {
      title: '优势特质',
      type: 'strength',
      content: topStrengths.length > 0 ? topStrengths.join('、') : '特质均衡'
    },
    {
      title: '适配方向',
      type: 'direction',
      content: topDirections.length > 0 ? topDirections.slice(0, 2).join('、') : '等待岗位匹配'
    }
  ]
})

const counselorAdvice = computed(() => {
  const topStrengths = strengths.value.slice(0, 2)
  const topJob = recommendedJobs.value[0]
  const topJobTitle = topJob?.job_title || topJob?.title

  if (portraitData.value && portraitData.value.length > 0) {
    const strengthText = topStrengths.length > 0 ? `你在${topStrengths.join('、')}上的表现更突出` : '你的大五人格画像整体较为均衡'
    const jobText = topJobTitle ? `，当前可优先结合“${topJobTitle}”等岗位实例观察适配证据` : '，后续可以结合具体岗位实例进一步验证适配方向'
    return `${strengthText}${jobText}。我会把这些特质转化为岗位沟通、协作方式和成长建议，帮助你理解报告背后的原因。`
  }

  return '完成一次智能面试评估后，我会结合你的大五人格画像与岗位匹配结果，给出更具体的解释和发展建议。'
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
  if (latestReport.value?.id) {
    router.push({
      path: '/home/psychology',
      query: { recordId: String(latestReport.value.id) }
    })
    return
  }
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
            选择、对话、评估，全流程智能化支持，助你精准把握人岗匹配的每一个关键细节，开启高效求职之旅。
          </p>

          <div class="hero-actions">
            <el-button class="hero-action-btn primary-action" size="large" @click="startNewAssessment">
              <el-icon><MagicStick /></el-icon>
              <span>开始新评估</span>
            </el-button>
            <el-button class="hero-action-btn secondary-action" size="large" :disabled="!latestReport" @click="viewLatestReport">
              <el-icon><Document /></el-icon>
              <span>查看最新报告</span>
            </el-button>
          </div>
        </div>

        <div class="hero-visual" aria-hidden="true">
          <img src="/首页logo.png" alt="" class="hero-visual-image" />
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

          <template v-else>
            <div class="portrait-summary-strip">
              <div>
                <span>基础人格</span>
                <p>{{ portraitConclusion }}</p>
              </div>
              <button class="portrait-detail-link" type="button" @click="goToPsychologyDetail">查看完整画像</button>
            </div>

          <div class="portrait-layout">
            <div class="portrait-block radar-block">
              <RadarChart :data="portraitData" :size="300" />
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
          </template>
        </article>
      </div>

      <aside class="side-column">
        <article class="dashboard-card side-card side-card-primary">
          <div class="section-head compact">
            <div>
              <h3>AI 心理咨询师解读</h3>
              <p>基于当前大五人格画像与岗位匹配结果生成</p>
            </div>
            <button class="text-link" type="button" @click="goToPsychologyDetail">查看详情</button>
          </div>

          <div class="insight-panel ai-counselor-entry">
            <div class="insight-visual counselor-visual" aria-label="AI 心理咨询助手">
              <div class="counselor-glow"></div>
              <img src="/ai-counselor.png" alt="AI 心理咨询助手" class="insight-visual-image counselor-image" />
            </div>

            <div class="counselor-consult">
              <div class="counselor-bubble counselor-float-card main-advice">
                <span class="counselor-bubble-label">AI 咨询师建议</span>
                <p>{{ counselorAdvice }}</p>
              </div>

              <div
                v-for="item in counselorTags"
                :key="item.title"
                :class="['counselor-tag-card', 'counselor-float-card', item.type]"
              >
                <span>{{ item.title }}</span>
                <strong>{{ item.content }}</strong>
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
  height: 48px;
  border-radius: 16px;
}

.hero-actions :deep(.hero-action-btn) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 28px;
  font-size: 15px;
  font-weight: 700;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease;
}

.hero-actions :deep(.hero-action-btn .el-icon) {
  font-size: 18px;
}

.hero-actions :deep(.hero-action-btn:hover) {
  transform: translateY(-1px);
}

.hero-actions :deep(.primary-action) {
  color: #ffffff;
  border: none;
  background: linear-gradient(90deg, #2f8cff 0%, #5a3ff5 100%);
  box-shadow: 0 14px 30px rgba(90, 103, 255, 0.3);
}

.hero-actions :deep(.primary-action .el-icon) {
  color: rgba(255, 255, 255, 0.96);
}

.hero-actions :deep(.primary-action:hover),
.hero-actions :deep(.primary-action:focus-visible) {
  color: #ffffff;
  border: none;
  background: linear-gradient(90deg, #287ff2 0%, #5239e6 100%);
  box-shadow: 0 18px 36px rgba(90, 103, 255, 0.34);
}

.hero-actions :deep(.secondary-action) {
  color: #24324a;
  border: 1.5px solid #7aa8ff;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 10px 22px rgba(148, 163, 184, 0.08);
}

.hero-actions :deep(.secondary-action .el-icon) {
  color: #4c94ff;
}

.hero-actions :deep(.secondary-action:hover),
.hero-actions :deep(.secondary-action:focus-visible) {
  color: #172133;
  border-color: #5f90ff;
  background: #ffffff;
  box-shadow: 0 14px 28px rgba(95, 144, 255, 0.14);
}

.hero-actions :deep(.secondary-action.is-disabled) {
  color: #94a3b8;
  border-color: #c7d8ff;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: none;
}

.hero-actions :deep(.secondary-action.is-disabled .el-icon) {
  color: #a8b7d1;
}

.hero-visual {
  position: relative;
  border-radius: 34px;
  background: #fafbff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
  min-height: 184px;
  overflow: hidden;
}

.hero-visual-image {
  width: 100%;
  height: 100%;
  min-height: 184px;
  display: block;
  object-fit: cover;
  object-position: center;
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

.portrait-summary-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 14px 16px;
  border: 1px solid rgba(213, 222, 255, 0.86);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.96), rgba(248, 245, 255, 0.92));
}

.portrait-summary-strip span {
  display: block;
  margin-bottom: 5px;
  color: #5b67ff;
  font-size: 12px;
  font-weight: 800;
}

.portrait-summary-strip p {
  margin: 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.7;
}

.portrait-detail-link {
  flex-shrink: 0;
  height: 34px;
  padding: 0 13px;
  border: 1px solid rgba(129, 140, 248, 0.32);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  color: #5b67ff;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.portrait-layout {
  display: grid;
  grid-template-columns: minmax(380px, 1.08fr) minmax(390px, 0.92fr);
  align-items: stretch;
}

.portrait-block {
  min-width: 0;
}

.radar-block {
  min-height: 342px;
  padding: 8px 26px 8px 10px;
  border-right: 1px solid #edf2ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-block {
  min-height: 342px;
  padding: 4px 0 4px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-overview {
  display: grid;
  grid-template-columns: 94px minmax(0, 1fr);
  gap: 14px;
  padding: 14px;
  border-radius: 18px;
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
  gap: 10px;
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

.side-card-primary {
  border-radius: 24px;
  background: #ffffff;
  box-shadow: 0 18px 44px rgba(88, 103, 176, 0.12);
}

.side-card-primary .section-head {
  margin-bottom: 14px;
}

.side-card-primary .section-head h3 {
  margin-bottom: 7px;
  color: #172033;
}

.side-card-primary .section-head p {
  margin: 0;
  max-width: 310px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.insight-panel {
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  min-height: 440px;
}

.ai-counselor-entry {
  position: relative;
  display: block;
  min-height: 378px;
  padding: 16px;
  border: 1px solid rgba(213, 222, 255, 0.82);
  border-radius: 22px;
  background:
    radial-gradient(circle at 50% 66%, rgba(129, 140, 248, 0.16), transparent 34%),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  overflow: hidden;
}

.insight-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 198px;
  padding: 10px 0;
}

.counselor-visual {
  position: absolute;
  left: 50%;
  bottom: 74px;
  transform: translateX(-50%);
  width: min(58%, 210px);
  min-height: 210px;
  border-radius: 20px;
  overflow: visible;
  background:
    radial-gradient(circle at 52% 36%, rgba(139, 92, 246, 0.22), transparent 38%),
    radial-gradient(circle at 68% 62%, rgba(96, 165, 250, 0.18), transparent 42%),
    linear-gradient(145deg, #f8fbff 0%, #eef4ff 54%, #f6f2ff 100%);
  box-shadow: inset 0 0 0 1px rgba(129, 140, 248, 0.18), 0 20px 38px rgba(99, 102, 241, 0.12);
}

.counselor-glow {
  position: absolute;
  width: 154px;
  height: 154px;
  left: 50%;
  top: 46%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(99, 102, 241, 0.24);
  box-shadow:
    0 0 0 18px rgba(219, 234, 254, 0.46),
    0 0 42px rgba(96, 165, 250, 0.26);
}

.counselor-glow::before,
.counselor-glow::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.28);
  box-shadow: 0 0 18px rgba(96, 165, 250, 0.3);
}

.counselor-glow::before {
  width: 8px;
  height: 8px;
  right: 26px;
  top: 24px;
}

.counselor-glow::after {
  width: 6px;
  height: 6px;
  left: 22px;
  bottom: 42px;
}

.insight-visual-image {
  width: min(100%, 196px);
  aspect-ratio: 1 / 1.38;
  display: block;
  object-fit: contain;
  object-position: center;
}

.counselor-image {
  position: relative;
  z-index: 1;
  width: clamp(150px, 72%, 178px);
  max-height: 218px;
  aspect-ratio: auto;
  filter: drop-shadow(0 24px 26px rgba(60, 72, 125, 0.22));
}

.counselor-consult {
  position: absolute;
  inset: 18px;
  z-index: 2;
  pointer-events: none;
}

.counselor-float-card {
  position: absolute;
  pointer-events: auto;
  backdrop-filter: blur(12px);
  animation: counselorFloat 5.8s ease-in-out infinite;
}

@keyframes counselorFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-7px); }
}

.counselor-bubble {
  padding: 14px 16px;
  border: 1px solid rgba(199, 210, 254, 0.72);
  border-radius: 22px 22px 22px 8px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 28px rgba(99, 102, 241, 0.09);
}

.main-advice {
  top: 2px;
  left: 0;
  right: 0;
  max-height: 132px;
  overflow: hidden;
}

.counselor-bubble::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 34px;
  width: 14px;
  height: 14px;
  border-left: 1px solid rgba(199, 210, 254, 0.72);
  border-bottom: 1px solid rgba(199, 210, 254, 0.72);
  background: rgba(255, 255, 255, 0.96);
  transform: rotate(45deg);
}

.counselor-bubble-label {
  display: inline-flex;
  margin-bottom: 8px;
  color: #5b67ff;
  font-size: 13px;
  font-weight: 800;
}

.counselor-bubble p {
  margin: 0;
  color: #334155;
  font-size: 13px;
  line-height: 1.65;
}

.counselor-tag-card {
  width: 126px;
  padding: 10px 12px;
  border-radius: 16px;
  border: 1px solid #e5edff;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 14px 30px rgba(88, 103, 176, 0.1);
}

.counselor-tag-card span {
  display: block;
  margin-bottom: 5px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.counselor-tag-card strong {
  display: block;
  color: #1e293b;
  font-size: 13px;
  line-height: 1.38;
}

.counselor-tag-card.strength {
  left: 14px;
  bottom: 58px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(255, 255, 255, 0.95));
}

.counselor-tag-card.growth {
  right: 14px;
  bottom: 58px;
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.08), rgba(255, 255, 255, 0.95));
  animation-delay: -1.8s;
}

.counselor-tag-card.direction {
  left: calc(50% - 63px);
  bottom: 8px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.08), rgba(255, 255, 255, 0.95));
  animation-delay: -3.2s;
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

  .ai-counselor-entry {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-height: 0;
    padding: 16px;
  }

  .insight-visual {
    min-height: 124px;
  }

  .counselor-visual {
    position: relative;
    left: auto;
    bottom: auto;
    transform: none;
    width: 100%;
    min-height: 260px;
  }

  .counselor-image {
    max-height: 250px;
  }

  .counselor-consult {
    position: static;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .counselor-float-card,
  .main-advice,
  .counselor-tag-card,
  .counselor-tag-card.strength,
  .counselor-tag-card.growth,
  .counselor-tag-card.direction {
    position: static;
    width: auto;
    animation: none;
  }

  .main-advice {
    grid-column: 1 / -1;
    max-height: none;
  }

  .counselor-bubble {
    border-radius: 20px;
  }

  .counselor-bubble::before {
    left: 42px;
    top: -8px;
    border-left: 1px solid rgba(199, 210, 254, 0.72);
    border-top: 1px solid rgba(199, 210, 254, 0.72);
    border-bottom: none;
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

  .counselor-consult {
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
