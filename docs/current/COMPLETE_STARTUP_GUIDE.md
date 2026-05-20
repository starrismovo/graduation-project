# 应聘流程修复 - 完整启动指南

## 📋 修复内容摘要

| 问题 | 原因 | 修复 |
|------|------|------|
| 422 错误 | candidate_id 为 NaN | 添加完善的 null/NaN 检查 |
| 401 错误 | API 强制认证 | ✅ 已在之前修复 |
| 500 错误 | 序列化问题 | ✅ 已在之前修复 |

---

## 🚀 快速启动

### 步骤 1: 启动后端服务器

```bash
cd d:\Desktop\graduation-project
python backend/main.py
```

**预期输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 步骤 2: 在新终端启动前端

```bash
cd d:\Desktop\graduation-project\frontend
npm run dev
```

**预期输出**：
```
vite v... dev server running at:
  ➜  Local:   http://localhost:5173/
```

### 步骤 3: 打开浏览器

访问 `http://localhost:5173`

---

## 📝 完整测试流程

### 阶段 1: 登录/注册
```
[ ] 打开首页
[ ] 登录或注册候选人账户
[ ] 确保能成功登录
```

### 阶段 2: 简历上传 (Step 0-1)
```
[ ] 进入评估页面
[ ] 上传或填写简历
[ ] 填写基本信息
[ ] 点击"确认"进入下一步
[ ] 应该看到 Step 1 完成标记
```

### 阶段 3: 岗位选择 (Step 2)
```
[ ] 应该自动进入 Step 2 (岗位选择)
[ ] 看到可用的岗位列表
[ ] 点击一个岗位查看详情
[ ] 看到岗位要求、技能、人格框架等
```

### 阶段 4: 应聘 (关键步骤)
```
[ ] 在岗位详情中看到"确认应聘"按钮
[ ] 打开浏览器 DevTools (F12)
[ ] 转到 Network 标签
[ ] 点击"确认应聘"
[ ] 观察网络请求：
    - 应该看到 POST /jobs/apply 请求
    - 状态码应该是 200 OK （而不是 422）
[ ] 看到成功提示信息
[ ] UI 自动进入 Step 3
```

### 阶段 5: 面试阶段 (Step 3+)
```
[ ] 应该看到面试说明
[ ] 点击"开始面试"
[ ] 进入 Step 4 (多轮对话)
[ ] 与 AI 对话进行多轮面试
```

---

## 🔍 故障排查

### 问题 1: 点击应聘后仍然看到 422 错误

**检查清单**：
1. [ ] 确认已修改的代码已保存
2. [ ] 确认前端已重新启动 npm
3. [ ] 打开 DevTools，查看 Network 标签的请求数据
4. [ ] 查看 Console 标签是否有错误

**如果仍然失败**：
```javascript
// 在浏览器控制台执行
console.log('localStorage candidateId:', localStorage.getItem('candidateId'))
console.log('props candidateId:', ???) // 无法从控制台访问
```

### 问题 2: 点击应聘后没有任何反应

**检查清单**：
1. [ ] 打开浏览器 Console，看是否有 JS 错误
2. [ ] 查看网络请求是否发送
3. [ ] 如果没有发送请求，说明前端代码阻止了它（这是好的，说明修复生效了）
4. [ ] 检查是否显示了错误提示："无法获取候选人ID，请重新登录"

### 问题 3: 按钮加载中，但长时间无响应

**检查清单**：
1. [ ] 查看后端是否收到请求（后端日志）
2. [ ] 查看网络请求的响应时间
3. [ ] 如果超过 30 秒，可能是超时（检查 request.ts 的超时设置）

---

## 🧪 高级诊断

### 生成详细日志

**修改 JobRequirementsManager.vue 中的 handleApplyForJob**：

```typescript
const handleApplyForJob = async () => {
  console.log('🔵 [handleApplyForJob START]')
  
  if (!selectedJob.value) {
    console.log('❌ selectedJob is empty')
    return
  }

  applying.value = true
  try {
    // 获取候选人 ID，支持多种方式
    let candidateId = props.candidateId
    console.log('🔵 [1] props.candidateId:', candidateId)
    
    if (!candidateId) {
      const storedId = localStorage.getItem('candidateId')
      console.log('🔵 [2] localStorage candidateId:', storedId)
      candidateId = storedId ? parseInt(storedId) : null
      console.log('🔵 [3] after parseInt:', candidateId, 'isNaN?', isNaN(candidateId))
    }
    
    // 验证 candidateId
    if (!candidateId || isNaN(candidateId)) {
      console.log('❌ [4] candidateId invalid, returning')
      ElMessage.error('无法获取候选人ID，请重新登录')
      applying.value = false
      return
    }
    
    console.log('✅ [5] candidateId valid:', candidateId)
    
    const payload = {
      candidate_id: candidateId,
      job_id: selectedJob.value.id,
    }
    console.log('🔵 [6] Sending payload:', payload)
    
    const response = await applyForJob(payload)
    console.log('🔵 [7] Response received:', response)
    
    if (response.data?.code === 200 || response.status === 200) {
      console.log('✅ [8] Success')
      ElMessage.success('应聘成功！')
      
      emit('apply-job', {
        jobId: selectedJob.value.id,
        jobName: selectedJob.value.title || selectedJob.value.name,
        candidateId: candidateId,
      })
      
      await loadApplications()
      selectedJob.value = null
    } else {
      console.log('❌ [8] Unexpected status:', response.status)
    }
  } catch (error) {
    console.log('❌ Error caught:', error)
    ElMessage.error('应聘失败：' + error.message)
  } finally {
    applying.value = false
    console.log('🔵 [DONE]')
  }
}
```

然后在浏览器控制台观察输出。

---

## 📊 验证清单

### 后端检查
- [ ] 后端启动成功，监听 http://127.0.0.1:8000
- [ ] GET /jobs/ 返回 200 OK，包含岗位列表
- [ ] POST /jobs/apply 接收有效请求返回 200 OK

### 前端检查
- [ ] 前端启动成功，运行在 http://localhost:5173
- [ ] 所有页面都能加载
- [ ] JobRequirementsManager 组件正确显示

### 集成检查
- [ ] 能够登录/注册候选人
- [ ] 能够上传简历
- [ ] 能够进入岗位选择界面
- [ ] 能够点击应聘并收到成功响应 ✅
- [ ] 能够进入面试阶段

---

## 🎯 成功标志

### 第一步成功
```
[INFO] 127.0.0.1:59999 - "POST /jobs/apply HTTP/1.1" 200 OK
(而不是 422 Unprocessable Entity)
```

### 第二步成功
```
在浏览器中看到：
✅ "应聘成功！" 消息提示
✅ UI 自动切换到 Step 3 (面试说明)
```

### 第三步成功
```
✅ 能够开始多轮面试对话
✅ 系统继续正常运行直到步骤完成
```

---

## 💾 快速恢复

如果需要重置数据：

```bash
cd d:\Desktop\graduation-project\backend

# 清除所有应聘记录
python -c "
from database import SessionLocal
from models import CandidateJobApplication
db = SessionLocal()
db.query(CandidateJobApplication).delete()
db.commit()
print('Cleaned up all applications')
"

# 重新启动后端
python main.py
```

---

## 📞 支持

如果遇到其他问题：

1. 查看 [FIX_422_ERROR.md](./FIX_422_ERROR.md) 了解修复详情
2. 查看 [FRONTEND_TROUBLESHOOTING.md](./FRONTEND_TROUBLESHOOTING.md) 了解前端调试
3. 查看 [JOB_APPLICATION_FLOW_FIX.md](./JOB_APPLICATION_FLOW_FIX.md) 了解应聘流程修复

---

**最后更新**: 2026-03-28

**状态**: ✅ 修复完成，准备好进行完整测试
