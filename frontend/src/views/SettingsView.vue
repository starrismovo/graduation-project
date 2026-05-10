<template>
  <div class="settings-page">
    <div class="page-shell">
      <el-page-header @back="goBack">
        <template #content>
          <h2>账号设置</h2>
        </template>
      </el-page-header>

      <section class="settings-hero">
        <div>
          <p class="eyebrow">安全与偏好</p>
          <h3>{{ userStore.isHR ? '招聘方账号管理' : '候选人账号管理' }}</h3>
          <p>
            {{ userStore.isHR ? '维护登录安全、联系方式和招聘流程提醒。' : '维护登录安全、联系方式、评估提醒和投递隐私。' }}
          </p>
        </div>
      </section>

      <div class="settings-layout">
        <el-card class="settings-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <h3>账号安全</h3>
                <p>维护登录身份与联系方式，确保通知和账号找回路径可用。</p>
              </div>
            </div>
          </template>

          <el-form :model="securityForm" label-position="top" class="settings-form">
            <div class="form-grid">
              <el-form-item label="用户名">
                <el-input v-model="securityForm.username" disabled />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="securityForm.email" placeholder="用于登录提醒、报告通知与账号找回" />
              </el-form-item>
              <el-form-item label="手机号">
                <el-input v-model="securityForm.phone" placeholder="用于联系确认与安全校验" />
              </el-form-item>
            </div>
            <el-form-item class="action-row compact">
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

          <el-form :model="passwordForm" label-position="top" class="settings-form">
            <div class="form-grid three">
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
                  placeholder="不少于 6 位"
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
            </div>
            <el-form-item class="action-row compact">
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
                <p>围绕面试流程、评估报告和推荐更新提供提醒开关。</p>
              </div>
            </div>
          </template>

          <el-form :model="notificationForm" label-width="0" class="settings-form wide-form">
            <div class="switch-list">
              <div class="switch-item">
                <div>
                  <h4>面试提醒</h4>
                  <p>在面试开始前或有新的面试邀请时提醒查看。</p>
                </div>
                <el-switch v-model="notificationForm.notifyInterviewReminder" />
              </div>

              <div class="switch-item">
                <div>
                  <h4>评估完成提醒</h4>
                  <p>当一次完整评估流程结束后，提醒进入结果查看环节。</p>
                </div>
                <el-switch v-model="notificationForm.notifyAssessmentCompleted" />
              </div>

              <div class="switch-item">
                <div>
                  <h4>评估报告提醒</h4>
                  <p>当系统生成评估报告后，及时提醒进入报告页面。</p>
                </div>
                <el-switch v-model="notificationForm.notifyReportReady" />
              </div>

              <div class="switch-item" v-if="!userStore.isHR">
                <div>
                  <h4>岗位推荐提醒</h4>
                  <p>当系统基于最新评估结果更新推荐岗位时提醒查看。</p>
                </div>
                <el-switch v-model="notificationForm.notifyJobRecommendation" />
              </div>

              <template v-if="userStore.isHR">
                <div class="switch-item">
                  <div>
                    <h4>候选人投递提醒</h4>
                    <p>有新的候选人投递岗位时提醒查看，便于及时筛选与跟进。</p>
                  </div>
                  <el-switch v-model="notificationForm.notifyCandidateDelivery" />
                </div>

                <div class="switch-item">
                  <div>
                    <h4>候选人评估完成提醒</h4>
                    <p>候选人完成评估后提醒查看其评估报告。</p>
                  </div>
                  <el-switch v-model="notificationForm.notifyCandidateAssessmentCompleted" />
                </div>
              </template>
            </div>

            <el-form-item class="action-row">
              <el-button type="primary" :loading="savingNotifications" @click="saveNotifications">
                保存提醒设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-if="!userStore.isHR" class="settings-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <h3>隐私控制</h3>
                <p>控制投递与报告展示时的身份暴露程度。</p>
              </div>
            </div>
          </template>

          <el-form :model="privacyForm" label-width="0" class="settings-form wide-form">
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

            <div class="privacy-tip">
              当前设置仅影响投递和报告查看场景下的展示方式，不改变账号保存的真实资料。
            </div>

            <el-form-item class="action-row">
              <el-button type="primary" :loading="savingPrivacy" @click="savePrivacy">
                保存隐私设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
  const [profileResult, notificationResult] = await Promise.allSettled([
    request.get('/user/profile'),
    request.get('/user/settings/notifications')
  ])

  if (profileResult.status !== 'fulfilled') {
    throw new Error('获取账号设置失败')
  }

  const profileResponse = profileResult.value
  if (profileResponse.data?.code === 200 && profileResponse.data?.data) {
    fillForms(profileResponse.data.data)
  } else {
    throw new Error(profileResponse.data?.message || '获取账号设置失败')
  }

  if (notificationResult.status !== 'fulfilled') {
    ElMessage.warning('流程提醒设置暂时无法加载')
    return
  }

  const notificationResponse = notificationResult.value
  if (notificationResponse.data?.code === 200 && notificationResponse.data?.data) {
    fillNotificationForm(notificationResponse.data.data)
  } else {
    ElMessage.warning(notificationResponse.data?.message || '流程提醒设置暂时无法加载')
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
  min-height: 100%;
  width: 100%;
  background: transparent;
}

.page-shell {
  max-width: 1080px;
  margin: 0 auto;
}

.el-page-header {
  margin-bottom: 20px;
}

.el-page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2a44;
}

.settings-hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 26px 28px;
  border: 1px solid #e1e8f5;
  border-radius: 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f6f8ff 100%);
  box-shadow: 0 12px 30px rgba(31, 42, 68, 0.07);
}

.eyebrow {
  margin: 0 0 6px;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.settings-hero h3 {
  margin: 0 0 8px;
  color: #1f2a44;
  font-size: 24px;
  font-weight: 700;
}

.settings-hero p {
  margin: 0;
  color: #5f6b85;
  font-size: 14px;
  line-height: 1.7;
}

.settings-layout {
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
  padding: 20px 24px 8px;
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
  max-width: 100%;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2px 18px;
}

.form-grid.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.wide-form {
  max-width: 100%;
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
  margin-bottom: 16px;
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
  margin-bottom: 20px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f5f7ff;
  color: #58627a;
  line-height: 1.7;
  font-size: 13px;
  border: 1px solid #e0e7ff;
}

.action-row {
  margin-top: 4px;
  padding-top: 18px;
  border-top: 1px solid #edf2f8;
}

.action-row.compact {
  margin-top: 2px;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  border-radius: 10px;
}

:deep(.el-form-item__label) {
  color: #334155;
  font-weight: 600;
}

:deep(.el-button--primary) {
  background-color: #4f7cff;
  border-color: #4f7cff;
}

:deep(.el-button--primary:hover) {
  background-color: #3f6df0;
  border-color: #3f6df0;
}

@media (max-width: 900px) {
  .form-grid,
  .form-grid.three,
  .privacy-options {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .settings-hero {
    flex-direction: column;
    padding: 22px 18px;
  }

  .settings-card :deep(.el-card__body) {
    padding: 20px 18px 6px;
  }

  .switch-item {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
