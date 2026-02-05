<template>
  <div class="personality-scale">
    <div class="scale-header">
      <h4>大五人格量表（简化版）</h4>
      <div class="instruction">请根据自身情况对以下条目进行评分（1 = 完全不同意，5 = 完全同意）</div>
    </div>

    <el-form :model="scores" class="scale-form">
      <el-form-item v-for="(item, idx) in scaleItems" :key="idx" :label="`第 ${idx + 1} 题`">
        <div class="question">{{ item.question }}</div>
        <el-radio-group v-model="scores[item.key]" size="large">
          <el-radio :label="1">1（不同意）</el-radio>
          <el-radio :label="2">2</el-radio>
          <el-radio :label="3">3（中性）</el-radio>
          <el-radio :label="4">4</el-radio>
          <el-radio :label="5">5（同意）</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item>
        <div class="actions">
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" @click="submit">提交量表</el-button>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits<{
  (e: 'save', payload: Record<string, number>): void
  (e: 'next'): void
}>()

const scaleItems = [
  { key: 'extraversion', question: '我是一个健谈、外向的人' },
  { key: 'agreeableness', question: '我容易与他人合作' },
  { key: 'conscientiousness', question: '我做事有条理、守纪律' },
  { key: 'neuroticism', question: '我经常感到紧张或焦虑' },
  { key: 'openness', question: '我对新思想和经验持开放态度' },
  { key: 'extraversion_2', question: '我喜欢在聚会中成为中心人物' },
  { key: 'agreeableness_2', question: '我关心他人的感受' },
  { key: 'conscientiousness_2', question: '我能完成承诺的任务' }
]

const scores = reactive<Record<string, number>>({
  extraversion: 0,
  agreeableness: 0,
  conscientiousness: 0,
  neuroticism: 0,
  openness: 0,
  extraversion_2: 0,
  agreeableness_2: 0,
  conscientiousness_2: 0
})

function reset() {
  Object.keys(scores).forEach(key => {
    scores[key] = 0
  })
}

function submit() {
  const allFilled = Object.values(scores).every(v => v !== 0)
  if (!allFilled) {
    ElMessage.warning('请完成所有题目')
    return
  }
  ElMessage.success('量表已提交')
  emit('save', { ...scores })
  emit('next')
}
</script>

<style scoped>
.personality-scale { background: #fff; padding: 20px; }
.scale-header { margin-bottom: 20px; }
.scale-header h4 { margin: 0 0 8px 0; }
.instruction { color: #666; font-size: 13px; }
.scale-form { max-width: 800px; }
.question { font-size: 14px; margin-bottom: 10px; color: #333; }
.actions { display: flex; gap: 10px; justify-content: flex-end; }
</style>
