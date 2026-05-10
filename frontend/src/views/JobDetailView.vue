3<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Briefcase, CollectionTag, Location, OfficeBuilding } from '@element-plus/icons-vue'
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
          <p class="eyebrow">Role Insight</p>
          <div class="title-row">
            <button class="back-icon-btn" type="button" aria-label="返回岗位列表" @click="router.push('/home/jobs')">
              <el-icon><ArrowLeft /></el-icon>
            </button>
            <h1>{{ jobDetail.name }}</h1>
          </div>
          <div class="headline-meta">
            <span><el-icon><OfficeBuilding /></el-icon>{{ jobDetail.company }}</span>
            <span><el-icon><Location /></el-icon>{{ jobDetail.city }}</span>
            <span><el-icon><Briefcase /></el-icon>{{ salaryText }}</span>
            <span><el-icon><CollectionTag /></el-icon>{{ jobDetail.category }}</span>
          </div>
        </div>
      </div>

      <div class="summary-panel">
        <div class="summary-copy">
          <h2>先确认岗位，再决定进入哪条面试链路</h2>
          <p>你可以先把岗位加入面试中心，稍后统一管理；也可以从这里直接进入 AI 面试间，即刻开始。</p>
        </div>

        <div class="summary-actions">
          <el-button class="action-btn primary-action" type="primary" size="large" @click="startInterview">直接开始AI面试</el-button>
          <el-button class="action-btn secondary-action" size="large" plain :disabled="alreadyInHub || hubSaving" @click="saveToHub">
            {{ alreadyInHub ? '已在面试中心中' : '加入我的面试中心' }}
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
          <div class="overview-list overview-grid">
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
  padding: 24px 28px 32px;
  background:
    radial-gradient(circle at top left, rgba(93, 124, 255, 0.16), transparent 28%),
    radial-gradient(circle at top right, rgba(124, 77, 255, 0.1), transparent 24%),
    linear-gradient(180deg, #f7f9ff 0%, #eef4ff 100%);
}

.detail-shell {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  margin-bottom: 24px;
  padding: 8px 4px 0;
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
  border: 1px solid rgba(210, 221, 255, 0.95);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  color: #5b67ff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.22s ease;
  flex-shrink: 0;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.back-icon-btn:hover {
  border-color: #c7d2fe;
  background: #ffffff;
  color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(91, 103, 255, 0.14);
}

.back-icon-btn :deep(.el-icon) {
  font-size: 20px;
}

.eyebrow {
  margin: 0 0 8px;
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  letter-spacing: 0.1em;
  font-size: 13px;
  font-weight: 700;
  color: #5b67ff;
  background: rgba(91, 103, 255, 0.12);
}

.detail-header h1 {
  margin: 0;
  font-size: 40px;
  line-height: 1.08;
  color: #172133;
  letter-spacing: -0.04em;
}

.headline-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.headline-meta span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  color: #475569;
  font-size: 14px;
  border: 1px solid rgba(223, 230, 250, 0.95);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
}

.headline-meta span :deep(.el-icon) {
  color: #5b67ff;
}

.summary-panel {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 26px 28px;
  margin-bottom: 24px;
  border-radius: 28px;
  background:
    radial-gradient(circle at right top, rgba(255, 255, 255, 0.14), transparent 28%),
    linear-gradient(135deg, #7c89c5 100%, #243b7a 46%, #6a48ff 100%);
  color: #fff;
  box-shadow: 0 24px 50px rgba(36, 59, 122, 0.2);
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
  justify-content: center;
}

.summary-actions :deep(.el-button),
.job-detail-page > div[style] :deep(.el-button) {
  height: 48px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 700;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.summary-actions :deep(.el-button:hover),
.job-detail-page > div[style] :deep(.el-button:hover) {
  transform: translateY(-1px);
}

.summary-actions :deep(.primary-action),
.job-detail-page :deep(.primary-action) {
  border: none;
  background: linear-gradient(90deg, #4da0ff 0%, #6d4bff 100%);
  box-shadow: 0 14px 30px rgba(84, 104, 255, 0.3);
}

.summary-actions :deep(.primary-action:hover),
.job-detail-page :deep(.primary-action:hover) {
  background: linear-gradient(90deg, #4697f6 0%, #6343f0 100%);
  box-shadow: 0 18px 34px rgba(84, 104, 255, 0.35);
}

.summary-actions :deep(.secondary-action) {
  border-color: rgba(183, 201, 255, 0.9);
  background: rgba(255, 255, 255, 0.96);
  color: #24324a;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.summary-actions :deep(.secondary-action:hover) {
  border-color: #8faeff;
  background: #ffffff;
  color: #172133;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.35fr 0.95fr;
  gap: 20px;
}

.detail-card {
  border-radius: 24px;
  border: 1px solid rgba(223, 230, 250, 0.95);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.detail-card :deep(.el-card__header) {
  padding: 20px 24px 14px;
  border-bottom: 1px solid rgba(235, 240, 251, 0.95);
  background: linear-gradient(180deg, rgba(248, 250, 255, 0.9), rgba(255, 255, 255, 0.72));
}

.detail-card :deep(.el-card__body) {
  padding: 22px 24px 24px;
}

.traits-card {
  grid-column: 1 / -1;
}

.card-title {
  font-size: 19px;
  font-weight: 700;
  color: #172133;
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

.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.overview-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 112px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(234, 238, 251, 0.95);
  background: linear-gradient(180deg, rgba(250, 251, 255, 0.98), rgba(245, 248, 255, 0.98));
}

.overview-label {
  color: #667085;
  font-size: 13px;
}

.overview-item strong {
  font-size: 17px;
  line-height: 1.5;
  color: #172133;
}

/* ===== 大五人格特质样式 ===== */
.traits-container {
  padding: 8px;
}

.traits-intro {
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(107, 127, 255, 0.08) 0%, rgba(124, 77, 255, 0.06) 100%);
  border-radius: 18px;
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
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(234, 238, 251, 0.95);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
}

.trait-card-container:hover {
  border-color: #d9e1fb;
  box-shadow: 0 18px 36px rgba(84, 104, 255, 0.12);
  transform: translateY(-3px);
}

.trait-header {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-top: 4px solid;
  background: linear-gradient(135deg, rgba(248, 250, 255, 0.95) 0%, rgba(240, 244, 255, 0.9) 100%);
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
  background: rgba(255, 255, 255, 0.72);
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
  background: #edf2ff;
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
  background: linear-gradient(180deg, rgba(248, 250, 255, 0.96), rgba(243, 246, 255, 0.96));
  border-radius: 14px;
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
  background: linear-gradient(135deg, #f5f8ff 0%, #eef3ff 100%);
  border-radius: 18px;
  border: 1px solid rgba(223, 230, 250, 0.95);
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
  .overview-grid,
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
    padding: 18px 14px 24px;
  }

  .detail-header h1 {
    font-size: 30px;
  }

  .summary-panel {
    padding: 22px 20px;
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
