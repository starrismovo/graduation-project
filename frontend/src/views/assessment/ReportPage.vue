<template>
  <div class="report-container" v-loading="loading">
    <!-- 顶部返回栏 -->
    <div class="report-header">
      <el-button type="text" @click="goBack">
        <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" fill="currentColor"/></svg></el-icon>
        返回
      </el-button>
      <h2>评估报告详情</h2>
      <div></div>
    </div>

    <!-- 报告内容 -->
    <div v-if="reportData" class="report-content">
      <div class="report-layout">
        <aside class="report-sidenav">
          <div class="sidenav-title">报告导航</div>
          <button
            v-for="item in sectionMenu"
            :key="item.key"
            class="sidenav-item"
            :class="{ active: activeSection === item.key }"
            @click="scrollToSection(item.key)"
          >
            <svg class="sidenav-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path v-if="item.key === 'overview'" d="M4 5h7v6H4zM13 5h7v4h-7zM13 11h7v8h-7zM4 13h7v6H4z" />
              <path v-else-if="item.key === 'details'" d="M4 6h16M4 12h16M4 18h10" />
              <path v-else-if="item.key === 'details'" d="M17 17l2 2 3-3" />
              <path v-else-if="item.key === 'capability'" d="M4 17l5-5 3 3 7-8" />
              <path v-else-if="item.key === 'capability'" d="M17 7h2v2" />
              <path v-else-if="item.key === 'psychology'" d="M12 3a7 7 0 0 0-7 7c0 2.7 1.5 4.5 3.2 5.7.8.6 1.3 1.4 1.3 2.3V19h4v-1c0-.9.5-1.7 1.3-2.3C17.5 14.5 19 12.7 19 10a7 7 0 0 0-7-7z" />
              <path v-else-if="item.key === 'psychology'" d="M10 22h4" />
              <path v-else-if="item.key === 'suggestions'" d="M9 18h6M10 21h4" />
              <path v-else-if="item.key === 'suggestions'" d="M12 3a6 6 0 0 0-4 10.5c.8.7 1.3 1.7 1.3 2.8V18h5.4v-1.7c0-1.1.5-2.1 1.3-2.8A6 6 0 0 0 12 3z" />
              <path v-else d="M7 4h10l3 3v13H4V4z" />
              <path v-if="item.key === 'history'" d="M14 4v4h4M8 12h8M8 16h6" />
            </svg>
            <span>{{ item.label }}</span>
          </button>
        </aside>

        <div class="report-main">
          <!-- 顶部概览：基本信息 + 匹配度拆解 -->
          <el-row id="section-overview" :gutter="24" class="overview-section">
            <el-col :xs="24" :md="12">
              <!-- 基本信息 -->
              <el-card class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">📋 评估基本信息</div>
            </template>
            <el-form label-width="100px" :model="reportData">
              <el-form-item label="评估岗位">
                <span class="info-value">{{ reportData.job_title }}</span>
              </el-form-item>
              <el-form-item label="评估时间">
                <span class="info-value">{{ formatTime(reportData.created_at) }}</span>
              </el-form-item>
              <el-form-item label="评估模式">
                <el-tag>{{ reportData.assessment_mode || '多角色对话' }}</el-tag>
              </el-form-item>
              <el-form-item label="评估阶段数">
                <span class="info-value">{{ reportData.assessement_details?.roles_participated?.length || 3 }} 个角色</span>
              </el-form-item>
            </el-form>
              </el-card>
            </el-col>

            <el-col :xs="24" :md="12">
              <!-- 匹配度快速视图 -->
              <el-card class="report-card match-quick-view" shadow="hover">
            <template #header>
              <div class="card-title">⚡ 匹配度概览</div>
            </template>
            <div class="quick-match">
              <div class="main-score">
                <div class="score-circle-small">
                  <svg viewBox="0 0 100 100" class="ring-svg-small">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#e4e7ed" stroke-width="6"/>
                    <circle cx="50" cy="50" r="40" fill="none" :stroke="getScoreColor(reportData.match_score)" stroke-width="6" stroke-linecap="round" :stroke-dasharray="ringDasharray" transform="rotate(-90 50 50)" class="ring-progress" />
                  </svg>
                  <div class="score-text">
                    <span class="main-num">{{ reportData.match_score }}%</span>
                  </div>
                </div>
                <div class="match-level">
                  <p class="level-label">{{ getMatchLevel(reportData.match_score) }}</p>
                  <p class="level-desc">与岗位契合程度</p>
                </div>
              </div>
              <div class="dimensions-mini">
                <div class="mini-item">
                  <span class="mini-label">性格匹配</span>
                  <span class="mini-value">{{ personalityMatchScore }}%</span>
                </div>
                <div class="mini-item">
                  <span class="mini-label">技能匹配</span>
                  <span class="mini-value">{{ skillMatchScore }}%</span>
                </div>
                <div class="mini-item">
                  <span class="mini-label">背景匹配</span>
                  <span class="mini-value">{{ educationMatchScore }}%</span>
                </div>
              </div>
            </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 核心内容：规则网格布局 -->
          <div class="content-grid">
            <!-- 第一行：重点信息 -->
            <el-row :gutter="24" class="content-row">
              <el-col :xs="24" :sm="24" :md="8" class="content-col">
                <el-card id="section-psychology" class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></el-icon>
                🧠 心理特质
              </div>
            </template>

            <div class="portrait-display">
              <RadarChart 
                :data="reportData.personality_trait || reportData.portrait || []"
                :height="280"
              />
            </div>

            <div class="traits-summary" v-if="reportData.personality_trait && reportData.personality_trait.length">
              <h4>特质评分：</h4>
              <div class="traits-list-compact">
                <div 
                  v-for="trait in reportData.personality_trait" 
                  :key="trait.name"
                  class="trait-item-compact"
                >
                  <span class="trait-name">{{ trait.name }}</span>
                  <el-progress 
                    :percentage="trait.score * 10"
                    :color="getTraitColor(trait.score)"
                    :text-inside="false"
                    :stroke-width="3"
                    style="flex: 1; margin: 0 8px;"
                  />
                  <span class="trait-score">{{ trait.score }}/10</span>
                </div>
              </div>
            </div>
          </el-card>
              </el-col>

              <el-col :xs="24" :sm="24" :md="8" class="content-col">
                <el-card id="section-details" class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5-7h3v2h-3v3h-2v-3h-3v-2h3V8h2v3z" fill="currentColor"/></svg></el-icon>
                🎯 我的特质 vs 岗位需求
              </div>
            </template>
            <div class="requirement-comparison">
              <el-table :data="traitComparison" stripe size="small">
                <el-table-column prop="name" label="特质维度" width="100" />
                <el-table-column label="我的评分" width="110" align="center">
                  <template #default="{ row }">
                    <div class="score-cell">
                      <el-progress :percentage="row.myScore * 10" :color="getTraitColor(row.myScore)" :text-inside="true" :stroke-width="3" />
                      <span class="score-value">{{ row.myScore }}/10</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="岗位需求" width="100" align="center">
                  <template #default="{ row }">
                    <span class="requirement-range">{{ row.requiredMin }}-{{ row.requiredMax }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="匹配" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.matched ? 'success' : 'warning'" :effect="'light'">
                      {{ row.matched ? '✅ 满足' : '⚠️ 缺陷' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="分析" min-width="180" show-overflow-tooltip>
                  <template #default="{ row }">
                    <span class="analysis-text">{{ row.analysis }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
              </el-col>

              <el-col :xs="24" :sm="24" :md="8" class="content-col">
                <el-card id="section-suggestions" class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">💡 建议</div>
            </template>
            <div class="recommendations-list">
              <div
                v-for="(rec, idx) in Array.isArray(reportData.recommendations) ? reportData.recommendations : []"
                :key="idx"
                class="rec-item"
              >
                <span class="rec-num">{{ idx + 1 }}</span>
                <span class="rec-text">{{ rec }}</span>
              </div>
              <div v-if="!reportData.recommendations || !Array.isArray(reportData.recommendations) || !reportData.recommendations.length" class="rec-empty">
                暂无个性化建议，建议完成更多面试评估以生成精确建议。
              </div>
            </div>
          </el-card>
              </el-col>
            </el-row>

            <!-- 第二行：能力拆解 -->
            <el-row :gutter="24" class="content-row">
              <el-col :xs="24" :sm="24" :md="8" class="content-col">
                <el-card class="report-card" shadow="hover" v-if="reportData.conversation_summary">
            <template #header>
              <div class="card-title">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M11.99 5c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm6.93 6c0 .19-.02.37-.05.54h1.54c.05-.17.07-.35.07-.54 0-.19-.02-.37-.07-.54h-1.54c.03.17.05.35.05.54zm1.98-1.38c-.19-.32-.44-.62-.74-.86.29.44.46.94.51 1.39h1.6c-.22-.38-.51-.71-.87-.97.01.15.01.30 0 .44zm-7.91-2.02c.27.36.48.77.62 1.22h2.46c.65 0 1.24.28 1.65.73-.41-.35-.94-.55-1.51-.55h-2.22zm0 6.04h2.22c.57 0 1.1-.2 1.51-.55-.41.45-1 .73-1.65.73H7.7c.14.45.35.86.62 1.22zm10.91-3.02c-.05.45-.22.95-.51 1.39.3-.24.55-.54.74-.86.14-.25.24-.52.31-.81-.06.09-.12.17-.18.25-.27.36-.62.66-1.04.88.37-.26.66-.59.88-.97h-1.6c-.05.44-.22.94-.51 1.38.3-.24.55-.54.74-.86l.15-.17z" fill="currentColor"/></svg></el-icon>
                💬 对话亮点
              </div>
            </template>
            <div class="dialogue-highlights">
              <el-collapse>
                <el-collapse-item title="HR破冰" name="1">
                  <div class="phase-info-compact">
                    <p class="phase-text-compact">{{ getPhaseHighlight('hr') }}</p>
                  </div>
                </el-collapse-item>
                <el-collapse-item title="技术深度" name="2">
                  <div class="phase-info-compact">
                    <p class="phase-text-compact">{{ getPhaseHighlight('tech') }}</p>
                  </div>
                </el-collapse-item>
                <el-collapse-item title="产品思维" name="3">
                  <div class="phase-info-compact">
                    <p class="phase-text-compact">{{ getPhaseHighlight('product') }}</p>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
              </el-col>

              <el-col :xs="24" :sm="24" :md="8" class="content-col">
                <el-card id="section-capability" class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/></svg></el-icon>
                📊 匹配度拆解
              </div>
            </template>
            <div class="match-breakdown">
              <div class="overall-score-display">
                <div class="score-ring">
                  <svg viewBox="0 0 120 120" class="ring-svg">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#e4e7ed" stroke-width="8"/>
                    <circle cx="60" cy="60" r="50" fill="none" :stroke="getScoreColor(reportData.match_score)" stroke-width="8" stroke-linecap="round" :stroke-dasharray="ringDasharray" transform="rotate(-90 60 60)" class="ring-progress" />
                  </svg>
                  <div class="score-content">
                    <span class="score-number">{{ reportData.match_score || 0 }}%</span>
                    <span class="score-label">综合匹配度</span>
                  </div>
                </div>
              </div>
              <div class="dimension-scores">
                <div class="score-item">
                  <div class="item-header">
                    <span class="item-name">性格特质匹配</span>
                    <span class="item-value">{{ personalityMatchScore }}%</span>
                  </div>
                  <el-progress :percentage="personalityMatchScore" color="#67c23a" :text-inside="false" :stroke-width="6" />
                  <span class="item-weight">权重 40% → 贡献 {{ (personalityMatchScore * 0.4).toFixed(1) }}%</span>
                </div>
                <div class="score-item">
                  <div class="item-header">
                    <span class="item-name">技能匹配度</span>
                    <span class="item-value">{{ skillMatchScore }}%</span>
                  </div>
                  <el-progress :percentage="skillMatchScore" color="#409eff" :text-inside="false" :stroke-width="6" />
                  <span class="item-weight">权重 45% → 贡献 {{ (skillMatchScore * 0.45).toFixed(1) }}%</span>
                </div>
                <div class="score-item">
                  <div class="item-header">
                    <span class="item-name">教育背景</span>
                    <span class="item-value">{{ educationMatchScore }}%</span>
                  </div>
                  <el-progress :percentage="educationMatchScore" color="#e6a23c" :text-inside="false" :stroke-width="6" />
                  <span class="item-weight">权重 15% → 贡献 {{ (educationMatchScore * 0.15).toFixed(1) }}%</span>
                </div>
              </div>
              <div class="formula-display">
                <p class="formula-title">计算公式</p>
                <p class="formula-equation">{{ personalityMatchScore }}% × 40% + {{ skillMatchScore }}% × 45% + {{ educationMatchScore }}% × 15% = <strong>{{ reportData.match_score }}%</strong></p>
              </div>
            </div>
          </el-card>
              </el-col>

              <el-col :xs="24" :sm="24" :md="8" class="content-col">
                <el-card class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">📋 下一步</div>
            </template>
            <div class="action-steps">
              <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h4>分享报告</h4>
                  <p>将此报告分享给HR或目标企业</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h4>多岗位评估</h4>
                  <p>尝试其他岗位的评估，发现更多可能</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <h4>持续发展</h4>
                  <p>根据建议，聚焦改进空间的特质</p>
                </div>
              </div>
            </div>

            <div class="action-buttons">
              <el-button type="primary" @click="downloadReport">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2z" fill="currentColor"/></svg></el-icon>
                下载报告
              </el-button>
              <el-button @click="goHome">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="currentColor"/></svg></el-icon>
                返回首页
              </el-button>
            </div>
          </el-card>
              </el-col>
            </el-row>

            <!-- 第三行：历史记录 -->
            <el-row :gutter="24" class="history-row">
              <el-col :xs="24">
                <el-card id="section-history" class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">🗂 历史报告</div>
            </template>
            <p class="history-tip">查看你过去的评估记录，追踪能力变化趋势。</p>
            <el-button class="history-btn" @click="goHome">前往历史报告列表</el-button>
          </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载失败 -->
    <div v-else-if="!loading" class="error-state">
      <EmptyState
        title="报告加载失败"
        text="无法找到对应的评估报告，请返回重试"
      />
      <el-button type="primary" @click="goBack">返回</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import RadarChart from '@/components/RadarChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import { fetchReportDetail } from '@/utils/request'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const reportData = ref<any>(null)
const personalityMatchScore = ref(78)
const skillMatchScore = ref(85)
const educationMatchScore = ref(90)
const traitComparison = ref<any[]>([])
const ringDasharray = ref('157 314')
const activeSection = ref('overview')
const sectionMenu = [
  { key: 'overview', label: '报告概览' },
  { key: 'details', label: '匹配详情' },
  { key: 'capability', label: '能力分析' },
  { key: 'psychology', label: '心理解读' },
  { key: 'suggestions', label: '建议中心' },
  { key: 'history', label: '历史报告' }
]

function scrollToSection(key: string) {
  activeSection.value = key
  const target = document.getElementById(`section-${key}`)
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

function updateActiveSectionByScroll() {
  const offsets = sectionMenu
    .map((item) => {
      const el = document.getElementById(`section-${item.key}`)
      if (!el) return null
      return { key: item.key, top: el.getBoundingClientRect().top }
    })
    .filter(Boolean) as Array<{ key: string; top: number }>

  const current = offsets
    .filter((item) => item.top <= 130)
    .sort((a, b) => b.top - a.top)[0]

  if (current && current.key !== activeSection.value) {
    activeSection.value = current.key
  }
}

function generateTraitComparison() {
  if (!reportData.value?.personality_trait) return
  
  const traits = reportData.value.personality_trait
  const jobRequirements: Record<string, {min: number, max: number, weight: number}> = {
    '外向性': { min: 5, max: 9, weight: 0.2 },
    '宜人性': { min: 6, max: 10, weight: 0.25 },
    '尽责性': { min: 7, max: 10, weight: 0.3 },
    '神经质': { min: 0, max: 5, weight: 0.15 },
    '开放性': { min: 6, max: 10, weight: 0.1 }
  }
  
  const comparison = traits.map((trait: any) => {
    const req = jobRequirements[trait.name] || { min: 4, max: 8, weight: 0.2 }
    const matched = trait.score >= req.min && trait.score <= req.max
    const gap = matched ? 0 : (trait.score < req.min ? req.min - trait.score : trait.score - req.max)
    
    const analysisMap: Record<string, string> = {
      '外向性': matched ? '社交活力与人际互动良好' : '可提升人际互动主动性',
      '宜人性': matched ? '团队合作与协调能力强' : '可增强团队沟通与协作',
      '尽责性': matched ? '计划性强、执行力高' : '可提升组织与自律能力',
      '神经质': matched ? '情绪稳定，压力管理能力强' : '可增强情绪调节能力',
      '开放性': matched ? '思维开放，接受新想法' : '可提升创新思维与学习能力'
    }
    
    return {
      name: trait.name,
      myScore: trait.score,
      requiredMin: req.min,
      requiredMax: req.max,
      matched,
      gap,
      analysis: analysisMap[trait.name] || '表现符合岗位需求'
    }
  })
  
  traitComparison.value = comparison
  
  // 计算匹配度权重
  const matchedCount = comparison.filter((c: any) => c.matched).length
  const personalityScore = Math.round((matchedCount / comparison.length) * 100)
  personalityMatchScore.value = personalityScore
  
  // 更新环形进度
  const circumference = 2 * Math.PI * 50
  const filled = (reportData.value.match_score / 100) * circumference
  ringDasharray.value = `${filled} ${circumference - filled}`
}

function getPhaseHighlight(phase: string): string {
  const summary = reportData.value?.conversation_summary || ''
  const phases: Record<string, string> = {
    'hr': '在与HR的交流中，展现出良好的沟通能力和岗位理解。',
    'tech': '技术深度探讨中，展示了扎实的专业基础和问题解决能力。',
    'product': '产品思维对话中，表现出良好的用户视角和创新意识。'
  }
  return phases[phase] || summary.substring(0, 100) + '...'
}

function getPhaseInsight(phase: string): string {
  const insights: Record<string, string> = {
    'hr': '表现出高度的自我认知和职业规划意识，与岗位契合度高。',
    'tech': '系统化思维强，技能掌握全面，完全满足岗位的技术要求。',
    'product': '思维敏捷，能够多角度思考问题，展现出良好的综合素质。'
  }
  return insights[phase]
}

async function loadReport() {
  loading.value = true
  try {
    const recordId = route.params.recordId
    reportData.value = await fetchReportDetail(recordId)
    generateTraitComparison()
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

function formatTime(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

function getTraitColor(score: number): string {
  if (score >= 8) return '#67c23a'
  if (score >= 6) return '#409eff'
  if (score >= 4) return '#e6a23c'
  return '#f56c6c'
}

function getMatchLevel(score: number): string {
  if (score >= 80) return '高度匹配'
  if (score >= 60) return '中等匹配'
  return '需要提升'
}

function downloadReport() {
  ElMessage.info('报告下载功能开发中')
  // 未来可实现 PDF 导出功能
}

function goBack() {
  router.back()
}

function goHome() {
  router.push('/home')
}

onMounted(() => {
  loadReport()
  window.addEventListener('scroll', updateActiveSectionByScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateActiveSectionByScroll)
})
</script>

<style scoped>
.report-container {
  padding: 24px;
  background: linear-gradient(135deg, #f9fafc 0%, #e8eef5 100%);
  min-height: 100vh;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 12px 0;
}

.report-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.report-content {
  animation: fadeIn 0.3s ease-in;
}

.report-layout {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.report-sidenav {
  position: sticky;
  top: 84px;
  background: #ffffff;
  border: 1px solid #e8edf5;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
  padding: 12px;
}

.sidenav-title {
  padding: 8px 10px;
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
}

.sidenav-item {
  width: 100%;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  color: #4b5563;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sidenav-item:hover {
  background: #f4f7ff;
  color: #2563eb;
}

.sidenav-item.active {
  background: #eaf2ff;
  color: #1d4ed8;
  font-weight: 600;
}

.sidenav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.report-main {
  min-width: 0;
}

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.content-row {
  margin-bottom: 0;
}

.content-row .content-col {
  display: flex;
}

.content-row .report-card {
  width: 100%;
  height: 100%;
  margin-bottom: 0;
}

.history-row .report-card {
  margin-bottom: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.report-card {
  margin-bottom: 24px;
  border: 1px solid #e8edf5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #fff;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.report-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  border-color: #d0dce6;
  transform: translateY(-2px);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.card-title :deep(.el-icon) {
  font-size: 18px;
  color: #409eff;
}

.report-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
  background: #fafbfc;
}

.report-card :deep(.el-card__body) {
  padding: 20px;
}

.portrait-display :deep(.echarts-container) {
  width: 100%;
  height: 280px;
  margin-bottom: 16px;
}

.report-card :deep(.el-form-item) {
  margin-bottom: 12px;
}

.report-card :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.traits-summary {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
  margin-top: 16px;
}

.traits-summary h4 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.traits-list-compact {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trait-item-compact {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trait-name {
  flex-shrink: 0;
  min-width: 70px;
  font-size: 12px;
  color: #2c3e50;
  font-weight: 500;
}

.trait-score {
  flex-shrink: 0;
  min-width: 50px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
}

.summary-text {
  line-height: 1.8;
  color: #606266;
  margin: 0;
}

.phase-info-compact {
  padding: 10px 0 2px;
}

.phase-text-compact {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #4b5563;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #2c3e50;
  font-weight: 600;
}

.analysis-section ul {
  margin: 0;
  padding-left: 20px;
  list-style: disc;
}

.analysis-section li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.6;
}

.analysis-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rec-item {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  background: #f9fafc;
  border: 1px solid #e8edf5;
  border-left: 3px solid #409eff;
  border-radius: 6px;
  transition: all 0.3s;
}

.rec-item:hover {
  background: #f0f5ff;
  border-left-color: #66b1ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.12);
}

.rec-num {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.rec-text {
  flex: 1;
  color: #606266;
  line-height: 1.5;
  font-size: 13px;
}

.rec-empty {
  padding: 14px;
  border-radius: 8px;
  border: 1px dashed #cbd5e1;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
  background: #f8fafc;
}

.action-steps {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8edf5;
}

.step {
  display: flex;
  gap: 14px;
  padding: 12px 0;
  transition: all 0.3s;
}

.step:hover {
  padding-left: 4px;
  padding-right: -4px;
}

.step-number {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.step-content h4 {
  margin: 2px 0 4px 0;
  font-size: 13px;
  color: #2c3e50;
  font-weight: 600;
}

.step-content p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-direction: column;
}

.action-buttons :deep(.el-button) {
  width: 100%;
  height: 40px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.3s;
}

.action-buttons :deep(.el-button--primary) {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
}

.action-buttons :deep(.el-button--primary:hover) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transform: translateY(-2px);
}

.action-buttons :deep(.el-button:not(.el-button--primary)) {
  border: 1px solid #e8edf5;
  color: #2c3e50;
}

.action-buttons :deep(.el-button:not(.el-button--primary):hover) {
  border-color: #409eff;
  color: #409eff;
  background: #f5f7fa;
}

.history-tip {
  margin: 0 0 14px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.7;
}

.history-btn {
  width: 100%;
  border-radius: 8px;
}

.error-state {
  text-align: center;
  padding: 40px 20px;
}

/* ==================== 概览区域 ==================== */
.overview-section {
  margin-bottom: 28px;
}

.overview-section .report-card {
  background: linear-gradient(135deg, #ffffff 0%, #f9fafc 100%);
  border: 1px solid #e8edf5;
}

.quick-match {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quick-match .main-score {
  display: flex;
  align-items: center;
  gap: 24px;
}

.quick-match .match-level {
  flex: 1;
}

.score-circle-small {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.ring-svg-small {
  width: 100%;
  height: 100%;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  line-height: 1;
}

.main-num {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
}

.level-label {
  margin: 4px 0 0 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.level-desc {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.dimensions-mini {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8edf5;
}

.mini-item {
  text-align: center;
  padding: 8px;
  transition: all 0.3s;
}

.mini-item:hover {
  background: #f9fafc;
  border-radius: 6px;
  padding: 10px;
}

.mini-item .mini-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
  font-weight: 500;
}

.mini-item .mini-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
  letter-spacing: 0.5px;
}

/* ==================== 岗位需求对比 ==================== */
.requirement-comparison {
  overflow-x: auto;
}

.requirement-comparison :deep(.el-table) {
  font-size: 13px;
}

.requirement-comparison :deep(.el-table__header-wrapper) {
  background: #f9fafc;
}

.requirement-comparison :deep(.el-table__header th) {
  background: #f9fafc !important;
  border-color: #e8edf5;
  font-weight: 600;
  color: #2c3e50;
}

.requirement-comparison :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.requirement-comparison :deep(.el-table__row:hover > td) {
  background: #f5f7fa !important;
}

.requirement-comparison :deep(.el-table__body-wrapper) {
  border: 1px solid #e8edf5;
  border-top: none;
  border-radius: 0 0 6px 6px;
}

.score-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.score-cell :deep(.el-progress) {
  width: 100%;
}

.score-value {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
}

.requirement-range {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.analysis-text {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* ==================== 匹配度拆解 ==================== */
.match-breakdown {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overall-score-display {
  display: flex;
  justify-content: center;
  margin-bottom: 0;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8edf5;
}

.score-ring {
  position: relative;
  width: 180px;
  height: 180px;
}

.ring-svg {
  width: 100%;
  height: 100%;
}

.ring-progress {
  transition: stroke-dasharray 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.score-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  line-height: 1;
}

.score-number {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50;
}

.score-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.dimension-scores {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid #e8edf5;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
}

.item-value {
  font-size: 14px;
  font-weight: 700;
  color: #409eff;
}

.score-item :deep(.el-progress) {
  flex: 1;
  margin: 6px 0;
}

.item-weight {
  font-size: 11px;
  color: #909399;
  line-height: 1.5;
}

.formula-display {
  padding: 14px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eff3f8 100%);
  border: 1px solid #e8edf5;
  border-radius: 6px;
  text-align: center;
  margin-top: 4px;
}

.formula-title {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.3px;
}

.formula-equation {
  margin: 0;
  font-size: 12px;
  color: #606266;
  font-family: 'Courier New', monospace;
  line-height: 1.8;
  word-break: break-all;
}

.formula-equation strong {
  font-size: 14px;
  color: #409eff;
  font-weight: 700;
}

/* ==================== 对话亮点 ==================== */
.dialogue-highlights {
  overflow: hidden;
}

.dialogue-highlights :deep(.el-collapse) {
  border: none;
  background: transparent;
}

.dialogue-highlights :deep(.el-collapse-item) {
  border: none;
  margin-bottom: 8px;
}

.dialogue-highlights :deep(.el-collapse-item__header) {
  background: #f5f7fa;
  border: 1px solid #e8edf5;
  border-radius: 6px;
  font-weight: 500;
  font-size: 13px;
  height: 44px;
  padding: 0 16px;
  color: #2c3e50;
  transition: all 0.3s;
}

.dialogue-highlights :deep(.el-collapse-item__header:hover) {
  background: #eff3f8;
  border-color: #d0dce6;
}

.dialogue-highlights :deep(.el-collapse-item__content) {
  padding: 0;
}

.dialogue-highlights :deep(.is-active) .el-collapse-item__header {
  background: #e6f2ff;
  border-color: #409eff;
  color: #409eff;
}

.phase-info {
  padding: 16px 0;
}

.phase-text {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.8;
  font-size: 13px;
}

.insight-box {
  padding: 12px 14px;
  background: #e6f7ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
}

.insight-box strong {
  color: #409eff;
  font-size: 12px;
}

.insight-box p {
  margin: 6px 0 0 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .report-container {
    padding: 16px;
  }

  .report-layout {
    grid-template-columns: 1fr;
  }

  .report-sidenav {
    position: static;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
  }

  .sidenav-title {
    grid-column: 1 / -1;
  }

  .report-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .dimensions-mini {
    gap: 12px;
  }

  .content-grid {
    gap: 20px;
  }
}

@media (max-width: 992px) {
  .quick-match .main-score {
    gap: 16px;
  }

  .score-circle-small {
    width: 80px;
    height: 80px;
  }

  .main-num {
    font-size: 24px;
  }

  .dimensions-mini {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .report-container {
    padding: 12px;
  }

  .report-header h2 {
    font-size: 18px;
  }

  .report-sidenav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    padding: 10px;
  }

  .sidenav-item {
    font-size: 13px;
    padding: 8px;
  }

  .overview-section {
    margin-bottom: 20px;
  }

  .quick-match .main-score {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .match-level {
    text-align: center;
  }

  .dimensions-mini {
    gap: 12px;
    grid-template-columns: repeat(3, 1fr);
  }

  .content-col {
    width: 100% !important;
  }

  .content-grid {
    gap: 16px;
  }

  .traits-list {
    gap: 8px;
  }

  .action-steps {
    gap: 12px;
  }

  .requirement-comparison :deep(.el-table) {
    font-size: 12px;
  }

  .requirement-comparison :deep(.el-table__cell) {
    padding: 8px;
  }
}
</style>
