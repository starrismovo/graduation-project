<template>
  <div class="assessment-page">
    <el-container>
      <el-header class="assessment-header">
        <el-steps :active="activeStep" finish-status="success" align-center>
          <el-step title="基本信息"></el-step>
          <el-step title="情境问答"></el-step>
          <el-step title="认知任务"></el-step>
          <el-step title="特质量表"></el-step>
          <el-step title="生成报告"></el-step>
        </el-steps>
      </el-header>

      <el-main class="assessment-main">
        <div class="left-col">
          <!-- 动态模块说明：根据 activeStep 切换 -->
          <el-card class="task-card">
            <div class="task-header">
              <h3 v-if="activeStep === 1">当前模块：基础信息</h3>
              <h3 v-else-if="activeStep === 2">当前模块：情境问答</h3>
              <h3 v-else-if="activeStep === 3">当前模块：认知任务</h3>
              <h3 v-else-if="activeStep === 4">当前模块：特质量表</h3>
              <h3 v-else>当前模块：报告生成</h3>
            </div>

            <div class="task-body">
              <!-- 基础信息展示 -->
              <div v-if="activeStep === 1">
                <p class="task-desc">请填写并确认自己的基本信息。</p>
                <ul class="task-meta">
                  <li><strong>姓名：</strong>{{ candidate.name || candidate.id }}</li>
                  <li><strong>年龄：</strong>{{ candidate.age ?? '-' }}</li>
                  <li><strong>学历：</strong>{{ candidate.education ?? '-' }}</li>
                  <li><strong>专业：</strong>{{ candidate.major ?? '-' }}</li>
                  <li><strong>期望岗位：</strong>{{ candidate.desired_job ?? '-' }}</li>
                  <li><strong>工作经验：</strong>{{ candidate.experience_years ?? '-' }} 年</li>
                  <li><strong>技能：</strong>{{ (candidate.skills || []).join('、') || '-' }}</li>
                </ul>
              </div>

              <!-- 情境问答说明 -->
              <div v-else-if="activeStep === 2">
                <p v-if="currentScenario" class="task-desc">{{ currentScenario.title }}</p>
                <p v-else class="task-desc">加载情景中...</p>
                
                <div v-if="currentScenario" class="task-meta">
                  <p class="scenario-desc">{{ currentScenario.description }}</p>
                  <ul>
                    <li><strong>目标特质：</strong>{{ currentScenario.target_traits.join(' / ') }}</li>
                    <li><strong>预计时间：</strong>约 2-5 分钟</li>
                    <li><strong>最多轮次：</strong>{{ currentScenario.max_rounds }} 轮</li>
                  </ul>
                </div>
              </div>

              <!-- 认知任务说明 -->
              <div v-else-if="activeStep === 3">
                <p class="task-desc">🧠 认知能力评估</p>
                <div class="task-meta">
                  <p><strong>任务阶段：</strong>从行为认知过渡到认知能力层面</p>
                  <p v-if="latestScores" class="recommendation">
                    <strong>推荐：</strong>根据情境表现，为你推荐适合的认知任务
                  </p>
                  <p><strong>可选任务：</strong></p>
                  <ul style="margin: 0; padding-left: 20px; font-size: 12px;">
                    <li>🔢 N-Back 记忆任务 - 工作记忆和注意力</li>
                    <li>⚡ 反应时任务 - 信息处理速度</li>
                    <li>🧩 逻辑推理 - 推理和问题解决能力</li>
                  </ul>
                </div>
              </div>

              <!-- 特质量表说明 -->
              <div v-else-if="activeStep === 4">
                <p class="task-desc">特质量表：填写若干条目以量化五大人格维度（静态演示）。</p>
                <ul class="task-meta">
                  <li><strong>本轮目标：</strong>采集量表项以生成画像</li>
                  <li><strong>预计时间：</strong>约 4-8 分钟</li>
                </ul>
                <el-divider />
                <div class="task-actions">
                  <el-button type="primary" @click="handleNext">开始填写量表</el-button>
                </div>
              </div>

              <!-- 报告生成说明 -->
              <div v-else>
                <p class="task-desc">报告生成：汇总前四步数据，生成可视化报告（雷达图、匹配度等）。</p>
                <ul class="task-meta">
                  <li><strong>操作：</strong>点击生成报告以预览</li>
                </ul>
                <el-divider />
                <div class="task-actions">
                  <el-button type="primary" @click="ElMessage.info('生成报告（静态演示）')">生成报告</el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 已采集数据卡 + AI 分析感知面板 -->
          <el-card class="collected-card" v-if="activeStep === 2">
            <div class="collected-header">
              <h4>已采集回答</h4>
              <el-tag v-if="answers.length > 0" type="success" size="small">{{ answers.length }}/{{ maxRounds }}</el-tag>
            </div>
            
            <!-- 时间线显示回答历史 -->
            <div v-if="answers.length === 0" class="empty">
              <el-icon class="empty-icon"><i class="el-icon-circle-plus-outline"></i></el-icon>
              <p>尚未输入回答</p>
            </div>
            <el-timeline v-else class="answers-timeline">
              <el-timeline-item v-for="(a, idx) in answers" :key="idx" :timestamp="a.time" placement="top">
                <div class="answer-item">
                  <div class="answer-text">{{ a.text }}</div>
                  <div class="answer-meta">
                    <span>⏱ {{ a.latency }}s</span>
                    <el-tag size="mini" type="info">{{ a.emotion }}</el-tag>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>

          <!-- AI 模型感知分析面板：实时显示 LLM 反馈 -->
          <el-card class="insights-card" v-if="activeStep === 2 && answers.length > 0">
            <div class="insights-header">
              <h4>🤖 AI 分析面板</h4>
              <el-tag type="success" v-if="latestScores" effect="light">已分析</el-tag>
              <el-tag type="info" v-else effect="light">分析中...</el-tag>
            </div>

            <!-- 特质评分雷达数据 -->
            <div v-if="latestScores" class="scores-display">
              <div class="traits-grid">
                <div v-for="(score, trait) in latestScores" :key="trait" class="trait-card">
                  <div class="trait-name">{{ trait }}</div>
                  <div class="trait-score">
                    <span class="score-value">{{ score }}</span>
                    <span class="score-max">/10</span>
                  </div>
                  <el-progress 
                    :percentage="score * 10" 
                    :color="getScoreColor(score)"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>

            <!-- 分析理由 -->
            <div v-if="latestReasonings" class="reasoning-section">
              <el-divider />
              <h5>分析理由</h5>
              <div class="reasoning-list">
                <div v-for="(reason, trait) in latestReasonings" :key="trait" class="reasoning-item">
                  <div class="reasoning-trait">{{ trait }}</div>
                  <div class="reasoning-text">{{ reason }}</div>
                </div>
              </div>
            </div>

            <!-- 动态反馈 -->
            <div v-if="answers.length > 0" class="feedback-section">
              <el-divider />
              <h5>实时反馈</h5>
              <div class="feedback-text">
                <p v-if="answers.length === 1">✓ 已收集第 1 轮回答，AI 正在分析...</p>
                <p v-else-if="answers.length === 2">✓ 已收集第 2 轮回答，{{latestScores ? '分析完成' : 'AI 正在分析...'}}</p>
                <p v-else>✓ 已收集第 3 轮回答，{{latestScores ? '分析完成，可提交完成' : 'AI 正在分析...'}}</p>
              </div>
            </div>
          </el-card>
        </div>

        <div class="right-col">
          <!-- Step 1: 基础信息 -->
          <BasicInfo v-if="activeStep === 1" :candidate-id="candidateId" :candidate="candidate" @save="handleSave" @next="handleNext" />

          <!-- Step 2: 情境问答 -->
          <SituationalQA 
            v-else-if="activeStep === 2"
            :candidate-id="candidateId"
            @update-scenario="handleScenarioUpdate"
            @update-answers="handleAnswersUpdate"
            @next="handleNext"
          />

          <!-- Step 3: 认知任务 -->
          <CognitiveTask v-else-if="activeStep === 3" :hr-scores="latestScores" @next="handleNext" />

          <!-- Step 4: 特质量表 -->
          <PersonalityScale 
            v-else-if="activeStep === 4"
            @save="handleScoresSave"
            @next="handleNext"
          />

          <!-- Step 5: 报告生成 -->
          <ReportGenerate 
            v-else-if="activeStep === 5"
            :candidate="candidate"
            :personalityScores="personalityScores"
            @finish="handleFinish"
          />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import BasicInfo from './assessment/BasicInfo.vue'
import SituationalQA from './assessment/components/SituationalQA.vue'
import CognitiveTask from './assessment/components/CognitiveTask.vue'
import PersonalityScale from './assessment/components/PersonalityScale.vue'
import ReportGenerate from './assessment/components/ReportGenerate.vue'

const router = useRouter()
const route = useRoute()
const activeStep = ref(1) // 从基础信息开始

// 候选人 ID（唯一标识）
const candidateId = computed(() => String(route.params.id || 'demo-001'))

// 候选人画像（由 BasicInfo 编辑并保存）
const candidate = ref<Record<string, any>>({})

// 当前情景信息（由 SituationalQA 传来）
const currentScenario = ref<Record<string, any> | null>(null)

// 评估数据
const answers = ref<Array<{ text: string; time: string; latency: number; emotion: string }>>([])
const personalityScores = ref<Record<string, number>>({})

// AI 分析数据
const latestScores = ref<Record<string, number> | null>(null)
const latestReasonings = ref<Record<string, string> | null>(null)
const maxRounds = ref(3)

// 根据路由 param 填充 demo 数据
if (route.params.id === 'demo' || !route.params.id) {
  candidate.value = {
    id: 'demo-001',
    name: '演示用户',
    age: 28,
    education: '本科',
    major: '计算机科学',
    desired_job: '前端工程师',
    experience_years: 3,
    skills: ['JavaScript', 'Vue']
  }
} else {
  candidate.value = { id: candidateId.value }
}

function handleSave(updated: Record<string, any>) {
  candidate.value = { ...candidate.value, ...updated }
}

function handleNext() {
  if (activeStep.value < 5) {
    activeStep.value += 1
  } else {
    ElMessage.success('评估已完成！')
  }
}

function handleAnswersUpdate(newAnswers: Array<any>) {
  answers.value = newAnswers
  
  // 从最新的回答中提取 AI 分析数据
  if (newAnswers.length > 0) {
    const latestAnswer = newAnswers[newAnswers.length - 1]
    
    // 如果包含分析数据，则更新
    if (latestAnswer.scores) {
      latestScores.value = latestAnswer.scores
    }
    if (latestAnswer.reasoning) {
      latestReasonings.value = latestAnswer.reasoning
    }
  }
}

// 根据分数获取颜色
function getScoreColor(score: number): string {
  if (score >= 8) return '#67c23a'   // 绿色：优秀
  if (score >= 6) return '#409eff'   // 蓝色：良好
  if (score >= 4) return '#e6a23c'   // 橙色：一般
  return '#f56c6c'                   // 红色：需改进
}

// 接收情景信息（动态更新左侧情景描述）
function handleScenarioUpdate(scenario: Record<string, any>) {
  currentScenario.value = scenario
}

function handleScoresSave(scores: Record<string, number>) {
  personalityScores.value = scores
}

function handleFinish() {
  ElMessage.success('评估全流程完成，感谢参与！')
  // 可选：重定向到报告页面或首页
  // router.push('/home')
}

function startModule() {
  ElMessage.info('开始本轮情境问答（静态前端演示）')
}
</script>

<style scoped>
.assessment-header { background: #fff; padding: 18px; }
.assessment-main { 
  display: flex; 
  gap: 20px; 
  padding: 24px;
}
.left-col { 
  width: 420px; 
  display: flex; 
  flex-direction: column; 
  gap: 16px;
}
.right-col { 
  flex: 1;
}
.task-card .task-header h3 { margin: 0; }
.task-desc { 
  color: #333; 
  margin: 8px 0;
  font-weight: 600;
  font-size: 15px;
}
.task-meta { 
  list-style: none; 
  padding: 0; 
  margin: 8px 0; 
  color: #666;
}
.task-meta li { margin-bottom: 8px; }
.scenario-desc {
  background: #f0f9ff;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #409eff;
  margin: 8px 0;
  font-size: 13px;
  line-height: 1.6;
  color: #333;
}
.task-actions { 
  display: flex; 
  gap: 10px; 
  margin-top: 10px;
}

/* 改进的已采集数据卡 */
.collected-card { 
  padding: 12px;
}
.collected-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 12px; 
}
.collected-header h4 { margin: 0; font-size: 14px; }
.answers-timeline { padding: 0; }
.collected-card .empty { 
  color: #999; 
  text-align: center; 
  padding: 20px 0;
}
.empty-icon { font-size: 24px; color: #ccc; }
.answer-item { padding: 8px 0; }
.answer-text { color: #333; font-size: 13px; line-height: 1.5; }
.answer-meta { 
  display: flex; 
  gap: 8px; 
  margin-top: 4px; 
  font-size: 12px;
  color: #999;
}

/* AI 分析感知面板 */
.insights-card { 
  padding: 12px; 
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border: 1px solid #667eea30;
}
.insights-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #667eea30;
}
.insights-header h4 { margin: 0; font-size: 14px; color: #333; }

/* 特质评分网格 */
.scores-display { padding: 8px 0; }
.traits-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 12px;
}
.trait-card { 
  padding: 10px; 
  background: #fff; 
  border-radius: 6px;
  border: 1px solid #eee;
  transition: all 0.3s ease;
}
.trait-card:hover { 
  border-color: #667eea; 
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}
.trait-name { 
  font-size: 12px; 
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}
.trait-score { 
  display: flex; 
  align-items: baseline; 
  gap: 2px;
  margin-bottom: 6px;
}
.score-value { 
  font-size: 16px; 
  font-weight: 700;
  color: #667eea;
}
.score-max { 
  font-size: 11px; 
  color: #999;
}

/* 分析理由部分 */
.reasoning-section { padding: 8px 0; }
.reasoning-section h5 { 
  margin: 8px 0; 
  font-size: 12px; 
  font-weight: 600;
  color: #333;
}
.reasoning-list { 
  display: flex; 
  flex-direction: column; 
  gap: 8px;
}
.reasoning-item { 
  padding: 8px; 
  background: #fff; 
  border-radius: 4px;
  border-left: 3px solid #667eea;
}
.reasoning-trait { 
  font-size: 11px; 
  font-weight: 600;
  color: #667eea;
  margin-bottom: 2px;
}
.reasoning-text { 
  font-size: 12px; 
  color: #666;
  line-height: 1.4;
}

/* 动态反馈部分 */
.feedback-section { padding: 8px 0; }
.feedback-section h5 { 
  margin: 8px 0; 
  font-size: 12px; 
  font-weight: 600;
  color: #333;
}
.feedback-text { 
  padding: 8px; 
  background: #f0f9ff; 
  border-radius: 4px;
  border-left: 3px solid #409eff;
}
.feedback-text p { 
  margin: 0; 
  font-size: 12px; 
  color: #333;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .assessment-main { 
    flex-direction: column;
  }
  .left-col { 
    width: 100%;
  }
  .chat-card { height: 400px; }
}
</style>
