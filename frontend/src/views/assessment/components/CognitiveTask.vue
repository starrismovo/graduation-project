<template>
  <div class="cognitive-task">
    <!-- 任务概览 -->
    <div class="task-overview" v-if="!taskStarted">
      <div class="overview-header">
        <h3>🧠 认知能力评估</h3>
        <p class="subtitle">从行为认知过渡到认知能力层面的深入评估</p>
      </div>

      <div class="task-selector">
        <el-alert 
          :title="`根据情境表现推荐任务：${recommendedTask.label}`" 
          :description="`${recommendedTask.description}`"
          type="info"
          closable
          show-icon
        />
        
        <div class="tasks-grid">
          <div 
            v-for="task in taskTypes" 
            :key="task.id"
            class="task-card"
            :class="{ recommended: task.id === recommendedTaskId }"
            @click="selectTask(task.id)"
          >
            <div class="task-icon">{{ task.icon }}</div>
            <div class="task-name">{{ task.label }}</div>
            <div class="task-info">
              <span class="duration">⏱ {{ task.duration }}s</span>
              <span class="difficulty">{{ task.difficulty }}</span>
            </div>
            <div class="task-traits">
              <el-tag v-for="t in task.traits" :key="t" size="small">{{ t }}</el-tag>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <el-button @click="$emit('next')">跳过此步</el-button>
          <el-button 
            type="primary" 
            @click="startTask"
            :disabled="!selectedTaskId"
          >
            开始选定任务
          </el-button>
        </div>
      </div>
    </div>

    <!-- 任务执行 -->
    <div class="task-execution" v-else>
      <!-- N-Back 记忆任务 -->
      <NBackTask 
        v-if="selectedTaskId === 'n-back'"
        :difficulty="taskDifficulty"
        @complete="handleTaskComplete"
      />

      <!-- 反应时任务 -->
      <ReactionTimeTask 
        v-else-if="selectedTaskId === 'reaction-time'"
        :difficulty="taskDifficulty"
        @complete="handleTaskComplete"
      />

      <!-- 逻辑推理任务 -->
      <LogicTask 
        v-else-if="selectedTaskId === 'logic'"
        :difficulty="taskDifficulty"
        @complete="handleTaskComplete"
      />
    </div>

    <!-- 任务结果总结 -->
    <div class="task-summary" v-if="taskCompleted && taskResults">
      <h3>📊 认知评估结果</h3>
      
      <div class="metrics-grid">
        <div v-for="(value, key) in taskResults.metrics" :key="key" class="metric-card">
          <div class="metric-label">{{ formatMetricLabel(String(key)) }}</div>
          <div class="metric-value">{{ formatMetricValue(String(key), value) }}</div>
          <div class="metric-bar">
            <el-progress 
              :percentage="getMetricPercentage(String(key), value)" 
              :color="getMetricColor(String(key), value)"
              :show-text="false"
            />
          </div>
        </div>
      </div>

      <div class="analysis-section">
        <h4>🎯 分析结果</h4>
        <div class="analysis-text">{{ taskResults.analysis }}</div>
      </div>

      <div class="action-buttons">
        <el-button @click="resetTask">重新选择任务</el-button>
        <el-button type="primary" @click="finishCognitive">完成认知评估</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import NBackTask from '../cognitive/NBackTask.vue'
import ReactionTimeTask from '../cognitive/ReactionTimeTask.vue'
import LogicTask from '../cognitive/LogicTask.vue'

interface TaskType {
  id: string
  label: string
  description: string
  icon: string
  duration: number
  difficulty: string
  traits: string[]
}

const emit = defineEmits<{
  (e: 'next'): void
}>()

const props = defineProps<{
  hrScores?: Record<string, number>
}>()

// 任务类型定义
const taskTypes: TaskType[] = [
  {
    id: 'n-back',
    label: 'N-Back 记忆任务',
    description: '考察工作记忆容量和注意力集中度',
    icon: '🔢',
    duration: 90,
    difficulty: '中等',
    traits: ['注意力', '工作记忆']
  },
  {
    id: 'reaction-time',
    label: '反应时任务',
    description: '考察信息处理速度和反应敏锐度',
    icon: '⚡',
    duration: 60,
    difficulty: '简单',
    traits: ['处理速度', '注意力']
  },
  {
    id: 'logic',
    label: '逻辑推理任务',
    description: '考察推理能力和问题解决能力',
    icon: '🧩',
    duration: 120,
    difficulty: '困难',
    traits: ['推理能力', '学习能力']
  }
]

// 任务状态
const taskStarted = ref(false)
const taskCompleted = ref(false)
const selectedTaskId = ref<string | null>(null)
const taskDifficulty = ref(1)
const taskResults = ref<any>(null)

// 推荐任务逻辑（基于HR评估）
const recommendedTaskId = computed(() => {
  if (!props.hrScores) return 'reaction-time'
  
  const scores = props.hrScores
  const conscientiousness = scores['责任心'] || 5
  const emotionalStability = scores['情绪稳定性'] || 5
  
  // 如果责任心和情绪稳定性都高，推荐困难任务
  if (conscientiousness > 7 && emotionalStability > 7) {
    return 'logic'
  }
  // 如果责任心较低，推荐简单任务
  if (conscientiousness < 5) {
    return 'reaction-time'
  }
  // 否则推荐中等难度
  return 'n-back'
})

const recommendedTask = computed(() => {
  return taskTypes.find(t => t.id === recommendedTaskId.value) || taskTypes[1]
})

function selectTask(taskId: string) {
  selectedTaskId.value = taskId
}

function startTask() {
  if (!selectedTaskId.value) {
    ElMessage.warning('请选择一个任务')
    return
  }
  
  // 根据HR评估结果调整难度
  if (props.hrScores) {
    const avgScore = Object.values(props.hrScores).reduce((a, b) => a + b, 0) / Object.values(props.hrScores).length
    taskDifficulty.value = avgScore > 7 ? 3 : avgScore > 5 ? 2 : 1
  }
  
  taskStarted.value = true
}

function handleTaskComplete(results: any) {
  taskResults.value = results
  taskCompleted.value = true
}

function resetTask() {
  taskStarted.value = false
  taskCompleted.value = false
  selectedTaskId.value = null
  taskResults.value = null
}

function finishCognitive() {
  ElMessage.success('认知任务已完成')
  emit('next')
}

function formatMetricLabel(key: string): string {
  const labels: Record<string, string> = {
    accuracy: '准确率',
    avgReactionTime: '平均反应时',
    consistency: '一致性',
    score: '总分'
  }
  return labels[key] || key
}

function formatMetricValue(key: string, value: any): string {
  if (key === 'accuracy' || key === 'consistency') {
    return `${(value * 100).toFixed(1)}%`
  }
  if (key === 'avgReactionTime') {
    return `${value.toFixed(0)}ms`
  }
  return String(value)
}

function getMetricPercentage(key: string, value: any): number {
  if (key === 'accuracy' || key === 'consistency') {
    return value * 100
  }
  if (key === 'avgReactionTime') {
    // 反应时越短越好
    return Math.max(0, 100 - (value / 10))
  }
  return Math.min(100, (value / 10) * 100)
}

function getMetricColor(key: string, value: any): string {
  const percentage = getMetricPercentage(key, value)
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#409eff'
  if (percentage >= 40) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.cognitive-task {
  background: #fff;
  padding: 20px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

/* 任务概览 */
.task-overview {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.overview-header {
  margin-bottom: 24px;
  text-align: center;
}

.overview-header h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #333;
}

.subtitle {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.task-selector {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 任务卡片网格 */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin: 12px 0;
}

.task-card {
  padding: 16px;
  border: 2px solid #eee;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.task-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.task-card.recommended {
  border-color: #67c23a;
  background: #f0f9f0;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.15);
}

.task-card.recommended::before {
  content: '⭐ 推荐';
  display: block;
  font-size: 12px;
  color: #67c23a;
  font-weight: 600;
  margin-bottom: 4px;
}

.task-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.task-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
}

.task-info {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
}

.duration {
  padding: 2px 6px;
  background: #f0f0f0;
  border-radius: 3px;
}

.difficulty {
  padding: 2px 6px;
  background: #fff0f0;
  border-radius: 3px;
  color: #e6a23c;
}

.task-traits {
  display: flex;
  gap: 4px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 12px;
}

/* 任务结果总结 */
.task-summary {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-summary h3 {
  margin: 0 0 12px 0;
  color: #333;
}

.task-summary h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

/* 指标网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.metric-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 6px;
}

.metric-bar {
  width: 100%;
}

/* 分析结果 */
.analysis-section {
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.analysis-text {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
}

/* 任务执行 */
.task-execution {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
