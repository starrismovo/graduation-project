<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import JobCard from '@/components/JobCard.vue'
import request from '@/utils/request'

const router = useRouter()

// 数据
const jobs = ref<any[]>([])
const loading = ref(false)
const total = ref(0)

// 筛选条件
const searchKeyword = ref('')
const selectedCity = ref('')
const selectedSalary = ref('')
const sortBy = ref<'latest' | 'recommended' | 'salary_high' | 'salary_low'>('recommended')
const currentPage = ref(1)
const pageSize = ref(12)

// 城市列表
const cities = ref<string[]>([])

// 薪资范围选项
const salaryRanges = [
  { label: '5k以下', min: 0, max: 5 },
  { label: '5k-10k', min: 5, max: 10 },
  { label: '10k-20k', min: 10, max: 20 },
  { label: '20k-30k', min: 20, max: 30 },
  { label: '30k以上', min: 30, max: 100 },
]

// 加载岗位数据
async function loadJobs() {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortBy.value // 添加排序参数
    }
    if (searchKeyword.value.trim()) params.keyword = searchKeyword.value.trim()
    if (selectedCity.value) params.city = selectedCity.value
    
    // 薪资范围筛选
    if (selectedSalary.value) {
      const range = salaryRanges.find(r => r.label === selectedSalary.value)
      if (range) {
        params.salary_min = range.min
        params.salary_max = range.max
      }
    }

    const res = await request.get('/jobs/search', { params })
    const data = res.data?.data || res.data || {}
    
    // 应用本地排序优化（客户端侧处理）
    let jobsList = data.items || data.jobs || []
    
    if (sortBy.value === 'salary_high') {
      jobsList.sort((a: any, b: any) => {
        const aMax = b.salary_max || 999
        const bMax = b.salary_max || 999
        return bMax - aMax
      })
    } else if (sortBy.value === 'salary_low') {
      jobsList.sort((a: any, b: any) => {
        const aMin = a.salary_min || 0
        const bMin = b.salary_min || 0
        return aMin - bMin
      })
    } else if (sortBy.value === 'recommended') {
      // 按 match_score 排序（推荐指数高的优先）
      jobsList.sort((a: any, b: any) => {
        const aScore = a.match_score || 0
        const bScore = b.match_score || 0
        return bScore - aScore
      })
    }
    
    jobs.value = jobsList
    total.value = data.total || jobs.value.length
  } catch (error) {
    console.error('加载岗位失败:', error)
    ElMessage.error('加载岗位数据失败')
  } finally {
    loading.value = false
  }
}

// 加载筛选选项
async function loadFilters() {
  try {
    const res = await request.get('/jobs/filters')
    const data = res.data?.data || res.data || {}
    cities.value = (data.cities || []).filter((c: string) => c && c !== '未填写')
  } catch {
    // 静默失败
  }
}

// 搜索
function handleSearch() {
  currentPage.value = 1
  loadJobs()
}

// 重置
function handleReset() {
  searchKeyword.value = ''
  selectedCity.value = ''
  selectedSalary.value = ''
  currentPage.value = 1
  loadJobs()
}

// 快速选城市
function selectCity(city: string) {
  selectedCity.value = selectedCity.value === city ? '' : city
}

// 分页
function handlePageChange(page: number) {
  currentPage.value = page
  loadJobs()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadJobs()
}

function goToJobDetail(jobId: number | string) {
  router.push(`/home/jobs/${jobId}`)
}

function startJobAssessment(jobId: number | string) {
  router.push({
    path: '/home/interviews/room',
    query: {
      jobId: String(jobId)
    }
  })
}

// 监听筛选条件变化
watch([selectedCity, selectedSalary, sortBy], () => {
  currentPage.value = 1
  loadJobs()
})

onMounted(() => {
  loadFilters()
  loadJobs()
})
</script>

<template>
  <div class="job-list-page">
    <!-- 页面头部 -->
    <div class="page-hero">
      <div class="hero-content">
        <h1 class="hero-title">探索岗位，先看详情再进入面试</h1>
        <p class="hero-desc">从 {{ total.toLocaleString() }} 个真实职位中，先确认岗位信息，再决定加入面试 Hub 或直接发起 AI 面试</p>
        
        <!-- 搜索栏 -->
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索职位名称、公司名..."
            size="large"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon :size="18"><Search /></el-icon>
            </template>
          </el-input>
          <button class="search-btn" @click="handleSearch">搜索</button>
        </div>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <!-- 排序选项 -->
      <div class="sort-controls">
        <span class="sort-label">排序</span>
        <div class="sort-buttons">
          <button 
            :class="['sort-btn', { active: sortBy === 'recommended' }]"
            @click="sortBy = 'recommended'"
            title="按推荐指数排序"
          >
            <svg class="sort-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            推荐排序
          </button>
          <button 
            :class="['sort-btn', { active: sortBy === 'latest' }]"
            @click="sortBy = 'latest'"
            title="按最新发布时间排序"
          >
            <svg class="sort-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2m0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8m.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
            最新
          </button>
          <button 
            :class="['sort-btn', { active: sortBy === 'salary_high' }]"
            @click="sortBy = 'salary_high'"
            title="按薪资从高到低"
          >
            <svg class="sort-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            薪资高
          </button>
          <button 
            :class="['sort-btn', { active: sortBy === 'salary_low' }]"
            @click="sortBy = 'salary_low'"
            title="按薪资从低到高"
          >
            <svg class="sort-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" transform="rotate(180 12 12)"/></svg>
            薪资低
          </button>
        </div>
      </div>

      <!-- 城市快捷标签 -->
      <div class="filter-group">
        <span class="filter-label">城市</span>
        <div class="city-tags">
          <button 
            :class="['city-tag', { active: !selectedCity }]"
            @click="selectedCity = ''"
          >全部</button>
          <button 
            v-for="city in cities" 
            :key="city"
            :class="['city-tag', { active: selectedCity === city }]"
            @click="selectCity(city)"
          >{{ city }}</button>
        </div>
      </div>
      
      <!-- 薪资范围 -->
      <div class="filter-group">
        <span class="filter-label">薪资</span>
        <div class="city-tags">
          <button 
            :class="['city-tag', { active: !selectedSalary }]"
            @click="selectedSalary = ''"
          >不限</button>
          <button 
            v-for="range in salaryRanges" 
            :key="range.label"
            :class="['city-tag', { active: selectedSalary === range.label }]"
            @click="selectedSalary = selectedSalary === range.label ? '' : range.label"
          >{{ range.label }}</button>
        </div>
      </div>
      
      <!-- 结果统计 + 重置 -->
      <div class="filter-footer">
        <span class="result-info">
          共找到 <strong>{{ total.toLocaleString() }}</strong> 个岗位
        </span>
        <button 
          v-if="selectedCity || selectedSalary || searchKeyword"
          class="reset-btn" 
          @click="handleReset"
        >清除筛选</button>
      </div>
    </div>

    <!-- 岗位卡片网格 -->
    <div class="job-grid" v-loading="loading">
      <template v-if="jobs.length > 0">
        <div v-for="job in jobs" :key="job.id" class="grid-item">
          <JobCard
            :job="job"
            @assess="startJobAssessment"
            @click="goToJobDetail(job.id)"
          />
        </div>
      </template>
      
      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="28" stroke="#ddd" stroke-width="2"/>
            <path d="M22 26h20M22 32h14M22 38h8" stroke="#ccc" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <p class="empty-text">没有找到匹配的岗位</p>
        <button class="reset-btn" @click="handleReset">清除筛选条件</button>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-area" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<style scoped>
.job-list-page {
  min-height: calc(100vh - 60px);
  background: #f8f9fc;
}

/* ===== 顶部 Hero ===== */
.page-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 56px 32px 64px;
  color: #fff;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
}

.hero-content {
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
}

.hero-title {
  margin: 0 0 14px;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.hero-desc {
  margin: 0 0 32px;
  font-size: 16px;
  opacity: 0.9;
  line-height: 1.6;
}

/* 搜索框 */
.search-box {
  display: flex;
  gap: 0;
  max-width: 600px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 28px rgba(0,0,0,0.12);
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px 0 0 12px;
  box-shadow: none !important;
  padding: 6px 16px;
  height: 48px;
}

.search-btn {
  padding: 0 28px;
  border: none;
  background: #fff;
  color: #667eea;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.search-btn:hover {
  background: #f0f2ff;
}

/* ===== 筛选区 ===== */
.filter-section {
  max-width: 1420px;
  margin: -28px auto 0;
  padding: 28px 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: relative;
  z-index: 1;
  margin-left: 24px;
  margin-right: 24px;
}

/* ===== 排序控制 ===== */
.sort-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  margin-bottom: 8px;
  border-bottom: 3px solid #f0f1f3;
}

.sort-label {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  width: 36px;
}

.sort-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 13px;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  background: #fff;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.sort-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.sort-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.sort-icon {
  width: 14px;
  height: 14px;
}

.filter-group {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 12px 0;
}

.filter-group + .filter-group {
  border-top: 1px solid #f0f1f3;
}

.filter-label {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  padding-top: 5px;
  width: 36px;
}

.city-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.city-tag {
  padding: 5px 14px;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  background: #fff;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
}

.city-tag:hover {
  border-color: #667eea;
  color: #667eea;
}

.city-tag.active {
  background: #667eea;
  border-color: #667eea;
  color: #fff;
}

.filter-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 14px;
  border-top: 1px solid #f0f1f3;
  margin-top: 8px;
}

.result-info {
  font-size: 13px;
  color: #909399;
}

.result-info strong {
  color: #667eea;
  font-weight: 600;
}

.reset-btn {
  padding: 5px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  color: #909399;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

/* ===== 卡片网格 ===== */
.job-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 28px 24px;
  padding: 40px 32px;
  max-width: 1420px;
  margin: 0 auto;
  min-height: 200px;
  background: #fafbfc;
  border-radius: 8px;
}

.grid-item {
  display: flex;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 32px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%);
  border-radius: 8px;
  border: 2px dashed #e5e7eb;
}

.empty-icon svg {
  width: 64px;
  height: 64px;
}

.empty-text {
  margin: 16px 0;
  color: #909399;
  font-size: 14px;
}

/* ===== 分页 ===== */
.pagination-area {
  display: flex;
  justify-content: center;
  padding: 40px 32px 60px;
  background: #fafbfc;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .page-hero {
    padding: 28px 16px 36px;
  }
  .hero-title {
    font-size: 22px;
  }
  .filter-section {
    margin: -16px 12px 0;
    padding: 14px 16px;
  }
  .filter-group {
    flex-direction: column;
    gap: 6px;
  }
  .filter-label {
    width: auto;
  }
  .job-grid {
    grid-template-columns: 1fr;
    padding: 20px 16px;
    gap: 16px;
    background: transparent;
  }
  .search-box {
    flex-direction: column;
    border-radius: 12px;
  }
  .search-input :deep(.el-input__wrapper) {
    border-radius: 12px 12px 0 0;
  }
  .search-btn {
    padding: 12px;
    border-radius: 0 0 12px 12px;
    border-top: 1px solid #eee;
  }
}

@media (min-width: 1200px) {
  .job-grid {
    grid-template-columns: repeat(auto-fit, minmax(335px, 1fr));
    gap: 26px 22px;
    padding: 36px 28px;
  }
}

@media (min-width: 1400px) {
  .filter-section {
    max-width: 1420px;
    margin-left: auto;
    margin-right: auto;
    margin-top: -20px;
  }
  .job-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 30px 24px;
    padding: 40px 32px;
  }
}

@media (min-width: 1600px) {
  .job-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 32px 28px;
    padding: 48px 40px;
  }
}
</style>
