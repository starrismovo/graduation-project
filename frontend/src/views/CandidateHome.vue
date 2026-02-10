<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ref, onMounted, computed } from 'vue'
import { getHomePageData, startInterview } from '../utils/request'

const userStore = useUserStore()
const router = useRouter()

// 搜索关键词
const searchKeyword = ref('')

// 筛选条件
const filters = ref({
  category: '', // 职业方向
  style: '' // 探索风格（替代传统筛选）
})

// 探索进度数据
const explorationProgress = ref({
  journeys_started: 0, // 已开始的探索
  journeys_completed: 0, // 已完成的探索
  abilities_discovered: 0, // 已发现的能力
  constellation_level: 1 // 星座等级（基于完成度）
})

// 热门岗位（星系）列表
const galaxyJobs = ref<any[]>([])

// 加载状态
const loading = ref(true)

// 是否已创建虚拟形象
const hasAvatar = ref(false)

// 加载主页数据
const loadHomeData = async () => {
  try {
    loading.value = true
    const response = await getHomePageData({
      category: filters.value.category || undefined,
      search: searchKeyword.value || undefined
    })
    
    const data = response.data
    
    // 转换后端数据到探索进度
    explorationProgress.value = {
      journeys_started: data.stats?.in_progress || 0,
      journeys_completed: data.stats?.completed || 0,
      abilities_discovered: Math.min((data.stats?.completed || 0) * 3, 15), // 每完成一次探索发现3个能力
      constellation_level: Math.floor((data.stats?.completed || 0) / 3) + 1 // 每3次探索提升1级
    }
    
    galaxyJobs.value = data.recommended_jobs || []
    
    // 检查用户是否有虚拟形象（从用户信息或本地存储）
    hasAvatar.value = localStorage.getItem('userAvatar') !== null
  } catch (error: any) {
    console.error('加载探索数据失败:', error)
    
    if (error.message?.includes('timeout')) {
      ElMessage.error('星海连接超时，请稍后再试')
    } else if (!error.response) {
      ElMessage.error('无法连接到星海导航系统')
    } else {
      ElMessage.error('加载失败，请刷新重试')
    }
  } finally {
    loading.value = false
  }
}

// 搜索岗位
const onSearch = () => {
  loadHomeData()
}

// 开始探索某个岗位
const startJourney = async (job: any) => {
  // 如果还没创建虚拟形象，先引导创建
  if (!hasAvatar.value) {
    ElMessage({
      message: '开始探索前，让我们先创建你的星际探险家形象',
      type: 'info',
      duration: 3000
    })
    router.push('/avatar-creator')
    return
  }
  
  try {
    const response = await startInterview(job.id)
    const interviewId = response?.data?.id ?? job.id
    
    ElMessage.success(`🚀 准备进入${job.name}的星际航程...`)
    
    // 跳转到故事场景页面
    setTimeout(() => {
      router.push(`/journey/${interviewId}`)
    }, 1500)
  } catch (error: any) {
    console.error('启动探索失败:', error)
    ElMessage.warning('星海导航暂时不可用，进入本地探索模式')
    router.push(`/journey/${job.id}`)
  }
}

// 快速探索（随机推荐）
const quickExplore = async () => {
  if (galaxyJobs.value.length === 0) {
    ElMessage.info('正在准备你的专属探索路线...')
    router.push('/journey/demo')
    return
  }
  
  // 过滤未完成的岗位
  const availableJobs = galaxyJobs.value.filter(job => !job.applied)
  if (availableJobs.length === 0) {
    ElMessage.warning('你已探索完所有星系！查看你的星图了解更多')
    router.push('/constellation-map')
    return
  }
  
  const randomJob = availableJobs[Math.floor(Math.random() * availableJobs.length)]
  await startJourney(randomJob)
}

// 前往星图（报告页）
const goToConstellationMap = () => {
  router.push('/constellation-map')
}

// 前往虚拟形象创建/编辑
const goToAvatarCreator = () => {
  router.push('/avatar-creator')
}

// 前往探索自我测试
const goToSelfDiscovery = () => {
  ElMessage.info('进入轻量级自我发现测试...')
  router.push('/self-discovery')
}

// 计算进度百分比
const progressPercentage = computed(() => {
  const total = explorationProgress.value.journeys_started + 
                explorationProgress.value.journeys_completed
  if (total === 0) return 0
  return Math.round((explorationProgress.value.journeys_completed / total) * 100)
})

onMounted(() => {
  if (userStore.isHR) {
    return
  }
  loadHomeData()
})
</script>

<template>
  <div class="galaxy-home">
    <!-- 星空背景 -->
    <div class="stars-background">
      <div class="star" v-for="i in 50" :key="i" 
           :style="{
             left: Math.random() * 100 + '%',
             top: Math.random() * 100 + '%',
             animationDelay: Math.random() * 3 + 's'
           }"></div>
    </div>

    <!-- Hero区域：星海启航 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">✨ 探索自己是永恒的话题</div>
        <h1 class="hero-title">
          <span class="gradient-text">星海启航</span>
        </h1>
        <p class="hero-subtitle">
          开启你的职业探索之旅，在星际故事中发现真实的自己
        </p>
        
        <div class="hero-actions">
          <button class="btn-primary glow" @click="quickExplore">
            <span class="btn-icon">🚀</span>
            <span>开始探索</span>
          </button>
          <button class="btn-secondary" @click="goToSelfDiscovery">
            <span class="btn-icon">🧭</span>
            <span>先了解自己</span>
          </button>
        </div>

        <div class="hero-hint">
          <div class="hint-item">
            <span class="hint-icon">⏱️</span>
            <span>约10-15分钟</span>
          </div>
          <div class="hint-item">
            <span class="hint-icon">🎮</span>
            <span>沉浸式故事体验</span>
          </div>
          <div class="hint-item">
            <span class="hint-icon">📊</span>
            <span>生成专属星图</span>
          </div>
        </div>
      </div>

      <!-- 探索进度星盘 -->
      <div class="progress-constellation" v-if="explorationProgress.journeys_completed > 0">
        <div class="constellation-card">
          <div class="constellation-header">
            <h3>你的星座等级</h3>
            <div class="level-badge">Lv.{{ explorationProgress.constellation_level }}</div>
          </div>
          <div class="progress-circle">
            <svg viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="54" class="progress-bg"/>
              <circle cx="60" cy="60" r="54" class="progress-fill"
                      :style="{ strokeDashoffset: 339.3 - (339.3 * progressPercentage / 100) }"/>
            </svg>
            <div class="progress-text">{{ progressPercentage }}%</div>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ explorationProgress.journeys_completed }}</div>
              <div class="stat-label">已完成探索</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ explorationProgress.abilities_discovered }}</div>
              <div class="stat-label">已发现能力</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 搜索与筛选 -->
    <section class="search-section">
      <div class="container">
        <div class="search-card">
          <div class="search-header">
            <h2>探索星系岗位</h2>
            <p>每个岗位都是一段独特的星际故事</p>
          </div>
          
          <div class="search-bar">
            <input 
              v-model="searchKeyword" 
              type="text" 
              placeholder="搜索你感兴趣的职业方向..."
              @keyup.enter="onSearch"
              class="search-input"
            />
            <button @click="onSearch" class="search-btn">
              <span>🔍</span>
            </button>
          </div>

          <div class="filter-tabs">
            <button 
              :class="['filter-tab', { active: filters.category === '' }]"
              @click="filters.category = ''; loadHomeData()"
            >
              全部星系
            </button>
            <button 
              :class="['filter-tab', { active: filters.category === '技术岗' }]"
              @click="filters.category = '技术岗'; loadHomeData()"
            >
              🛸 技术星系
            </button>
            <button 
              :class="['filter-tab', { active: filters.category === '产品岗' }]"
              @click="filters.category = '产品岗'; loadHomeData()"
            >
              🎯 产品星系
            </button>
            <button 
              :class="['filter-tab', { active: filters.category === '设计岗' }]"
              @click="filters.category = '设计岗'; loadHomeData()"
            >
              🎨 设计星系
            </button>
            <button 
              :class="['filter-tab', { active: filters.category === '运营岗' }]"
              @click="filters.category = '运营岗'; loadHomeData()"
            >
              📈 运营星系
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 岗位星系列表 -->
    <section class="galaxy-grid-section">
      <div class="container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">🌌</div>
          <p>正在加载星系地图...</p>
        </div>

        <div v-else-if="galaxyJobs.length === 0" class="empty-state">
          <div class="empty-icon">🔭</div>
          <h3>未发现匹配的星系</h3>
          <p>尝试调整搜索条件或开始自我发现测试</p>
          <button class="btn-secondary" @click="goToSelfDiscovery">
            开始自我发现
          </button>
        </div>

        <div v-else class="galaxy-grid">
          <div 
            v-for="job in galaxyJobs" 
            :key="job.id"
            class="galaxy-card"
            :class="{ explored: job.applied }"
          >
            <!-- 星系图标 -->
            <div class="galaxy-icon">
              <div class="planet"></div>
              <div class="orbit"></div>
            </div>

            <!-- 星系信息 -->
            <div class="galaxy-info">
              <div class="galaxy-header">
                <h3 class="galaxy-name">{{ job.name }}</h3>
                <span v-if="job.applied" class="explored-badge">已探索</span>
              </div>
              
              <p class="galaxy-company">{{ job.company }}</p>
              
              <div class="galaxy-tags">
                <span class="tag">{{ job.city }}</span>
                <span class="tag">{{ job.salary }}</span>
              </div>

              <div class="galaxy-story">
                <p class="story-hint">
                  <span class="story-icon">📖</span>
                  {{ job.description || '在这段旅程中，你将扮演一名' + job.name + '，面对真实的职场挑战...' }}
                </p>
              </div>

              <div class="galaxy-traits">
                <span class="trait-label">探索方向：</span>
                <span class="trait-value">{{ job.trait_hint || job.suggested_traits || '适合探索型性格' }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="galaxy-actions">
              <button 
                class="btn-explore"
                :disabled="job.applied"
                @click="startJourney(job)"
              >
                <span v-if="job.applied">✓ 已探索</span>
                <span v-else>🚀 开始探索</span>
              </button>
              <button class="btn-detail">了解详情</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 快捷入口 -->
    <section class="quick-access-section">
      <div class="container">
        <div class="access-grid">
          <div class="access-card" @click="goToAvatarCreator">
            <div class="access-icon">👤</div>
            <h4>{{ hasAvatar ? '编辑形象' : '创建形象' }}</h4>
            <p>{{ hasAvatar ? '自定义你的探险家形象' : '开始前先创建你的虚拟形象' }}</p>
          </div>

          <div class="access-card" @click="goToConstellationMap">
            <div class="access-icon">🗺️</div>
            <h4>我的星图</h4>
            <p>查看探索记录与能力雷达图</p>
          </div>

          <div class="access-card">
            <div class="access-icon">📝</div>
            <h4>航行日志</h4>
            <p>回顾你的探索历程</p>
          </div>

          <div class="access-card">
            <div class="access-icon">🎁</div>
            <h4>探险家勋章</h4>
            <p>分享你的成就与发现</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部说明 -->
    <section class="about-section">
      <div class="container">
        <div class="about-card">
          <h3>关于星海探索</h3>
          <p>
            这不是一次测试，而是一段探索之旅。在沉浸式的故事场景中，你将自然地展现真实的自己。
            每一次选择都没有对错，只有不同的风格。系统将帮助你发现自己的能力亮点，找到适合的职业方向。
          </p>
          <p class="privacy-note">
            🔒 你的所有数据仅用于生成个人探索报告，我们尊重你的隐私与选择。
          </p>
          <div class="about-links">
            <a href="javascript:void(0)">了解评估原理</a>
            <a href="javascript:void(0)">隐私政策</a>
            <a href="javascript:void(0)">联系我们</a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.galaxy-home {
  min-height: 100vh;
  background: #0a0e27;
  color: #e0e6ed;
  position: relative;
  overflow-x: hidden;
  font-family: 'Space Mono', monospace;
}

/* 星空背景动画 */
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

/* Hero区域 */
.hero-section {
  position: relative;
  z-index: 1;
  padding: 80px 20px 60px;
  background: linear-gradient(180deg, 
    rgba(88, 28, 135, 0.3) 0%, 
    rgba(10, 14, 39, 0.5) 50%,
    transparent 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 60px;
  flex-wrap: wrap;
}

.hero-content {
  max-width: 600px;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(167, 139, 250, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  border-radius: 20px;
  font-size: 13px;
  margin-bottom: 24px;
  letter-spacing: 0.5px;
}

.hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 64px;
  font-weight: 900;
  margin-bottom: 20px;
  line-height: 1.1;
}

.gradient-text {
  background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #f59e0b 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.3); }
}

.hero-subtitle {
  font-size: 18px;
  color: #cbd5e1;
  margin-bottom: 40px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.btn-primary {
  padding: 16px 32px;
  background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(167, 139, 250, 0.6);
}

.btn-primary.glow {
  animation: glow-pulse 2s infinite;
}

@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 4px 20px rgba(167, 139, 250, 0.4); }
  50% { box-shadow: 0 4px 40px rgba(167, 139, 250, 0.8); }
}

.btn-secondary {
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.btn-icon {
  font-size: 20px;
}

.hero-hint {
  display: flex;
  gap: 24px;
  justify-content: center;
  flex-wrap: wrap;
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #94a3b8;
}

.hint-icon {
  font-size: 18px;
}

/* 探索进度星盘 */
.progress-constellation {
  position: relative;
}

.constellation-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 24px;
  padding: 32px;
  backdrop-filter: blur(20px);
  min-width: 280px;
}

.constellation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.constellation-header h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  color: #a78bfa;
}

.level-badge {
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
}

.progress-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
}

.progress-circle svg {
  transform: rotate(-90deg);
}

.progress-bg {
  fill: none;
  stroke: rgba(167, 139, 250, 0.1);
  stroke-width: 8;
}

.progress-fill {
  fill: none;
  stroke: url(#gradient);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 339.3;
  transition: stroke-dashoffset 1s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  color: #a78bfa;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
}

/* 容器 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 搜索区域 */
.search-section {
  position: relative;
  z-index: 1;
  padding: 40px 0;
}

.search-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 24px;
  padding: 32px;
  backdrop-filter: blur(20px);
}

.search-header {
  text-align: center;
  margin-bottom: 32px;
}

.search-header h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.search-header p {
  color: #94a3b8;
  font-size: 14px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  padding: 16px 24px;
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-family: 'Space Mono', monospace;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.3);
}

.search-input::placeholder {
  color: #64748b;
}

.search-btn {
  padding: 16px 24px;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: scale(1.05);
}

.filter-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.filter-tab {
  padding: 10px 20px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 20px;
  color: #cbd5e1;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Space Mono', monospace;
}

.filter-tab:hover {
  background: rgba(167, 139, 250, 0.2);
  border-color: rgba(167, 139, 250, 0.4);
}

.filter-tab.active {
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  border-color: transparent;
  color: white;
  font-weight: 700;
}

/* 岗位星系网格 */
.galaxy-grid-section {
  position: relative;
  z-index: 1;
  padding: 40px 0 60px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  font-size: 48px;
  animation: spin 2s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-family: 'Orbitron', sans-serif;
  margin-bottom: 8px;
  color: #a78bfa;
}

.empty-state p {
  color: #94a3b8;
  margin-bottom: 24px;
}

.galaxy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.galaxy-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.galaxy-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #a78bfa, #ec4899, #f59e0b);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.galaxy-card:hover::before {
  opacity: 1;
}

.galaxy-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(167, 139, 250, 0.3);
  border-color: rgba(167, 139, 250, 0.5);
}

.galaxy-card.explored {
  opacity: 0.7;
  background: rgba(30, 41, 59, 0.4);
}

.galaxy-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  position: relative;
}

.planet {
  width: 60px;
  height: 60px;
  background: radial-gradient(circle at 30% 30%, #ec4899, #a78bfa);
  border-radius: 50%;
  position: absolute;
  top: 10px;
  left: 10px;
  box-shadow: 0 0 30px rgba(167, 139, 250, 0.6);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.orbit {
  width: 80px;
  height: 80px;
  border: 2px dashed rgba(167, 139, 250, 0.3);
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 0;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.galaxy-info {
  margin-bottom: 20px;
}

.galaxy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.galaxy-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  color: #e0e6ed;
  margin: 0;
}

.explored-badge {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.4);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #22c55e;
}

.galaxy-company {
  color: #a78bfa;
  font-size: 14px;
  margin-bottom: 12px;
}

.galaxy-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tag {
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  color: #cbd5e1;
}

.galaxy-story {
  margin: 16px 0;
  padding: 12px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  border-left: 3px solid #a78bfa;
}

.story-hint {
  font-size: 13px;
  line-height: 1.6;
  color: #cbd5e1;
  margin: 0;
  display: flex;
  gap: 8px;
}

.story-icon {
  flex-shrink: 0;
}

.galaxy-traits {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 12px;
}

.trait-label {
  color: #64748b;
}

.trait-value {
  color: #ec4899;
  font-weight: 700;
}

.galaxy-actions {
  display: flex;
  gap: 12px;
}

.btn-explore {
  flex: 1;
  padding: 12px;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Orbitron', sans-serif;
}

.btn-explore:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.5);
}

.btn-explore:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-detail {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Space Mono', monospace;
}

.btn-detail:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* 快捷入口 */
.quick-access-section {
  position: relative;
  z-index: 1;
  padding: 40px 0;
}

.access-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.access-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
}

.access-card:hover {
  transform: translateY(-4px);
  border-color: rgba(167, 139, 250, 0.5);
  box-shadow: 0 8px 30px rgba(167, 139, 250, 0.3);
}

.access-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.access-card h4 {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  margin-bottom: 8px;
  color: #e0e6ed;
}

.access-card p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* 底部说明 */
.about-section {
  position: relative;
  z-index: 1;
  padding: 60px 0 80px;
}

.about-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 24px;
  padding: 40px;
  backdrop-filter: blur(20px);
  text-align: center;
}

.about-card h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 28px;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.about-card p {
  color: #cbd5e1;
  line-height: 1.8;
  margin-bottom: 16px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.privacy-note {
  color: #94a3b8;
  font-size: 14px;
  margin-top: 24px;
}

.about-links {
  display: flex;
  gap: 24px;
  justify-content: center;
  margin-top: 24px;
  flex-wrap: wrap;
}

.about-links a {
  color: #a78bfa;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.about-links a:hover {
  color: #ec4899;
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 42px;
  }

  .hero-section {
    padding: 60px 20px 40px;
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .btn-primary, .btn-secondary {
    width: 100%;
    justify-content: center;
  }

  .search-header h2 {
    font-size: 24px;
  }

  .galaxy-grid {
    grid-template-columns: 1fr;
  }

  .access-grid {
    grid-template-columns: 1fr;
  }
}
</style>
