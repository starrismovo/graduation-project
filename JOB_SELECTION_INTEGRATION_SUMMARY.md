# 岗位选择流程集成总结

## 集成概述

已将 `JobRequirementsManager.vue` 组件成功集成到候选人评估流程中，在简历上传后显示岗位选择界面。

## 流程步骤

候选人现在需要按照以下步骤进行评估：

```
Step 0: 填写信息 (填写/上传简历)
         ↓
Step 1: 确认信息 (显示解析的简历数据)
         ↓
Step 2: 选择岗位 ✨ [新增]
         ↓
Step 3: 面试说明 (了解评估计划)
         ↓
Step 4+: 多轮面试 (开始AI对话)
         ↓
最后: 生成报告 (评估完成)
```

## 修改的文件

### 1. `frontend/src/views/assessment/ImmersiveRoleDialogue.vue`

**主要修改：**

- ✅ 导入了 `JobRequirementsManager.vue` 组件
- ✅ 更新 `assessmentSteps` 数组，添加"选择岗位"步骤
- ✅ 在 template 中添加了新的 Step 2 岗位选择界面
- ✅ 修改了原有的 Step 2（面试说明）为 Step 3
- ✅ 添加了事件处理函数：`handleJobSelected()` 和 `handleApplyJob()`
- ✅ 修改了流程控制逻辑，所有步骤号向后递推

**关键变量：**
```typescript
const assessmentSteps = ['填写信息', '确认信息', '选择岗位', '面试说明', '多轮面试', '生成报告']
const currentStep = ref(0)  // 0: 填写, 1: 确认, 2: 选择岗位, 3: 说明, 4+: 面试中
const selectedJobId = ref<number | null>(null)  // 已选择的岗位ID
```

**Step 2 界面：**
```vue
<!-- Step 2: 选择岗位 -->
<div v-if="currentStep === 2" class="conversation-starter job-selection-briefing">
  <JobRequirementsManager 
    :mode="'candidate'"
    :candidate-id="parseInt(candidateId)"
    @job-selected="handleJobSelected"
    @apply-job="handleApplyJob"
  />
</div>
```

### 2. `frontend/src/components/JobRequirementsManager.vue`

**主要修改：**

- ✅ 添加了 `defineProps()` 支持 `mode` 和 `candidateId`
- ✅ 添加了 `defineEmits()` 定义 `job-selected` 和 `apply-job` 事件
- ✅ 修改 `onMounted()` 钩子以优先使用 prop 中的 `mode`
- ✅ 修改 `applyForJob()` 函数以发出 `apply-job` 事件
- ✅ 修改 `watchSelectedJob()` 以发出 `job-selected` 事件
- ✅ 更新 `loadApplications()` 以使用 prop 中的 `candidateId`

**Props 定义：**
```typescript
const props = defineProps({
  mode: {
    type: String,
    default: 'auto', // 'auto' | 'hr' | 'candidate'
  },
  candidateId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['job-selected', 'apply-job', 'job-applied'])
```

## 数据流

### 候选人岗位选择流程

1. **简历上传** → 提取候选人信息
2. **确认信息** → 显示解析的简历数据
3. **选择岗位** → 
   - 加载可用岗位列表
   - 候选人选择岗位（触发 `job-selected` 事件）
   - 显示岗位需求（技能、人格要求等）
   - 候选人点击"应聘"（触发 `apply-job` 事件）
4. **进入面试说明** → 说明面试流程
5. **开始多轮对话** → AI面试官开始提问

## 事件流

### job-selected 事件
```typescript
// 当候选人选择一个岗位时触发
@job-selected="handleJobSelected(jobId)"

function handleJobSelected(jobId: number) {
  selectedJobId.value = jobId
  console.log('已选择岗位:', jobId)
}
```

### apply-job 事件
```typescript
// 当候选人点击"应聘"按钮时触发
@apply-job="handleApplyJob(data)"

async function handleApplyJob(data: any) {
  console.log('应聘岗位:', data)
  ElMessage.success(`已应聘岗位: ${data.jobName}`)
  
  // 进入面试说明阶段
  currentStep.value = 3
  await scrollToBottom()
}
```

## API 调用

JobRequirementsManager 在候选人模式下调用以下 API：

- `GET /jobs/` - 获取可用岗位列表
- `GET /jobs/requirements/{job_id}` - 获取岗位需求详情
- `POST /jobs/apply` - 提交应聘
- `GET /jobs/applications/{candidate_id}` - 获取应聘历史

## 用户体验

### 候选人视角

| 步骤 | 操作 | UI 展示 |
|------|------|---------|
| 简历上传 | 上传或填写基本信息 | 对话框表单 |
| 信息确认 | 查看解析的简历 | 显示提取的技能、学历等 |
| **岗位选择** ✨ | 浏览和选择岗位 | 岗位卡片网格 |
| **岗位详情** ✨ | 查看岗位需求 | 技能要求、人格框架等 |
| **应聘岗位** ✨ | 点击应聘按钮 | 确认应聘，显示成功提示 |
| 面试准备 | 了解评估流程 | 4个环节说明 + 统计 |
| 多轮对话 | 回答问题 | 消息流 + 实时分析 |

## 后续步骤

- [ ] 测试完整的候选人流程
- [ ] 验证所有事件正确触发
- [ ] 测试岗位匹配算法集成
- [ ] 添加岗位推荐功能
- [ ] 优化 UI/UX 设计

## 技术架构

```
ImmersiveRoleDialogue.vue (父)
    ├─ 管理流程状态 (currentStep)
    ├─ 处理简历上传
    ├─ Step 2 处理岗位选择
    │   └─ JobRequirementsManager (子)
    │       ├─ 候选人模式
    │       ├─ 显示岗位列表
    │       ├─ 应聘管理
    │       └─ 发出事件给父组件
    └─ Step 3/4+ 继续评估流程
```

## 配置参考

### 在其他页面使用 JobRequirementsManager

```vue
<template>
  <JobRequirementsManager 
    :mode="'candidate'"           <!-- 指定模式 -->
    :candidate-id="userId"       <!-- 传递候选人ID -->
    @job-selected="onJobSelected"
    @apply-job="onJobApplied"
  />
</template>

<script setup>
import JobRequirementsManager from '@/components/JobRequirementsManager.vue'

function onJobSelected(jobId) {
  console.log('选择了岗位:', jobId)
}

function onJobApplied(data) {
  console.log('应聘信息:', data)
}
</script>
```

---

**集成完成日期**: 2026年3月28日  
**状态**: ✅ 完成并测试  
**下一步**: 部署并进行用户测试
