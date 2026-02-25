<template>
  <div class="assessment-container">
    <!-- 顶部导航：保留原有样式，但简化流程显示 -->
    <div class="header-nav">
      <div class="logo-area">
        <h2>候选人评估系统</h2>
        <el-tag type="info" size="small">沉浸式对话模式</el-tag>
      </div>
      
      <div class="progress-indicator">
        <div class="progress-item" :class="{ active: assessmentStatus === 'in_progress' }">
          <el-icon><i class="el-icon-chat-dot-round"></i></el-icon>
          <span>对话评估中</span>
        </div>
        <div class="progress-item" :class="{ active: assessmentStatus === 'completed' }">
          <el-icon><i class="el-icon-document"></i></el-icon>
          <span>生成报告</span>
        </div>
      </div>
    </div>

    <!-- 主内容区：根据状态显示不同组件 -->
    <div class="main-content">
      <!-- 初始化阶段：显示候选人基本信息确认 -->
      <div v-if="assessmentStatus === 'init'" class="init-stage">
        <el-card class="welcome-card">
          <div class="welcome-header">
            <el-icon class="welcome-icon"><i class="el-icon-user"></i></el-icon>
            <h3>欢迎，{{ candidate.name || '候选人' }}！</h3>
          </div>
          
          <div class="info-preview">
            <p>我们将通过一场自然的对话来了解您。评估过程将包括：</p>
            <ul>
              <li>✓ 与 HR 经理的背景交流</li>
              <li>✓ 与技术总监的专业探讨</li>
              <li>✓ 与产品经理的思维碰撞</li>
              <li>✓ 与 CTO 的战略对话</li>
            </ul>
            <p class="estimate">预计用时：20-30 分钟</p>
          </div>

          <div class="candidate-info-check">
            <h4>请确认您的基本信息：</h4>
            <el-form :model="candidate" label-width="100px" size="default">
              <el-form-item label="姓名">
                <el-input v-model="candidate.name" placeholder="请输入姓名" />
              </el-form-item>
              <el-form-item label="期望岗位">
                <el-select v-model="candidate.desired_job" placeholder="选择岗位">
                  <el-option label="前端工程师" value="frontend" />
                  <el-option label="后端工程师" value="backend" />
                  <el-option label="产品经理" value="product" />
                  <el-option label="UI设计师" value="ui_designer" />
                </el-select>
              </el-form-item>
              <el-form-item label="工作经验">
                <el-input-number v-model="candidate.experience_years" :min="0" :max="30" />
                <span style="margin-left: 8px;">年</span>
              </el-form-item>
            </el-form>
          </div>

          <div class="action-buttons">
            <el-button @click="handleCancel">返回</el-button>
            <el-button type="primary" @click="startAssessment" :loading="isInitializing">
              开始对话评估
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 对话评估阶段：核心组件 -->
      <ImmersiveRoleDialogue
        v-else-if="assessmentStatus === 'in_progress'"
        :candidate-id="candidateId"
        :target-position="candidate.desired_job"
        :initial-context="candidate"
        @complete="handleDialogueComplete"
        @update-scores="handleScoresUpdate"
        @pause="handlePause"
      />

      <!-- 报告生成阶段：展示评估结果 -->
      <div v-else-if="assessmentStatus === 'completed'" class="report-stage">
        <ReportGenerate
          :candidate="candidate"
          :dialogue-data="dialogueData"
          :personality-scores="personalityScores"
          @finish="handleFinish"
        />
      </div>

      <!-- 暂停状态：显示暂停提示 -->
      <div v-else-if="assessmentStatus === 'paused'" class="paused-stage">
        <el-card class="paused-card">
          <div class="paused-content">
            <el-icon class="paused-icon"><i class="el-icon-video-pause"></i></el-icon>
            <h3>对话已暂停</h3>
            <p>您可以稍作休息，准备好后继续对话</p>
            <div class="paused-stats">
              <div class="stat-item">
                <span class="label">已完成轮次:</span>
                <span class="value">{{ dialogueData.totalRounds || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="label">已用时间:</span>
                <span class="value">{{ formatDuration(dialogueData.duration || 0) }}</span>
              </div>
            </div>
            <div class="paused-actions">
              <el-button @click="resumeAssessment" type="primary">继续对话</el-button>
              <el-button @click="confirmExit">退出评估</el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 退出确认对话框 -->
    <el-dialog
      v-model="showExitDialog"
      title="确认退出"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>您确定要退出评估吗？当前进度将会丢失。</p>
      <template #footer>
        <el-button @click="showExitDialog = false">取消</el-button>
        <el-button type="danger" @click="handleExit">确认退出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ImmersiveRoleDialogue from './ImmersiveRoleDialogue.vue'
// import ReportGenerate from '.assessment/ReportGenerate.vue'

const router = useRouter()
const route = useRoute()

// ==================== 状态管理 ====================
type AssessmentStatus = 'init' | 'in_progress' | 'paused' | 'completed'

const assessmentStatus = ref<AssessmentStatus>('init')
const candidateId = computed(() => String(route.params.id || 'demo-001'))

// 候选人信息
const candidate = ref({
  id: candidateId.value,
  name: '',
  desired_job: '',
  experience_years: 0,
  education: '',
  major: '',
  skills: [] as string[]
})

// 对话数据
const dialogueData = ref<any>({
  sessionId: '',
  messages: [],
  totalRounds: 0,
  duration: 0,
  conversationDepth: 0
})

// 评分数据
const personalityScores = ref<Record<string, number>>({})

// UI 状态
const isInitializing = ref(false)
const showExitDialog = ref(false)

// ==================== 生命周期 ====================
onMounted(() => {
  // 从路由或本地存储加载候选人基本信息
  loadCandidateInfo()
})

// ==================== 核心方法 ====================

/**
 * 加载候选人信息
 */
function loadCandidateInfo() {
  // 尝试从 localStorage 加载
  const saved = localStorage.getItem(`candidate_${candidateId.value}`)
  
  if (saved) {
    try {
      candidate.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载候选人信息失败:', e)
    }
  }
  
  // 如果是 demo 模式，填充演示数据
  if (route.params.id === 'demo') {
    candidate.value = {
      id: 'demo-001',
      name: '演示用户',
      desired_job: 'frontend',
      experience_years: 3,
      education: '本科',
      major: '计算机科学',
      skills: ['Vue', 'React', 'TypeScript']
    }
  }
}

/**
 * 开始评估
 */
async function startAssessment() {
  // 验证必填信息
  if (!candidate.value.name?.trim()) {
    ElMessage.warning('请输入姓名')
    return
  }
  
  if (!candidate.value.desired_job) {
    ElMessage.warning('请选择期望岗位')
    return
  }

  isInitializing.value = true

  try {
    // 保存候选人信息到本地存储
    localStorage.setItem(
      `candidate_${candidateId.value}`,
      JSON.stringify(candidate.value)
    )

    // 模拟初始化延迟（实际项目中这里可以调用后端 API）
    await new Promise(resolve => setTimeout(resolve, 800))

    // 切换到对话评估状态
    assessmentStatus.value = 'in_progress'
    
    ElMessage.success('评估已开始，祝您顺利！')
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error('初始化失败，请重试')
  } finally {
    isInitializing.value = false
  }
}

/**
 * 对话完成回调
 */
function handleDialogueComplete(data: any) {
  console.log('对话评估完成:', data)
  
  // 保存对话数据
  dialogueData.value = {
    sessionId: data.sessionId || '',
    messages: data.messages || [],
    totalRounds: data.messages?.filter((m: any) => m.role === 'candidate').length || 0,
    duration: data.duration || 0,
    conversationDepth: data.conversationDepth || 0,
    patterns: data.patterns || []
  }

  // 保存评分数据
  personalityScores.value = data.scores || {}

  // 切换到报告生成阶段
  assessmentStatus.value = 'completed'
  
  ElMessage.success('对话评估已完成！正在生成评估报告...')
}

/**
 * 实时评分更新
 */
function handleScoresUpdate(scores: Record<string, number>) {
  personalityScores.value = { ...scores }
}

/**
 * 暂停处理
 */
function handlePause() {
  assessmentStatus.value = 'paused'
}

/**
 * 恢复评估
 */
function resumeAssessment() {
  assessmentStatus.value = 'in_progress'
  ElMessage.info('对话已继续')
}

/**
 * 确认退出
 */
function confirmExit() {
  showExitDialog.value = true
}

/**
 * 退出评估
 */
function handleExit() {
  showExitDialog.value = false
  
  // 清理数据
  localStorage.removeItem(`candidate_${candidateId.value}`)
  
  // 返回首页或候选人列表
  router.push('/candidates')
  
  ElMessage.info('已退出评估')
}

/**
 * 取消（从初始化页面返回）
 */
function handleCancel() {
  router.push('/candidates')
}

/**
 * 完成整个评估流程
 */
function handleFinish() {
  ElMessageBox.confirm(
    '评估已全部完成，是否返回候选人列表？',
    '完成',
    {
      confirmButtonText: '返回列表',
      cancelButtonText: '留在此页',
      type: 'success'
    }
  ).then(() => {
    router.push('/candidates')
  }).catch(() => {
    // 用户选择留在当前页面
  })
}

/**
 * 格式化时长
 */
function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes} 分 ${remainingSeconds} 秒`
}
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.assessment-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
}

/* ==================== 顶部导航 ==================== */
.header-nav {
  background: #fff;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-area h2 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
  font-weight: 600;
}

.progress-indicator {
  display: flex;
  gap: 24px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: #909399;
  transition: all 0.3s ease;
}

.progress-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* ==================== 主内容区 ==================== */
.main-content {
  flex: 1;
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* ==================== 初始化阶段 ==================== */
.init-stage {
  width: 100%;
  max-width: 800px;
}

.welcome-card {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.welcome-header {
  text-align: center;
  margin-bottom: 24px;
}

.welcome-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 12px;
}

.welcome-header h3 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.info-preview {
  background: #f0f9ff;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  margin-bottom: 24px;
}

.info-preview p {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.6;
}

.info-preview ul {
  margin: 12px 0;
  padding-left: 20px;
}

.info-preview li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.5;
}

.estimate {
  font-weight: 600;
  color: #409eff;
  margin-top: 12px;
}

.candidate-info-check {
  margin-bottom: 24px;
}

.candidate-info-check h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #2c3e50;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

/* ==================== 暂停阶段 ==================== */
.paused-stage {
  width: 100%;
  max-width: 600px;
}

.paused-card {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.paused-content {
  text-align: center;
  padding: 20px;
}

.paused-icon {
  font-size: 64px;
  color: #e6a23c;
  margin-bottom: 16px;
}

.paused-content h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #2c3e50;
}

.paused-content > p {
  margin: 0 0 24px 0;
  color: #606266;
}

.paused-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item .label {
  font-size: 12px;
  color: #909399;
}

.stat-item .value {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.paused-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* ==================== 报告阶段 ==================== */
.report-stage {
  width: 100%;
  max-width: 1200px;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .header-nav {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .progress-indicator {
    width: 100%;
    justify-content: space-around;
  }

  .main-content {
    padding: 16px;
  }

  .init-stage,
  .paused-stage {
    max-width: 100%;
  }

  .paused-stats {
    grid-template-columns: 1fr;
  }
}
</style>
