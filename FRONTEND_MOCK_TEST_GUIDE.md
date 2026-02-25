# 前端本地 Mock 测试指南

## 📋 概述

在后端 API 未完成前，可使用 Mock 数据进行前端开发和测试。本文档提供快速本地测试方案。

---

## 🛠️ 快速开始 (推荐)

### 方案 1：修改 request.ts 使用 Mock 数据（最快）

编辑 `frontend/src/utils/request.ts`，在 API 函数中返回 Mock 数据：

```typescript
// ============ Mock 数据 ============

const MOCK_PORTRAIT = [
  { name: '外向性', score: 8.5 },
  { name: '宜人性', score: 7.2 },
  { name: '尽责性', score: 9.1 },
  { name: '神经质', score: 3.4 },
  { name: '开放性', score: 8.8 }
]

const MOCK_HISTORY = [
  {
    id: 1,
    job_id: 101,
    job_title: '高级前端工程师',
    match_score: 85,
    created_at: '2024-02-20T10:30:00Z',
    assessment_status: 'completed'
  },
  {
    id: 2,
    job_id: 102,
    job_title: '技术负责人',
    match_score: 78,
    created_at: '2024-02-18T14:15:00Z',
    assessment_status: 'completed'
  }
]

const MOCK_JOBS = [
  {
    id: 101,
    title: '高级前端工程师',
    description: '领导前端技术团队，负责核心基础设施建设和技术方案设计',
    department: '技术部',
    level: 'P7',
    match_score: 88
  },
  {
    id: 102,
    title: '技术负责人',
    description: '负责技术部门战略规划和人才培养',
    department: '技术部',
    level: 'P8',
    match_score: 82
  },
  {
    id: 103,
    title: '产品经理',
    description: '负责C端产品规划与迭代',
    department: '产品部',
    level: 'P6',
    match_score: 76
  }
]

const MOCK_REPORT = {
  id: 1,
  job_title: '高级前端工程师',
  match_score: 85,
  created_at: '2024-02-20T10:30:00Z',
  personality_trait: MOCK_PORTRAIT,
  conversation_summary: '候选人在对话中展现了出色的问题分析能力和技术深度。在与技术总监的讨论中，能够清晰地解释复杂的技术概念。在与产品经理的交流中，表现出很好的用户视角思维。',
  match_analysis: {
    strengths: [
      '技术深度扎实，能独立解决复杂技术问题',
      '沟通能力强，能清晰表达和倾听他人观点',
      '学习能力强，对新技术充满热情'
    ],
    gaps: [
      '项目管理经验不足',
      '大团队协作经验相对较少'
    ]
  },
  recommendations: [
    '建议参与更多大型项目的团队合作',
    '推荐学习系统架构和服务设计相关知识',
    '可考虑参与开源项目，扩展技术视野'
  ]
}

// ============ Mock API 函数 ============

export const fetchPortrait = async (candidateId: string | number) => {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 500))
  return MOCK_PORTRAIT
}

export const fetchHistory = async (candidateId: string | number) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  return MOCK_HISTORY
}

export const fetchJobs = async (candidateId: string | number) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  return MOCK_JOBS
}

export const fetchReportDetail = async (recordId: string | number) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  return MOCK_REPORT
}
```

**使用方式：**
1. 复制上述代码到 `request.ts` 末尾
2. 注释掉原有的 API 函数实现（或保留真实实现，通过环境变量切换）
3. 启动前端，正常使用

**优点：** 最快，无需额外配置
**缺点：** 无法测试错误处理，需手动注释

---

### 方案 2：使用 MSW (Mock Service Worker)（推荐）

MSW 是拦截网络请求的现代方案，可无缝切换真实API和Mock数据。

#### 安装

```bash
npm install msw --save-dev
```

#### 创建 Mock 处理器

新增文件 `frontend/src/mocks/handlers.ts`：

```typescript
import { http, HttpResponse } from 'msw'

export const handlers = [
  // 心理画像
  http.get('/assessment/portrait/:candidateId', () => {
    return HttpResponse.json({
      code: 200,
      message: 'success',
      data: [
        { name: '外向性', score: 8.5 },
        { name: '宜人性', score: 7.2 },
        { name: '尽责性', score: 9.1 },
        { name: '神经质', score: 3.4 },
        { name: '开放性', score: 8.8 }
      ]
    })
  }),

  // 历史记录
  http.get('/assessment/history/:candidateId', () => {
    return HttpResponse.json({
      code: 200,
      message: 'success',
      data: [
        {
          id: 1,
          job_id: 101,
          job_title: '高级前端工程师',
          match_score: 85,
          created_at: '2024-02-20T10:30:00Z'
        }
      ]
    })
  }),

  // 推荐岗位
  http.get('/assessment/recommended-jobs/:candidateId', () => {
    return HttpResponse.json({
      code: 200,
      message: 'success',
      data: [
        {
          id: 101,
          title: '高级前端工程师',
          description: '领导前端技术团队',
          department: '技术部',
          match_score: 88
        }
      ]
    })
  }),

  // 报告详情
  http.get('/assessment/report/:recordId', () => {
    return HttpResponse.json({
      code: 200,
      message: 'success',
      data: {
        id: 1,
        job_title: '高级前端工程师',
        match_score: 85,
        personality_trait: [
          { name: '外向性', score: 8.5 }
        ]
      }
    })
  })
]
```

#### 设置 MSW Server

新增文件 `frontend/src/mocks/server.ts`：

```typescript
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

#### 在测试中启用

新增/编辑 `frontend/src/mocks/browser.ts`（Vitest/Jest）：

```typescript
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)
```

#### 在 main.ts 中启用（开发模式）

```typescript
// frontend/src/main.ts
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)

// 仅在开发模式下启用 Mock
if (import.meta.env.DEV && import.meta.env.VITE_MOCK === 'true') {
  import('./mocks/browser').then(({ worker }) => {
    worker.start()
  })
}

app.mount('#app')
```

#### 在 .env 中配置

```bash
# .env.local
VITE_MOCK=true     # 启用 Mock
# VITE_MOCK=false  # 使用真实 API
```

**优点：** 生产环境无需改动代码，可动态切换
**缺点：** 初始配置稍复杂

---

## 📊 Mock 数据完整示例

### 新用户场景

```typescript
// 新用户：没有任何评估记录
const MOCK_NEW_USER = {
  portrait: [],          // 空
  history: [],           // 空
  jobs: [                // 默认热门岗位
    { id: 201, title: '前端工程师', match_score: 0 },
    { id: 202, title: '后端工程师', match_score: 0 },
    { id: 203, title: '产品经理', match_score: 0 }
  ]
}
```

### 老用户场景

```typescript
// 老用户：有3次评估记录
const MOCK_OLD_USER = {
  portrait: [
    { name: '外向性', score: 8 },
    { name: '宜人性', score: 7 },
    { name: '尽责性', score: 9 },
    { name: '神经质', score: 3 },
    { name: '开放性', score: 8.5 }
  ],
  history: [
    { id: 1, job_title: '高级前端', match_score: 85, created_at: '2024-02-20' },
    { id: 2, job_title: '技术负责人', match_score: 78, created_at: '2024-02-18' },
    { id: 3, job_title: '架构师', match_score: 82, created_at: '2024-02-15' }
  ],
  jobs: [
    { id: 101, title: '高级前端工程师', match_score: 88 },
    { id: 102, title: '技术负责人', match_score: 82 },
    { id: 103, title: '架构师', match_score: 85 }
  ]
}
```

---

## 🧪 本地测试步骤

### 步骤 1: 启动前端开发服务器

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

### 步骤 2: 登录测试账户

| 角色 | 用户名 | 密码 | 预期 |
|------|--------|------|------|
| 新候选人 | `new_candidate` | `123456` | 首页显示欢迎弹窗 + 空状态 |
| 老候选人 | `old_candidate` | `123456` | 首页显示画像 + 历史 + 推荐 |

### 步骤 3: 验证各功能

#### ✅ 新用户流程
```
1. 登录 new_candidate
2. 跳转到 /home
3. 应看到：
   ✓ "欢迎弹窗"对话框
   ✓ 空状态雷达图（插画+文字）
   ✓ "开始新评估" 按钮可点击
   ✓ "查看最新报告" 按钮禁用
4. 点击 "开始新评估"
   ✓ 关闭弹窗
   ✓ 跳转到 /immersive
5. 返回首页
   ✓ 数据已更新？（取决于后端实现）
```

#### ✅ 老用户流程
```
1. 登录 old_candidate
2. 跳转到 /home
3. 应看到：
   ✓ 完整的心理画像（雷达图 + 数值）
   ✓ 文字总结（优势/改进空间）
   ✓ 历史评估列表（3条记录）
   ✓ 推荐岗位卡片（3个）
   ✓ 欢迎弹窗不显示
   ✓ "查看最新报告" 按钮启用
4. 点击历史记录 → 跳转到报告页
5. 点击岗位卡 → 跳转到评估页
```

#### ✅ 响应式布局
```
使用浏览器开发者工具的响应式设计模式：
- Desktop (1920px) ✓ 左侧角色面板 | 中间对话 | 右侧洞察面板
- Tablet (768px) ✓ 布局调整
- Mobile (375px) ✓ 竖屏堆叠
```

---

## 🔧 常见调整

### 修改 Mock 数据匹配度

```typescript
// 让 old_candidate 的推荐岗位都 > 85 分
const MOCK_JOBS_HIGH_MATCH = MOCK_JOBS.map(job => ({
  ...job,
  match_score: 80 + Math.random() * 20  // 80-100 随机
}))
```

### 模拟错误响应

```typescript
// MSW 中添加错误端点
http.get('/assessment/portrait/:candidateId', () => {
  return HttpResponse.json(
    { code: 500, message: 'Internal Server Error' },
    { status: 500 }
  )
})
```

### 模拟延迟

```typescript
// 调整延迟时间以测试 loading 状态
await new Promise(resolve => setTimeout(resolve, 2000))  // 2 秒
```

---

## 🎬 快速演示视频脚本

如果需要向导师/ 评审展示系统，可按以下流程操作：

```
时间: 2 分钟
1. 登录 old_candidate (30秒)
   → 展示首页完整设计
   → 说明：这是重新设计的候选人首页，强调"AI评估中心"定位
   
2. 点击推荐岗位卡 (30秒)
   → 进入评估页
   → 说明：岗位推荐是基于心理画像的智能推荐
   
3. 返回首页，点击历史记录 (30秒)
   → 查看报告页
   → 说明：详细报告包含心理特质、匹配分析、改进建议
   
4. 未来规划 (30秒)
   → 说明计划的后端接口实现
   → 说明与现有评估流程的集成
```

---

## 📝 注意事项

### 生成环境切换
当后端 API 完成时，确保可以无缝切换：

```typescript
// 真实 API 调用时，删除 Mock 相关代码或设置 VITE_MOCK=false
export const fetchPortrait = async (candidateId: string | number) => {
  // 真实实现
  const response = await request.get(`/assessment/portrait/${candidateId}`)
  return response.data?.data || []
}
```

### 缓存问题
测试时可能遇到缓存问题，使用 DevTools 清除：
```javascript
// 浏览器控制台
localStorage.clear()
sessionStorage.clear()
```

### 时间敏感测试
某些功能（如"最新报告"时间戳）可能需要调整 Mock 数据的时间：
```typescript
const now = new Date()
const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)

created_at: yesterday.toISOString()
```

---

## ✅ 验收清单

- [ ] 前端页面能正常加载，无控制台错误
- [ ] 新用户看到欢迎弹窗和空状态
- [ ] 老用户看到完整的心理画像和历史
- [ ] 推荐岗位卡可点击，跳转正确
- [ ] 历史列表可点击，跳转报告页
- [ ] 响应式布局在各尺寸正确显示
- [ ] "开始新评估"导航至评估页
- [ ] "查看最新报告"在有数据时启用
- [ ] 性能良好（加载<1秒，切换<300ms）

---

## 🔗 相关文档

- [前端实现指南](./CANDIDATE_HOME_IMPLEMENTATION.md)
- [后端API规范](./BACKEND_API_SPECIFICATION.md)
- [项目README](./README.md)
