<template>
  <el-card>
    <div class="basic-info-header">
      <h3>被评估者信息（静态画像）</h3>
      <div class="sub">请确认或填写候选人基本信息，保存后进入下一步。</div>
    </div>

    <el-form :model="form" label-width="100px" class="basic-form">
      <el-form-item label="姓名 / 编号">
        <el-input v-model="form.name" placeholder="姓名 / 编号" />
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
        <el-input v-model="form.desired_job" placeholder="期望岗位" />
      </el-form-item>

      <el-form-item label="工作经验">
        <el-input-number v-model="form.experience_years" :min="0" :max="50" /> 年
      </el-form-item>

      <el-form-item label="技能标签">
        <el-select v-model="form.skills" multiple placeholder="选择或输入技能标签" filterable>
          <el-option label="JavaScript" value="JavaScript" />
          <el-option label="Python" value="Python" />
          <el-option label="产品设计" value="产品设计" />
          <el-option label="数据分析" value="数据分析" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <div class="actions">
          <el-button @click="onCancel">取消</el-button>
          <el-button type="primary" @click="onSave" :loading="loading">保存并下一步</el-button>
        </div>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { saveBasicInfo } from '@/api/candidate'

const props = defineProps<{ candidateId?: string; candidate?: Record<string, any> }>()
const emit = defineEmits<{
  (e: 'save', payload: Record<string, any>): void
  (e: 'next'): void
  (e: 'cancel'): void
}>()

const loading = ref(false)

// 获取 candidateId，优先级：props.candidateId > candidate.id > 'temp-' + timestamp
const candidateId = computed(() => {
  return props.candidateId || props.candidate?.id || `temp-${Date.now()}`
})

const form = reactive({
  name: props.candidate?.name ?? '测试用户',
  age: props.candidate?.age ?? 28,
  education: props.candidate?.education ?? '本科',
  major: props.candidate?.major ?? '计算机科学',
  desired_job: props.candidate?.desired_job ?? '前端工程师',
  experience_years: props.candidate?.experience_years ?? 3,
  skills: props.candidate?.skills ?? ['JavaScript', 'Vue']
})

async function onSave() {
  loading.value = true
  try {
    await saveBasicInfo(candidateId.value, { ...form })
    ElMessage.success('基础信息已保存')
    emit('save', { id: candidateId.value, ...form })
    emit('next')
  } catch (error: any) {
    console.error('保存失败:', error)
    
    // 优化错误提示
    if (error.message?.includes('timeout')) {
      ElMessage.error('请求超时，请检查后端服务是否运行（python main.py）')
    } else if (error.response?.status === 404) {
      ElMessage.error('后端服务未找到，请确保服务运行在 http://127.0.0.1:8000')
    } else if (error.response?.status === 500) {
      ElMessage.error('服务器错误：' + (error.response?.data?.detail || '未知错误'))
    } else if (!error.response) {
      ElMessage.error('无法连接到服务器，请检查后端是否运行')
    } else {
      ElMessage.error('保存失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

function onCancel() {
  emit('cancel')
}
</script>

<style scoped>
.basic-info-header { margin-bottom: 12px }
.basic-info-header h3 { margin: 0 }
.basic-info-header .sub { color: #666; font-size: 13px }
.basic-form { max-width: 680px }
.actions { display:flex; gap:10px; justify-content:flex-end }
</style>
