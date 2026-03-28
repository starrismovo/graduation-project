<template>
  <div class="job-requirements-editor">
    <!-- HR - 编辑岗位需求 -->
    <div v-if="isHR" class="hr-section">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span class="title">📋 编辑岗位需求</span>
            <el-button type="primary" size="small" @click="parseJD">生成需求</el-button>
          </div>
        </template>

        <!-- Step 1: 上传 JD 文本 -->
        <el-form :model="formData" label-width="120px" class="form-section">
          <el-form-item label="岗位名称">
            <el-input v-model="formData.jobName" placeholder="如: 高级 Python 工程师" />
          </el-form-item>

          <el-form-item label="岗位类别">
            <el-select v-model="formData.roleCategory" placeholder="选择岗位类别">
              <el-option label="后端开发" value="backend" />
              <el-option label="前端开发" value="frontend" />
              <el-option label="产品管理" value="product" />
              <el-option label="设计" value="design" />
              <el-option label="HR" value="hr" />
              <el-option label="管理" value="management" />
            </el-select>
          </el-form-item>

          <el-form-item label="岗位描述 (JD)">
            <el-input
              v-model="formData.jdText"
              type="textarea"
              rows="6"
              placeholder="粘贴完整的岗位描述..."
            />
          </el-form-item>
        </el-form>

        <!-- Step 2: 自动生成的技能列表 -->
        <div class="section">
          <h3>📌 所需技能（{{ filteredSkills.length }}）</h3>
          <div class="skills-grid">
            <div
              v-for="(skill, idx) in formData.skills"
              :key="idx"
              class="skill-card"
              :class="{ 'must-have': skill.is_must_have }"
            >
              <div class="skill-header">
                <span class="skill-name">{{ skill.skill_name }}</span>
                <el-button-group>
                  <el-button
                    v-if="skill.is_must_have"
                    type="danger"
                    text
                    size="small"
                    @click="skill.is_must_have = false"
                  >
                    必需
                  </el-button>
                  <el-button v-else type="info" text size="small" @click="skill.is_must_have = true">
                    可选
                  </el-button>
                  <el-button type="danger" text size="small" @click="formData.skills.splice(idx, 1)">
                    删除
                  </el-button>
                </el-button-group>
              </div>
              <div class="skill-details">
                <span>等级: {{ skill.required_level || '未设定' }}</span>
                <span>优先级: {{ skill.priority_score }}/10</span>
                <span v-if="skill.years_experience">{{ skill.years_experience }}年经验</span>
              </div>
            </div>
          </div>
          <el-button text type="primary" @click="addSkill">+ 添加技能</el-button>
        </div>

        <!-- Step 3: 大五人格框架 -->
        <div class="section">
          <h3>🧠 大五人格要求</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="personality-item">
                <label>开放性 (Openness)</label>
                <el-slider
                  v-model="formData.personality_framework.openness_min"
                  :min="0"
                  :max="100"
                  show-stops
                />
                <span class="range-label">最小值: {{ formData.personality_framework.openness_min }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="personality-item">
                <label>尽责性 (Conscientiousness)</label>
                <el-slider
                  v-model="formData.personality_framework.conscientiousness_min"
                  :min="0"
                  :max="100"
                  show-stops
                />
                <span class="range-label"
                  >最小值: {{ formData.personality_framework.conscientiousness_min }}</span
                >
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="personality-item">
                <label>外向性 (Extraversion)</label>
                <el-slider
                  v-model="formData.personality_framework.extraversion_min"
                  :min="0"
                  :max="100"
                  show-stops
                />
                <span class="range-label"
                  >最小值: {{ formData.personality_framework.extraversion_min }}</span
                >
              </div>
            </el-col>
            <el-col :span="12">
              <div class="personality-item">
                <label>宜人性 (Agreeableness)</label>
                <el-slider
                  v-model="formData.personality_framework.agreeableness_min"
                  :min="0"
                  :max="100"
                  show-stops
                />
                <span class="range-label"
                  >最小值: {{ formData.personality_framework.agreeableness_min }}</span
                >
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="personality-item">
                <label>神经质 (Neuroticism) - 越低越好</label>
                <el-slider
                  v-model="formData.personality_framework.neuroticism_max"
                  :min="0"
                  :max="100"
                  show-stops
                />
                <span class="range-label">最大值: {{ formData.personality_framework.neuroticism_max }}</span>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 保存按钮 -->
        <div class="footer">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" @click="saveRequirements" :loading="loading">
            💾 保存岗位需求
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 候选人 - 选择岗位 -->
    <div v-else class="candidate-section">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span class="title">🎯 选择应聘岗位</span>
            <el-button type="primary" size="small" @click="loadAvailableJobs">刷新</el-button>
          </div>
        </template>

        <!-- 岗位列表 -->
        <div class="jobs-list">
          <div
            v-for="job in availableJobs"
            :key="job.id"
            class="job-item"
            :class="{ selected: selectedJob?.id === job.id }"
            @click="selectedJob = job"
          >
            <div class="job-header">
              <h4>{{ job.name }}</h4>
              <el-tag type="success">{{ job.category }}</el-tag>
            </div>
            <p class="job-description">{{ job.description }}</p>
            <div class="job-meta">
              <span>📍 {{ job.city }}</span>
              <span>💰 ¥{{ job.salary_min }}k - ¥{{ job.salary_max }}k</span>
            </div>
          </div>
        </div>

        <!-- 选中岗位的详细需求 -->
        <div v-if="selectedJob" class="job-details">
          <el-divider />
          <h3>📋 岗位详细需求</h3>

          <!-- 所需技能 -->
          <div class="detail-section">
            <h4>所需技能</h4>
            <div class="skills-display">
              <el-tag
                v-for="skill in selectedJobRequirements?.skills || []"
                :key="skill.skill_name"
                :type="skill.is_must_have ? 'danger' : 'info'"
                effect="dark"
              >
                {{ skill.skill_name }} {{ skill.is_must_have ? '(必需)' : '' }}
              </el-tag>
            </div>
          </div>

          <!-- 大五人格要求 -->
          <div class="detail-section">
            <h4>大五人格要求</h4>
            <div class="personality-display">
              <el-row :gutter="20">
                <el-col :span="8" v-if="selectedJobRequirements?.personality_framework">
                  <div class="trait-info">
                    <span class="trait-label">开放性:</span>
                    <span class="trait-value"
                      >最低 {{
                        selectedJobRequirements.personality_framework.openness_min
                      }}</span
                    >
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="trait-info">
                    <span class="trait-label">尽责性:</span>
                    <span class="trait-value"
                      >最低 {{
                        selectedJobRequirements?.personality_framework
                          ?.conscientiousness_min
                      }}</span
                    >
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>

          <!-- 应聘按钮 -->
          <div class="footer">
            <el-button @click="selectedJob = null">取消</el-button>
            <el-button type="primary" @click="handleApplyForJob" :loading="applying">
              🚀 确认应聘
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 应聘历史 -->
      <el-card class="box-card" style="margin-top: 20px">
        <template #header>
          <span>📊 应聘记录</span>
        </template>

        <el-table :data="applications" stripe>
          <el-table-column prop="job.name" label="岗位" width="200" />
          <el-table-column prop="job.company" label="公司" width="150" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.application_status)">
                {{ getStatusLabel(row.application_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="personality_match_score" label="人格匹配" width="120">
            <template #default="{ row }">
              {{ row.personality_match_score ? row.personality_match_score + '%' : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="applied_at" label="应聘时间" width="180" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createJobRequirementsFromJD,
  updateJobRequirements,
  getJobRequirements,
  applyForJob,
  getCandidateApplications,
  getJobMatch,
  getAllJobs,
  getJobDetail
} from '@/api/job'

// Props & Emits
const props = defineProps({
  mode: {
    type: String,
    default: 'auto', // 'auto' | 'hr' | 'candidate'
  },
  candidateId: {
    type: [Number, null],
    default: null,
    validator: (val) => {
      // 允许 null 或正整数
      if (val === null || val === undefined) return true
      if (typeof val === 'number' && val > 0 && Number.isInteger(val)) return true
      console.warn('【JobRequirementsManager】Invalid candidateId:', val, 'Expected null or positive integer')
      return false
    }
  },
})

const emit = defineEmits(['job-selected', 'apply-job', 'job-applied'])

const isHR = ref(false) // 由登录状态决定
const loading = ref(false)
const applying = ref(false)

// HR 表单数据
const formData = ref({
  jobName: '',
  roleCategory: 'backend',
  jdText: '',
  skills: [],
  requirement_tags: [],
  personality_framework: {
    openness_min: 30,
    openness_max: 100,
    openness_weight: 1.0,
    conscientiousness_min: 50,
    conscientiousness_max: 100,
    conscientiousness_weight: 1.5,
    extraversion_min: 20,
    extraversion_max: 100,
    extraversion_weight: 1.0,
    agreeableness_min: 40,
    agreeableness_max: 100,
    agreeableness_weight: 1.0,
    neuroticism_min: 0,
    neuroticism_max: 60,
    neuroticism_weight: 1.2,
  },
})

// 候选人数据
const availableJobs = ref([])
const selectedJob = ref(null)
const selectedJobRequirements = ref(null)
const applications = ref([])

// 计算属性
const filteredSkills = computed(() => {
  return formData.value.skills.filter((s) => s.is_must_have)
})

// 方法 - HR
const parseJD = async () => {
  if (!formData.value.jdText.trim()) {
    ElMessage.warning('请输入岗位描述')
    return
  }

  loading.value = true
  try {
    const response = await createJobRequirementsFromJD({
      job_id: formData.value.jobId,
      jd_text: formData.value.jdText,
      role_category: formData.value.roleCategory,
    })

    if (response.data?.code === 200 || response.status === 200) {
      ElMessage.success('岗位需求已自动生成！')
      // 更新表单数据...
    }
  } catch (error) {
    ElMessage.error('生成失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const addSkill = () => {
  formData.value.skills.push({
    skill_name: '',
    skill_type: 'tool',
    required_level: 'intermediate',
    years_experience: null,
    is_must_have: false,
    priority_score: 5,
  })
}

const saveRequirements = async () => {
  if (!formData.value.skills.length) {
    ElMessage.warning('请至少添加一项技能需求')
    return
  }

  loading.value = true
  try {
    const response = await updateJobRequirements({
      job_id: formData.value.jobId,
      skills: formData.value.skills,
      requirement_tags: formData.value.requirement_tags,
      personality_framework: formData.value.personality_framework,
    })

    if (response.data?.code === 200 || response.status === 200) {
      ElMessage.success('岗位需求已保存！')
    }
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  ElMessageBox.confirm('确定要重置表单吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    formData.value = {
      jobName: '',
      roleCategory: 'backend',
      jdText: '',
      skills: [],
      requirement_tags: [],
      personality_framework: { ...formData.value.personality_framework },
    }
  })
}

// 方法 - 候选人
const loadAvailableJobs = async () => {
  try {
    const response = await getAllJobs()
    availableJobs.value = response.data?.data || response.data || []
  } catch (error) {
    ElMessage.error('加载岗位失败：' + error.message)
  }
}

const loadJobRequirements = async (jobId) => {
  try {
    const response = await getJobRequirements(jobId)
    selectedJobRequirements.value = response.data
  } catch (error) {
    ElMessage.error('加载岗位需求失败：' + error.message)
  }
}

const handleApplyForJob = async () => {
  if (!selectedJob.value) return

  applying.value = true
  try {
    // 获取候选人 ID，支持多种方式
    let candidateId = props.candidateId
    console.log('【handleApplyForJob】第1步 - props.candidateId:', {
      value: candidateId,
      type: typeof candidateId,
      isNaN: Number.isNaN(candidateId),
      isValid: candidateId && !Number.isNaN(candidateId) && Number.isInteger(candidateId)
    })
    
    // 检查 props 是否已经是 NaN
    if (Number.isNaN(candidateId)) {
      console.warn('【handleApplyForJob】Props 中收到 NaN，尝试从 localStorage 获取')
      const storedId = localStorage.getItem('candidateId')
      candidateId = storedId ? parseInt(storedId) : null
    }
    
    if (!candidateId) {
      const storedId = localStorage.getItem('candidateId')
      console.log('【handleApplyForJob】第2步 - localStorage.candidateId:', storedId)
      candidateId = storedId ? parseInt(storedId) : null
      console.log('【handleApplyForJob】第2步-处理后:', {
        candidateId,
        isNaN: Number.isNaN(candidateId)
      })
    }
    
    // 验证 candidateId
    if (!candidateId || Number.isNaN(candidateId) || !Number.isInteger(Number(candidateId))) {
      console.error('【handleApplyForJob】无效的 candidateId:', {
        value: candidateId,
        isNaN: Number.isNaN(candidateId)
      })
      ElMessage.error('无法获取候选人ID，请重新登录')
      applying.value = false
      return
    }
    
    console.log('【handleApplyForJob】第3步 - 发送应聘请求:', {
      candidate_id: candidateId,
      job_id: selectedJob.value.id
    })
    
    const response = await applyForJob({
      candidate_id: candidateId,
      job_id: selectedJob.value.id,
    })

    console.log('【handleApplyForJob】第4步 - 收到响应:', {
      status: response.status,
      code: response.data?.code
    })

    if (response.data?.code === 200 || response.status === 200) {
      ElMessage.success('应聘成功！')
      
      // 发出 apply-job 事件
      emit('apply-job', {
        jobId: selectedJob.value.id,
        jobName: selectedJob.value.title || selectedJob.value.name,
        candidateId: candidateId,
      })
      
      await loadApplications()
      selectedJob.value = null
    }
  } catch (error) {
    ElMessage.error('应聘失败：' + error.message)
  } finally {
    applying.value = false
  }
}

const loadApplications = async () => {
  try {
    // 获取候选人 ID，支持多种方式
    let candidateId = props.candidateId
    console.log('【loadApplications】第1步 - props.candidateId:', {
      value: candidateId,
      type: typeof candidateId,
      isValid: candidateId && !isNaN(Number(candidateId))
    })
    
    if (!candidateId) {
      const storedId = localStorage.getItem('candidateId')
      console.log('【loadApplications】第2步 - localStorage.candidateId:', {
        value: storedId,
        type: typeof storedId,
        isNull: storedId === null
      })
      
      candidateId = storedId ? parseInt(storedId) : null
      console.log('【loadApplications】第2步-处理后:', {
        candidateId,
        isNaN: isNaN(candidateId)
      })
    }
    
    // 验证 candidateId
    if (!candidateId || isNaN(Number(candidateId))) {
      console.warn('【loadApplications】无效的 candidateId:', {
        candidateId,
        timestamp: new Date().toLocaleTimeString()
      })
      return
    }
    
    console.log('【loadApplications】第3步 - 获取应聘记录，candidateId:', candidateId)
    
    const response = await getCandidateApplications(candidateId)
    console.log('【loadApplications】第4步 - 收到响应:', {
      status: response.status,
      dataLength: response.data?.length || 0
    })
    
    applications.value = response.data
  } catch (error) {
    console.error('【loadApplications】错误:', {
      message: error.message,
      stack: error.stack
    })
    ElMessage.error('加载应聘记录失败：' + error.message)
  }
}

const getStatusType = (status) => {
  const types = {
    applied: 'info',
    personality_assessed: 'warning',
    interviewing: 'primary',
    passed: 'success',
    rejected: 'danger',
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    applied: '已申请',
    personality_assessed: '已评估',
    interviewing: '面试中',
    passed: '通过',
    rejected: '未通过',
  }
  return labels[status] || status
}

onMounted(() => {
  // 检查用户类型：优先使用 props.mode，其次检查 localStorage
  let userType
  if (props.mode === 'auto') {
    userType = localStorage.getItem('userType')
  } else if (props.mode === 'hr') {
    userType = 'HR'
  } else if (props.mode === 'candidate') {
    userType = 'CANDIDATE'
  }
  
  isHR.value = userType === 'HR'

  if (isHR.value) {
    // HR 初始化
    formData.value.jobId = parseInt(localStorage.getItem('jobId')) || 1
  } else {
    // 候选人初始化
    loadAvailableJobs()
    loadApplications()
  }
})

// 监察
const watchSelectedJob = async (job) => {
  if (job) {
    await loadJobRequirements(job.id)
    // 发出 job-selected 事件
    emit('job-selected', job.id)
  }
}

watch(selectedJob, watchSelectedJob)
</script>

<style scoped lang="scss">
.job-requirements-editor {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: bold;
    }
  }

  .form-section {
    margin-bottom: 20px;
  }

  .section {
    margin: 20px 0;

    h3 {
      border-bottom: 2px solid #409eff;
      padding-bottom: 10px;
      margin-bottom: 15px;
    }

    h4 {
      margin-bottom: 10px;
      color: #333;
    }
  }

  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 15px;
    margin-bottom: 15px;

    .skill-card {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 15px;
      background: #f9f9f9;
      transition: all 0.3s;

      &.must-have {
        border-color: #f56c6c;
        background: #fef0f0;
      }

      &:hover {
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .skill-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        .skill-name {
          font-weight: bold;
          font-size: 14px;
        }
      }

      .skill-details {
        display: flex;
        flex-direction: column;
        gap: 5px;
        font-size: 12px;
        color: #666;
      }
    }
  }

  .personality-item {
    margin-bottom: 20px;

    label {
      display: block;
      margin-bottom: 10px;
      font-weight: bold;
      color: #333;
    }

    .range-label {
      display: block;
      margin-top: 5px;
      font-size: 12px;
      color: #666;
    }
  }

  .jobs-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
    margin-bottom: 20px;

    .job-item {
      border: 2px solid #ddd;
      border-radius: 8px;
      padding: 15px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: #409eff;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
      }

      &.selected {
        border-color: #409eff;
        background: #f0f9ff;
      }

      .job-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        h4 {
          margin: 0;
          color: #333;
        }
      }

      .job-description {
        font-size: 13px;
        color: #666;
        margin: 10px 0;
        line-height: 1.5;
      }

      .job-meta {
        display: flex;
        gap: 15px;
        font-size: 12px;
        color: #999;
      }
    }
  }

  .job-details {
    background: #f5f7fa;
    padding: 20px;
    border-radius: 8px;

    .detail-section {
      margin-bottom: 20px;

      h4 {
        margin-bottom: 10px;
      }

      .skills-display {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      .personality-display {
        .trait-info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;

          .trait-label {
            font-weight: bold;
          }

          .trait-value {
            color: #409eff;
            font-weight: bold;
          }
        }
      }
    }
  }

  .footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
}
</style>
