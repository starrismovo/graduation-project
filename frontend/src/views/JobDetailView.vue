3<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { addHubJob, hasHubJob } from '@/utils/interviewHub'
import { getJobDetail } from '@/utils/request'

interface JobDetail {
  id: number
  name: string
  description: string
  company: string
  category: string
  city: string
  salary_min: number
  salary_max: number
  required_traits?: Record<string, number>
}

interface TraitConfig {
  key: string
  label: string
  description: string
  color: string
  icon: string
}

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const hubSaving = ref(false)
const jobDetail = ref<JobDetail | null>(null)
const alreadyInHub = ref(false)

const jobId = computed(() => Number(route.params.jobId))
const salaryText = computed(() => {
  if (!jobDetail.value) {
    return ''
  }

  return `${Math.round(jobDetail.value.salary_min)}k-${Math.round(jobDetail.value.salary_max)}k`
})

// 大五人格特质配置
const traitConfigMap: Record<string, TraitConfig> = {
  openness: {
    key: 'openness',
    label: '开放性',
    description: '代表对新想法、新经验的接受程度。高分表示富有想象力、创新意识强；低分表示实际、传统。',
    color: '#6B7FFF',
    icon: '🌟'
  },
  conscientiousness: {
    key: 'conscientiousness',
    label: '尽责性',
    description: '代表做事的谨慎程度和目标导向性。高分表示自律、有计划、可靠；低分表示灵活但可能缺乏条理。',
    color: '#FF6B9D',
    icon: '✓'
  },
  extraversion: {
    key: 'extraversion',
    label: '外向性',
    description: '代表社交倾向和活跃程度。高分表示热情、善交际、善表达；低分表示内敛、深思熟虑。',
    color: '#FFA500',
    icon: '💬'
  },
  agreeableness: {
    key: 'agreeableness',
    label: '宜人性',
    description: '代表与他人相处的方式。高分表示友善、合作、同情；低分表示竞争、批判、直率。',
    color: '#00D084',
    icon: '🤝'
  },
  neuroticism: {
    key: 'neuroticism',
    label: '神经质',
    description: '代表情绪稳定性。低分表示稳定、乐观、抗压；高分表示容易焦虑、敏感。',
    color: '#FF5252',
    icon: '⚡'
  }
}

// 岗位相关说明映射表
const traitImportanceMap: Record<string, string> = {
  openness: '在这个岗位中，需要不断学习新的技术、工具和方法，开放性强的人更容易适应变化，提出创新解决方案。',
  conscientiousness: '这个岗位需要严谨的态度和良好的自律性。尽责性强的人能够按时交付、细心处理细节、遵循流程。',
  extraversion: '需要与团队高效沟通和协作，或与客户交流。外向性强的人更善于表达、更容易融入团队。',
  agreeableness: '团队合作和良好的人际关系对这个岗位至关重要。宜人性强的人更易达成共识、解决冲突、促进团队凝聚力。',
  neuroticism: '岗位中需要面对压力和挑战。神经质低（即情绪稳定）的人能够更好地应对压力、保持冷静决策。'
}

const processedTraits = computed(() => {
  if (!jobDetail.value?.required_traits) return []
  
  return Object.entries(jobDetail.value.required_traits)
    .filter(([, value]) => value !== null && value !== undefined)
    .map(([key, value]) => {
      const config = traitConfigMap[key] || {
        key,
        label: key,
        description: '',
        color: '#999',
        icon: '•'
      }
      const score = typeof value === 'number' ? value : Number(value)
      return {
        ...config,
        score: Math.round(score * 10) / 10,
        percentage: Math.min(100, Math.max(0, (score / 10) * 100)),
        importance: traitImportanceMap[key] || '该岗位对这个特质有一定要求，能够帮助更好地表现。'
      }
    })
})

function getScoreExplanation(score: number): string {
  if (score >= 8) return '需要很强'
  if (score >= 6) return '需要较强'
  if (score >= 4) return '需要中等'
  if (score >= 2) return '需要一定程度'
  return '需要基础'
}

function getScoreLevel(score: number) {
  if (score >= 7) return { label: '高需求', color: '#DC2626', bg: 'rgba(254, 226, 226, 0.45)', barBg: 'rgba(254, 226, 226, 0.3)' }
  if (score >= 4) return { label: '中需求', color: '#D97706', bg: 'rgba(255, 237, 199, 0.45)', barBg: 'rgba(255, 237, 199, 0.3)' }
  return { label: '低需求', color: '#16A34A', bg: 'rgba(220, 252, 231, 0.45)', barBg: 'rgba(220, 252, 231, 0.3)' }
}

function formatTraitValue(value: unknown) {
  if (Array.isArray(value)) {
    return value.join('、')
  }

  if (typeof value === 'object' && value !== null) {
    return Object.entries(value as Record<string, unknown>)
      .map(([key, item]) => `${key}: ${String(item)}`)
      .join('；')
  }

  return String(value)
}

async function loadJobDetail() {
  if (!jobId.value) {
    ElMessage.error('岗位编号无效')
    router.replace('/home/jobs')
    return
  }

  loading.value = true
  try {
    const response = await getJobDetail(jobId.value)
    jobDetail.value = response.data?.data || response.data || null
  } catch (error) {
    console.error('加载岗位详情失败:', error)
    ElMessage.error('加载岗位详情失败')
  } finally {
    loading.value = false
  }
}

async function refreshHubStatus() {
  if (!jobId.value) {
    alreadyInHub.value = false
    return
  }
  alreadyInHub.value = await hasHubJob(jobId.value)
}

async function saveToHub() {
  if (!jobDetail.value) {
    return
  }

  hubSaving.value = true
  try {
    const success = await addHubJob({
      id: jobDetail.value.id,
      title: jobDetail.value.name,
      company: jobDetail.value.company,
      city: jobDetail.value.city,
      category: jobDetail.value.category,
      salary_min: jobDetail.value.salary_min,
      salary_max: jobDetail.value.salary_max
    })

    if (!success) {
      ElMessage.error('加入面试 Hub 失败，请稍后重试')
      return
    }

    alreadyInHub.value = true
    ElMessage.success('已加入我的面试 Hub')
    router.push({
      path: '/home/interviews',
      query: {
        tab: 'saved',
        highlightJobId: String(jobDetail.value.id)
      }
    })
  } finally {
    hubSaving.value = false
  }
}

function startInterview() {
  if (!jobDetail.value) {
    return
  }

  router.push({
    path: '/home/interviews/room',
    query: {
      jobId: String(jobDetail.value.id)
    }
  })
}

onMounted(async () => {
  await loadJobDetail()
  await refreshHubStatus()
})
</script>

<template>
  <div class="job-detail-page" v-loading="loading">
    <div class="detail-shell" v-if="jobDetail">
      <div class="detail-header">
        <div>
          <p class="eyebrow">Job Detail</p>
          <div class="title-row">
            <button class="back-icon-btn" type="button" aria-label="返回岗位列表" @click="router.push('/home/jobs')">
              <el-icon><ArrowLeft /></el-icon>
            </button>
            <h1>{{ jobDetail.name }}</h1>
          </div>
          <div class="headline-meta">
            <span>{{ jobDetail.company }}</span>
            <span>{{ jobDetail.city }}</span>
            <span>{{ salaryText }}</span>
            <span>{{ jobDetail.category }}</span>
          </div>
        </div>
      </div>

      <div class="summary-panel">
        <div class="summary-copy">
          <h2>先确认岗位，再决定进入哪条面试链路</h2>
          <p>你可以先把岗位加入 Hub，稍后统一管理；也可以从这里直接进入 AI 面试间，跳过 Hub 立即开始。</p>
        </div>

        <div class="summary-actions">
          <el-button type="primary" size="large" @click="startInterview">直接开始AI面试</el-button>
          <el-button size="large" plain :disabled="alreadyInHub || hubSaving" @click="saveToHub">
            {{ alreadyInHub ? '已在面试 Hub 中' : '加入我的面试 Hub' }}
          </el-button>
        </div>
      </div>

      <div class="content-grid">
        <el-card shadow="hover" class="detail-card">
          <template #header>
            <div class="card-title">岗位说明</div>
          </template>
          <div class="description-text">{{ jobDetail.description }}</div>
        </el-card>

        <el-card shadow="hover" class="detail-card">
          <template #header>
            <div class="card-title">岗位画像</div>
          </template>
          <div class="overview-list">
            <div class="overview-item">
              <span class="overview-label">岗位名称</span>
              <strong>{{ jobDetail.name }}</strong>
            </div>
            <div class="overview-item">
              <span class="overview-label">公司</span>
              <strong>{{ jobDetail.company }}</strong>
            </div>
            <div class="overview-item">
              <span class="overview-label">城市</span>
              <strong>{{ jobDetail.city }}</strong>
            </div>
            <div class="overview-item">
              <span class="overview-label">薪资范围</span>
              <strong>{{ salaryText }}</strong>
            </div>
          </div>
        </el-card>

        <el-card shadow="hover" class="detail-card traits-card">
          <template #header>
            <div class="card-title">
              <span class="title-icon">🎯</span>核心要求
            </div>
          </template>

          <div v-if="processedTraits.length === 0" style="padding: 40px; text-align: center; color: #999;">
            该岗位暂未配置结构化要求
          </div>

          <div v-else class="traits-container">
            <div class="traits-intro">
              <p>这个岗位对候选人的大五人格特质有特定要求。下方展示了每个维度的期望分数，以及为什么这些特质对该岗位很重要。</p>
            </div>
            
            <div class="trait-cards-grid">
              <div v-for="trait in processedTraits" :key="trait.key"
                class="trait-card-container"
                :style="{ backgroundColor: getScoreLevel(trait.score).bg }">
                <div class="trait-header" :style="{ borderTopColor: trait.color }">
                  <div class="trait-icon">{{ trait.icon }}</div>
                  <div class="trait-title-section">
                    <div>
                      <h3>{{ trait.label }}</h3>
                      <p class="trait-subtitle">{{ trait.description }}</p>
                    </div>
                    <div class="trait-badges">
                      <span class="score-level-badge" :style="{ color: getScoreLevel(trait.score).color, backgroundColor: getScoreLevel(trait.score).barBg, borderColor: getScoreLevel(trait.score).color }">
                        {{ getScoreLevel(trait.score).label }}
                      </span>
                      <div class="trait-score-badge" :style="{ color: trait.color, borderColor: trait.color }">{{ trait.score }}/10</div>
                    </div>
                  </div>
                </div>

                <div class="trait-content">
                  <div class="score-bar-section">
                    <div class="score-bar-label">
                      <span>期望强度</span>
                      <span class="score-explanation" :style="{ color: trait.color }">{{ getScoreExplanation(trait.score) }}</span>
                    </div>
                    <div class="score-bar-wrapper">
                      <div 
                        class="score-bar-fill" 
                        :style="{ 
                          width: trait.percentage + '%',
                          backgroundColor: trait.color
                        }"
                      />
                    </div>
                  </div>

                  <div class="trait-importance" :style="{ borderLeftColor: trait.color }">
                    <p class="importance-text">{{ trait.importance }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="traits-summary">
              <div class="summary-box">
                <h4>💡 如何理解这些要求？</h4>
                <ul>
                  <li><strong>8-10分：</strong>该特质对岗位至关重要，是核心素质要求</li>
                  <li><strong>6-7分：</strong>该特质很重要，能够帮助你更好地表现</li>
                  <li><strong>4-5分：</strong>该特质中等重要，具备基础能力即可</li>
                  <li><strong>0-3分：</strong>该特质要求较低或相对不重要</li>
                </ul>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <div v-else-if="!loading" style="display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 60px);">
      <div style="text-align: center;">
        <p style="font-size: 16px; color: #999; margin-bottom: 20px;">岗位不存在或已下线</p>
        <el-button type="primary" @click="router.push('/home/jobs')">返回岗位列表</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.job-detail-page {
  min-height: calc(100vh - 60px);
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(93, 124, 255, 0.14), transparent 28%),
    radial-gradient(circle at bottom right, rgba(255, 165, 0, 0.08), transparent 35%),
    linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
}

.detail-shell {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  margin-bottom: 24px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.back-icon-btn {
  width: 44px;
  height: 44px;
  border: 1px solid #d9dee8;
  border-radius: 0;
  background: #f3f5fa;
  color: #6b7280;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s ease;
  flex-shrink: 0;
}

.back-icon-btn:hover {
  border-color: #c9d2e3;
  background: #e9edf6;
  color: #374151;
}

.back-icon-btn :deep(.el-icon) {
  font-size: 20px;
}

.eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 13px;
  color: #6b7280;
}

.detail-header h1 {
  margin: 0;
  font-size: 38px;
  line-height: 1.1;
  color: #111827;
}

.headline-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.headline-meta span {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.06);
  color: #374151;
  font-size: 14px;
}

.summary-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 26px 28px;
  margin-bottom: 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, #111827 0%, #23314f 100%);
  color: #fff;
  box-shadow: 0 24px 50px rgba(17, 24, 39, 0.18);
}

.summary-copy h2 {
  margin: 0 0 10px;
  font-size: 26px;
}

.summary-copy p {
  margin: 0;
  max-width: 680px;
  color: rgba(255, 255, 255, 0.76);
  line-height: 1.7;
}

.summary-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 220px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.35fr 0.95fr;
  gap: 20px;
}

.detail-card {
  border-radius: 22px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.traits-card {
  grid-column: 1 / -1;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 20px;
}

.description-text {
  line-height: 1.85;
  white-space: pre-wrap;
  color: #475467;
}

.overview-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #edf2f7;
}

.overview-label {
  color: #667085;
}

/* ===== 大五人格特质样式 ===== */
.traits-container {
  padding: 8px;
}

.traits-intro {
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(107, 127, 255, 0.08) 0%, rgba(255, 165, 0, 0.08) 100%);
  border-radius: 16px;
  margin-bottom: 24px;
  border-left: 4px solid #6B7FFF;
}

.traits-intro p {
  margin: 0;
  color: #475467;
  line-height: 1.6;
  font-size: 14px;
}

.trait-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.trait-card-container {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #edf2f7;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.trait-card-container:hover {
  border-color: #d9dee8;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.trait-header {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-top: 4px solid;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 100%);
}

.trait-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.trait-title-section {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.trait-badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.score-level-badge {
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid;
  letter-spacing: 0.04em;
}

.trait-title-section h3 {
  margin: 0 0 4px;
  font-size: 17px;
  font-weight: 600;
  color: #111827;
}

.trait-subtitle {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.4;
  max-width: 180px;
}

.trait-score-badge {
  padding: 5px 10px;
  background: transparent;
  border-radius: 20px;
  font-size: 15px;
  font-weight: 700;
  border: 1.5px solid;
  white-space: nowrap;
  flex-shrink: 0;
}

.trait-content {
  padding: 20px;
}

.score-bar-section {
  margin-bottom: 20px;
}

.score-bar-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #667085;
  font-weight: 500;
}

.score-explanation {
  font-size: 13px;
  font-weight: 700;
}

.score-bar-wrapper {
  width: 100%;
  height: 8px;
  background: #edf2f7;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trait-importance {
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border-left: 3px solid #e5e7eb;
}

.importance-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #667085;
}

.traits-summary {
  margin-top: 24px;
}

.summary-box {
  padding: 20px;
  background: linear-gradient(135deg, #f0f4f8 0%, #eef3f9 100%);
  border-radius: 16px;
  border: 1px solid #e5e7eb;
}

.summary-box h4 {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.summary-box ul {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.summary-box li {
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #475467;
}

.summary-box li:last-child {
  margin-bottom: 0;
}

@media (max-width: 900px) {
  .detail-header,
  .summary-panel {
    flex-direction: column;
  }

  .content-grid,
  .trait-cards-grid {
    grid-template-columns: 1fr;
  }

  .summary-actions {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 640px) {
  .job-detail-page {
    padding: 20px;
  }

  .detail-header h1 {
    font-size: 30px;
  }

  .summary-panel {
    padding: 22px;
  }

  .trait-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .trait-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>