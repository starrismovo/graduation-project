import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface EvaluationResult {
  jobId?: number
  assessmentId?: string
  sessionId?: string
  timestamp?: number
  candidateId?: string
}

export const useAssessmentStore = defineStore('assessment', () => {
  // 最新完成的评估
  const latestEvaluation = ref<EvaluationResult | null>(null)

  // 评估完成时的时间戳（用于检测变化）
  const completionTimestamp = ref<number>(0)

  // 计算属性：是否刚完成评估
  const hasNewEvaluation = computed(() => {
    return completionTimestamp.value > 0
  })

  // 标记评估完成
  const markEvaluationComplete = (result: EvaluationResult) => {
    latestEvaluation.value = {
      ...result,
      timestamp: Date.now()
    }
    completionTimestamp.value = Date.now()
    console.log('✅ 评估完成标记已设置:', latestEvaluation.value)
  }

  // 清除评估完成标记（HomeView 刷新后调用）
  const clearCompletionMark = () => {
    completionTimestamp.value = 0
  }

  // 重置状态
  const reset = () => {
    latestEvaluation.value = null
    completionTimestamp.value = 0
  }

  return {
    latestEvaluation,
    completionTimestamp,
    hasNewEvaluation,
    markEvaluationComplete,
    clearCompletionMark,
    reset
  }
})
