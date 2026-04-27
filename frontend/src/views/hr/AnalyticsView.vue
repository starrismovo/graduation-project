<template>
  <div class="analytics-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">招聘漏斗、匹配分布与各岗位评估概况</p>
      </div>
      <el-button :icon="Refresh" @click="loadAll">刷新数据</el-button>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid" v-loading="loading">
      <div class="kpi-card blue">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">在招岗位</div>
          <div class="kpi-value">{{ summary.openJobs }}</div>
        </div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">评估总人次</div>
          <div class="kpi-value">{{ summary.totalAssessments }}</div>
        </div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">平均匹配度</div>
          <div class="kpi-value">{{ summary.avgMatchRate }}%</div>
        </div>
      </div>

      <div class="kpi-card orange">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">已完成评估</div>
          <div class="kpi-value">{{ summary.completedAssessments }}</div>
        </div>
      </div>
    </div>

    <!-- 主体内容：两列 -->
    <div class="main-grid">
      <!-- 左：各岗位评估数 -->
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">各岗位评估人数</h3>
        </div>
        <div class="bar-chart" v-if="jobChartData.length > 0">
          <div
            v-for="item in jobChartData"
            :key="item.name"
            class="bar-row"
          >
            <div class="bar-label" :title="item.name">{{ truncate(item.name, 12) }}</div>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: (item.count / maxJobCount * 100) + '%' }"
              />
            </div>
            <div class="bar-count">{{ item.count }}</div>
          </div>
        </div>
        <div v-else class="chart-empty">暂无数据</div>
      </div>

      <!-- 右：匹配分数分布 -->
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">匹配分数分布</h3>
        </div>
        <div class="donut-section" v-if="scoreDistribution.some(d => d.count > 0)">
          <div class="donut-legend">
            <div
              v-for="seg in scoreDistribution"
              :key="seg.label"
              class="legend-item"
            >
              <span class="legend-dot" :style="{ background: seg.color }" />
              <span class="legend-label">{{ seg.label }}</span>
              <span class="legend-value">{{ seg.count }} 人</span>
              <span class="legend-pct">（{{ seg.pct }}%）</span>
            </div>
          </div>
          <!-- 简易横条图形式展示分布 -->
          <div class="dist-bars">
            <div v-for="seg in scoreDistribution" :key="seg.label" class="dist-row">
              <div class="dist-name" :style="{ color: seg.color }">{{ seg.label }}</div>
              <div class="dist-track">
                <div
                  class="dist-fill"
                  :style="{ width: seg.pct + '%', background: seg.color }"
                />
              </div>
              <div class="dist-pct">{{ seg.pct }}%</div>
            </div>
          </div>
        </div>
        <div v-else class="chart-empty">暂无评估数据</div>
      </div>
    </div>

    <!-- 各岗位详情表 -->
    <div class="detail-card">
      <div class="card-header">
        <h3 class="card-title">各岗位评估详情</h3>
      </div>
      <el-table :data="jobStats" border stripe style="width: 100%" empty-text="暂无数据">
        <el-table-column label="岗位名称" prop="name" min-width="180" />
        <el-table-column label="评估人次" prop="total" min-width="100" align="center" sortable />
        <el-table-column label="已完成" prop="completed" min-width="100" align="center" sortable />
        <el-table-column label="进行中" prop="pending" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.pending > 0" type="warning" size="small">{{ row.pending }}</el-tag>
            <span v-else style="color: #9ca3af">0</span>
          </template>
        </el-table-column>
        <el-table-column label="平均匹配度" min-width="160" sortable>
          <template #default="{ row }">
            <div class="inline-score">
              <div class="inline-bar">
                <div
                  class="inline-fill"
                  :class="getScoreClass(row.avgScore)"
                  :style="{ width: row.avgScore + '%' }"
                />
              </div>
              <span>{{ row.avgScore }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="高匹配(≥80%)" min-width="120" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.highMatch }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getHRJobList } from '@/api/job'
import request from '@/utils/request'

const loading = ref(false)

const summary = ref({
  openJobs: 0,
  totalAssessments: 0,
  completedAssessments: 0,
  avgMatchRate: 0,
})

// 各岗位评估人次（柱状图用）
const jobChartData = ref<{ name: string; count: number }[]>([])
const maxJobCount = computed(() => Math.max(...jobChartData.value.map(d => d.count), 1))

// 匹配分数分布
const scoreDistribution = ref([
  { label: '优秀 (≥80)', color: '#67c23a', count: 0, pct: 0 },
  { label: '良好 (60-79)', color: '#409eff', count: 0, pct: 0 },
  { label: '一般 (40-59)', color: '#e6a23c', count: 0, pct: 0 },
  { label: '较差 (<40)', color: '#f56c6c', count: 0, pct: 0 },
])

// 各岗位汇总表
const jobStats = ref<any[]>([])

onMounted(loadAll)

async function loadAll() {
  loading.value = true
  try {
    // 并行加载岗位列表和候选人数据
    const [jobRes, candRes] = await Promise.all([
      getHRJobList({ limit: 200 }),
      request.get('/assessment/hr/candidates', { params: { limit: 200 } }),
    ])

    const jobs: any[] = jobRes.data?.items || []
    const candidates: any[] = candRes.data?.data?.items || []

    // ===== KPI =====
    summary.value.openJobs = jobs.length
    summary.value.totalAssessments = candidates.length
    summary.value.completedAssessments = candidates.filter(c => c.assessment_status === 'completed').length

    const withScore = candidates.filter(c => c.match_score != null)
    summary.value.avgMatchRate = withScore.length
      ? Math.round(withScore.reduce((s, c) => s + c.match_score, 0) / withScore.length)
      : 0

    // ===== 柱状图：各岗位评估人数 =====
    const jobCountMap: Record<string, number> = {}
    for (const c of candidates) {
      const key = c.job_title || '未知岗位'
      jobCountMap[key] = (jobCountMap[key] || 0) + 1
    }
    jobChartData.value = Object.entries(jobCountMap)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)

    // ===== 分布 =====
    const total = withScore.length || 1
    const buckets = [0, 0, 0, 0]
    for (const c of withScore) {
      if (c.match_score >= 80) buckets[0]++
      else if (c.match_score >= 60) buckets[1]++
      else if (c.match_score >= 40) buckets[2]++
      else buckets[3]++
    }
    scoreDistribution.value = scoreDistribution.value.map((seg, i) => ({
      ...seg,
      count: buckets[i],
      pct: Math.round((buckets[i] / total) * 100),
    }))

    // ===== 各岗位详情表 =====
    const statMap: Record<number, any> = {}
    for (const job of jobs) {
      statMap[job.id] = {
        name: job.name,
        total: 0,
        completed: 0,
        pending: 0,
        scoreSum: 0,
        scoreCount: 0,
        highMatch: 0,
      }
    }
    for (const c of candidates) {
      if (!c.job_id || !statMap[c.job_id]) {
        if (c.job_id) {
          statMap[c.job_id] = {
            name: c.job_title || '未知',
            total: 0, completed: 0, pending: 0,
            scoreSum: 0, scoreCount: 0, highMatch: 0,
          }
        } else continue
      }
      const s = statMap[c.job_id]
      s.total++
      if (c.assessment_status === 'completed') s.completed++
      else s.pending++
      if (c.match_score != null) {
        s.scoreSum += c.match_score
        s.scoreCount++
        if (c.match_score >= 80) s.highMatch++
      }
    }
    jobStats.value = Object.values(statMap)
      .filter(s => s.total > 0)
      .map(s => ({
        ...s,
        avgScore: s.scoreCount ? Math.round(s.scoreSum / s.scoreCount) : 0,
      }))
      .sort((a, b) => b.total - a.total)
  } catch (e: any) {
    ElMessage.error('加载分析数据失败：' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function getScoreClass(score: number) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

function truncate(str: string, len: number) {
  return str.length > len ? str.slice(0, len) + '…' : str
}
</script>

<style scoped>
.analytics-view {
  max-width: 1400px;
  margin: 0 auto;
}

/* ========== 头部 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* ========== KPI ========== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 14px;
  color: #fff;
}

.kpi-card.blue   { background: linear-gradient(135deg, #667eea, #764ba2); }
.kpi-card.purple { background: linear-gradient(135deg, #a855f7, #6366f1); }
.kpi-card.green  { background: linear-gradient(135deg, #10b981, #059669); }
.kpi-card.orange { background: linear-gradient(135deg, #f59e0b, #d97706); }

.kpi-icon {
  width: 44px;
  height: 44px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon svg { width: 24px; height: 24px; stroke: #fff; }

.kpi-label {
  font-size: 13px;
  opacity: 0.85;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -1px;
  line-height: 1;
}

/* ========== 双列布局 ========== */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 28px;
}

@media (max-width: 900px) {
  .main-grid { grid-template-columns: 1fr; }
}

/* ========== 通用卡片 ========== */
.chart-card,
.detail-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  padding: 24px;
}

.detail-card { margin-bottom: 0; }

.card-header { margin-bottom: 20px; }

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.chart-empty {
  text-align: center;
  padding: 48px 0;
  color: #9ca3af;
  font-size: 14px;
}

/* ========== 柱状图 ========== */
.bar-chart { display: flex; flex-direction: column; gap: 12px; }

.bar-row { display: flex; align-items: center; gap: 10px; }

.bar-label {
  width: 100px;
  font-size: 13px;
  color: #374151;
  text-align: right;
  flex-shrink: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: #f3f4f6;
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 5px;
  transition: width 0.4s ease;
}

.bar-count {
  width: 28px;
  font-size: 13px;
  color: #6b7280;
  text-align: right;
}

/* ========== 分布 ========== */
.donut-section { display: flex; flex-direction: column; gap: 16px; }

.donut-legend { display: flex; flex-direction: column; gap: 6px; }

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label { color: #374151; flex: 1; }
.legend-value { font-weight: 500; color: #1f2937; }
.legend-pct { color: #9ca3af; }

.dist-bars { display: flex; flex-direction: column; gap: 10px; margin-top: 8px; }

.dist-row { display: flex; align-items: center; gap: 8px; }

.dist-name {
  width: 90px;
  font-size: 12px;
  font-weight: 500;
  text-align: right;
  flex-shrink: 0;
}

.dist-track {
  flex: 1;
  height: 12px;
  background: #f3f4f6;
  border-radius: 6px;
  overflow: hidden;
}

.dist-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.4s ease;
}

.dist-pct {
  width: 36px;
  font-size: 12px;
  color: #6b7280;
  text-align: right;
}

/* ========== 内联分数 ========== */
.inline-score {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.inline-bar {
  flex: 1;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.inline-fill {
  height: 100%;
  border-radius: 3px;
}
.inline-fill.high { background: #67c23a; }
.inline-fill.medium { background: #409eff; }
.inline-fill.low { background: #f56c6c; }
</style>
