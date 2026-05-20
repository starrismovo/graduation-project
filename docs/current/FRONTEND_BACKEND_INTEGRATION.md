# 前端与后端 API 集成指南

## 📋 概述

本指南说明如何在前端（Vue 3 + TypeScript）中集成后端评估系统的 API。

---

## 🔌 API 调用配置

### 1️⃣ 更新 API 基础配置

确保 `frontend/src/utils/request.ts` 的基础 URL 配置正确：

```typescript
// frontend/src/utils/request.ts

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 添加认证 token
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### 2️⃣ 环境配置

在 `frontend/.env.local` 或 `frontend/.env` 中配置：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
```

---

## 📡 实现 API 函数

### 更新 `frontend/src/utils/request.ts`

添加以下评估相关的 API 函数：

```typescript
// frontend/src/utils/request.ts

import axios from 'axios'

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

// 请求拦截器 - 添加认证 token
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理错误
instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API 错误:', error.response?.data || error.message)
    throw error
  }
)

// ==================== 评估相关 API ====================

/**
 * 获取候选人的心理画像
 * @param candidateId 候选人ID
 * @returns {Promise<{code: number, data: Array}>}
 */
export const fetchPortrait = async (candidateId: string | number) => {
  return instance.get(`/assessment/portrait/${candidateId}`)
}

/**
 * 获取候选人的历史评估记录
 * @param candidateId 候选人ID
 * @param limit 返回数量（默认10）
 * @param offset 分页偏移（默认0）
 * @returns {Promise<{code: number, data: Array}>}
 */
export const fetchHistory = async (
  candidateId: string | number,
  limit: number = 10,
  offset: number = 0
) => {
  return instance.get(`/assessment/history/${candidateId}`, {
    params: { limit, offset }
  })
}

/**
 * 获取推荐岗位
 * @param candidateId 候选人ID
 * @param limit 推荐岗位数量（默认5）
 * @returns {Promise<{code: number, data: Array}>}
 */
export const fetchJobs = async (
  candidateId: string | number,
  limit: number = 5
) => {
  return instance.get(`/assessment/recommended-jobs/${candidateId}`, {
    params: { limit }
  })
}

/**
 * 获取评估报告详情
 * @param recordId 评估记录ID
 * @returns {Promise<{code: number, data: Object}>}
 */
export const fetchReportDetail = async (recordId: string | number) => {
  return instance.get(`/assessment/report/${recordId}`)
}

/**
 * 创建新的评估记录
 * @param candidateId 候选人ID
 * @param jobId 岗位ID
 * @returns {Promise<{code: number, data: Object}>}
 */
export const createAssessment = async (
  candidateId: string,
  jobId: number
) => {
  return instance.post('/assessment/records', {
    candidate_id: candidateId,
    job_id: jobId
  })
}

/**
 * 更新评估记录
 * @param recordId 评估记录ID
 * @param data 更新数据
 * @returns {Promise<{code: number, data: Object}>}
 */
export const updateAssessment = async (
  recordId: number,
  data: {
    match_score?: number
    assessment_status?: string
    conversation_summary?: string
    total_rounds?: number
    duration_minutes?: number
    personality_traits?: Record<string, number>
    strengths?: string[]
    gaps?: string[]
    recommendations?: string[]
  }
) => {
  return instance.patch(`/assessment/records/${recordId}`, data)
}

export default instance
```

---

## 🏠 HomeView 中的实现

在 `frontend/src/views/HomeView.vue` 中，API 调用已配置如下：

```typescript
// 加载数据
async function loadData() {
  loading.value = true
  try {
    const candidateId = user.value?.id || userStore.userId
    if (!candidateId) {
      console.warn('未获取到候选人ID')
      return
    }

    // 并行请求三个 API
    const [portrait, historyData, jobs] = await Promise.all([
      fetchPortrait(candidateId).catch(() => null),
      fetchHistory(candidateId).catch(() => []),
      fetchJobs(candidateId).catch(() => [])
    ])

    portraitData.value = portrait
    history.value = historyData || []
    recommendedJobs.value = jobs || []

    if (isNewUser.value) {
      showWelcome.value = true
    }
  } catch (error) {
    console.error('加载首页数据失败:', error)
    ElMessage.error('加载数据失败，请刷新重试')
  } finally {
    loading.value = false
  }
}
```

---

## 📊 数据类型定义

### 创建 TypeScript 类型定义文件

创建 `frontend/src/types/assessment.ts`：

```typescript
// frontend/src/types/assessment.ts

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
  assessement_details?: {
    total_rounds?: number
    duration_minutes?: number
    conversation_depth?: number
    roles_participated?: string[]
    overall_impression?: string
  }
}

/**
 * API 响应格式
 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}
```

---

## 🔄 获取数据流程

### 用户首次访问流程

```
用户登录
    ↓
进入首页 (HomeView.vue)
    ↓
检测 isNewUser（历史记录为空）
    ↓
显示欢迎弹窗 + 空状态雷达图
    ↓
用户点击"开始新评估"
    ↓
跳转到 /immersive 开始对话
    ↓
AI 评估完成，调用 updateAssessment
    ↓
返回首页，重新加载数据
    ↓
展示心理画像、历史记录、推荐岗位
```

### 用户再次访问流程

```
用户登录
    ↓
进入首页（isNewUser=false）
    ↓
并行调用三个 API：
  1. fetchPortrait    → 心理画像
  2. fetchHistory     → 历史评估
  3. fetchJobs        → 推荐岗位
    ↓
渲染各组件
    ↓
用户可以：
  - 点击"开始新评估" → /immersive
  - 点击历史记录 → /journey-report/{record_id}
  - 点击岗位卡片 → /assessment/{job_id}
```

---

## ⚡ 性能优化建议

### 1️⃣ 数据缓存

```typescript
// 在 stores/user.ts 中添加缓存
const assessmentCache = ref({
  portrait: null,
  history: [],
  jobs: [],
  lastUpdate: 0
})

const CACHE_DURATION = 5 * 60 * 1000  // 5分钟

export const useAssessmentCache = () => {
  const isCacheValid = () => {
    return Date.now() - assessmentCache.value.lastUpdate < CACHE_DURATION
  }

  const invalidateCache = () => {
    assessmentCache.value.lastUpdate = 0
  }

  return { assessmentCache, isCacheValid, invalidateCache }
}
```

### 2️⃣ 错误处理

```typescript
async function loadData() {
  loading.value = true
  try {
    // API 调用
  } catch (error) {
    if (error.response?.status === 401) {
      // 未认证 - 重定向到登录
      ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
    } else if (error.response?.status === 404) {
      // 数据不存在
      ElMessage.warning('数据不存在')
    } else {
      ElMessage.error('加载数据失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
```

### 3️⃣ 加载状态

在模板中添加加载指示器：

```vue
<el-skeleton v-if="loading" :rows="5" />
<div v-else>
  <!-- 内容 -->
</div>
```

---

## 🧪 测试 API 集成

### 测试步骤

1️⃣ **启动后端**
```bash
cd backend
python -m uvicorn main:app --reload
```

2️⃣ **启动前端**
```bash
cd frontend
npm run dev
```

3️⃣ **测试数据加载**
- 打开浏览器开发者工具 (F12)
- 切换到 Network 标签
- 访问首页
- 观察API请求和响应

4️⃣ **验证数据渲染**
- 心理画像雷达图是否渲染
- 历史评估列表是否显示
- 推荐岗位卡片是否显示

### 自动化测试

```typescript
// frontend/src/utils/__tests__/assessment.spec.ts

import { describe, it, expect, beforeAll } from 'vitest'
import { fetchPortrait, fetchHistory, fetchJobs } from '../request'

describe('Assessment API', () => {
  const TEST_CANDIDATE_ID = 'cand_001'

  it('should fetch portrait data', async () => {
    const response = await fetchPortrait(TEST_CANDIDATE_ID)
    expect(response.code).toBe(200)
    expect(Array.isArray(response.data)).toBe(true)
  })

  it('should fetch history data', async () => {
    const response = await fetchHistory(TEST_CANDIDATE_ID)
    expect(response.code).toBe(200)
    expect(Array.isArray(response.data)).toBe(true)
  })

  it('should fetch recommended jobs', async () => {
    const response = await fetchJobs(TEST_CANDIDATE_ID)
    expect(response.code).toBe(200)
    expect(Array.isArray(response.data)).toBe(true)
  })
})
```

---

## 🐛 常见问题解决

### 问题 1: CORS 错误

**错误信息：** `Access to XMLHttpRequest at 'http://localhost:8000/assessment/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**解决方案：**
- 后端已配置 CORS（见 main.py）
- 确保前端请求使用正确的基础 URL
- 检查浏览器控制台错误详情

### 问题 2: 401 未认证

**错误信息：** `{"code": 401, "message": "Unauthorized"}`

**解决方案：**
- 确保用户已登录
- 检查 localStorage 中的 auth_token
- 可能需要刷新 token

### 问题 3: 404 数据不存在

**错误信息：** `{"code": 404, "detail": "评估记录不存在"}`

**解决方案：**
- 确认 candidate_id 或 record_id 正确
- 检查数据库中是否有该条记录
- 可能需要先运行初始化脚本

### 问题 4: 数据为空

**现象：** 雷达图或岗位列表为空

**解决方案：**
- 新用户第一次访问时，portrait 为空是正常的
- 需要完成第一次评估后才会有数据
- 检查 fetchHistory() 返回值

---

## 📝 调试技巧

### 1️⃣ 启用详细日志

```typescript
// frontend/src/utils/request.ts

instance.interceptors.response.use(
  (response) => {
    console.log('[API Response]', response.config.url, response.data)
    return response.data
  },
  (error) => {
    console.error('[API Error]', error.config.url, error.response?.data || error.message)
    throw error
  }
)
```

### 2️⃣ 使用 Vue DevTools

- 安装 Vue DevTools 浏览器扩展
- 在 stores 中查看状态变化
- 追踪 computed 值变化

### 3️⃣ Swagger UI 测试

在浏览器中访问 http://localhost:8000/docs，可直接测试所有 API

---

## ✅ 集成检查清单

- [ ] request.ts 已添加所有评估 API 函数
- [ ] 环境变量已配置
- [ ] HomeView.vue 能正确调用 fetchPortrait、fetchHistory、fetchJobs
- [ ] 数据能正确显示在各组件中
- [ ] 雷达图能正确渲染
- [ ] 历史记录列表正常显示
- [ ] 岗位推荐卡片正常显示
- [ ] 路由跳转正常工作
- [ ] 错误处理正确

---

## 🚀 下一步

1. **实现评估流程集成**
   - 对话完成后调用 updateAssessment
   - 更新候选人的心理特质

2. **报告页面实现**
   - 创建 /journey-report/{record_id} 页面
   - 调用 fetchReportDetail() 展示完整报告

3. **实时通知**
   - 评估完成时显示成功提示
   - 数据更新时刷新首页

4. **性能优化**
   - 添加数据缓存
   - 优化加载时间

---

## 📞 技术支持

如有问题，请：
1. 查看 BACKEND_INTEGRATION_GUIDE.md
2. 检查 API 文档：http://localhost:8000/docs
3. 查看浏览器控制台错误
4. 运行 backend/test_assessment_api.py 验证后端

