# 🏗️ 集成后的系统架构详解

**文档类型**: 架构说明  
**同步日期**: 2026-02-25  
**版本**: v2.0 (集成 ImmersiveRoleDialogue 后)

---

## 整体架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                    毕业设计系统整体架构                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─ 前端应用 (Vue 3 + TypeScript) ──────────────────────────┐    │
│  │                                                          │    │
│  │  ┌─ AssessmentView (主流程管理) ────────────────────┐   │    │
│  │  │                                                 │   │    │
│  │  │  Step 1: BasicInfo (基础信息)                  │   │    │
│  │  │            ↓                                    │   │    │
│  │  │  Step 2: SituationalQA (情景问答)              │   │    │
│  │  │            ↓                                    │   │    │
│  │  │  Step 3: ImmersiveRoleDialogue ✨ (新增)       │   │    │
│  │  │            ↓                                    │   │    │
│  │  │  Step 4: CognitiveTask (认知任务)              │   │    │
│  │  │            ↓                                    │   │    │
│  │  │  Step 5: PersonalityScale (特质量表)           │   │    │
│  │  │            ↓                                    │   │    │
│  │  │  Step 6: ReportGenerate (报告生成)             │   │    │
│  │  │                                                 │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                          │    │
│  │  ┌─ ImmersiveRoleDialogue (多角色对话) ──────────────┐  │    │
│  │  │                                                   │  │    │
│  │  │  ├─ 角色系统                                     │  │    │
│  │  │  │  ├─ HR 经理                                   │  │    │
│  │  │  │  ├─ 技术总监                                 │  │    │
│  │  │  │  ├─ 产品经理                                 │  │    │
│  │  │  │  └─ CTO                                       │  │    │
│  │  │  │                                                │  │    │
│  │  │  ├─ 对话引擎                                     │  │    │
│  │  │  │  ├─ 消息流处理                               │  │    │
│  │  │  │  ├─ LLM 分析 (Mock → 待替换)                 │  │    │
│  │  │  │  └─ 实时评分                                 │  │    │
│  │  │  │                                                │  │    │
│  │  │  └─ 数据同步                                     │  │    │
│  │  │     ├─ @complete 事件                           │  │    │
│  │  │     ├─ @update-scores 事件                      │  │    │
│  │  │     └─ completionData 结构                      │  │    │
│  │  │                                                   │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─ API 调用层 (utils/request.ts) ──────────────────────────┐    │
│  │                                                          │    │
│  │  情景问答 API:                                          │    │
│  │  ├─ GET /api/interview/scenarios                       │    │
│  │  ├─ POST /api/interview/save-response                  │    │
│  │  └─ POST /api/interview/score-answer                   │    │
│  │                                                          │    │
│  │  多角色对话 API: (待实现)                              │    │
│  │  ├─ POST /api/assessment/                              │    │
│  │  ├─ POST /api/assessment/{id}/analyze-dialogue         │    │
│  │  ├─ POST /api/assessment/{id}/next-question            │    │
│  │  └─ POST /api/assessment/{id}/save-response            │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              后端服务 (FastAPI + SQLAlchemy)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─ 路由层 ─────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ✅ routers/auth.py (认证)                              │   │
│  │  ✅ routers/job.py (岗位管理)                           │   │
│  │  ✅ routers/candidate.py (候选人)                       │   │
│  │  ✅ routers/interview.py (面试)                         │   │
│  │  ✅ routers/hr_agent.py (情景问答) HR-Agent ✅         │   │
│  │  ⏳ routers/assessment.py (评估) ← 待实现              │   │
│  │  ⏳ routers/interviewer.py (面试官) ← 待实现            │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─ 数据模型层 ─────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ✅ models/user.py (用户)                               │   │
│  │  ✅ models/job.py (岗位)                                │   │
│  │  ✅ models/interview.py (面试)                          │   │
│  │  ✅ models/candidate.py (候选人)                        │   │
│  │  ✅ models/hr_agent.py (情景、回答、评分) HR-Agent     │   │
│  │  ✅ models/assessment.py (评估记录) ← 已定义             │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─ LLM 集成层 ──────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ✅ prompts/hr_agent_llm.py (情景评分)                  │   │
│  │  ⏳ prompts/assessment_llm.py (对话分析) ← 待实现       │   │
│  │     ├─ 多角色身份模拟                                  │   │
│  │     ├─ 智能追问生成                                    │   │
│  │     └─ 综合评分逻辑                                    │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─ 数据库 (SQLite/PostgreSQL) ──────────────────────────────┐   │
│  │                                                          │   │
│  │  users → interviews → interview_responses              │   │
│  │  candidates                                             │   │
│  │  jobs                                                   │   │
│  │  scenarios → [responses, scores] (HR-Agent)             │   │
│  │  assessment_records → dialogue_history (新增)           │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 数据流详解

### 单个评估周期的完整数据流

```
用户操作          前端状态变化         后端处理                数据库更新
──────────────────────────────────────────────────────────────────────

1️⃣ 输入基础信息
   BasicInfo     candidate 填充    [无后端调用]         [暂不保存]
   点击 Next ──→ activeStep = 1
   

2️⃣ 情景问答评估
   SituationalQA ──→ answers[] ──→ POST /api/interview/save-response
                  │               │  
   emit          latestScores     返回: scores, reasoning
                 + reasoning      │
                                  ✓ scenarios 表记录
                                  ✓ responses 表记录
                                  ✓ scores 计算

3️⃣ 多角色对话 ✨ 新增
   ImmersiveRoleDialogue ──→ messages[] ──→ POST /api/assessment/analyze
                           │              │ (待实现)
   emit 'complete'        immersiveScores 返回: scores, patterns
                           + patterns    │
                           + metadata    ✓ assessment_records 记录
                                        ✓ dialogue_history 保存
                                        ✓ trait_scores 更新

4️⃣ 认知任务（使用前面的评分上下文）
   CognitiveTask  ← hr-scores (immersiveScores 优先)
                  ├─ 参考多角色对话的评分维度
                  └─ 深入考察特定能力

5️⃣ 特质量表
   PersonalityScale ──→ personalityScores ──→ POST /api/interview/scale
                                              ✓ personality_traits 保存

6️⃣ 报告生成
   ReportGenerate ← allScores (合并)
   │
   allScores = {
     ...情景问答评分,
     ...多角色对话评分,  ← 新增的维度
     ...特质量表评分
   }
   ├─ 展示综合评分 (多维度)
   ├─ 对标分析
   └─ 改进建议
```

---

## 组件交互序列

```
┌─────────────┐
│Assessment   │  Step 2          Step 3              Step 4
│View         │  ──────────────────────────────────────────
│(父)         │
└─────────────┘
      │
      ├──→ SituationalQA
      │    ├─ @update-answers
      │    │   └─ handleAnswersUpdate()
      │    │       └─ latestScores 更新
      │    │
      │    └─ @next
      │        └─ handleNext()
      │            └─ activeStep = 2
      │
      ├──→ ImmersiveRoleDialogue ✨ (新增)
      │    ├─ Props:
      │    │  ├─ candidateId: string
      │    │  ├─ targetPosition: string
      │    │  ├─ initialContext: candidate
      │    │  └─ assessmentId?: number
      │    │
      │    ├─ @update-scores
      │    │   └─ handleImmersiveScores()
      │    │       └─ immersiveScores 更新 (实时)
      │    │
      │    ├─ @complete
      │    │   └─ handleImmersiveComplete(data)
      │    │       ├─ immersiveData 保存
      │    │       ├─ immersiveScores 合并
      │    │       └─ ElMessage.success()
      │    │
      │    └─ emit 时携带的数据:
      │        {
      │          sessionId: string
      │          messages: Message[]
      │          scores: Record<string, number>
      │          patterns: Pattern[]
      │          duration: number
      │          conversationDepth: number
      │          candidateId: string
      │          totalRounds: number
      │          highlights: string[]
      │        }
      │
      ├──→ CognitiveTask
      │    ├─ Props: hr-scores
      │    │   (优先使用 immersiveScores 如果有)
      │    │
      │    └─ @next
      │
      ├──→ PersonalityScale
      │    ├─ @save
      │    │   └─ personalityScores 更新
      │    │
      │    └─ @next
      │
      └──→ ReportGenerate
           ├─ Props:
           │  ├─ candidate: 用户信息
           │  └─ personalityScores: allScores (合并)
           │      {
           │        ...latestScores (情景),
           │        ...immersiveScores (对话),
           │        ...personalityScores (特质)
           │      }
           │
           └─ @finish
```

---

## 状态管理（Reactive）

### AssessmentView 的状态树

```typescript
{
  // 基本信息
  candidate: {
    id,
    name,
    age,
    education,
    major,
    desired_job,
    experience_years,
    skills
  },

  // 流程控制
  activeStep: number,           // 1-6
  showImmersiveMode: boolean,   // true 则显示 Step 3

  // 步骤 2: 情景问答
  currentScenario: {
    title,
    description,
    target_traits,
    max_rounds
  },
  answers: Array<{
    text: string
    time: string
    latency: number
    emotion: string
    scores?: Record<string, number>
    reasoning?: Record<string, string>
  }>,
  latestScores: Record<string, number>,    // 情景评分
  latestReasonings: Record<string, string>,
  
  // 步骤 3: 多角色对话 ✨ 新增
  immersiveData: {                         // 完整对话数据
    sessionId,
    messages,
    duration,
    ...
  },
  immersiveScores: Record<string, number>, // 对话评分

  // 步骤 5: 特质量表
  personalityScores: Record<string, number>,

  // 计算属性
  allScores: computed(() => ({             // 合并所有评分
    ...latestScores,
    ...immersiveScores,
    ...personalityScores
  }))
}
```

---

## 关键修改点对比

| 方面 | 修改前 | 修改后 |
|------|--------|--------|
| **步骤数** | 5 步 | 6 步 |
| **评估模式** | 单模式 | 多模态 |
| **组件导入** | 5 个 | 6 个 |
| **评分来源** | 2 个 | 3 个 + 合并逻辑 |
| **数据流** | 线性 | 树形（汇聚） |
| **Props** | 简单 | 包含 context |
| **Emits** | 基础 | 多事件 |
| **报告数据** | personalityScores | allScores |

---

## 代码修改位置速查表

### 前端修改

```
AssessmentView.vue
├─ 第 7-13 行: <el-step> 增加多角色对话
├─ 第 19-26 行: task-header 条件判断更新
├─ 第 220-240 行: 导入 ImmersiveRoleDialogue
├─ 第 280-295 行: 组件渲染逻辑增强
├─ 第 247-260 行: 数据状态增加
├─ 第 288-300 行: 事件处理函数新增
└─ 第 500-510 行: CSS 样式新增

ImmersiveRoleDialogue.vue
├─ 第 370-380 行: Props 定义更新
├─ 第 382-392 行: Emits 定义增加
├─ 第 750-800 行: completeAssessment() 修改
└─ 第 850-890 行: generateReport() 修改
```

---

## 后续扩展点

```
当前状态 (✅ 完成)
└─ 前端集成完成，可构建和测试

下个阶段 (⏳ 待做)
├─ Phase 2.1: 后端 Assessment API
│  └─ 实现 CRUD 操作、数据持久化
│
├─ Phase 2.2: 替换 Mock 为真实 API
│  └─ analyzeResponse, generateNextQuestion 等
│
├─ Phase 2.3: 增强报告
│  └─ ReportGenerate 显示多维度分析
│
└─ Phase 2.4: 优化体验
   ├─ 错误处理和重试
   ├─ 自动保存进度
   ├─ 性能优化
   └─ 响应式完善
```

---

## 性能思考

### 当前复杂度分析

```
引入 ImmersiveRoleDialogue 前:
- 组件数: 5 个
- Props 层次: 3 层
- 事件链: 6 个
- 状态复杂度: O(n)

引入后:
- 组件数: 6 个 (+20%)
- Props 层次: 3 层 (无增加)
- 事件链: 8 个 (+33%)
- 状态复杂度: O(n) + merge logic
- 可能的性能降低: <5% (接受范围)
```

### 优化建议

```
立即优化:
□ 虚拟滚动处理大量消息
□ 图表懒加载
□ API 请求去重

后期优化:
□ 状态分层管理 (Pinia store)
□ 本地缓存策略
□ 网络请求拦截和重试
```

---

## 部署架构

```
本地开发:
Frontend (http://localhost:5173)
    ↓
Backend (http://127.0.0.1:8000)
    ↓
Database (SQLite: graduation-project.db)

生产环境（建议）:
Frontend (静态 CDN / Nginx)
    ↓
Backend API Gateway (Docker / K8s)
    ├─ hr_agent 服务
    ├─ assessment 服务  ← 新增
    └─ auth 服务
    ↓
PostgreSQL (生产数据库，替换 SQLite)
    ↓
LLM API (OpenAI / ChatGPT / DeepSeek)
```

---

## 总结

经过这次集成，系统从"**多步骤评估**"升级为"**多模态沉浸式评估**"：

| 维度 | 提升 |
|------|------|
| **评估维度** | 增加从单一情景到多角色多维度 |
| **用户体验** | 从问卷式到对话式 |
| **数据质量** | 从离散答案到连续对话 |
| **技术复杂度** | 从静态流程到动态交互 |
| **商业价值** | 从基础评估到深度评估 |

这为硕士毕业设计提供了坚实的技术基础和完整的使用场景！🎓

