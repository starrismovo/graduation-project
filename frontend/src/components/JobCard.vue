<template>
  <el-card class="job-card" shadow="hover" @click="handleClick">
    <template #header>
      <div class="job-header">
        <h3 class="job-title">{{ job.title }}</h3>
        <el-tag 
          v-if="job.match_score" 
          :type="getTagType(job.match_score)"
          size="small"
          class="match-tag"
        >
          {{ job.match_score }}%匹配
        </el-tag>
      </div>
    </template>

    <div class="job-content">
      <p v-if="job.description" class="job-description">
        {{ truncateText(job.description, 80) }}
      </p>

      <div class="job-meta">
        <span v-if="job.department" class="meta-item">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="none" stroke="currentColor" stroke-width="2"/></svg></el-icon>
          {{ job.department }}
        </span>
        <span v-if="job.level" class="meta-item">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" fill="currentColor"/></svg></el-icon>
          {{ job.level }}
        </span>
      </div>

      <!-- 匹配度条 -->
      <div v-if="job.match_score" class="match-bar">
        <el-progress 
          :percentage="job.match_score" 
          :color="getBarColor(job.match_score)"
          :stroke-width="4"
          :show-text="false"
        />
      </div>

      <!-- CTA 按钮 -->
      <div class="card-footer">
        <el-button 
          type="primary" 
          size="small" 
          @click.stop="$emit('assess', job.id)"
        >
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9 11H7v2h2v-2zm8 0h-2v2h2v-2zm4-7H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H3V6h18v14z" fill="currentColor"/></svg></el-icon>
          立即评估
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Job {
  id: number | string
  title: string
  description?: string
  department?: string
  level?: string
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

function getTagType(score: number): 'success' | 'warning' | 'info' | 'danger' {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'info'
}

function getBarColor(score: number): string {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}
</script>


<style scoped>
.job-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
}

.job-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
  border-color: #409eff;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 0;
  border-bottom: 0;
}

.job-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
  word-break: break-word;
}

.match-tag {
  flex-shrink: 0;
  white-space: nowrap;
}

.job-content {
  padding: 12px 0;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.job-description {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  word-break: break-word;
}

.job-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.meta-item :deep(.el-icon) {
  font-size: 14px;
}

.match-bar {
  margin: 12px 0;
  flex-shrink: 0;
}

.match-bar :deep(.el-progress__bar) {
  background-color: currentColor;
}

.card-footer {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.card-footer :deep(.el-button) {
  flex: 1;
  font-size: 13px;
}

@media (max-width: 768px) {
  .job-card {
    min-height: auto;
  }

  .job-header {
    flex-direction: column;
    gap: 8px;
  }

  .match-tag {
    align-self: flex-start;
  }
}
</style>
