# 🎯 下一步行动计划

**当前状态**: ImmersiveRoleDialogue 集成到 AssessmentView ✅  
**下一个里程碑**: 后端 API 实现 + Mock 替换

---

## 立即行动（今天）

### Task 1: 验证构建 (15分钟)

```bash
cd D:\Desktop\graduation-project\frontend

# 检查是否有错误
npm run build

# 预期输出:
# ✓ 1234 modules transformed
# dist/index.html  45.23 kB
# dist/assets/...
```

**失败排查**:
```bash
# 如果有 TypeScript 错误做：
npm run build 2>&1 | head -20  # 查看前20行错误

# 常见错误：
# 1) ImmersiveRoleDialogue 组件路径不对
#    → 检查: frontend/src/views/assessment/ImmersiveRoleDialogue.vue
# 2) Import 语句有问题
#    → 检查: AssessmentView.vue 第 220 行
# 3) Props 类型定义有误
#    → 检查: ImmersiveRoleDialogue.vue 第 370 行
```

---

### Task 2: 启动并测试前端 (30分钟)

```bash
# 启动开发服务器
npm run dev

# 预期看到:
# VITE v7.2.4 ready in 1234 ms
# ➜  Local:   http://localhost:5173/
```

**浏览器测试**:
```javascript
// 1. 打开 http://localhost:5173/assessment/demo
// 预期: 看到 Step 1 (基础信息)

// 2. 按右下角 "下一步" 按钮
// 预期: 进入 Step 2 (情景问答)

// 3. 再按 "下一步"
// 预期: 进入 Step 3 (多角色对话) ← 新增！

// 4. 检查左侧面板
// 预期: 看到 4 个角色卡片 (HR、技术总监、产品经理、CTO)

// 5. 检查右侧面板
// 预期: 看到 3 个卡片 (雷达图、行为模式、进度追踪)

// 6. 打开浏览器开发者工具 (F12)
// Console 中应该没有红色错误
```

---

### Task 3: 验证数据流 (30分钟)

**在浏览器控制台执行**:

```javascript
// 查看 Vue 实例状态
const apps = document.querySelectorAll('[data-v-app]')
// 应该有一个 Vue 3 应用

// 如果你安装了 Vue DevTools 扩展，可以查看：
// - 点击 Vue tab
// - 查看 AssessmentView 组件
// - 检查 `immersiveScores` 状态
```

**检查点**:
- [ ] AssessmentView 成功加载
- [ ] 可以导航到 Step 3 (多角色对话)
- [ ] ImmersiveRoleDialogue 组件渲染（看得到 UI）
- [ ] 没有关键 JavaScript 错误
- [ ] 能在 Step 3 输入和发送回答

---

## 第一周计划

### Day 1-2: 后端 Assessment API 实现 (🔴 高优先)

**目标**: 创建基础的评估记录 API

```python
# 需要创建: backend/routers/assessment.py
# 需要修改: backend/models/assessment.py
# 需要修改: backend/main.py (添加路由)

# 关键 API:
POST   /api/assessment/
  请求: {
    candidate_id: int,
    job_id: int,
    mode: "dialogue" | "situational",
    started_at: datetime
  }
  响应: {
    id: int,
    candidate_id: int,
    created_at: datetime,
    status: "started"
  }

GET    /api/assessment/{id}
  响应: {
    id: int,
    candidate_id: int,
    status: string,
    dialogue_history: [],
    scores: {},
    ...
  }

POST   /api/assessment/{id}/save-response
  请求: {
    message: string,
    speaker: string,
    analysis: {scores, sentiment, ...}
  }
  响应: {success: true}
```

**文档**: QUICK_IMPLEMENTATION_GUIDE.md (Problem 3 章节)

---

### Day 3-4: 替换 ImmersiveRoleDialogue Mock 函数 (🔴 高优先)

**目标**: 真实的 LLM 整合和 API 调用

**修改文件**: `frontend/src/views/assessment/ImmersiveRoleDialogue.vue`

**具体修改**:

1️⃣ 添加新的 API 调用函数 (request.ts):
```typescript
// frontend/src/utils/request.ts

export const analyzeDialogueMessage = (assessmentId: number, message: string, speaker: string) => {
  return request.post(`/api/assessment/${assessmentId}/analyze`, {
    message,
    speaker,
    timestamp: Date.now()
  })
}

export const getNextDialogueQuestion = (assessmentId: number, currentSpeaker: string, depth: number) => {
  return request.post(`/api/assessment/${assessmentId}/next-question`, {
    current_speaker: currentSpeaker,
    conversation_depth: depth
  })
}
```

2️⃣ 修改 ImmersiveRoleDialogue 的 mock 函数:
```typescript
// ImmersiveRoleDialogue.vue 中

// ❌ 删除这个 mock 函数
async function analyzeResponse(content: string, speaker: string) {
  return new Promise<any>((resolve) => {
    setTimeout(() => {
      resolve({
        scores: generateMockScores(),  // ← Mock
        sentiment: generateMockPatterns()
      })
    }, 1500)
  })
}

// ✅ 替换为真实 API 调用
async function analyzeResponse(content: string, speaker: string) {
  try {
    const response = await analyzeDialogueMessage(
      props.assessmentId || 0,
      content,
      speaker
    )
    return response.data
  } catch (error) {
    ElMessage.error('分析失败，请重试')
    return {
      scores: generateMockScores(),  // 降级处理
      sentiment: { emotion: '待分析', confidence: 0 }
    }
  }
}
```

---

### Day 5: 测试和调试 (🟠 中优先)

**测试场景 1: 完整流程**
```
1. 填写基础信息
2. 完成情景问答（3轮）
3. 进入多角色对话
4. 与 4 个角色交互
5. 完成对话
6. 查看综合报告
```

**测试场景 2: 错误处理**
```
1. 网络断开，重新连接
2. API 超时，自动重试
3. 无效输入，友好提示
```

**工具**:
- Postman 或 Insomnia: 测试 API 端点
- 浏览器 DevTools: 检查网络请求
- 数据库工具: 验证数据持久化

---

## 硬性里程碑

| 日期 | 任务 | 负责人 | 状态 |
|------|------|--------|------|
| 今日 | 前端构建 + 路由测试 | 你 | ⏳ 进行中 |
| 明日 | 后端 Assessment API | 你 | ⏳ 待开始 |
| 3日后 | 替换 Mock 为真实 API | 你 | ⏳ 待开始 |
| 5日后 | 完整流程测试通过 | 你 | ⏳ 待开始 |

---

## 🎯 关键 KPI

### 前端完成度
- [x] 组件导入
- [x] Props 配置
- [x] 事件处理
- [ ] 真实 API 调用 (下周)

### 后端完成度
- [ ] 数据模型
- [ ] API 端点
- [ ] LLM 整合
- [ ] 数据持久化

### 系统完成度
- [ ] 前后端通信
- [ ] 完整流程测试
- [ ] 错误处理
- [ ] 性能优化

---

## 关键检查点

在进入下个阶段之前，确认：

```bash
# 1. 前端无构建错误
cd frontend && npm run build
✓ 预期: 构建成功

# 2. 前端可启动
npm run dev
✓ 预期: 开发服务器运行

# 3. 可以导航到多角色对话
访问 http://localhost:5173/assessment/demo
按 Next → Next → 到达 Step 3
✓ 预期: 看到多角色对话 UI

# 4. 后端仍在运行
cd ../backend && python main.py
✓ 预期: FastAPI 应用启动，访问 /docs

# 5. 没有关键错误
浏览器 F12 → Console
✓ 预期: 没有红色错误，少量警告可接受
```

---

## 常见卡点及解决方案

### 卡点 1: 前端构建失败

**症状**: `npm run build` 报 TypeScript 错误

**原因**: ImmersiveRoleDialogue 导入或 Props 类型不匹配

**解决**:
```bash
# 1. 检查导入路径
grep -n "ImmersiveRoleDialogue" src/views/AssessmentView.vue

# 2. 检查文件是否存在
ls -la src/views/assessment/ImmersiveRoleDialogue.vue

# 3. 检查 Props 定义是否正确
grep -A 10 "defineProps" src/views/assessment/ImmersiveRoleDialogue.vue
```

---

### 卡点 2: ImmersiveRoleDialogue 报错或不显示

**症状**: Step 3 画面黑屏或有错误

**原因**: Props 未正确传入，或组件绑定问题

**检查清单**:
```vue
<!-- AssessmentView.vue 中 -->
<ImmersiveRoleDialogue
  :candidate-id="candidateId"                    ✓ 必须
  :target-position="candidate.desired_job"       ✓ 必须
  :initial-context="candidate"                   ✓ 新增
  :assessment-id="assessmentId"                  ← 如果需要
  @complete="handleImmersiveComplete"            ✓ 必须
  @update-scores="handleImmersiveScores"         ✓ 必须
/>
```

---

### 卡点 3: 数据流断裂

**症状**: 完成多角色对话后，Step 4 看不到评分

**原因**: allScores 计算属性没有包含 immersiveScores

**解决**:
```typescript
// AssessmentView.vue 中
const allScores = computed(() => ({
  ...(latestScores.value || {}),
  ...immersiveScores.value,     // ← 必须有这行
  ...personalityScores.value
}))

// 报告组件必须使用 allScores
<ReportGenerate :personalityScores="allScores" />
```

---

## 下周看板 🗓️

```
Priority 1 (必做):
┌─────────────────────────────────┐
│ ✅ 前端构建验证                  │
│ ⏳ 后端 Assessment API 完成       │
│ ⏳ Mock → 真实 API 替换          │
│ ⏳ 完整流程端到端测试            │
└─────────────────────────────────┘

Priority 2 (该做):
┌─────────────────────────────────┐
│ ⏳ ReportGenerate 增强           │
│ ⏳ 错误处理和重试机制            │
│ ⏳ 性能优化                      │
│ ⏳ 用户体验细节                  │
└─────────────────────────────────┘

Priority 3 (不急):
┌─────────────────────────────────┐
│ ⏳ PDF 导出功能                  │
│ ⏳ 数据分析仪表板                │
│ ⏳ 多语言支持                    │
│ ⏳ 性能监控                      │
└─────────────────────────────────┘
```

---

## 📞 技术支持

遇到问题？检查这些文档：

1. **MODULE_ANALYSIS_REPORT.md** - 整体架构和问题分析
2. **QUICK_IMPLEMENTATION_GUIDE.md** - 快速实施指南（包含 API 代码示例）
3. **IMMERSIVE_INTEGRATION_PLAN.md** - 集成方案详细设计
4. **IMMERSIVE_INTEGRATION_COMPLETE.md** - 集成完成报告

---

## 🎊 预期成果

完成这周的工作后，系统将：

✨ 拥有完整的沉浸式评估流程  
✨ 多模态数据采集（情景 + 对话 + 任务 + 特质）  
✨ 实时 LLM 分析和评分  
✨ 综合报告生成  
✨ 可用于毕业演示

---

**今天就开始验证构建吧！** 🚀

```bash
cd frontend
npm run build
```
