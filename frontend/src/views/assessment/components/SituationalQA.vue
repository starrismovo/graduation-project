<template>
  <div class="situational-qa">
    <div class="agent-info">
      <img class="agent-avatar" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%23667eea'/%3E%3Ctext x='32' y='40' font-size='28' text-anchor='middle' fill='%23fff'%3EA%3C/text%3E%3C/svg%3E" />
      <div>
        <div class="agent-name">虚拟面试官 · HR-Agent</div>
        <div class="agent-sub">情境问答评估中 ({{ currentRound }}/{{ maxRounds }})</div>
      </div>
    </div>

    <!-- 初始情景展示 -->
    <div v-if="!scenarioLoaded" class="scenario-intro">
      <el-skeleton :rows="3" animated />
      <el-button type="primary" @click="loadScenario" style="margin-top: 12px;">加载情景</el-button>
    </div>

    <!-- 情景描述 + 自动开始对话 -->
    <div v-if="scenarioLoaded && !conversationStarted" class="scenario-preparing">
      <div class="scenario-content">
        <h4>{{ scenario.title }}</h4>
        <p>{{ scenario.description }}</p>
        <div class="scenario-footer">
          <span>目标特质：{{ scenario.target_traits.join(' / ') }}</span>
          <span>最多 {{ scenario.max_rounds }} 轮对话</span>
        </div>
      </div>
      <div class="preparing-indicator">
        <el-icon class="is-loading"><i class="el-icon-loading"></i></el-icon>
        <span>面试官正在准备开场白...</span>
      </div>
    </div>

    <!-- 对话界面：自动开始，无缝输入 -->
    <div v-else class="conversation-view">
      <div class="chat-window" ref="chatWindow">
        <!-- 首次输入提示 -->
        <div v-if="answers.length === 0" class="first-tip">
          <el-icon class="tip-icon"><i class="el-icon-info"></i></el-icon>
          <div class="tip-text">
            <p>面试官已发送开场白，请在下方输入框中输入你的回答。</p>
            <p style="font-size: 12px; color: #999; margin-top: 4px;">💡 提示：详细、有条理的回答会获得更高的评分</p>
          </div>
        </div>

        <!-- 对话消息 -->
        <div v-for="(m, idx) in messages" :key="idx" :class="['chat-item', m.role]">
          <div class="chat-bubble">{{ m.content }}</div>
          <div class="chat-meta">{{ m.time }} {{ m.latency ? '· ' + m.latency + 's' : '' }}</div>
        </div>

        <!-- 加载中提示 -->
        <div v-if="isLoading && answers.length > 0" class="loading-tip">
          <el-icon class="is-loading"><i class="el-icon-loading"></i></el-icon>
          <span>AI 正在分析你的回答...</span>
        </div>
      </div>

      <!-- 输入框 + 提交按钮 -->
      <div class="chat-input">
        <el-input 
          ref="inputRef"
          type="textarea" 
          v-model="userInput" 
          :placeholder="inputPlaceholder" 
          rows="3" 
          :disabled="isLoading"
          @keydown.ctrl.enter="submitAnswer"
          @keydown.meta.enter="submitAnswer"
        ></el-input>
        
        <div class="input-hint">
          <span v-if="!isLoading" style="color: #999; font-size: 12px;">
            💡 Ctrl+Enter 快捷提交 | 
            <span v-if="currentRound >= maxRounds"> 已完成所有回答</span>
            <span v-else> 还有 {{ maxRounds - currentRound + 1 }} 轮</span>
          </span>
        </div>

        <div class="chat-controls">
          <el-button @click="cancelConversation">退出评估</el-button>
          <el-button 
            type="primary" 
            @click="submitAnswer" 
            :loading="isLoading" 
            :disabled="!userInput.trim() || isLoading"
          >
            提交回答
          </el-button>
          <el-button 
            v-if="currentRound >= maxRounds && answers.length > 0" 
            type="success" 
            @click="finishScenario"
          >
            完成情景 ✓
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const props = defineProps<{
  candidateId: string
  scenarioId?: string
}>()

const emit = defineEmits<{
  (e: 'update-answers', payload: Array<any>): void
  (e: 'update-scenario', payload: any): void
  (e: 'next'): void
}>()

// 状态管理
const scenario = ref<any>(null)
const scenarioLoaded = ref(false)
const conversationStarted = ref(false)
const currentRound = ref(0)
const maxRounds = ref(3)
const isLoading = ref(false)
const inputRef = ref<any>(null)

const messages = ref<Array<{ role: string; content: string; time: string; latency?: number }>>([])
const userInput = ref('')
const answers = ref<Array<{ text: string; time: string; latency: number; emotion: string }>>([])

// 计算动态占位符
const inputPlaceholder = computed(() => {
  if (isLoading.value) return '正在处理...'
  if (answers.length === 0) return '请开始你的回答...'
  if (currentRound.value >= maxRounds.value) return '已完成所有回答'
  return `请回答第 ${currentRound.value} 轮问题...`
})

// 第一个问题（初始问题）
const initialQuestions: Record<string, string> = {
  'scenario_001': '你好，我是 HR-Agent，我们现在讨论一个情景。请根据左侧所述情景，说出你的初步想法和处理方案。',
  'scenario_002': '我是你的面试官，请听我讲述这个情景，然后告诉我你的看法。'
}

function nowTime(): string {
  const d = new Date()
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// 加载情景
async function loadScenario() {
  isLoading.value = true
  try {
    const sid = props.scenarioId || 'scenario_001'
    const res = await request.get(`/api/interview/scenarios/${sid}`)
    scenario.value = res.data
    maxRounds.value = res.data.max_rounds || 3
    scenarioLoaded.value = true
    
    // 将情景信息传给父组件（左侧动态显示）
    emit('update-scenario', res.data)
    
    // 自动开始对话（不需要用户点击按钮）
    setTimeout(() => {
      startConversation()
    }, 500) // 延迟 500ms，给用户看到情景的机会
    
  } catch (error) {
    ElMessage.error('加载情景失败')
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

// 开始对话：自动生成开场白
function startConversation() {
  conversationStarted.value = true
  currentRound.value = 1
  
  // 根据场景生成或使用预定义的开场白
  let openingMessage = initialQuestions[scenario.value.id]
  
  // 如果没有预定义，根据场景特征生成
  if (!openingMessage) {
    const traits = scenario.value.target_traits?.join('、') || '综合能力'
    openingMessage = `你好，我是 HR 面试官。我们今天要讨论一个情景，重点考察你的${traits}。请根据上述情景，说出你的初步想法和处理方案。`
  }
  
  messages.value = [
    {
      role: 'agent',
      content: openingMessage,
      time: nowTime(),
      latency: 0
    }
  ]
  
  // 自动焦点到输入框
  setTimeout(() => {
    inputRef.value?.focus()
  }, 300)
}

// 提交回答
async function submitAnswer() {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入回答')
    return
  }

  isLoading.value = true
  const startTime = Date.now()

  try {
    const answer = userInput.value.trim()
    const latency = ((Date.now() - startTime) / 1000).toFixed(1)

    // 1. 保存回答
    const responseData = {
      candidate_id: props.candidateId,
      scenario_id: scenario.value.id,
      round_num: currentRound.value,
      question: messages.value[messages.value.length - 1]?.content || '',
      answer,
      answer_latency: parseFloat(latency),
      emotion: 'neutral'
    }

    const saveRes = await request.post('/api/interview/save-response', responseData)
    const responseId = saveRes.data.id

    // 2. 评分
    const scoreRes = await request.post('/api/interview/score-answer', {
      candidate_id: props.candidateId,
      scenario_id: scenario.value.id,
      response_id: responseId,
      target_traits: scenario.value.target_traits,
      answer
    })

    // 添加用户回答到消息
    messages.value.push({
      role: 'candidate',
      content: answer,
      time: nowTime(),
      latency: parseFloat(latency)
    })

    // 记录回答
    answers.value.push({
      text: answer,
      time: nowTime(),
      latency: parseFloat(latency),
      emotion: 'neutral',
      scores: scoreRes.data.scores,        // 📊 添加评分
      reasoning: scoreRes.data.reasoning   // 💡 添加分析理由
    })

    userInput.value = ''

    // 3. 检查是否可以继续
    if (currentRound.value < maxRounds.value) {
      // 生成追问
      setTimeout(async () => {
        try {
          await generateFollowUp()
        } catch (error) {
          console.error(error)
        }
      }, 800) // 延迟一点，让用户看到自己的回答
    } else {
      // 达到最大轮次
      messages.value.push({
        role: 'agent',
        content: '感谢你的详细回答。我们已经完成了所有轮次的问答。请点击"完成情景"按钮结束本轮评估。',
        time: nowTime()
      })
    }

    // 发送更新
    emit('update-answers', answers.value)
  } catch (error) {
    ElMessage.error('提交失败，请重试')
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

// 生成追问：自动进行，无需用户交互
async function generateFollowUp() {
  try {
    const previousAnswers = messages.value
      .filter((_, i) => i > 0)
      .reduce((acc, msg, i) => {
        if (i % 2 === 0) {
          acc.push({ question: msg.content, answer: messages.value[i + 2]?.content || '' })
        }
        return acc
      }, [] as any[])

    const followUpRes = await request.post('/api/interview/follow-up-question', {
      candidate_id: props.candidateId,
      scenario_id: scenario.value.id,
      round_num: currentRound.value + 1,
      previous_answers: previousAnswers
    })

    currentRound.value++
    messages.value.push({
      role: 'agent',
      content: followUpRes.data.question,
      time: nowTime()
    })

    // 自动焦点到输入框
    setTimeout(() => {
      inputRef.value?.focus()
    }, 300)
    
  } catch (error) {
    ElMessage.error('生成追问失败，请重试')
    console.error(error)
  }
}

// 完成情景
function finishScenario() {
  ElMessage.success('情景问答已完成')
  emit('next')
}

// 取消对话
function cancelConversation() {
  conversationStarted.value = false
  messages.value = []
  userInput.value = ''
  currentRound.value = 0
}

onMounted(() => {
  loadScenario()
})
</script>

<style scoped>
.situational-qa { background: #fff; padding: 12px; min-height: 600px; display: flex; flex-direction: column; }
.agent-info { display: flex; gap: 12px; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }
.agent-avatar { width: 48px; height: 48px; border-radius: 6px; }
.agent-name { font-weight: 600; }
.agent-sub { color: #999; font-size: 12px; }

.scenario-intro { padding: 20px; text-align: center; }

/* 场景准备状态：自动开始前的界面 */
.scenario-preparing { 
  padding: 20px; 
  flex: 1; 
  display: flex; 
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.scenario-content { 
  padding: 20px; 
  background: #f0f9ff; 
  border-radius: 8px; 
  margin-bottom: 20px; 
  flex: 1;
  min-width: 100%;
}
.scenario-content h4 { margin-top: 0; color: #409eff; }
.scenario-content p { color: #333; line-height: 1.6; }
.scenario-footer { 
  display: flex; 
  justify-content: space-between; 
  font-size: 12px; 
  color: #999; 
  margin-top: 12px; 
  padding-top: 12px; 
  border-top: 1px solid #ddd;
}

/* 准备中指示器 */
.preparing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-size: 14px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 6px;
  animation: pulse 2s infinite;
}
.preparing-indicator .is-loading {
  font-size: 18px;
}

/* 对话界面 */
.conversation-view { flex: 1; display: flex; flex-direction: column; }
.chat-window { 
  flex: 1; 
  overflow: auto; 
  padding: 12px; 
  background: #f7f9fb; 
  border-radius: 6px; 
  margin: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-item { margin-bottom: 0; display: flex; flex-direction: column; }
.chat-item.agent { align-items: flex-start; }
.chat-item.candidate { align-items: flex-end; }
.chat-bubble { 
  padding: 10px 14px; 
  border-radius: 8px; 
  max-width: 75%; 
  word-wrap: break-word;
  animation: slideIn 0.3s ease-out;
}
.chat-item.agent .chat-bubble { background: #fff; color: #333; border: 1px solid #ddd; }
.chat-item.candidate .chat-bubble { background: #409eff; color: #fff; }
.chat-meta { font-size: 12px; color: #999; margin-top: 4px; }

/* 首次输入提示 */
.first-tip {
  padding: 12px;
  background: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 8px;
}
.tip-icon {
  font-size: 18px;
  color: #409eff;
  flex-shrink: 0;
}
.tip-text {
  flex: 1;
  font-size: 13px;
  color: #333;
}
.tip-text p {
  margin: 0;
  line-height: 1.5;
}

/* 加载中提示 */
.loading-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 12px;
  padding: 8px 0;
  justify-content: flex-start;
}
.loading-tip .is-loading {
  font-size: 14px;
  color: #409eff;
}

/* 输入框样式 */
.chat-input { 
  margin-top: 12px; 
  display: flex; 
  flex-direction: column; 
  gap: 8px;
}

.input-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
  padding: 0 2px;
  min-height: 20px;
}

.chat-controls { 
  display: flex; 
  gap: 8px; 
  justify-content: flex-end;
}

/* 动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@media (max-width: 900px) {
  .situational-qa { min-height: 400px; }
  .chat-bubble { max-width: 90%; }
  .scenario-content { margin-bottom: 0; }
}
</style>
