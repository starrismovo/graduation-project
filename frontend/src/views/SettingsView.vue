<template>
  <div class="settings-page">
    <el-page-header @back="goBack">
      <template #content>
        <h2>账号设置</h2>
      </template>
    </el-page-header>

    <div class="settings-layout">
      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <h3>账号安全</h3>
              <p>维护登录身份与联系方式，确保系统通知和账号找回路径可用。</p>
            </div>
          </div>
        </template>

        <el-form :model="securityForm" label-width="110px" class="settings-form">
          <el-form-item label="用户名">
            <el-input v-model="securityForm.username" disabled />
          </el-form-item>
          <el-form-item label="账号角色">
            <el-input :model-value="roleLabel" disabled />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="securityForm.email" placeholder="用于登录提醒、报告通知与账号找回" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="securityForm.phone" placeholder="用于联系确认与安全校验" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="savingSecurity" @click="saveSecurity">
              保存账号信息
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <h3>登录密码</h3>
              <p>通过原密码校验后更新登录密码，降低账号被误用或泄露的风险。</p>
            </div>
          </div>
        </template>

        <el-form :model="passwordForm" label-width="110px" class="settings-form">
          <el-form-item label="当前密码">
            <el-input
              v-model="passwordForm.currentPassword"
              type="password"
              show-password
              placeholder="请输入当前登录密码"
            />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              show-password
              placeholder="建议使用不少于 6 位的新密码"
            />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              show-password
              placeholder="请再次输入新密码"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="savingPassword" @click="changePassword">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <h3>流程提醒</h3>
              <p>围绕面试流程、评估报告和推荐更新提供提醒开关，避免遗漏关键进度。</p>
            </div>
          </div>
        </template>

        <el-form :model="notificationForm" label-width="0" class="settings-form wide-form">
          <div class="section-intro blue">
            通知内容将按业务场景展示为“面试邀请”“评估报告”“岗位推荐”等信息，不直接暴露后端系统对象名称。
          </div>

          <div class="switch-group">
            <div class="group-title">流程提醒</div>
            <div class="switch-list">
              <div class="switch-item">
                <div>
                  <h4>面试提醒</h4>
                  <p>在面试开始前或有新的面试邀请时提醒查看，避免错过流程节点。</p>
                </div>
                <el-switch v-model="notificationForm.notifyInterviewReminder" />
              </div>

              <div class="switch-item">
                <div>
                  <h4>面试流程完成提醒</h4>
                  <p>当一次完整评估流程结束后，提醒用户进入后续结果查看环节。</p>
                </div>
                <el-switch v-model="notificationForm.notifyAssessmentCompleted" />
              </div>

              <div class="switch-item">
                <div>
                  <h4>评估报告生成提醒</h4>
                  <p>当系统完成分析并生成评估报告后，及时提醒进入报告页面。</p>
                </div>
                <el-switch v-model="notificationForm.notifyReportReady" />
              </div>
            </div>
          </div>

          <div class="switch-group" v-if="!userStore.isHR">
            <div class="group-title">推荐提醒</div>
            <div class="switch-list">
              <div class="switch-item">
                <div>
                  <h4>岗位推荐更新提醒</h4>
                  <p>当系统基于最新评估结果更新推荐岗位时，在首页和通知中心提示查看。</p>
                </div>
                <el-switch v-model="notificationForm.notifyJobRecommendation" />
              </div>
            </div>
          </div>

          <div class="switch-group" v-if="userStore.isHR">
            <div class="group-title">招聘提醒</div>
            <div class="switch-list">
              <div class="switch-item">
                <div>
                  <h4>候选人投递提醒</h4>
                  <p>有新的候选人投递岗位时提醒查看，便于及时进入筛选与跟进流程。</p>
                </div>
                <el-switch v-model="notificationForm.notifyCandidateDelivery" />
              </div>

              <div class="switch-item">
                <div>
                  <h4>候选人评估完成提醒</h4>
                  <p>当候选人完成评估后提醒查看其评估报告，支持后续招聘决策。</p>
                </div>
                <el-switch v-model="notificationForm.notifyCandidateAssessmentCompleted" />
              </div>
            </div>
          </div>

          <el-form-item>
            <el-button type="primary" :loading="savingNotifications" @click="saveNotifications">
              保存提醒设置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <h3>隐私控制</h3>
              <p>控制投递与报告展示时的身份暴露程度，帮助用户在展示效果与信息保护之间取得平衡。</p>
            </div>
          </div>
        </template>

        <el-form :model="privacyForm" label-width="110px" class="settings-form wide-form">
          <div class="section-intro">
            本区域仅影响候选人在投递和报告查看场景下的展示方式，不改变系统后端保存的真实身份信息。
          </div>

          <el-form-item label="身份展示">
            <div class="privacy-options">
              <label
                v-for="option in privacyOptions"
                :key="option.value"
                :class="['privacy-option', { active: privacyForm.deliveryPrivacy === option.value }]"
              >
                <input v-model="privacyForm.deliveryPrivacy" type="radio" :value="option.value" />
                <div class="privacy-option-title">{{ option.title }}</div>
                <div class="privacy-option-desc">{{ option.description }}</div>
              </label>
            </div>
          </el-form-item>

          <el-form-item>
            <div class="privacy-tip">
              当前设置会影响候选人在“岗位投递”“面试流程”“评估报告”相关页面中的身份展示方式。
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="savingPrivacy" @click="savePrivacy">
              保存隐私设置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card danger-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <h3>数据管理</h3>
              <p>对历史评估数据进行风险较高的处理时，系统会通过显著警示和二次确认降低误操作概率。</p>
            </div>
          </div>
        </template>

        <div class="danger-panel">
          <div class="danger-badge-row">
            <span class="danger-badge">高风险操作</span>
            <span class="danger-note">删除后不可恢复</span>
          </div>

          <div class="danger-grid">
            <div class="danger-block">
              <div class="danger-block-title">影响范围</div>
              <p>将删除当前账号下的历史评估记录与相关结果数据，用于重置个人评估过程。</p>
            </div>
            <div class="danger-block">
              <div class="danger-block-title">不会影响</div>
              <p>不会删除系统中的岗位模板、岗位实例，也不会影响其他用户的数据。</p>
            </div>
          </div>

          <div class="danger-action-row">
            <div class="danger-helper">
              建议仅在确有重置需求时执行，删除前请确认相关评估报告已不再需要保留。
            </div>
            <el-button type="danger" plain @click="deleteAllAssessments">
              删除我的评估记录
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const savingSecurity = ref(false)
const savingPassword = ref(false)
const savingNotifications = ref(false)
const savingPrivacy = ref(false)

const securityForm = reactive({
  username: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const notificationForm = reactive({
  notifyInterviewReminder: true,
  notifyAssessmentCompleted: true,
  notifyReportReady: true,
  notifyJobRecommendation: true,
  notifyCandidateDelivery: true,
  notifyCandidateAssessmentCompleted: true
})

const privacyForm = reactive({
  deliveryPrivacy: 2
})

const privacyOptions = [
  {
    value: 1,
    title: '实名展示',
    description: '适用于需要明确身份信息的正式投递场景。'
  },
  {
    value: 2,
    title: '昵称展示',
    description: '优先展示昵称，兼顾识别性与隐私保护。'
  },
  {
    value: 3,
    title: '匿名编号',
    description: '以匿名编号替代姓名，适合更强调隐私的场景。'
  }
]

const roleLabel = computed(() => (userStore.isHR ? 'HR 招聘方' : '候选人'))

const fillForms = (profile: Record<string, any>) => {
  securityForm.username = profile.username || userStore.username || ''
  securityForm.email = profile.email || ''
  securityForm.phone = profile.phone || ''
  privacyForm.deliveryPrivacy = profile.delivery_privacy || 2
}

const fillNotificationForm = (settings: Record<string, any>) => {
  notificationForm.notifyInterviewReminder = settings.notify_interview_reminder ?? true
  notificationForm.notifyAssessmentCompleted = settings.notify_assessment_completed ?? true
  notificationForm.notifyReportReady = settings.notify_report_ready ?? true
  notificationForm.notifyJobRecommendation = settings.notify_job_recommendation ?? true
  notificationForm.notifyCandidateDelivery = settings.notify_candidate_delivery ?? true
  notificationForm.notifyCandidateAssessmentCompleted =
    settings.notify_candidate_assessment_completed ?? true
}

const fetchSettings = async () => {
  const [profileResponse, notificationResponse] = await Promise.all([
    request.get('/user/profile'),
    request.get('/user/settings/notifications')
  ])

  if (profileResponse.data?.code === 200 && profileResponse.data?.data) {
    fillForms(profileResponse.data.data)
  } else {
    throw new Error(profileResponse.data?.message || '获取账号设置失败')
  }

  if (notificationResponse.data?.code === 200 && notificationResponse.data?.data) {
    fillNotificationForm(notificationResponse.data.data)
  } else {
    throw new Error(notificationResponse.data?.message || '获取提醒设置失败')
  }
}

const saveSecurity = async () => {
  savingSecurity.value = true
  try {
    const response = await request.patch('/user/profile', {
      email: securityForm.email,
      phone: securityForm.phone
    })

    if (response.data?.code !== 200) {
      throw new Error(response.data?.message || '保存失败')
    }

    userStore.updateUserInfo({
      email: securityForm.email,
      phone: securityForm.phone
    })
    ElMessage.success('账号信息已保存')
  } catch (error: any) {
    ElMessage.error(error.message || '账号信息保存失败')
  } finally {
    savingSecurity.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请完整填写密码信息')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于 6 位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  savingPassword.value = true
  try {
    const response = await request.post('/user/change-password', {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })

    if (response.data?.code !== 200) {
      throw new Error(response.data?.message || '密码修改失败')
    }

    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    ElMessage.success('密码修改成功')
  } catch (error: any) {
    ElMessage.error(error.message || '密码修改失败')
  } finally {
    savingPassword.value = false
  }
}

const saveNotifications = async () => {
  savingNotifications.value = true
  try {
    const response = await request.patch('/user/settings/notifications', {
      notify_interview_reminder: notificationForm.notifyInterviewReminder,
      notify_assessment_completed: notificationForm.notifyAssessmentCompleted,
      notify_report_ready: notificationForm.notifyReportReady,
      notify_job_recommendation: notificationForm.notifyJobRecommendation,
      notify_candidate_delivery: notificationForm.notifyCandidateDelivery,
      notify_candidate_assessment_completed: notificationForm.notifyCandidateAssessmentCompleted
    })

    if (response.data?.code !== 200) {
      throw new Error(response.data?.message || '保存失败')
    }

    fillNotificationForm(response.data.data || {})
    ElMessage.success('流程提醒设置已保存')
  } catch (error: any) {
    ElMessage.error(error.message || '流程提醒设置保存失败')
  } finally {
    savingNotifications.value = false
  }
}

const savePrivacy = async () => {
  savingPrivacy.value = true
  try {
    const response = await request.patch('/user/profile', {
      delivery_privacy: privacyForm.deliveryPrivacy
    })

    if (response.data?.code !== 200) {
      throw new Error(response.data?.message || '保存失败')
    }

    userStore.updateUserInfo({
      deliveryPrivacy: privacyForm.deliveryPrivacy
    })
    ElMessage.success('隐私设置已保存')
  } catch (error: any) {
    ElMessage.error(error.message || '隐私设置保存失败')
  } finally {
    savingPrivacy.value = false
  }
}

const deleteAllAssessments = async () => {
  try {
    await ElMessageBox.confirm(
      '确认删除当前账号下的全部评估记录吗？删除后相关评估报告与历史结果将无法恢复。',
      '删除评估记录',
      {
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消'
      }
    )

    const response = await request.delete('/user/assessments')
    if (response.data?.code === 200) {
      ElMessage.success(response.data?.message || '评估记录已删除')
    } else {
      ElMessage.error(response.data?.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('删除操作失败')
    }
  }
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  try {
    await fetchSettings()
  } catch (error: any) {
    ElMessage.error(error.message || '账号设置加载失败')
  }
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  padding: 40px 20px 56px;
  background:
    radial-gradient(circle at top left, rgba(102, 126, 234, 0.14), transparent 28%),
    linear-gradient(180deg, #f4f7fb 0%, #fbfcff 100%);
}

.el-page-header {
  max-width: 1080px;
  margin: 0 auto 20px;
}

.el-page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2a44;
}


.settings-layout {
  max-width: 1080px;
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.settings-card {
  border: 1px solid #e5eaf3;
  border-radius: 18px;
  box-shadow: 0 10px 28px rgba(31, 42, 68, 0.06);
  overflow: hidden;
}

.settings-card :deep(.el-card__header) {
  padding: 20px 24px 14px;
  border-bottom: 1px solid #edf2f8;
}

.settings-card :deep(.el-card__body) {
  padding: 20px 24px 24px;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.card-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #1f2a44;
}

.card-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.7;
}

.settings-form {
  max-width: 680px;
}

.wide-form {
  max-width: 100%;
}

.section-intro {
  margin-bottom: 18px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f7f9fc;
  color: #5f6b85;
  font-size: 13px;
  line-height: 1.7;
  border: 1px solid #e9eef6;
}

.section-intro.blue {
  background: linear-gradient(135deg, #f6f8ff 0%, #f3f7ff 100%);
  border-color: #dfe7ff;
  color: #4b5d8a;
}

.switch-group + .switch-group {
  margin-top: 22px;
}

.group-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.switch-list {
  display: grid;
  gap: 14px;
  margin-bottom: 20px;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 18px;
  border: 1px solid #e7edf7;
  border-radius: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.switch-item:hover {
  border-color: #d2dcf3;
  box-shadow: 0 8px 18px rgba(99, 102, 241, 0.06);
}

.switch-item h4 {
  margin: 0 0 6px;
  font-size: 15px;
  color: #1f2a44;
}

.switch-item p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.7;
}

.privacy-options {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.privacy-option {
  position: relative;
  display: block;
  padding: 16px;
  border: 1px solid #e7edf7;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.privacy-option:hover {
  border-color: #c8d5f2;
  box-shadow: 0 8px 18px rgba(99, 102, 241, 0.06);
}

.privacy-option.active {
  border-color: #667eea;
  background: linear-gradient(180deg, #f8f9ff 0%, #eef3ff 100%);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.1);
}

.privacy-option input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.privacy-option-title {
  margin-bottom: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1f2a44;
}

.privacy-option-desc {
  font-size: 13px;
  line-height: 1.7;
  color: #6b7280;
}

.privacy-tip {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f5f7ff;
  color: #58627a;
  line-height: 1.7;
  font-size: 13px;
  border: 1px solid #e0e7ff;
}

.danger-card {
  border-color: #f2d7da;
  background: linear-gradient(180deg, #fffefe 0%, #fff9f9 100%);
}

.danger-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.danger-badge-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.danger-badge {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: #fee2e2;
  color: #b91c1c;
  font-size: 12px;
  font-weight: 700;
}

.danger-note {
  font-size: 12px;
  color: #b45309;
}

.danger-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.danger-block {
  padding: 16px;
  border-radius: 14px;
  border: 1px solid #f2d7da;
  background: #fff;
}

.danger-block-title {
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #7f1d1d;
}

.danger-block p {
  margin: 0;
  color: #6b7280;
  line-height: 1.7;
  font-size: 13px;
}

.danger-action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 18px;
  border-radius: 14px;
  background: #fff5f5;
  border: 1px dashed #ef9a9a;
}

.danger-helper {
  color: #7c2d12;
  font-size: 13px;
  line-height: 1.7;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  border-radius: 10px;
}

@media (max-width: 900px) {
  .settings-hero {
    flex-direction: column;
  }

  .hero-meta {
    align-items: flex-start;
  }

  .privacy-options,
  .danger-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .settings-page {
    padding: 24px 12px 40px;
  }

  .settings-hero {
    padding: 20px 18px;
    border-radius: 16px;
  }

  .settings-hero h3 {
    font-size: 20px;
  }

  .danger-action-row,
  .card-header,
  .switch-item {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
