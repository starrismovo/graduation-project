/**
 * 评估系统相关的 TypeScript 类型定义
 */

/**
 * 心理特质评分
 */
export interface TraitScore {
  name: string          // 特质名称
  score: number         // 评分（0-10）
  description?: string  // 特质描述
}

/**
 * 评估历史记录项
 */
export interface AssessmentHistoryItem {
  id: number
  job_id: number
  job_title: string
  match_score: number | null
  created_at: string
  assessment_status: string
  assessment_mode: string
}

/**
 * 岗位推荐卡片
 */
export interface JobRecommendation {
  id: number
  title: string
  description: string
  department: string
  level: string
  match_score: number
  match_reason?: string
}

/**
 * 匹配分析
 */
export interface MatchAnalysis {
  strengths: string[]
  gaps: string[]
}

/**
 * 评估详情统计
 */
export interface AssessmentDetails {
  total_rounds?: number
  duration_minutes?: number
  conversation_depth?: number
  roles_participated?: string[]
  overall_impression?: string
}

/**
 * 完整评估报告
 */
export interface AssessmentReport {
  id: number
  candidate_id: string
  job_id: number
  job_title: string
  match_score: number | null
  created_at: string
  updated_at: string
  assessment_mode: string
  personality_trait: TraitScore[]
  conversation_summary?: string
  match_analysis?: MatchAnalysis
  recommendations?: string[]
  assessement_details?: AssessmentDetails
}

/**
 * API 响应格式
 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/**
 * 用户个人资料
 */
export interface UserProfile {
  id?: string;
  name?: string;
  username?: string;
  email?: string;
  is_hr?: boolean;
  created_at?: string;
  // 添加以下字段（注意字段名与后端返回的键名一致）
  nickname?: string;
  realName?: string;
  phone?: string;
  bio?: string;
  avatar?: string;
  deliveryPrivacy?: number;  // 注意是下划线风格
}
