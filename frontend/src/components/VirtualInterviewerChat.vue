<template>
  <div class="interviewer-chat-container">
    <!-- 面试官选择面板 -->
    <div class="interviewer-selector" v-if="!sessionStarted">
      <h2>选择虚拟面试官</h2>
      <p>请选择你要进行对话的面试官：</p>
      
      <div class="interviewers-grid">
        <div
          v-for="interviewer in availableInterviewers"
          :key="interviewer.role_id"
          class="interviewer-card"
          @click="selectInterviewer(interviewer)"
          :class="{ selected: selectedInterviewer?.role_id === interviewer.role_id }"
        >
          <h3>{{ interviewer.role_name }}</h3>
          <p class="role-type">{{ getRoleTypeCN(interviewer.role_type) }}</p>
          <p class="description">{{ interviewer.role_description }}</p>
          <div class="focus-areas">
            <span v-for="area in interviewer.focus_areas" :key="area" class="tag">
              {{ area }}
            </span>
          </div>
        </div>
      </div>
      
      <button
        @click="startInterview"
        :disabled="!selectedInterviewer"
        class="btn btn-primary start-btn"
      >
        开始面试
      </button>
    </div>

    <!-- 聊天界面 -->
    <div class="chat-interface" v-else>
      <!-- 头部：显示当前面试官信息 -->
      <div class="chat-header">
        <div class="interviewer-info">
          <h3>{{ currentInterviewer?.role_name }}</h3>
          <p>第 {{ currentRound + 1 }} 轮面试</p>
        </div>
        <button @click="switchInterviewer" class="btn btn-secondary">
          切换面试官
        </button>
      </div>

      <!-- 对话历史 -->
      <div class="chat-history">
        <div
          v-for="(message, idx) in chatHistory"
          :key="idx"
          class="message"
          :class="{ 'message-assistant': message.role === 'assistant', 'message-user': message.role === 'user' }"
        >
          <div class="message-content">
            <span v-if="message.role === 'assistant'" class="sender">{{ currentInterviewer?.role_name }}</span>
            <span v-else class="sender">你</span>
            <p>{{ message.content }}</p>
          </div>
        </div>

        <!-- 流式输出显示 -->
        <div v-if="streamingContent" class="message message-streaming">
          <div class="message-content">
            <span class="sender">{{ currentInterviewer?.role_name }}</span>
            <p>{{ streamingContent }}</p>
            <span class="cursor">▌</span>
          </div>
        </div>

        <!-- 加载指示器 -->
        <div v-if="isLoading" class="message message-loading">
          <div class="spinner"></div>
          <p>面试官正在思考...</p>
        </div>

        <!-- 评估进行中 -->
        <div v-if="evaluationInProgress" class="evaluation-indicator">
          <span class="dot-pulse"></span>
          后台评估进行中...
        </div>
      </div>

      <!-- 输入框 -->
      <div class="chat-input-area">
        <textarea
          v-model="userMessage"
          @keydown.enter.ctrl="sendMessage"
          @keydown.enter.shift="newLine"
          placeholder="输入你的回答... (Ctrl+Enter 发送)"
          :disabled="isLoading"
          class="message-input"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!userMessage.trim() || isLoading"
          class="btn btn-primary send-btn"
        >
          {{ isLoading ? '等待中...' : '发送' }}
        </button>
      </div>

      <!-- 评分面板 -->
      <div v-if="currentScores && Object.keys(currentScores).length > 0" class="scores-panel">
        <h4>当前评分</h4>
        <div class="scores-list">
          <div v-for="(score, dimension) in currentScores" :key="dimension" class="score-item">
            <span class="dimension">{{ dimension }}</span>
            <div class="score-bar">
              <div class="score-value" :style="{ width: (score / 10 * 100) + '%' }"></div>
            </div>
            <span class="score-number">{{ score.toFixed(1) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 面试官切换对话 -->
    <div v-if="showSwitchDialog" class="modal-overlay">
      <div class="modal">
        <h2>选择下一位面试官</h2>
        <div class="interviewers-list">
          <div
            v-for="interviewer in availableInterviewers"
            :key="interviewer.role_id"
            class="list-item"
            :class="{ disabled: interviewer.role_id === currentInterviewer?.role_id }"
            @click="confirmSwitch(interviewer)"
          >
            <h4>{{ interviewer.role_name }}</h4>
            <p>{{ interviewer.role_description }}</p>
          </div>
        </div>
        <button @click="showSwitchDialog = false" class="btn btn-secondary">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { request } from '@/utils/request'

// ==================== 数据定义 ====================

interface Interviewer {
  role_id: string
  role_name: string
  role_type: string
  tone: string
  focus_areas: string[]
  role_description: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

interface SessionState {
  session_id: string
  current_interviewer: string
  current_round: number
  conversation_count: number
  questions_asked: string[]
  scores: Record<string, number>
}

// ==================== 状态 ====================

const availableInterviewers = ref<Interviewer[]>([])
const selectedInterviewer = ref<Interviewer | null>(null)
const currentInterviewer = ref<Interviewer | null>(null)
const sessionStarted = ref(false)
const sessionId = ref<string>('')
const candidateId = ref<string>('candidate_001')

const chatHistory = ref<ChatMessage[]>([])
const userMessage = ref<string>('')
const isLoading = ref(false)
const streamingContent = ref<string>('')
const currentRound = ref(0)
const currentScores = ref<Record<string, number>>({})
const evaluationInProgress = ref(false)

const showSwitchDialog = ref(false)

// ==================== 计算属性 ====================

const chatHistoryRef = ref<HTMLElement | null>(null)

const roleTypeMap: Record<string, string> = {
  hr: '人力资源专家',
  tech_lead: '技术总监',
  product_manager: '产品经理',
  ceo: '首席执行官'
}

function getRoleTypeCN(roleType: string): string {
  return roleTypeMap[roleType] || roleType
}

// ==================== 方法 ====================

// 初始化：加载所有面试官
async function loadInterviewers() {
  try {
    const response = await request.get('/interview/interviewers')
    availableInterviewers.value = response.data
  } catch (error) {
    console.error('加载面试官失败', error)
  }
}

// 选择面试官
function selectInterviewer(interviewer: Interviewer) {
  selectedInterviewer.value = interviewer
}

// 开始面试
async function startInterview() {
  if (!selectedInterviewer.value) return

  try {
    // 创建会话
    const response = await request.post('/interview/session/create', {
      candidate_id: candidateId.value,
      interviewer_id: selectedInterviewer.value.role_id
    })

    sessionId.value = response.data.session_id
    currentInterviewer.value = selectedInterviewer.value
    sessionStarted.value = true

    // 添加欢迎消息
    chatHistory.value.push({
      role: 'assistant',
      content: response.data.opening_message,
      timestamp: new Date().toISOString()
    })

    // 滚动到底部
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('开始面试失败', error)
  }
}

// 发送消息 - 核心的流式处理
async function sendMessage() {
  if (!userMessage.value.trim() || !currentInterviewer.value) return

  const candidateMessage = userMessage.value
  userMessage.value = ''

  // 添加用户消息到历史
  chatHistory.value.push({
    role: 'user',
    content: candidateMessage,
    timestamp: new Date().toISOString()
  })

  isLoading.value = true
  evaluationInProgress.value = true
  streamingContent.value = ''

  try {
    // 使用 SSE 流式处理
    const eventSource = new EventSource(
      `/interview/chat/stream?` +
      `interviewer_id=${currentInterviewer.value.role_id}&` +
      `candidate_id=${candidateId.value}&` +
      `candidate_message=${encodeURIComponent(candidateMessage)}&` +
      `round_num=${currentRound.value}`
    )

    let fullResponse = ''

    eventSource.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.type === 'start') {
          streamingContent.value = ''
        } else if (data.type === 'content') {
          streamingContent.value += data.data
          fullResponse += data.data
        } else if (data.type === 'end') {
          // 对话完成
          chatHistory.value.push({
            role: 'assistant',
            content: fullResponse,
            timestamp: new Date().toISOString()
          })
          streamingContent.value = ''
          isLoading.value = false
          eventSource.close()
        } else if (data.type === 'error') {
          console.error('聊天错误:', data.message)
          isLoading.value = false
          eventSource.close()
        }
      } catch (error) {
        console.error('解析 SSE 消息失败:', error)
      }
    })

    eventSource.onerror = () => {
      isLoading.value = false
      eventSource.close()
    }

    // 后台评估任务会自动进行（不阻塞对话流）
    // 评估完成后 evaluationInProgress 会通过 WebSocket 或轮询更新

    // 更新会话状态（获取当前评分等）
    await updateSessionState()
  } catch (error) {
    console.error('发送消息失败', error)
    isLoading.value = false
  }

  await nextTick()
  scrollToBottom()
}

// 更新会话状态
async function updateSessionState() {
  try {
    const response = await request.get(`/interview/session/${sessionId.value}/state`)
    currentScores.value = response.data.scores || {}
    currentRound.value = response.data.current_round
  } catch (error) {
    console.error('更新会话状态失败:', error)
  }
}

// 切换面试官
function switchInterviewer() {
  showSwitchDialog.value = true
}

async function confirmSwitch(newInterviewer: Interviewer) {
  if (newInterviewer.role_id === currentInterviewer.value?.role_id) return

  try {
    const response = await request.post('/interview/interviewer/switch', {
      interviewer_id: newInterviewer.role_id,
      candidate_id: candidateId.value,
      session_id: sessionId.value
    })

    currentInterviewer.value = newInterviewer
    chatHistory.value.push({
      role: 'assistant',
      content: response.data.opening_message,
      timestamp: new Date().toISOString()
    })

    showSwitchDialog.value = false
    await updateSessionState()
    scrollToBottom()
  } catch (error) {
    console.error('切换面试官失败', error)
  }
}

// 滚动到底部
function scrollToBottom() {
  const container = document.querySelector('.chat-history')
  if (container) {
    setTimeout(() => {
      container.scrollTop = container.scrollHeight
    }, 0)
  }
}

// 新行
function newLine(event: KeyboardEvent) {
  // 让 Shift+Enter 正常换行
  event.preventDefault()
  userMessage.value += '\n'
}

// ==================== 生命周期 ====================

onMounted(async () => {
  await loadInterviewers()
})
</script>

<style scoped>
.interviewer-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* ==================== 面试官选择面板 ==================== */

.interviewer-selector {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.interviewer-selector h2 {
  font-size: 32px;
  margin-bottom: 20px;
  color: #2c3e50;
}

.interviewer-selector > p {
  font-size: 16px;
  color: #7f8c8d;
  margin-bottom: 40px;
}

.interviewers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1200px;
  margin-bottom: 40px;
}

.interviewer-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.interviewer-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.interviewer-card.selected {
  border-color: #3498db;
  background: #ecf0f1;
}

.interviewer-card h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: #2c3e50;
}

.interviewer-card .role-type {
  font-size: 14px;
  color: #3498db;
  margin-bottom: 12px;
  font-weight: 600;
}

.interviewer-card .description {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 16px;
  line-height: 1.5;
}

.focus-areas {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-block;
  background: #ecf0f1;
  color: #2c3e50;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
}

.start-btn {
  padding: 12px 48px;
  font-size: 16px;
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ==================== 聊天界面 ==================== */

.chat-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.interviewer-info h3 {
  font-size: 18px;
  margin-bottom: 4px;
}

.interviewer-info p {
  font-size: 14px;
  opacity: 0.9;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  animation: slideIn 0.3s ease;
}

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

.message-assistant {
  justify-content: flex-start;
}

.message-user {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message-assistant .message-content {
  background: #ecf0f1;
  color: #2c3e50;
}

.message-user .message-content {
  background: #3498db;
  color: white;
}

.sender {
  font-size: 12px;
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
  opacity: 0.8;
}

.message-streaming .cursor {
  display: inline-block;
  animation: blink 1s infinite;
  margin-left: 4px;
}

@keyframes blink {
  0%, 49% {
    opacity: 1;
  }
  50%, 100% {
    opacity: 0;
  }
}

.message-loading {
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ecf0f1;
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.evaluation-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fef9e7;
  border-radius: 8px;
  font-size: 14px;
  color: #f39c12;
}

.dot-pulse {
  width: 8px;
  height: 8px;
  background: #f39c12;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  background: white;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #bdc3c7;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  max-height: 100px;
  min-height: 44px;
}

.message-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.message-input:disabled {
  background: #ecf0f1;
  color: #95a5a6;
}

.send-btn {
  padding: 12px 24px;
  white-space: nowrap;
}

/* ==================== 评分面板 ==================== */

.scores-panel {
  padding: 16px;
  background: #f8f9fa;
  border-top: 1px solid #ecf0f1;
}

.scores-panel h4 {
  margin-bottom: 12px;
  color: #2c3e50;
  font-size: 14px;
}

.scores-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dimension {
  font-size: 12px;
  color: #7f8c8d;
  min-width: 80px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
}

.score-value {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.score-number {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  min-width: 30px;
  text-align: right;
}

/* ==================== 模态框 ==================== */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.interviewers-list {
  margin-bottom: 20px;
}

.list-item {
  padding: 16px;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 12px;
}

.list-item:hover:not(.disabled) {
  background: #f8f9fa;
  border-color: #3498db;
}

.list-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.list-item h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.list-item p {
  margin: 0;
  font-size: 14px;
  color: #7f8c8d;
}

/* ==================== 按钮 ==================== */

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ==================== 响应式设计 ==================== */

@media (max-width: 768px) {
  .interviewers-grid {
    grid-template-columns: 1fr;
  }

  .interviewer-selector {
    padding: 20px;
  }

  .message-content {
    max-width: 90%;
  }

  .scores-list {
    grid-template-columns: 1fr;
  }

  .chat-input-area {
    flex-direction: column;
  }
}
</style>
