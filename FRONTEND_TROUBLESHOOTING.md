# 前端应聘流程 - 检查清单

## 🔍 问题诊断

如果岗位选择后无法进入应聘环节，请按以下步骤检查：

---

## 检查点 1: 事件监听

**文件**: `frontend/src/views/assessment/ImmersiveRoleDialogue.vue`

**需要检查的代码**:
```vue
<!-- Step 2: 选择岗位 -->
<div v-if="currentStep === 2" class="conversation-starter job-selection-briefing">
  <JobRequirementsManager
    mode="'candidate'"
    :candidateId="currentUserId"
    @job-selected="handleJobSelected"
    @apply-job="handleApplyJob"
  />
</div>
```

**检查清单**:
- [ ] `@apply-job` 事件监听是否存在？
- [ ] 事件名称是否与子组件发出的事件匹配？
- [ ] `handleApplyJob` 处理函数是否被调用？

**测试方法**:
```javascript
// 在浏览器控制台中添加日志
// 编辑 ImmersiveRoleDialogue.vue
async function handleApplyJob(data: any) {
  console.log('======== handleApplyJob 被调用！', data);  // ← 添加这行
  ElMessage.success(`已应聘岗位: ${data.jobName}`)
  currentStep.value = 3
  await scrollToBottom()
}
```

---

## 检查点 2: 子组件事件发出

**文件**: `frontend/src/components/JobRequirementsManager.vue`

**需要检查的代码**:
```typescript
const handleApplyForJob = async () => {
  if (!selectedJob.value) return

  applying.value = true
  try {
    const candidateId = props.candidateId || parseInt(localStorage.getItem('candidateId'))
    const response = await applyForJob({
      candidate_id: candidateId,
      job_id: selectedJob.value.id,
    })

    if (response.data?.code === 200 || response.status === 200) {
      ElMessage.success('应聘成功！')
      
      // 发出事件
      emit('apply-job', {
        jobId: selectedJob.value.id,
        jobName: selectedJob.value.title || selectedJob.value.name,
        candidateId: candidateId,
      })
      
      await loadApplications()
      selectedJob.value = null
    }
  } catch (error) {
    ElMessage.error('应聘失败：' + error.message)
  } finally {
    applying.value = false
  }
}
```

**检查清单**:
- [ ] API 调用状态是否为 200？
- [ ] 是否执行了 `emit('apply-job', ...)`？
- [ ] 传递的数据是否正确？

**测试方法**:
```typescript
// 在浏览器控制台测试
// 打开浏览器 DevTools (F12)
// 在控制台输入以下命令查看是否有错误
console.log('检查是否有网络错误')
```

---

## 检查点 3: API 响应格式

**期望的响应格式**:
```json
{
  "status": 200,
  "data": {
    "id": 2,
    "candidate_id": 1,
    "job_id": 1,
    "application_status": "applied",
    "personality_match_score": null,
    "applied_at": "2026-03-28T..."
  }
}
```

**测试 API**:
```bash
# 1. 打开浏览器控制台
# 2. 执行下面的命令
fetch('http://localhost:8000/jobs/apply', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    candidate_id: 1,
    job_id: 1,
    notes: 'test'
  })
}).then(r => r.json()).then(console.log)
```

**检查清单**:
- [ ] 返回状态码 200？
- [ ] 返回的数据包含 `id` 字段（应聘记录 ID）？
- [ ] 是否有错误消息？

---

## 检查点 4: 状态更新

**验证 `currentStep` 是否更新**:

```vue
<!-- 在父组件中添加监视器 -->
<script setup>
watch(currentStep, (newVal) => {
  console.log('currentStep changed to:', newVal)  // 应该看到 3
})
</script>
```

**检查清单**:
- [ ] 点击应聘后，`currentStep` 是否从 2 变为 3？
- [ ] UI 是否显示面试说明（Step 3）？

---

## 常见问题排查

### ❌ 问题: 点击应聘后没有任何反应

**检查**:
1. 打开浏览器控制台 (`F12`)
2. 查看是否有 JavaScript 错误
3. 检查网络标签，看 `/jobs/apply` 请求的状态码
   - 200 → 检查事件监听
   - 401 → ✅ 后端已修复
   - 400/404 → 检查请求数据
   - 500 → ✅ 后端已修复

### ❌ 问题: "应聘成功" 消息显示，但没有进入 Step 3

**检查**:
```javascript
// 在 handleApplyJob 中添加日志
async function handleApplyJob(data: any) {
  console.log('1. handleApplyJob 开始执行', data)
  
  ElMessage.success(`已应聘岗位: ${data.jobName}`)
  
  console.log('2. 当前 currentStep:', currentStep.value)
  currentStep.value = 3
  console.log('3. 设置后 currentStep:', currentStep.value)
  
  await scrollToBottom()
  console.log('4. 完成')
}
```

如果日志显示 `currentStep` 没有变化，可能是：
- `currentStep` ref 定义有问题
- 使用了 `.value` 但应该直接赋值
- 父组件页面没有正确刷新

### ❌ 问题: API 返回 401 错误

**检查**: ✅ 这个问题已在后端修复
- 确保后端代码已更新
- 重启后端: `Ctrl+C` 然后 `python backend/main.py`

---

## 调试模式启用

### 在 JobRequirementsManager.vue 中启用日志

```typescript
const handleApplyForJob = async () => {
  console.log('🔵 [handleApplyForJob] 开始')
  console.log('   - selectedJob:', selectedJob.value)
  
  if (!selectedJob.value) {
    console.log('❌ [handleApplyForJob] selectedJob 为空')
    return
  }

  applying.value = true
  try {
    const candidateId = props.candidateId || parseInt(localStorage.getItem('candidateId'))
    console.log('🔵 [handleApplyForJob] 候选人ID:', candidateId)
    
    const payload = {
      candidate_id: candidateId,
      job_id: selectedJob.value.id,
    }
    console.log('🔵 [handleApplyForJob] 请求数据:', payload)
    
    const response = await applyForJob(payload)
    console.log('🔵 [handleApplyForJob] 响应:', response)

    if (response.data?.code === 200 || response.status === 200) {
      console.log('✅ [handleApplyForJob] 应聘成功')
      
      ElMessage.success('应聘成功！')
      
      const eventData = {
        jobId: selectedJob.value.id,
        jobName: selectedJob.value.name,
        candidateId: candidateId,
      }
      console.log('🔵 [handleApplyForJob] 发出事件:', eventData)
      emit('apply-job', eventData)
      
      await loadApplications()
      selectedJob.value = null
    } else {
      console.log('❌ [handleApplyForJob] 响应状态不正确:', response.status)
    }
  } catch (error) {
    console.log('❌ [handleApplyForJob] 错误:', error)
    ElMessage.error('应聘失败：' + error.message)
  } finally {
    applying.value = false
  }
}
```

在父组件 ImmersiveRoleDialogue.vue 中也添加日志：

```typescript
async function handleApplyJob(data: any) {
  console.log('🟢 [handleApplyJob] 父组件收到事件:', data)
  
  ElMessage.success(`已应聘岗位: ${data.jobName}`)
  
  console.log('🟢 [handleApplyJob] 更新 currentStep: 2 → 3')
  currentStep.value = 3
  
  await scrollToBottom()
  
  console.log('🟢 [handleApplyJob] 完成，当前 Step:', currentStep.value)
}
```

然后在浏览器控制台观察日志输出：
```
🔵 [handleApplyForJob] 开始
   - selectedJob: {id: 1, name: "后端工程师"}
🔵 [handleApplyForJob] 候选人ID: 1
🔵 [handleApplyForJob] 请求数据: {candidate_id: 1, job_id: 1}
🔵 [handleApplyForJob] 响应: {...}
✅ [handleApplyForJob] 应聘成功
🔵 [handleApplyForJob] 发出事件: {...}
🟢 [handleApplyJob] 父组件收到事件: {...}
🟢 [handleApplyJob] 更新 currentStep: 2 → 3
```

如果看不到 `🟢` 的日志，说明事件没有被正确接收。

---

## 验证步骤

### 最终测试
1. ✅ 启动后端服务
2. ✅ 启动前端服务
3. 打开浏览器: http://localhost:5173
4. 登录或注册候选人账户
5. **上传简历** (Step 0-1)
6. **进入岗位选择** (Step 2)
   - 应该看到可用的岗位列表
   - 点击一个岗位查看详情
7. **点击"确认应聘"按钮**
   - 打开浏览器控制台 (F12)
   - 查看网络请求和日志
8. **验证进入 Step 3**
   - 应该看到"面试说明"
   - UI 应该切换到下一个步骤

---

## 快速诊断命令

在浏览器控制台执行：

```javascript
// 检查 API 可用性
fetch('http://localhost:8000/jobs/')
  .then(r => r.json())
  .then(jobs => console.log('Jobs:', jobs))
  .catch(e => console.log('Error connecting to API:', e))

// 测试应聘 API
fetch('http://localhost:8000/jobs/apply', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({candidate_id: 1, job_id: 1})
})
  .then(r => r.json())
  .then(res => console.log('Apply result:', res))
  .catch(e => console.log('Apply error:', e))
```

---

## 后续支持

如果按照以上步骤检查后仍有问题，请提供：
1. 浏览器控制台的完整错误消息
2. 网络请求的状态码和响应内容
3. 前端日志输出

这样可以更精准地定位问题。
