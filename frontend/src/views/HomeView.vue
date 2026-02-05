<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { ref, onMounted } from 'vue'
import { getHomePageData, startInterview } from '../utils/request'

const userStore = useUserStore()
const router = useRouter()

// 筛选条件
const filters = ref({
  jobType: '',
  city: '',
  salary: '',
  traitPreference: '' // 新增：特质偏好筛选（如 高外向性）
})

// 面试统计信息
const interviewStats = ref({
  completed: 0,
  inProgress: 0,
  total: 0,
  passed: 0,
  avg_match: 0 // 平均匹配度（%），由后端返回 matching/avg 字段填充
})

// 推荐岗位列表
const recommendedJobs = ref<any[]>([])

// 加载状态
const loading = ref(true)

// 加载主页数据
const loadHomeData = async () => {
  try {
    loading.value = true
    const response = await getHomePageData({
      category: filters.value.jobType || undefined,
      city: filters.value.city || undefined,
      salary_range: filters.value.salary || undefined,
      trait_preference: filters.value.traitPreference || undefined
    })
    
    const data = response.data
    // 兼容后端不同命名的统计字段，优先使用 avg_match/avg_match_score
    interviewStats.value = {
      completed: data.stats?.completed ?? 0,
      inProgress: data.stats?.in_progress ?? data.stats?.inProgress ?? 0,
      total: data.stats?.total ?? 0,
      passed: data.stats?.passed ?? 0,
      avg_match: data.stats?.avg_match ?? data.stats?.avg_match_score ?? data.stats?.average_matching_score ?? 0
    }
    recommendedJobs.value = data.recommended_jobs || []
  } catch (error: any) {
    console.error('加载主页数据失败:', error)
    
    // 提供更详细的错误反馈
    if (error.message?.includes('timeout')) {
      ElMessage.error('请求超时，后端响应缓慢。请检查: python main.py')
    } else if (!error.response) {
      ElMessage.error('无法连接到服务器。请确保后端服务运行: python main.py')
    } else {
      ElMessage.error('加载数据失败，请刷新重试')
    }
  } finally {
    loading.value = false
  }
}

// 监听筛选条件变化
const onFilterChange = () => {
  loadHomeData()
}

// 开始评估（AI 智能体模拟评估）
const goToAssessment = async (jobId: number) => {
  try {
    const response = await startInterview(jobId) // 复用后端的创建面试接口作为评估入口
    // 如果后端返回 interview id，则使用之；否则回退到 jobId 以便前端演示
    const interviewId = response?.data?.id ?? jobId
    ElMessage.success('评估已开始')
    // 跳转到评估页面（未来实现）
    router.push(`/assessment/${interviewId}`)
  } catch (error: any) {
    console.error('开始评估失败:', error)
    // 后端可能未启动或不可达，回退到本地演示页面
    ElMessage.warning('无法连接后端，进入本地评估演示页面')
    router.push(`/assessment/${jobId}`)
  }
}

// 向后兼容：保留 goToInterview 名称调用评估入口
const goToInterview = (jobId: number) => goToAssessment(jobId)

// 随机选择岗位开始面试
const randomInterview = async () => {
  if (recommendedJobs.value.length === 0) {
    // 无推荐岗位时回退到本地静态演示页面，方便离线或后端未启动时测试
    ElMessage.info('暂无推荐岗位，进入本地评估演示')
    router.push('/assessment/demo')
    return
  }
  
  const randomJob = recommendedJobs.value[Math.floor(Math.random() * recommendedJobs.value.length)]
  if (randomJob.applied) {
    ElMessage.warning('该岗位已应聘，请选择其他岗位')
    return
  }
  
  await goToInterview(randomJob.id)
}

// 跳转到报告页面（强调可视化雷达图/匹配报告）
const goToReports = () => {
  ElMessage.info('跳转到评估报告页面（功能开发中；包含雷达图可视化）')
  // 未来路由：router.push('/reports')
}

// 页面挂载时检查用户角色
onMounted(() => {
  // 如果是HR用户，不在这个组件显示（由 IndexView 控制）
  if (userStore.isHR) {
    return
  }
  loadHomeData()
})
</script>

<template>
  <div class="home-container">
    <!-- 顶部欢迎区 -->
    <div class="welcome-section hero">
      <el-card class="welcome-card hero-card">
        <div class="hero-content">
          <div class="hero-text">
            <h1 class="hero-title">开始你的 AI 心理特质评估</h1>
            <p class="hero-subtitle">10分钟 · 多智能体模拟 · 生成职业匹配雷达图</p>
            <div class="hero-cta-wrap">
              <el-button class="hero-cta" type="primary" size="large" @click="randomInterview">🚀 立即开始评估</el-button>
              <div class="hero-note">系统将自动推荐适合你的岗位，或从推荐列表中选择用于评估</div>
            </div>
          </div>
          <div class="hero-visual">
            <!-- 占位：未来可放图示/动画或 AI 智能体缩略图 -->
            <div class="visual-placeholder">📊</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主容器 -->
    <div class="main-content">
      <!-- 面试进度状态卡 -->
      <div class="progress-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="status-card">
              <div class="status-item">
                <div class="status-number">{{ interviewStats.completed }}</div>
                <div class="status-label">已评估岗位数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="status-card">
              <div class="status-item">
                <div class="status-number">{{ interviewStats.inProgress }}</div>
                <div class="status-label">进行中评估</div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="status-card">
              <div class="status-item">
                <div class="status-number">{{ recommendedJobs.length }}</div>
                <div class="status-label">推荐岗位数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="status-card success">
              <div class="status-item">
                <div class="status-number">{{ interviewStats.avg_match }}%</div>
                <div class="status-label">平均匹配度</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 筛选条件区 -->
      <div class="filter-section">
        <el-card>
          <div class="filter-title">岗位搜索</div>
          <el-row :gutter="15">
            <el-col :xs="24" :sm="8">
              <el-select v-model="filters.jobType" placeholder="选择岗位类型" clearable @change="onFilterChange">
                <el-option label="技术岗" value="技术岗" />
                <el-option label="产品岗" value="产品岗" />
                <el-option label="设计岗" value="设计岗" />
                <el-option label="运营岗" value="运营岗" />
                <el-option label="市场岗" value="市场岗" />
              </el-select>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-select v-model="filters.city" placeholder="选择城市" clearable @change="onFilterChange">
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="深圳" value="深圳" />
                <el-option label="杭州" value="杭州" />
                <el-option label="南京" value="南京" />
              </el-select>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-select v-model="filters.salary" placeholder="选择薪资范围" clearable @change="onFilterChange">
                <el-option label="15k-20k" value="15k-20k" />
                <el-option label="20k-30k" value="20k-30k" />
                <el-option label="30k-50k" value="30k-50k" />
                <el-option label="50k-100k" value="50k-100k" />
              </el-select>
            </el-col>
          </el-row>
          <!-- 新增：特质偏好筛选 -->
          <el-row style="margin-top:12px">
            <el-col :xs="24" :sm="12">
              <el-select v-model="filters.traitPreference" placeholder="特质偏好（如：高外向性）" clearable @change="onFilterChange">
                <el-option label="高外向性岗位" value="high_extraversion" />
                <el-option label="高责任心岗位" value="high_conscientiousness" />
                <el-option label="高开放性岗位" value="high_openness" />
                <el-option label="高宜人性岗位" value="high_agreeableness" />
              </el-select>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 岗位推荐区 -->
      <div class="jobs-section">
        <div class="section-title">热门岗位推荐</div>
        <el-empty v-if="recommendedJobs.length === 0 && !loading" description="暂无推荐岗位" />
        <el-row v-else :gutter="20">
          <el-col 
            v-for="job in recommendedJobs" 
            :key="job.id"
            :xs="24" :sm="12" :md="8"
          >
            <el-card class="job-card" :class="{ 'applied': job.applied }">
              <div class="job-header">
                <div>
                  <h4 class="job-name">{{ job.name }}</h4>
                  <p class="company-name">{{ job.company }}</p>
                </div>
                <el-tag v-if="job.applied" type="success" size="small">已评估</el-tag>
              </div>
              
              <div class="job-details">
                <p><strong>薪资范围：</strong>{{ job.salary }}</p>
                <p><strong>工作地点：</strong>{{ job.city }}</p>
                <p><strong>岗位类别：</strong>{{ job.category }}</p>
                <p><strong>岗位特质：</strong>{{ job.trait_hint || job.suggested_traits || '适合外向型性格' }}</p>
              </div>

              <p class="job-description">{{ job.description }}</p>

              <div class="job-footer">
                <el-button type="primary" @click="goToAssessment(job.id)" :disabled="job.applied">
                  {{ job.applied ? '已评估' : '👉 使用该岗位进行评估' }}
                </el-button>
                <el-button>查看详情</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 快速入口区 -->
      <div class="quick-entry-section">
        <el-row :gutter="20" class="quick-entry-row">
            <el-col :xs="24" :sm="12" :md="6">
            <el-card class="quick-entry-card large-btn">
              <el-button type="primary" size="large" @click="randomInterview">
                🎯 立即评估
              </el-button>
              <p class="card-desc">随机选择岗位开始 AI 评估</p>
            </el-card>
          </el-col>
            <el-col :xs="24" :sm="12" :md="6">
            <el-card class="quick-entry-card large-btn">
              <el-button size="large" @click="goToReports">
                📊 我的报告
              </el-button>
              <p class="card-desc">查看评估报告与可视化雷达图</p>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="quick-entry-card">
              <div class="small-card-content">
                <div class="icon">📝</div>
                <div>
                  <h5>我的简历</h5>
                  <p>上传/管理简历</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="quick-entry-card">
              <div class="small-card-content">
                <div class="icon">⚙️</div>
                <div>
                  <h5>个人设置</h5>
                  <p>修改账户信息</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 底部信息区 -->
      <div class="footer-section">
        <el-card class="info-card">
          <h4>关于本课题</h4>
          <p>本系统使用 AI 智能体模拟真实岗位场景，进行心理特质评估并给出匹配度建议，旨在支持量化决策与招聘/职业发展研究。</p>
          <p>报告包含机器学习匹配结果与可视化（雷达图）以便决策参考。</p>
          <p><el-link type="primary" href="javascript:void(0)">📧 联系我们</el-link> | <el-link type="primary" href="javascript:void(0)">❓ 研究说明</el-link></p>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  padding: 0;
  margin: 0;
}

/* 顶部欢迎区 */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  color: white;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card :deep(.el-card__body) {
  padding: 30px;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.welcome-header h2 {
  margin: 0 0 15px 0;
  font-size: 28px;
  font-weight: bold;
}

.user-info {
  margin: 8px 0;
  font-size: 16px;
}

.username, .role {
  font-weight: bold;
  color: #ffd700;
}

.welcome-tip {
  margin-top: 15px;
  font-size: 15px;
  color: #e0e0e0;
  font-style: italic;
}

/* Hero 样式：第一屏核心评估入口 */
.welcome-section.hero {
  padding: 56px 20px;
}
.hero-card {
  background: rgba(255,255,255,0.06);
  border: none;
  max-width: 1200px;
  margin: 0 auto;
}
.hero-content {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
}
.hero-text {
  flex: 1;
  color: white;
}
.hero-title {
  font-size: 38px;
  margin: 0 0 12px 0;
  font-weight: 700;
}
.hero-subtitle {
  margin: 0 0 18px 0;
  color: rgba(255,255,255,0.9);
  font-size: 16px;
}
.hero-cta-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.hero-cta {
  font-size: 18px;
  padding: 14px 28px;
}
.hero-note {
  font-size: 13px;
  color: rgba(255,255,255,0.85);
}
.hero-visual {
  width: 180px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.visual-placeholder {
  font-size: 48px;
}

.welcome-header button {
  white-space: nowrap;
}

/* 主容器 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 面试进度状态卡 */
.progress-section {
  margin-bottom: 30px;
}

.status-card {
  height: 100%;
  border: 1px solid #e0e7ff;
  transition: all 0.3s ease;
}

.status-card:hover {
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.status-card.success {
  border-color: #67c23a;
}

.status-item {
  text-align: center;
  padding: 15px 0;
}

.status-number {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.status-card.success .status-number {
  color: #67c23a;
}

.status-label {
  font-size: 14px;
  color: #666;
}

/* 筛选条件区 */
.filter-section {
  margin-bottom: 30px;
}

.filter-section :deep(.el-card__body) {
  padding: 20px;
}

.filter-title {
  font-weight: bold;
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
}

.filter-section :deep(.el-select) {
  width: 100%;
}

/* 岗位推荐区 */
.jobs-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
  padding-left: 5px;
  border-left: 4px solid #667eea;
}

.job-card {
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #e0e7ff;
}

.job-card:hover {
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.2);
  transform: translateY(-4px);
  border-color: #667eea;
}

.job-card.applied {
  opacity: 0.85;
  background-color: #f9f9f9;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.job-name {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #333;
}

.company-name {
  margin: 0;
  color: #667eea;
  font-weight: 500;
  font-size: 14px;
}

.job-details {
  margin-bottom: 12px;
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.job-details p {
  margin: 5px 0;
}

.job-description {
  color: #888;
  font-size: 13px;
  margin: 12px 0;
  line-height: 1.6;
  min-height: 40px;
}

.job-footer {
  display: flex;
  gap: 8px;
  margin-top: 15px;
}

.job-footer button {
  flex: 1;
}

/* 快速入口区 */
.quick-entry-section {
  margin-bottom: 40px;
}

.quick-entry-row .el-col {
  margin-bottom: 20px;
}

.quick-entry-card {
  height: 100%;
  border: 1px solid #e0e7ff;
  transition: all 0.3s ease;
}

.quick-entry-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
}

.large-btn {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 140px;
}

.large-btn :deep(.el-card__body) {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.large-btn button {
  width: 100%;
}

.card-desc {
  margin: 10px 0 0 0;
  font-size: 13px;
  color: #999;
  text-align: center;
}

.small-card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon {
  font-size: 32px;
  min-width: 50px;
}

.small-card-content h5 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.small-card-content p {
  margin: 0;
  font-size: 13px;
  color: #999;
}

/* 底部信息区 */
.footer-section {
  margin-bottom: 20px;
}

.info-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border: 1px solid #d9d9d9;
}

.info-card h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.info-card p {
  margin: 8px 0;
  color: #666;
  line-height: 1.6;
  font-size: 14px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .welcome-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .welcome-header h2 {
    font-size: 22px;
  }

  .welcome-card :deep(.el-card__body) {
    padding: 20px;
  }

  .main-content {
    padding: 20px 10px;
  }

  .section-title {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .welcome-section {
    padding: 20px 10px;
  }

  .welcome-header h2 {
    font-size: 18px;
  }

  .welcome-header button {
    width: 100%;
  }
}
</style>