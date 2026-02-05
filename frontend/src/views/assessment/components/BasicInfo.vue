<template>
  <el-card>
    <div class="basic-info-header">
      <h3>被评估者信息（静态画像）</h3>
      <div class="sub">初始化候选人向量空间，信息将绑定 candidate_id 存入后端数据库与特征存储</div>
    </div>

    <el-form :model="form" label-width="100px" class="basic-form">
      <el-form-item label="候选人 ID">
        <el-input v-model="form.id" disabled placeholder="系统自动生成" />
        <div class="hint">全局唯一标识，用于绑定后续评估数据</div>
      </el-form-item>

      <el-form-item label="姓名">
        <el-input v-model="form.name" placeholder="请输入姓名" />
      </el-form-item>

      <el-form-item label="年龄">
        <el-input-number v-model="form.age" :min="16" :max="100" />
      </el-form-item>

      <el-form-item label="学历">
        <el-select v-model="form.education" placeholder="请选择学历">
          <el-option label="大专" value="大专" />
          <el-option label="本科" value="本科" />
          <el-option label="硕士" value="硕士" />
          <el-option label="博士" value="博士" />
        </el-select>
      </el-form-item>

      <el-form-item label="专业">
        <el-input v-model="form.major" placeholder="专业" />
      </el-form-item>

      <el-form-item label="期望岗位">
        <el-select v-model="form.desired_job" placeholder="从HR发布的岗位中选择" :loading="jobsLoading">
          <el-option v-for="job in availableJobs" :key="job.id" :label="job.title" :value="job.id" />
        </el-select>
        <div class="hint">从HR系统同步的岗位列表</div>
      </el-form-item>

      <el-form-item label="工作经验">
        <el-input-number v-model="form.experience_years" :min="0" :max="50" /> 年
      </el-form-item>

      <el-form-item label="技能标签">
        <el-select 
          v-model="form.skills" 
          multiple 
          placeholder="选择预设技能或输入自定义标签"
          filterable
          allow-create
          default-first-option
        >
          <el-option v-for="skill in availableSkills" :key="skill" :label="skill" :value="skill" />
        </el-select>
        <div class="hint">支持预设技能或自定义输入（回车确认）</div>
      </el-form-item>

      <el-form-item>
        <div class="actions">
          <el-button @click="onCancel">取消</el-button>
          <el-button type="primary" @click="onSave">保存并下一步</el-button>
        </div>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{ candidate?: Record<string, any> }>()
const emit = defineEmits<{
  (e: 'save', payload: Record<string, any>): void
  (e: 'next'): void
  (e: 'cancel'): void
}>()

// 预设技能标签
const availableSkills = ref<string[]>([
  'JavaScript', 'Python', 'Java', 'Go',
  'Vue', 'React', 'Angular',
  'SQL', 'MongoDB',
  '产品设计', '数据分析', '项目管理',
  '系统设计', '架构设计'
])

// HR岗位列表
const availableJobs = ref<Array<{ id: string; title: string }>>([])
const jobsLoading = ref(false)

const form = reactive({
  id: props.candidate?.id ?? generateCandidateId(),
  name: props.candidate?.name ?? '',
  age: props.candidate?.age ?? 25,
  education: props.candidate?.education ?? '本科',
  major: props.candidate?.major ?? '',
  desired_job: props.candidate?.desired_job ?? '',
  experience_years: props.candidate?.experience_years ?? 0,
  skills: props.candidate?.skills ?? []
})

// 生成全局唯一 candidate_id
function generateCandidateId(): string {
  return `candidate_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 从后端获取HR发布的岗位
async function fetchAvailableJobs() {
  jobsLoading.value = true
  try {
    // TODO: 替换为实际后端API
    // const response = await fetch('/api/hr/jobs')
    // availableJobs.value = await response.json()
    
    // 演示数据
    availableJobs.value = [
      { id: 'job_001', title: '前端工程师' },
      { id: 'job_002', title: '后端工程师' },
      { id: 'job_003', title: '全栈工程师' },
      { id: 'job_004', title: '产品经理' },
      { id: 'job_005', title: '数据分析师' }
    ]
  } catch (error) {
    ElMessage.error('加载岗位列表失败')
  } finally {
    jobsLoading.value = false
  }
}

function onSave() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入姓名')
    return
  }
  if (!form.desired_job) {
    ElMessage.warning('请选择期望岗位')
    return
  }

  ElMessage.success('基础信息已保存，候选人向量空间已初始化')
  emit('save', { ...form })
  emit('next')
}

function onCancel() {
  emit('cancel')
}

onMounted(() => {
  fetchAvailableJobs()
})
</script>

<style scoped>
.basic-info-header { margin-bottom: 16px }
.basic-info-header h3 { margin: 0; font-size: 16px }
.basic-info-header .sub { color: #666; font-size: 13px; margin-top: 4px }
.basic-form { max-width: 680px }
.hint { color: #909399; font-size: 12px; margin-top: 4px }
.actions { display: flex; gap: 10px; justify-content: flex-end }
</style>
