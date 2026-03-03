<template>
  <div class="immersive-dialogue">
    <!-- 舞台背景：模拟真实会议室 -->
    <div class="stage-background">
      <div class="ambient-layer"></div>
      <div class="meeting-room-overlay"></div>
    </div>

    <!-- 多角色面板：展示当前参与的所有角色 -->
    <div class="roles-panel">
      <div 
        v-for="role in activeRoles" 
        :key="role.id"
        :class="['role-card', { active: role.id === currentSpeaker, completed: role.completed }]"
      >
        <div class="role-avatar">
          <img :src="role.avatar" :alt="role.name" />
          <div v-if="role.id === currentSpeaker" class="speaking-indicator"></div>
        </div>
        <div class="role-info">
          <div class="role-name">{{ role.name }}</div>
          <div class="role-title">{{ role.title }}</div>
          <div class="role-status">{{ getRoleStatus(role) }}</div>
        </div>
        <div class="role-progress">
          <el-progress 
            :percentage="role.progress" 
            :color="role.color"
            :show-text="false"
            :stroke-width="3"
          />
        </div>
      </div>
    </div>

    <!-- 主对话区：沉浸式聊天界面 -->
    <div class="dialogue-container">
      <div class="dialogue-header">
        <div class="session-info">
          <h3>{{ sessionTitle }}</h3>
          <div class="session-meta">
            <el-tag size="small" type="info">{{ currentPhase }}</el-tag>
            <span class="time-elapsed">{{ formatTime(elapsedTime) }}</span>
            <span class="conversation-depth">对话深度: {{ conversationDepth }}/10</span>
          </div>
        </div>
        
        <!-- 实时情绪与语气分析 -->
        <div class="sentiment-monitor" v-if="latestSentiment">
          <div class="sentiment-indicator">
            <span class="label">候选人状态:</span>
            <el-tag :type="getSentimentType(latestSentiment.emotion)" size="small">
              {{ latestSentiment.emotion }}
            </el-tag>
          </div>
          <div class="confidence-bar">
            <span class="label">表达自信度:</span>
            <el-progress 
              :percentage="latestSentiment.confidence" 
              :color="getConfidenceColor(latestSentiment.confidence)"
              :show-text="false"
              :stroke-width="4"
            />
          </div>
        </div>
      </div>

      <!-- 消息流 -->
      <div class="message-stream" ref="messageStream">
        <!-- 动态引导提示 -->
        <div v-if="messages.length === 0" class="conversation-starter">
          <div class="starter-content">
            <el-icon class="starter-icon"><i class="el-icon-chat-dot-round"></i></el-icon>
            <h4>欢迎来到沉浸式评估对话</h4>
            <p>接下来，您将与 {{ activeRoles.length }} 位决策者进行自然对话</p>
            <p class="starter-tip">💡 放轻松，像真实面试一样交流即可</p>
          </div>
        </div>

        <!-- 消息列表 -->
        <div 
          v-for="(msg, idx) in messages" 
          :key="idx"
          :class="['message-item', msg.role === 'candidate' ? 'from-candidate' : 'from-role']"
        >
          <!-- 角色消息 -->
          <div v-if="msg.role !== 'candidate'" class="role-message">
            <div class="message-avatar">
              <img :src="getRoleAvatar(msg.role)" :alt="msg.roleName" />
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="speaker-name">{{ msg.roleName }}</span>
                <span class="speaker-title">{{ msg.roleTitle }}</span>
                <span class="timestamp">{{ msg.time }}</span>
              </div>
              <div class="message-body">
                <p>{{ msg.content }}</p>
                <!-- 隐式评估标签 -->
                <div v-if="msg.implicitTags" class="implicit-tags">
                  <el-tag 
                    v-for="tag in msg.implicitTags" 
                    :key="tag"
                    size="small"
                    effect="plain"
                    type="info"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- 候选人消息 -->
          <div v-else class="candidate-message">
            <div class="message-content">
              <div class="message-header">
                <span class="timestamp">{{ msg.time }}</span>
                <span class="response-metrics">
                  <el-icon><i class="el-icon-timer"></i></el-icon>
                  {{ msg.latency }}s
                </span>
              </div>
              <div class="message-body">
                <p>{{ msg.content }}</p>
              </div>
              <!-- 实时反馈气泡 -->
              <div v-if="msg.liveFeedback" class="live-feedback">
                <el-icon class="feedback-icon"><i class="el-icon-data-analysis"></i></el-icon>
                <span>{{ msg.liveFeedback }}</span>
              </div>
            </div>
            <div class="message-avatar">
              <div class="candidate-avatar">You</div>
            </div>
          </div>

          <!-- 角色切换过渡动画 -->
          <div v-if="msg.isRoleTransition" class="role-transition">
            <div class="transition-line"></div>
            <div class="transition-text">
              <el-icon><i class="el-icon-refresh-right"></i></el-icon>
              {{ msg.transitionText }}
            </div>
            <div class="transition-line"></div>
          </div>
        </div>

        <!-- 打字中指示器 -->
        <div v-if="isTyping" class="typing-indicator">
          <div class="typing-avatar">
            <img :src="getRoleAvatar(currentSpeaker)" alt="typing" />
          </div>
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- 智能输入区 -->
      <div class="input-area">
        <!-- 上下文提示条 -->
        <div v-if="contextHint" class="context-hint">
          <el-icon><i class="el-icon-warning-outline"></i></el-icon>
          <span>{{ contextHint }}</span>
        </div>

        <!-- 输入框 -->
        <div class="input-wrapper">
          <el-input
            ref="inputRef"
            v-model="userInput"
            type="textarea"
            :placeholder="dynamicPlaceholder"
            :rows="3"
            :disabled="isProcessing"
            @keydown.ctrl.enter="submitMessage"
            @keydown.meta.enter="submitMessage"
            @input="handleInputChange"
          />
          
          <!-- 智能建议 -->
          <div v-if="smartSuggestions.length > 0" class="smart-suggestions">
            <div class="suggestion-label">💡 建议:</div>
            <div class="suggestion-pills">
              <el-tag 
                v-for="(sugg, idx) in smartSuggestions" 
                :key="idx"
                size="small"
                effect="plain"
                @click="applySuggestion(sugg)"
                style="cursor: pointer;"
              >
                {{ sugg }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="input-controls">
          <div class="control-hints">
            <span>Ctrl+Enter 快速发送</span>
            <span v-if="allowSkip" class="skip-hint" @click="skipCurrentQuestion">
              跳过此问题 →
            </span>
          </div>
          <div class="control-buttons">
            <el-button @click="pauseConversation" :icon="isPaused ? 'VideoPause' : 'VideoPlay'">
              {{ isPaused ? '继续' : '暂停' }}
            </el-button>
            <el-button 
              type="primary" 
              @click="submitMessage"
              :loading="isProcessing"
              :disabled="!canSubmit"
            >
              发送回答
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧洞察面板 -->
    <div class="insights-sidebar">
      <!-- 实时评估雷达 -->
      <el-card class="insight-card radar-card">
        <template #header>
          <div class="card-header">
            <span>实时能力雷达</span>
            <el-tag size="small" type="success">动态更新</el-tag>
          </div>
        </template>
        <div class="radar-chart" ref="radarChart"></div>
        <div class="radar-legend">
          <div v-for="(score, trait) in latestScores" :key="trait" class="legend-item">
            <div class="legend-color" :style="{ background: getTraitColor(trait) }"></div>
            <span class="legend-name">{{ trait }}</span>
            <span class="legend-value">{{ score }}/10</span>
          </div>
        </div>
      </el-card>

      <!-- 行为模式分析 -->
      <el-card class="insight-card pattern-card">
        <template #header>
          <div class="card-header">
            <span>行为模式识别</span>
          </div>
        </template>
        <div class="pattern-list">
          <div v-for="pattern in detectedPatterns" :key="pattern.id" class="pattern-item">
            <div class="pattern-indicator" :style="{ background: pattern.color }"></div>
            <div class="pattern-info">
              <div class="pattern-name">{{ pattern.name }}</div>
              <div class="pattern-desc">{{ pattern.description }}</div>
              <div class="pattern-confidence">
                <span>置信度: {{ pattern.confidence }}%</span>
                <el-progress 
                  :percentage="pattern.confidence" 
                  :color="pattern.color"
                  :show-text="false"
                  :stroke-width="3"
                />
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 对话阶段追踪 -->
      <el-card class="insight-card phase-card">
        <template #header>
          <div class="card-header">
            <span>评估进度</span>
          </div>
        </template>
        <el-steps direction="vertical" :active="currentPhaseIndex" finish-status="success">
          <el-step 
            v-for="(phase, idx) in assessmentPhases" 
            :key="idx"
            :title="phase.title"
            :description="phase.description"
          >
            <template #icon>
              <el-icon v-if="idx < currentPhaseIndex"><i class="el-icon-check"></i></el-icon>
              <el-icon v-else-if="idx === currentPhaseIndex"><i class="el-icon-loading"></i></el-icon>
              <span v-else>{{ idx + 1 }}</span>
            </template>
          </el-step>
        </el-steps>
      </el-card>
    </div>

    <!-- 完成对话弹窗 -->
    <el-dialog
      v-model="showCompletionDialog"
      title="对话评估完成"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="completion-summary">
        <div class="summary-header">
          <el-icon class="success-icon"><i class="el-icon-success-filled"></i></el-icon>
          <h3>恭喜！您已完成所有环节</h3>
        </div>
        <div class="summary-stats">
          <div class="stat-item">
            <div class="stat-value">{{ totalMessages }}</div>
            <div class="stat-label">交互轮次</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatTime(elapsedTime) }}</div>
            <div class="stat-label">总用时</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ completedPhases }}/{{ assessmentPhases.length }}</div>
            <div class="stat-label">完成阶段</div>
          </div>
        </div>
        <div class="summary-highlights">
          <h4>亮点总结</h4>
          <ul>
            <li v-for="(highlight, idx) in highlights" :key="idx">{{ highlight }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCompletionDialog = false">查看详细报告</el-button>
        <el-button type="primary" @click="generateReport">生成完整报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== 类型定义 ====================
interface Role {
  id: string
  name: string
  title: string
  avatar: string
  color: string
  focus: string[]  // 关注的能力维度
  progress: number
  completed: boolean
}

interface Message {
  role: string
  roleName?: string
  roleTitle?: string
  content: string
  time: string
  latency?: number
  implicitTags?: string[]
  liveFeedback?: string
  isRoleTransition?: boolean
  transitionText?: string
}

interface AssessmentPhase {
  id: string
  title: string
  description: string
  roles: string[]
  targetDepth: number
}

interface Pattern {
  id: string
  name: string
  description: string
  confidence: number
  color: string
}

// ==================== Props & Emits ====================
const props = defineProps<{
  candidateId: string
  targetPosition?: string
  assessmentId?: number
  initialContext?: any
}>()

const emit = defineEmits<{
  (e: 'complete', data: any): void
  (e: 'update-scores', scores: Record<string, number>): void
  (e: 'save', data: any): void
}>()

// ==================== 核心状态 ====================
// 角色系统
const activeRoles = ref<Role[]>([
  {
    id: 'hr',
    name: '李明',
    title: 'HR 经理',
    avatar: generateAvatar('HR'),
    color: '#409eff',
    focus: ['沟通能力', '团队协作', '文化契合'],
    progress: 0,
    completed: false
  },
  {
    id: 'tech_lead',
    name: '张伟',
    title: '技术总监',
    avatar: generateAvatar('TL'),
    color: '#67c23a',
    focus: ['技术深度', '问题解决', '系统思维'],
    progress: 0,
    completed: false
  },
  {
    id: 'product',
    name: '王芳',
    title: '产品经理',
    avatar: generateAvatar('PM'),
    color: '#e6a23c',
    focus: ['产品思维', '用户洞察', '创新能力'],
    progress: 0,
    completed: false
  },
  {
    id: 'cto',
    name: '刘强',
    title: 'CTO',
    avatar: generateAvatar('CT'),
    color: '#f56c6c',
    focus: ['战略思维', '领导力', '决策能力'],
    progress: 0,
    completed: false
  }
])

// 评估阶段定义
const assessmentPhases = ref<AssessmentPhase[]>([
  {
    id: 'opening',
    title: '破冰与背景了解',
    description: 'HR 与候选人建立联系，收集基础信息',
    roles: ['hr'],
    targetDepth: 2
  },
  {
    id: 'technical',
    title: '技术深度探索',
    description: '技术总监评估专业能力与问题解决',
    roles: ['tech_lead'],
    targetDepth: 4
  },
  {
    id: 'product_thinking',
    title: '产品思维对话',
    description: '产品经理考察用户视角与创新意识',
    roles: ['product'],
    targetDepth: 6
  },
  {
    id: 'multi_perspective',
    title: '多方圆桌讨论',
    description: '多角色联合提问，考察综合素质',
    roles: ['hr', 'tech_lead', 'product'],
    targetDepth: 8
  },
  {
    id: 'strategic',
    title: '战略层面交流',
    description: 'CTO 最终评估与战略匹配度',
    roles: ['cto'],
    targetDepth: 10
  }
])

// 对话系统
const messages = ref<Message[]>([])
const userInput = ref('')
const currentSpeaker = ref('hr')
const currentPhase = ref('破冰与背景了解')
const currentPhaseIndex = ref(0)
const conversationDepth = ref(0)
const isProcessing = ref(false)
const isTyping = ref(false)
const isPaused = ref(false)

// 时间追踪
const startTime = ref<number>(Date.now())
const elapsedTime = ref(0)
const timerInterval = ref<number | null>(null)

// 评估数据
const latestScores = ref<Record<string, number>>({
  '沟通能力': 0,
  '技术深度': 0,
  '问题解决': 0,
  '团队协作': 0,
  '创新思维': 0,
  '领导潜力': 0
})

const latestSentiment = ref<{ emotion: string; confidence: number } | null>(null)
const detectedPatterns = ref<Pattern[]>([])

// UI 辅助
const sessionTitle = ref('候选人综合评估对话')
const contextHint = ref<string | null>(null)
const smartSuggestions = ref<string[]>([])
const allowSkip = ref(false)
const showCompletionDialog = ref(false)
const highlights = ref<string[]>([])
const inputRef = ref<any>(null)
const messageStream = ref<any>(null)
const radarChart = ref<any>(null)

// ==================== 计算属性 ====================
const dynamicPlaceholder = computed(() => {
  if (isProcessing.value) return '正在分析中...'
  if (isPaused.value) return '对话已暂停'
  
  const phase = assessmentPhases.value[currentPhaseIndex.value]
  if (!phase) return '请输入您的回答...'
  
  return `回答 ${phase.title} 相关问题...`
})

const canSubmit = computed(() => {
  return !isProcessing.value && !isPaused.value && userInput.value.trim().length > 0
})

const totalMessages = computed(() => {
  return messages.value.filter(m => m.role === 'candidate').length
})

const completedPhases = computed(() => {
  return assessmentPhases.value.filter((_, idx) => idx < currentPhaseIndex.value).length
})

// ==================== 核心方法 ====================
// 提交消息
async function submitMessage() {
  if (!canSubmit.value) return

  const content = userInput.value.trim()
  const submitTime = Date.now()
  const lastQuestion = messages.value.filter(m => m.role !== 'candidate').pop()
  const questionTime = lastQuestion?.timestamp || submitTime
  const latency = ((submitTime - questionTime) / 1000).toFixed(1)

  // 添加候选人消息
  messages.value.push({
    role: 'candidate',
    content,
    time: nowTime(),
    latency: parseFloat(latency),
    liveFeedback: generateLiveFeedback(content)
  })

  userInput.value = ''
  isProcessing.value = true
  
  await scrollToBottom()

  try {
    // 1. 提交到后端分析
    const analysis = await analyzeResponse(content, currentSpeaker.value)
    
    // 2. 更新评分
    updateScores(analysis.scores)
    
    // 3. 更新情绪分析
    latestSentiment.value = analysis.sentiment
    
    // 4. 更新行为模式
    if (analysis.patterns) {
      updatePatterns(analysis.patterns)
    }
    
    // 5. 更新角色进度
    updateRoleProgress(currentSpeaker.value)
    
    // 6. 生成下一个问题
    await generateNextQuestion()
    
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error('系统处理失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

// 分析回答 - 调用真实后端 API
async function analyzeResponse(content: string, speaker: string) {
  try {
    const currentRole = activeRoles.value.find(r => r.id === speaker)
    
    const response = await fetch(
      'http://127.0.0.1:8000/assessment/immersive/analyze-response',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify({
          candidate_id: props.candidateId,
          candidate_name: localStorage.getItem('candidate_name') || '候选人',
          candidate_background: props.initialContext?.background,
          current_speaker: speaker,
          speaker_name: currentRole?.name || '',
          speaker_title: currentRole?.title || '',
          candidate_response: content,
          previous_messages: messages.value.slice(-5),
          conversation_depth: conversationDepth.value
        })
      }
    )
    
    if (!response.ok) {
      console.warn('分析 API 失败，使用本地模拟')
      return getLocalFallbackAnalysis(speaker)
    }
    
    const data = await response.json()
    
    if (data.code === 200 && data.data) {
      return {
        scores: data.data.scores || {},
        sentiment: data.data.sentiment || { emotion: '思考中', confidence: 70 },
        patterns: data.data.patterns || []
      }
    } else {
      return getLocalFallbackAnalysis(speaker)
    }
  } catch (error) {
    console.error('分析回答失败:', error)
    return getLocalFallbackAnalysis(speaker)
  }
}

// 本地备用分析
function getLocalFallbackAnalysis(speaker: string) {
  const trait_scores: Record<string, Record<string, number>> = {
    hr: { "沟通能力": 7.5, "团队协作": 7.0, "文化契合": 7.5 },
    tech_lead: { "技术深度": 7.5, "问题解决": 8.0, "系统思维": 7.0 },
    product: { "产品思维": 7.0, "用户洞察": 7.5, "创新能力": 7.5 },
    cto: { "战略思维": 7.5, "领导力": 7.0, "决策能力": 7.5 }
  }
  
  return {
    scores: trait_scores[speaker] || trait_scores.hr,
    sentiment: { emotion: '自信', confidence: 75 },
    patterns: [
      {
        id: 'p1',
        name: '结构化思维',
        description: '回答展现了清晰的逻辑结构',
        confidence: 78,
        color: '#67c23a'
      },
      {
        id: 'p2',
        name: '实例驱动',
        description: '善于用具体案例支撑观点',
        confidence: 72,
        color: '#409eff'
      }
    ]
  }
}

// 生成下一个问题
async function generateNextQuestion() {
  isTyping.value = true
  
  await new Promise(resolve => setTimeout(resolve, 1200))
  
  const phase = assessmentPhases.value[currentPhaseIndex.value]
  
  // 检查是否需要切换角色
  if (shouldSwitchRole()) {
    await handleRoleTransition()
  }
  
  // 生成问题
  const question = await fetchNextQuestion(currentSpeaker.value, messages.value)
  
  const role = activeRoles.value.find(r => r.id === currentSpeaker.value)
  
  messages.value.push({
    role: currentSpeaker.value,
    roleName: role?.name || '',
    roleTitle: role?.title || '',
    content: question.content,
    time: nowTime(),
    implicitTags: question.tags,
    timestamp: Date.now()
  } as any)
  
  isTyping.value = false
  conversationDepth.value++
  
  // 更新上下文提示
  updateContextHint(question.context)
  
  // 生成智能建议
  smartSuggestions.value = question.suggestions || []
  
  await scrollToBottom()
  
  // 检查是否完成
  if (conversationDepth.value >= 10) {
    completeAssessment()
  }
}

// 角色切换
async function handleRoleTransition() {
  const nextRole = determineNextRole()
  
  messages.value.push({
    role: 'system',
    content: '',
    time: '',
    isRoleTransition: true,
    transitionText: `${getRoleName(currentSpeaker.value)} 的提问环节结束，接下来由 ${getRoleName(nextRole)} 继续对话`
  })
  
  currentSpeaker.value = nextRole
  
  // 更新阶段
  const phaseIndex = assessmentPhases.value.findIndex(p => p.roles.includes(nextRole))
  if (phaseIndex !== -1) {
    currentPhaseIndex.value = phaseIndex
    currentPhase.value = assessmentPhases.value[phaseIndex].title
  }
  
  await scrollToBottom()
}

// 判断是否切换角色
function shouldSwitchRole(): boolean {
  const phase = assessmentPhases.value[currentPhaseIndex.value]
  if (!phase) return false
  
  // 达到目标深度，且当前角色进度 > 80%
  const role = activeRoles.value.find(r => r.id === currentSpeaker.value)
  return conversationDepth.value >= phase.targetDepth && (role?.progress || 0) > 80
}

// 确定下一个角色
function determineNextRole(): string {
  const nextPhaseIndex = currentPhaseIndex.value + 1
  if (nextPhaseIndex >= assessmentPhases.value.length) {
    return currentSpeaker.value
  }
  
  const nextPhase = assessmentPhases.value[nextPhaseIndex]
  return nextPhase.roles[0]
}

// 更新评分
function updateScores(newScores: Record<string, number>) {
  // 平滑更新，避免突变
  Object.keys(newScores).forEach(key => {
    const current = latestScores.value[key] || 0
    const target = newScores[key]
    latestScores.value[key] = Math.round((current * 0.7 + target * 0.3) * 10) / 10
  })
  
  emit('update-scores', latestScores.value)
  
  // 更新雷达图
  nextTick(() => {
    renderRadarChart()
  })
}

// 更新角色进度
function updateRoleProgress(roleId: string) {
  const role = activeRoles.value.find(r => r.id === roleId)
  if (!role) return
  
  const increment = 100 / 5  // 假设每个角色需要 5 次互动
  role.progress = Math.min(100, role.progress + increment)
  
  if (role.progress >= 100) {
    role.completed = true
  }
}

// 更新行为模式
function updatePatterns(patterns: Pattern[]) {
  detectedPatterns.value = patterns
}

// 生成实时反馈
function generateLiveFeedback(content: string): string {
  const length = content.length
  if (length < 30) return '回答较简短，可以更详细一些'
  if (length > 200) return '回答很详尽！'
  return '回答长度适中'
}

// 更新上下文提示
function updateContextHint(context: string | null) {
  contextHint.value = context
}

// 应用智能建议
function applySuggestion(suggestion: string) {
  userInput.value = suggestion
  inputRef.value?.focus()
}

// 跳过问题
function skipCurrentQuestion() {
  if (!allowSkip.value) return
  
  ElMessage.warning('已跳过当前问题')
  generateNextQuestion()
}

// 暂停对话
function pauseConversation() {
  isPaused.value = !isPaused.value
  
  if (isPaused.value) {
    ElMessage.info('对话已暂停')
  } else {
    ElMessage.success('对话已继续')
    inputRef.value?.focus()
  }
}

// 完成评估
function completeAssessment() {
  // 生成亮点总结
  highlights.value = [
    '展现了出色的沟通能力，回答清晰有条理',
    '技术深度方面表现突出，能够深入分析问题',
    '产品思维活跃，能从用户角度思考问题',
    '团队协作意识强，善于倾听和反馈'
  ]

  // 准备完成数据
  const completionData = {
    sessionId: `session_${Date.now()}`,
    messages: messages.value,
    scores: latestScores.value,
    patterns: detectedPatterns.value,
    duration: elapsedTime.value,
    conversationDepth: conversationDepth.value,
    candidateId: props.candidateId,
    assessmentId: props.assessmentId,
    startTime: new Date(startTime.value),
    endTime: new Date(),
    totalRounds: messages.value.filter(m => m.role === 'candidate').length,
    highlights: highlights.value
  }

  // 发送 complete 事件给父组件
  emit('complete', completionData)

  showCompletionDialog.value = true
}

// 生成报告
async function generateReport() {
  ElMessage.success('正在保存评估数据...')
  showCompletionDialog.value = false
  
  // 准备完成数据
  const completionData = {
    candidate_id: props.candidateId,
    assessment_id: props.assessmentId,
    job_id: props.initialContext?.job_id,
    messages: messages.value.map(m => ({
      role: m.role,
      content: m.content,
      time: m.time,
      roleName: m.roleName,
      roleTitle: m.roleTitle
    })),
    scores: latestScores.value,
    patterns: detectedPatterns.value,
    duration_seconds: Math.floor(elapsedTime.value / 1000),
    conversation_depth: conversationDepth.value,
    total_rounds: messages.value.filter(m => m.role === 'candidate').length,
    highlights: highlights.value
  }
  
  try {
    // 调用后端保存会话 API
    const response = await fetch(
      'http://127.0.0.1:8000/assessment/immersive/save-session',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify(completionData)
      }
    )
    
    if (!response.ok) {
      throw new Error('保存会话失败')
    }
    
    const result = await response.json()
    
    if (result.code === 200) {
      ElMessage.success('评估数据已保存')
      completionData.assessment_id = result.data?.assessment_id
      completionData.sessionId = result.data?.session_id
    }
  } catch (error) {
    console.error('保存会话错误:', error)
    ElMessage.warning('无法保存到服务器，但可以继续查看报告')
  }
  
  // 通知父组件进行下一步
  emit('save', completionData)
  
  // 然后 emit complete 通知完成
  setTimeout(() => {
    emit('complete', completionData)
  }, 500)
}

// ==================== 辅助方法 ====================
function getRoleStatus(role: Role): string {
  if (role.completed) return '已完成'
  if (role.id === currentSpeaker.value) return '对话中'
  return '等待中'
}

function getRoleAvatar(roleId: string): string {
  const role = activeRoles.value.find(r => r.id === roleId)
  return role?.avatar || ''
}

function getRoleName(roleId: string): string {
  const role = activeRoles.value.find(r => r.id === roleId)
  return role?.name || ''
}

function getSentimentType(emotion: string): string {
  const map: Record<string, string> = {
    '自信': 'success',
    '谨慎': 'warning',
    '积极': 'success',
    '思考中': 'info'
  }
  return map[emotion] || 'info'
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return '#67c23a'
  if (confidence >= 60) return '#409eff'
  if (confidence >= 40) return '#e6a23c'
  return '#f56c6c'
}

function getTraitColor(trait: string): string {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c45656']
  const index = Object.keys(latestScores.value).indexOf(trait)
  return colors[index % colors.length]
}

function generateAvatar(initials: string): string {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c']
  const color = colors[Math.floor(Math.random() * colors.length)]
  return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='${encodeURIComponent(color)}'/%3E%3Ctext x='32' y='40' font-size='20' text-anchor='middle' fill='%23fff'%3E${initials}%3C/text%3E%3C/svg%3E`
}

function nowTime(): string {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

async function scrollToBottom() {
  await nextTick()
  if (messageStream.value) {
    messageStream.value.scrollTop = messageStream.value.scrollHeight
  }
}

function handleInputChange() {
  // 可以在这里添加实时输入分析
}

// ==================== 真实后端 API ====================
async function fetchNextQuestion(speaker: string, history: Message[]) {
  try {
    // 构建对话历史 JSON
    const historyJson = history.map(msg => ({
      role: msg.role,
      content: msg.content
    }))
    
    const currentRole = activeRoles.value.find(r => r.id === speaker)
    
    // 构建查询参数
    const params = new URLSearchParams({
      candidate_id: props.candidateId,
      role_id: speaker,
      role_name: currentRole?.name || speaker,
      conversation_depth: conversationDepth.value.toString(),
      history: JSON.stringify(historyJson)
    })
    
    // 调用后端 API
    const response = await fetch(
      `http://127.0.0.1:8000/assessment/immersive/next-question?${params}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        }
      }
    )
    
    if (!response.ok) {
      console.warn('API 调用失败，使用本地模拟')
      return getLocalFallbackQuestion(speaker)
    }
    
    const data = await response.json()
    
    if (data.code === 200 && data.data) {
      return {
        content: data.data.content,
        tags: data.data.tags || [],
        suggestions: data.data.suggestions || [],
        context: data.data.context
      }
    } else {
      return getLocalFallbackQuestion(speaker)
    }
  } catch (error) {
    console.error('获取问题失败:', error)
    return getLocalFallbackQuestion(speaker)
  }
}

// 本地备用问题库
function getLocalFallbackQuestion(roleId: string) {
  const questionBank: Record<string, any> = {
    hr: {
      content: '请简单介绍一下你自己和你的背景？',
      tags: ['背景了解', '自我认知'],
      suggestions: ['我叫...，毕业于...', '我有...年的工作经验'],
      context: '这是一个开放性问题，轻松回答即可'
    },
    tech_lead: {
      content: '描述一下你最近解决的一个技术难题？',
      tags: ['问题解决', '技术深度'],
      suggestions: ['遇到了...问题', '我通过...方法解决'],
      context: '尽量具体描述技术细节'
    },
    product: {
      content: '如果让你设计一个新功能，你会如何思考？',
      tags: ['产品思维', '用户洞察'],
      suggestions: ['首先了解用户需求', '然后分析竞品'],
      context: '展示你的产品思维过程'
    },
    cto: {
      content: '你对未来 3-5 年的职业规划是什么？',
      tags: ['战略思维', '目标导向'],
      suggestions: ['我的目标是...', '为此我计划...'],
      context: '这是一个关键问题，认真思考'
    }
  }
  
  return questionBank[roleId] || questionBank.hr
}

// 渲染雷达图
function renderRadarChart() {
  if (!radarChart.value) return
  
  const chart = echarts.init(radarChart.value)
  
  const indicator = Object.keys(latestScores.value).map(key => ({
    name: key,
    max: 10
  }))
  
  const data = Object.values(latestScores.value)
  
  const option = {
    radar: {
      indicator,
      splitNumber: 4,
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.05)', 'rgba(64, 158, 255, 0.1)']
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '当前评估',
        areaStyle: {
          color: 'rgba(64, 158, 255, 0.3)'
        },
        lineStyle: {
          color: '#409eff',
          width: 2
        }
      }]
    }]
  }
  
  chart.setOption(option)
}

// ==================== 生命周期 ====================
onMounted(() => {
  // 启动定时器
  timerInterval.value = window.setInterval(() => {
    elapsedTime.value = Date.now() - startTime.value
  }, 1000)
  
  // 初始化对话
  setTimeout(() => {
    generateNextQuestion()
  }, 1000)
  
  // 初始化雷达图
  nextTick(() => {
    renderRadarChart()
  })
})

// 监听分数变化
watch(latestScores, () => {
  renderRadarChart()
}, { deep: true })
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.immersive-dialogue {
  position: relative;
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  grid-template-rows: auto 1fr;
  gap: 16px;
  height: 100vh;
  padding: 16px;
  background: #f5f7fa;
  overflow: hidden;
}

/* ==================== 舞台背景 ==================== */
.stage-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.ambient-layer {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(64, 158, 255, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(103, 194, 58, 0.08) 0%, transparent 50%);
  animation: ambient-shift 20s ease-in-out infinite;
}

.meeting-room-overlay {
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.5) 100%);
}

@keyframes ambient-shift {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

/* ==================== 角色面板 ==================== */
.roles-panel {
  position: relative;
  z-index: 1;
  grid-column: 1;
  grid-row: 1 / 3;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.role-card {
  padding: 12px;
  border-radius: 8px;
  background: #fafbfc;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
}

.role-card.active {
  background: linear-gradient(135deg, #e3f2fd 0%, #f0f7ff 100%);
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.role-card.completed {
  opacity: 0.7;
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
}

.role-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.role-avatar {
  position: relative;
  width: 48px;
  height: 48px;
  margin-bottom: 8px;
}

.role-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.speaking-indicator {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: #67c23a;
  border: 2px solid #fff;
  border-radius: 50%;
  animation: pulse-speaking 1.5s ease-in-out infinite;
}

@keyframes pulse-speaking {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.role-info {
  margin-bottom: 8px;
}

.role-name {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 2px;
}

.role-title {
  font-size: 12px;
  color: #909399;
}

.role-status {
  font-size: 11px;
  color: #67c23a;
  margin-top: 4px;
}

.role-progress {
  margin-top: 8px;
}

/* ==================== 对话容器 ==================== */
.dialogue-container {
  position: relative;
  z-index: 1;
  grid-column: 2;
  grid-row: 1 / 3;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.dialogue-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.session-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.session-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 13px;
}

.time-elapsed,
.conversation-depth {
  opacity: 0.9;
}

.sentiment-monitor {
  margin-top: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  display: flex;
  gap: 20px;
  align-items: center;
}

.sentiment-indicator,
.confidence-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.sentiment-indicator .label,
.confidence-bar .label {
  font-size: 12px;
  opacity: 0.9;
}

/* ==================== 消息流 ==================== */
.message-stream {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafbfc;
}

.conversation-starter {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.starter-content {
  text-align: center;
  max-width: 400px;
}

.starter-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.starter-content h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #2c3e50;
}

.starter-content p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.starter-tip {
  color: #909399;
  font-size: 13px;
  margin-top: 12px;
}

.message-item {
  margin-bottom: 20px;
  animation: message-slide-in 0.3s ease-out;
}

@keyframes message-slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.role-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.candidate-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
}

.speaker-name {
  font-weight: 600;
  color: #2c3e50;
}

.speaker-title {
  color: #909399;
}

.timestamp {
  color: #c0c4cc;
}

.response-metrics {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
}

.message-body {
  padding: 12px 16px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e4e7ed;
  line-height: 1.6;
  color: #2c3e50;
}

.candidate-message .message-body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
}

.implicit-tags {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.live-feedback {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.feedback-icon {
  font-size: 14px;
}

.candidate-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: flex-end;
}

.candidate-message .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* 角色切换 */
.role-transition {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0;
  padding: 12px 0;
}

.transition-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e4e7ed 50%, transparent 100%);
}

.transition-text {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  padding: 6px 12px;
  background: #f5f7fa;
  border-radius: 16px;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 12px;
  align-items: center;
  animation: message-slide-in 0.3s ease-out;
}

.typing-avatar {
  width: 40px;
  height: 40px;
}

.typing-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

/* ==================== 输入区 ==================== */
.input-area {
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.context-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  background: #fff7e6;
  border-left: 3px solid #e6a23c;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
}

.input-wrapper {
  margin-bottom: 12px;
}

.smart-suggestions {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
}

.suggestion-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.suggestion-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-hints {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.skip-hint {
  color: #409eff;
  cursor: pointer;
  transition: color 0.2s;
}

.skip-hint:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

/* ==================== 洞察面板 ==================== */
.insights-sidebar {
  position: relative;
  z-index: 1;
  grid-column: 3;
  grid-row: 1 / 3;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.insight-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
}

.radar-card {
  flex: 0 0 auto;
}

.radar-chart {
  width: 100%;
  height: 220px;
}

.radar-legend {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-name {
  flex: 1;
  color: #606266;
}

.legend-value {
  font-weight: 600;
  color: #2c3e50;
}

.pattern-card {
  flex: 0 0 auto;
}

.pattern-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pattern-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.pattern-indicator {
  width: 4px;
  border-radius: 2px;
  flex-shrink: 0;
}

.pattern-info {
  flex: 1;
}

.pattern-name {
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.pattern-desc {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  margin-bottom: 6px;
}

.pattern-confidence {
  font-size: 11px;
  color: #909399;
}

.pattern-confidence span {
  margin-bottom: 4px;
  display: block;
}

.phase-card {
  flex: 1;
  min-height: 0;
}

/* ==================== 完成对话框 ==================== */
.completion-summary {
  padding: 20px 0;
}

.summary-header {
  text-align: center;
  margin-bottom: 24px;
}

.success-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 12px;
}

.summary-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  display: block;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.summary-highlights h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #2c3e50;
}

.summary-highlights ul {
  margin: 0;
  padding-left: 20px;
}

.summary-highlights li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1400px) {
  .immersive-dialogue {
    grid-template-columns: 240px 1fr 280px;
  }
}

@media (max-width: 1200px) {
  .immersive-dialogue {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }
  
  .roles-panel {
    grid-column: 1;
    grid-row: 1;
    flex-direction: row;
    overflow-x: auto;
  }
  
  .dialogue-container {
    grid-column: 1;
    grid-row: 2;
  }
  
  .insights-sidebar {
    grid-column: 1;
    grid-row: 3;
    flex-direction: row;
    overflow-x: auto;
  }
  
  .insight-card {
    flex: 0 0 300px;
  }
}
</style>
