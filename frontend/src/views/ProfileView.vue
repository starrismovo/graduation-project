<template>
  <div class="profile-page">
    <div class="page-shell">
      <el-page-header @back="goBack">
        <template #content>
          <h2>个人信息</h2>
        </template>
      </el-page-header>

      <section class="profile-hero">
        <div class="avatar-wrap">
          <el-avatar :size="104" :src="userForm.avatar || defaultAvatar" class="user-avatar" />
        </div>

        <div class="hero-content">
          <div class="hero-title-row">
            <div>
              <p class="eyebrow">{{ isHR ? '招聘方资料' : '候选人档案' }}</p>
              <h3>{{ userForm.nickname || userForm.username || '未设置昵称' }}</h3>
            </div>
            <el-tag v-if="isHR" type="warning" effect="light" class="role-tag">
              <el-icon><UserFilled /></el-icon>
              HR 招聘方
            </el-tag>
          </div>
          <p class="hero-desc">
            {{ isHR ? '完善工作联系方式，便于进行岗位管理与候选人沟通。' : '完善基础资料后，可在投递和评估报告展示中保持一致、清晰的身份信息。' }}
          </p>
          <div class="avatar-actions">
            <el-upload
              action="#"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
              accept="image/*"
            >
              <el-button type="primary" size="small">更换头像</el-button>
            </el-upload>
            <span class="avatar-tip">支持 JPG、PNG，大小不超过 2MB</span>
          </div>
        </div>
      </section>

      <el-card class="profile-card" shadow="never">
        <div class="card-heading">
          <h3>基础资料</h3>
          <p>{{ isHR ? '用于招聘管理端展示和工作联系。' : '用于系统内展示、投递联系与评估报告身份展示。' }}</p>
        </div>

        <el-form :model="userForm" label-position="top" ref="userFormRef" class="form-section">
          <div class="form-grid">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>

            <el-form-item label="显示昵称" prop="nickname">
              <el-input v-model="userForm.nickname" placeholder="用于系统内展示" maxlength="20" />
            </el-form-item>

            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="userForm.realName" :placeholder="isHR ? '请输入真实姓名' : '用于正式投递（可选）'" />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="userForm.email" :placeholder="isHR ? '工作邮箱' : '用于登录和通知'" />
            </el-form-item>

            <el-form-item label="电话" prop="phone">
              <el-input v-model="userForm.phone" :placeholder="isHR ? '工作联系电话' : '用于 HR 联系（可选）'" />
            </el-form-item>
          </div>

          <el-form-item :label="isHR ? '个人简介' : '自我介绍'">
            <el-input
              type="textarea"
              v-model="userForm.bio"
              :rows="4"
              :placeholder="isHR ? '介绍您的招聘方向或公司背景' : '简要说明教育经历、求职方向或主要技能'"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>

          <el-form-item v-if="!isHR" label="投递隐私">
            <el-radio-group v-model="userForm.deliveryPrivacy" class="privacy-radio-group">
              <el-radio :label="1">实名展示</el-radio>
              <el-radio :label="2">昵称展示</el-radio>
              <el-radio :label="3">匿名编号</el-radio>
            </el-radio-group>
            <div class="privacy-tip">
              该设置仅影响投递与报告查看时的身份展示，不改变账号保存的真实资料。
            </div>
          </el-form-item>

          <el-form-item v-if="isHR">
            <div class="hr-role-info">
              <el-icon color="#e6a23c" :size="16"><Warning /></el-icon>
              <span>当前账号可进行岗位管理、候选人邀请和评估报告查看。</span>
            </div>
          </el-form-item>

          <el-form-item class="action-row">
            <el-button type="primary" @click="saveProfile" :loading="loading">保存修改</el-button>
            <el-button @click="goBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <div class="footer-tip">
        所有信息仅用于系统内评估、投递与联系展示。
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled, Warning } from '@element-plus/icons-vue'
import request from '@/utils/request'

const userStore = useUserStore()
const router = useRouter()
const isHR = computed(() => userStore.isHR)

const userFormRef = ref(null)
const loading = ref(false)
const userForm = ref({
  username: userStore.username || '',
  nickname: userStore.profile?.nickname || userStore.username || '',
  realName: userStore.profile?.realName || '',
  email: userStore.profile?.email || '',
  phone: userStore.profile?.phone || '',
  bio: userStore.profile?.bio || '',
  avatar: userStore.profile?.avatar || '',
  deliveryPrivacy: userStore.profile?.deliveryPrivacy || 2
})

const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

const fetchUserProfile = async () => {
  try {
    if (!userStore.token) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    const response = await request.get('/user/profile')

    if (response.data?.code === 200 && response.data?.data) {
      const profile = response.data.data
      userForm.value = {
        username: profile.username || '',
        nickname: profile.nickname || profile.username || '',
        realName: profile.real_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
        bio: profile.bio || '',
        avatar: profile.avatar || '',
        deliveryPrivacy: profile.delivery_privacy || 2
      }
    }
  } catch (error: any) {
    console.error('获取用户信息失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      userStore.logout()
      router.push('/login')
    }
  }
}

const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB！')
  }
  return isImage && isLt2M
}

const handleAvatarUpload = async (param: any) => {
  const file = param.file
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await request.post('/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data?.code === 200 && response.data?.data?.avatar) {
      userForm.value.avatar = response.data.data.avatar
      await saveProfile()
      ElMessage.success('头像上传成功')
    } else {
      ElMessage.error(response.data?.message || '头像上传失败')
    }
  } catch (error: any) {
    console.error('头像上传错误:', error)
    ElMessage.error('头像上传失败')
  }
}

const saveProfile = async () => {
  if (!userStore.token) {
    ElMessage.error('登录已过期，请重新登录')
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const response = await request.patch('/user/profile', {
      nickname: userForm.value.nickname,
      real_name: userForm.value.realName,
      email: userForm.value.email,
      phone: userForm.value.phone,
      bio: userForm.value.bio,
      avatar: userForm.value.avatar,
      delivery_privacy: userForm.value.deliveryPrivacy
    })

    if (response.data?.code === 200) {
      userStore.updateUserInfo({
        nickname: userForm.value.nickname,
        realName: userForm.value.realName,
        email: userForm.value.email,
        phone: userForm.value.phone,
        bio: userForm.value.bio,
        avatar: userForm.value.avatar,
        deliveryPrivacy: userForm.value.deliveryPrivacy
      })
      ElMessage.success('个人信息已保存')
    } else {
      ElMessage.error(response.data?.message || '保存失败')
    }
  } catch (error: any) {
    console.error('保存错误:', error)
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      userStore.logout()
      router.push('/login')
    } else {
      ElMessage.error('保存失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchUserProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100%;
  width: 100%;
  background: transparent;
}

.page-shell {
  max-width: 1000px;
  margin: 0 auto;
}

.el-page-header {
  margin-bottom: 20px;
}

.el-page-header h2 {
  margin: 0;
  font-weight: 700;
  font-size: 24px;
  color: #1f2a44;
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px;
  margin-bottom: 20px;
  border: 1px solid #e5eaf3;
  border-radius: 18px;
  background: linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
  box-shadow: 0 12px 30px rgba(31, 42, 68, 0.07);
}

.avatar-wrap {
  flex: 0 0 auto;
  padding: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5b8cff, #8b5cf6);
}

.user-avatar {
  display: block;
  border: 4px solid #fff;
  box-shadow: 0 10px 20px rgba(64, 101, 255, 0.16);
}

.hero-content {
  flex: 1;
  min-width: 0;
}

.hero-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.hero-content h3 {
  margin: 0;
  color: #1f2a44;
  font-size: 24px;
  font-weight: 700;
}

.hero-desc {
  max-width: 620px;
  margin: 10px 0 18px;
  color: #5f6b85;
  line-height: 1.7;
  font-size: 14px;
}

.avatar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.role-tag {
  gap: 4px;
  align-items: center;
}

.avatar-tip {
  color: #64748b;
  font-size: 13px;
}

.profile-card {
  border: 1px solid #e5eaf3;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 10px 28px rgba(31, 42, 68, 0.06);
  overflow: hidden;
}

.profile-card :deep(.el-card__body) {
  padding: 26px 28px 8px;
}

.card-heading {
  margin-bottom: 22px;
}

.card-heading h3 {
  margin: 0 0 6px;
  color: #1f2a44;
  font-size: 18px;
  font-weight: 700;
}

.card-heading p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.7;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2px 18px;
}

.privacy-tip {
  width: 100%;
  color: #58627a;
  font-size: 13px;
  margin-top: 8px;
  line-height: 1.7;
  padding: 10px 12px;
  background: #f5f7ff;
  border: 1px solid #e0e7ff;
  border-radius: 10px;
}

.privacy-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 14px;
}

.action-row {
  margin-top: 22px;
  padding-top: 20px;
  border-top: 1px solid #edf2f8;
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

:deep(.el-radio__label) {
  color: #334155;
}

.hr-role-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  padding: 12px 14px;
  background: #fdf6ec;
  border: 1px solid #f5dab1;
  border-radius: 10px;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.footer-tip {
  text-align: center;
  color: #64748b;
  font-size: 13px;
  margin-top: 22px;
}

:deep(.el-tag) {
  border-radius: 999px;
}

@media (max-width: 768px) {
  .profile-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 22px 18px;
  }

  .hero-title-row {
    width: 100%;
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .profile-card :deep(.el-card__body) {
    padding: 22px 18px 6px;
  }
}
</style>
