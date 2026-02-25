# 📐 集成方案设计文档

**日期**: 2026-02-25  
**目标**: 将 ImmersiveRoleDialogue 与 AssessmentView 进行无缝集成

---

## 当前状态分析

### AssessmentView (现有)
```
Step 1: BasicInfo      → 基础信息采集
Step 2: SituationalQA  → 情景问答评估  
Step 3: CognitiveTask  → 认知任务
Step 4: PersonalityScale → 特质量表
Step 5: ReportGenerate → 报告生成
```

### ImmersiveRoleDialogue (独立)
```
独立的完整组件，包含：
- 4个角色（HR、技术总监、产品经理、CTO）
- 5个评估阶段
- 实时评分和分析
- 但全是 mock 数据
```

---

## 推荐集成方案

### 方案 A: 增强型集成 ⭐ **推荐**
```
Step 1: BasicInfo              基础信息
    ↓
Step 2: SituationalQA          情景问答（保留）
    ↓
Step 2.5: ImmersiveRoleDialogue ✨ **新增** （可选）
    ↓
Step 3: CognitiveTask          认知任务 
    ↓
Step 4: PersonalityScale       特质量表
    ↓
Step 5: ReportGenerate         报告生成

优点:
✅ 不破坏现有流程
✅ 用户可选参加多角色对话
✅ 数据可累积
✅ 循序渐进评估

缺点:
⚠️ 流程较长
```

### 方案 B: 标准替换集成
```
允许用户选择评估模式：
├─ 传统模式 → 情景问答 + 认知任务 + 量表
└─ 沉浸式模式 → 多角色对话 (ImmersiveRoleDialogue)

优点:
✅ 模式清晰
✅ 用户自主选择
✅ 各自专注

缺点:
❌ 两个完全独立的流程
```

---

## 实施步骤（选择方案 A）

### Step 1: 增加新的步骤定义
在 AssessmentView 中：
- 增加 Step 2.5 的 UI（或重新编号为 Step 3，后续步骤顺序下移）
- 导入 ImmersiveRoleDialogue 组件

### Step 2: 状态数据同步
将 ImmersiveRoleDialogue 的数据流入到 AssessmentView:
- 接收 immersive 返回的评分
- 与现有的 latestScores 合并
- 保持统一的数据结构

### Step 3: 修复 ImmersiveRoleDialogue 的 Mock 问题
- 添加 props 接收 assessmentId
- 替换 mock API 为真实后端调用
- 确保评分数据正确返回

### Step 4: 前端路由调整
- 保留原有的 /assessment/:id 路由
- 该路由自动使用新的集成流程

---

## 数据流设计

```
┌─ AssessmentView ────────────────────────────────────────┐
│  activeStep = 1 (BasicInfo)                             │
│  ↓ handleNext()                                         │
│  activeStep = 2 (SituationalQA)                         │
│  ├─ answers: [...回答...]                              │
│  ├─ latestScores: 情景评分                              │
│  ↓ handleNext()                                         │
│  activeStep = 3 (ImmersiveRoleDialogue) ← 新增          │
│  ├─ assessmentId: 关联的评估记录 ID                     │
│  ├─ @complete 事件:                                     │
│  │  ├─ scores: 多角色评分                               │
│  │  ├─ messages: 对话消息                               │
│  │  ├─ duration: 持续时间                               │
│  │  └─ patterns: 行为模式                               │
│  ├─ 合并 scores 到 allScores                            │
│  ↓ handleNext()                                         │
│  activeStep = 4 (CognitiveTask)                         │
│  ↓ handleNext()                                         │
│  activeStep = 5 (PersonalityScale)                      │
│  ↓ handleNext()                                         │
│  activeStep = 6 (ReportGenerate)                        │
│  └─ 显示整个评估的综合结果                              │
└─────────────────────────────────────────────────────────┘
```

---

## 关键修改点

### 1. AssessmentView.vue

**修改步骤数**:
```vue
<el-step title="基本信息"></el-step>           <!-- 1 -->
<el-step title="情境问答"></el-step>           <!-- 2 -->
<el-step title="多角色对话"></el-step>         <!-- 3 新增 -->
<el-step title="认知任务"></el-step>           <!-- 4 -->
<el-step title="特质量表"></el-step>           <!-- 5 -->
<el-step title="生成报告"></el-step>           <!-- 6 -->
```

**添加动态显示逻辑**:
```typescript
const activeStep = ref(1)
const scores = ref({
  situational: {},   // 情景问答的评分
  immersive: {},     // 多角色对话的评分
  cognitive: {},     // 认知任务的评分
  personality: {}    // 特质量表的评分
})

// 合并所有评分用于最终报告
const allScores = computed(() => ({
  ...scores.value.situational,
  ...scores.value.immersive,
  ...scores.value.cognitive,
  ...scores.value.personality
}))
```

### 2. ImmersiveRoleDialogue.vue

**修改 props**:
```typescript
const props = defineProps<{
  candidateId: string
  targetPosition?: string
  assessmentId?: number  // 新增：关联到这个评估记录
  initialContext?: any   // 新增：从前面的步骤继承上下文
}>()
```

**修改 emits**:
```typescript
const emit = defineEmits<{
  (e: 'complete', data: {
    scores: Record<string, number>
    patterns: any[]
    messages: any[]
    duration: number
  }): void
  (e: 'update-scores', scores: Record<string, number>): void
  (e: 'save', data: any): void  // 新增：保存进度
}>()
```

---

## 实施优先级

🔴 **立即** (影响后续所有工作):
1. 修改 AssessmentView 增加 Step 3
2. 导入 ImmersiveRoleDialogue 组件

🟠 **跟进** (确保数据流):
3. 设计数据结构和 API 接口
4. 修改 ImmersiveRoleDialogue 为受控组件

🟡 **优化** (增强体验):
5. 后端 API 实现
6. 错误处理和重试机制

---

## 预期收益

✅ 用户从基础信息 → 情景问答 → 多角色对话，逐步深入评估  
✅ 数据完整采集和累积  
✅ 综合报告包含多维度评分  
✅ 系统展示多模态评估能力

