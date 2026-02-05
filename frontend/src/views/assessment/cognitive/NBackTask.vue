<template>
  <div class="nback-task">
    <!-- 任务说明 -->
    <div class="task-intro" v-if="!started">
      <h4>N-Back 记忆任务</h4>
      <div class="instruction">
        <p>这个任务会依次显示数字。你需要判断当前数字是否与 {{ nBackValue }} 步前出现过的数字相同。</p>
        <ul>
          <li>按 <strong style="color: #67c23a;">Y</strong> 键表示"相同"</li>
          <li>按 <strong style="color: #f56c6c;">N</strong> 键表示"不同"</li>
          <li>尽量准确和快速响应</li>
        </ul>
      </div>
      <el-button type="primary" @click="startTask">开始任务</el-button>
    </div>

    <!-- 任务进行中 -->
    <div class="task-running" v-else-if="!finished">
      <div class="progress-section">
        <el-progress 
          :percentage="(trialIndex / totalTrials) * 100" 
          :show-text="true"
          text-inside
        />
        <span class="progress-text">{{ trialIndex }}/{{ totalTrials }}</span>
      </div>

      <div class="stimulus-display" :class="{ correct: feedback === 'correct', incorrect: feedback === 'incorrect' }">
        <div class="large-number">{{ currentNumber }}</div>
        <div class="feedback-text" v-if="feedback">{{ feedbackText }}</div>
      </div>

      <div class="instructions-hint">
        <span class="hint-y">Y - 相同</span>
        <span class="hint-separator">|</span>
        <span class="hint-n">N - 不同</span>
      </div>
    </div>

    <!-- 任务完成 -->
    <div class="task-results" v-else>
      <h4>任务完成</h4>
      <div class="results-summary">
        <div class="result-item">
          <div class="label">总轮数</div>
          <div class="value">{{ totalTrials }}</div>
        </div>
        <div class="result-item">
          <div class="label">正确答案</div>
          <div class="value correct">{{ correctCount }}</div>
        </div>
        <div class="result-item">
          <div class="label">错误答案</div>
          <div class="value error">{{ totalTrials - correctCount }}</div>
        </div>
        <div class="result-item">
          <div class="label">准确率</div>
          <div class="value accent">{{ (accuracy * 100).toFixed(1) }}%</div>
        </div>
        <div class="result-item">
          <div class="label">平均反应时</div>
          <div class="value">{{ avgReactionTime.toFixed(0) }}ms</div>
        </div>
      </div>

      <el-button type="primary" @click="completeTask">完成</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  difficulty: number
}>()

const emit = defineEmits<{
  (e: 'complete', results: any): void
}>()

// 任务参数
const nBackValue = computed(() => props.difficulty === 1 ? 1 : props.difficulty === 2 ? 2 : 3)
const totalTrials = computed(() => props.difficulty === 1 ? 20 : props.difficulty === 2 ? 30 : 40)

// 任务状态
const started = ref(false)
const finished = ref(false)
const trialIndex = ref(0)
const currentNumber = ref(0)
const numbers = ref<number[]>([])
const responses = ref<Array<{ trial: number; correct: boolean; reactionTime: number }>>([])
const feedback = ref<'correct' | 'incorrect' | null>(null)
const feedbackText = ref('')
const currentTrialStartTime = ref(0)

// 统计数据
const correctCount = computed(() => responses.value.filter(r => r.correct).length)
const accuracy = computed(() => correctCount.value / totalTrials.value)
const avgReactionTime = computed(() => 
  responses.value.length > 0 
    ? responses.value.reduce((a, b) => a + b.reactionTime, 0) / responses.value.length
    : 0
)

// 生成 N-Back 序列
function generateNBackSequence() {
  const sequence: number[] = []
  const nValue = nBackValue.value
  
  for (let i = 0; i < totalTrials.value; i++) {
    if (i < nValue) {
      // 前 n 个随机数字
      sequence.push(Math.floor(Math.random() * 9) + 1)
    } else {
      // 50% 概率重复 n 步前的数字，50% 新数字
      if (Math.random() < 0.5) {
        sequence.push(sequence[i - nValue])
      } else {
        sequence.push(Math.floor(Math.random() * 9) + 1)
      }
    }
  }
  
  return sequence
}

function startTask() {
  started.value = true
  numbers.value = generateNBackSequence()
  nextTrial()
}

function nextTrial() {
  if (trialIndex.value >= totalTrials.value) {
    finished.value = true
    return
  }

  currentNumber.value = numbers.value[trialIndex.value]
  feedback.value = null
  feedbackText.value = ''
  currentTrialStartTime.value = Date.now()
}

function handleKeyPress(event: KeyboardEvent) {
  if (!started.value || finished.value) return

  const key = event.key.toUpperCase()
  if (key !== 'Y' && key !== 'N') return

  event.preventDefault()

  const reactionTime = Date.now() - currentTrialStartTime.value
  const isMatch = trialIndex.value >= nBackValue.value && 
    currentNumber.value === numbers.value[trialIndex.value - nBackValue.value]
  const isCorrect = (key === 'Y' && isMatch) || (key === 'N' && !isMatch)

  // 记录响应
  responses.value.push({
    trial: trialIndex.value,
    correct: isCorrect,
    reactionTime
  })

  // 显示反馈
  feedback.value = isCorrect ? 'correct' : 'incorrect'
  feedbackText.value = isCorrect ? '✓ 正确' : '✗ 错误'

  // 继续下一个
  trialIndex.value++
  setTimeout(() => {
    nextTrial()
  }, 500)
}

function completeTask() {
  emit('complete', {
    taskId: 'n-back',
    metrics: {
      accuracy: accuracy.value,
      avgReactionTime: avgReactionTime.value,
      correctCount: correctCount.value,
      totalTrials: totalTrials.value
    },
    analysis: generateAnalysis()
  })
}

function generateAnalysis(): string {
  const acc = accuracy.value
  const rt = avgReactionTime.value
  
  let analysis = ''
  
  if (acc > 0.8) {
    analysis += '✓ 工作记忆能力强，能够准确跟踪信息。'
  } else if (acc > 0.6) {
    analysis += '◐ 工作记忆能力中等，但在高负荷下可能出现遗漏。'
  } else {
    analysis += '✗ 工作记忆能力需要提升，建议加强注意力训练。'
  }
  
  analysis += ' '
  
  if (rt < 800) {
    analysis += '⚡ 反应速度快，信息处理效率高。'
  } else if (rt < 1200) {
    analysis += '◐ 反应速度中等，处理速度正常。'
  } else {
    analysis += '⏱ 反应速度偏慢，需要提升信息处理速度。'
  }
  
  return analysis
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
.nback-task {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-intro {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-intro h4 {
  margin: 0;
  color: #333;
}

.instruction {
  background: #f0f9ff;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.instruction p {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

.instruction ul {
  margin: 0;
  padding-left: 20px;
  color: #333;
  font-size: 14px;
}

.instruction li {
  margin: 4px 0;
}

.task-running {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.progress-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

.progress-section :deep(.el-progress) {
  flex: 1;
}

.progress-text {
  min-width: 60px;
  text-align: right;
  font-weight: 600;
  color: #409eff;
}

.stimulus-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.stimulus-display.correct {
  border-color: #67c23a;
  background: #f0f9f0;
}

.stimulus-display.incorrect {
  border-color: #f56c6c;
  background: #fef0f0;
}

.large-number {
  font-size: 72px;
  font-weight: 700;
  color: #409eff;
  line-height: 1;
  margin-bottom: 16px;
}

.feedback-text {
  font-size: 18px;
  font-weight: 600;
}

.stimulus-display.correct .feedback-text {
  color: #67c23a;
}

.stimulus-display.incorrect .feedback-text {
  color: #f56c6c;
}

.instructions-hint {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
}

.hint-y {
  color: #67c23a;
  font-weight: 600;
}

.hint-n {
  color: #f56c6c;
  font-weight: 600;
}

.hint-separator {
  color: #ccc;
}

.task-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-results h4 {
  margin: 0;
  color: #333;
}

.results-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.result-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  text-align: center;
}

.label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.value {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

.value.correct {
  color: #67c23a;
}

.value.error {
  color: #f56c6c;
}

.value.accent {
  color: #e6a23c;
}
</style>
