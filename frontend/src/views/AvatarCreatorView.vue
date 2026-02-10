<template>
  <div class="avatar-creator-page">
    <!-- 星空背景 -->
    <div class="stars-background">
      <div class="star" v-for="i in 30" :key="i" 
           :style="{
             left: Math.random() * 100 + '%',
             top: Math.random() * 100 + '%',
             animationDelay: Math.random() * 3 + 's'
           }"></div>
    </div>

    <div class="creator-container">
      <div class="creator-header">
        <h1 class="creator-title">创建你的星际探险家形象</h1>
        <p class="creator-subtitle">选择一个代表你的虚拟形象，它将陪伴你的整个探索旅程</p>
      </div>

      <div class="creator-main">
        <!-- 左侧：预览区 -->
        <div class="preview-section">
          <div class="preview-card">
            <div class="preview-title">形象预览</div>
            <div class="avatar-preview" :class="selectedStyle">
              <div class="avatar-display">
                {{ currentAvatar }}
              </div>
            </div>
            <div class="preview-name">{{ avatarName || '探险家' }}</div>
          </div>
        </div>

        <!-- 右侧：自定义选项 -->
        <div class="options-section">
          <el-card class="options-card">
            <!-- 步骤1：选择风格 -->
            <div class="option-group">
              <h3 class="option-title">1. 选择风格</h3>
              <div class="style-grid">
                <div 
                  v-for="style in styles" 
                  :key="style.id"
                  class="style-option"
                  :class="{ active: selectedStyle === style.id }"
                  @click="selectStyle(style.id)"
                >
                  <div class="style-icon">{{ style.icon }}</div>
                  <div class="style-name">{{ style.name }}</div>
                </div>
              </div>
            </div>

            <el-divider />

            <!-- 步骤2：选择形象 -->
            <div class="option-group">
              <h3 class="option-title">2. 选择形象</h3>
              <div class="avatar-grid">
                <div 
                  v-for="avatar in avatars" 
                  :key="avatar.id"
                  class="avatar-option"
                  :class="{ active: selectedAvatar === avatar.id }"
                  @click="selectAvatar(avatar.id, avatar.emoji)"
                >
                  <div class="avatar-emoji">{{ avatar.emoji }}</div>
                </div>
              </div>
            </div>

            <el-divider />

            <!-- 步骤3：自定义名称 -->
            <div class="option-group">
              <h3 class="option-title">3. 自定义名称（可选）</h3>
              <el-input 
                v-model="avatarName" 
                placeholder="给你的探险家起个名字..."
                maxlength="20"
                show-word-limit
              />
            </div>

            <el-divider />

            <!-- 快速操作 -->
            <div class="quick-actions">
              <el-button @click="randomGenerate" icon="Refresh">
                随机生成
              </el-button>
              <el-button type="primary" @click="saveAvatar" :loading="isSaving">
                完成创建
              </el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="creator-footer">
        <p>💡 提示：你可以随时在设置中修改你的虚拟形象</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 风格选项
const styles = ref([
  { id: 'simple', name: '简约', icon: '⚪' },
  { id: 'sci-fi', name: '科幻', icon: '🚀' },
  { id: 'retro', name: '复古', icon: '🎮' },
  { id: 'cute', name: '萌系', icon: '🌸' }
])

// 形象选项
const avatars = ref([
  { id: 1, emoji: '👨‍💼' },
  { id: 2, emoji: '👩‍💼' },
  { id: 3, emoji: '👨‍🚀' },
  { id: 4, emoji: '👩‍🚀' },
  { id: 5, emoji: '🧑‍💻' },
  { id: 6, emoji: '👨‍🔬' },
  { id: 7, emoji: '👩‍🔬' },
  { id: 8, emoji: '🧙‍♂️' },
  { id: 9, emoji: '🧙‍♀️' },
  { id: 10, emoji: '🦸‍♂️' },
  { id: 11, emoji: '🦸‍♀️' },
  { id: 12, emoji: '🧑‍🎨' }
])

// 选中状态
const selectedStyle = ref('simple')
const selectedAvatar = ref(1)
const currentAvatar = ref('👨‍💼')
const avatarName = ref('')
const isSaving = ref(false)

// 选择风格
const selectStyle = (styleId: string) => {
  selectedStyle.value = styleId
}

// 选择形象
const selectAvatar = (avatarId: number, emoji: string) => {
  selectedAvatar.value = avatarId
  currentAvatar.value = emoji
}

// 随机生成
const randomGenerate = () => {
  const randomStyle = styles.value[Math.floor(Math.random() * styles.value.length)]
  const randomAvatar = avatars.value[Math.floor(Math.random() * avatars.value.length)]
  
  selectStyle(randomStyle.id)
  selectAvatar(randomAvatar.id, randomAvatar.emoji)
  
  ElMessage.success('已随机生成形象')
}

// 保存形象
const saveAvatar = async () => {
  isSaving.value = true
  
  const avatarData = {
    style: selectedStyle.value,
    avatar: currentAvatar.value,
    name: avatarName.value || '探险家'
  }
  
  // 保存到本地存储
  localStorage.setItem('userAvatar', JSON.stringify(avatarData))
  
  // 模拟保存延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  ElMessage.success('形象创建成功！')
  isSaving.value = false
  
  // 返回上一页或首页
  router.back()
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Space+Mono:wght@400;700&display=swap');

* {
  box-sizing: border-box;
}

.avatar-creator-page {
  min-height: 100vh;
  background: #0a0e27;
  color: #e0e6ed;
  position: relative;
  overflow-x: hidden;
  font-family: 'Space Mono', monospace;
}

/* 星空背景 */
.stars-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* 容器 */
.creator-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

/* 头部 */
.creator-header {
  text-align: center;
  margin-bottom: 48px;
}

.creator-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.creator-subtitle {
  font-size: 16px;
  color: #94a3b8;
}

/* 主区域 */
.creator-main {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 32px;
  margin-bottom: 40px;
}

/* 预览区 */
.preview-card {
  background: rgba(30, 41, 59, 0.6);
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-radius: 24px;
  padding: 32px;
  backdrop-filter: blur(20px);
  text-align: center;
  position: sticky;
  top: 100px;
}

.preview-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  color: #a78bfa;
  margin-bottom: 24px;
}

.avatar-preview {
  width: 280px;
  height: 280px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(236, 72, 153, 0.1));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid rgba(167, 139, 250, 0.3);
  transition: all 0.5s ease;
}

.avatar-preview.sci-fi {
  border-color: rgba(59, 130, 246, 0.5);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
  box-shadow: 0 0 40px rgba(59, 130, 246, 0.3);
}

.avatar-preview.retro {
  border-color: rgba(251, 146, 60, 0.5);
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.1), rgba(239, 68, 68, 0.1));
}

.avatar-preview.cute {
  border-color: rgba(236, 72, 153, 0.5);
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(249, 115, 22, 0.1));
}

.avatar-display {
  font-size: 120px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.preview-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  color: #e0e6ed;
}

/* 选项区 */
.options-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  backdrop-filter: blur(20px);
}

.options-card :deep(.el-card__body) {
  padding: 32px;
}

.option-group {
  margin-bottom: 24px;
}

.option-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  margin: 0 0 16px 0;
  color: #a78bfa;
}

/* 风格网格 */
.style-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.style-option {
  padding: 20px;
  background: rgba(15, 23, 42, 0.4);
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.style-option:hover {
  background: rgba(167, 139, 250, 0.1);
  border-color: rgba(167, 139, 250, 0.4);
}

.style-option.active {
  background: rgba(167, 139, 250, 0.2);
  border-color: #a78bfa;
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3);
}

.style-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.style-name {
  font-size: 14px;
  font-weight: 600;
}

/* 形象网格 */
.avatar-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.avatar-option {
  aspect-ratio: 1;
  background: rgba(15, 23, 42, 0.4);
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-option:hover {
  background: rgba(167, 139, 250, 0.1);
  border-color: rgba(167, 139, 250, 0.4);
  transform: scale(1.1);
}

.avatar-option.active {
  background: rgba(167, 139, 250, 0.2);
  border-color: #a78bfa;
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3);
}

.avatar-emoji {
  font-size: 36px;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 底部 */
.creator-footer {
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .creator-main {
    grid-template-columns: 1fr;
  }
  
  .preview-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .style-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .avatar-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
