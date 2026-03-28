# 候选人ID登录流程修复指南

## 🎯 问题诊断

用户反映：`【parsedCandidateId】无法获取有效的 candidateId，returning null`

**根本原因**：
```
登录流程 → 候选人ID路由器到页面流:

❌ 错误流程:
1. 登录: userStore 保存 user_id 到 localStorage 键 'user_id'
2. AssessmentView: 查找 localStorage 键 'candidateId' ❌ 不存在
3. 结果: candidateId = 'demo-001' (演示值)
4. ImmersiveRoleDialogue: 接收 'demo-001'
5. parsedCandidateId: parseInt('demo-001') = NaN ❌

✅ 修复后流程:
1. 登录: userStore 保存 user_id 到 'user_id'
2. AssessmentView: 从 userStore.userId 直接读取 ✅
3. 结果: candidateId = 实际的用户 ID 数字
4. ImmersiveRoleDialogue: 接收有效的数字
5. parsedCandidateId: parseInt('123') = 123 ✅
```

---

## 📝 修复内容

### 文件1: AssessmentView.vue (L230-280)

**修改**：添加 `useUserStore` 导入并改进 `candidateId` computed 逻辑

```typescript
// 新增导入
import { useUserStore } from '@/stores/user'

// 改进的 candidateId computed - 4层级防御
const candidateId = computed(() => {
  // 第1层：路由参数
  const routeId = route.params.id
  if (routeId && routeId !== 'demo') {
    return String(routeId)
  }
  
  // 第2层：userStore.userId（登录后最可靠的来源）✅
  if (userStore.userId) {
    console.log('使用 userStore.userId:', userStore.userId)
    return userStore.userId
  }
  
  // 第3层：localStorage 中的 user_id
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId && storedUserId !== 'null' && !isNaN(Number(storedUserId))) {
    return storedUserId
  }
  
  // 第4层：演示值
  return 'demo-001'
})
```

### 文件2: ImmersiveRoleDialogue.vue (L726-754)

**改进**：提高 `parsedCandidateId` 的有效性检查和日志清晰度

---

## 🧪 验证步骤 (5分钟)

### 前置条件
- ✅ 后端运行中 (`python main.py`)
- ✅ 前端运行中 (`npm run dev`)
- ✅ 有测试用户账户

### 步骤1: 清除缓存重启

```powershell
# 终端1: 停止前端
# 按 Ctrl+C

# 清除浏览器缓存 (或关闭再打开)
# 在浏览器DevTools中: Applications → Clear storage

# 重启前端
npm run dev
```

### 步骤2: 打开控制台

在浏览器中：
```
F12 或 右键 → 检查 → 控制台选项卡
```

### 步骤3: 登录

```
用户名: candidate1
密码: 123456
```

### 步骤4: 查看登录日志

**预期日志**：
```
✅ 登录成功！
【userStore】login 被调用
【userStore】candidateId computed 被触发
【AssessmentView】candidateId 计算开始
【AssessmentView】第2层 - 使用 userStore.userId: 2  ✅
```

### 步骤5: 导航到评估

点击 "开始评估" 或直接访问 `/assessment`

### 步骤6: 检查关键日志

**预期看到**（在控制台）：

```
✅【AssessmentView】第2层 - 使用 userStore.userId: 2
✅【ImmersiveRoleDialogue】第1步 - candidateId: 2
✅【parsedCandidateId】✅ 使用 props 中的值: 2
✅【JobRequirementsManager】props.candidateId: {value: 2, type: 'number', isValid: true}
```

**不应该看到**：
```
❌【parsedCandidateId】无法获取有效的 candidateId，returning null
❌ NaN
❌【AssessmentView】无法获取真实 candidateId，使用演示值
```

### 步骤7: 测试应聘流程

1. 进入 "多角色对话" 步骤
2. 选择一个岗位
3. 点击 "确认应聘"
4. **预期**：
   - 应该收到 200 状态码
   - 不应该看到 NaN 错误
   - 应该看到成功消息

---

## 📊 数据流验证

### 完整的数据流现在应该是：

```
登录页面 (LoginView.vue)
  ↓
userStore.login(data)  ← 保存 user_id
  ↓
localStorage['user_id'] ← 持久化保存
  ↓
导航到 /assessment
  ↓
AssessmentView
  ├─ candidateId computed
  │  ├─ 查看 route.params.id ❌ (无)
  │  ├─ 查看 userStore.userId ✅ (2)
  │  └─ 返回 "2"
  │
  ├─ props :candidate-id="2"
  │
  └─ ImmersiveRoleDialogue
     ├─ parsedCandidateId computed
     │  ├─ parseInt("2") = 2 ✅
     │  └─ 传递给 JobRequirementsManager
     │
     └─ JobRequirementsManager
        └─ props.candidateId = 2 ✅
```

---

## ❌ 故障排除

### 情况1：仍然看到 "无法获取有效的 candidateId"

**原因**：可能没有保存修复后的文件或浏览器缓存

**解决**：
```bash
# 1. 清除构建缓存
rm -r node_modules/.vite

# 2. 硬刷新浏览器
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# 3. 检查文件修改是否保存
# 编辑器中查看 AssessmentView.vue 第240-280 行
```

### 情况2：登录后 userStore.userId 仍为空

**原因**：后端登录接口没有返回 user_id

**检查**：
```bash
# 在后端 Python 终端中测试
python -c "
import requests
resp = requests.post('http://127.0.0.1:8000/auth/login', 
  data={'username': 'candidate1', 'password': '123456'})
import json
print(json.dumps(resp.json(), indent=2))
"

# 查看响应中是否有 'user_id' 字段
```

### 情况3：localStorage 中有 'user_id' 但 userStore.userId 仍为空

**原因**：可能是店铺没有正确初始化

**解决**：在浏览器控制台中：
```javascript
// 检查 userStore 状态
import { useUserStore } from '/src/stores/user'
const userStore = useUserStore()
console.log('userId:', userStore.userId)
console.log('token:', userStore.token)
```

---

## 📱 通过真实数据验证完整流程

### 测试场景

**场景**：从登录到岗位应聘的完整流程

1. **登录测试**
   - 用户名: `candidate1`
   - 密码: `123456`
   - 预期: localStorage 中有 `user_id: 2`

2. **评估页面测试**
   - 导航到 `/assessment`
   - 预期: 控制台显示 `userStore.userId: 2`

3. **岗位应聘测试**
   - 进入多角色对话步骤
   - 选择岗位
   - 点击 "确认应聘"
   - 预期: API 返回 200，candidateId 为 2

---

## ✅ 修复验证清单

- [ ] AssessmentView.vue 导入了 useUserStore
- [ ] AssessmentView.vue 的 candidateId computed 从 userStore 读取
- [ ] 登录后 userStore.userId 不为空
- [ ] 浏览器 localStorage 中有 'user_id'
- [ ] 导航到 /assessment 不显示演示值
- [ ] ImmersiveRoleDialogue 接收到有效的 candidateId
- [ ] parsedCandidateId 不返回 null
- [ ] JobRequirementsManager 的 props.candidateId 是有效的数字
- [ ] 应聘流程可以正常进行

---

## 🔗 相关文件

- [AssessmentView.vue](frontend/src/views/AssessmentView.vue) - L230-280
- [ImmersiveRoleDialogue.vue](frontend/src/views/assessment/ImmersiveRoleDialogue.vue) - L726-754
- [user.ts Store](frontend/src/stores/user.ts) - 登录数据保存
- [LoginView.vue](frontend/src/views/LoginView.vue) - L401-425
