<template>
  <div class="immersive-dialogue">
    <!-- 舞台背景：模拟真实会议室 -->
    <div class="stage-background">
      <div class="ambient-layer"></div>
      <div class="meeting-room-overlay"></div>
    </div>

    <!-- 左侧：候选人信息与流程控制 -->
    <div class="left-sidebar" :style="{ backgroundImage: svgImageUrl ? `url(${svgImageUrl})` : 'none' }">
      <!-- SVG遮罩文字，在 svg 模式时显示 -->
      <div v-if="leftPanelMode === 'svg'" class="svg-overlay">
        <div class="placeholder-text">
          <p></p>
          <p class="sub-text"></p>
        </div>
      </div>

      <!-- 面板内容（info模式）覆盖在背景上，半透明白色背景 -->
      <div v-if="leftPanelMode === 'info'" class="panel-overlay">
        <!-- 关闭按钮 -->
        <div class="panel-title">
          <el-button text icon="Close" @click="toggleLeftPanel('svg')" class="close-btn" />
          <el-icon><i class="el-icon-user"></i></el-icon>
          <span>候选人信息</span>
          <el-tag v-if="currentStep >= 1" size="small" type="success">已填充</el-tag>
        </div>
        <!-- 流程指示器 -->
        <div class="process-indicator">
          <div 
            v-for="(step, idx) in assessmentSteps" 
            :key="idx"
            :class="['step', { active: idx === currentStep, completed: idx < currentStep }]"
            @click="currentStep = idx"
          >
            <div class="step-number">{{ idx + 1 }}</div>
            <div class="step-title">{{ step }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 中间主对话区：沉浸式聊天界面 -->
    <div class="dialogue-container">
      <div class="dialogue-header">
        <div class="session-info">
          <div class="header-content">
            <div class="ai-profile">
              <img :src="aiInterviewerAvatar" class="ai-avatar" />
              <div class="ai-info">
                <h3>AI 面试官</h3>
                <p>{{ aiInterviewerTitle }}</p>
              </div>
            </div>
            <div class="session-meta">
              <el-tag size="small" type="info">{{ currentPhase }}</el-tag>
              <span class="time-elapsed">⏱️ {{ formatTime(elapsedTime) }}</span>
              <span class="progress">📊 {{ respondedCount }}/{{ interviewPlan.totalQuestions }}</span>
            </div>
          </div>
        </div>
        
        <!-- 实时情绪与语气分析 -->
        <div class="sentiment-monitor" v-if="latestSentiment && currentStep >= 3">
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
        <!-- Step 0: 初始欢迎 -->
        <div v-if="currentStep === 0" class="conversation-starter initial-greeting">
          <div class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>欢迎来到 AI 情境面试系统</h4>
            <p>你好！我是 AI 面试官，很高兴认识你。</p>
            <p class="starter-tip">请先完善你的个人信息或上传简历</p>
            <el-button type="primary" @click="openUploadDialog" class="upload-action-btn" size="large">
              📋 上传完善信息
            </el-button>
          </div>
        </div>

        <!-- Step 1: 简历解析阶段 -->
        <div v-if="currentStep === 1" class="conversation-starter resume-parsing">
          <div class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>✅ 信息已确认</h4>
            <p>我已成功分析了你的基本信息和背景</p>
            
            <!-- 显示解析的信息 -->
            <div v-if="parsedResumeData" class="parsed-info-display">
              <div class="info-card">
                <div class="info-header">📋 候选人信息</div>
                <div class="info-content">
                  <div class="info-row">
                    <span class="label">姓名:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.name }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">邮箱:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.email }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">学历:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.education }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">经验水平:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.experience_level }}</span>
                  </div>
                  <div class="info-row" v-if="parsedResumeData.extraction_method">
                    <span class="label">识别方式:</span>
                    <span class="value">
                      <el-tag :type="parsedResumeData.extraction_method === 'ocr' ? 'warning' : 'success'">
                        {{ parsedResumeData.extraction_method === 'ocr' ? '🤖 OCR识别(扫描版)' : '✅ 原生提取' }}
                      </el-tag>
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-if="parsedResumeData.candidate_info.technical_skills.length > 0" class="info-card">
                <div class="info-header">💻 技术能力</div>
                <div class="skills-list">
                  <el-tag 
                    v-for="skill in parsedResumeData.candidate_info.technical_skills"
                    :key="skill"
                    type="primary"
                    effect="light"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
              </div>

              <div v-if="parsedResumeData.candidate_info.soft_skills.length > 0" class="info-card">
                <div class="info-header">✨ 核心素质</div>
                <div class="skills-list">
                  <el-tag 
                    v-for="skill in parsedResumeData.candidate_info.soft_skills"
                    :key="skill"
                    type="success"
                    effect="light"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
              </div>

              <div class="info-card">
                <div class="info-header">📊 评估维度 ({{ parsedResumeData.assessed_dimensions.length }}项)</div>
                <div class="dimensions-list">
                  <div v-for="(dim, idx) in parsedResumeData.assessed_dimensions" :key="idx" class="dimension-item">
                    {{ ['🎯', '⚡', '🔥', '✨', '🚀'][idx % 5] }} {{ dim }}
                  </div>
                </div>
              </div>
            </div>

            <p class="starter-tip" style="margin-top: 16px;">准备好了吗？点击下方按钮开始面试</p>
            <el-button 
              type="primary" 
              @click="proceedToStep2" 
              size="large"
              class="start-interview-btn"
            >
              🎯 准备开始面试
            </el-button>
          </div>
        </div>

        <!-- Step 2: 面试说明与准备 -->
        <div v-if="currentStep === 2" class="conversation-starter interview-briefing">
          <div class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>📢 面试流程说明</h4>
            
            <div class="briefing-content">
              <p>我已为你制定了个性化的评估计划：</p>
              
              <div class="interview-plan">
                <div class="plan-item">
                  <div class="plan-icon">1️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">破冰与背景了解</div>
                    <p>我们先从你的工作经验和背景开始交流</p>
                  </div>
                </div>

                <div class="plan-item">
                  <div class="plan-icon">2️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">技术深度探索</div>
                    <p>深入讨论你的技术能力和问题解决经验</p>
                  </div>
                </div>

                <div class="plan-item">
                  <div class="plan-icon">3️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">产品思维对话</div>
                    <p>考察你的产品思维和创新意识</p>
                  </div>
                </div>

                <div class="plan-item">
                  <div class="plan-icon">4️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">综合素质评估</div>
                    <p>评价你的沟通能力和团队协作精神</p>
                  </div>
                </div>
              </div>

              <div class="interview-stats">
                <div class="stat-item">
                  <div class="stat-label">预计时长</div>
                  <div class="stat-value">6分钟</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">问题数量</div>
                  <div class="stat-value">{{ interviewPlan.totalQuestions }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">评估维度</div>
                  <div class="stat-value">{{ parsedResumeData?.assessed_dimensions.length || 5 }}</div>
                </div>
              </div>

              <p class="starter-tip">我会在下方实时显示分析结果，请尽量详细地表达你的想法</p>
            </div>

            <el-button 
              type="primary" 
              @click="startInterview" 
              size="large"
              class="start-interview-btn"
            >
              ▶️ 开始面试
            </el-button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div 
          v-for="(msg, idx) in messages" 
          :key="idx"
          :class="['message-item', msg.role === 'candidate' ? 'from-candidate' : 'from-ai']"
        >
          <!-- AI 消息 -->
          <div v-if="msg.role === 'ai'" class="ai-message">
            <div class="message-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="speaker-name">AI 面试官</span>
                <span class="timestamp">{{ msg.time }}</span>
              </div>
              <div class="message-body">
                <p>{{ msg.content }}</p>
                <!-- 评估标签 -->
                <div v-if="msg.tags" class="message-tags">
                  <el-tag 
                    v-for="tag in msg.tags" 
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
                <span class="response-metrics" v-if="msg.responseTime">
                  ⏱️ {{ msg.responseTime }}秒
                </span>
              </div>
              <div class="message-body">
                <p>{{ msg.content }}</p>
              </div>
              <!-- AI 反馈 -->
              <div v-if="msg.aiFeedback" class="ai-feedback">
                <el-icon><i class="el-icon-documentcopy"></i></el-icon>
                <span>{{ msg.aiFeedback }}</span>
              </div>
            </div>
            <div class="message-avatar">
              <div class="candidate-avatar">You</div>
            </div>
          </div>
        </div>

        <!-- 打字中指示器 -->
        <div v-if="isTyping" class="typing-indicator">
          <div class="typing-avatar">
            <img :src="aiInterviewerAvatar" />
          </div>
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- 智能输入区 -->
      <div class="input-area" v-if="currentStep >= 3">
        <!-- 上下文提示条 -->
        <div v-if="contextHint" class="context-hint">
          <el-icon><i class="el-icon-info"></i></el-icon>
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
            :disabled="isProcessing || currentStep < 3"
            @keydown.ctrl.enter="submitMessage"
            @keydown.meta.enter="submitMessage"
          />
        </div>

        <!-- 控制按钮 -->
        <div class="input-controls">
          <div class="control-hints">
            <span>💡 Ctrl+Enter 快速发送</span>
          </div>
          <div class="control-buttons">
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

    <!-- 注意：右侧评估面板已移除
         评估数据（实时雷达图、行为模式识别、回答统计）
         将在 HR 端单独实现，不在候选人端展示 -->
  </div>

  <!-- 上传/填写信息对话框 -->
  <el-dialog
    v-model="showUploadDialog"
    title="完善候选人信息"
    width="700px"
    class="info-dialog"
  >
    <div class="dialog-content">
      <!-- 简历上传区域 -->
      <div class="upload-section">
        <h4 class="section-title">📄 上传简历（可选）</h4>
        <p class="section-desc">支持 PDF、Word 等格式，系统将自动提取关键信息并填入下方表单</p>
        
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          @change="handleResumeUpload"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          class="resume-upload"
          :disabled="isAnalyzing"
        >
          <template #default>
            <div class="upload-content">
              <el-icon v-if="!isAnalyzing" class="upload-icon"><i class="el-icon-upload"></i></el-icon>
              <el-icon v-else class="upload-icon animate-spin"><i class="el-icon-loading"></i></el-icon>
              <div class="upload-text">
                <p v-if="!isAnalyzing" class="main">拖拽文件到此或<em>点击上传</em></p>
                <p v-else class="main">正在解析文件...</p>
                <p class="secondary">最大 10MB</p>
              </div>
            </div>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              <span v-if="resumeFile && isAnalyzing" class="file-info">
                ⏳ 正在解析: {{ resumeFile.name }}
              </span>
              <span v-else-if="resumeFile" class="file-info">
                ✓ 已选择: {{ resumeFile.name }}
              </span>
              <span v-else>
                完成后自动填入姓名、邮箱、学历、技能等信息
              </span>
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 信息填写区域 -->
      <div class="form-section">
        <h4 class="section-title">👤 基本信息</h4>
        
        <div class="form-group">
          <label class="form-label">姓名 <span class="required">*</span></label>
          <el-input 
            v-model="candidateInfo.name" 
            placeholder="请输入您的姓名"
            clearable
            class="form-input"
          >
            <template #suffix v-if="candidateInfo.name">
              <span class="auto-fill-indicator">✓ 已自动填入</span>
            </template>
          </el-input>
        </div>

        <div class="form-group">
          <label class="form-label">邮箱 <span class="required">*</span></label>
          <el-input 
            v-model="candidateInfo.email" 
            placeholder="请输入您的邮箱地址"
            type="email"
            clearable
            class="form-input"
          >
            <template #suffix v-if="candidateInfo.email">
              <span class="auto-fill-indicator">✓ 已自动填入</span>
            </template>
          </el-input>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学历 <span class="required">*</span></label>
            <el-select 
              v-model="candidateInfo.education" 
              placeholder="选择学历"
              class="form-select"
            >
              <el-option label="高中" value="高中" />
              <el-option label="大专" value="大专" />
              <el-option label="本科" value="本科" />
              <el-option label="硕士" value="硕士" />
              <el-option label="博士" value="博士" />
            </el-select>
            <span v-if="candidateInfo.education" class="auto-fill-tip">✓ 已自动填入</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">技能标签
            <span class="optional-tag">选填</span>
          </label>
          <el-input 
            v-model="candidateInfo.skills" 
            placeholder="e.g., JavaScript, Vue.js, Python（用逗号分隔）"
            clearable
            class="form-input"
          >
            <template #suffix v-if="candidateInfo.skills">
              <span class="auto-fill-indicator">✓ 已自动填入</span>
            </template>
          </el-input>
          <p class="form-help-text">上传简历后系统自动提取</p>
        </div>

        <div class="form-group">
          <label class="form-label">项目经验
            <span class="optional-tag">选填</span>
          </label>
          <el-input 
            v-model="candidateInfo.projects" 
            placeholder="列举您参与过的主要项目和成就"
            type="textarea"
            :rows="3"
            clearable
            class="form-input"
          >
          </el-input>
          <p class="form-help-text">上传简历后系统自动提取</p>
        </div>
      </div>

      <!-- 信息确认提示 -->
      <div class="info-tips" v-if="candidateInfo.name || candidateInfo.email">
        <el-alert
          title="信息已捕获"
          type="success"
          :closable="false"
          description="系统将使用以上信息生成个性化的面试策略。"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="cancelUpload">取消</el-button>
      <el-button type="primary" @click="proceedFromDialog" :loading="isAnalyzing">
        {{ isAnalyzing ? '分析中...' : '确认并继续' }}
      </el-button>
    </template>
  </el-dialog>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useAssessmentStore } from '@/stores/assessment'
import UploadInfoDialog from '@/components/UploadInfoDialog.vue'

// ==================== 类型定义 ====================
interface CandidateInfo {
  name: string
  email: string
  education: string
  skills: string
  projects: string
  background?: string
}

interface Message {
  role: 'ai' | 'candidate'
  content: string
  time: string
  tags?: string[]
  responseTime?: number
  aiFeedback?: string
}

interface InterviewPlan {
  totalQuestions: number
  estimatedTime: number
  category: string
  dimensions: string[]
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

// Store
const assessmentStore = useAssessmentStore()

// ==================== 流程控制 ====================
const assessmentSteps = [
  '填写信息',
  '确认信息',
  '面试说明',
  '多轮面试',
  '生成报告'
]

const currentStep = ref(0)  // 0: 填写, 1: 确认, 2: 说明, 3+: 面试中
const isAnalyzing = ref(false)
const infoConfirmed = ref(false)

// ==================== 左侧面板控制 ====================
const leftPanelMode = ref<'svg' | 'info'>('svg')  // svg: 显示欢迎图片, info: 显示流程
// SVG 图像地址列表
const svgList = ['/个人信息.svg','/个人信息2.svg','/个人信息3.svg']
const svgImageUrl = ref<string>(svgList[Math.floor(Math.random()*svgList.length)])


// 上传对话框状态
const showUploadDialog = ref(false)

// 解析的简历数据
const parsedResumeData = ref<any>(null)

// ==================== 候选人信息 ====================
const candidateInfo = ref<CandidateInfo>({
  name: '',
  email: '',
  education: '',
  skills: '',
  projects: '',
  background: ''
})

const resumeFile = ref<File | null>(null)

// ==================== 面试信息 ====================
const interviewPlan = ref<InterviewPlan>({
  totalQuestions: 8,
  estimatedTime: 6,
  category: '技术与综合能力',
  dimensions: ['技术能力', '问题解决', '沟通能力', '团队协作']
})

const aiInterviewerAvatar = ref(generateAvatar('AI'))
const aiInterviewerTitle = ref('高级智能面试官 • 多维度评估')

// ==================== 对话管理 ====================
const messages = ref<Message[]>([])
const userInput = ref('')
const isProcessing = ref(false)
const isTyping = ref(false)
const currentPhase = ref('面试准备中...')
const contextHint = ref<string | null>(null)

// ==================== 时间追踪 ====================
const startTime = ref<number>(0)
const elapsedTime = ref(0)
const timerInterval = ref<number | null>(null)

// ==================== 评估数据 ====================
const latestScores = ref<Record<string, number>>({
  '专业能力': 0,
  '逻辑思维': 0,
  '表达能力': 0,
  '学习能力': 0,
  '团队合作': 0,
  '创新思维': 0
})

const latestSentiment = ref<{ emotion: string; confidence: number } | null>(null)
const detectedPatterns = ref<Pattern[]>([])

// ==================== 统计数据 ====================
const respondedCount = ref(0)
const avgResponseTime = ref(0)
const avgResponseLength = computed(() => {
  if (respondedCount.value === 0) return 0
  const total = messages.value
    .filter(m => m.role === 'candidate')
    .reduce((sum, m) => sum + m.content.length, 0)
  return Math.round(total / respondedCount.value)
})
const clarityScore = computed(() => {
  return Math.max(5, Math.min(10, (avgResponseLength.value / 50) * 2 + 5))
})
const relevanceScore = computed(() => {
  return Math.max(6, Math.min(10, 7 + Math.random() * 2))
})

// ==================== UI 引用 ====================
const inputRef = ref<any>(null)
const messageStream = ref<any>(null)
const radarChart = ref<any>(null)

// ==================== 计算属性 ====================
const dynamicPlaceholder = computed(() => {
  if (isProcessing.value) return '正在分析中...'
  if (currentStep.value < 3) return '请先完成前置步骤...'
  return `请详细描述你的想法和经验...`
})

const canSubmit = computed(() => {
  return !isProcessing.value && currentStep.value >= 3 && userInput.value.trim().length > 0
})

// ==================== 简历上传与解析 ====================
function toggleLeftPanel(mode: 'svg' | 'info') {
  leftPanelMode.value = mode
}

function openUploadDialog() {
  // 切换面板为 info 以显示流程叠加背景
  leftPanelMode.value = 'info'
  currentStep.value = 0
  showUploadDialog.value = true
  console.log('打开上传对话框:', showUploadDialog.value)
}

function cancelUpload() {
  showUploadDialog.value = false
  // 如果还未完成任何填写，回到 SVG 欢迎屏
  if (!candidateInfo.value.name && !candidateInfo.value.education && !candidateInfo.value.skills) {
    leftPanelMode.value = 'svg'
  }
}

function handleResumeUpload(file: any) {
  resumeFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
  
  // 立即调用后端API解析文件
  uploadAndParseResume(file.raw, file.name)
}

async function uploadAndParseResume(file: File, filename: string) {
  // 创建FormData用于文件上传
  const formData = new FormData()
  formData.append('file', file)
  formData.append('candidate_id', props.candidateId)
  
  try {
    isAnalyzing.value = true
    console.log('开始上传文件:', filename, '大小:', file.size)
    
    // 调用后端API - 注意这里使用POST，参数在URL中
    const params = new URLSearchParams()
    params.append('candidate_id', props.candidateId)
    
    const response = await fetch(
      `/assessment/immersive/upload-resume?${params.toString()}`,
      {
        method: 'POST',
        body: formData
        // 不要设置 Content-Type header，浏览器会自动设置为 multipart/form-data
      }
    )
    
    console.log('后端响应状态码:', response.status)
    
    // 先检查response的状态和content-type
    if (!response.ok) {
      // 获取错误消息
      const contentType = response.headers.get('content-type')
      let errorMsg = `服务器错误 (${response.status})`
      
      if (contentType?.includes('application/json')) {
        try {
          const errorData = await response.json()
          errorMsg = errorData.detail || errorData.message || errorMsg
        } catch (e) {
          // JSON解析失败，使用默认错误信息
        }
      } else {
        // 非JSON响应，尝试获取文本
        try {
          const errorText = await response.text()
          if (errorText) {
            errorMsg = errorText.substring(0, 100) // 只显示前100个字符
          }
        } catch (e) {
          // 无法读取响应体
        }
      }
      
      console.error('后端返回错误:', errorMsg)
      throw new Error(errorMsg)
    }
    
    // 检查响应是否包含JSON
    const contentType = response.headers.get('content-type')
    if (!contentType?.includes('application/json')) {
      const responseText = await response.text()
      console.error('后端返回非JSON响应:', responseText.substring(0, 200))
      throw new Error('后端返回无效的响应格式（非JSON）')
    }
    
    // 安全地解析JSON
    let result
    try {
      result = await response.json()
    } catch (jsonError) {
      console.error('JSON解析错误:', jsonError)
      const responseText = await response.text()
      console.error('响应内容:', responseText.substring(0, 200))
      throw new Error('响应JSON格式错误')
    }
    
    console.log('解析后的结果:', result)
    
    if (result.code === 200) {
      const data = result.data
      
      // 保存完整的解析数据供Step 1展示
      parsedResumeData.value = result.data
      
      // 自动填入表单字段
      if (data.candidate_info) {
        const info = data.candidate_info
        
        // 填入基本信息
        if (info.name && info.name !== '未提取') {
          candidateInfo.value.name = info.name
          console.log('自动填入姓名:', info.name)
        }
        if (info.email) {
          candidateInfo.value.email = info.email
          console.log('自动填入邮箱:', info.email)
        }
        if (info.education && info.education !== '') {
          candidateInfo.value.education = info.education
          console.log('自动填入学历:', info.education)
        }
        
        // 填入技能
        if (info.technical_skills?.length > 0) {
          candidateInfo.value.skills = info.technical_skills.join(', ')
          console.log('自动填入技能:', info.technical_skills)
        }
        
        // 填入工作经验
        if (info.work_experience && info.work_experience !== ''){
          candidateInfo.value.projects = info.work_experience.substring(0, 200)
          console.log('自动填入工作经验')
        }
      }
      
      ElMessage.success('文件解析成功，信息已自动填入！')
      console.log('✓ 简历解析完成')
    } else {
      console.warn('解析返回非200状态:', result)
      ElMessage.warning(result.message || '文件解析完成，请检查自动填入的信息')
    }
  } catch (error) {
    console.error('文件解析失败:', error)
    const errorMsg = error instanceof Error ? error.message : String(error)
    ElMessage.error(`文件解析失败: ${errorMsg}`)
    console.error('建议: 检查后端服务是否正运行，查看后端日志获取详细信息')
  } finally {
    isAnalyzing.value = false
  }
}

async function proceedToStep1() {
  // 验证必填信息
  if (!candidateInfo.value.name || !candidateInfo.value.email) {
    ElMessage.error('请填写姓名和邮箱')
    return
  }

  isAnalyzing.value = true
  
  try {
    // 调用后端API解析简历
    const response = await fetch(
      `/assessment/immersive/parse-resume?` + new URLSearchParams({
        candidate_id: props.candidateId,
        candidate_name: candidateInfo.value.name,
        candidate_email: candidateInfo.value.email,
        education: candidateInfo.value.education || '',
        skills: candidateInfo.value.skills || '',
        projects: candidateInfo.value.projects || ''
      }),
      {
        method: 'POST'
      }
    )
    
    const result = await response.json()
    
    if (result.code === 200) {
      // 保存解析的数据
      parsedResumeData.value = result.data
      
      // 更新候选人信息
      if (result.data.candidate_info) {
        candidateInfo.value = {
          ...candidateInfo.value,
          ...result.data.candidate_info
        }
      }
      
      // 关闭对话框，进入Step 1
      showUploadDialog.value = false
      currentStep.value = 1
      
      // 自动滚动到下面
      await scrollToBottom()
      
      ElMessage.success('信息解析成功！')
    } else {
      throw new Error(result.message || '解析失败')
    }
  } catch (error) {
    console.error('简历解析失败:', error)
    ElMessage.error('信息解析失败，请重试')
  } finally {
    isAnalyzing.value = false
  }
}

async function proceedToStep2() {
  // 从Step 1进入Step 2，显示面试准备说明
  currentStep.value = 2
  await scrollToBottom()
}

// 从弹窗点击确认进入下一步
async function proceedFromDialog() {
  showUploadDialog.value = false
  await proceedToStep1()
}

async function proceedFromDialogComponent(info: CandidateInfo) {
  // 更新用户信息
  candidateInfo.value = { ...candidateInfo.value, ...info }
  showUploadDialog.value = false
  await proceedToStep1()
}

async function startInterview() {
  currentStep.value = 3
  respondedCount.value = 0
  
  // 启动计时器
  startTime.value = Date.now()
  timerInterval.value = window.setInterval(() => {
    elapsedTime.value = Date.now() - startTime.value
  }, 1000)
  
  // 显示初始欢迎消息并生成第一个问题
  isTyping.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 添加面试开始消息
  messages.value.push({
    role: 'ai',
    content: `好的，我们开始吧！我是本次的AI面试官，将从多个维度考察你的能力。\n\n第一个问题中，我们先从了解你的背景和工作经验开始。请放松，提供尽可能详细和真实的回答。`,
    time: nowTime(),
    tags: ['面试开始', '破冰']
  })
  
  isTyping.value = false
  await scrollToBottom()
  
  // 延迟后生成第一个问题
  await new Promise(resolve => setTimeout(resolve, 1000))
  await generateNextQuestion()
}

// ==================== 对话逻辑 ====================
async function generateNextQuestion() {
  isTyping.value = true
  await new Promise(resolve => setTimeout(resolve, 1200))
  
  // 获取下一个问题
  const question = await fetchNextQuestion()
  
  messages.value.push({
    role: 'ai',
    content: question.content,
    time: nowTime(),
    tags: question.tags
  })
  
  isTyping.value = false
  currentPhase.value = question.phase || '多轮面试中'
  contextHint.value = question.context || null
  
  await scrollToBottom()
  inputRef.value?.focus()
}

async function submitMessage() {
  if (!canSubmit.value) return

  const content = userInput.value.trim()
  const responseTime = Date.now()
  
  // 添加候选人消息
  messages.value.push({
    role: 'candidate',
    content,
    time: nowTime(),
    responseTime: Math.round((responseTime - startTime.value) / 1000)
  })
  
  respondedCount.value++
  userInput.value = ''
  isProcessing.value = true
  
  await scrollToBottom()
  
  try {
    // 1. 分析回答
    const analysis = await analyzeResponse(content)
    
    // 2. 更新评分
    updateScores(analysis.scores)
    
    // 3. 更新情绪
    latestSentiment.value = analysis.sentiment
    
    // 4. 更新模式
    if (analysis.patterns) {
      updatePatterns(analysis.patterns)
    }
    
    // 5. 添加反馈
    messages.value[messages.value.length - 1].aiFeedback = analysis.feedback
    
    // 6. 检查是否完成
    if (respondedCount.value >= interviewPlan.value.totalQuestions) {
      completeInterview()
    } else {
      // 7. 生成下一个问题
      await generateNextQuestion()
    }
    
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error('系统处理失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

async function analyzeResponse(content: string) {
  try {
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
          candidate_name: candidateInfo.value.name,
          candidate_background: candidateInfo.value.background,
          current_speaker: 'ai',
          speaker_name: 'AI 面试官',
          candidate_response: content,
          previous_messages: messages.value.slice(-5),
          conversation_depth: respondedCount.value
        })
      }
    )
    
    if (!response.ok) {
      return getLocalFallbackAnalysis()
    }
    
    const data = await response.json()
    if (data.code === 200 && data.data) {
      return {
        scores: data.data.scores || {},
        sentiment: data.data.sentiment || { emotion: '专注', confidence: 75 },
        patterns: data.data.patterns || [],
        feedback: data.data.feedback || '很好的回答！'
      }
    }
  } catch (error) {
    console.warn('API 调用失败:', error)
  }
  
  return getLocalFallbackAnalysis()
}

function getLocalFallbackAnalysis() {
  return {
    scores: {
      '专业能力': 7.5 + Math.random() * 2,
      '逻辑思维': 7.0 + Math.random() * 2,
      '表达能力': 7.5 + Math.random() * 2,
      '学习能力': 7.0 + Math.random() * 1.5,
      '团队合作': 7.5 + Math.random() * 1.5,
      '创新思维': 7.0 + Math.random() * 2
    },
    sentiment: { emotion: ['自信', '谨慎', '积极'][Math.floor(Math.random() * 3)], confidence: 70 + Math.random() * 20 },
    patterns: [
      {
        id: 'p1',
        name: '结构化思维',
        description: '回答清晰有条理',
        confidence: 78,
        color: '#67c23a'
      }
    ],
    feedback: '很好的回答！逻辑清晰，表达准确。'
  }
}

async function fetchNextQuestion() {
  try {
    const params = new URLSearchParams({
      candidate_id: props.candidateId,
      role_id: 'ai',
      role_name: 'AI面试官',
      conversation_depth: respondedCount.value.toString(),
      history: JSON.stringify(messages.value.filter(m => m.role === 'ai').map(m => ({ role: 'ai', content: m.content })))
    })
    
    const response = await fetch(
      `http://127.0.0.1:8000/assessment/immersive/next-question?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        }
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      if (data.code === 200 && data.data) {
        return {
          content: data.data.content,
          tags: data.data.tags || [],
          context: data.data.context,
          phase: data.data.phase
        }
      }
    }
  } catch (error) {
    console.warn('获取问题失败:', error)
  }
  
  return getLocalFallbackQuestion()
}

function getLocalFallbackQuestion() {
  const questions = [
    '请简单介绍一下你自己和你的背景？',
    '你在过去的工作中遇到过什么挑战？如何解决的？',
    '描述一个你最自豪的项目经历',
    '如何处理与团队成员的分歧？',
    '你如何保持技术知识的更新？',
    '在压力下工作时你会怎样？',
    '你对这个岗位最感兴趣的部分是什么？',
    '你对我们公司有什么了解？为什么想加入我们？'
  ]
  
  const q = questions[respondedCount.value % questions.length]
  return {
    content: q,
    tags: ['开放式问题', '经验分享'],
    context: '请详细描述你的思考过程',
    phase: '多轮面试'
  }
}

function updateScores(newScores: Record<string, number>) {
  Object.keys(newScores).forEach(key => {
    const current = latestScores.value[key] || 0
    const target = newScores[key]
    latestScores.value[key] = Math.round((current * 0.6 + target * 0.4) * 10) / 10
  })
  
  emit('update-scores', latestScores.value)
  // 评估数据不在候选人端显示，只在 HR 端显示
}

function updatePatterns(patterns: Pattern[]) {
  detectedPatterns.value = patterns
}

function completeInterview() {
  ElMessage.success('✨ 面试完成！')
  currentStep.value = 4
  
  // 清理计时器
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  
  // 准备完成数据
  const completionData = {
    sessionId: `session_${Date.now()}`,
    messages: messages.value,
    scores: latestScores.value,
    patterns: detectedPatterns.value,
    duration: elapsedTime.value,
    respondedCount: respondedCount.value,
    candidateId: props.candidateId,
    assessmentId: props.assessmentId,
    candidateInfo: {
      name: candidateInfo.value.name,
      education: candidateInfo.value.education,
      skills: candidateInfo.value.skills,
      projects: candidateInfo.value.projects
    },
    startTime: new Date(startTime.value),
    endTime: new Date(),
    totalQuestions: interviewPlan.value.totalQuestions,
    avgResponseTime: respondedCount.value > 0 
      ? Math.round(elapsedTime.value / respondedCount.value / 1000) 
      : 0
  }
  
  // 📌 标记评估完成，通知 HomeView 刷新数据
  assessmentStore.markEvaluationComplete({
    jobId: props.initialContext?.job_id,
    assessmentId: props.assessmentId?.toString(),
    sessionId: completionData.sessionId,
    candidateId: props.candidateId
  })
  
  // Emit 完成事件（父组件可能需要关闭模态框或导航）
  emit('complete', completionData)
}

// ==================== 辅助方法 ====================
function getRoleAvatar(roleId: string): string {
  return aiInterviewerAvatar.value
}

function getSentimentType(emotion: string): string {
  const map: Record<string, string> = {
    '自信': 'success',
    '谨慎': 'warning',
    '积极': 'success',
    '思考': 'info'
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
  const color = '#409eff'
  return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='${encodeURIComponent(color)}'/%3E%3Ctext x='32' y='40' font-size='20' text-anchor='middle' fill='%23fff' font-weight='bold'%3E${initials}%3C/text%3E%3C/svg%3E`
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

// 注意：雷达图渲染已移除，评估数据在 HR 端单独实现

// ==================== 生命周期 ====================
onMounted(() => {
  // 初始化不添加消息，让 Step 0 的 UI 直接显示
})
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.immersive-dialogue {
  position: relative;
  display: grid;
  grid-template-columns: 320px 1fr; /* 仅保留左侧信息面板和中间对话区 */
  grid-template-rows: 1fr;
  gap: 16px;
  height: 100vh;
  padding: 16px;
  background: #f5f7fa;
  overflow: visible;
  z-index: 1;
  /* 注意：右侧评估面板已移除，将在 HR 端实现 */
}

/* ==================== 左侧面板 ==================== */
.left-sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  /* SVG 背景通过内联样式设置 */
  background-color: #fff;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.svg-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: rgba(0,0,0,0.3);
  color: white;
  text-align: center;
}

/* panel-overlay - 仅显示流程控制器，不显示表单 */

.el-dialog__body .upload-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.el-dialog__body .info-form {
  margin-top: 12px;
}

.panel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: rgba(255,255,255,0.85);
  padding: 16px;
  overflow-y: auto;
  z-index: 1;
}

/* SVG 容器 */
.svg-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.svg-placeholder {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.placeholder-text {
  margin-bottom: 32px;
}

.placeholder-text p {
  margin: 0 0 12px 0;
  font-size: 18px;
}

.placeholder-text .sub-text {
  font-size: 14px;
  opacity: 0.9;
}

/* SVG 图片会替换上面的placeholder-text */
.svg-container svg,
.svg-container img {
  max-width: 100%;
  max-height: 350px;
  object-fit: contain;
}

/* 流程指示器 */
.process-indicator {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  overflow-y: auto;
  flex-shrink: 0;
}

.process-indicator .step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.process-indicator .step:hover {
  background: #f5f7fa;
}

.process-indicator .step.active {
  background: #e6eefb;
  color: #409eff;
}

.process-indicator .step.completed {
  color: #67c23a;
}

.process-indicator .step-number {
  min-width: 32px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f0f0f0;
  font-weight: bold;
  font-size: 13px;
}

.process-indicator .step.active .step-number {
  background: #409eff;
  color: white;
}

.process-indicator .step.completed .step-number {
  background: #67c23a;
  color: white;
}

.process-indicator .step-title {
  font-size: 13px;
  flex: 1;
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
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.5) 100%);
}

@keyframes ambient-shift {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

/* ==================== 左侧面板 ==================== */
.left-sidebar {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow-y: auto;
}

/* 流程指示器 */
.process-indicator {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafbfc;
}

.step.active {
  background: linear-gradient(135deg, #e3f2fd 0%, #e8f4f8 100%);
  border-left: 3px solid #409eff;
}

.step.completed {
  opacity: 0.7;
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
}

.step:hover {
  background: #f0f2f5;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step.completed .step-number {
  background: #67c23a;
}

.step-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.step.active .step-title {
  color: #2c3e50;
  font-weight: 600;
}

/* 信息面板 */
.info-panel {
  flex: 1;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.panel-title .close-btn {
  margin-left: auto;
  margin-right: auto;
  color: #909399;
}

.panel-title .close-btn:hover {
  color: #f56c6c;
}

.step-content {
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.upload-area {
  margin-bottom: 16px;
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 12px 0;
}

.form-item {
  font-size: 13px;
}

.next-btn,
.start-btn {
  width: 100%;
  margin-top: 12px;
}

.start-btn {
  height: 40px;
  font-size: 15px;
}

.info-display {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.confirm-checkbox {
  margin: 12px 0;
  font-size: 12px;
}

.process-preview {
  margin-bottom: 16px;
}

.process-preview h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #2c3e50;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
}

.plan-details h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.dimension-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.interview-progress {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-stats {
  padding: 12px;
  background: #fafbfc;
  border-radius: 6px;
}

.stat {
  margin-bottom: 8px;
}

.stat:last-child {
  margin-bottom: 0;
}

.stat-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.candidate-summary {
  padding: 12px;
  background: #fafbfc;
  border-radius: 6px;
}

.candidate-summary h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}

.summary-item .key {
  color: #909399;
}

.summary-item .value {
  color: #2c3e50;
  font-weight: 500;
}

/* ==================== 对话框操作按钮 ==================== */
.conversation-starter .action-btn {
  margin-top: 16px;
  padding: 8px 24px;
  font-size: 14px;
  font-weight: 600;
}

.conversation-starter .action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.upload-action-btn {
  margin-top: 24px;
  padding: 12px 40px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  min-height: 44px !important;
}

.upload-action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.start-interview-btn {
  margin-top: 24px;
  padding: 12px 40px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  min-height: 44px !important;
}

.start-interview-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* ==================== 解析信息展示 ==================== */
.parsed-info-display {
  margin: 20px 0;
  text-align: left;
}

.info-card {
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}

.info-header {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.info-row .label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
}

.info-row .value {
  color: #2c3e50;
  flex: 1;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skills-list :deep(.el-tag) {
  border-radius: 4px;
}

.dimensions-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.dimension-item {
  padding: 8px 12px;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  border: 1px solid #ebeef5;
}

/* ==================== 面试流程说明 ==================== */
.interview-briefing {
  padding: 20px;
}

.briefing-content {
  text-align: left;
  margin: 20px 0;
}

.interview-plan {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.plan-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.plan-icon {
  font-size: 24px;
  min-width: 40px;
  text-align: center;
  line-height: 1;
}

.plan-detail {
  flex: 1;
}

.plan-title {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.plan-item p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.interview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

/* ==================== 信息对话框样式 ==================== */
.info-dialog {
  --el-dialog-border-radius: 12px;
}

.info-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px 12px 0 0;
}

.info-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}

.info-dialog :deep(.el-dialog__close) {
  color: #fff;
}

.dialog-content {
  padding: 24px 0;
}

.upload-section,
.form-section {
  margin-bottom: 24px;
  padding: 0 24px;
}

.section-title {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-desc {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #909399;
}

/* 简历上传样式 */
.resume-upload {
  width: 100%;
}

.resume-upload :deep(.el-upload-dragger) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  transition: all 0.3s ease;
  padding: 40px 20px;
}

.resume-upload :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.resume-upload :deep(.el-upload-dragger.is-dragover) {
  border-color: #409eff;
  background-color: #e6eefb;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
}

.upload-icon.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.upload-text {
  text-align: center;
}

.upload-text .main {
  margin: 0;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.upload-text .main em {
  color: #409eff;
  font-style: normal;
  font-weight: 600;
}

.upload-text .secondary {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.resume-upload :deep(.el-upload__tip) {
  margin-top: 12px;
  font-size: 12px;
}

.file-info {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #f0f9ff;
  border-radius: 4px;
  color: #67c23a;
  font-weight: 500;
}

/* 表单样式 */
.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-row .form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.required {
  color: #f56c6c;
}

.optional-tag {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  margin-left: 4px;
}

.form-input,
.form-select {
  width: 100%;
  font-size: 13px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.form-select {
  --el-border-radius-base: 6px;
}

.auto-fill-indicator {
  font-size: 12px;
  color: #67c23a;
  font-weight: 600;
  margin-left: 4px;
}

.auto-fill-tip {
  display: block;
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
  font-weight: 600;
}

.form-help-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

/* 信息提示 */
.info-tips {
  margin: 0 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.info-tips :deep(.el-alert) {
  border-radius: 8px;
  --el-alert-bg-color: #f0f9ff;
  --el-alert-border-color: #b3e5fc;
  --el-alert-title-color: #0288d1;
  --el-alert-description-color: #01579b;
}

/* 确保 el-dialog 显示在最上方 */
:deep(.el-dialog) {
  z-index: 3000 !important;
}

:deep(.el-overlay) {
  z-index: 2999 !important;
}

:deep(.el-overlay__wrapper) {
  z-index: 2999 !important;
}

/* ==================== 对话容器 ==================== */
.dialogue-container {
  position: relative;
  z-index: 1;
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.ai-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
}

.ai-info h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.ai-info p {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

.session-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
}

.sentiment-monitor {
  margin-top: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.sentiment-indicator,
.confidence-bar {
  display: flex;
  align-items: center;
  gap: 8px;
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
  min-height: 200px;
}

.starter-content {
  text-align: center;
  max-width: 360px;
}

.greeting-avatar {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 12px;
  overflow: hidden;
}

.greeting-avatar img {
  width: 100%;
  height: 100%;
}

.starter-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
  display: block;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.starter-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #2c3e50;
}

.starter-content p {
  margin: 4px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

.starter-tip {
  color: #909399;
  font-size: 12px;
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

.ai-message {
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
  font-size: 12px;
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
  font-size: 13px;
}

.candidate-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: flex-end;
  flex-direction: row-reverse;
}

.candidate-message .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.candidate-message .message-body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
}

.message-tags {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.ai-feedback {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ==================== 打字指示器 ==================== */
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
  font-size: 12px;
  color: #606266;
}

.input-wrapper {
  margin-bottom: 12px;
}

.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-hints {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #909399;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

/* ==================== 右侧洞察面板 ==================== */
.insights-sidebar {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.insight-card {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 13px;
}

.radar-card {
  flex: 0 0 auto;
}

.radar-chart {
  width: 100%;
  height: 200px;
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
  font-size: 11px;
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
  gap: 10px;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}

.pattern-item {
  display: flex;
  gap: 10px;
  padding: 10px;
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
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 2px;
}

.pattern-desc {
  font-size: 11px;
  color: #606266;
  line-height: 1.3;
}

.pattern-confidence {
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
}

.stats-card {
  flex: 0 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat-item {
  padding: 10px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  text-align: center;
}

.stat-item .stat-label {
  font-size: 10px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-item .stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #409eff;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .immersive-dialogue {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 100vh;
  }
  
  .left-sidebar {
    order: 1;
    max-height: 40vh;
    overflow-y: auto;
  }
  
  .dialogue-container {
    order: 2;
    min-height: 60vh;
  }
  
  .message-content {
    max-width: 90%;
  }
}

@media (max-width: 768px) {
  .immersive-dialogue {
    padding: 8px;
    gap: 8px;
  }
  
  .left-sidebar {
    max-height: 40vh;
  }
  
  .dialogue-container {
    min-height: 50vh;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .session-meta {
    font-size: 11px;
    flex-wrap: wrap;
  }
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
