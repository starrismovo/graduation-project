# 422 错误修复总结

## 🔴 问题诊断

后端返回 `POST /jobs/apply HTTP/1.1" 422 Unprocessable Entity` 错误。

### 根本原因

前端发送的 `candidate_id` 为 `NaN` 或 `null`，导致 Pydantic 验证失败。

**问题代码**（JobRequirementsManager.vue 第 460 行）：
```typescript
const candidateId = props.candidateId || parseInt(localStorage.getItem('candidateId'))
```

**问题分析**：
- 如果 `props.candidateId` 为 `undefined` 或 `""`（空字符串）
- 且 `localStorage.getItem('candidateId')` 返回 `null`
- 那么 `parseInt(null)` 会返回 `NaN`
- 发送给后端的请求包含 `"candidate_id": NaN`
- 后端 Pydantic 验证失败 → 422 错误

---

## ✅ 修复内容

### 修改 1: JobRequirementsManager.vue - handleApplyForJob 函数

**前**：
```typescript
const candidateId = props.candidateId || parseInt(localStorage.getItem('candidateId'))
const response = await applyForJob({
  candidate_id: candidateId,
  job_id: selectedJob.value.id,
})
```

**后**：
```typescript
// 获取候选人 ID，支持多种方式
let candidateId = props.candidateId
if (!candidateId) {
  const storedId = localStorage.getItem('candidateId')
  candidateId = storedId ? parseInt(storedId) : null
}

// 验证 candidateId
if (!candidateId || isNaN(candidateId)) {
  ElMessage.error('无法获取候选人ID，请重新登录')
  applying.value = false
  return
}

const response = await applyForJob({
  candidate_id: candidateId,
  job_id: selectedJob.value.id,
})
```

### 修改 2: JobRequirementsManager.vue - loadApplications 函数

**前**：
```typescript
const candidateId = props.candidateId || parseInt(localStorage.getItem('candidateId'))
const response = await getCandidateApplications(candidateId)
```

**后**：
```typescript
// 获取候选人 ID，支持多种方式
let candidateId = props.candidateId
if (!candidateId) {
  const storedId = localStorage.getItem('candidateId')
  candidateId = storedId ? parseInt(storedId) : null
}

if (!candidateId || isNaN(candidateId)) {
  console.warn('无法获取候选人ID，跳过加载应聘记录')
  return
}

const response = await getCandidateApplications(candidateId)
```

---

## 🧪 诊断结果

### 422 错误触发条件

| 请求数据 | candidate_id 值 | 状态码 | 说明 |
|---------|-----------------|--------|------|
| 有效请求 | `1` (数字) | 400 | 业务逻辑错误：已申请过 |
| 无效请求 | `null` | 422 | ❌ Pydantic 验证失败 |
| 无效请求 | 缺少字段 | 422 | ❌ Pydantic 验证失败 |
| 无效请求 | `"candidate_123"` (字符串) | 422 | ❌ Pydantic 验证失败 |

---

## 🔧 防御措施

新代码添加了三道防线：

1. **null 检查**：验证 localStorage 值是否存在
2. **类型转换检查**：使用 `parseInt()` 后检查是否为 NaN
3. **提前返回**：如果 ID 无效，立即返回错误消息而不发送请求

---

## 📋 修改的文件

- `frontend/src/components/JobRequirementsManager.vue`
  - 第 455-475 行：修复 handleApplyForJob
  - 第 488-503 行：修复 loadApplications

---

## ✨ 预期修复后的行为

### 正确场景
```
1. 候选人选择岗位
2. 点击"确认应聘"
3. 前端检查 candidateId 有效性 ✓
4. 发送请求到后端（candidate_id 为有效整数）
5. 后端返回 200 OK 或 400（已申请过）
6. 显示成功消息并进入 Step 3
```

### 错误场景
```
1. 候选人进入岗位选择但未登录/login token 丢失
2. candidateId 获取失败（null）
3. 前端检查失败 ❌
4. 显示错误提示："无法获取候选人ID，请重新登录"
5. 请求未发送，避免 422 错误
```

---

## 🚀 测试方法

### 测试 1：正常流程
```bash
1. 启动后端：python backend/main.py
2. 启动前端：npm run dev
3. 登录或注册候选人
4. 上传简历
5. 进入岗位选择
6. 点击应聘
✓ 应该看到成功消息或"已申请过"提示
```

### 测试 2：模拟 localStorage 缺失
```javascript
// 在浏览器控制台
localStorage.removeItem('candidateId')
// 再尝试点击应聘
// 应该看到错误提示："无法获取候选人ID，请重新登录"
```

### 测试 3：检查日志
```javascript
// 打开浏览器 F12
// 查看控制台是否有错误信息
// 查看网络标签，应该看不到 POST /jobs/apply（因为已阻止）
```

---

## 📊 影响范围

- ✅ 修复了 422 error
- ✅ 改进了错误处理
- ✅ 添加了用户友好的错误提示
- ✅ 不影响其他功能

---

**下一步**: 完整端到端测试，确认应聘流程正常运行。
