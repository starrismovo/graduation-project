<script setup lang="ts">
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
  required_traits?: Record<string, unknown>
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
const traitEntries = computed(() => Object.entries(jobDetail.value?.required_traits || {}))

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
            <div class="card-title">核心要求</div>
          </template>

          <el-empty v-if="traitEntries.length === 0" description="该岗位暂未配置结构化要求" />

          <div v-else class="trait-list">
            <div v-for="([key, value], index) in traitEntries" :key="key" class="trait-item">
              <span class="trait-index">{{ index + 1 }}</span>
              <div>
                <strong>{{ key }}</strong>
                <p>{{ formatTraitValue(value) }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <el-empty v-else-if="!loading" description="岗位不存在或已下线">
      <el-button type="primary" @click="router.push('/home/jobs')">返回岗位列表</el-button>
    </el-empty>
  </div>
</template>

<style scoped>
.job-detail-page {
  min-height: calc(100vh - 60px);
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(93, 124, 255, 0.14), transparent 28%),
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
}

.traits-card {
  grid-column: 1 / -1;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
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

.trait-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.trait-item {
  display: flex;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  background: #f8fafc;
}

.trait-index {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 700;
}

.trait-item p {
  margin: 8px 0 0;
  color: #667085;
  line-height: 1.7;
}

@media (max-width: 900px) {
  .detail-header,
  .summary-panel {
    flex-direction: column;
  }

  .content-grid,
  .trait-list {
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
}
</style>