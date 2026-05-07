<template>
  <div class="job-card" @click="handleClick">
    <div class="card-glow"></div>

    <div class="card-top">
      <div class="title-wrap">
        <span class="job-badge">推荐岗位</span>
        <h3 class="job-title">{{ job.name || job.title || '未知岗位' }}</h3>
        <div class="company-row">
          <svg class="row-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M3 0a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V2a2 2 0 00-2-2H3zm1 3h2v2H4V3zm0 4h2v2H4V7zm0 4h2v2H4v-2zm4-8h2v2H8V3zm0 4h2v2H8V7zm0 4h2v2H8v-2z"/></svg>
          <span>{{ job.company || '未知公司' }}</span>
        </div>
      </div>

      <button
        class="card-like-btn"
        :class="{ active: isSaved }"
        @click.stop="toggleSavedJob"
        :disabled="savingStatus"
        :title="isSaved ? '取消收藏' : '加入收藏'"
      >
        <svg class="like-icon" viewBox="0 0 24 24" :fill="isSaved ? 'currentColor' : 'none'" :stroke="isSaved ? 'none' : 'currentColor'">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </button>
    </div>

    <div class="score-band" v-if="job.match_score">
      <span>匹配度</span>
      <strong>{{ Math.round(job.match_score) }}%</strong>
    </div>

    <div class="tag-row">
      <span class="tag tag-city" v-if="job.city">
        <svg class="tag-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0a5 5 0 00-5 5c0 4.5 5 11 5 11s5-6.5 5-11a5 5 0 00-5-5zm0 7a2 2 0 110-4 2 2 0 010 4z"/></svg>
        {{ job.city }}
      </span>
      <span class="tag tag-category" v-if="job.category && job.category !== '全职'">{{ job.category }}</span>
      <span class="tag tag-salary" v-if="job.salary || (job.salary_min && job.salary_max)">
        {{ job.salary || `${Math.round(job.salary_min!)}K-${Math.round(job.salary_max!)}K` }}
      </span>
    </div>

    <p class="job-desc" v-if="job.description">{{ truncateText(job.description, 72) }}</p>

    <div class="card-footer">
      <button class="ghost-btn" type="button" @click.stop="handleClick">查看信息</button>
      <button class="assess-btn" @click.stop="$emit('assess', job.id)">
        查看详情
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { addHubJob, removeHubJob, hasHubJob } from '@/utils/interviewHub'

interface Job {
  id: number | string
  name?: string
  title?: string
  company?: string
  city?: string
  category?: string
  salary?: string
  salary_min?: number
  salary_max?: number
  description?: string
  applied?: boolean
  match_score?: number
  [key: string]: any
}

const props = defineProps<{
  job: Job
}>()

const emit = defineEmits<{
  (e: 'assess', jobId: number | string): void
  (e: 'click'): void
  (e: 'save-toggle', jobId: number | string, isSaved: boolean): void
}>()

const isSaved = ref(false)
const savingStatus = ref(false)

onMounted(async () => {
  const jobId = Number(props.job.id || props.job.jobId)
  isSaved.value = await hasHubJob(jobId)
})

function handleClick() {
  emit('click')
}

async function toggleSavedJob() {
  const jobId = Number(props.job.id || props.job.jobId)

  savingStatus.value = true
  try {
    if (isSaved.value) {
      await removeHubJob(jobId)
      isSaved.value = false
    } else {
      const success = await addHubJob(props.job)
      if (success) {
        isSaved.value = true
      }
    }
    emit('save-toggle', props.job.id, isSaved.value)
  } catch (error) {
    console.error('切换收藏状态失败:', error)
  } finally {
    savingStatus.value = false
  }
}

function truncateText(text: string, length: number): string {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}
</script>

<style scoped>
.job-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 186px;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgba(227, 233, 255, 0.95);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 248, 255, 0.96));
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.job-card:hover {
  transform: translateY(-2px);
  border-color: #dbe2ff;
  box-shadow: 0 14px 28px rgba(99, 102, 241, 0.09);
}

.card-glow {
  position: absolute;
  top: -40px;
  right: -30px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.18), rgba(99, 102, 241, 0));
  pointer-events: none;
}

.card-top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.title-wrap {
  min-width: 0;
}

.job-badge {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 8px;
  margin-bottom: 8px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.1);
  color: #5b67ff;
  font-size: 10px;
  font-weight: 700;
}

.job-title {
  margin: 0;
  font-size: 16px;
  line-height: 1.3;
  font-weight: 700;
  color: #172033;
  letter-spacing: -0.03em;
}

.company-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  color: #68758d;
  font-size: 12px;
}

.row-icon {
  width: 14px;
  height: 14px;
}

.card-like-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e7ebff;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9aa4bb;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.card-like-btn:hover:not(.active) {
  color: #ef4444;
  border-color: #fecaca;
}

.card-like-btn.active {
  background: linear-gradient(135deg, #ff6b7a, #ff4d6d);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 12px 22px rgba(255, 77, 109, 0.26);
}

.card-like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-icon {
  width: 15px;
  height: 15px;
  stroke-width: 2;
}

.score-band {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 8px 10px;
  margin-top: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(90, 103, 255, 0.08), rgba(139, 92, 246, 0.1));
}

.score-band span {
  color: #67748e;
  font-size: 11px;
}

.score-band strong {
  font-size: 16px;
  color: #5b67ff;
  letter-spacing: -0.03em;
}

.tag-row {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.tag-icon {
  width: 10px;
  height: 10px;
}

.tag-city {
  color: #2563eb;
  background: #dbeafe;
}

.tag-category {
  color: #0f766e;
  background: #ccfbf1;
}

.tag-salary {
  color: #b45309;
  background: #fef3c7;
}

.job-desc {
  position: relative;
  z-index: 1;
  flex: 1;
  margin: 10px 0 0;
  color: #69778f;
  font-size: 12px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.ghost-btn,
.assess-btn {
  height: 34px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ghost-btn {
  flex: 1;
  border: 1px solid #dbe2ff;
  background: rgba(255, 255, 255, 0.78);
  color: #4b5563;
}

.ghost-btn:hover {
  border-color: #bcc8ff;
  color: #374151;
}

.assess-btn {
  flex: 1.2;
  border: none;
  background: linear-gradient(135deg, #5766ff 0%, #865dff 100%);
  color: #fff;
  box-shadow: 0 14px 26px rgba(91, 103, 255, 0.2);
}

.assess-btn:hover {
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .job-card {
    min-height: auto;
    padding: 14px;
  }

  .job-title {
    font-size: 15px;
  }

  .card-footer {
    flex-direction: column;
  }
}
</style>
