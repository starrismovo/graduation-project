<template>
  <div class="report-generate">
    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <!-- 报告内容 -->
    <div v-else>
      <el-tabs>
        <el-tab-pane label="综合报告">
          <div class="report-header">
            <h3>{{ candidate?.name || '候选人' }} - AI 心理特质评估报告</h3>
            <div class="meta">
              <span>🎯 岗位：{{ candidate?.desired_job || '-' }}</span>
              <span>📅 评估时间：{{ reportTime }}</span>
              <span v-if="matchScore" class="match-badge">匹配度：{{ Math.round(matchScore) }}%</span>
            </div>
          </div>

          <!-- 五大人格维度评估 -->
          <div class="report-section">
            <h4>🧠 五大人格维度评估</h4>
            <div class="big-five-container">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="metric-card">
                    <div class="metric-icon">🗣️</div>
                    <div class="metric-name">外向性 (Extraversion)</div>
                    <div class="metric-score">{{ bigFiveScores.extraversion.toFixed(1) }}/10</div>
                    <el-progress 
                      :percentage="bigFiveScores.extraversion * 10" 
                      color="#409eff"
                      :format="formatPercent"
                    ></el-progress>
                    <div class="metric-description">社交和人际互动倾向</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="metric-card">
                    <div class="metric-icon">📋</div>
                    <div class="metric-name">尽责性 (Conscientiousness)</div>
                    <div class="metric-score">{{ bigFiveScores.conscientiousness.toFixed(1) }}/10</div>
                    <el-progress 
                      :percentage="bigFiveScores.conscientiousness * 10" 
                      color="#67c23a"
                      :format="formatPercent"
                    ></el-progress>
                    <div class="metric-description">组织性和责任意识</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="metric-card">
                    <div class="metric-icon">💡</div>
                    <div class="metric-name">开放性 (Openness)</div>
                    <div class="metric-score">{{ bigFiveScores.openness.toFixed(1) }}/10</div>
                    <el-progress 
                      :percentage="bigFiveScores.openness * 10" 
                      color="#e6a23c"
                      :format="formatPercent"
                    ></el-progress>
                    <div class="metric-description">创新思维和学习能力</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="metric-card">
                    <div class="metric-icon">🤝</div>
                    <div class="metric-name">宜人性 (Agreeableness)</div>
                    <div class="metric-score">{{ bigFiveScores.agreeableness.toFixed(1) }}/10</div>
                    <el-progress 
                      :percentage="bigFiveScores.agreeableness * 10" 
                      color="#f56c6c"
                      :format="formatPercent"
                    ></el-progress>
                    <div class="metric-description">合作意识和共情能力</div>
                  </div>
                </el-col>
                <el-col :span="24">
                  <div class="metric-card">
                    <div class="metric-icon">😌</div>
                    <div class="metric-name">情绪稳定性 (Neuroticism Inverse)</div>
                    <div class="metric-score">{{ bigFiveScores.neuroticism.toFixed(1) }}/10</div>
                    <el-progress 
                      :percentage="bigFiveScores.neuroticism * 10" 
                      color="#8b5cf6"
                      :format="formatPercent"
                    ></el-progress>
                    <div class="metric-description">压力管理和情绪控制能力</div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>

          <!-- 岗位匹配度 -->
          <div class="report-section">
            <h4>🎯 岗位匹配度分析</h4>
            <div class="match-card">
              <div class="match-score-display">
                <div class="match-score">{{ Math.round(matchScore) }}%</div>
                <div class="match-description">与期望岗位的适配程度</div>
              </div>
              <el-progress 
                :percentage="matchScore" 
                :color="getMatchColor(matchScore)"
                :format="formatPercent"
              ></el-progress>
            </div>
          </div>

          <!-- 强项分析 -->
          <div class="report-section" v-if="strengths.length > 0">
            <h4>✅ 核心强项</h4>
            <div class="analysis-list">
              <div v-for="(item, idx) in strengths" :key="`strength-${idx}`" class="analysis-item strength-item">
                <el-icon class="item-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg></el-icon>
                <span>{{ item }}</span>
              </div>
            </div>
          </div>

          <!-- 改进空间 -->
          <div class="report-section" v-if="gaps.length > 0">
            <h4>📈 改进空间</h4>
            <div class="analysis-list">
              <div v-for="(item, idx) in gaps" :key="`gap-${idx}`" class="analysis-item gap-item">
                <el-icon class="item-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14m7-7H5"/></svg></el-icon>
                <span>{{ item }}</span>
              </div>
            </div>
          </div>

          <!-- 建议与改进 -->
          <div class="report-section" v-if="recommendations.length > 0">
            <h4>💡 专业建议</h4>
            <ul class="suggestions">
              <li v-for="(rec, idx) in recommendations" :key="`rec-${idx}`">
                {{ rec }}
              </li>
            </ul>
          </div>

          <!-- 操作按钮 -->
          <div class="report-footer">
            <el-button @click="downloadPDF" :loading="downloadingPDF">📥 导出 PDF 报告</el-button>
            <el-button type="primary" @click="finishAssessment">✓ 完成评估</el-button>
          </div>
        </el-tab-pane>

        <!-- 原始数据 -->
        <el-tab-pane label="原始数据">
          <div class="raw-data">
            <p><strong>候选人信息：</strong></p>
            <pre>{{ JSON.stringify(candidate, null, 2) }}</pre>
            <el-divider />
            <p><strong>五大人格评分：</strong></p>
            <pre>{{ JSON.stringify(bigFiveScores, null, 2) }}</pre>
            <el-divider />
            <p><strong>完整评分数据：</strong></p>
            <pre>{{ JSON.stringify(allScores, null, 2) }}</pre>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps<{
  candidate?: Record<string, any>
  personalityScores?: Record<string, number>
  allScores?: Record<string, number>
  jobId?: number
  assessmentMode?: string
}>()

const emit = defineEmits<{
  (e: 'finish'): void
}>()

// 状态
const loading = ref(false)
const downloadingPDF = ref(false)
const matchScore = ref(75)
const strengths = ref<string[]>([])
const gaps = ref<string[]>([])
const recommendations = ref<string[]>([])

// 五大人格评分（标准化）
const bigFiveScores = computed(() => ({
  extraversion: normalizeScore(props.personalityScores?.['外向性'] ?? 
                              props.personalityScores?.extraversion ?? 
                              props.allScores?.['外向性'] ?? 5),
  conscientiousness: normalizeScore(props.personalityScores?.['尽责性'] ?? 
                                   props.personalityScores?.conscientiousness ?? 
                                   props.allScores?.['尽责性'] ?? 5),
  openness: normalizeScore(props.personalityScores?.['开放性'] ?? 
                          props.personalityScores?.openness ?? 
                          props.allScores?.['开放性'] ?? 5),
  agreeableness: normalizeScore(props.personalityScores?.['宜人性'] ?? 
                               props.personalityScores?.agreeableness ?? 
                               props.allScores?.['宜人性'] ?? 5),
  neuroticism: normalizeScore(props.personalityScores?.['神经质'] ?? 
                             props.personalityScores?.neuroticism ?? 
                             props.allScores?.['神经质'] ?? 5)
}))

// 计算报告时间
const reportTime = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) + 
         ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

// 正规化分数到 0-10 范围
function normalizeScore(score: any): number {
  const num = parseFloat(score)
  if (isNaN(num)) return 5
  // 如果分数在 0-1 范围内，乘以 10
  if (num >= 0 && num <= 1) return num * 10
  // 如果分数在 0-100 范围内，除以 10
  if (num > 1 && num <= 100) return num / 10
  // 否则直接返回，并限制在 0-10 范围内
  return Math.max(0, Math.min(10, num))
}

// 百分比格式化
function formatPercent(percentage: number): string {
  return Math.round(percentage) + '%'
}

// 根据匹配度获取颜色
function getMatchColor(score: number): string {
  if (score >= 85) return '#67c23a'  // 绿色：很适合
  if (score >= 75) return '#409eff'  // 蓝色：适合
  if (score >= 60) return '#e6a23c'  // 橙色：一般
  return '#f56c6c'                   // 红色：不适合
}

// 初始化报告
onMounted(async () => {
  await generateReport()
})

// 生成报告
async function generateReport() {
  try {
    loading.value = true
    
    console.log('【ReportGenerate】开始生成报告', {
      candidate: props.candidate?.id,
      jobId: props.jobId,
      personalityScores: props.personalityScores,
      allScores: props.allScores
    })
    
    // 调用后端保存评估结果
    const payload = {
      candidate_id: props.candidate?.id || 'demo-001',
      job_id: props.jobId || 1,
      assessment_mode: props.assessmentMode || 'immersive',
      all_scores: props.allScores || {},
      personality_scores: bigFiveScores.value,
      situational_scores: props.personalityScores || {},
      candidate_info: props.candidate
    }
    
    console.log('【ReportGenerate】发送负载:', payload)
    
    const response = await axios.post('/assessment/save-result', payload)
    
    if (response.data.code === 200) {
      const recordId = response.data.data.record_id
      
      console.log('【ReportGenerate】评估已保存，recordId:', recordId)
      
      // 获取生成的报告
      const reportResponse = await axios.get(`/assessment/report/${recordId}`)
      
      if (reportResponse.data.code === 200) {
        const report = reportResponse.data.data
        console.log('【ReportGenerate】报告已获取:', report)
        
        matchScore.value = report.match_score || 75
        strengths.value = report.match_analysis?.strengths || []
        gaps.value = report.match_analysis?.gaps || []
        recommendations.value = report.recommendations || []
      }
    }
  } catch (err: any) {
    console.error('【ReportGenerate】生成报告失败:', err)
    
    // 提供默认值而不是失败
    matchScore.value = 75
    strengths.value = generateDefaultAnalysis('strengths', bigFiveScores.value)
    gaps.value = generateDefaultAnalysis('gaps', bigFiveScores.value)
    recommendations.value = generateDefaultRecommendations()
    
    ElMessage.warning('报告生成中使用默认分析...')
  } finally {
    loading.value = false
  }
}

// 生成默认分析
function generateDefaultAnalysis(type: 'strengths' | 'gaps', scores: any): string[] {
  if (type === 'strengths') {
    const analysis = []
    if (scores.conscientiousness >= 7) analysis.push('责任心强，执行力强')
    if (scores.openness >= 7) analysis.push('思维开放，学习能力强')
    if (scores.extraversion >= 7) analysis.push('沟通能力强，团队协作意识强')
    if (scores.agreeableness >= 7) analysis.push('同理心强，合作意识强')
    if (analysis.length === 0) analysis.push('表现均衡，基础素质扎实')
    return analysis
  } else {
    const analysis = []
    if (scores.conscientiousness < 6) analysis.push('需要提升执行力和自律性')
    if (scores.openness < 6) analysis.push('建议加强学习心态和创新意识')
    if (scores.extraversion < 6) analysis.push('可以加强沟通和表达能力')
    if (scores.neuroticism < 5) analysis.push('需要加强压力管理和情绪控制')
    if (analysis.length === 0) analysis.push('继续保持和完善各项能力')
    return analysis
  }
}

// 生成默认建议
function generateDefaultRecommendations(): string[] {
  return [
    '根据评估结果，建议职业发展方向明确',
    '持续提升专业技能，增强岗位胜任力',
    '建议参加团队领导力或项目管理培训',
    '定期反思和改进，制定个人发展计划'
  ]
}

// 下载 PDF
async function downloadPDF() {
  try {
    downloadingPDF.value = true
    ElMessage.info('PDF 导出功能开发中...')
    // TODO: 实现 PDF 导出功能
  } finally {
    downloadingPDF.value = false
  }
}

// 完成评估
function finishAssessment() {
  ElMessage.success('评估已完成，感谢参与！')
  emit('finish')
}
</script>

<style scoped>
.report-generate { background: #fff; padding: 20px; }
.report-header { margin-bottom: 20px; border-bottom: 2px solid #409eff; padding-bottom: 12px; }
.report-header h3 { margin: 0 0 8px 0; }
.meta { display: flex; gap: 20px; font-size: 12px; color: #666; }
.report-section { margin-bottom: 24px; }
.report-section h4 { margin: 0 0 12px 0; color: #333; }
.chart-placeholder { background: #f5f7fa; border-radius: 6px; }
.metric-card { padding: 12px; background: #f9f9f9; border-radius: 6px; }
.metric-name { font-weight: 500; margin-bottom: 6px; }
.metric-score { font-size: 18px; font-weight: bold; color: #409eff; margin-bottom: 8px; }
.match-card { text-align: center; padding: 20px; background: #f0f9ff; border-radius: 6px; }
.match-score { font-size: 48px; font-weight: bold; color: #409eff; }
.match-label { color: #666; margin: 8px 0; }
.match-detail { text-align: left; margin-top: 12px; font-size: 13px; }
.match-detail p { margin: 6px 0; }
.suggestions { padding-left: 20px; }
.suggestions li { margin: 6px 0; }
.report-footer { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; padding-top: 12px; border-top: 1px solid #ddd; }
.raw-data { padding: 12px; background: #f5f7fa; border-radius: 6px; }
.raw-data pre { overflow: auto; font-size: 12px; }
</style>
