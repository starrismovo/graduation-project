<template>
  <div class="report-generate">
    <el-tabs>
      <el-tab-pane label="综合报告">
        <div class="report-header">
          <h3>{{ candidate.name || '候选人' }} - AI 心理特质评估报告</h3>
          <div class="meta">
            <span>岗位：{{ candidate.desired_job || '-' }}</span>
            <span>评估时间：{{ reportTime }}</span>
          </div>
        </div>

        <div class="report-section">
          <h4>雷达图对比</h4>
          <div class="chart-placeholder">
            <div style="text-align: center; padding: 40px; color: #999;">
              📊 ECharts 双雷达图（理想岗位特质 vs 候选人评估结果）
            </div>
          </div>
        </div>

        <div class="report-section">
          <h4>五大人格维度评估</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="metric-card">
                <div class="metric-name">外向性 (Extraversion)</div>
                <div class="metric-score">{{ personalityScores.extraversion ?? 0 }}/10</div>
                <el-progress :percentage="(personalityScores.extraversion ?? 0) * 10" color="#409eff"></el-progress>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="metric-card">
                <div class="metric-name">责任心 (Conscientiousness)</div>
                <div class="metric-score">{{ personalityScores.conscientiousness ?? 0 }}/10</div>
                <el-progress :percentage="(personalityScores.conscientiousness ?? 0) * 10" color="#67c23a"></el-progress>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="metric-card">
                <div class="metric-name">开放性 (Openness)</div>
                <div class="metric-score">{{ personalityScores.openness ?? 0 }}/10</div>
                <el-progress :percentage="(personalityScores.openness ?? 0) * 10" color="#e6a23c"></el-progress>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="metric-card">
                <div class="metric-name">宜人性 (Agreeableness)</div>
                <div class="metric-score">{{ personalityScores.agreeableness ?? 0 }}/10</div>
                <el-progress :percentage="(personalityScores.agreeableness ?? 0) * 10" color="#f56c6c"></el-progress>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="report-section">
          <h4>岗位匹配度</h4>
          <div class="match-card">
            <div class="match-score">78%</div>
            <div class="match-label">与期望岗位相符度</div>
            <div class="match-detail">
              <p>✓ 强项：责任心、沟通能力、团队协作意识强</p>
              <p>△ 需要提高：时间管理、压力承受能力</p>
            </div>
          </div>
        </div>

        <div class="report-section">
          <h4>建议与评价</h4>
          <ul class="suggestions">
            <li>候选人在情境问答中表现出较好的问题分析能力</li>
            <li>建议在团队管理和冲突处理方面加强培训</li>
            <li>整体适合该岗位，建议继续推进</li>
          </ul>
        </div>

        <div class="report-footer">
          <el-button @click="downloadPDF">📥 导出 PDF 报告</el-button>
          <el-button type="primary" @click="finishAssessment">✓ 完成评估</el-button>
        </div>
      </el-tab-pane>

      <el-tab-pane label="原始数据">
        <div class="raw-data">
          <p><strong>候选人信息：</strong></p>
          <pre>{{ JSON.stringify(candidate, null, 2) }}</pre>
          <p><strong>量表分数：</strong></p>
          <pre>{{ JSON.stringify(personalityScores, null, 2) }}</pre>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

defineProps<{
  candidate?: Record<string, any>
  personalityScores?: Record<string, number>
}>()

const emit = defineEmits<{
  (e: 'finish'): void
}>()

const reportTime = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('zh-CN')
})

function downloadPDF() {
  ElMessage.info('PDF 导出功能（演示）')
}

function finishAssessment() {
  ElMessage.success('评估已完成！')
  emit('finish')
}
</script>

<style scoped>
.report-generate { background: #fff; padding: 20px; }
.report-header { margin-bottom: 20px; border-bottom: 2px solid #409eff; padding-bottom: 12px; }
.report-header h3 { margin: 0 0 8px 0; }
.meta { display: flex; gap: 20px; font-size: 12px; color: #666; }
.report-section { margin-bottom: 24px; }
.report-section h4 { margin: 0 0 12px 0; color: #333; }
.chart-placeholder { background: #f5f7fa; border-radius: 6px; }
.metric-card { padding: 12px; background: #f9f9f9; border-radius: 6px; }
.metric-name { font-weight: 500; margin-bottom: 6px; }
.metric-score { font-size: 18px; font-weight: bold; color: #409eff; margin-bottom: 8px; }
.match-card { text-align: center; padding: 20px; background: #f0f9ff; border-radius: 6px; }
.match-score { font-size: 48px; font-weight: bold; color: #409eff; }
.match-label { color: #666; margin: 8px 0; }
.match-detail { text-align: left; margin-top: 12px; font-size: 13px; }
.match-detail p { margin: 6px 0; }
.suggestions { padding-left: 20px; }
.suggestions li { margin: 6px 0; }
.report-footer { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; padding-top: 12px; border-top: 1px solid #ddd; }
.raw-data { padding: 12px; background: #f5f7fa; border-radius: 6px; }
.raw-data pre { overflow: auto; font-size: 12px; }
</style>
