<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  videoUrl: string
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '心理特质解读'
})

const emit = defineEmits<{
  click: []
}>()

const isHovered = ref(false)
</script>

<template>
  <div 
    class="mini-video-player"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="emit('click')"
  >
    <!-- 视频容器 -->
    <div class="video-container">
      <video
        :src="props.videoUrl"
        class="video-element"
        controls
        controlsList="nodownload"
        preload="metadata"
        autoplay
        muted
        loop
      ></video>
      
      <!-- 悬停效果覆盖层 -->
      <div v-if="isHovered" class="hover-overlay">
        <div class="hover-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <span>查看详情</span>
        </div>
      </div>
    </div>
    
    <!-- 标题 -->
    <div class="player-title">
      <h4>{{ title }}</h4>
      <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.mini-video-player {
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mini-video-player:hover {
  transform: translateY(-4px);
}

/* 视频容器 */
.video-container {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  border-radius: 12px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.3s ease;
}

.mini-video-player:hover .video-container {
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
}

.video-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
  background: #000;
}

/* 悬停效果层 */
.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  animation: fadeIn 0.2s ease;
  z-index: 10;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.hover-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.hover-icon svg {
  width: 48px;
  height: 48px;
  animation: pulse 0.6s ease infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.hover-icon span {
  font-size: 14px;
  font-weight: 600;
}

/* 标题区 */
.player-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px;
  gap: 8px;
}

.player-title h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: -0.3px;
  flex: 1;
  text-align: center;
}

.icon-arrow {
  width: 20px;
  height: 20px;
  color: #6366f1;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.mini-video-player:hover .icon-arrow {
  transform: translateX(4px);
}
</style>
