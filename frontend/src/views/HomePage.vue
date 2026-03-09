<script setup lang="ts">
import { useUserStore } from '../stores/user'
import HomeView from './HomeView.vue'
import HRHomeView from './HRHomeView.vue'

const userStore = useUserStore()
</script>

<template>
  <!-- 候选人主页 -->
  <HomeView v-if="!userStore.isHR" />
  
  <!-- HR主页 -->
  <HRHomeView v-else />
</template>

<style scoped></style>
