import { defineStore } from 'pinia'
import { ref, onMounted } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const isHR = ref<boolean>(false)
  const username = ref<string>('')

  // 保存到本地存储
  const saveToLocal = () => {
    localStorage.setItem('user_token', token.value)
    localStorage.setItem('user_isHR', JSON.stringify(isHR.value))
    localStorage.setItem('user_username', username.value)
  }

  // 从本地存储恢复
  const restoreFromLocal = () => {
    const savedToken = localStorage.getItem('user_token')
    const savedIsHR = localStorage.getItem('user_isHR')
    const savedUsername = localStorage.getItem('user_username')

    if (savedToken) {
      token.value = savedToken
      isHR.value = savedIsHR ? JSON.parse(savedIsHR) : false
      username.value = savedUsername || ''
    }
  }

  const login = (data: { access_token: string; is_hr: boolean; username?: string }) => {
    token.value = data.access_token
    isHR.value = data.is_hr
    username.value = data.username || ''
    saveToLocal() // 登录成功后保存到本地
  }

  const logout = () => {
    token.value = ''
    isHR.value = false
    username.value = ''
    localStorage.removeItem('user_token')
    localStorage.removeItem('user_isHR')
    localStorage.removeItem('user_username')
  }

  return { token, isHR, username, login, logout, restoreFromLocal }
})