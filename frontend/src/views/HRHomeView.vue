<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted } from 'vue'
import { getJobs } from '../utils/request'
import { Delete, Edit, View, Plus } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

// 岗位列表
const jobsList = ref<any[]>([])
const loading = ref(true)

// 对话框相关
const showCreateDialog = ref(false)
const createFormData = ref({
  name: '',
  description: '',
  company: '',
  category: '',
  city: '',
  salary_min: '',
  salary_max: ''
})

// 统计数据（假数据）
const stats = ref({
  totalJobs: 0,
  pendingReview: 12,
  avgMatchScore: 78.5
})

// 加载岗位列表
const loadJobs = async () => {
  try {
    loading.value = true
    const response = await getJobs({})
    jobsList.value = response.data || []
    stats.value.totalJobs = jobsList.value.length
  } catch (error) {
    console.error('加载岗位列表失败:', error)
    ElMessage.error('加载岗位列表失败')
  } finally {
    loading.value = false
  }
}

// 创建新岗位
const handleCreateJob = async () => {
  if (!createFormData.value.name || !createFormData.value.description) {
    ElMessage.warning('请填写岗位名称和描述')
    return
  }
  
  // 这里后续需要调用创建岗位的API
  ElMessage.success('岗位创建成功（功能开发中）')
  showCreateDialog.value = false
  resetCreateForm()
}

// 重置表单
const resetCreateForm = () => {
  createFormData.value = {
    name: '',
    description: '',
    company: '',
    category: '',
    city: '',
    salary_min: '',
    salary_max: ''
  }
}

// 编辑岗位
const handleEditJob = (job: any) => {
  ElMessage.info(`编辑岗位: ${job.name}（功能开发中）`)
  // router.push(`/hr/edit-job/${job.id}`)
}

// 删除岗位
const handleDeleteJob = (job: any) => {
  ElMessageBox.confirm(
    `确定要删除岗位 "${job.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      ElMessage.success('岗位删除成功（功能开发中）')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}
// 查看候选人报告
const handleViewReport = (job: any) => {
  ElMessage.info(`查看岗位 "${job.name}" 的候选人报告（功能开发中）`)
  // router.push(`/hr/job-report/${job.id}`)
}

onMounted(() => {
  loadJobs()
})
</script>

<template>
  <div class="hr-home-container">
    <!-- 欢迎区 -->
    <div class="welcome-section">
      <div class="welcome-card">
        <h2>欢迎来到HR管理主页</h2>
        <p>快速管理岗位或查看候选人评估报告</p>
      </div>
    </div>

    <!-- 主容器 -->
    <div class="main-content">
      <!-- 左侧：岗位管理 -->
      <div class="jobs-section">
        <div class="section-header">
          <h3>岗位管理</h3>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建新岗位
          </el-button>
        </div>

        <!-- 岗位表格 -->
        <el-table
          :data="jobsList"
          stripe
          style="width: 100%"
          :loading="loading"
          empty-text="暂无岗位"
        >
          <el-table-column prop="name" label="岗位名称" width="150" />
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="company" label="公司" width="120" />
          <el-table-column prop="category" label="类别" width="100" />
          <el-table-column prop="city" label="城市" width="100" />
          <el-table-column label="薪资范围" width="150">
            <template #default="{ row }">
              {{ row.salary_min }}k - {{ row.salary_max }}k
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleDateString('zh-CN') }}
            </template>
          </el-table-column>
          <el-table-column label="候选人数" width="100">
            <template #default="{ row }">
              <el-tag>{{ Math.floor(Math.random() * 10) + 1 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" :icon="View" @click="handleViewReport(row)">
                查看报告
              </el-button>
              <el-button link type="warning" :icon="Edit" @click="handleEditJob(row)">
                编辑
              </el-button>
              <el-button link type="danger" :icon="Delete" @click="handleDeleteJob(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 右侧：数据概览 -->
      <div class="overview-section">
        <!-- 统计卡片 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-value">{{ stats.totalJobs }}</div>
            <div class="stat-label">发布岗位</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.pendingReview }}</div>
            <div class="stat-label">待评估</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.avgMatchScore }}%</div>
            <div class="stat-label">平均匹配度</div>
          </div>
        </div>

        <!-- 快速入口 -->
        <div class="quick-actions">
          <h4>快速入口</h4>
          <el-button class="action-btn" type="primary" plain block>
            查看所有候选人报告
          </el-button>
          <el-button class="action-btn" type="success" plain block>
            团队管理
          </el-button>
          <el-button class="action-btn" type="info" plain block>
            数据分析
          </el-button>
        </div>

        <!-- 最近活动 -->
        <div class="recent-activity">
          <h4>最近岗位</h4>
          <div class="activity-list">
            <div v-if="jobsList.length === 0" class="empty-state">
              暂无岗位
            </div>
            <div v-for="job in jobsList.slice(0, 3)" :key="job.id" class="activity-item">
              <div class="activity-title">{{ job.name }}</div>
              <div class="activity-time">
                {{ new Date(job.created_at).toLocaleDateString('zh-CN') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建岗位对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建新岗位" width="500px">
      <el-form :model="createFormData" label-width="100px">
        <el-form-item label="岗位名称" required>
          <el-input v-model="createFormData.name" placeholder="请输入岗位名称" />
        </el-form-item>
        <el-form-item label="岗位描述" required>
          <el-input
            v-model="createFormData.description"
            placeholder="请输入岗位描述"
            type="textarea"
            rows="3"
          />
        </el-form-item>
        <el-form-item label="所属公司">
          <el-input v-model="createFormData.company" placeholder="请输入公司名称" />
        </el-form-item>
        <el-form-item label="岗位类别">
          <el-select v-model="createFormData.category" placeholder="请选择岗位类别">
            <el-option label="技术" value="技术" />
            <el-option label="产品" value="产品" />
            <el-option label="设计" value="设计" />
            <el-option label="运营" value="运营" />
            <el-option label="销售" value="销售" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作城市">
          <el-select v-model="createFormData.city" placeholder="请选择城市">
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="深圳" value="深圳" />
            <el-option label="杭州" value="杭州" />
            <el-option label="南京" value="南京" />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资范围(k)">
          <el-input-number v-model.number="createFormData.salary_min" placeholder="最低" />
          <span style="margin: 0 10px">-</span>
          <el-input-number v-model.number="createFormData.salary_max" placeholder="最高" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateJob">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.hr-home-container {
  min-height: 100%;
  background: transparent;
}

/* 欢迎区 */
.welcome-section {
  padding: 24px 0;
  margin-bottom: 24px;
}

.welcome-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.welcome-card h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #333;
}

.welcome-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.welcome-card h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #333;
}

.welcome-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 主容器布局 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

/* 岗位管理区 */
.jobs-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 数据概览区 */
.overview-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.quick-actions {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-actions h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.action-btn {
  margin-bottom: 8px !important;
  font-size: 13px;
}

.recent-activity {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recent-activity h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 8px;
}

.activity-item {
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-title {
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 11px;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
