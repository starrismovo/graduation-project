<template>
  <div class="report-container" v-loading="loading">
    <div class="report-header">
      <el-button type="text" @click="goBack">
        <el-icon>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" /><path d="M8 12h12" /></svg>
        </el-icon>
        返回
      </el-button>
      <div class="header-title-group">
        <h2>评估报告详情</h2>
        <p>围绕大五人格、岗位适配和职业发展建议形成结构化解释。</p>
      </div>
      <div class="header-spacer"></div>
    </div>

    <div v-if="reportData" class="report-content">
      <div class="report-layout">
        <div class="report-main">
          <section id="section-overview" class="report-section">
            <div class="section-header">
              <span class="section-badge">1</span>
              <div>
                <h3>评估基本信息</h3>
                <p>展示当前 AssessmentSession 对应的岗位、时间、模式与角色数量。</p>
              </div>
            </div>

            <div class="overview-info-grid">
              <article v-for="item in overviewInfoCards" :key="item.label" class="overview-info-card">
                <div class="overview-icon" :class="item.theme">{{ item.icon }}</div>
                <div class="overview-meta">
                  <div class="overview-label">{{ item.label }}</div>
                  <div class="overview-value">{{ item.value }}</div>
                </div>
              </article>
            </div>
          </section>

          <section class="report-section">
            <div class="section-header">
              <span class="section-badge">2</span>
              <div>
                <h3>匹配度概览</h3>
                <p>从综合匹配、性格匹配与技能匹配三个层面概括当前报告结论。</p>
              </div>
            </div>

            <div class="match-overview-card">
              <div class="match-main-panel">
                <div class="score-circle-large">
                  <svg viewBox="0 0 120 120" class="ring-svg-large">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="#e6ebf4" stroke-width="10" />
                    <circle
                      cx="60"
                      cy="60"
                      r="48"
                      fill="none"
                      :stroke="getScoreColor(reportData.match_score || 0)"
                      stroke-width="10"
                      stroke-linecap="round"
                      :stroke-dasharray="ringDasharrayLarge"
                      transform="rotate(-90 60 60)"
                    />
                  </svg>
                  <div class="score-circle-content">
                    <div class="score-percent">{{ Math.round(reportData.match_score || 0) }}%</div>
                    <div class="score-level">{{ getMatchLevel(reportData.match_score || 0) }}</div>
                  </div>
                </div>

                <div class="match-summary">
                  <div class="summary-head">
                    <span class="summary-kicker">综合判断</span>
                    <h4>{{ getMatchLevel(reportData.match_score || 0) }}</h4>
                  </div>
                  <p>{{ overviewSummary }}</p>
                </div>
              </div>

              <div class="match-dimension-grid">
                <article v-for="dimension in matchDimensions" :key="dimension.label" class="dimension-card">
                  <div class="dimension-top">
                    <div class="dimension-icon" :class="getDimensionTheme(dimension.label)">{{ getDimensionEmoji(dimension.label) }}</div>
                    <div>
                      <div class="dimension-label">{{ dimension.label }}</div>
                      <div class="dimension-value">{{ Math.round(dimension.score) }}%</div>
                    </div>
                  </div>
                  <div class="dimension-bar">
                    <span :style="{ width: `${Math.min(100, Math.max(0, dimension.score))}%`, background: getDimensionGradient(dimension.label) }"></span>
                  </div>
                  <p>{{ dimension.description }}</p>
                </article>
              </div>
            </div>
          </section>

          <section id="section-psychology" class="report-section">
            <div class="section-header">
              <span class="section-badge">3</span>
              <div>
                <h3>大五人格分析</h3>
                <p>报告从大五人格模型解释候选人在目标岗位中的稳定优势、潜在风险与发展方向。</p>
              </div>
            </div>

            <div class="psychology-panel">
              <div class="radar-card">
                <div class="panel-mini-title">人格雷达图</div>
                <div class="portrait-display">
                  <RadarChart :data="personalityTraits" :height="280" />
                </div>
                <p class="summary-text personality-summary">{{ personalitySummary }}</p>
              </div>

              <div class="analysis-stack">
                <div class="analysis-card good-card">
                  <div class="analysis-title-row">
                    <span class="analysis-dot good-dot"></span>
                    <h4>优势表现</h4>
                  </div>
                  <div class="chip-list">
                    <span v-for="(item, index) in strengthsList" :key="`s-${index}`" class="insight-chip success-chip">{{ item }}</span>
                  </div>
                </div>

                <div class="analysis-card warn-card">
                  <div class="analysis-title-row">
                    <span class="analysis-dot warn-dot"></span>
                    <h4>关注点</h4>
                  </div>
                  <div class="chip-list">
                    <span v-for="(item, index) in gapsList" :key="`g-${index}`" class="insight-chip warn-chip">{{ item }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="section-career" class="report-section">
            <div class="section-header">
              <span class="section-badge">4</span>
              <div>
                <h3>职业建议</h3>
                <p>从推荐岗位方向与谨慎投递方向两个层面给出可执行建议。</p>
              </div>
            </div>

            <div class="career-layout">
              <div class="career-column">
                <div class="career-column-title positive-title">推荐岗位方向</div>
                <article v-for="(item, index) in careerRecommendations" :key="`r-${item.title}-${index}`" class="career-card">
                  <div class="career-marker positive-marker">{{ index + 1 }}</div>
                  <div class="career-body">
                    <div class="career-top">
                      <h4>{{ item.title }}</h4>
                      <span class="fit-badge">{{ item.fit_level }}</span>
                    </div>
                    <p class="career-reason">{{ item.reason }}</p>
                    <div class="career-action">
                      <span class="action-label">建议行动</span>
                      <span>{{ item.action }}</span>
                    </div>
                  </div>
                </article>
              </div>

              <div class="career-column">
                <div class="career-column-title caution-title">不建议优先投递方向</div>
                <article v-for="(item, index) in cautiousCareerRecommendations" :key="`c-${item.title}-${index}`" class="career-card caution-card">
                  <div class="career-marker caution-marker">!</div>
                  <div class="career-body">
                    <div class="career-top">
                      <h4>{{ item.title }}</h4>
                      <span class="fit-badge caution-badge">{{ item.fit_level }}</span>
                    </div>
                    <p class="career-reason">{{ item.reason }}</p>
                    <div class="career-action">
                      <span class="action-label">调整建议</span>
                      <span>{{ item.action }}</span>
                    </div>
                  </div>
                </article>
              </div>
            </div>
          </section>

          <section id="section-details" class="report-section">
            <div class="section-header">
              <span class="section-badge">5</span>
              <div>
                <h3>人格特质与岗位需求对照</h3>
                <p>将个人 TraitScores 与岗位期望进行对照，形成更细粒度的解释。</p>
              </div>
            </div>

            <div class="trait-summary-bar">
              <div class="summary-pill success-pill">
                <span class="pill-label">匹配良好</span>
                <span class="pill-value">{{ alignedTraitCount }}</span>
              </div>
              <div class="summary-pill warning-pill">
                <span class="pill-label">需要关注</span>
                <span class="pill-value">{{ watchTraitCount }}</span>
              </div>
              <div class="summary-pill neutral-pill">
                <span class="pill-label">基本均衡</span>
                <span class="pill-value">{{ balancedTraitCount }}</span>
              </div>
            </div>

            <div class="table-shell">
              <el-table :data="traitInsights" size="small" border>
                <el-table-column prop="name" label="特质维度" min-width="110" />
                <el-table-column label="我的分数" min-width="100">
                  <template #default="scope">{{ scope.row.score.toFixed(1) }}/10</template>
                </el-table-column>
                <el-table-column label="岗位期望" min-width="110">
                  <template #default="scope">{{ formatRequirement(scope.row.job_requirement) }}</template>
                </el-table-column>
                <el-table-column label="匹配状态" min-width="100">
                  <template #default="scope">
                    <el-tag :type="getMatchTagType(scope.row.match_status)" size="small">{{ getMatchStatusLabel(scope.row.match_status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="summary" label="分析解读" min-width="260" show-overflow-tooltip />
                <el-table-column prop="advice" label="建议" min-width="220" show-overflow-tooltip />
              </el-table>
            </div>
          </section>

          <section class="report-section dual-section">
            <div class="section-header">
              <span class="section-badge">6</span>
              <div>
                <h3>人格维度解读</h3>
                <p>以卡片方式概括每个大五维度在当前 Job Instance 中的含义。</p>
              </div>
            </div>

            <div class="trait-card-grid">
              <article v-for="item in traitInsights" :key="item.name" class="trait-card">
                <div class="trait-status-line" :class="`line-${item.match_status}`"></div>
                <div class="trait-card-top">
                  <div>
                    <div class="trait-card-name-row">
                      <div class="trait-card-name">{{ item.name }}</div>
                      <el-tag :type="getMatchTagType(item.match_status)" size="small" effect="plain">{{ getMatchStatusLabel(item.match_status) }}</el-tag>
                    </div>
                    <div class="trait-card-desc">{{ item.description }}</div>
                  </div>
                  <div class="trait-card-score">{{ item.score.toFixed(1) }}</div>
                </div>
                <p class="trait-card-summary">{{ item.summary }}</p>
                <div class="trait-card-foot">
                  <span class="trait-requirement">岗位期望：{{ formatRequirement(item.job_requirement) }}</span>
                  <span class="trait-advice">{{ item.advice }}</span>
                </div>
              </article>
            </div>
          </section>

          <section id="section-actions" class="report-section">
            <div class="section-header">
              <span class="section-badge">7</span>
              <div>
                <h3>发展行动建议</h3>
                <p>按照近期、中期与持续三个层次形成更便于落地执行的优化路径。</p>
              </div>
            </div>

            <div class="timeline-shell">
              <article v-for="(item, index) in developmentActions" :key="`${item.phase}-${index}`" class="timeline-item">
                <div class="timeline-line" :class="getActionTheme(item.phase)"></div>
                <div class="timeline-node" :class="getActionTheme(item.phase)"></div>
                <div class="timeline-phase" :class="getActionTheme(item.phase)">{{ item.phase }}</div>
                <div class="timeline-card">
                  <div class="timeline-title">{{ item.title }}</div>
                  <p>{{ item.description }}</p>
                </div>
              </article>
            </div>

            <div class="action-buttons">
              <el-button type="primary" @click="downloadReport">下载报告</el-button>
              <el-button @click="goHome">返回首页</el-button>
              <el-button type="text" @click="goReportList">查看历史报告</el-button>
            </div>
          </section>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="error-state">
      <EmptyState title="报告加载失败" text="无法找到对应的评估报告，请返回重试" />
      <el-button type="primary" @click="goBack">返回</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RadarChart from '@/components/RadarChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import { fetchReportDetail } from '@/utils/request'
import type {
  AssessmentReport,
  CareerRecommendationItem,
  DevelopmentActionItem,
  MatchDimension,
  TraitInsight,
  TraitScore,
} from '@/types/assessment'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const reportData = ref<AssessmentReport | null>(null)

const personalityTraits = computed<TraitScore[]>(() => reportData.value?.personality_trait || [])
const reportSections = computed(() => reportData.value?.report_sections)

const roleCount = computed(() => reportData.value?.assessement_details?.roles_participated?.length || 3)

const overviewInfoCards = computed(() => [
  { label: '评估岗位', value: reportData.value?.job_title || '-', icon: '户', theme: 'blue' },
  { label: '评估时间', value: formatTime(reportData.value?.created_at), icon: '时', theme: 'green' },
  { label: '评估模式', value: reportData.value?.assessment_mode || '多角色对话', icon: '模', theme: 'purple' },
  { label: '评估阶段数', value: `${roleCount.value} 个角色`, icon: '角', theme: 'orange' }
])

const ringDasharrayLarge = computed(() => {
  const circumference = 2 * Math.PI * 48
  const filled = ((reportData.value?.match_score || 0) / 100) * circumference
  return `${filled} ${circumference - filled}`
})

const matchDimensions = computed<MatchDimension[]>(() => {
  if (reportSections.value?.match_dimensions?.length) {
    return reportSections.value.match_dimensions
  }
  return [
    { label: '性格匹配', score: reportData.value?.match_score || 0, description: '基于人格特质的岗位适配结果。' },
    { label: '技能匹配', score: 50, description: '当前版本未返回细分技能匹配时的默认展示。' },
    { label: '综合匹配', score: reportData.value?.match_score || 0, description: '综合评估结果。' }
  ]
})

const overviewSummary = computed(() => {
  return reportSections.value?.overview_summary || reportData.value?.conversation_summary || '当前报告已形成基础评估结论，可结合人格分析与职业建议进一步理解匹配原因。'
})

const personalitySummary = computed(() => {
  return reportSections.value?.personality_summary || '系统基于大五人格模型，对候选人在当前岗位情境下的稳定特质进行结构化解释。'
})

const traitInsights = computed<TraitInsight[]>(() => {
  if (reportSections.value?.trait_insights?.length) {
    return reportSections.value.trait_insights
  }
  return personalityTraits.value.map((trait) => ({
    name: trait.name,
    score: trait.score,
    description: trait.description,
    job_requirement: null,
    match_status: 'balanced',
    summary: '该维度已有基础评估结果，但尚未生成更细粒度的岗位解释。',
    advice: '建议结合后续评估记录持续观察该维度在目标岗位中的表现。'
  }))
})

const alignedTraitCount = computed(() => traitInsights.value.filter((item) => item.match_status === 'aligned').length)
const watchTraitCount = computed(() => traitInsights.value.filter((item) => item.match_status === 'watch' || item.match_status === 'gap').length)
const balancedTraitCount = computed(() => traitInsights.value.filter((item) => item.match_status === 'balanced').length)

const careerRecommendations = computed<CareerRecommendationItem[]>(() => {
  if (reportSections.value?.career_recommendations?.length) {
    return reportSections.value.career_recommendations
  }
  return (reportData.value?.recommendations || []).map((item, index) => ({
    title: `建议 ${index + 1}`,
    fit_level: '通用建议',
    reason: item,
    action: '建议结合目标岗位继续补充项目案例和面试证据。'
  }))
})

const cautiousCareerRecommendations = computed<CareerRecommendationItem[]>(() => {
  if (reportSections.value?.cautious_career_recommendations?.length) {
    return reportSections.value.cautious_career_recommendations
  }
  return [
    {
      title: '需结合能力证据谨慎投递的岗位方向',
      fit_level: '谨慎尝试',
      reason: '当前报告未提供独立的回避方向判断时，系统默认建议优先投递与推荐方向一致的岗位实例。',
      action: '建议先提升目标岗位要求较高但当前证据不足的维度，再逐步扩展投递范围。'
    }
  ]
})

const developmentActions = computed<DevelopmentActionItem[]>(() => {
  if (reportSections.value?.development_actions?.length) {
    return reportSections.value.development_actions
  }
  return [
    {
      phase: '近期',
      title: '完善岗位案例表达',
      description: '围绕目标岗位准备 2 到 3 个完整案例，突出问题分析、协同推进与结果复盘。'
    },
    {
      phase: '中期',
      title: '补足薄弱特质对应能力',
      description: '针对当前报告中偏弱的维度，制定 4 周训练计划并观察复测结果。'
    },
    {
      phase: '持续',
      title: '定期复测并迭代投递策略',
      description: '持续记录不同岗位实例中的反馈表现，动态修正职业方向与能力提升重点。'
    }
  ]
})

const strengthsList = computed(() => {
  return reportData.value?.match_analysis?.strengths?.length
    ? reportData.value.match_analysis.strengths
    : ['当前报告以人格分析为主，建议结合后续多轮 AssessmentSession 持续补充优势证据。']
})

const gapsList = computed(() => {
  return reportData.value?.match_analysis?.gaps?.length
    ? reportData.value.match_analysis.gaps
    : ['当前报告未发现明确短板描述，建议重点关注特质对照中的“需关注”维度。']
})

function goBack() {
  router.back()
}

function goHome() {
  router.push('/home')
}

function goReportList() {
  router.push('/home/reports')
}

function downloadReport() {
  ElMessage.success('报告下载功能开发中')
}

function formatTime(dateString?: string): string {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

function formatRequirement(value?: number | null): string {
  if (value === null || value === undefined) return '未提供'
  return `${value.toFixed(1)}/10`
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

function getMatchLevel(score: number): string {
  if (score >= 85) return '高度匹配'
  if (score >= 70) return '良好匹配'
  if (score >= 55) return '中等匹配'
  return '待提升'
}

function getMatchStatusLabel(status: TraitInsight['match_status']): string {
  if (status === 'aligned') return '匹配良好'
  if (status === 'watch') return '需要关注'
  if (status === 'gap') return '存在差距'
  return '基本均衡'
}

function getMatchTagType(status: TraitInsight['match_status']): 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'aligned') return 'success'
  if (status === 'watch') return 'warning'
  if (status === 'gap') return 'danger'
  return 'info'
}

function getDimensionTheme(label: string) {
  if (label.includes('性格')) return 'theme-blue'
  if (label.includes('技能')) return 'theme-green'
  return 'theme-purple'
}

function getDimensionGradient(label: string) {
  if (label.includes('性格')) return 'linear-gradient(90deg, #4f8cff 0%, #72a9ff 100%)'
  if (label.includes('技能')) return 'linear-gradient(90deg, #20b486 0%, #5fd3a7 100%)'
  return 'linear-gradient(90deg, #7c5cff 0%, #9c7cff 100%)'
}

function getDimensionEmoji(label: string) {
  if (label.includes('性格')) return '人'
  if (label.includes('技能')) return '技'
  return '综'
}

function getActionTheme(phase: string) {
  if (phase === '近期') return 'phase-near'
  if (phase === '中期') return 'phase-mid'
  return 'phase-long'
}

async function loadReport() {
  loading.value = true
  try {
    const recordId = route.params.recordId as string
    reportData.value = await fetchReportDetail(recordId)
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.report-container {
  max-width: 1480px;
  margin: 0 auto;
  padding: 28px 24px 48px;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(93, 135, 255, 0.12), transparent 28%),
    radial-gradient(circle at top right, rgba(34, 197, 94, 0.08), transparent 24%),
    linear-gradient(180deg, #f6f8fc 0%, #eef3fb 100%);
}

.report-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 18px;
  margin-bottom: 26px;
}

.report-header :deep(.el-button) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #334155;
  border-radius: 999px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(217, 226, 240, 0.95);
  box-shadow: 0 8px 22px rgba(46, 72, 122, 0.08);
}

.report-header :deep(.el-button svg) {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.header-title-group h2 {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  color: #10213f;
  letter-spacing: -0.02em;
}

.header-title-group p {
  margin: 8px 0 0;
  color: #6b7a93;
  font-size: 14px;
}

.header-spacer {
  width: 48px;
}

.report-content {
  margin-top: 8px;
}

.report-layout {
  display: block;
}

.report-main {
  min-width: 0;
}

.report-section {
  margin-bottom: 18px;
  border-radius: 22px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(224, 231, 241, 0.95);
  box-shadow: 0 16px 38px rgba(35, 53, 87, 0.08);
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 18px;
}

.section-badge {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.24);
}

.section-header h3 {
  margin: 1px 0 4px;
  color: #14213d;
  font-size: 18px;
  font-weight: 800;
}

.section-header p {
  margin: 0;
  color: #72819a;
  font-size: 13px;
  line-height: 1.6;
}

.overview-info-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.overview-info-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid #ebf0f7;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
}

.overview-icon {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
}

.overview-icon.blue {
  background: #e8f0ff;
  color: #2f65eb;
}

.overview-icon.green {
  background: #eafaf2;
  color: #0f9f68;
}

.overview-icon.purple {
  background: #f0ecff;
  color: #7c4dff;
}

.overview-icon.orange {
  background: #fff1e8;
  color: #ea6c2f;
}

.overview-label {
  color: #7a879d;
  font-size: 12px;
}

.overview-value {
  margin-top: 4px;
  color: #14213d;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.45;
}

.match-overview-card {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
}

.match-main-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #fafdff 0%, #eef5ff 100%);
  border: 1px solid #dfe9fb;
}

.score-circle-large {
  position: relative;
  width: 170px;
  height: 170px;
}

.ring-svg-large {
  width: 100%;
  height: 100%;
}

.score-circle-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-percent {
  font-size: 38px;
  font-weight: 800;
  color: #2351d4;
  line-height: 1;
}

.score-level {
  margin-top: 8px;
  color: #1d3d8f;
  font-size: 14px;
  font-weight: 700;
}

.match-summary {
  margin-top: 16px;
  text-align: center;
}

.summary-kicker {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  background: #e8f0ff;
  color: #2d61df;
  font-size: 12px;
  font-weight: 700;
}

.summary-head h4 {
  margin: 10px 0 8px;
  color: #14213d;
  font-size: 18px;
  font-weight: 800;
}

.match-summary p {
  margin: 0;
  color: #6c7b93;
  line-height: 1.8;
  font-size: 13px;
}

.match-dimension-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.dimension-card {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid #ebf0f7;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
}

.dimension-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dimension-icon {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 800;
}

.dimension-icon.theme-blue {
  background: #e9f1ff;
  color: #2f65eb;
}

.dimension-icon.theme-green {
  background: #eafaf2;
  color: #16a16a;
}

.dimension-icon.theme-purple {
  background: #f1edff;
  color: #7d52ff;
}

.dimension-label {
  color: #708097;
  font-size: 12px;
}

.dimension-value {
  margin-top: 4px;
  color: #12203b;
  font-size: 24px;
  font-weight: 800;
}

.dimension-bar {
  height: 8px;
  margin: 14px 0 10px;
  border-radius: 999px;
  background: #edf2f8;
  overflow: hidden;
}

.dimension-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.dimension-card p {
  margin: 0;
  color: #72829c;
  font-size: 12px;
  line-height: 1.7;
}

.psychology-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 18px;
}

.radar-card,
.analysis-card,
.table-shell,
.timeline-shell {
  border-radius: 20px;
  border: 1px solid #ebf0f7;
  background: linear-gradient(180deg, #ffffff 0%, #fafcff 100%);
}

.radar-card {
  padding: 18px 18px 16px;
}

.panel-mini-title {
  margin-bottom: 10px;
  color: #5c6f8f;
  font-size: 13px;
  font-weight: 700;
}

.portrait-display :deep(.echarts-container) {
  width: 100%;
  height: 280px;
}

.summary-text {
  margin: 0;
  color: #6c7a93;
  font-size: 13px;
  line-height: 1.85;
}

.analysis-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-card {
  padding: 18px;
}

.good-card {
  background: linear-gradient(180deg, #fbfff8 0%, #f3fbf5 100%);
}

.warn-card {
  background: linear-gradient(180deg, #fffdfa 0%, #fff5ef 100%);
}

.analysis-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.analysis-title-row h4 {
  margin: 0;
  color: #14213d;
  font-size: 16px;
  font-weight: 800;
}

.analysis-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.good-dot {
  background: #22a06b;
}

.warn-dot {
  background: #f97316;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.insight-chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.success-chip {
  background: #e9f8ef;
  color: #157f51;
}

.warn-chip {
  background: #fff1e8;
  color: #cb5a1f;
}

.career-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.career-column-title {
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 800;
}

.positive-title {
  color: #145a36;
}

.caution-title {
  color: #a85012;
}

.career-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid #e8edf5;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
}

.career-column .career-card + .career-card {
  margin-top: 12px;
}

.caution-card {
  background: linear-gradient(180deg, #fffdf9 0%, #fff6ef 100%);
}

.career-marker {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
}

.positive-marker {
  background: #e8f1ff;
  color: #2f65eb;
}

.caution-marker {
  background: #fff0e6;
  color: #eb6b2d;
}

.career-body {
  min-width: 0;
  flex: 1;
}

.career-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.career-top h4 {
  margin: 0;
  color: #152340;
  font-size: 15px;
  font-weight: 800;
}

.fit-badge {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  background: #edf2ff;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 800;
}

.caution-badge {
  background: #ffedd5;
  color: #c2410c;
}

.career-reason {
  margin: 10px 0 0;
  color: #6d7a92;
  font-size: 13px;
  line-height: 1.8;
}

.career-action {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 14px;
  background: #f7faff;
  color: #516179;
  font-size: 12px;
  line-height: 1.7;
}

.action-label {
  color: #2747aa;
  font-weight: 800;
}

.table-shell {
  padding: 10px;
}

.trait-summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}

.summary-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.pill-label {
  opacity: 0.92;
}

.pill-value {
  min-width: 22px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
}

.success-pill {
  background: #eaf8ef;
  color: #157f51;
}

.warning-pill {
  background: #fff2e8;
  color: #cb5a1f;
}

.neutral-pill {
  background: #eef3fb;
  color: #4f5f7a;
}

.table-shell :deep(.el-table) {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #e6edf7;
  background: #fff;
}

.table-shell :deep(.el-table th.el-table__cell) {
  background: linear-gradient(180deg, #f7faff 0%, #f1f5fb 100%);
  color: #42526b;
  font-weight: 800;
  border-bottom: 1px solid #dde6f2;
}

.table-shell :deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid #edf2f8;
  color: #334155;
}

.table-shell :deep(.el-table--border::before),
.table-shell :deep(.el-table--border::after),
.table-shell :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.table-shell :deep(.el-table__row:hover > td.el-table__cell) {
  background: #f8fbff;
}

.trait-card-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.trait-card {
  position: relative;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid #e7edf6;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(39, 63, 105, 0.05);
}

.trait-status-line {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 4px;
}

.line-aligned {
  background: linear-gradient(90deg, #16a34a 0%, #4ade80 100%);
}

.line-watch {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.line-gap {
  background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
}

.line-balanced {
  background: linear-gradient(90deg, #64748b 0%, #94a3b8 100%);
}

.trait-card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.trait-card-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.trait-card-name {
  color: #16213d;
  font-size: 15px;
  font-weight: 800;
}

.trait-card-desc {
  margin-top: 6px;
  color: #7b89a0;
  font-size: 12px;
  line-height: 1.65;
}

.trait-card-score {
  min-width: 52px;
  text-align: right;
  color: #2563eb;
  font-size: 26px;
  font-weight: 800;
}

.trait-card-summary {
  margin: 14px 0 0;
  color: #68778f;
  font-size: 12px;
  line-height: 1.8;
}

.trait-card-foot {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #edf2f8;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trait-requirement {
  color: #2b4fb8;
  font-size: 12px;
  font-weight: 700;
}

.trait-advice {
  color: #6b7a92;
  font-size: 12px;
  line-height: 1.7;
}

.timeline-shell {
  position: relative;
  padding: 8px 8px 8px 22px;
}

.timeline-shell::before {
  content: '';
  position: absolute;
  left: 24px;
  top: 20px;
  bottom: 20px;
  width: 2px;
  background: linear-gradient(180deg, #d8e5fb 0%, #dfe8f5 100%);
}

.timeline-item {
  position: relative;
  display: grid;
  grid-template-columns: 8px 12px 72px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.timeline-item + .timeline-item {
  margin-top: 14px;
}

.timeline-line {
  width: 8px;
  height: 8px;
}

.timeline-node {
  position: relative;
  z-index: 1;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin-top: 6px;
  box-shadow: 0 0 0 5px #fff;
}

.timeline-phase {
  margin-top: 0;
  padding: 6px 10px;
  border-radius: 999px;
  text-align: center;
  font-size: 12px;
  font-weight: 800;
}

.timeline-card {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid #e8edf5;
  background: #fbfdff;
}

.timeline-title {
  color: #152340;
  font-size: 15px;
  font-weight: 800;
}

.timeline-card p {
  margin: 8px 0 0;
  color: #6d7b94;
  font-size: 13px;
  line-height: 1.8;
}

.phase-near.timeline-node,
.phase-near.timeline-line {
  background: #2563eb;
}

.phase-mid.timeline-node,
.phase-mid.timeline-line {
  background: #14b8a6;
}

.phase-long.timeline-node,
.phase-long.timeline-line {
  background: #f97316;
}

.phase-near.timeline-phase {
  background: #e8f0ff;
  color: #2559d3;
}

.phase-mid.timeline-phase {
  background: #e8fbf8;
  color: #0f9d8f;
}

.phase-long.timeline-phase {
  background: #fff1e8;
  color: #dc5d1b;
}

.action-buttons {
  margin-top: 18px;
  display: flex;
  gap: 10px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 320px;
}

@media (max-width: 1280px) {
  .overview-info-grid,
  .match-dimension-grid,
  .trait-card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .psychology-panel,
  .career-layout,
  .match-overview-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .report-container {
    padding: 18px 14px 36px;
  }

  .report-header {
    grid-template-columns: 1fr;
    justify-items: start;
  }

  .header-spacer {
    display: none;
  }

  .header-title-group h2 {
    font-size: 24px;
  }

  .overview-info-grid,
  .match-dimension-grid,
  .trait-card-grid {
    grid-template-columns: 1fr;
  }

  .trait-summary-bar {
    flex-direction: column;
  }

  .career-top,
  .trait-card-top {
    flex-direction: column;
  }

  .timeline-item {
    grid-template-columns: 0 12px 58px minmax(0, 1fr);
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
