<template>
  <div class="empty-state">
    <div class="empty-icon">
      <!-- 默认插画 SVG -->
      <svg v-if="!image" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" class="empty-svg">
        <defs>
          <linearGradient id="emptyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#e3f2fd"/>
            <stop offset="100%" style="stop-color:#bbdefb"/>
          </linearGradient>
        </defs>
        <circle cx="60" cy="60" r="55" fill="url(#emptyGrad)" opacity="0.5"/>
        <circle cx="45" cy="50" r="6" fill="#909399"/>
        <circle cx="75" cy="50" r="6" fill="#909399"/>
        <path d="M 50 70 Q 60 78 70 70" stroke="#909399" stroke-width="2" fill="none" stroke-linecap="round"/>
        <circle cx="60" cy="90" r="3" fill="#c0c4cc"/>
        <circle cx="46" cy="92" r="3" fill="#c0c4cc"/>
        <circle cx="74" cy="92" r="3" fill="#c0c4cc"/>
      </svg>

      <!-- 自定义插画 -->
      <img v-else :src="image" :alt="title" class="empty-img" />
    </div>

    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-text">{{ text }}</p>

    <el-button v-if="buttonText" type="primary" size="large" @click="$emit('action')">
      {{ buttonText }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  image?: string | null
  title?: string
  text?: string
  buttonText?: string
}>()

defineEmits<{
  (e: 'action'): void
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  min-height: 300px;
  background: linear-gradient(135deg, #f9fafc 0%, #f0f5fb 100%);
  border-radius: 8px;
}

.empty-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-svg {
  width: 100%;
  height: 100%;
  opacity: 0.8;
}

.empty-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.empty-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.empty-text {
  margin: 0 0 24px 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
  max-width: 400px;
}
</style>
