<template>
  <div class="logic-task">
    <!-- 任务说明 -->
    <div class="task-intro" v-if="!started">
      <h4>逻辑推理任务</h4>
      <div class="instruction">
        <p>这个任务会提供一组图形模式，你需要找出规律并选择正确的下一个图形。</p>
        <ul>
          <li>仔细观察模式的变化规律</li>
          <li>从给出的选项中选择最符合规律的答案</li>
          <li>共有 {{ totalProblems }} 个推理问题</li>
          <li>时间充足，准确率优先</li>
        </ul>
      </div>
      <el-button type="primary" @click="startTask">开始任务</el-button>
    </div>

    <!-- 任务进行中 -->
    <div class="task-running" v-else-if="!finished">
      <div class="progress-section">
        <el-progress 
          :percentage="(currentProblem / totalProblems) * 100" 
          :show-text="true"
          text-inside
        />
        <span class="progress-text">{{ currentProblem }}/{{ totalProblems }}</span>
      </div>

      <div class="problem-display" v-if="problems[currentProblem - 1]">
        <h5>{{ problems[currentProblem - 1].description }}</h5>
        
        <div class="pattern-area">
          <div class="pattern-row">
            <div v-for="(item, idx) in problems[currentProblem - 1].pattern" :key="idx" class="pattern-item">
              <div class="shape" :class="item.type" :style="{ background: item.color }"></div>
            </div>
            <div class="pattern-question">?</div>
          </div>
        </div>

        <div class="options-area">
          <div 
            v-for="(option, idx) in problems[currentProblem - 1].options"
            :key="idx"
            class="option-card"
            :class="{ selected: selectedOption === idx, correct: feedback === 'correct' && selectedOption === idx, incorrect: feedback === 'incorrect' && selectedOption === idx }"
            @click="selectOption(idx)"
          >
            <div class="shape" :class="option.type" :style="{ background: option.color }"></div>
            <div class="option-label">{{ String.fromCharCode(65 + idx) }}</div>
          </div>
        </div>

        <div v-if="selectedOption !== null" class="feedback-area">
          <div v-if="feedback === 'correct'" class="feedback success">✓ 正确！规律识别准确。</div>
          <div v-else-if="feedback === 'incorrect'" class="feedback error">✗ 错误。正确答案是选项 {{ String.fromCharCode(65 + problems[currentProblem - 1].correctOption) }}</div>
        </div>

        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="nextProblem"
            :disabled="selectedOption === null"
          >
            {{ currentProblem === totalProblems ? '完成' : '下一题' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 任务完成 -->
    <div class="task-results" v-else>
      <h4>任务完成</h4>
      <div class="results-summary">
        <div class="result-item">
          <div class="label">总题数</div>
          <div class="value">{{ totalProblems }}</div>
        </div>
        <div class="result-item">
          <div class="label">正确答案</div>
          <div class="value correct">{{ correctCount }}</div>
        </div>
        <div class="result-item">
          <div class="label">错误答案</div>
          <div class="value error">{{ totalProblems - correctCount }}</div>
        </div>
        <div class="result-item">
          <div class="label">准确率</div>
          <div class="value accent">{{ (accuracy * 100).toFixed(1) }}%</div>
        </div>
        <div class="result-item">
          <div class="label">平均耗时</div>
          <div class="value">{{ avgTime.toFixed(0) }}s</div>
        </div>
      </div>

      <el-button type="primary" @click="completeTask">完成</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  difficulty: number
}>()

const emit = defineEmits<{
  (e: 'complete', results: any): void
}>()

// 任务参数
const totalProblems = computed(() => props.difficulty === 1 ? 5 : props.difficulty === 2 ? 8 : 10)

// 问题数据
interface Problem {
  description: string
  pattern: Array<{ type: string; color: string }>
  options: Array<{ type: string; color: string }>
  correctOption: number
}

const problems: Problem[] = [
  {
    description: '找出下一个图形',
    pattern: [
      { type: 'circle', color: '#409eff' },
      { type: 'square', color: '#e6a23c' },
      { type: 'circle', color: '#67c23a' }
    ],
    options: [
      { type: 'square', color: '#f56c6c' },
      { type: 'triangle', color: '#409eff' },
      { type: 'circle', color: '#f56c6c' },
      { type: 'square', color: '#409eff' }
    ],
    correctOption: 0
  },
  {
    description: '根据颜色和形状的规律完成序列',
    pattern: [
      { type: 'circle', color: '#409eff' },
      { type: 'circle', color: '#67c23a' },
      { type: 'circle', color: '#e6a23c' }
    ],
    options: [
      { type: 'circle', color: '#f56c6c' },
      { type: 'square', color: '#f56c6c' },
      { type: 'triangle', color: '#f56c6c' },
      { type: 'circle', color: '#409eff' }
    ],
    correctOption: 0
  },
  {
    description: '识别几何图形的递进规律',
    pattern: [
      { type: 'square', color: '#409eff' },
      { type: 'circle', color: '#409eff' },
      { type: 'triangle', color: '#409eff' }
    ],
    options: [
      { type: 'square', color: '#409eff' },
      { type: 'circle', color: '#409eff' },
      { type: 'pentagon', color: '#409eff' },
      { type: 'hexagon', color: '#409eff' }
    ],
    correctOption: 2
  },
  {
    description: '复杂规律推理',
    pattern: [
      { type: 'circle', color: '#409eff' },
      { type: 'square', color: '#67c23a' },
      { type: 'circle', color: '#e6a23c' }
    ],
    options: [
      { type: 'square', color: '#f56c6c' },
      { type: 'circle', color: '#f56c6c' },
      { type: 'triangle', color: '#409eff' },
      { type: 'square', color: '#e6a23c' }
    ],
    correctOption: 1
  },
  {
    description: '识别形状变化规律',
    pattern: [
      { type: 'circle', color: '#409eff' },
      { type: 'circle', color: '#409eff' },
      { type: 'square', color: '#409eff' }
    ],
    options: [
      { type: 'square', color: '#409eff' },
      { type: 'triangle', color: '#409eff' },
      { type: 'circle', color: '#67c23a' },
      { type: 'square', color: '#67c23a' }
    ],
    correctOption: 1
  }
]

// 任务状态
const started = ref(false)
const finished = ref(false)
const currentProblem = ref(0)
const selectedOption = ref<number | null>(null)
const feedback = ref<'correct' | 'incorrect' | null>(null)
const responses = ref<Array<{ correct: boolean; time: number }>>([])
const problemStartTime = ref(0)

// 统计数据
const correctCount = computed(() => responses.value.filter(r => r.correct).length)
const accuracy = computed(() => correctCount.value / totalProblems.value)
const avgTime = computed(() =>
  responses.value.length > 0
    ? responses.value.reduce((a, b) => a + b.time, 0) / responses.value.length
    : 0
)

function startTask() {
  started.value = true
  currentProblem.value = 1
  problemStartTime.value = Date.now()
}

function selectOption(optionIndex: number) {
  selectedOption.value = optionIndex
  const isCorrect = optionIndex === problems[currentProblem.value - 1].correctOption
  feedback.value = isCorrect ? 'correct' : 'incorrect'
  
  const time = (Date.now() - problemStartTime.value) / 1000
  responses.value.push({
    correct: isCorrect,
    time
  })
}

function nextProblem() {
  if (currentProblem.value >= totalProblems.value) {
    finished.value = true
    return
  }

  currentProblem.value++
  selectedOption.value = null
  feedback.value = null
  problemStartTime.value = Date.now()
}

function completeTask() {
  emit('complete', {
    taskId: 'logic',
    metrics: {
      accuracy: accuracy.value,
      avgTime: avgTime.value,
      correctCount: correctCount.value,
      totalProblems: totalProblems.value
    },
    analysis: generateAnalysis()
  })
}

function generateAnalysis(): string {
  const acc = accuracy.value
  const time = avgTime.value
  
  let analysis = ''
  
  if (acc > 0.8) {
    analysis += '✓ 逻辑推理能力强，能够快速识别复杂模式。'
  } else if (acc > 0.6) {
    analysis += '◐ 逻辑推理能力中等，需要更多思考但能解决问题。'
  } else {
    analysis += '⚠ 逻辑推理能力需要提升，建议加强模式识别训练。'
  }
  
  analysis += ' '
  
  if (time < 20) {
    analysis += '⚡ 问题解决速度快，思维敏捷。'
  } else if (time < 40) {
    analysis += '✓ 问题解决速度正常。'
  } else {
    analysis += '⏱ 需要加快问题解决速度。'
  }
  
  return analysis
}
</script>

<style scoped>
.logic-task {
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

.problem-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.problem-display h5 {
  margin: 0;
  color: #333;
  font-size: 14px;
}

.pattern-area {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 6px;
}

.pattern-row {
  display: flex;
  justify-content: center;
  gap: 16px;
  align-items: center;
}

.pattern-item {
  width: 60px;
  height: 60px;
  border: 2px solid #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
}

.pattern-question {
  width: 60px;
  height: 60px;
  border: 2px dashed #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #ccc;
  font-weight: 700;
}

.shape {
  width: 40px;
  height: 40px;
}

.shape.circle {
  border-radius: 50%;
}

.shape.square {
  border-radius: 4px;
}

.shape.triangle {
  width: 0;
  height: 0;
  border-left: 20px solid transparent;
  border-right: 20px solid transparent;
  border-bottom: 40px solid;
}

.shape.pentagon {
  clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%);
}

.shape.hexagon {
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

.options-area {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
}

.option-card {
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.option-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.option-card.selected {
  border-color: #409eff;
  background: #f0f9ff;
}

.option-card.correct {
  border-color: #67c23a;
  background: #f0f9f0;
}

.option-card.incorrect {
  border-color: #f56c6c;
  background: #fef0f0;
}

.option-label {
  font-size: 12px;
  color: #666;
  font-weight: 600;
}

.feedback-area {
  margin-top: 12px;
}

.feedback {
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
}

.feedback.success {
  background: #f0f9f0;
  color: #67c23a;
  border-left: 3px solid #67c23a;
}

.feedback.error {
  background: #fef0f0;
  color: #f56c6c;
  border-left: 3px solid #f56c6c;
}

.action-buttons {
  display: flex;
  justify-content: center;
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
