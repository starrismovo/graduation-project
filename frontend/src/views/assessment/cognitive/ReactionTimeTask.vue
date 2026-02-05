<template>
  <div class="reaction-time-task">
    <!-- 任务说明 -->
    <div class="task-intro" v-if="!started">
      <h4>反应时任务</h4>
      <div class="instruction">
        <p>当屏幕中央出现 <strong style="color: #f56c6c;">●</strong> 时，请尽快点击或按空格键。</p>
        <ul>
          <li>尽量快速反应，但避免误触</li>
          <li>共有 {{ totalTrials }} 个刺激</li>
          <li>刺激间隔随机，保持注意力集中</li>
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

      <div class="stimulus-area" v-if="showStimulus" @click="respondToStimulus">
        <div class="stimulus-dot"></div>
        <div class="instruction-click">点击 或 按空格</div>
      </div>

      <div class="waiting-screen" v-else>
        <p>准备...</p>
      </div>
    </div>

    <!-- 任务完成 -->
    <div class="task-results" v-else>
      <h4>任务完成</h4>
      <div class="results-summary">
        <div class="result-item">
          <div class="label">完成轮数</div>
          <div class="value">{{ trialIndex }}</div>
        </div>
        <div class="result-item">
          <div class="label">平均反应时</div>
          <div class="value accent">{{ avgReactionTime.toFixed(0) }}ms</div>
        </div>
        <div class="result-item">
          <div class="label">最快反应</div>
          <div class="value">{{ minReactionTime }}ms</div>
        </div>
        <div class="result-item">
          <div class="label">最慢反应</div>
          <div class="value">{{ maxReactionTime }}ms</div>
        </div>
        <div class="result-item">
          <div class="label">反应稳定性</div>
          <div class="value">{{ consistency.toFixed(1) }}%</div>
        </div>
      </div>

      <el-button type="primary" @click="completeTask">完成</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  difficulty: number
}>()

const emit = defineEmits<{
  (e: 'complete', results: any): void
}>()

// 任务参数
const totalTrials = computed(() => props.difficulty === 1 ? 15 : props.difficulty === 2 ? 20 : 25)

// 任务状态
const started = ref(false)
const finished = ref(false)
const showStimulus = ref(false)
const trialIndex = ref(0)
const reactionTimes = ref<number[]>([])
const stimulusStartTime = ref(0)
const expectedResponseTime = ref(0)

// 统计数据
const avgReactionTime = computed(() =>
  reactionTimes.value.length > 0
    ? reactionTimes.value.reduce((a, b) => a + b, 0) / reactionTimes.value.length
    : 0
)

const minReactionTime = computed(() =>
  reactionTimes.value.length > 0
    ? Math.min(...reactionTimes.value)
    : 0
)

const maxReactionTime = computed(() =>
  reactionTimes.value.length > 0
    ? Math.max(...reactionTimes.value)
    : 0
)

const consistency = computed(() => {
  if (reactionTimes.value.length < 2) return 100
  const avg = avgReactionTime.value
  const variance = reactionTimes.value.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / reactionTimes.value.length
  const stdDev = Math.sqrt(variance)
  return Math.max(0, 100 - (stdDev / avg) * 100)
})

function startTask() {
  started.value = true
  nextTrial()
}

function nextTrial() {
  if (trialIndex.value >= totalTrials.value) {
    finished.value = true
    return
  }

  showStimulus.value = false
  const delay = Math.random() * 2000 + 1000 // 1-3 秒随机延迟
  
  setTimeout(() => {
    if (!finished.value) {
      showStimulus.value = true
      stimulusStartTime.value = Date.now()
    }
  }, delay)
}

function respondToStimulus() {
  if (!showStimulus.value) return

  const reactionTime = Date.now() - stimulusStartTime.value
  reactionTimes.value.push(reactionTime)

  showStimulus.value = false
  trialIndex.value++

  setTimeout(() => {
    nextTrial()
  }, 300)
}

function handleKeyPress(event: KeyboardEvent) {
  if (!started.value || finished.value) return
  if (event.code !== 'Space') return
  
  event.preventDefault()
  respondToStimulus()
}

function completeTask() {
  emit('complete', {
    taskId: 'reaction-time',
    metrics: {
      avgReactionTime: avgReactionTime.value,
      consistency: consistency.value / 100,
      minReactionTime: minReactionTime.value,
      maxReactionTime: maxReactionTime.value
    },
    analysis: generateAnalysis()
  })
}

function generateAnalysis(): string {
  const rt = avgReactionTime.value
  const cons = consistency.value
  
  let analysis = ''
  
  if (rt < 600) {
    analysis += '⚡ 反应速度极快，信息处理效率高，认知反应敏锐。'
  } else if (rt < 800) {
    analysis += '✓ 反应速度快，处理速度良好。'
  } else if (rt < 1000) {
    analysis += '◐ 反应速度中等，处理速度正常。'
  } else {
    analysis += '⏱ 反应速度偏慢，可以通过训练提升。'
  }
  
  analysis += ' '
  
  if (cons > 85) {
    analysis += '✓ 反应非常稳定，注意力集中度高。'
  } else if (cons > 70) {
    analysis += '◐ 反应较为稳定，但偶有波动。'
  } else {
    analysis += '⚠ 反应波动较大，需要改进稳定性。'
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
.reaction-time-task {
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

.stimulus-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.1s ease;
}

.stimulus-area:active {
  background: #f0f9ff;
  border-color: #409eff;
}

.stimulus-dot {
  width: 80px;
  height: 80px;
  background: #f56c6c;
  border-radius: 50%;
  margin-bottom: 20px;
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  70% {
    box-shadow: 0 0 0 20px rgba(245, 108, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

.instruction-click {
  font-size: 14px;
  color: #666;
  text-align: center;
}

.waiting-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
}

.waiting-screen p {
  margin: 0;
  font-size: 18px;
  color: #999;
  font-weight: 600;
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

.value.accent {
  color: #e6a23c;
}
</style>
