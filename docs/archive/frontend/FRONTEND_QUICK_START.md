# 前端快速开始指南 - AI 智能面试系统

## 🚀 5 分钟启动前端应用

### 前置要求

- Node.js 16+
- npm 8+
- 后端服务正在运行于 http://localhost:8000（可选，但推荐）

---

## ⚡ 快速启动

### 方式 1️⃣：自动启动脚本（推荐）

在项目根目录运行：

```powershell
# Windows PowerShell
.\startup.ps1

# 选择选项 2: 启动后端和前端（自动）
```

---

### 方式 2️⃣：手动启动

#### 步骤 1：安装依赖

```bash
cd frontend
npm install
```

预期输出：
```
added 500+ packages in 45s
```

#### 步骤 2：启动开发服务器

```bash
npm run dev
```

预期输出：
```
  VITE v4.x.x  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

#### 步骤 3：访问应用

打开浏览器访问：http://localhost:5173

---

## ✅ 验证集成

### 检查清单

访问应用后，检查以下内容：

- [ ] 页面加载完毕，无错误
- [ ] 能看到首页（HomeView）
- [ ] 心理画像区域显示（可能为空状态）
- [ ] 历史评估部分可见（如果有数据）
- [ ] 推荐岗位卡片可见（如果有数据）
- [ ] 浏览器控制台（F12）无红色错误

### 测试后端连接

打开浏览器开发者工具（F12），查看 Network 标签：

1. 刷新页面
2. 查看是否有以下 API 调用：
   - GET `/assessment/portrait/{candidateId}`
   - GET `/assessment/history/{candidateId}`
   - GET `/assessment/recommended-jobs/{candidateId}`

如果看到这些请求，说明前端已成功调用后端 API ✅

---

## 🔧 常见问题

### 问题 1️⃣：页面白屏或报错

**解决方案：**
```bash
# 清除缓存和重新安装
rm -r node_modules package-lock.json
npm install
npm run dev
```

### 问题 2️⃣：后端 API 调用失败

**症状：** 浏览器控制台显示 `GET /assessment/... 404`

**解决方案：**
1. 确认后端服务已启动：http://localhost:8000
2. 检查后端端口是否为 8000
3. 查看 `frontend/src/utils/request.ts` 中的 baseURL 配置

```typescript
const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',  // 确保这是正确的
  timeout: 30000,
})
```

### 问题 3️⃣：CORS 错误

**症状：** `Access to XMLHttpRequest blocked by CORS policy`

**解决方案：**
后端已配置 CORS，确保：
1. 后端正在运行
2. 前端是从 `http://localhost:5173` 访问（不是其他端口）

### 问题 4️⃣：登录后无法显示候选人数据

**症状：** 首页显示欢迎弹窗，但数据为空

**解决方案：**
1. 新用户第一次访问时，数据为空是正常的
2. 需要完成一次评估后，才会有心理画像和历史记录
3. 检查 localStorage 中是否存储了 `user_id`

```javascript
// 在浏览器控制台检查
localStorage.getItem('user_id')
localStorage.getItem('user_token')
```

---

## 📱 项目结构

```
frontend/
├── src/
│   ├── views/
│   │   ├── HomeView.vue           ← 候选人首页（主要页面）
│   │   ├── IndexView.vue          ← 容器页面
│   │   └── ...
│   ├── components/
│   │   ├── RadarChart.vue         ← 心理画像雷达图
│   │   ├── AssessmentHistory.vue  ← 历史评估列表
│   │   ├── JobCard.vue            ← 岗位推荐卡片
│   │   └── EmptyState.vue         ← 空状态提示
│   ├── stores/
│   │   └── user.ts                ← 用户状态管理
│   ├── utils/
│   │   └── request.ts             ← API 调用函数
│   ├── types/
│   │   └── assessment.ts          ← TypeScript 类型定义
│   └── router/
│       └── index.ts               ← 路由配置
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## 🎯 核心功能点

### 1️⃣ HomeView.vue - 候选人首页

**位置：** `frontend/src/views/HomeView.vue`

**功能：**
- 显示心理画像（雷达图）
- 展示历史评估记录
- 推荐相关岗位
- 新用户欢迎提示

**API 调用：**
```typescript
const [portrait, historyData, jobs] = await Promise.all([
  fetchPortrait(candidateId),    // 心理画像
  fetchHistory(candidateId),     // 历史记录
  fetchJobs(candidateId)         // 推荐岗位
])
```

### 2️⃣ RadarChart.vue - 心理画像

**位置：** `frontend/src/components/RadarChart.vue`

**功能：**
- 绘制五大人格特质雷达图
- 实时响应数据变化
- 支持多种设备尺寸

**使用方式：**
```vue
<RadarChart :data="portraitData" />
```

### 3️⃣ AssessmentHistory.vue - 历史记录

**位置：** `frontend/src/components/AssessmentHistory.vue`

**功能：**
- 显示评估历史列表
- 点击查看详情
- 显示匹配度进度条

### 4️⃣ JobCard.vue - 岗位推荐

**位置：** `frontend/src/components/JobCard.vue`

**功能：**
- 展示推荐岗位
- 显示匹配度标签
- 快速评估按钮

---

## 🔌 API 集成点

### 前端调用的后端 API

```typescript
// 在 frontend/src/utils/request.ts 中定义

// 1. 获取心理画像
fetchPortrait(candidateId)
// GET /assessment/portrait/{candidateId}

// 2. 获取历史评估
fetchHistory(candidateId)
// GET /assessment/history/{candidateId}

// 3. 获取推荐岗位
fetchJobs(candidateId)
// GET /assessment/recommended-jobs/{candidateId}

// 4. 获取报告详情
fetchReportDetail(recordId)
// GET /assessment/report/{recordId}
```

---

## 🧪 测试 API 集成

### 在浏览器中测试

1. 打开 http://localhost:8000/docs
2. 在 Swagger UI 中测试各个 API 端点
3. 确认数据格式正确

### 在前端中测试

打开浏览器开发者工具（F12），执行：

```javascript
// 测试 API 调用
const { fetchPortrait } = await import('/src/utils/request.ts')
const portrait = await fetchPortrait('cand_001')
console.log(portrait)
```

---

## 📊 状态管理

### 用户状态（Pinia Store）

**位置：** `frontend/src/stores/user.ts`

**可用状态：**
```typescript
const userStore = useUserStore()

userStore.token          // 认证 token
userStore.username       // 用户名
userStore.userId         // 用户ID
userStore.isHR           // 是否HR用户
userStore.profile        // 用户详细资料
userStore.candidateId    // 候选人ID（计算属性）
```

**使用方式：**
```typescript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const candidateId = userStore.candidateId
```

---

## 🎨 样式和 UI

### 使用的 UI 库

- **Element Plus**：Vue 3 组件库
- **Icon**：使用 Element Plus 内置图标
- **自定义样式**：Scoped CSS

### 响应式设计

页面支持三种断点：
- 桌面端（>1200px）：完整布局
- 平板端（768px - 1200px）：折叠布局
- 手机端（<768px）：单列布局

---

## 🚀 构建和部署

### 开发模式

```bash
npm run dev
```

### 生产构建

```bash
# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 构建输出

```
dist/
├── index.html
├── assets/
│   ├── js/
│   └── css/
└── ...
```

---

## 📚 重要文件说明

| 文件 | 用途 |
|------|------|
| `main.ts` | 应用入口 |
| `App.vue` | 根组件 |
| `HomeView.vue` | 候选人首页 |
| `request.ts` | API 调用封装 |
| `user.ts` | 用户状态管理 |
| `router/index.ts` | 路由配置 |
| `types/assessment.ts` | 类型定义 |

---

## 🔗 相关链接

- **后端文档**：[BACKEND_INTEGRATION_GUIDE.md](../BACKEND_INTEGRATION_GUIDE.md)
- **API 规范**：[BACKEND_API_SPECIFICATION.md](../BACKEND_API_SPECIFICATION.md)
- **集成指南**：[FRONTEND_BACKEND_INTEGRATION.md](../FRONTEND_BACKEND_INTEGRATION.md)
- **Vite 文档**：https://vitejs.dev/
- **Vue 3 文档**：https://vuejs.org/
- **Element Plus**：https://element-plus.org/

---

## 💡 提示和最佳实践

### 开发中

1. **使用 Vue DevTools**
   - 安装浏览器扩展
   - 调试组件和状态

2. **查看网络请求**
   - F12 → Network 标签
   - 审查 API 调用和响应

3. **检查浏览器存储**
   - F12 → Application → Storage
   - 查看 localStorage 中的数据

### 调试技巧

```typescript
// 在组件中添加日志
console.log('candidateId:', userStore.candidateId)
console.log('portrait data:', portraitData.value)
console.log('history:', history.value)
```

---

## ✅ 完成检查清单

启动前端后，检查以下内容：

- [ ] npm install 完成，无错误
- [ ] npm run dev 启动成功
- [ ] 访问 http://localhost:5173 能打开应用
- [ ] 页面能正常渲染
- [ ] 能看到首页布局
- [ ] 浏览器控制台无红色错误
- [ ] 能看到 API 调用（Network 标签）
- [ ] 数据正确显示

---

**🎉 前端集成完成！**

现在您有了一个完整的前后端集成系统：
- ✅ 前端应用正在运行
- ✅ 后端 API 可访问
- ✅ 数据能正确显示

享受开发! 🚀
