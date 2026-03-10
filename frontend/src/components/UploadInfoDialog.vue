<template>
  <el-dialog
    v-model:visible="visible"
    title="完善个人信息"
    width="600px"
    append-to-body
    destroy-on-close
  >
    <div class="upload-area">
      <el-upload
        drag
        action="#"
        :auto-upload="false"
        @change="handleResumeUpload"
        accept=".pdf,.doc,.docx"
      >
        <el-icon class="el-icon-upload"><i class="el-icon-upload"></i></el-icon>
        <div class="el-upload__text">拖拽或<em>点击</em>上传简历</div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF、Word 格式，文件大小不超过 10MB</div>
        </template>
      </el-upload>

      <div class="info-form">
        <el-input 
          v-model="localInfo.name" 
          placeholder="姓名"
          class="form-item"
        />
        <el-input 
          v-model="localInfo.email" 
          placeholder="邮箱"
          class="form-item"
        />
        <el-select 
          v-model="localInfo.education" 
          placeholder="学历"
          class="form-item"
        >
          <el-option label="高中" value="高中" />
          <el-option label="大专" value="大专" />
          <el-option label="本科" value="本科" />
          <el-option label="硕士" value="硕士" />
          <el-option label="博士" value="博士" />
        </el-select>
      </div>
    </div>

    <template #footer>
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="confirm">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'  // defineProps/defineEmits are compiler macros, no need to import

interface CandidateInfo {
  name: string
  email: string
  education: string
}

const props = defineProps<{
  modelValue: boolean
  info: CandidateInfo
}>()
const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
  (e: 'confirm', info: CandidateInfo): void
  (e: 'cancel'): void
  (e: 'upload', file: File): void
}>()

const visible = ref(props.modelValue)

const localInfo = ref<CandidateInfo>({
  name: props.info?.name || '',
  email: props.info?.email || '',
  education: props.info?.education || ''
})

// 监听 modelValue props 变化，同步到 visible
watch(() => props.modelValue, (newVal) => {
  console.log('[UploadInfoDialog] props.modelValue changed to:', newVal)
  console.log('[UploadInfoDialog] visible ref before:', visible.value)
  visible.value = newVal
  console.log('[UploadInfoDialog] visible ref after:', visible.value)
}, { immediate: true })

// 监听 visible 变化，同步到父组件
watch(() => visible.value, (newVal) => {
  console.log('UploadInfoDialog: visible changed to:', newVal)
  if (newVal !== props.modelValue) {
    console.log('UploadInfoDialog: emitting update:modelValue =', newVal)
    emit('update:modelValue', newVal)
  }
})

// 当 props.info 更新时，同步 localInfo
watch(() => props.info, (newInfo) => {
  if (newInfo) {
    localInfo.value = {
      name: newInfo.name || '',
      email: newInfo.email || '',
      education: newInfo.education || ''
    }
  }
}, { deep: true })

function handleResumeUpload(file: any) {
  emit('upload', file.raw)
}

function confirm() {
  emit('confirm', localInfo.value)
  visible.value = false
}

function cancel() {
  emit('cancel')
  visible.value = false
}
</script>

<style scoped>
.upload-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-form {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-item {
  font-size: 13px;
}
</style>