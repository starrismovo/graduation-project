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
    <div class="video-shell">
      <div class="video-header">
        <span class="video-badge">智能解读</span>
        <h4>{{ title }}</h4>
        <p>通过短视频快速理解当前 TraitScores 的结构特征与岗位适配含义。</p>
      </div>

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

        <div v-if="isHovered" class="hover-overlay">
          <div class="hover-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>查看详情</span>
          </div>
        </div>
      </div>

      <div class="video-footer">
        <span>进入心理解读中心</span>
        <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mini-video-player {
  cursor: pointer;
}

.video-shell {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  border: 1px solid rgba(226, 232, 255, 0.95);
  background:
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.12), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 247, 255, 0.98));
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
  padding: 24px;
  transition: transform 0.24s ease, box-shadow 0.24s ease;
}

.mini-video-player:hover .video-shell {
  transform: translateY(-2px);
  box-shadow: 0 24px 50px rgba(99, 102, 241, 0.12);
}

.video-header {
  margin-bottom: 18px;
}

.video-badge {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(91, 103, 255, 0.1);
  color: #5b67ff;
  font-size: 11px;
  font-weight: 700;
}

.video-header h4 {
  margin: 14px 0 8px;
  font-size: 24px;
  color: #182234;
  letter-spacing: -0.04em;
}

.video-header p {
  margin: 0;
  color: #6f7c93;
  font-size: 13px;
  line-height: 1.8;
}

.video-container {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  border-radius: 22px;
  overflow: hidden;
  background: #0f172a;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.18);
}

.video-element {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: #000;
}

.hover-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
}

.hover-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #fff;
}

.hover-icon svg {
  width: 42px;
  height: 42px;
}

.hover-icon span {
  font-size: 14px;
  font-weight: 700;
}

.video-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  color: #5b67ff;
  font-size: 13px;
  font-weight: 700;
}

.icon-arrow {
  width: 18px;
  height: 18px;
}
</style>
