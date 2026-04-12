<template>
  <div class="job-card" @click="handleClick">
    <!-- 薪资角标 -->
    <div class="salary-badge" v-if="job.salary || (job.salary_min && job.salary_max)">
      {{ job.salary || `${Math.round(job.salary_min!)}k-${Math.round(job.salary_max!)}k` }}
    </div>

    <!-- 收藏按钮 - 改到右侧悬浮 -->
    <button 
      class="card-like-btn" 
      :class="{ active: isSaved }"
      @click.stop="toggleSavedJob"
      :disabled="savingStatus"
      :title="isSaved ? '取消收藏' : '添加到心动岗位'"
    >
      <svg 
        class="like-icon" 
        viewBox="0 0 24 24" 
        :fill="isSaved ? 'currentColor' : 'none'"
        :stroke="isSaved ? 'none' : 'currentColor'"
      >
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
      </svg>
    </button>
    
    <div class="card-body">
      <!-- 职位名称 -->
      <h3 class="job-title">{{ job.name || job.title || '未知职位' }}</h3>
      
      <!-- 公司 -->
      <div class="company-row">
        <svg class="row-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M3 0a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V2a2 2 0 00-2-2H3zm1 3h2v2H4V3zm0 4h2v2H4V7zm0 4h2v2H4v-2zm4-8h2v2H8V3zm0 4h2v2H8V7zm0 4h2v2H8v-2z"/></svg>
        <span>{{ job.company || '未知公司' }}</span>
      </div>
      
      <!-- 标签 -->
      <div class="tag-row">
        <span class="tag tag-city" v-if="job.city">
          <svg class="tag-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0a5 5 0 00-5 5c0 4.5 5 11 5 11s5-6.5 5-11a5 5 0 00-5-5zm0 7a2 2 0 110-4 2 2 0 010 4z"/></svg>
          {{ job.city }}
        </span>
        <span class="tag tag-category" v-if="job.category && job.category !== '全职'">{{ job.category }}</span>
        <span class="tag tag-match" v-if="job.match_score">
          <svg class="tag-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1a4 4 0 100 8 4 4 0 000-8zM0 8a8 8 0 1116 0A8 8 0 010 8z"/></svg>
          {{ Math.round(job.match_score) }}%
        </span>
      </div>
      
      <!-- 描述 -->
      <p class="job-desc" v-if="job.description">{{ truncateText(job.description, 60) }}</p>
    </div>
    
    <!-- 底部操作 -->
    <div class="card-action">
      <button class="assess-btn" @click.stop="$emit('assess', job.id)">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M10 3a7 7 0 100 14 7 7 0 000-14zm0 11.2A4.2 4.2 0 1110 5.8a4.2 4.2 0 010 8.4zm0-6.4a2.2 2.2 0 100 4.4 2.2 2.2 0 000-4.4z"/></svg>
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
  // 检查是否已收藏
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
  background: #fff;
  border-radius: 14px;
  padding: 32px 24px 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
  cursor: pointer;
  border: 2px solid #eef0f4;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.job-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.25s;
}

.job-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(102, 126, 234, 0.2);
  border-color: #d4d9f5;
}

.job-card:hover::before {
  opacity: 1;
}

/* 薪资角标 */
.salary-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 14px;
  font-weight: 700;
  color: #e74c3c;
  letter-spacing: -0.3px;
  background: #fff5f5;
  padding: 4px 10px;
  border-radius: 6px;
}

/* 收藏按钮 - 右侧悬浮 */
.card-like-btn {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #ddd;
  z-index: 3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-like-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 1);
  color: #fe4c4c;
  transform: translateY(-50%) scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-like-btn.active {
  background: #fe4c4c;
  color: white;
  box-shadow: 0 6px 16px rgba(254, 76, 76, 0.35);
}

.card-like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-icon {
  width: 19px;
  height: 19px;
  stroke-width: 2;
}

/* 卡片内容 */
.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 50px;
}

.job-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.company-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  margin-top: 2px;
}

.row-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  opacity: 0.6;
}

/* 标签 */
.tag-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.tag-icon {
  width: 11px;
  height: 11px;
}

.tag-city {
  background: #eef3ff;
  color: #4a6cf7;
}

.tag-category {
  background: #f0faf4;
  color: #2d9d61;
}

.tag-match {
  background: #fff5e6;
  color: #ff8c42;
}

.job-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
  flex: 1;
  margin-top: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 底部按钮 */
.card-action {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid #f2f3f5;
}

.assess-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 0;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
}

.assess-btn:hover {
  opacity: 0.9;
  transform: scale(1.02);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

@media (max-width: 768px) {
  .job-card {
    padding: 24px 18px 18px;
  }
  
  .salary-badge {
    font-size: 12px;
    padding: 3px 8px;
  }
  
  .card-like-btn {
    width: 32px;
    height: 32px;
  }
  
  .like-icon {
    width: 16px;
    height: 16px;
  }
  
  .card-body {
    gap: 10px;
  }
  
  .job-title {
    font-size: 15px;
  }
}
</style>

