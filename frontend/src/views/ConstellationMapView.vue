<template>
  <div class="placeholder-page">
    <h1>我的星图</h1>
    <p>功能开发中...</p>
    <el-button @click="$router.push('/home')">返回首页</el-button>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.placeholder-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0a0e27;
  color: white;
}
</style>