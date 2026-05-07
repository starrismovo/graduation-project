<template>
  <div class="cognitive-placeholder">
    <h3>N-Back 记忆任务</h3>
    <p>当前为前端占位实现，用于保持认知评估流程可编译、可联调。</p>
    <div class="meta">难度等级：{{ difficulty }}</div>
    <el-button type="primary" @click="completeTask">完成任务</el-button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  difficulty?: number
}>()

const emit = defineEmits<{
  (e: 'complete', payload: {
    metrics: {
      accuracy: number
      avgReactionTime: number
      consistency: number
      score: number
    }
    analysis: string
  }): void
}>()

function completeTask() {
  emit('complete', {
    metrics: {
      accuracy: 0.82,
      avgReactionTime: 920,
      consistency: 0.78,
      score: (props.difficulty || 1) * 3
    },
    analysis: 'N-Back 记忆任务已完成，后续可替换为正式的交互式认知评估组件。'
  })
}
</script>

<style scoped>
.cognitive-placeholder {
  padding: 24px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cognitive-placeholder h3,
.cognitive-placeholder p,
.meta {
  margin: 0;
}

.meta {
  color: #64748b;
  font-size: 13px;
}
</style>
