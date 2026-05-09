<script setup lang="ts">
import { ref } from 'vue'

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
  // TODO: 接入现有 AI 咨询入口时，在此处携带维度上下文进入咨询流程。
}

const handleSyncAllToConsult = () => {
  syncedDimensionIndexes.value = personalityDimensions.map((_, idx) => idx)
  // TODO: 接入现有 AI 咨询入口时，在此处同步全部维度上下文。
}

</script>

<template>
  <div class="psychology-detail-page">
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
              并给出职业发展与行动建议，让自我认知转化为成长动力。
            </p>
          </div>

          <div class="hero-actions">
            <button class="hero-ghost-button" type="button" @click="handleConsultDimension(activeDimension)">
              生成咨询问题
            </button>
            <button class="hero-primary-button" type="button" @click="handleSyncAllToConsult">
              立即 AI 咨询
            </button>
          </div>
        </div>

        <div class="hero-overview-card">
          <div class="overview-block">
            <span class="overview-label">总体概览</span>
            <p>你的整体人格特征均衡，兼具探索精神与责任感，在人际互动中表现友好，同时保持较为稳定的情绪状态。</p>
            <div class="overview-score">
              <span>综合评分</span>
              <strong>86</strong>
              <small>/100</small>
            </div>
          </div>

          <div class="overview-block">
            <span class="overview-label">高突出的特质</span>
            <div class="overview-tags">
              <span>责任心强</span>
              <span>情绪稳定</span>
              <span>乐于协作</span>
            </div>
          </div>

          <div class="overview-block">
            <span class="overview-label">成长建议</span>
            <p>可在保持稳定优势的基础上，适度突破舒适区，增强表达影响力与创新尝试。</p>
            <span class="overview-update">更新于 2026-05-08</span>
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
            preload="metadata"
            class="video-element"
          ></video>
          </div>
        </div>

        <div class="video-description video-guide-card">
          <div class="video-guide-head">
            <span class="video-guide-accent"></span>
            <div>
              <h2>先看视频，重点解读</h2>
              <p>通过更短的路径建立整体认知，再进入五维细化分析与追问。</p>
            </div>
          </div>

          <div class="guide-list">
            <div class="guide-item">
              <span class="guide-icon guide-icon--blue">1</span>
              <div class="guide-copy">
                <h3>先整体，后细节</h3>
                <p>快速了解大五人格的核心含义与整体画像，先建立统一理解框架。</p>
              </div>
            </div>

            <div class="guide-item">
              <span class="guide-icon guide-icon--violet">2</span>
              <div class="guide-copy">
                <h3>基于你的结果解读</h3>
                <p>结合评估结果，理解各维度在岗位匹配、行为风格与成长方向上的表现。</p>
              </div>
            </div>

            <div class="guide-item">
              <span class="guide-icon guide-icon--green">3</span>
              <div class="guide-copy">
                <h3>一看就懂，可追问</h3>
                <p>看完即可进入 AI 咨询，将人格维度与后续职业发展建议串联起来。</p>
              </div>
            </div>
          </div>

          <button class="guide-action-button" type="button" @click="handleConsultDimension(activeDimension)">
            标记已看完，展开详细解读
          </button>
        </div>
        </div>

        <div class="consult-side-card">
          <div class="consult-side-top">
            <div>
              <div class="consult-side-badge">AI 职业咨询师</div>
              <div class="consult-side-status">
                <span class="consult-status-dot"></span>
                <span>在线</span>
              </div>
            </div>
            <button class="consult-more" type="button" aria-label="更多操作">...</button>
          </div>

          <div class="consult-avatar-panel">
            <div class="consult-avatar-shell">
              <svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" class="consult-bot">
                <defs>
                  <linearGradient id="consultBotGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#7c3aed" />
                    <stop offset="100%" stop-color="#5b67ff" />
                  </linearGradient>
                </defs>
                <rect x="26" y="26" width="68" height="48" rx="22" fill="url(#consultBotGrad)" />
                <rect x="36" y="36" width="48" height="28" rx="14" fill="#ffffff" opacity="0.95" />
                <circle cx="51" cy="50" r="5" fill="#5b67ff" />
                <circle cx="69" cy="50" r="5" fill="#5b67ff" />
                <path d="M49 61Q60 68 71 61" stroke="#5b67ff" stroke-width="4" fill="none" stroke-linecap="round" />
                <path d="M60 26V18" stroke="#8b5cf6" stroke-width="5" stroke-linecap="round" />
                <rect x="49" y="10" width="22" height="10" rx="5" fill="#d9d6fe" />
                <circle cx="27" cy="88" r="10" fill="#dbeafe" />
                <circle cx="93" cy="88" r="10" fill="#e9d5ff" />
              </svg>
            </div>
          </div>

          <p class="consult-side-desc">
            基于你的心理画像与岗位匹配结果，继续提炼咨询问题，获得更有针对性的建议。
          </p>

          <div class="consult-side-actions">
            <button class="consult-primary-button" type="button" @click="handleConsultDimension(activeDimension)">
              开始咨询
            </button>
            <button class="consult-secondary-button" type="button" @click="handleSyncAllToConsult">
              同步到首页咨询
            </button>
            <button class="consult-secondary-button" type="button">
              查看咨询记录
            </button>
          </div>

          <div class="consult-context-tip">
            <span class="consult-context-icon"></span>
            <span>已同步 {{ syncedDimensionIndexes.length }} 个维度追问上下文</span>
          </div>
        </div>
      </div>

      <div class="dimensions-section">
        <div class="dimensions-shell">
          <div class="dimensions-head">
            <div class="dimensions-head-copy">
              <h2 class="section-title">五维解读卡片</h2>
              <p class="section-desc">每个维度均可发起追问，获取更深入的个性化建议</p>
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
              全部同步到咨询
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
                      <h3 class="modern-dimension-name" :style="{ color: dim.palette.title }">{{ dimensionDisplayMeta[idx].title }}</h3>
                      <p class="modern-dimension-subtitle">{{ dimensionDisplayMeta[idx].english }}</p>
                    </div>
                  </div>

                  <span class="modern-dimension-mark" :style="{ color: dim.palette.title, borderColor: dim.palette.border }">
                    {{ dimensionDisplayMeta[idx].statusIcon }}
                  </span>
                </div>

                <div class="modern-dimension-body">
                  <div class="modern-dimension-copy">
                    <p class="modern-dimension-description">{{ dimensionDisplayMeta[idx].summary }}</p>

                    <div class="modern-tag-list">
                      <span
                        v-for="tag in dimensionDisplayMeta[idx].tags"
                        :key="tag"
                        class="modern-tag"
                        :style="{ background: dim.palette.chip, color: dim.palette.title }"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </div>

                  <div class="modern-dimension-visual">
                    <img :src="dim.image" :alt="dimensionDisplayMeta[idx].title" class="modern-dimension-image" loading="lazy" />
                  </div>
                </div>

                <div class="modern-dimension-footer">
                  <div class="modern-dimension-status" :class="{ synced: isDimensionSynced(idx) }">
                    <span class="modern-dimension-status-dot"></span>
                    <span>{{ isDimensionSynced(idx) ? '已同步咨询上下文' : '可发起追问' }}</span>
                  </div>

                  <el-button
                    class="dimension-consult-button"
                    size="small"
                    type="primary"
                    @click.stop="handleConsultDimension(idx)"
                  >
                    咨询该维度
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
            <li>
              <strong>自我认知</strong>：先找出你的高分和低分维度，理解“自然偏好”与“压力反应”
            </li>
            <li>
              <strong>岗位匹配</strong>：将人格倾向与岗位要求对照，优先选择优势能够被放大的场景
            </li>
            <li>
              <strong>人际协作</strong>：把“你习惯怎么做”明确告诉团队，降低沟通误差
            </li>
            <li>
              <strong>成长策略</strong>：为每个低分维度设定一个可执行的小目标，并按周复盘
            </li>
            <li>
              <strong>动态更新</strong>：每隔一段时间复测一次，关注趋势变化而非单次分数
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
  font-size: 12px;
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
  font-size: 12px;
  font-weight: 800;
}

.hero-desc {
  margin: 12px 0 0;
  max-width: 820px;
  font-size: 15px;
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
  font-size: 14px;
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
  font-size: 13px;
  font-weight: 800;
}

.overview-block p {
  margin: 0;
  color: #667085;
  font-size: 13px;
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
  font-size: 12px;
  font-weight: 700;
}

.overview-score strong {
  color: #4f46e5;
  font-size: 22px;
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
  font-size: 12px;
  font-weight: 700;
}

.overview-update {
  display: inline-block;
  margin-top: 14px;
  color: #98a2b3;
  font-size: 12px;
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
  border-radius: 24px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.video-card {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  background:
    radial-gradient(circle at 88% 18%, rgba(139, 92, 246, 0.14), transparent 28%),
    linear-gradient(180deg, rgba(241, 245, 255, 0.98), rgba(255, 255, 255, 0.98));
  display: flex;
  flex-direction: column;
  align-self: stretch;
}

.video-card-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  margin-bottom: 10px;
  background: rgba(124, 58, 237, 0.12);
  color: #7c3aed;
  font-size: 12px;
  font-weight: 700;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: 16px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.18);
}

.video-element {
  display: block;
  width: 100%;
  height: 100%;
  background: #000;
}

.video-description {
  padding: 24px 22px;
  border-radius: 24px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.94));
}

.video-description h2 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.video-description p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #667085;
  line-height: 1.75;
}

.video-description p:last-child {
  margin-bottom: 0;
}

.video-guide-card {
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 22px 20px 18px;
  height: 100%;
  min-height: 0;
  border: none;
  box-shadow: none;
  align-self: stretch;
  overflow: hidden;
}

.video-guide-head {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 20px;
}

.video-guide-accent {
  width: 4px;
  min-height: 44px;
  border-radius: 999px;
  background: linear-gradient(180deg, #7c3aed, #5b67ff);
  flex-shrink: 0;
}

.video-guide-head p {
  margin: 6px 0 0;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 18px;
  flex: 1;
  min-height: 0;
}

.guide-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.guide-icon {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 700;
}

.guide-icon--blue {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

.guide-icon--violet {
  background: rgba(124, 58, 237, 0.12);
  color: #7c3aed;
}

.guide-icon--green {
  background: rgba(34, 197, 94, 0.12);
  color: #16a34a;
}

.guide-copy h3 {
  margin: 0 0 6px;
  font-size: 14px;
  line-height: 1.4;
  color: #344054;
  font-weight: 700;
}

.guide-copy p {
  margin: 0;
  font-size: 12px;
  line-height: 1.68;
}

.guide-action-button {
  margin-top: 4px;
  flex-shrink: 0;
  width: 100%;
  height: 42px;
  border: 1px solid rgba(199, 210, 254, 0.96);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(245, 247, 255, 0.98));
  color: #6366f1;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.24s ease;
}

.guide-action-button:hover {
  border-color: #a5b4fc;
  background: #ffffff;
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
  font-size: 18px;
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
  font-size: 13px;
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
  border-radius: 20px;
  background:
    radial-gradient(circle at 50% 46%, rgba(91, 103, 255, 0.2), transparent 32%),
    linear-gradient(180deg, rgba(237, 233, 254, 0.88), rgba(248, 250, 255, 0.98));
  min-height: 190px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.consult-avatar-shell {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.consult-bot {
  width: 100%;
  max-width: 168px;
  height: auto;
  filter: drop-shadow(0 18px 26px rgba(91, 103, 255, 0.16));
}

.consult-side-desc {
  margin: 16px 0 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.8;
  min-height: 72px;
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
  font-size: 14px;
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
  font-size: 12px;
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
  padding: 24px;
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
  margin-bottom: 22px;
}

.dimensions-head-copy {
  min-width: 0;
}

.dimensions-shell .section-title {
  margin: 0 0 6px 0;
  font-size: 26px;
  line-height: 1.2;
  font-weight: 700;
  color: #1f2937;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.dimensions-shell .section-desc {
  margin: 0;
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.08);
  color: #7c86a2;
  font-size: 13px;
  font-weight: 600;
}

.sync-all-button {
  min-height: 42px;
  padding: 0 16px;
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
  gap: 20px;
  align-items: stretch;
}

.modern-dimension-card {
  grid-column: span 2;
  min-height: 330px;
  min-width: 0;
  display: flex;
  border-radius: 22px;
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
  box-shadow: 0 18px 38px rgba(103, 103, 190, 0.16);
}

.modern-dimension-surface {
  width: 100%;
  height: 100%;
  min-height: 0;
  border: 1px solid rgba(214, 223, 245, 0.9);
  border-radius: 22px;
  padding: 18px 18px 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.07);
  transition: box-shadow 0.28s ease, transform 0.28s ease;
}

.modern-dimension-card:hover .modern-dimension-surface {
  box-shadow: 0 18px 34px rgba(15, 23, 42, 0.1);
}

.modern-dimension-header,
.modern-dimension-heading,
.modern-dimension-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modern-dimension-header {
  gap: 12px;
  align-items: center;
  min-height: 50px;
  margin-bottom: 12px;
}

.modern-dimension-heading {
  justify-content: flex-start;
  gap: 12px;
  min-width: 0;
}

.modern-dimension-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.modern-title-wrap {
  min-width: 0;
}

.modern-dimension-name {
  margin: 0 0 4px;
  font-size: 18px;
  line-height: 1.25;
  font-weight: 700;
}

.modern-dimension-subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.4;
  font-weight: 600;
}

.modern-dimension-mark {
  width: 34px;
  height: 34px;
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
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  flex: 1;
  min-height: 0;
}

.modern-dimension-copy {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 12px;
  min-width: 0;
  flex: 1;
  min-height: 0;
}

.modern-dimension-description {
  margin: 0;
  color: #5f6b7d;
  font-size: 13px;
  line-height: 1.68;
  min-height: 90px;
  max-height: 90px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  line-clamp: 4;
}

.modern-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
  min-height: 62px;
  align-content: flex-start;
}

.modern-tag {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}

.modern-dimension-visual {
  width: 142px;
  min-width: 142px;
  height: 104px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  align-self: center;
  overflow: hidden;
}

.modern-dimension-image {
  width: 142px;
  height: 104px;
  object-fit: contain;
  object-position: center center;
  filter: drop-shadow(0 14px 28px rgba(15, 23, 42, 0.12));
}

.modern-dimension-footer {
  margin-top: auto;
  min-height: 48px;
  padding-top: 12px;
  border-top: 1px solid rgba(214, 221, 241, 0.68);
  gap: 12px;
}

.modern-dimension-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #667085;
  font-size: 13px;
  font-weight: 600;
}

.modern-dimension-status.synced {
  color: #4f7f62;
}

.modern-dimension-status-dot {
  width: 18px;
  height: 18px;
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
  width: 112px;
  min-width: 112px;
  height: 34px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #7c3aed 0%, #5b67ff 100%);
  box-shadow: 0 10px 22px rgba(108, 92, 231, 0.24);
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
  padding: 24px;
  background:
    radial-gradient(circle at 12% 10%, rgba(59, 130, 246, 0.08), transparent 30%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(247, 250, 255, 0.96));
  border-radius: 24px;
  border: 1px solid rgba(224, 231, 255, 0.96);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
}

.tips-header h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #1f2937;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.tips-header p {
  margin: 8px 0 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.7;
}

.tips-list {
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.tips-list li {
  margin: 0;
  min-height: 128px;
  padding: 18px 16px 16px 44px;
  position: relative;
  font-size: 14px;
  color: #667085;
  line-height: 1.68;
  border: 1px solid rgba(224, 231, 255, 0.96);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.tips-list li:before {
  content: '';
  position: absolute;
  left: 16px;
  top: 20px;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 4px solid rgba(99, 102, 241, 0.16);
  background: #6366f1;
  box-sizing: border-box;
}

.tips-list li:last-child {
  margin-bottom: 0;
}

.tips-list strong {
  display: block;
  margin-bottom: 6px;
  color: #344054;
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
    min-height: 360px;
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

  .guide-action-button,
  .consult-primary-button,
  .consult-secondary-button {
    width: 100%;
  }

  .hero-section {
    padding: 18px;
    border-radius: 20px;
  }

  .hero-desc {
    font-size: 14px;
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
    height: 260px;
    border-radius: 14px;
  }

}
</style>
