<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 应用初始化：从本地存储恢复用户信息
onMounted(() => {
  userStore.restoreFromLocal()
})
</script>

<style>
/* 可选：全局样式 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
