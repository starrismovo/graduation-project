<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { fetchPsychologyDetail } from '@/utils/request'

const route = useRoute()
const userStore = useUserStore()

// 大五人格维度解释
const personalityDimensions = [
  {
    icon: '🎨',
    image: '/开放性.jpg',
    palette: {
      bg: '#ece9ff',
      border: '#c7bffd',
      title: '#5a60c9',
      chip: '#ded7ff'
    }
  },
  {
    icon: '📚',
    image: '/尽责性.jpg',
    palette: {
      bg: '#e9efdf',
      border: '#c0cc9a',
      title: '#6f8440',
      chip: '#dce8bd'
    }
  },
  {
    icon: '🎤',
    image: '/外向性.jpg',
    palette: {
      bg: '#efe4d4',
      border: '#d9b98d',
      title: '#6d3018',
      chip: '#edd7b8'
    }
  },
  {
    icon: '💞',
    image: '/宜人性.jpg',
    palette: {
      bg: '#f4e0d2',
      border: '#e3b5a1',
      title: '#c46e4a',
      chip: '#efd3c6'
    }
  },
  {
    icon: '🌊',
    image: '/神经质.jpg',
    palette: {
      bg: '#d8e5f1',
      border: '#b0c7dd',
      title: '#577693',
      chip: '#cadced'
    }
  }
]

const videoUrl = '/lv_0_20260407225241.mp4'
const activeDimension = ref(0)
const syncedDimensionIndexes = ref<number[]>([])
const loading = ref(false)
const psychologyDetail = ref<any | null>(null)
const bubbleMessage = ref('点击任一人格维度后，我会基于本次评估报告给出简短解释。')

const dimensionDisplayMeta = [
  {
    title: '开放性',
    english: 'Openness',
    summary: '你具有较强的好奇心与想象力，乐于接触新观点、新体验，并愿意从不同角度理解问题。',
    tags: ['好奇心强', '创新思维', '学习驱动'],
    statusIcon: '✦'
  },
  {
    title: '尽责性',
    english: 'Conscientiousness',
    summary: '你做事有计划、目标清晰，注重细节与规范，能够稳定推进任务并保持执行质量。',
    tags: ['责任心强', '计划性', '自律稳定'],
    statusIcon: '✳'
  },
  {
    title: '外向性',
    english: 'Extraversion',
    summary: '你乐于与人交流，表达积极，在互动场景中更容易带动氛围并形成影响力。',
    tags: ['社交活跃', '表达力强', '积极乐观'],
    statusIcon: '✦'
  },
  {
    title: '宜人性',
    english: 'Agreeableness',
    summary: '你友善、理解他人，愿意在协作中提供支持，也更容易形成温和稳定的团队关系。',
    tags: ['友善包容', '乐于助人', '团队合作'],
    statusIcon: '❤'
  },
  {
    title: '神经质 / 情绪稳定性',
    english: 'Neuroticism / Emotional Stability',
    summary: '你在压力情境下的情绪反应与恢复能力，会影响决策节奏、心理韧性与长期稳定表现。',
    tags: ['情绪稳定', '抗压能力', '心理韧性'],
    statusIcon: '◌'
  }
]

const isDimensionSynced = (idx: number) => syncedDimensionIndexes.value.includes(idx)

const fallbackOverview = {
  summary: '系统已基于本次评估会话形成大五人格解释，可结合岗位匹配结果理解个人优势与发展方向。',
  score: 0,
  highlighted_traits: ['责任心强', '情绪稳定', '乐于协作'],
  growth_advice: '建议结合评估结果持续完善岗位案例与能力证据。',
  updated_at: '2026-05-08'
}

const overview = computed(() => psychologyDetail.value?.overview || fallbackOverview)

const traitCards = computed(() => {
  const serverCards = psychologyDetail.value?.trait_cards
  if (Array.isArray(serverCards) && serverCards.length) {
    return serverCards
  }
  return dimensionDisplayMeta.map((item, idx) => ({
    trait_key: ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'][idx],
    trait_name: item.title,
    english: item.english,
    summary: item.summary,
    tags: item.tags,
    match_status: 'balanced',
    bubble_message: `你当前关注的是“${item.title}”。${item.summary} 建议结合后续评估结果继续观察该维度。`
  }))
})

const matchStatusText = (status?: string) => {
  const statusMap: Record<string, string> = {
    aligned: '适配较好',
    balanced: '基本适配',
    gap: '存在差距',
    insufficient: '证据不足'
  }
  return statusMap[String(status || '').toLowerCase()] || '待进一步判断'
}

const formatTraitScore = (score?: number | null) => {
  if (score === null || score === undefined || Number.isNaN(Number(score))) return '暂无'
  const numericScore = Number(score)
  return numericScore > 10 ? numericScore.toFixed(0) : numericScore.toFixed(1)
}

const formatRequirementRange = (requirement?: number | null) => {
  if (requirement === null || requirement === undefined || Number.isNaN(Number(requirement))) {
    return '暂无明确区间'
  }
  const center = Number(requirement)
  const min = Math.max(0, center - 1)
  const max = Math.min(10, center + 1)
  return `${min.toFixed(1)} - ${max.toFixed(1)}`
}

const traitRecruitingMeanings: Record<string, string> = {
  openness: '开放性体现候选人面对新问题、新工具和不确定任务时的探索意愿。在招聘场景中，该维度常用于观察学习迁移、创新思考和复杂问题理解能力。',
  conscientiousness: '尽责性体现候选人的目标意识、计划执行和细节控制能力。在招聘场景中，该维度常用于判断任务交付稳定性、责任边界意识和长期可靠性。',
  extraversion: '外向性体现候选人在沟通、表达和人际互动中的主动程度。在招聘场景中，该维度常用于观察候选人能否清晰表达观点、推动协作并在团队或客户场景中形成影响力。',
  agreeableness: '宜人性体现候选人在协作关系中的同理心、支持性和冲突处理方式。在招聘场景中，该维度常用于判断团队适应、跨角色沟通和组织协同潜力。',
  neuroticism: '神经质/情绪稳定性体现候选人面对压力、反馈和不确定情境时的情绪波动与恢复能力。在招聘场景中，该维度常用于观察抗压表现、风险应对和稳定决策能力。'
}

const currentDimensionCard = computed(() => traitCards.value[activeDimension.value] || traitCards.value[0] || {})

const currentDimensionMeaning = computed(() => {
  const card = currentDimensionCard.value
  return traitRecruitingMeanings[card.trait_key] || card.summary || '该维度用于辅助理解候选人在岗位情境中的行为倾向和发展空间。'
})

const currentDimensionEvidence = computed(() => {
  const card = currentDimensionCard.value
  const rawEvidence = card.evidence || card.evidences || card.behavior_evidence || card.source_evidence || []
  const evidenceList = Array.isArray(rawEvidence)
    ? rawEvidence
    : typeof rawEvidence === 'string'
      ? rawEvidence.split(/[；;。]/).filter(Boolean)
      : []
  const normalized = evidenceList
    .map((item: any) => typeof item === 'string' ? item : item?.text || item?.description || item?.content)
    .filter(Boolean)
    .slice(0, 3)

  if (normalized.length) return normalized

  return [
    `当前评估已形成“${card.trait_name || '该维度'}”的初步判断，但面试回答中的直接行为证据仍需进一步补充。`,
    '建议在后续追问中围绕具体任务、个人行动和结果影响补充案例，以提高评估解释的可信度。',
    card.summary || '系统将结合后续 AssessmentSession 中的回答持续更新该维度的证据链。'
  ].slice(0, 3)
})

const currentEvidenceStatus = computed(() => {
  const card = currentDimensionCard.value
  const rawEvidence = card.evidence || card.evidences || card.behavior_evidence || card.source_evidence || []
  const count = Array.isArray(rawEvidence) ? rawEvidence.length : (rawEvidence ? 1 : 0)
  if (count >= 2) return '证据较充分'
  if (count === 1) return '证据有限'
  return '证据待补充'
})

const currentDimensionAdvice = computed(() => {
  const card = currentDimensionCard.value
  return card.advice || '建议在后续面试中使用 STAR 结构补充具体案例，说明情境、任务目标、个人行动及最终结果。'
})

const actionGuides = computed(() => {
  const guides = psychologyDetail.value?.action_guides
  if (Array.isArray(guides) && guides.length) {
    return guides
  }
  return [
    { title: '自我认知', description: '先找出你的高分和低分维度，理解“自然偏好”与“压力反应”' },
    { title: '岗位匹配', description: '将人格倾向与岗位要求对照，优先选择优势能够被放大的场景' },
    { title: '人际协作', description: '把“你习惯怎么做”明确告诉团队，降低沟通误差' },
    { title: '成长策略', description: '为每个低分维度设定一个可执行的小目标，并按周复盘' },
    { title: '动态更新', description: '每隔一段时间复测一次，关注趋势变化而非单次分数' }
  ]
})

const overviewUpdatedAt = computed(() => {
  const value = overview.value.updated_at
  if (!value) return '暂无更新时间'
  try {
    return new Date(value).toLocaleDateString('zh-CN')
  } catch {
    return String(value)
  }
})

const focusDimension = (idx: number) => {
  activeDimension.value = idx
}

const syncDimensionToConsult = (idx: number) => {
  if (!syncedDimensionIndexes.value.includes(idx)) {
    syncedDimensionIndexes.value = [...syncedDimensionIndexes.value, idx]
  }
}

const handleConsultDimension = (idx: number) => {
  activeDimension.value = idx
  syncDimensionToConsult(idx)
  bubbleMessage.value = traitCards.value[idx]?.bubble_message || '已基于本次评估结果生成该维度的简短解释。'
}

const handleSyncAllToConsult = () => {
  syncedDimensionIndexes.value = personalityDimensions.map((_, idx) => idx)
  bubbleMessage.value = `已汇总 ${syncedDimensionIndexes.value.length} 个维度。${overview.value.growth_advice}`
}

const loadPsychologyDetail = async () => {
  loading.value = true
  try {
    const recordId = route.query.recordId as string | undefined
    psychologyDetail.value = await fetchPsychologyDetail({
      recordId,
      candidateId: userStore.candidateId
    })
    bubbleMessage.value = psychologyDetail.value?.overview?.growth_advice || bubbleMessage.value
  } catch (error) {
    console.warn('心理解读详情加载失败，使用页面默认展示:', error)
    ElMessage.warning('暂未找到可回溯的心理解读结果，已展示默认说明')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPsychologyDetail()
})

</script>

<template>
  <div class="psychology-detail-page" v-loading="loading">
    <div class="page-content">
      <section class="hero-section">
        <div class="hero-main">
          <div class="hero-copy">
            <p class="hero-breadcrumb">心理解读 / 大五人格心理解读</p>
            <div class="hero-title-line">
              <h1 class="hero-title">大五人格心理解读</h1>
              <span class="hero-pill">BIG FIVE</span>
            </div>
            <p class="hero-desc">
              基于心理测评结果的可解释路径，帮助你了解自己的性格特征、优势与发展方向，
              并通过气泡式建议给出职业发展与行动提示，让自我认知转化为成长动力。
            </p>
          </div>

          <div class="hero-actions">
            <button class="hero-ghost-button" type="button" @click="handleConsultDimension(activeDimension)">
              查看当前维度建议
            </button>
            <button class="hero-primary-button" type="button" @click="handleSyncAllToConsult">
              汇总五维建议
            </button>
          </div>
        </div>

        <div class="hero-overview-card">
          <div class="overview-block">
            <span class="overview-label">总体概览</span>
            <p>{{ overview.summary }}</p>
            <div class="overview-score">
              <span>综合评分</span>
              <strong>{{ Math.round(overview.score || 0) }}</strong>
              <small>/100</small>
            </div>
          </div>

          <div class="overview-block">
            <span class="overview-label">高突出的特质</span>
            <div class="overview-tags">
              <span v-for="item in overview.highlighted_traits" :key="item">{{ item }}</span>
            </div>
          </div>

          <div class="overview-block">
            <span class="overview-label">成长建议</span>
            <p>{{ overview.growth_advice }}</p>
            <span class="overview-update">更新于 {{ overviewUpdatedAt }}</span>
          </div>
        </div>
      </section>

      <div class="video-section">
        <div class="video-combined-shell">
        <div class="video-card">
          <div class="video-card-badge">AI 解读视频</div>
          <div class="video-wrapper">
          <video
            :src="videoUrl"
            controls
            controlsList="nodownload"
            preload="auto"
            autoplay
            muted
            playsinline
            class="video-element"
          ></video>
          </div>
        </div>

        <div class="video-description video-guide-card trait-interpretation-panel">
          <div class="trait-panel-head">
            <div class="trait-panel-title-wrap">
              <span class="trait-panel-eyebrow">当前人格维度</span>
              <h2>{{ currentDimensionCard.trait_name }} {{ currentDimensionCard.english }}</h2>
            </div>
            <span class="trait-match-badge" :class="`status-${currentDimensionCard.match_status || 'balanced'}`">
              {{ matchStatusText(currentDimensionCard.match_status) }}
            </span>
          </div>

          <div class="trait-metrics-grid">
            <div class="trait-metric-card">
              <span>维度得分</span>
              <strong>{{ formatTraitScore(currentDimensionCard.score) }}</strong>
              <small>/10</small>
            </div>
            <div class="trait-metric-card">
              <span>证据状态</span>
              <strong>{{ currentEvidenceStatus }}</strong>
            </div>
            <div class="trait-metric-card">
              <span>岗位要求区间</span>
              <strong>{{ formatRequirementRange(currentDimensionCard.job_requirement) }}</strong>
            </div>
          </div>

          <div class="trait-panel-section">
            <h3>维度含义</h3>
            <p>{{ currentDimensionMeaning }}</p>
          </div>

          <div class="trait-panel-section">
            <h3>本次评估证据</h3>
            <ul class="trait-evidence-list">
              <li v-for="item in currentDimensionEvidence" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div class="trait-advice-box">
            <span>改进建议</span>
            <p>{{ currentDimensionAdvice }}</p>
          </div>

          <button class="guide-action-button" type="button" @click="handleConsultDimension(activeDimension)">
            同步到右侧助手
          </button>
        </div>
        </div>

        <div class="consult-side-card">
          <div class="consult-side-top">
            <div>
              <div class="consult-side-badge">AI 解读助手</div>
              <div class="consult-side-status">
                <span class="consult-status-dot"></span>
                <span>基于本次评估</span>
              </div>
            </div>
            <button class="consult-more" type="button" aria-label="更多操作">...</button>
          </div>

          <div class="consult-avatar-panel">
            <div class="consult-avatar-shell">
              <span class="consult-avatar-orbit" aria-hidden="true"></span>
              <img src="/ai-counselor.png" alt="AI 解读助手" class="consult-bot consult-counselor-image" />
            </div>
          </div>

          <p class="consult-side-desc">
            基于你的心理画像与岗位匹配结果，展示当前维度的简短解释与行动建议。
          </p>

          <div class="consult-bubble">
            <span class="consult-bubble-label">AI 气泡回复</span>
            <p>{{ bubbleMessage }}</p>
          </div>

          <div class="consult-side-actions">
            <button class="consult-primary-button" type="button" @click="handleConsultDimension(activeDimension)">
              查看当前建议
            </button>
            <button class="consult-secondary-button" type="button" @click="handleSyncAllToConsult">
              汇总五维建议
            </button>
          </div>

          <div class="consult-context-tip">
            <span class="consult-context-icon"></span>
            <span>已选中 {{ syncedDimensionIndexes.length }} 个维度用于气泡解释</span>
          </div>
        </div>
      </div>

      <div class="dimensions-section">
        <div class="dimensions-shell">
          <div class="dimensions-head">
            <div class="dimensions-head-copy">
              <h2 class="section-title">五维解读卡片</h2>
              <p class="section-desc">每个维度均可查看气泡式建议，获取更清晰的个性化解释</p>
            </div>

            <el-button class="sync-all-button" @click="handleSyncAllToConsult">
              <svg class="sync-all-icon" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M16.6667 10.0001C16.6667 13.6819 13.6819 16.6667 10 16.6667C6.3181 16.6667 3.33334 13.6819 3.33334 10.0001C3.33334 6.31818 6.3181 3.33341 10 3.33341C11.777 3.33341 13.3917 4.02844 14.5861 5.16108"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                />
                <path
                  d="M12.9167 3.33337H16.6667V7.08337"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M3.33334 10.0001C3.33334 13.6819 6.3181 16.6667 10 16.6667C11.777 16.6667 13.3917 15.9717 14.5861 14.8391"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linecap="round"
                  opacity="0.35"
                />
              </svg>
              汇总五维建议
            </el-button>
          </div>

          <div class="dimensions-grid-modern">
            <article
              v-for="(dim, idx) in personalityDimensions"
              :key="`modern-${idx}`"
              class="modern-dimension-card"
              :class="{
                active: activeDimension === idx,
                wide: idx >= 3,
                synced: isDimensionSynced(idx)
              }"
              :style="{ animationDelay: idx * 80 + 'ms' }"
              @click="focusDimension(idx)"
            >
              <div
                class="modern-dimension-surface"
                :style="{
                  background: `linear-gradient(180deg, ${dim.palette.bg} 0%, rgba(255,255,255,0.98) 100%)`,
                  borderColor: dim.palette.border
                }"
              >
                <div class="modern-dimension-header">
                  <div class="modern-dimension-heading">
                    <span class="modern-dimension-icon" :style="{ background: dim.palette.chip, color: dim.palette.title }">
                      {{ dim.icon }}
                    </span>
                    <div class="modern-title-wrap">
                      <h3 class="modern-dimension-name" :style="{ color: dim.palette.title }">{{ traitCards[idx].trait_name }}</h3>
                      <p class="modern-dimension-subtitle">{{ traitCards[idx].english }}</p>
                    </div>
                  </div>

                  <span class="modern-dimension-mark" :style="{ color: dim.palette.title, borderColor: dim.palette.border }">
                    {{ dimensionDisplayMeta[idx].statusIcon }}
                  </span>
                </div>

                <div class="modern-dimension-body">
                  <div class="modern-dimension-copy">
                    <p class="modern-dimension-description">{{ traitCards[idx].summary }}</p>

                    <div class="modern-tag-list">
                      <span
                        v-for="tag in traitCards[idx].tags"
                        :key="tag"
                        class="modern-tag"
                        :style="{ background: dim.palette.chip, color: dim.palette.title }"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </div>

                  <div class="modern-dimension-visual">
                    <img :src="dim.image" :alt="traitCards[idx].trait_name" class="modern-dimension-image" loading="lazy" />
                  </div>
                </div>

                <div class="modern-dimension-footer">
                  <div class="modern-dimension-status" :class="{ synced: isDimensionSynced(idx) }">
                    <span class="modern-dimension-status-dot"></span>
                    <span>{{ isDimensionSynced(idx) ? '已加入气泡解释' : '可查看建议' }}</span>
                  </div>

                  <el-button
                    class="dimension-consult-button"
                    size="small"
                    type="primary"
                    @click.stop="handleConsultDimension(idx)"
                  >
                    查看建议
                  </el-button>
                </div>
              </div>
            </article>
          </div>

        </div>
      </div>

      <div class="tips-section">
        <div class="tips-card">
          <div class="tips-header">
            <h3>如何把评估结果用于行动</h3>
            <p>将心理特质解释转化为后续学习、岗位选择与职业发展的可执行线索。</p>
          </div>
          <ul class="tips-list">
            <li v-for="(item, index) in actionGuides" :key="item.title" class="tip-action-card">
              <div class="tip-card-top">
                <span class="tip-step">0{{ index + 1 }}</span>
                <span class="tip-dot"></span>
              </div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.description }}</p>
              <div class="tip-card-foot">
                <span>{{ index < 2 ? '优先执行' : index < 4 ? '持续练习' : '定期复盘' }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.psychology-detail-page {
  background:
    radial-gradient(circle at 10% 4%, rgba(96, 165, 250, 0.22) 0, rgba(96, 165, 250, 0) 28%),
    radial-gradient(circle at 92% 12%, rgba(124, 58, 237, 0.16) 0, rgba(124, 58, 237, 0) 30%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 48%, #f9fbff 100%);
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 24px 28px 44px;
  max-width: 1480px;
  margin: 0 auto;
  width: 100%;
}

.hero-section {
  position: relative;
  margin-bottom: 24px;
  border: 1px solid rgba(199, 210, 254, 0.88);
  border-radius: 26px;
  padding: 24px;
  overflow: hidden;
  background:
    radial-gradient(circle at 76% 16%, rgba(124, 58, 237, 0.12), transparent 32%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(242, 247, 255, 0.94));
  box-shadow: 0 22px 55px rgba(71, 85, 105, 0.09);
  backdrop-filter: blur(10px);
}

.hero-section::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(99, 102, 241, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.06) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: linear-gradient(90deg, rgba(0, 0, 0, 0.7), transparent 78%);
}

.hero-main,
.hero-overview-card {
  position: relative;
  z-index: 1;
}

.hero-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.hero-copy {
  min-width: 0;
}

.hero-breadcrumb {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 600;
  color: #667085;
}

.hero-title-line {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-title {
  margin: 0;
  font-size: clamp(30px, 3.2vw, 46px);
  line-height: 1.06;
  font-weight: 800;
  color: #111827;
  letter-spacing: -0.04em;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 11px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-size: 13px;
  font-weight: 800;
}

.hero-desc {
  margin: 12px 0 0;
  max-width: 820px;
  font-size: 16px;
  line-height: 1.8;
  color: #526071;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.hero-ghost-button,
.hero-primary-button {
  height: 48px;
  padding: 0 22px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.hero-ghost-button {
  border: 1px solid rgba(203, 213, 225, 0.95);
  background: rgba(255, 255, 255, 0.92);
  color: #475467;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.hero-primary-button {
  border: none;
  background: linear-gradient(135deg, #7c3aed 0%, #5b67ff 100%);
  color: #ffffff;
  box-shadow: 0 16px 30px rgba(91, 103, 255, 0.28);
}

.hero-ghost-button:hover,
.hero-primary-button:hover {
  transform: translateY(-1px);
}

.hero-ghost-button:hover {
  border-color: #a5b4fc;
  color: #4f46e5;
}

.hero-overview-card {
  margin-top: 24px;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(220px, 0.7fr) minmax(0, 1fr);
  gap: 1px;
  overflow: hidden;
  border: 1px solid rgba(199, 210, 254, 0.9);
  border-radius: 18px;
  background: rgba(199, 210, 254, 0.86);
  box-shadow: 0 16px 38px rgba(15, 23, 42, 0.06);
}

.overview-block {
  min-height: 128px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.88);
}

.overview-label {
  display: block;
  margin-bottom: 10px;
  color: #344054;
  font-size: 14px;
  font-weight: 800;
}

.overview-block p {
  margin: 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.75;
}

.overview-score {
  margin-top: 14px;
  display: inline-flex;
  align-items: baseline;
  gap: 5px;
  padding: 8px 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #eef2ff, #ffffff);
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.overview-score strong {
  color: #4f46e5;
  font-size: 24px;
}

.overview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.overview-tags span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.1);
  color: #15803d;
  font-size: 13px;
  font-weight: 700;
}

.overview-update {
  display: inline-block;
  margin-top: 14px;
  color: #98a2b3;
  font-size: 13px;
  font-weight: 600;
}

.video-section {
  display: flex;
  align-items: stretch;
  gap: 22px;
  margin-bottom: 34px;
}

.video-combined-shell {
  flex: 1.72 1 0;
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(360px, 1.05fr) minmax(300px, 0.72fr);
  align-items: stretch;
  gap: 18px;
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  background:
    radial-gradient(circle at 10% 12%, rgba(99, 102, 241, 0.1), transparent 26%),
    linear-gradient(180deg, rgba(244, 247, 255, 0.98), rgba(255, 255, 255, 0.96));
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.07);
  overflow: hidden;
}

.video-card,
.video-guide-card,
.consult-side-card {
  border-radius: 16px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.video-card {
  min-width: 0;
  padding: 16px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  background:
    linear-gradient(180deg, rgba(241, 245, 255, 0.98), rgba(255, 255, 255, 0.98));
  display: flex;
  flex-direction: column;
  align-self: stretch;
  justify-content: flex-start;
}

.video-card-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  margin: 0 0 14px;
  background: rgba(124, 58, 237, 0.12);
  color: #7c3aed;
  font-size: 13px;
  font-weight: 700;
  align-self: flex-start;
}

.video-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  min-height: 0;
  margin: auto 0;
  border-radius: 16px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04);
}

.video-element {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.video-description {
  padding: 22px;
  border-radius: 16px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.94));
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.video-description h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.video-description p {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #667085;
  line-height: 1.58;
}

.video-description p:last-child {
  margin-bottom: 0;
}

.video-guide-card {
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 22px;
  height: auto;
  min-height: auto;
  border: 1px solid rgba(224, 231, 255, 0.96);
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  align-self: stretch;
  overflow: visible;
}

.video-guide-head {
  display: flex;
  align-items: flex-start;
  gap: 0;
  margin-bottom: 18px;
}

.video-guide-accent {
  display: none;
}

.video-guide-head p {
  margin: 6px 0 0;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
  flex: 1;
  min-height: 0;
}

.guide-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.guide-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 700;
  margin-top: 1px;
}

.guide-icon--blue {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.guide-icon--violet {
  background: rgba(124, 58, 237, 0.1);
  color: #7c3aed;
}

.guide-icon--green {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.guide-copy h3 {
  margin: 0 0 5px;
  font-size: 15px;
  line-height: 1.5;
  color: #344054;
  font-weight: 700;
}

.guide-copy p {
  margin: 0;
  font-size: 14px;
  line-height: 1.58;
}

.trait-interpretation-panel {
  gap: 12px;
  padding: 18px;
}

.trait-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
}

.trait-panel-title-wrap {
  min-width: 0;
}

.trait-panel-eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 9px;
  margin-bottom: 6px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  color: #5b67ff;
  font-size: 12px;
  font-weight: 800;
}

.trait-panel-head h2 {
  margin: 0;
  overflow-wrap: anywhere;
}

.trait-match-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  min-height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(199, 210, 254, 0.9);
  background: rgba(238, 242, 255, 0.95);
  color: #4f46e5;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.trait-match-badge.status-aligned {
  border-color: rgba(34, 197, 94, 0.22);
  background: rgba(34, 197, 94, 0.1);
  color: #15803d;
}

.trait-match-badge.status-gap {
  border-color: rgba(245, 158, 11, 0.26);
  background: rgba(245, 158, 11, 0.1);
  color: #b45309;
}

.trait-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
  gap: 10px;
}

.trait-metric-card {
  min-width: 0;
  min-height: 68px;
  padding: 10px;
  border-radius: 14px;
  border: 1px solid rgba(224, 231, 255, 0.9);
  background: linear-gradient(180deg, rgba(248, 250, 255, 0.96), rgba(255, 255, 255, 0.96));
}

.trait-metric-card span {
  display: block;
  margin-bottom: 6px;
  color: #7c86a2;
  font-size: 12px;
  font-weight: 700;
}

.trait-metric-card strong {
  display: inline;
  color: #1f2937;
  font-size: 17px;
  line-height: 1.2;
  font-weight: 800;
  overflow-wrap: anywhere;
}

.trait-metric-card small {
  margin-left: 3px;
  color: #98a2b3;
  font-size: 12px;
  font-weight: 700;
}

.trait-panel-section {
  min-width: 0;
}

.trait-panel-section h3,
.trait-advice-box span {
  display: block;
  margin: 0 0 6px;
  color: #344054;
  font-size: 14px;
  font-weight: 800;
}

.trait-panel-section p,
.trait-advice-box p {
  margin: 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.62;
}

.trait-evidence-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.trait-evidence-list li {
  position: relative;
  min-width: 0;
  padding: 8px 10px 8px 26px;
  border-radius: 12px;
  border: 1px solid rgba(224, 231, 255, 0.78);
  background: rgba(255, 255, 255, 0.78);
  color: #526071;
  font-size: 13px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.trait-evidence-list li::before {
  content: '';
  position: absolute;
  left: 11px;
  top: 17px;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #7c3aed;
}

.trait-advice-box {
  min-width: 0;
  padding: 11px 14px;
  border-radius: 14px;
  border: 1px solid rgba(199, 210, 254, 0.82);
  background:
    radial-gradient(circle at 8% 18%, rgba(124, 58, 237, 0.09), transparent 38%),
    rgba(248, 250, 255, 0.94);
}

.guide-action-button {
  margin-top: auto;
  align-self: flex-end;
  flex-shrink: 0;
  width: 176px;
  height: 40px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #7c3aed 0%, #5b67ff 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 22px rgba(91, 103, 255, 0.2);
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.guide-action-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 26px rgba(91, 103, 255, 0.24);
}

.consult-side-card {
  flex: 0 0 320px;
  min-width: 300px;
  padding: 18px;
  background:
    radial-gradient(circle at 20% 12%, rgba(124, 58, 237, 0.12), transparent 34%),
    linear-gradient(180deg, rgba(244, 242, 255, 0.98), rgba(255, 255, 255, 0.98));
  display: flex;
  flex-direction: column;
  align-self: stretch;
}

.consult-side-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.consult-side-badge {
  font-size: 20px;
  line-height: 1.25;
  font-weight: 700;
  color: #344054;
}

.consult-side-status {
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #667085;
  font-size: 14px;
  font-weight: 600;
}

.consult-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
}

.consult-more {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #98a2b3;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.consult-avatar-panel {
  margin-top: 18px;
  border-radius: 24px;
  background:
    radial-gradient(circle at 52% 36%, rgba(139, 92, 246, 0.2), transparent 38%),
    radial-gradient(circle at 68% 62%, rgba(96, 165, 250, 0.18), transparent 42%),
    linear-gradient(145deg, #f8fbff 0%, #eef4ff 54%, #f6f2ff 100%);
  min-height: 270px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(129, 140, 248, 0.18), 0 18px 34px rgba(99, 102, 241, 0.12);
}

.consult-avatar-shell {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
}

.consult-avatar-orbit {
  position: absolute;
  width: 210px;
  height: 210px;
  left: 50%;
  top: 47%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(99, 102, 241, 0.24);
  box-shadow:
    0 0 0 18px rgba(219, 234, 254, 0.46),
    0 0 42px rgba(96, 165, 250, 0.26);
}

.consult-avatar-orbit::before,
.consult-avatar-orbit::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.28);
  box-shadow: 0 0 18px rgba(96, 165, 250, 0.3);
}

.consult-avatar-orbit::before {
  width: 8px;
  height: 8px;
  right: 26px;
  top: 24px;
}

.consult-avatar-orbit::after {
  width: 6px;
  height: 6px;
  left: 22px;
  bottom: 42px;
}

.consult-bot {
  width: 100%;
  max-width: 238px;
  height: auto;
  filter: drop-shadow(0 24px 26px rgba(60, 72, 125, 0.22));
}

.consult-counselor-image {
  position: relative;
  z-index: 1;
  max-height: 252px;
  object-fit: contain;
  object-position: center bottom;
}

.consult-side-desc {
  margin: 16px 0 0;
  color: #667085;
  font-size: 15px;
  line-height: 1.8;
  min-height: 0;
}

.consult-bubble {
  margin-top: 14px;
  padding: 14px 16px;
  border: 1px solid rgba(199, 210, 254, 0.82);
  border-radius: 18px 18px 18px 6px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 12px 26px rgba(91, 103, 255, 0.08);
}

.consult-bubble-label {
  display: inline-flex;
  margin-bottom: 8px;
  color: #5b67ff;
  font-size: 13px;
  font-weight: 800;
}

.consult-bubble p {
  margin: 0;
  color: #526071;
  font-size: 14px;
  line-height: 1.75;
}

.consult-side-actions {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.consult-primary-button,
.consult-secondary-button {
  height: 44px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.24s ease;
}

.consult-primary-button {
  border: none;
  background: linear-gradient(135deg, #7c3aed 0%, #5b67ff 100%);
  color: #ffffff;
  box-shadow: 0 12px 28px rgba(108, 92, 231, 0.22);
}

.consult-primary-button:hover {
  transform: translateY(-1px);
}

.consult-secondary-button {
  border: 1px solid rgba(217, 225, 245, 0.98);
  background: rgba(255, 255, 255, 0.96);
  color: #475467;
}

.consult-secondary-button:hover {
  border-color: #c7d2fe;
  color: #4f46e5;
}

.consult-context-tip {
  margin-top: 20px;
  padding-top: 16px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #7c86a2;
  font-size: 13px;
  font-weight: 600;
  border-top: 1px solid rgba(220, 228, 245, 0.88);
}

.consult-context-icon {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 1.5px solid currentColor;
  position: relative;
}

.consult-context-icon::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: currentColor;
  transform: translate(-50%, -50%);
}

.dimensions-section {
  margin-bottom: 28px;
}

.dimensions-shell {
  padding: 18px;
  border-radius: 26px;
  border: 1px solid rgba(226, 232, 255, 0.92);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 20px 48px rgba(15, 23, 42, 0.07);
}

.dimensions-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
}

.dimensions-head-copy {
  min-width: 0;
}

.dimensions-shell .section-title {
  margin: 0 0 6px 0;
  font-size: 24px;
  line-height: 1.2;
  font-weight: 700;
  color: #1f2937;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.dimensions-shell .section-desc {
  margin: 0;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.08);
  color: #7c86a2;
  font-size: 13px;
  font-weight: 600;
}

.sync-all-button {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid #d7def0;
  background: #ffffff;
  color: #475467;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.sync-all-button:hover,
.sync-all-button:focus {
  border-color: #c7d2fe;
  color: #5b67ff;
  background: #fdfdff;
}

.sync-all-icon {
  width: 16px;
  height: 16px;
  margin-right: 6px;
}

.dimensions-grid-modern {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 18px;
  align-items: stretch;
}

.modern-dimension-card {
  grid-column: span 2;
  min-height: 240px;
  min-width: 0;
  display: flex;
  border-radius: 18px;
  cursor: pointer;
  animation: floatUp 0.5s ease both;
  transition: transform 0.28s ease, box-shadow 0.28s ease;
}

.modern-dimension-card:nth-child(n + 4),
.modern-dimension-card.wide {
  grid-column: span 3;
}

.modern-dimension-card:hover {
  transform: translateY(-2px);
}

.modern-dimension-card.active .modern-dimension-surface {
  box-shadow: 0 14px 30px rgba(103, 103, 190, 0.14);
}

.modern-dimension-surface {
  width: 100%;
  height: 100%;
  min-height: 0;
  border: 1px solid rgba(214, 223, 245, 0.9);
  border-radius: 18px;
  padding: 14px 14px 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  transition: box-shadow 0.28s ease, transform 0.28s ease;
}

.modern-dimension-card:hover .modern-dimension-surface {
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.09);
}

.modern-dimension-header,
.modern-dimension-heading,
.modern-dimension-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modern-dimension-header {
  gap: 10px;
  align-items: center;
  min-height: 48px;
  margin-bottom: 8px;
}

.modern-dimension-heading {
  justify-content: flex-start;
  gap: 10px;
  min-width: 0;
}

.modern-dimension-icon {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.modern-title-wrap {
  min-width: 0;
}

.modern-dimension-name {
  margin: 0 0 3px;
  font-size: 19px;
  line-height: 1.25;
  font-weight: 700;
}

.modern-dimension-subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.4;
  font-weight: 600;
}

.modern-dimension-mark {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  border: 1px solid;
  background: rgba(255, 255, 255, 0.72);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.modern-dimension-body {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: hidden;
}

.modern-dimension-copy {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 10px;
  min-width: 0;
  width: 55%;
  flex: 0 0 55%;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.modern-dimension-description {
  margin: 0;
  color: #5f6b7d;
  font-size: 14px;
  line-height: 1.6;
  min-height: 74px;
  max-height: 74px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  line-clamp: 4;
}

.modern-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 0;
  min-height: 28px;
  align-content: flex-start;
}

.modern-tag {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}

.modern-dimension-visual {
  width: 190px;
  min-width: 190px;
  height: 132px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  right: -4px;
  bottom: -2px;
  overflow: hidden;
}

.modern-dimension-image {
  width: 190px;
  height: 132px;
  object-fit: contain;
  object-position: center center;
  filter: drop-shadow(0 12px 22px rgba(15, 23, 42, 0.12));
}

.modern-dimension-footer {
  margin: auto -14px 0;
  min-height: 52px;
  padding: 10px 14px;
  border-top: 1px solid rgba(214, 221, 241, 0.68);
  gap: 10px;
  background: rgba(255, 255, 255, 0.38);
}

.modern-dimension-status {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #667085;
  font-size: 14px;
  font-weight: 600;
}

.modern-dimension-status.synced {
  color: #4f7f62;
}

.modern-dimension-status-dot {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 1.5px solid currentColor;
  position: relative;
  flex-shrink: 0;
}

.modern-dimension-status-dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: currentColor;
  transform: translate(-50%, -50%);
}

.dimension-consult-button {
  width: 118px;
  min-width: 118px;
  height: 36px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  background: linear-gradient(135deg, #7c3aed 0%, #5b67ff 100%);
  box-shadow: 0 10px 22px rgba(108, 92, 231, 0.24);
}

.modern-dimension-card.wide .modern-dimension-copy {
  width: 50%;
  flex-basis: 50%;
}

.modern-dimension-card.wide .modern-dimension-visual {
  width: 260px;
  min-width: 260px;
  height: 150px;
  right: 18px;
}

.modern-dimension-card.wide .modern-dimension-image {
  width: 260px;
  height: 150px;
}

.dimension-consult-button:hover,
.dimension-consult-button:focus {
  background: linear-gradient(135deg, #7035e8 0%, #525fff 100%);
}

@keyframes floatUp {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tips-section {
  margin-bottom: 0;
}

.tips-card {
  position: relative;
  overflow: hidden;
  padding: 28px 30px 30px;
  background:
    radial-gradient(circle at 88% 8%, rgba(124, 58, 237, 0.11), transparent 26%),
    radial-gradient(circle at 12% 10%, rgba(59, 130, 246, 0.08), transparent 30%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(247, 250, 255, 0.96));
  border-radius: 24px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
}

.tips-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 4px;
  background: linear-gradient(90deg, #5b67ff, #8b5cf6, #38bdf8);
}

.tips-header {
  max-width: 760px;
}

.tips-header h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: #1f2937;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.tips-header p {
  margin: 8px 0 0;
  color: #667085;
  font-size: 15px;
  line-height: 1.7;
}

.tips-list {
  position: relative;
  margin: 22px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.tips-list li {
  margin: 0;
  min-height: 186px;
  padding: 18px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(199, 210, 254, 0.86);
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.96));
  box-shadow: 0 14px 30px rgba(71, 85, 105, 0.055);
  display: flex;
  flex-direction: column;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.tips-list li:hover {
  transform: translateY(-3px);
  border-color: rgba(129, 140, 248, 0.9);
  box-shadow: 0 20px 38px rgba(91, 103, 255, 0.12);
}

.tips-list li:last-child {
  margin-bottom: 0;
}

.tip-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.tip-step {
  color: rgba(91, 103, 255, 0.16);
  font-size: 32px;
  line-height: 1;
  font-weight: 900;
  letter-spacing: 0;
}

.tip-dot {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #5b67ff, #8b5cf6);
  box-shadow: 0 0 0 7px rgba(91, 103, 255, 0.1);
}

.tips-list strong {
  display: block;
  margin-bottom: 10px;
  color: #344054;
  font-size: 17px;
  line-height: 1.45;
  font-weight: 800;
}

.tips-list p {
  margin: 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.75;
}

.tip-card-foot {
  margin-top: auto;
  padding-top: 16px;
}

.tip-card-foot span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 11px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.1);
  color: #5b67ff;
  font-size: 12px;
  font-weight: 800;
}

@media (max-width: 1100px) {
  .hero-main {
    flex-direction: column;
  }

  .hero-actions {
    width: 100%;
  }

  .hero-ghost-button,
  .hero-primary-button {
    flex: 1;
  }

  .hero-overview-card {
    grid-template-columns: 1fr;
  }

  .dimensions-grid-modern {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }

  .modern-dimension-card,
  .modern-dimension-card.wide {
    grid-column: span 1;
    min-height: 390px;
  }

  .modern-dimension-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .modern-dimension-visual {
    width: 180px;
    min-width: 180px;
    height: 130px;
    justify-content: center;
    align-self: center;
  }

  .video-section {
    flex-direction: column;
  }

  .video-combined-shell {
    width: 100%;
    grid-template-columns: 1fr;
  }

  .video-card,
  .video-guide-card,
  .consult-side-card {
    width: 100%;
    min-width: 0;
  }

  .consult-context-tip {
    margin-top: 18px;
  }

  .video-wrapper {
    min-height: 0;
  }

  .tips-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

}

@media (max-width: 768px) {
  .page-content {
    padding: 20px 16px 32px;
  }

  .dimensions-shell {
    padding: 18px;
    border-radius: 20px;
  }

  .dimensions-head {
    flex-direction: column;
    margin-bottom: 18px;
  }

  .dimensions-shell .section-title {
    font-size: 26px;
  }

  .dimensions-shell .section-desc {
    padding: 8px 12px;
    min-height: auto;
    line-height: 1.5;
  }

  .sync-all-button {
    width: 100%;
    justify-content: center;
  }

  .dimensions-grid-modern {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .modern-dimension-card,
  .modern-dimension-card.wide {
    grid-column: span 1;
    min-height: auto;
  }

  .modern-dimension-surface {
    min-height: 340px;
    padding: 20px 18px 16px;
  }

  .modern-dimension-description {
    min-height: 0;
  }

  .modern-dimension-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .dimension-consult-button {
    width: 100%;
  }

  .video-card,
  .video-guide-card,
  .consult-side-card {
    border-radius: 20px;
  }

  .video-combined-shell {
    padding: 16px;
    border-radius: 22px;
  }

  .video-guide-card,
  .consult-side-card {
    min-width: 0;
  }

  .video-description,
  .tips-card {
    padding: 18px;
  }

  .guide-list {
    gap: 14px;
  }

  .consult-primary-button,
  .consult-secondary-button {
    width: 100%;
  }

  .hero-section {
    padding: 18px;
    border-radius: 20px;
  }

  .hero-desc {
    font-size: 15px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-ghost-button,
  .hero-primary-button {
    width: 100%;
  }

  .overview-block {
    min-height: auto;
  }

  .tips-list {
    grid-template-columns: 1fr;
  }

  .tips-list li {
    min-height: auto;
  }

  .video-wrapper {
    height: auto;
    border-radius: 14px;
  }

}
</style>
