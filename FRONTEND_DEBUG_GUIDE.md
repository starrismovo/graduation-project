# 前端调试指南 - 应聘流程修复

## 🎯 浏览器内置调试方法

### 方法 1: DevTools Console 快速检查

**步骤**：
1. 打开浏览器 DevTools: `F12` 或 `右键 → 检查`
2. 选择 `Console` 标签
3. 在应聘页面，粘贴以下命令并执行：

```javascript
// 检查 localStorage 中的候选人 ID
const candId = localStorage.getItem('candidateId');
console.log('📌 LocalStorage candidateId:', {
  raw: candId,
  type: typeof candId,
  isNull: candId === null,
  isParsable: !isNaN(parseInt(candId))
});

// 如果 ID 存在，显示完整信息
if (candId) {
  const parsed = parseInt(candId);
  console.log('✅ 成功解析:', {
    original: candId,
    parsed: parsed,
    isNaN: isNaN(parsed)
  });
} else {
  console.error('❌ LocalStorage 中没有 candidateId');
  console.log('💡 需要重新登录');
}
```

### 方法 2: Network 标签监控请求

**步骤**：
1. 打开 DevTools: `F12`
2. 选择 `Network` 标签
3. **勾选** "Preserve logs" 选项（防止页面刷新时清空日志）
4. 在应聘页面点击"确认应聘"按钮
5. 查看网络请求列表中的 `jobs/apply` 请求

**期望结果**：
```
Method: POST
Status: 200 OK      ← ✅ 成功（或 400 如果已申请过）
NOT 422 ❌ 不应该出现 422
```

**查看请求数据**：
1. 点击 `jobs/apply` 请求行
2. 选择 `Request` 标签，查看发送的数据
3. 应该看到：
```json
{
  "candidate_id": 1,    // ← 整数，不是 NaN
  "job_id": 1
}
```

### 方法 3: 响应体检查

**步骤**：
1. 在 Network 标签中找到 `jobs/apply` 请求
2. 选择 `Response` 标签
3. 应该看到成功响应：
```json
{
  "code": 200,
  "message": "Application submitted successfully",
  "data": {
    "id": xxx,
    "candidate_id": 1,
    "job_id": 1,
    "application_date": "2026-03-28T..."
  }
}
```

---

## 🔍 逐步排查流程

### 场景 1: 点击应聘后立即出现红色提示

**诊断**：
```javascript
// 检查是否是我们的防御代码在工作
// 在浏览器控制台查看是否有日志输出
console.log('检查前端验证...');
```

**预期日志**：
```
❌ candidateId invalid, returning
❌ 无法获取候选人ID，请重新登录
```

**修复**：
1. 重新登录（确保 localStorage 有正确的 candidateId）
2. 清除 localStorage 并重新登录：
```javascript
localStorage.clear();
// 然后刷新页面，重新登录
```

### 场景 2: 请求发送到后端但返回 422

**诊断**：
1. 打开 Network 标签
2. 查看 `jobs/apply` 的 `Request` 数据
3. 检查 `candidate_id` 字段：

**如果是 NaN**：
```javascript
// 这是问题！说明前端没有正确验证
// 检查是否是缓存问题
location.reload();  // 硬刷新
```

**如果是 null**：
```javascript
// localStorage 中没有值
// 重新登录
```

**如果是字符串**：
```javascript
// 类型错误，应该是数字
// 检查前端代码是否有 parseInt
```

### 场景 3: 请求发送后长时间没响应

**诊断**：
1. 查看 Network 标签中请求的时间
2. 如果超过 30 秒，检查：
```javascript
// 检查后端是否在运行
fetch('http://127.0.0.1:8000/docs')
  .then(r => console.log('✅ 后端在运行:', r.status))
  .catch(e => console.log('❌ 后端未运行:', e.message));
```

3. 如果后端没运行，重新启动：
```bash
cd d:\Desktop\graduation-project
python backend/main.py
```

---

## 🧪 完整测试脚本

### 脚本 1: 快速验证流程

在 Console 中执行（需要在应聘页面）：

```javascript
// ========== 快速验证脚本 ==========
(async function testJobApplication() {
  console.log('🔵 [开始测试应聘流程]');
  
  // Step 1: 检查 localStorage
  const candId = localStorage.getItem('candidateId');
  console.log('Step 1 - LocalStorage 检查:', {
    value: candId,
    valid: candId && !isNaN(parseInt(candId))
  });
  
  if (!candId || isNaN(parseInt(candId))) {
    console.error('❌ candidateId 无效，测试中止');
    return;
  }
  
  // Step 2: 获取岗位列表
  console.log('Step 2 - 获取岗位列表...');
  try {
    const jobsRes = await fetch('http://127.0.0.1:8000/jobs/');
    const jobsData = await jobsRes.json();
    console.log('✅ 岗位列表:', jobsData);
    
    const jobs = jobsData.data || jobsData;
    if (!Array.isArray(jobs) || jobs.length === 0) {
      console.error('❌ 没有岗位');
      return;
    }
    
    const testJob = jobs[0];
    console.log('使用岗位:', testJob);
    
    // Step 3: 提交应聘
    console.log('Step 3 - 提交应聘请求...');
    const applyRes = await fetch('http://127.0.0.1:8000/jobs/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_id: parseInt(candId),
        job_id: testJob.id
      })
    });
    
    console.log('响应状态码:', applyRes.status);
    const applyData = await applyRes.json();
    console.log('响应数据:', applyData);
    
    if (applyRes.status === 200) {
      console.log('✅ 应聘成功！');
    } else if (applyRes.status === 400) {
      console.log('⚠️  岗位已申请过');
    } else if (applyRes.status === 422) {
      console.error('❌ 422 验证错误 - 修复可能失效');
    } else {
      console.error('❌ 未知错误');
    }
  } catch (e) {
    console.error('❌ 异常:', e);
  }
  
  console.log('🔵 [测试完成]');
})();
```

### 脚本 2: 深层诊断

获取所有相关信息：

```javascript
// ========== 深层诊断脚本 ==========
(async function diagnosticReport() {
  const report = {
    timestamp: new Date().toISOString(),
    localStorage: {
      candidateId: localStorage.getItem('candidateId'),
      all: { ...localStorage }
    },
    backend: {},
    frontend: navigator.userAgent
  };
  
  // 测试后端连接
  try {
    const healthRes = await fetch('http://127.0.0.1:8000/docs');
    report.backend.status = healthRes.status;
    report.backend.running = healthRes.ok;
  } catch (e) {
    report.backend.error = e.message;
    report.backend.running = false;
  }
  
  // 获取岗位列表
  try {
    const jobsRes = await fetch('http://127.0.0.1:8000/jobs/');
    report.backend.jobsStatus = jobsRes.status;
    const jobsData = await jobsRes.json();
    report.backend.jobsCount = Array.isArray(jobsData) ? jobsData.length : 
                               Array.isArray(jobsData.data) ? jobsData.data.length : 0;
  } catch (e) {
    report.backend.jobsError = e.message;
  }
  
  console.log('📋 诊断报告:');
  console.table(report);
  console.log('完整报告:', JSON.stringify(report, null, 2));
  
  // 提供建议
  console.log('\n💡 诊断建议:');
  if (!report.backend.running) {
    console.log('1. ❌ 后端未运行 - 执行: cd d:\\Desktop\\graduation-project && python main.py');
  } else {
    console.log('1. ✅ 后端运行正常');
  }
  
  if (!report.localStorage.candidateId) {
    console.log('2. ❌ candidateId 未设置 - 需要重新登录');
  } else {
    console.log('2. ✅ candidateId 已设置:', report.localStorage.candidateId);
  }
})();
```

---

## 🎨 修改验证代码的临时调试

如果想添加更多日志到前端代码，编辑：
`frontend/src/components/JobRequirementsManager.vue`

在 `handleApplyForJob` 方法中找到这一段：

```typescript
const handleApplyForJob = async () => {
  if (!selectedJob.value) {
    return
  }

  applying.value = true
  try {
    // === 在这里添加调试日志 ===
    console.log('🔵 handleApplyForJob 开始');
    
    let candidateId = props.candidateId
    console.log('Props candidateId:', candidateId);
    
    if (!candidateId) {
      const storedId = localStorage.getItem('candidateId')
      console.log('localStorage.candidateId:', storedId);
      candidateId = storedId ? parseInt(storedId) : null
      console.log('After parseInt:', candidateId, 'isNaN?', isNaN(candidateId));
    }
    
    if (!candidateId || isNaN(candidateId)) {
      console.error('❌ candidateId 无效');
      ElMessage.error('无法获取候选人ID，请重新登录')
      applying.value = false
      return
    }
    
    const payload = {
      candidate_id: candidateId,
      job_id: selectedJob.value.id,
    }
    console.log('📤 发送数据:', payload);
    
    // === 继续返回到原始代码 ===
    const response = await applyForJob(payload)
    console.log('📥 收到响应:', response.status, response.data);
```

保存后，刷新浏览器，再次尝试应聘，查看 Console 输出。

---

## 📊 常见问题快速检查清单

| 症状 | 可能原因 | 快速检查 |
|------|--------|--------|
| 点击无反应 | localStorage 缺少 candidateId | `localStorage.getItem('candidateId')` |
| 422 错误 | candidateId 是 NaN | `parseInt(localStorage.getItem(...))` |
| 422 错误 | job_id 缺失/错误 | 岗位选择是否成功 |
| 401 错误 | 不应该再出现 | 检查是否用最新代码 |
| 500 错误 | 后端异常 | 查看后端日志 |
| 连接超时 | 后端未运行 | 检查 `http://127.0.0.1:8000/docs` |

---

## 🚀 快速重置方法

如果一切都坏了，快速重置：

```bash
# 1. 清除前端 node_modules 并重新安装
cd d:\Desktop\graduation-project\frontend
rm -r node_modules
npm install
npm run dev

# 在新终端:
# 2. 重启后端
cd d:\Desktop\graduation-project
python backend/main.py
```

在浏览器：
```javascript
// 清除所有本地存储
localStorage.clear();
sessionStorage.clear();
// 刷新
location.reload();
```

---

## 📞 更多信息

- 查看 [COMPLETE_STARTUP_GUIDE.md](./COMPLETE_STARTUP_GUIDE.md) 获取启动指南
- 查看 [FIX_422_ERROR.md](./FIX_422_ERROR.md) 了解修复技术细节
- 查看 backend 日志了解服务器端信息

**状态**: 📝 文档已准备，可随时使用
