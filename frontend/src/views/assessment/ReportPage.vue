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
      <el-row :gutter="24">
        <!-- 左侧：报告摘要 -->
        <el-col :xs="24" :md="14">
          <!-- 基本信息 -->
          <el-card class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">评估基本信息</div>
            </template>
            <el-form label-width="100px" :model="reportData">
              <el-form-item label="评估岗位">
                <span>{{ reportData.job_title }}</span>
              </el-form-item>
              <el-form-item label="评估时间">
                <span>{{ formatTime(reportData.created_at) }}</span>
              </el-form-item>
              <el-form-item label="匹配度">
                <el-progress 
                  :percentage="reportData.match_score" 
                  :color="getScoreColor(reportData.match_score)"
                />
              </el-form-item>
              <el-form-item label="评估模式">
                <el-tag>{{ reportData.assessment_mode || '多角色对话' }}</el-tag>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 心理画像 -->
          <el-card class="report-card" shadow="hover">
            <template #header>
              <div class="card-title">
                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></el-icon>
                心理特质评分
              </div>
            </template>

            <div class="portrait-display">
              <RadarChart 
                :data="reportData.personality_trait || reportData.portrait || []"
                :height="300"
              />
            </div>

            <div class="traits-summary" v-if="reportData.personality_trait && reportData.personality_trait.length">
              <h4>特质分析：</h4>
              <div class="traits-list">
                <div 
                  v-for="trait in reportData.personality_trait" 
                  :key="trait.name"
                  class="trait-item"
                >
                  <span class="trait-name">{{ trait.name }}</span>
                  <el-progress 
                    :percentage="trait.score * 10"
                    :color="getTraitColor(trait.score)"
                    :text-inside="true"
                    :stroke-width="4"
                    style="flex: 1"
                  />
                  <span class="trait-score">{{ trait.score }}/10</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 对话内容摘要 -->
          <el-card class="report-card" shadow="hover" v-if="reportData.conversation_summary">
            <template #header>
              <div class="card-title">对话摘要</div>
            </template>
            <p class="summary-text">{{ reportData.conversation_summary }}</p>
          </el-card>

          <!-- 匹配分析 -->
          <el-card class="report-card" shadow="hover" v-if="reportData.match_analysis">
            <template #header>
              <div class="card-title">岗位匹配分析</div>
            </template>
            <div class="analysis-content">
              <div class="analysis-section">
                <h4>✅ 匹配优势</h4>
                <ul v-if="Array.isArray(reportData.match_analysis.strengths)">
                  <li v-for="(item, idx) in reportData.match_analysis.strengths" :key="idx">
                    {{ item }}
                  </li>
                </ul>
                <p v-else>{{ reportData.match_analysis.strengths }}</p>
              </div>
              <div class="analysis-section">
                <h4>⚠️ 发展空间</h4>
                <ul v-if="Array.isArray(reportData.match_analysis.gaps)">
                  <li v-for="(item, idx) in reportData.match_analysis.gaps" :key="idx">
                    {{ item }}
                  </li>
                </ul>
                <p v-else>{{ reportData.match_analysis.gaps }}</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：建议和行动 -->
        <el-col :xs="24" :md="10">
          <!-- 推荐建议 -->
          <el-card class="report-card" shadow="hover" v-if="reportData.recommendations">
            <template #header>
              <div class="card-title">💡 建议</div>
            </template>
            <div class="recommendations-list">
              <div 
                v-for="(rec, idx) in Array.isArray(reportData.recommendations) 
                  ? reportData.recommendations 
                  : [reportData.recommendations]" 
                :key="idx"
                class="rec-item"
              >
                <span class="rec-num">{{ idx + 1 }}</span>
                <span class="rec-text">{{ rec }}</span>
              </div>
            </div>
          </el-card>

          <!-- 下一步行动 -->
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import RadarChart from '@/components/RadarChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import { fetchReportDetail } from '@/utils/request'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const reportData = ref<any>(null)

async function loadReport() {
  loading.value = true
  try {
    const recordId = route.params.recordId
    reportData.value = await fetchReportDetail(recordId)
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

onMounted(loadReport)
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
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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

.portrait-display :deep(.echarts-container) {
  width: 100%;
  height: 300px;
  margin-bottom: 20px;
}

.traits-summary {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
  margin-top: 16px;
}

.traits-summary h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 14px;
}

.traits-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trait-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trait-name {
  flex-shrink: 0;
  min-width: 80px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.trait-score {
  flex-shrink: 0;
  min-width: 50px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
}

.summary-text {
  line-height: 1.8;
  color: #606266;
  margin: 0;
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
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
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

.action-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.step {
  display: flex;
  gap: 12px;
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
}

.step-content h4 {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #2c3e50;
  font-weight: 600;
}

.step-content p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-direction: column;
}

.action-buttons :deep(.el-button) {
  width: 100%;
}

.error-state {
  text-align: center;
  padding: 40px 20px;
}

@media (max-width: 1200px) {
  .report-container {
    padding: 16px;
  }

  .report-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .report-container {
    padding: 12px;
  }

  .report-header h2 {
    font-size: 18px;
  }

  .traits-list {
    gap: 8px;
  }

  .action-steps {
    gap: 12px;
  }
}
</style>
