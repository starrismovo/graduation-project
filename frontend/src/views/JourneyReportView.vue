<template>
  <div class="report-page">
    <!-- 星空背景 -->
    <div class="stars-background">
      <div class="star" v-for="i in 50" :key="i" 
           :style="{
             left: Math.random() * 100 + '%',
             top: Math.random() * 100 + '%',
             animationDelay: Math.random() * 3 + 's'
           }"></div>
    </div>

    <div class="report-container">
      <!-- 顶部标题区 -->
      <div class="report-header">
        <div class="header-badge">✨ 探索完成</div>
        <h1 class="report-title">你的星际航行日志</h1>
        <p class="report-subtitle">{{ jobName }} · {{ completionDate }}</p>
      </div>

      <!-- 虚拟形象 + 勋章 -->
      <div class="hero-section">
        <div class="avatar-display">
          <div class="avatar-image">👤</div>
          <div class="constellation-badge">
            <div class="badge-icon">⭐</div>
            <div class="badge-text">
              <div class="badge-level">Lv.{{ constellationLevel }}</div>
              <div class="badge-name">星际探险家</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 旅程回顾 -->
      <section class="journey-review">
        <div class="section-card">
          <h2 class="section-title">🌟 旅程回顾</h2>
          <div class="review-text">
            <p>
              在【{{ jobName }}】的星际航程中，你完成了 {{ totalChapters }} 个章节的探索，
              通过 {{ totalChoices }} 次关键决策，展现了你独特的能力组合。
            </p>
            <p>
              以下是你在这段旅程中的亮点发现：
            </p>
          </div>
        </div>
      </section>

      <!-- 核心能力亮点 -->
      <section class="abilities-highlight">
        <div class="section-card">
          <h2 class="section-title">💎 核心能力亮点</h2>
          
          <div class="highlight-grid">
            <div 
              v-for="(ability, idx) in topAbilities" 
              :key="idx"
              class="highlight-card"
            >
              <div class="highlight-icon">💎</div>
              <div class="highlight-content">
                <h3 class="highlight-name">{{ ability.name }}</h3>
                <p class="highlight-desc">{{ ability.evidence }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 能力星图（雷达图） -->
      <section class="ability-radar">
        <div class="section-card">
          <h2 class="section-title">📊 能力星图</h2>
          <p class="section-desc">这是你能力的可视化展示，每个维度都反映了你在探索中的表现</p>
          
          <div class="radar-container">
            <canvas ref="radarCanvas" id="abilityRadar"></canvas>
          </div>

          <div class="ability-scores">
            <div 
              v-for="(score, ability) in abilityScores" 
              :key="ability"
              class="score-item"
            >
              <div class="score-label">{{ ability }}</div>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: score + '%' }"></div>
                <span class="score-value">{{ score }}%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 发展建议 -->
      <section class="development-suggestions">
        <div class="section-card">
          <h2 class="section-title">💡 发展建议</h2>
          
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, idx) in suggestions" 
              :key="idx"
              class="suggestion-item"
            >
              <div class="suggestion-icon">{{ suggestion.icon }}</div>
              <div class="suggestion-content">
                <h4>{{ suggestion.title }}</h4>
                <p>{{ suggestion.text }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 匹配岗位推荐 -->
      <section class="job-recommendations">
        <div class="section-card">
          <h2 class="section-title">🎯 匹配岗位推荐</h2>
          <p class="section-desc">基于你的能力星图，以下岗位可能也适合你：</p>
          
          <div class="recommendations-grid">
            <div 
              v-for="job in recommendedJobs" 
              :key="job.id"
              class="recommendation-card"
            >
              <div class="job-match-score">{{ job.matchScore }}%</div>
              <h3 class="job-name">{{ job.name }}</h3>
              <p class="job-reason">{{ job.matchReason }}</p>
              <el-button size="small" @click="exploreJob(job.id)">
                继续探索
              </el-button>
            </div>
          </div>
        </div>
      </section>

      <!-- 分享与下载 -->
      <section class="share-section">
        <div class="section-card">
          <div class="share-content">
            <div class="share-preview">
              <h3>探险家证书</h3>
              <div class="certificate-preview">
                <div class="cert-header">✨ 星际探险家证书 ✨</div>
                <div class="cert-avatar">👤</div>
                <div class="cert-name">恭喜探险家</div>
                <div class="cert-achievement">完成【{{ jobName }}】探索</div>
                <div class="cert-tags">
                  <span v-for="tag in certificateTags" :key="tag" class="cert-tag">
                    #{{ tag }}
                  </span>
                </div>
                <div class="cert-date">{{ completionDate }}</div>
                <div class="cert-level">星座等级: Lv.{{ constellationLevel }}</div>
              </div>
            </div>
            
            <div class="share-actions">
              <h3>分享你的成就</h3>
              <p>将你的探索成果分享给朋友，或下载完整报告</p>
              <div class="action-buttons">
                <el-button type="primary" @click="shareToSocial">
                  🔗 生成分享链接
                </el-button>
                <el-button @click="downloadReport">
                  📥 下载完整报告
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 继续探索 -->
      <section class="continue-section">
        <div class="section-card center">
          <h2>继续你的星际探索</h2>
          <p>每一次探索都会让你更了解自己</p>
          <div class="continue-buttons">
            <el-button type="primary" size="large" @click="goHome">
              🚀 探索更多岗位
            </el-button>
            <el-button size="large" @click="viewConstellationMap">
              🗺️ 查看我的星图
            </el-button>
          </div>
        </div>
      </section>

      <!-- 底部隐私提示 -->
      <div class="privacy-note">
        <p>🔒 你的所有数据仅用于生成个人报告，我们尊重你的隐私与选择。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Chart from 'chart.js/auto'

const router = useRouter()
const route = useRoute()

// 基础信息
const jobId = computed(() => route.params.jobId)
const jobName = ref('前端工程师')
const completionDate = ref(new Date().toLocaleDateString('zh-CN'))
const constellationLevel = ref(2)

// 探索统计
const totalChapters = ref(5)
const totalChoices = ref(12)

// 能力数据（从路由参数获取或模拟）
const abilitiesCollected = ref<any[]>([])

// 顶级能力亮点
const topAbilities = ref([
  {
    name: '危机处理专家',
    evidence: '在控制台黑屏事件中，你冷静分析问题根源，快速定位并修复，展现了出色的问题解决能力。'
  },
  {
    name: '团队协作达人',
    evidence: '你主动与后端工程师沟通，达成双赢的解决方案，体现了良好的沟通协作能力。'
  },
  {
    name: '学习成长型选手',
    evidence: '面对陌生的系统，你快速上手并提出改进建议，展现了强大的学习能力和主动性。'
  }
])

// 能力评分
const abilityScores = ref({
  '逻辑思维': 85,
  '沟通协作': 78,
  '创新能力': 90,
  '抗压能力': 81,
  '学习意愿': 88,
  '问题解决': 87
})

// 发展建议
const suggestions = ref([
  {
    icon: '🎯',
    title: '发挥你的创新优势',
    text: '你的创新能力突出（90%），适合参与前沿技术项目和产品创新。建议在简历中重点突出你的创新案例。'
  },
  {
    icon: '📈',
    title: '继续提升抗压能力',
    text: '你在高压场景中展现了81%的稳定性。可以尝试参与更多紧急项目，锻炼在压力下的决策能力。'
  },
  {
    icon: '🤝',
    title: '拓展跨团队协作经验',
    text: '你的沟通协作能力良好（78%）。建议主动参与跨部门项目，积累更多协作经验。'
  }
])

// 推荐岗位
const recommendedJobs = ref([
  {
    id: 2,
    name: '全栈工程师',
    matchScore: 89,
    matchReason: '你的逻辑思维和学习能力非常适合全栈开发的多样性挑战'
  },
  {
    id: 3,
    name: '技术 Leader',
    matchScore: 82,
    matchReason: '你的团队协作和问题解决能力使你适合带领技术团队'
  },
  {
    id: 4,
    name: '产品经理',
    matchScore: 76,
    matchReason: '你的创新思维和沟通能力可以在产品岗位上发挥价值'
  }
])

// 证书标签
const certificateTags = ref([
  '危机处理专家',
  '创新思维者',
  '团队协作达人'
])

// 雷达图
const radarCanvas = ref<HTMLCanvasElement | null>(null)

// 绘制雷达图
const drawRadarChart = () => {
  if (!radarCanvas.value) return

  const ctx = radarCanvas.value.getContext('2d')
  if (!ctx) return

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: Object.keys(abilityScores.value),
      datasets: [{
        label: '能力星图',
        data: Object.values(abilityScores.value),
        backgroundColor: 'rgba(167, 139, 250, 0.2)',
        borderColor: 'rgba(167, 139, 250, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(236, 72, 153, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(236, 72, 153, 1)'
      }]
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
            color: '#94a3b8'
          },
          grid: {
            color: 'rgba(167, 139, 250, 0.2)'
          },
          pointLabels: {
            color: '#e0e6ed',
            font: {
              size: 14,
              family: "'Space Mono', monospace"
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
}

// 探索新岗位
const exploreJob = (jobId: number) => {
  router.push(`/journey/${jobId}`)
}

// 返回首页
const goHome = () => {
  router.push('/home')
}

// 查看星图
const viewConstellationMap = () => {
  router.push('/constellation-map')
}

// 分享到社交平台
const shareToSocial = () => {
  const shareUrl = `${window.location.origin}/share/${jobId.value}`
  
  // 复制到剪贴板
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElMessage.success('分享链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 下载报告
const downloadReport = () => {
  ElMessage.info('报告下载功能开发中...')
  // 实际应该生成 PDF 或其他格式的报告
}

onMounted(() => {
  // 从路由参数获取能力数据
  if (route.query.abilities) {
    try {
      abilitiesCollected.value = JSON.parse(route.query.abilities as string)
    } catch (error) {
      console.error('解析能力数据失败:', error)
    }
  }
  
  // 绘制雷达图
  setTimeout(() => {
    drawRadarChart()
  }, 300)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');

* {
  box-sizing: border-box;
}

.report-page {
  min-height: 100vh;
  background: #0a0e27;
  color: #e0e6ed;
  position: relative;
  overflow-x: hidden;
  font-family: 'Space Mono', monospace;
}

/* 星空背景 */
.stars-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* 容器 */
.report-container {
  position: relative;
  z-index: 1;
  max-width: 1000px;
  margin: 0 auto;
  padding: 60px 20px;
}

/* 头部 */
.report-header {
  text-align: center;
  margin-bottom: 48px;
}

.header-badge {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(167, 139, 250, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  border-radius: 20px;
  font-size: 13px;
  margin-bottom: 24px;
}

.report-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 48px;
  font-weight: 900;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #a78bfa, #ec4899, #f59e0b);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.3); }
}

.report-subtitle {
  font-size: 16px;
  color: #94a3b8;
}

/* Hero 区域 */
.hero-section {
  text-align: center;
  margin-bottom: 64px;
}

.avatar-display {
  display: inline-block;
  position: relative;
}

.avatar-image {
  font-size: 120px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.constellation-badge {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  border-radius: 50px;
  box-shadow: 0 8px 30px rgba(167, 139, 250, 0.4);
}

.badge-icon {
  font-size: 32px;
}

.badge-level {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  font-weight: 700;
}

.badge-name {
  font-size: 14px;
  opacity: 0.9;
}

/* 章节卡片 */
.section-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 24px;
  padding: 40px;
  backdrop-filter: blur(20px);
  margin-bottom: 40px;
}

.section-card.center {
  text-align: center;
}

.section-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 28px;
  margin: 0 0 16px 0;
  color: #a78bfa;
}

.section-desc {
  color: #94a3b8;
  margin-bottom: 24px;
  line-height: 1.6;
}

/* 旅程回顾 */
.review-text p {
  line-height: 1.8;
  margin-bottom: 16px;
  color: #cbd5e1;
}

/* 能力亮点 */
.highlight-grid {
  display: grid;
  gap: 24px;
}

.highlight-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 16px;
  border-left: 4px solid #a78bfa;
  transition: all 0.3s ease;
}

.highlight-card:hover {
  background: rgba(167, 139, 250, 0.1);
  transform: translateX(8px);
}

.highlight-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.highlight-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  color: #a78bfa;
  margin: 0 0 12px 0;
}

.highlight-desc {
  line-height: 1.6;
  color: #cbd5e1;
  margin: 0;
}

/* 雷达图 */
.radar-container {
  max-width: 600px;
  margin: 0 auto 32px;
  padding: 32px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 16px;
}

#abilityRadar {
  max-height: 400px;
}

.ability-scores {
  display: grid;
  gap: 16px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-label {
  width: 120px;
  font-weight: 600;
  color: #e0e6ed;
}

.score-bar {
  flex: 1;
  height: 32px;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #ec4899);
  border-radius: 16px;
  transition: width 1s ease;
}

.score-value {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: 700;
  font-size: 14px;
}

/* 发展建议 */
.suggestions-list {
  display: grid;
  gap: 20px;
}

.suggestion-item {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 16px;
  border-left: 4px solid #ec4899;
}

.suggestion-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.suggestion-content h4 {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  color: #ec4899;
  margin: 0 0 8px 0;
}

.suggestion-content p {
  line-height: 1.6;
  color: #cbd5e1;
  margin: 0;
}

/* 岗位推荐 */
.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.recommendation-card {
  padding: 24px;
  background: rgba(15, 23, 42, 0.4);
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  border-color: rgba(167, 139, 250, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(167, 139, 250, 0.3);
}

.job-match-score {
  display: inline-block;
  padding: 8px 20px;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  border-radius: 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
}

.job-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  margin: 0 0 12px 0;
  color: #e0e6ed;
}

.job-reason {
  color: #94a3b8;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

/* 分享区域 */
.share-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}

.share-preview h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  margin-bottom: 20px;
  color: #a78bfa;
}

.certificate-preview {
  padding: 32px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(236, 72, 153, 0.1));
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  text-align: center;
}

.cert-header {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  margin-bottom: 20px;
  color: #a78bfa;
}

.cert-avatar {
  font-size: 64px;
  margin-bottom: 16px;
}

.cert-name {
  font-size: 16px;
  margin-bottom: 8px;
  color: #e0e6ed;
}

.cert-achievement {
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  margin-bottom: 16px;
  color: #ec4899;
}

.cert-tags {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.cert-tag {
  padding: 4px 12px;
  background: rgba(167, 139, 250, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  border-radius: 12px;
  font-size: 11px;
}

.cert-date,
.cert-level {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.share-actions h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  margin-bottom: 12px;
  color: #a78bfa;
}

.share-actions p {
  color: #94a3b8;
  margin-bottom: 24px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-buttons button {
  width: 100%;
}

/* 继续探索 */
.continue-section h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  margin-bottom: 12px;
  color: #e0e6ed;
}

.continue-section p {
  color: #94a3b8;
  margin-bottom: 32px;
}

.continue-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 隐私提示 */
.privacy-note {
  text-align: center;
  padding: 24px;
  color: #94a3b8;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .report-title {
    font-size: 32px;
  }
  
  .section-card {
    padding: 24px;
  }
  
  .share-content {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .continue-buttons {
    flex-direction: column;
  }
  
  .continue-buttons button {
    width: 100%;
  }
}
</style>
