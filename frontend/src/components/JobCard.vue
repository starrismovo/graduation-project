<template>
  <div class="job-card" @click="handleClick">
    <!-- 薪资角标 -->
    <div class="salary-badge" v-if="job.salary || (job.salary_min && job.salary_max)">
      {{ job.salary || `${Math.round(job.salary_min!)}k-${Math.round(job.salary_max!)}k` }}
    </div>
    
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
      </div>
      
      <!-- 描述 -->
      <p class="job-desc" v-if="job.description">{{ truncateText(job.description, 60) }}</p>
    </div>
    
    <!-- 底部操作 -->
    <div class="card-action">
      <button class="assess-btn" @click.stop="$emit('assess', job.id)">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/><path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767A2 2 0 0010 16h2l3 3v-3h1a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/></svg>
        开始AI面试
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
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
}>()

function handleClick() {
  emit('click')
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
  padding: 22px 20px 16px;
  display: flex;
  flex-direction: column;
  height: 100%;
  cursor: pointer;
  border: 1px solid #eef0f4;
  transition: all 0.25s ease;
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
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.15);
  border-color: #d4d9f5;
}

.job-card:hover::before {
  opacity: 1;
}

/* 薪资角标 */
.salary-badge {
  position: absolute;
  top: 14px;
  right: 16px;
  font-size: 15px;
  font-weight: 700;
  color: #e74c3c;
  letter-spacing: -0.3px;
}

/* 卡片内容 */
.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.job-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.4;
  padding-right: 80px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.company-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.row-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  opacity: 0.5;
}

/* 标签 */
.tag-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
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

.job-desc {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  flex: 1;
}

/* 底部按钮 */
.card-action {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #f2f3f5;
}

.assess-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 0;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.assess-btn:hover {
  opacity: 0.9;
  transform: scale(1.01);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

@media (max-width: 768px) {
  .job-card {
    padding: 16px;
  }
  .salary-badge {
    font-size: 13px;
  }
}
</style>
