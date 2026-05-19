<template>
  <div class="history-section">
    <div class="history-head">
      <div>
        <h3>历史评估记录</h3>
        <p>展示已完成的评估记录与报告结果，便于回溯人岗匹配变化。</p>
      </div>
    </div>

    <div class="history-panel">
      <el-table :data="data" class="history-table">
        <el-table-column prop="created_at" label="评估时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="job_title" label="对应岗位" min-width="180" />

        <el-table-column prop="match_score" label="匹配度" width="160">
          <template #default="{ row }">
            <div class="match-cell">
              <el-progress
                :percentage="row.match_score"
                :color="getScoreColor(row.match_score)"
                :stroke-width="8"
                :show-text="false"
              />
              <span class="match-value">{{ row.match_score }}%</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <button class="view-btn" type="button" @click="$emit('view', row)">查看详情</button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
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
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#5b67ff'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}
</script>

<style scoped>
.history-section {
  border-radius: 28px;
  border: 1px solid rgba(226, 232, 255, 0.95);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.history-head {
  padding: 24px 26px 18px;
}

.history-head h3 {
  margin: 0 0 6px;
  font-size: 26px;
  color: #172133;
  letter-spacing: -0.04em;
}

.history-head p {
  margin: 0;
  color: #73809a;
  font-size: 13px;
  line-height: 1.8;
}

.history-panel {
  padding: 0 16px 16px;
}

.history-table {
  --el-table-border-color: #eef2ff;
  --el-table-header-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  border-radius: 20px;
  overflow: hidden;
}

.match-cell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
}

.match-value {
  font-size: 12px;
  font-weight: 700;
  color: #334155;
}

.view-btn {
  border: none;
  background: transparent;
  color: #5b67ff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.history-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.history-table :deep(th.el-table__cell) {
  padding: 18px 0 12px;
  background: transparent;
  color: #7b879c;
  font-size: 12px;
  font-weight: 700;
}

.history-table :deep(td.el-table__cell) {
  padding: 16px 0;
  color: #1f2937;
  font-size: 13px;
}

.history-table :deep(.el-table__row) {
  transition: background 0.2s ease;
}

.history-table :deep(.el-table__row:hover > td.el-table__cell) {
  background: rgba(247, 249, 255, 0.9);
}
</style>
