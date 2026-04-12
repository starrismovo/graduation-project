<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()

// 大五人格维度解释
const personalityDimensions = [
  {
    name: '开放性 (Openness)',
    subtitle: '对新体验与新观点的接纳程度',
    description: '开放性高的人更容易被新鲜事物激发灵感，喜欢探索、创作和表达。开放性较低的人更重视稳定与秩序，偏好已验证的方案。',
    icon: '🎨',
    image: '/开放性.jpg',
    highExamples: ['画画、写作、尝试新菜', '愿意体验陌生场景', '对艺术和创意活动感兴趣'],
    lowExamples: ['更偏好熟悉流程', '对变化持谨慎态度', '习惯按既有规则执行'],
    palette: {
      bg: '#ece9ff',
      border: '#c7bffd',
      title: '#5a60c9',
      chip: '#ded7ff'
    }
  },
  {
    name: '尽责性 (Conscientiousness)',
    subtitle: '自律、计划性与目标执行能力',
    description: '尽责性高的人通常做事有条理、行动稳定，能持续推进任务并按时交付。尽责性较低的人更随性灵活，但可能受情绪和环境影响较大。',
    icon: '📚',
    image: '/尽责性.jpg',
    highExamples: ['会提前规划任务顺序', '较少拖延，注重兑现承诺', '做事重细节和完成质量'],
    lowExamples: ['容易边做边改方向', '短期冲劲强但持续性波动', '可能忽略流程和复盘'],
    palette: {
      bg: '#e9efdf',
      border: '#c0cc9a',
      title: '#6f8440',
      chip: '#dce8bd'
    }
  },
  {
    name: '外向性 (Extraversion)',
    subtitle: '社交活力、表达欲与行动能量',
    description: '外向性高的人在社交场景中更容易启动互动，喜欢直接表达观点以及主动带动气氛。外向性较低的人更偏向深度独处与安静思考。',
    icon: '🎤',
    image: '/外向性.jpg',
    highExamples: ['更愿意主动发言和组织活动', '从人群互动中获得能量', '倾向快速表达想法'],
    lowExamples: ['偏好小范围深度交流', '社交后需要安静恢复', '先观察再表达'],
    palette: {
      bg: '#efe4d4',
      border: '#d9b98d',
      title: '#6d3018',
      chip: '#edd7b8'
    }
  },
  {
    name: '友好性 (Agreeableness)',
    subtitle: '合作倾向、同理心与关系敏感度',
    description: '友好性高的人更关注关系质量，善于体察他人感受并促进合作。友好性较低的人更强调边界和效率，在冲突场景中更直接。',
    icon: '💞',
    image: '/宜人性.jpg',
    highExamples: ['重视团队和谐与互助', '愿意站在对方立场思考', '冲突中倾向协商'],
    lowExamples: ['更强调原则与结果', '表达方式更直接', '在竞争情境中更果断'],
    palette: {
      bg: '#f4e0d2',
      border: '#e3b5a1',
      title: '#c46e4a',
      chip: '#efd3c6'
    }
  },
  {
    name: '神经质/情绪稳定性 (Neuroticism/Emotional Stability)',
    subtitle: '面对压力时的情绪波动与恢复能力',
    description: '神经质较高的人对压力线索更敏感，情绪体验更强烈；情绪稳定性较高的人更能保持平衡并快速恢复。关键不在“好坏”，而在认识与调节。',
    icon: '🌊',
    image: '/神经质.jpg',
    highExamples: ['容易提前担心潜在风险', '压力来临时情绪起伏更明显', '对反馈和关系变化更敏感'],
    lowExamples: ['遇事更容易保持平和', '能较快从挫折中恢复', '对压力刺激的耐受更高'],
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

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="psychology-detail-page">
    <div class="page-content">
      <section class="hero-section">
        <p class="hero-tag">Big Five Personality Guide</p>
        <h1 class="hero-title">大五人格心理解读</h1>
        <p class="hero-desc">
          参考插画海报的视觉语言，我们把“人格概念”转成了更直观的日常场景提示。
          你可以先看视频，再通过下方卡片理解每个维度在生活中的常见表现。
        </p>
      </section>

      <div class="video-section">
        <div class="video-wrapper">
          <video
            :src="videoUrl"
            controls
            controlsList="nodownload"
            preload="metadata"
            class="video-element"
          ></video>
        </div>

        <div class="video-description">
          <h2>先看视频，建立整体认知</h2>
          <p>
            大五人格模型通过五个维度描述个体的稳定倾向，它并不用于“贴标签”，而是帮助你更准确地理解自己的行为偏好。
          </p>
          <p>
            建议结合你的评估报告一起阅读本页内容：先看维度定义，再看高低分常见表现，最后回到岗位匹配做行动决策。
          </p>
        </div>
      </div>

      <div class="dimensions-section">
        <h2 class="section-title">五维度解读卡片</h2>
        <p class="section-desc">点击卡片切换聚焦，快速浏览每个维度在生活中的典型信号</p>

        <div class="feature-illustration">
          <img
            :src="personalityDimensions[activeDimension].image"
            :alt="personalityDimensions[activeDimension].name"
            class="feature-illustration-image"
          />
          <div class="feature-illustration-meta">
            <p class="feature-illustration-label">当前聚焦维度</p>
            <h3 class="feature-illustration-title">{{ personalityDimensions[activeDimension].name }}</h3>
          </div>
        </div>

        <div class="dimensions-grid">
          <div
            v-for="(dim, idx) in personalityDimensions"
            :key="idx"
            class="dimension-card"
            :class="{ active: activeDimension === idx }"
            :style="{ animationDelay: idx * 80 + 'ms' }"
            @click="activeDimension = idx"
          >
            <div
              class="card-main"
              :style="{
                background: dim.palette.bg,
                borderColor: dim.palette.border
              }"
            >
              <div class="card-header">
                <span class="dimension-icon" :style="{ background: dim.palette.chip }">{{ dim.icon }}</span>
                <div class="title-wrap">
                  <h3 class="dimension-name" :style="{ color: dim.palette.title }">{{ dim.name }}</h3>
                  <p class="dimension-subtitle">{{ dim.subtitle }}</p>
                </div>
              </div>
              <p class="dimension-description">{{ dim.description }}</p>

              <div class="dimension-illustration-wrap">
                <img :src="dim.image" :alt="dim.name" class="dimension-illustration" loading="lazy" />
              </div>

              <div class="card-examples">
                <div class="example-group">
                  <p class="example-title">高分常见表现</p>
                  <div class="chips-wrap">
                    <span v-for="item in dim.highExamples" :key="item" class="example-chip">
                      {{ item }}
                    </span>
                  </div>
                </div>

                <div class="example-group">
                  <p class="example-title">低分常见表现</p>
                  <div class="chips-wrap">
                    <span v-for="item in dim.lowExamples" :key="item" class="example-chip muted">
                      {{ item }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tips-section">
        <div class="tips-card">
          <div class="tips-header">
            <h3>如何把评估结果用于行动</h3>
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

      <div class="bottom-actions">
        <el-button size="large" @click="goBack">返回首页查看评估结果</el-button>
        <el-button type="primary" size="large" @click="$router.push('/home')">
          <svg class="inline-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
          </svg>
          回到首页
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.psychology-detail-page {
  background:
    radial-gradient(circle at 12% 10%, rgba(87, 118, 147, 0.14) 0, rgba(87, 118, 147, 0) 24%),
    radial-gradient(circle at 88% 24%, rgba(196, 110, 74, 0.16) 0, rgba(196, 110, 74, 0) 26%),
    linear-gradient(160deg, #f7f4ec 0%, #eef2f3 55%, #f2ede5 100%);
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 32px 24px;
  max-width: 1240px;
  margin: 0 auto;
  width: 100%;
}

.hero-section {
  margin-bottom: 26px;
  border: 1px solid rgba(108, 88, 63, 0.2);
  border-radius: 18px;
  padding: 22px 24px;
  background: rgba(255, 252, 246, 0.84);
  backdrop-filter: blur(3px);
}

.hero-tag {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #7d684b;
  text-transform: uppercase;
}

.hero-title {
  margin: 0 0 10px;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.06;
  font-weight: 800;
  color: #4f3929;
  font-family: 'ZCOOL KuaiLe', 'YouYuan', 'STKaiti', 'KaiTi', serif;
}

.hero-desc {
  margin: 0;
  max-width: 820px;
  font-size: 15px;
  line-height: 1.8;
  color: #5b4f42;
}

.video-section {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  gap: 20px;
  margin-bottom: 48px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  min-height: 320px;
  border-radius: 16px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: 0 12px 28px rgba(73, 54, 34, 0.16);
}

.video-element {
  display: block;
  width: 100%;
  height: 100%;
  background: #000;
}

.video-description {
  padding: 24px;
  border-radius: 16px;
  border: 1px dashed rgba(93, 72, 43, 0.35);
  background: rgba(255, 248, 238, 0.92);
}

.video-description h2 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 700;
  color: #5f3f26;
  font-family: 'ZCOOL KuaiLe', 'YouYuan', 'STKaiti', 'KaiTi', serif;
}

.video-description p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #624f40;
  line-height: 1.8;
}

.video-description p:last-child {
  margin-bottom: 0;
}

.video-description strong {
  color: #825a3a;
  font-weight: 600;
}

.dimensions-section {
  margin-bottom: 48px;
}

.section-title {
  margin: 0 0 6px 0;
  font-size: clamp(24px, 3.1vw, 34px);
  line-height: 1.15;
  font-weight: 800;
  color: #4f3929;
  font-family: 'ZCOOL KuaiLe', 'YouYuan', 'STKaiti', 'KaiTi', serif;
}

.section-desc {
  margin: 0 0 24px 0;
  font-size: 14px;
  color: #6d6050;
}

.feature-illustration {
  margin-bottom: 22px;
  background: rgba(255, 248, 238, 0.88);
  border: 1px dashed rgba(93, 71, 41, 0.3);
  border-radius: 16px;
  padding: 12px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.55fr);
  gap: 12px;
  align-items: center;
}

.feature-illustration-image {
  width: 100%;
  max-height: 420px;
  object-fit: contain;
  object-position: center;
  border-radius: 12px;
  border: 1px solid rgba(93, 71, 41, 0.2);
  box-shadow: 0 10px 26px rgba(93, 71, 41, 0.12);
  background: #f8f6f2;
}

.feature-illustration-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

.feature-illustration-label {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #7f6a4f;
  text-transform: uppercase;
}

.feature-illustration-title {
  margin: 0;
  font-size: 22px;
  line-height: 1.2;
  color: #5a3d26;
  font-family: 'ZCOOL KuaiLe', 'YouYuan', 'STKaiti', 'KaiTi', serif;
}

.dimensions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.dimension-card {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(108, 88, 63, 0.12);
  transition: all 0.3s ease;
  animation: floatUp 0.5s ease both;
}

.card-main {
  height: 100%;
  border: 1px solid;
  border-radius: 16px;
  padding: 18px;
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

.dimension-card:hover {
  transform: translateY(-4px) rotate(-0.2deg);
  box-shadow: 0 12px 30px rgba(93, 71, 41, 0.16);
}

.dimension-card.active {
  transform: translateY(-4px);
  box-shadow: 0 14px 32px rgba(93, 71, 41, 0.2);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.dimension-icon {
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  flex-shrink: 0;
}

.title-wrap {
  min-width: 0;
}

.dimension-name {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  line-height: 1.25;
}

.dimension-subtitle {
  margin: 3px 0 0;
  color: #6a5b4b;
  font-size: 12px;
}

.dimension-description {
  margin: 0;
  font-size: 13px;
  color: #5f5448;
  line-height: 1.75;
}

.dimension-illustration-wrap {
  margin-top: 12px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(93, 71, 41, 0.2);
  background: rgba(248, 246, 242, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
}

.dimension-illustration {
  display: block;
  width: 100%;
  height: 100%;
  max-height: 320px;
  object-fit: contain;
  object-position: center;
}

.card-examples {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.example-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-title {
  margin: 0;
  font-size: 12px;
  color: #685949;
  font-weight: 700;
}

.chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-chip {
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1.35;
  color: #503d2e;
  background: rgba(255, 250, 242, 0.88);
  border: 1px solid rgba(80, 61, 46, 0.18);
}

.example-chip.muted {
  background: rgba(255, 255, 255, 0.58);
  color: #6c5c4e;
}

.tips-section {
  margin-bottom: 32px;
}

.tips-card {
  padding: 28px;
  background: linear-gradient(130deg, #f6ebe0 0%, #f8f3ec 100%);
  border-radius: 16px;
  border: 1px dashed rgba(93, 71, 41, 0.3);
}

.tips-header h3 {
  margin: 0 0 16px 0;
  font-size: 24px;
  font-weight: 800;
  color: #5f3f26;
  font-family: 'ZCOOL KuaiLe', 'YouYuan', 'STKaiti', 'KaiTi', serif;
}

.tips-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tips-list li {
  margin-bottom: 14px;
  padding-left: 28px;
  position: relative;
  font-size: 14px;
  color: #5b4c3d;
  line-height: 1.7;
}

.tips-list li:before {
  content: '●';
  position: absolute;
  left: 0;
  color: #7f5a3a;
  font-weight: 700;
  font-size: 10px;
  top: 7px;
}

.tips-list li:last-child {
  margin-bottom: 0;
}

.tips-list strong {
  color: #7b4a2e;
  font-weight: 600;
}

.bottom-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px dashed rgba(93, 71, 41, 0.24);
}

.bottom-actions :deep(.el-button) {
  min-width: 160px;
}

.inline-icon {
  width: 18px;
  height: 18px;
  margin-right: 6px;
}

@media (max-width: 1100px) {
  .video-section {
    grid-template-columns: 1fr;
  }

  .video-wrapper {
    min-height: 280px;
  }

  .feature-illustration {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 20px 16px;
  }

  .hero-section {
    padding: 16px;
    border-radius: 14px;
  }

  .hero-desc {
    font-size: 14px;
  }

  .dim-tabs {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .dim-tab {
    flex: 1 1 calc(50% - 8px);
    min-width: 140px;
    transform: none !important;
  }

  .dim-detail-top {
    grid-template-columns: 1fr;
  }

  .video-wrapper {
    min-height: 220px;
    border-radius: 14px;
  }

  .video-description,
  .tips-card {
    padding: 18px;
  }

  .bottom-actions {
    flex-direction: column;
  }

  .bottom-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
