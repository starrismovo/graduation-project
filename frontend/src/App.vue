<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { setCandidateId, clearCandidateId } from '@/utils/interviewHub'

const userStore = useUserStore()

// 应用初始化：从本地存储恢复用户信息
onMounted(() => {
  userStore.restoreFromLocal()
})

watch(
  () => [userStore.userId, userStore.profile?.id, userStore.isHR],
  ([uid, pid, isHR]) => {
    if (isHR) {
      clearCandidateId()
      return
    }

    const idValue = Number(uid || pid || 0)
    if (Number.isFinite(idValue) && idValue > 0) {
      setCandidateId(idValue)
    } else {
      clearCandidateId()
    }
  },
  { immediate: true }
)
</script>

<style>
/* 可选：全局样式 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

html,
body,
#app,
#app :where(:not(input):not(textarea):not([contenteditable="true"]):not([contenteditable=""])) {
  caret-color: transparent;
}

#app input,
#app textarea,
#app [contenteditable="true"],
#app [contenteditable=""],
#app .el-input__inner,
#app .el-textarea__inner {
  caret-color: auto;
}

/* ==== 光标规范：纯展示文字不显示 I 型输入光标 ==== */
/* !important 确保压倒 UA 样式和 Element Plus 的 cursor:auto */
*, *::before, *::after {
  cursor: default !important;
}
/* 可点击 / 交互元素恢复 pointer */
a,
button,
[role="button"],
[role="link"],
[role="tab"],
[role="menuitem"],
label[for],
.el-button,
.el-button *,
.el-menu-item,
.el-menu-item *,
.el-tabs__item,
.el-tabs__item *,
.el-select,
.el-select *,
.el-dropdown,
.el-dropdown *,
.el-pagination button,
.el-checkbox,
.el-checkbox *,
.el-radio,
.el-radio *,
.el-switch,
.el-switch *,
.el-upload,
.el-upload *,
.el-slider__button,
[tabindex]:not([tabindex="-1"]) {
  cursor: pointer !important;
}
/* 表单输入元素保留 text 光标 */
input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="file"]):not([type="submit"]):not([type="button"]):not([type="reset"]),
textarea {
  cursor: text !important;
}
input[type="checkbox"],
input[type="radio"],
input[type="range"],
input[type="file"],
input[type="submit"],
input[type="button"],
input[type="reset"],
select {
  cursor: pointer !important;
}
/* 禁用态（优先级最高，放最后） */
:disabled,
[disabled],
.el-button.is-disabled,
.el-button.is-disabled *,
.el-input.is-disabled input,
.el-select.is-disabled,
.el-select.is-disabled * {
  cursor: not-allowed !important;
}
</style>
