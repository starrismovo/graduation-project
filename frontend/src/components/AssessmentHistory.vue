<template>
  <div class="history-section">
    <h3 class="section-title">
      <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" fill="currentColor"/></svg></el-icon>
      历史评估记录
    </h3>

    <el-table :data="data" stripe class="history-table">
      <el-table-column prop="created_at" label="评估时间" width="160">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column prop="job_title" label="对应岗位" min-width="180" />

      <el-table-column prop="match_score" label="匹配度" width="100" align="center">
        <template #default="{ row }">
          <el-progress
            :percentage="row.match_score"
            :color="getScoreColor(row.match_score)"
            :stroke-width="6"
            :text-inside="true"
          />
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-button type="text" @click="$emit('view', row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface HistoryRecord {
  id: string | number
  job_title: string
  match_score: number
  created_at: string
  [key: string]: any
}

defineProps<{
  data: HistoryRecord[]
}>()

defineEmits<{
  (e: 'view', record: HistoryRecord): void
}>()

function formatTime(dateString: string): string {
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
</script>

<style scoped>
.history-section {
  margin: 32px 0;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title :deep(.el-icon) {
  font-size: 20px;
  color: #409eff;
}

.history-table {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.history-table :deep(.el-table__header th) {
  background: #f5f7fa;
  color: #2c3e50;
  font-weight: 600;
}

.history-table :deep(.el-table__body) {
  background: #fff;
}
</style>
