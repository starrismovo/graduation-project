<template>
  <div class="profile-page">
    <el-page-header @back="goBack">
      <template #content>
        <h2>个人信息</h2>
      </template>
    </el-page-header>

    <el-card class="profile-card" shadow="never">
      <!-- 头像上传区 -->
      <div class="avatar-section">
  <div class="avatar-left">
    <el-avatar :size="120" :src="userForm.avatar || defaultAvatar" class="user-avatar"/>
  </div>

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

    <p class="avatar-tip">支持 JPG、PNG，建议尺寸 120×120</p>
  </div>
</div>


      <!-- 基本信息表单 -->
      <el-form :model="userForm" label-width="120px" ref="userFormRef" class="form-section">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" disabled />
        </el-form-item>

        <el-form-item label="显示昵称" prop="nickname">
          <el-input v-model="userForm.nickname" placeholder="用于系统内展示" maxlength="20" />
          <template #tip>
            <span class="form-tip">HR在报告中看到的名字，可与真实姓名不同</span>
          </template>
        </el-form-item>

        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="userForm.realName" placeholder="用于正式投递（可选）" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="用于登录和通知" />
        </el-form-item>

        <el-form-item label="电话" prop="phone">
          <el-input v-model="userForm.phone" placeholder="用于HR联系（可选）" />
        </el-form-item>

        <el-form-item label="自我介绍">
          <el-input
            type="textarea"
            v-model="userForm.bio"
            :rows="3"
            placeholder="一句话介绍自己，例如：3年前端开发经验，热爱挑战"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- 投递隐私设置 -->
        <el-form-item label="投递隐私">
          <el-radio-group v-model="userForm.deliveryPrivacy">
            <el-radio :label="1">实名（姓名 + 联系方式）</el-radio>
            <el-radio :label="2">昵称（仅显示 {{ userForm.nickname || '昵称' }}）</el-radio>
            <el-radio :label="3">匿名（显示编号，如 #C12345）</el-radio>
          </el-radio-group>
          <div class="privacy-tip">
            设置后，投递报告时HR将看到对应信息。您随时可修改。
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveProfile">保存修改</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 底部提示 -->
    <div class="footer-tip">
      <p>所有信息仅用于系统内评估与投递，严格保护您的隐私。</p>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// 路由 & Store
const userStore = useUserStore()
const router = useRouter()

// 表单数据
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

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

// 从后端获取用户信息
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

// 头像上传前校验
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

// 处理头像上传（调用后端上传接口）
const handleAvatarUpload = async (param: any) => {
  const file = param.file;
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await request.post('/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    if (response.data?.code === 200 && response.data?.data?.avatar) {
      userForm.value.avatar = response.data.data.avatar;
      // 立即保存到数据库
      await saveProfile();
      ElMessage.success('头像上传成功');
    } else {
      ElMessage.error(response.data?.message || '头像上传失败');
    }
  } catch (error: any) {
    console.error('头像上传错误:', error);
    ElMessage.error('头像上传失败');
  }
};

// 保存个人信息
const saveProfile = async () => {
  console.log('准备保存的数据:', {
    avatar: userForm.value.avatar, // 确保有值且不为空
    nickname: userForm.value.nickname,
    real_name: userForm.value.realName,
    // ... 其他字段
  });
  
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
      // 更新 Pinia store
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

// 返回上一页
const goBack = () => {
  router.back()
}

// 删除所有评估数据
const deleteAllData = () => {
  ElMessageBox.confirm('确定删除所有评估数据吗？此操作不可逆！', '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      const response = await request.delete('/user/assessments')
      
      if (response.data?.code === 200) {
        ElMessage.success(response.data?.message || '数据已删除')
      } else {
        ElMessage.error(response.data?.message || '删除失败')
      }
    } catch (error: any) {
      console.error('删除错误:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserProfile()
})
</script>


<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(180deg, #f5f7fa 0%, #fafbfc 100%);
}

/* 卡片 */
.profile-card {
  max-width: 760px;
  margin: 30px auto;
  padding: 40px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.profile-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

/* 头像区域 */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 30px;
  padding-bottom: 25px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 30px;
}

/* 头像 */
.user-avatar {
  border: 3px solid #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.25);
}

/* 头像操作 */
.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.avatar-left {
  display: flex;
  align-items: center;
}

.avatar-tip {
  color: #909399;
  font-size: 12px;
}

/* 表单 */
.form-section {
  max-width: 620px;
}

/* 每个表单间距 */
.el-form-item {
  margin-bottom: 22px;
}

/* 输入框样式统一 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #bfcfe7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
}

/* 表单提示 */
.form-tip {
  color: #909399;
  font-size: 12px;
  margin-left: 6px;
}

/* 隐私说明 */
.privacy-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
  line-height: 1.6;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

/* 按钮区域 */
.el-form-item:last-child {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 底部提示 */
.footer-tip {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 30px;
}

/* header */
.el-page-header {
  max-width: 760px;
  margin: 0 auto;
}

.el-page-header h2 {
  font-weight: 600;
  font-size: 20px;
  color: #2c3e50;
}

/* 按钮样式统一 */
:deep(.el-button--primary) {
  background-color: #409eff;
  border-color: #409eff;
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  background-color: #66b1ff;
  border-color: #66b1ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
}

:deep(.el-button--primary:active) {
  background-color: #0a7ce4;
  border-color: #0a7ce4;
}

/* 默认按钮 */
:deep(.el-button:not(.is-disabled)) {
  transition: all 0.3s ease;
}

:deep(.el-button:hover:not(.is-disabled)) {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 单选框 */
:deep(.el-radio__label) {
  color: #2c3e50;
}

:deep(.el-radio.is-checked .el-radio__inner) {
  border-color: #409eff;
  background-color: #409eff;
}

/* 标签 */
:deep(.el-tag) {
  border-radius: 4px;
}

</style>