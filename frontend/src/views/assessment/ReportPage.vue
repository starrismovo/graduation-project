<template>
  <div class="report-container" v-loading="loading">
    <div class="report-header">
      <el-button type="text" @click="goBack">
        <el-icon>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" /><path d="M8 12h12" /></svg>
        </el-icon>
        返回
      </el-button>
      <h2>评估报告详情</h2>
      <div></div>
    </div>

    <div v-if="reportData" class="report-content">
      <div class="report-layout">
        <aside class="report-sidenav">
          <div class="sidenav-title">报告导航</div>
          <button
            v-for="item in sectionMenu"
            :key="item.key"
            class="sidenav-item"
            :class="{ active: activeSection === item.key }"
            @click="scrollToSection(item.key)"
          >
            <svg class="sidenav-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path v-if="item.key === 'overview'" d="M4 5h7v6H4zM13 5h7v4h-7zM13 11h7v8h-7zM4 13h7v6H4z" />
              <path v-else-if="item.key === 'psychology'" d="M8.5 14.5c0-1.7 1.4-3 3-3h1c1.7 0 3 1.3 3 3v1.5H8.5z" />
              <path v-else-if="item.key === 'psychology'" d="M10 9.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM16 10.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z" />
              <path v-else-if="item.key === 'capability'" d="M6 16h3v-8H6zM10.5 20h3v-12h-3zM15 13h3v7h-3z" />
              <path v-else-if="item.key === 'details'" d="M6 5v14M10 9v10M14 7v12M18 11v8" />
              <path v-else-if="item.key === 'suggestions'" d="M8 4h8v2h3v14H5V6h3z" />
              <path v-else-if="item.key === 'suggestions'" d="M9 10h6M9 14h6" />
              <path v-else d="M12 5a7 7 0 1 0 7 7" />
            </svg>
            <span>{{ item.label }}</span>
          </button>
        </aside>

        <div class="report-main">
          <el-row id="section-overview" :gutter="24" class="overview-section">
            <el-col :xs="24" :md="12">
              <el-card class="report-card" shadow="hover">
                <template #header>
                  <div class="card-title">评估基本信息</div>
                </template>
                <el-form label-width="100px" :model="reportData">
                  <el-form-item label="评估岗位"><span class="info-value">{{ reportData.job_title || '-' }}</span></el-form-item>
                  <el-form-item label="评估时间"><span class="info-value">{{ formatTime(reportData.created_at) }}</span></el-form-item>
                  <el-form-item label="评估模式"><el-tag>{{ reportData.assessment_mode || '多角色对话' }}</el-tag></el-form-item>
                  <el-form-item label="评估阶段数"><span class="info-value">{{ roleCount }} 个角色</span></el-form-item>
                </el-form>
              </el-card>
            </el-col>

            <el-col :xs="24" :md="12">
              <el-card class="report-card match-quick-view" shadow="hover">
                <template #header>
                  <div class="card-title">匹配度概览</div>
                </template>
                <div class="quick-match">
                  <div class="main-score">
                    <div class="score-circle-small">
                      <svg viewBox="0 0 100 100" class="ring-svg-small">
                        <circle cx="50" cy="50" r="40" fill="none" stroke="#e4e7ed" stroke-width="6" />
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          :stroke="getScoreColor(reportData.match_score || 0)"
                          stroke-width="6"
                          stroke-linecap="round"
                          :stroke-dasharray="ringDasharray"
                          transform="rotate(-90 50 50)"
                          class="ring-progress"
                        />
                      </svg>
                      <div class="score-text"><span class="main-num">{{ reportData.match_score || 0 }}%</span></div>
                    </div>
                    <div class="match-level">
                      <p class="level-label">{{ getMatchLevel(reportData.match_score || 0) }}</p>
                      <p class="level-desc">与岗位契合程度</p>
                    </div>
                  </div>
                  <div class="dimensions-mini">
                    <div class="mini-item"><span class="mini-label">性格匹配</span><span class="mini-value">{{ personalityMatchScore }}%</span></div>
                    <div class="mini-item"><span class="mini-label">技能匹配</span><span class="mini-value">{{ skillMatchScore }}%</span></div>
                    <div class="mini-item"><span class="mini-label">背景匹配</span><span class="mini-value">{{ educationMatchScore }}%</span></div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <div class="content-grid">
            <!-- 心理特质与能力亮点 -->
            <el-row :gutter="24" class="hero-row">
              <el-col :xs="24" :md="14" class="content-col">
                <el-card id="section-psychology" class="report-card report-card-main" shadow="hover">
                  <template #header>
                    <div class="card-title">心理特质</div>
                  </template>
                  <div class="portrait-display">
                    <RadarChart :data="personalityTraits" :height="240" />
                  </div>
                </el-card>
              </el-col>

              <el-col :xs="24" :md="10" class="content-col side-stack">
                <el-card id="section-capability" class="report-card" shadow="hover">
                  <template #header>
                    <div class="card-title">能力亮点</div>
                  </template>
                  <p class="summary-text">{{ reportData.conversation_summary || '综合表现稳定，建议持续强化可迁移能力。' }}</p>
                </el-card>

                <el-card id="section-suggestions" class="report-card" shadow="hover">
                  <template #header>
                    <div class="card-title">建议</div>
                  </template>
                  <div class="recommendations-list">
                    <div v-for="(item, index) in recommendations" :key="index" class="rec-item">
                      <div class="rec-num">{{ index + 1 }}</div>
                      <div class="rec-content">{{ item }}</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 岗位需求对比 -->
            <el-row :gutter="24" class="content-row">
              <el-col :xs="24" class="content-col">
                <el-card id="section-details" class="report-card" shadow="hover">
                  <template #header>
                    <div class="card-title">我的特质 vs 岗位需求</div>
                  </template>
                  <el-table :data="traitComparison" size="small" border>
                    <el-table-column prop="name" label="特质维度" min-width="100" />
                    <el-table-column label="我的分数" min-width="100">
                      <template #default="scope">{{ scope.row.myScore }}/10</template>
                    </el-table-column>
                    <el-table-column label="岗位需求" min-width="100">
                      <template #default="scope">{{ scope.row.requiredMin }}-{{ scope.row.requiredMax }}</template>
                    </el-table-column>
                    <el-table-column label="匹配" min-width="80">
                      <template #default="scope">
                        <el-tag :type="scope.row.matched ? 'success' : 'warning'" size="small">{{ scope.row.matched ? '✓' : '△' }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="分析" min-width="140">
                      <template #default="scope">{{ scope.row.analysis }}</template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>
            </el-row>

            <!-- 关键因素与下一步 -->
            <el-row :gutter="24" class="content-row history-row">
              <el-col :xs="24" :md="12" class="content-col">
                <el-card class="report-card" shadow="hover">
                  <template #header>
                    <div class="card-title">岗位匹配的关键因素</div>
                  </template>
                  <div class="key-factors-list">
                    <div v-for="factor in keyFactors" :key="factor.name" class="factor-item">
                      <div class="factor-header">
                        <span class="factor-name">{{ factor.name }}</span>
                        <span class="factor-level" :style="{ color: factor.color }">{{ factor.level }}</span>
                      </div>
                      <div class="factor-progress">
                        <div class="progress-bar-container">
                          <div class="progress-bar" :style="{ width: factor.score * 10 + '%', backgroundColor: factor.color }"></div>
                        </div>
                        <span class="progress-text">{{ factor.score.toFixed(1) }}/10</span>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-col>

              <el-col :xs="24" :md="12" class="content-col">
                <el-card class="report-card" shadow="hover">
                  <template #header>
                    <div class="card-title">下一步</div>
                  </template>
                  <p style="color: #475569; margin: 0; line-height: 1.8;">
                    根据评估结果，建议你：<br>
                    1. 关注心理特质评分低于岗位需求的维度<br>
                    2. 有针对性地参加培训课程<br>
                    3. 定期复测以追踪进展
                  </p>

                  <div class="action-buttons">
                    <el-button type="primary" @click="downloadReport">下载报告</el-button>
                    <el-button @click="goHome">返回首页</el-button>
                    <el-button type="text" @click="goReportList">查看历史报告</el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RadarChart from '@/components/RadarChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import { fetchReportDetail } from '@/utils/request'

type Trait = { name: string; score: number }

interface ReportData {
  job_title?: string
  created_at?: string
  assessment_mode?: string
  match_score?: number
  conversation_summary?: string
  personality_trait?: Trait[]
  portrait?: Trait[]
  recommendations?: string[]
  assessement_details?: {
    roles_participated?: string[]
  }
}

interface TraitComparisonItem {
  name: string
  myScore: number
  requiredMin: number
  requiredMax: number
  matched: boolean
  analysis: string
}

interface KeyFactor {
  name: string
  score: number
  level: string
  color: string
}

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const reportData = ref<ReportData | null>(null)
const traitComparison = ref<TraitComparisonItem[]>([])
const personalityMatchScore = ref(0)
const skillMatchScore = ref(76)
const educationMatchScore = ref(82)
const ringDasharray = ref('0 314')
const keyFactors = ref<KeyFactor[]>([])

const sectionMenu = [
  { key: 'overview', label: '报告概览' },
  { key: 'psychology', label: '心理特质' },
  { key: 'capability', label: '能力亮点' },
  { key: 'details', label: '特质对比' },
  { key: 'suggestions', label: '建议' }
]

const activeSection = ref('overview')
const scrollContainer = ref<HTMLElement | Window>(window)

const personalityTraits = computed<Trait[]>(() => reportData.value?.personality_trait || reportData.value?.portrait || [])

const roleCount = computed(() => reportData.value?.assessement_details?.roles_participated?.length || 3)

const recommendations = computed(() => {
  if (reportData.value?.recommendations?.length) {
    return reportData.value.recommendations
  }
  return [
    '继续强化高匹配维度，形成稳定优势。',
    '围绕差距维度制定4周训练计划。',
    '每两周复盘一次面试表现，持续校准方向。'
  ]
})

const phaseHighlight = computed(() => getPhaseHighlight('hr'))

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

function getScoreColor(score: number): string {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

function getTraitColor(score: number): string {
  if (score >= 8) return '#67c23a'
  if (score >= 6) return '#409eff'
  if (score >= 4) return '#e6a23c'
  return '#f56c6c'
}

function getMatchLevel(score: number): string {
  if (score >= 85) return '高度匹配'
  if (score >= 70) return '良好匹配'
  if (score >= 55) return '中等匹配'
  return '待提升'
}

function getPhaseHighlight(_phase: string): string {
  return reportData.value?.conversation_summary || '在模拟面试中展现了较强的表达与理解能力，整体节奏稳定。'
}

function getFactorLevel(score: number): { level: string; color: string } {
  if (score >= 8) return { level: '优秀', color: '#67c23a' }
  if (score >= 6.5) return { level: '良好', color: '#409eff' }
  if (score >= 5) return { level: '中等', color: '#e6a23c' }
  return { level: '待提升', color: '#f56c6c' }
}

function generateTraitComparison() {
  const traits = personalityTraits.value
  if (!traits.length) {
    traitComparison.value = []
    personalityMatchScore.value = 0
    keyFactors.value = []
    return
  }

  const jobRequirements: Record<string, { min: number; max: number }> = {
    外向性: { min: 6, max: 9 },
    宜人性: { min: 6, max: 9 },
    尽责性: { min: 7, max: 10 },
    神经质: { min: 0, max: 5 },
    开放性: { min: 6, max: 10 }
  }

  traitComparison.value = traits.map((trait) => {
    const req = jobRequirements[trait.name] || { min: 5, max: 8 }
    const score = Number(trait.score || 0)
    const matched = score >= req.min && score <= req.max
    const analysis = matched ? '该维度符合岗位心理画像要求。' : '该维度与岗位区间存在差距，建议专项训练。'

    return {
      name: trait.name,
      myScore: Number(score.toFixed(1)),
      requiredMin: req.min,
      requiredMax: req.max,
      matched,
      analysis
    }
  })

  const matchedCount = traitComparison.value.filter((item) => item.matched).length
  personalityMatchScore.value = Math.round((matchedCount / traitComparison.value.length) * 100)

  const circumference = 2 * Math.PI * 40
  const filled = ((reportData.value?.match_score || 0) / 100) * circumference
  ringDasharray.value = `${filled} ${circumference - filled}`

  // 计算三大关键因素（基于人格特质）
  const expressiveness = (traitComparison.value.find((t) => t.name === '外向性')?.myScore || 5) + 0.5
  const execution = (traitComparison.value.find((t) => t.name === '尽责性')?.myScore || 5) + 0.3
  const learning = (traitComparison.value.find((t) => t.name === '开放性')?.myScore || 5) + 0.2

  keyFactors.value = [
    {
      name: '表达能力',
      score: Math.min(10, Math.max(0, expressiveness)),
      ...getFactorLevel(expressiveness)
    },
    {
      name: '执行力',
      score: Math.min(10, Math.max(0, execution)),
      ...getFactorLevel(execution)
    },
    {
      name: '学习能力',
      score: Math.min(10, Math.max(0, learning)),
      ...getFactorLevel(learning)
    }
  ]
}

async function loadReport() {
  loading.value = true
  try {
    const recordId = route.params.recordId as string
    reportData.value = await fetchReportDetail(recordId)
    generateTraitComparison()
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

function scrollToSection(key: string) {
  const el = document.getElementById(`section-${key}`)
  if (!el) return

  const container = scrollContainer.value
  const targetOffset = 90

  if (container === window) {
    const top = el.getBoundingClientRect().top + window.scrollY - targetOffset
    window.scrollTo({ top, behavior: 'smooth' })
  } else {
    const containerEl = container as HTMLElement
    const containerRect = containerEl.getBoundingClientRect()
    const elementRect = el.getBoundingClientRect()
    const top = containerEl.scrollTop + (elementRect.top - containerRect.top) - targetOffset
    containerEl.scrollTo({ top, behavior: 'smooth' })
  }

  activeSection.value = key
}

function updateActiveSectionByScroll() {
  const keys = sectionMenu.map((item) => item.key)
  const offset = 130
  const container = scrollContainer.value
  const containerTop = container === window ? 0 : (container as HTMLElement).getBoundingClientRect().top

  for (let i = keys.length - 1; i >= 0; i -= 1) {
    const el = document.getElementById(`section-${keys[i]}`)
    if (el && el.getBoundingClientRect().top - containerTop <= offset) {
      activeSection.value = keys[i]
      return
    }
  }

  activeSection.value = 'overview'
}

onMounted(async () => {
  await loadReport()
  await nextTick()
  scrollContainer.value = (document.querySelector('.app-main') as HTMLElement) || window
  scrollContainer.value.addEventListener('scroll', updateActiveSectionByScroll as EventListener, { passive: true })
  updateActiveSectionByScroll()
})

onBeforeUnmount(() => {
  scrollContainer.value.removeEventListener('scroll', updateActiveSectionByScroll as EventListener)
})
</script>

<style scoped>
.report-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.report-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 24px;
  font-weight: 700;
}

.report-header :deep(.el-button) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #334155;
}

.report-header :deep(.el-button svg),
.card-title :deep(svg) {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.report-content {
  margin-top: 12px;
}

.report-layout {
  display: grid;
  grid-template-columns: 196px minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.report-sidenav {
  position: sticky;
  top: 90px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
  border: 1px solid #ebeff7;
  border-radius: 14px;
  padding: 14px 12px;
  box-shadow: 0 8px 28px rgba(29, 45, 94, 0.06);
}

.sidenav-title {
  font-size: 12px;
  color: #a0aec0;
  letter-spacing: 0.6px;
  margin-bottom: 8px;
  padding: 0 10px;
}

.sidenav-item {
  width: 100%;
  border: 0;
  background: transparent;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-radius: 12px;
  color: #5f6e86;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.22s ease;
}

.sidenav-item:hover {
  background: #f5f7fc;
  color: #4d5f86;
}

.sidenav-item.active {
  background: #eef2ff;
  color: #5c72f2;
  font-weight: 600;
  box-shadow: inset 0 0 0 1px #e3e9ff;
}

.sidenav-icon {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
  opacity: 0.95;
}

.report-main {
  min-width: 0;
}

.overview-section {
  margin-bottom: 24px;
}

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-row,
.content-row,
.history-row {
  margin-bottom: 0;
}

.side-stack {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-card {
  margin-bottom: 0;
  border: 1px solid #e8edf5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #fff;
  border-radius: 10px;
  transition: all 0.25s ease;
  overflow: hidden;
}

.report-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: #d0dce6;
  transform: translateY(-2px);
}

.report-card-main {
  border-color: #d7e4fb;
  box-shadow: 0 6px 20px rgba(30, 64, 175, 0.12);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.report-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
  background: #fafbfc;
}

.report-card :deep(.el-card__body) {
  padding: 20px;
}

.info-value {
  color: #334155;
  font-weight: 500;
}

.quick-match {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.main-score {
  display: flex;
  align-items: center;
  gap: 14px;
}

.score-circle-small {
  position: relative;
  width: 108px;
  height: 108px;
}

.ring-svg-small {
  width: 100%;
  height: 100%;
}

.score-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-num {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}

.level-label {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
  font-weight: 600;
}

.level-desc {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
}

.dimensions-mini {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.mini-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini-label {
  color: #64748b;
  font-size: 12px;
}

.mini-value {
  color: #1e40af;
  font-size: 16px;
  font-weight: 700;
}

.portrait-display :deep(.echarts-container) {
  width: 100%;
  height: 240px;
  margin-bottom: 0;
}

.traits-summary {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
  margin-top: 16px;
}

.match-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fc;
  border-radius: 8px;
}

.breakdown-label {
  color: #475569;
  font-size: 14px;
  font-weight: 500;
}

.breakdown-value {
  color: #5c72f2;
  font-size: 20px;
  font-weight: 700;
}

.key-factors-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.factor-item {
  padding: 14px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5fe 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.factor-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.factor-name {
  color: #2c3e50;
  font-size: 15px;
  font-weight: 600;
}

.factor-level {
  font-size: 13px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(99, 179, 237, 0.1);
}

.factor-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar-container {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-text {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  min-width: 45px;
  text-align: right;
}

.traits-summary h4 {
  margin: 0 0 12px;
  color: #2c3e50;
  font-size: 13px;
  font-weight: 600;
}

.traits-list-compact {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trait-item-compact {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trait-name {
  min-width: 70px;
  font-size: 12px;
  color: #2c3e50;
  font-weight: 500;
}

.trait-score {
  min-width: 56px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
}

.summary-text,
.phase-text-compact,
.analysis-section p,
.history-tip {
  color: #475569;
  line-height: 1.7;
  margin: 0;
}

.phase-info-compact {
  margin-bottom: 12px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-section h4 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 8px;
  font-size: 14px;
  color: #1f2937;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rec-item {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border: 1px solid #e8edf5;
  border-left: 3px solid #3b82f6;
  border-radius: 8px;
}

.rec-num {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-content {
  color: #334155;
  line-height: 1.65;
}

.next-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #eaf2ff;
  color: #1d4ed8;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}

.step-content h4 {
  margin: 0;
  color: #1f2937;
  font-size: 14px;
}

.step-content p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.action-buttons {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}

.history-btn {
  margin-top: 14px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 300px;
}

@media (max-width: 1200px) {
  .report-layout {
    grid-template-columns: 1fr;
  }

  .report-sidenav {
    position: static;
    margin-bottom: 8px;
  }

  .content-grid,
  .side-stack {
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .report-container {
    padding: 14px;
  }

  .report-header h2 {
    font-size: 20px;
  }

  .dimensions-mini {
    grid-template-columns: 1fr;
  }

  .main-score {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-buttons {
    flex-direction: column;
  }

  .content-grid,
  .side-stack {
    gap: 16px;
  }
}
</style>
