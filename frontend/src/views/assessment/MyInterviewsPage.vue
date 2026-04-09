<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { fetchHistory } from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const records = ref<any[]>([])
const statusFilter = ref('')

const filteredRecords = computed(() => {
  if (!statusFilter.value) return records.value
  return records.value.filter((item) => item.assessment_status === statusFilter.value)
})

function getStatusLabel(status: string) {
  if (status === 'completed') return '已完成'
  if (status === 'pending') return '进行中'
  if (status === 'failed') return '失败'
  return '未知'
}

function getStatusType(status: string) {
  if (status === 'completed') return 'success'
  if (status === 'pending') return 'warning'
  if (status === 'failed') return 'danger'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadInterviewHistory() {
  const candidateId = userStore.userId || userStore.profile?.id
  if (!candidateId) {
    ElMessage.error('未获取到用户信息')
    return
  }

  loading.value = true
  try {
    const data = await fetchHistory(candidateId)
    records.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载面试记录失败:', error)
    ElMessage.error('加载面试记录失败')
  } finally {
    loading.value = false
  }
}

function goToInterview(record: any) {
  router.push({
    path: '/home/interviews',
    query: {
      jobId: String(record.job_id)
    }
  })
}

function viewReport(recordId: number) {
  router.push(`/home/report/${recordId}`)
}

onMounted(() => {
  loadInterviewHistory()
})
</script>

<template>
  <div class="my-interviews-page" v-loading="loading">
    <div class="page-header">
      <div>
        <h2>我的面试</h2>
        <p>查看从岗位浏览发起的 AI 面试记录和当前状态</p>
      </div>
      <div class="header-actions">
        <el-select v-model="statusFilter" placeholder="全部状态" clearable class="status-filter">
          <el-option label="全部状态" value="" />
          <el-option label="进行中" value="pending" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-button @click="loadInterviewHistory">刷新</el-button>
      </div>
    </div>

    <el-empty
      v-if="!loading && filteredRecords.length === 0"
      description="暂无面试记录"
    >
      <el-button type="primary" @click="router.push('/home/jobs')">去选择岗位</el-button>
    </el-empty>

    <div v-else class="record-list">
      <el-card
        v-for="record in filteredRecords"
        :key="record.id"
        class="record-card"
        shadow="hover"
      >
        <div class="record-main">
          <div class="record-info">
            <div class="title-row">
              <h3>{{ record.job_title || '未知岗位' }}</h3>
              <el-tag :type="getStatusType(record.assessment_status)">
                {{ getStatusLabel(record.assessment_status) }}
              </el-tag>
            </div>
            <p class="meta">发起时间：{{ formatDate(record.created_at) }}</p>
            <p class="meta">面试模式：{{ record.assessment_mode === 'immersive' ? '沉浸式 AI 面试' : record.assessment_mode }}</p>
            <p class="meta" v-if="record.match_score != null">当前匹配度：{{ Math.round(record.match_score) }}%</p>
          </div>

          <div class="record-actions">
            <el-button
              v-if="record.assessment_status === 'pending'"
              type="primary"
              @click="goToInterview(record)"
            >继续面试</el-button>
            <el-button
              v-else-if="record.assessment_status === 'completed'"
              type="primary"
              plain
              @click="viewReport(record.id)"
            >查看报告</el-button>
            <el-button v-else @click="goToInterview(record)">重新进入</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.my-interviews-page {
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  color: #1f2937;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status-filter {
  width: 140px;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.record-card {
  border-radius: 16px;
}

.record-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.record-info {
  flex: 1;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.title-row h3 {
  margin: 0;
  font-size: 20px;
  color: #111827;
}

.meta {
  margin: 4px 0;
  color: #6b7280;
}

.record-actions {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .page-header,
  .record-main {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions,
  .record-actions {
    width: 100%;
  }

  .status-filter {
    width: 100%;
  }
}
</style>