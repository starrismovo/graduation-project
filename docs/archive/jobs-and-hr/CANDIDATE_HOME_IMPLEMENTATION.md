# 候选人首页重新设计 - 完整实现指南

## 📋 概述

将候选人首页（HomeView.vue）从传统招聘平台风格重新设计为 **"AI评估中心"** 模式，强调：
- 心理画像可视化（五大人格雷达图）
- 沉浸式多角色对话评估
- 岗位匹配决策支持

---

## 🗂️ 文件变更清单

### 1️⃣ **页面组件**

#### `frontend/src/views/HomeView.vue` ✅
**状态：已更新**
- 完整重构为新设计的候选人首页
- 新增顶部欢迎栏 + 操作按钮
- 心理画像展示区（雷达图 + 文字总结）
- 历史评估记录列表（AssessmentHistory组件）
- 精选岗位推荐（3-5条JobCard组件）
- 底部系统说明卡
- 新用户欢迎对话框
- 完整的响应式样式

**关键逻辑：**
```typescript
// 新/老用户判断
const isNewUser = computed(() => history.value.length === 0)

// 数据加载
async function loadData() {
  const [portrait, history, jobs] = await Promise.all([
    fetchPortrait(candidateId),
    fetchHistory(candidateId),
    fetchJobs(candidateId)
  ])
}

// 开始评估导航
function startNewAssessment() {
  router.push('/immersive')
}
```

#### `frontend/src/views/assessment/ReportPage.vue` ✅
**新建文件**
- 评估报告详情页
- 展示基本信息、心理特质、匹配分析
- 建议和下一步行动
- 下载报告功能（预留）

---

### 2️⃣ **可复用组件**

#### `frontend/src/components/RadarChart.vue` ✅
**新建文件 - 五大人格雷达图**
```vue
<RadarChart 
  :data="[
    { name: '外向性', score: 8 },
    { name: '宜人性', score: 7 },
    { name: '尽责性', score: 9 },
    { name: '神经质', score: 3 },
    { name: '开放性', score: 8 }
  ]"
/>
```
- 基于ECharts的雷达图可视化
- 自动响应数据变化
- 支持窗口缩放

#### `frontend/src/components/EmptyState.vue` ✅
**新建文件 - 空状态提示**
```vue
<EmptyState
  title="还没有评估"
  text="点击'开始新评估'来探索你的心理特质！"
  :button-text="null"
/>
```
- 友好的插画（默认SVG或自定义图片）
- 支持操作按钮
- 多场景复用

#### `frontend/src/components/AssessmentHistory.vue` ✅
**新建文件 - 历史评估列表**
```vue
<AssessmentHistory
  :data="[
    {
      id: 1,
      created_at: '2024-02-24 10:30',
      job_title: '前端工程师',
      match_score: 85
    }
  ]"
  @view="viewRecord"
/>
```
- 表格展示历史记录
- 匹配度进度条可视化
- 查看详情功能

#### `frontend/src/components/JobCard.vue` ✅
**新建文件 - 岗位推荐卡**
```vue
<JobCard
  :job="{
    id: 1,
    title: '高级前端工程师',
    description: '领导前端团队开发...',
    department: '技术部',
    match_score: 88
  }"
  @assess="goToAssessment"
/>
```
- 简洁卡片设计
- 匹配度标签 + 进度条
- 点击评估按钮快速开始

---

### 3️⃣ **API 函数**

#### `frontend/src/utils/request.ts` ✅
**新增函数：**

```typescript
/**
 * 获取候选人的心理画像
 * @returns [{name: string, score: number}]
 */
export const fetchPortrait = async (candidateId: string | number)

/**
 * 获取历史评估记录
 * @returns [{id, job_id, job_title, match_score, created_at}]
 */
export const fetchHistory = async (candidateId: string | number)

/**
 * 获取推荐岗位
 * @returns [{id, title, match_score, description, department, level}]
 */
export const fetchJobs = async (candidateId: string | number)

/**
 * 获取报告详情
 * @returns 完整报告数据
 */
export const fetchReportDetail = async (recordId: string | number)
```

**后端对接端点示例：**
```
GET /assessment/portrait/{candidateId}
GET /assessment/history/{candidateId}
GET /assessment/recommended-jobs/{candidateId}
GET /assessment/report/{recordId}
```

---

### 4️⃣ **路由配置**

#### `frontend/src/router/index.ts` ✅
**新增和更新的路由：**

```typescript
{
  path: '/home',
  component: IndexView,
  meta: { requiresAuth: true }
  // 主页容器（Index内嵌HomeView或HRHomeView）
}

{
  path: '/candidate-home',
  name: 'CandidateHome',
  component: () => import('../views/HomeView.vue'),
  meta: { requiresAuth: true }
  // 候选人首页（新设计）
}

{
  path: '/immersive',
  name: 'ImmersiveAssessment',
  component: () => import('../views/assessment/ImmersiveRoleDialogue.vue'),
  meta: { requiresAuth: true, mode: 'immersive' }
  // 沉浸式对话评估
}

{
  path: '/assessment/:id',
  name: 'Assessment',
  component: AssessmentView,
  meta: { requiresAuth: true }
  // 固有评估流程（带岗位参数）
}

{
  path: '/report/:recordId',
  name: 'AssessmentReport',
  component: () => import('../views/assessment/ReportPage.vue'),
  meta: { requiresAuth: true }
  // 评估报告页
}
```

---

## 🔄 用户交互流程

### 新用户流程
```
登录 → 访问 /home → 检测 isNewUser=true
→ 展示欢迎弹窗 + 空状态雷达图
→ 用户点击"开始新评估"
→ 路由至 /immersive（多角色对话）
→ 完成评估后跳转至报告页
→ 报告保存后返回首页，显示新画像 + 历史记录
```

### 老用户流程
```
登录 → 访问 /home
→ 加载并展示心理画像 + 历史记录 + 推荐岗位
→ 用户可：
   ① 点击"开始新评估" → 启动新的评估流程
   ② 点击历史记录 → 查看详细报告
   ③ 点击推荐岗位卡 → 对该岗位进行评估
```

---

## 🎨 视觉与交互设计要点

### 色彩方案
- **主色**：`#409eff`（蓝色，用于按钮和标签）
- **强调**：`#667eea - #764ba2`（渐变紫色，用于特殊按钮）
- **成功**：`#67c23a`（绿色）
- **预警**：`#e6a23c`（橙色）
- **错误**：`#f56c6c`（红色）
- **背景**：`#f9fafc - #e8eef5`（浅蓝渐变）

### 关键组件样式
- **顶部操作栏**：大按钮（140px+），对比色突出
- **卡片设计**：浅阴影 + hover提升效果
- **空状态**：友好插画 + 鼓励语
- **进度条**：彩色渐变，高度6px
- **响应式**：平板用flex-col，手机用100%宽度

---

## ⚙️ 后端接口要求

### 心理画像接口
```json
GET /assessment/portrait/{candidateId}
Response: {
  data: [
    { name: "外向性", score: 8 },
    { name: "宜人性", score: 7 },
    { name: "尽责性", score: 9 },
    { name: "神经质", score: 3 },
    { name: "开放性", score: 8 }
  ]
}
```

### 历史记录接口
```json
GET /assessment/history/{candidateId}
Response: {
  data: [
    {
      id: 1,
      job_id: 101,
      job_title: "前端工程师",
      match_score: 85,
      created_at: "2024-02-20T10:30:00Z",
      assessment_status: "completed"
    }
  ]
}
```

### 推荐岗位接口
```json
GET /assessment/recommended-jobs/{candidateId}
Response: {
  data: [
    {
      id: 101,
      title: "高级前端工程师",
      description: "领导前端技术团队...",
      department: "技术部",
      level: "P7",
      match_score: 88
    }
  ]
}
```

### 报告详情接口
```json
GET /assessment/report/{recordId}
Response: {
  data: {
    id: 1,
    job_title: "前端工程师",
    match_score: 85,
    created_at: "2024-02-20T10:30:00Z",
    personality_trait: [ ... ],
    conversation_summary: "候选人展现了...",
    match_analysis: {
      strengths: ["沟通能力强", "技术深度扎实"],
      gaps: ["项目管理经验不足"]
    },
    recommendations: [
      "建议学习项目管理工具",
      "参与大型项目团队工作"
    ]
  }
}
```

---

## 🚀 部署与测试清单

### 前端测试
- [ ] HomeView 在无历史记录时正确显示空状态和欢迎弹窗
- [ ] 心理画像雷达图正确渲染
- [ ] 历史列表在有数据时正确显示
- [ ] 推荐岗位卡片可点击并跳转
- [ ] 响应式布局在各端正确显示
- [ ] 路由导航流畅无卡顿

### 后端测试
- [ ] 四个API端点可正常调用
- [ ] 返回数据格式符合期望
- [ ] 错误处理正确（超时、404等）
- [ ] 新用户第一次访问返回空数组
- [ ] 老用户返回真实数据

### 集成测试
- [ ] 新用户完整流程：注册 → 首页 → 开始评估 → 完成 → 首页更新
- [ ] 老用户流程：登录 → 首页显示画像 → 查看历史 → 新评估
- [ ] 评估报告页面正确展示
- [ ] 匹配度计算准确

---

## 📝 注意事项

### 数据缓存
- 建议在顶部操作栏添加"刷新"按钮
- 使用 localStorage 缓存用户画像（可选）
- 评估完成后清空缓存，触发数据重新加载

### 性能优化
- 使用 Promise.all() 并行加载三个数据
- 图表初始化放在 onMounted() 中
- 路由跳转时传参而非全局状态（若可能）

### 错误处理
- API 调用失败时返回空数组，页面显示空状态
- 显示友好的错误提示，而非直接throw
- 实装 loading 状态防止重复请求

### 未来扩展
- 支持导出PDF报告
- 心理特质动态评分算法优化
- 个性化岗位推荐算法
- 对话内容详细回放
- 与简历/投递记录关联

---

## 📚 文件清单总结

```
frontend/src/
├── views/
│   ├── HomeView.vue ✅ (已更新)
│   ├── IndexView.vue (容器，保持不变)
│   ├── HRHomeView.vue (HR首页，保持不变)
│   └── assessment/
│       ├── ReportPage.vue ✅ (新建)
│       ├── ImmersiveRoleDialogue.vue (已存在)
│       └── AssessmentViewIntegration.vue (已存在)
├── components/
│   ├── RadarChart.vue ✅ (新建)
│   ├── EmptyState.vue ✅ (新建)
│   ├── AssessmentHistory.vue ✅ (新建)
│   └── JobCard.vue ✅ (新建)
├── router/
│   └── index.ts ✅ (已更新路由配置)
└── utils/
    └── request.ts ✅ (新增API函数)
```

---

## ✅ 完成度

| 组件/功能 | 状态 | 备注 |
|---------|------|------|
| HomeView重新设计 | ✅ | 完整实现 |
| RadarChart | ✅ | ECharts 集成 |
| EmptyState | ✅ | 通用组件 |
| AssessmentHistory | ✅ | 表格展示 |
| JobCard | ✅ | 卡片推荐 |
| ReportPage | ✅ | 报告详情 |
| API 函数 | ✅ | 4个核心函数 |
| 路由配置 | ✅ | 完整路由 |
| 样式响应式 | ✅ | 三断点适配 |
| 用户流程 | ✅ | 新/老用户分流 |
| 后端对接 | 🔄 | 需后端实现API |

---

## 🎯 课题契合度

✨ **本设计强调：**
- **AI智能体驱动**：核心是沉浸式多角色对话（ImmersiveRoleDialogue）
- **心理特质可视化**：雷达图 + 文字总结，清晰展示 Big Five 评分
- **匹配决策支持**：基于画像的岗位推荐、历史对比、改进建议
- **脱离招聘痕迹**：无海投、无筛选器，纯评估中心定位

✅ **完美适应"基于AI智能体的人岗匹配心理特质评估系统"课题**

---

## 📞 技术支持

- **前端框架**：Vue 3 + TypeScript
- **UI库**：Element Plus
- **数据可视化**：ECharts
- **状态管理**：Pinia（useUserStore）
- **路由**：Vue Router 4
- **HTTP**：Axios（axios实例）

所有组件已采用 Composition API + `<script setup>` 现代写法。
