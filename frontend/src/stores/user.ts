import { defineStore } from 'pinia'
import { ref, computed, onMounted } from 'vue'
import type { UserProfile } from '@/types/assessment'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const isHR = ref<boolean>(false)
  const username = ref<string>('')
  const userId = ref<string>('')
  const profile = ref<UserProfile | null>(null)

  // 计算属性：候选人ID（从 userId 获取）
  const candidateId = computed(() => userId.value || username.value)

  // 保存到本地存储
  const saveToLocal = () => {
    localStorage.setItem('user_token', token.value)
    localStorage.setItem('user_isHR', JSON.stringify(isHR.value))
    localStorage.setItem('user_username', username.value)
    localStorage.setItem('user_id', userId.value)
    localStorage.setItem('user_profile', JSON.stringify(profile.value))

  }

  // 从本地存储恢复
  const restoreFromLocal = () => {
    const savedToken = localStorage.getItem('user_token')
    const savedIsHR = localStorage.getItem('user_isHR')
    const savedUsername = localStorage.getItem('user_username')
    const savedUserId = localStorage.getItem('user_id')
    const savedProfile = localStorage.getItem('user_profile')

    if (savedToken) {
      token.value = savedToken
      isHR.value = savedIsHR ? JSON.parse(savedIsHR) : false
      username.value = savedUsername || ''
      userId.value = savedUserId || ''
      profile.value = savedProfile ? JSON.parse(savedProfile) : null
    }
  }

  const login = (data: {
    access_token: string
    is_hr: boolean
    username?: string
    user_id?: string
    name?: string
    email?: string
  }) => {
    token.value = data.access_token
    isHR.value = data.is_hr
    username.value = data.username || ''
    userId.value = data.user_id || data.username || ''
    profile.value = {
      id: data.user_id,
      name: data.name || data.username,
      username: data.username,
      is_hr: data.is_hr,
      email: data.email
    }
    saveToLocal() // 登录成功后保存到本地
  }

  const logout = () => {
    token.value = ''
    isHR.value = false
    username.value = ''
    userId.value = ''
    profile.value = null
    localStorage.removeItem('user_token')
    localStorage.removeItem('user_isHR')
    localStorage.removeItem('user_username')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_profile')
  }
  const updateUserInfo = (newInfo: Partial<UserProfile>) => {
    if (profile.value) {
      profile.value = { ...profile.value, ...newInfo }
    } else {
      profile.value = newInfo as UserProfile
    }
    saveToLocal() // 更新后同步保存到本地
  }

  return {
    // state
    token,
    isHR,
    username,
    userId,
    profile,
    // computed
    candidateId,
    // methods
    login,
    logout,
    saveToLocal,
    restoreFromLocal,
    updateUserInfo
  }
})