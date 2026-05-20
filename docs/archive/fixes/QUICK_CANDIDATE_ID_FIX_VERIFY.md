# 快速验证：登录后候选人ID获取修复

## 问题
用户登录后，`candidateId` 无法正确获取，导致后续流程中 `candidateId===null`。

## 根本原因
- AssessmentView.vue 的 `candidateId` computed 从 localStorage 查找 `'candidateId'` 键
- 但 userStore 实际上保存的是 `'user_id'` 键
- 结果总是返回演示值 `'demo-001'`

## 修复
修改 AssessmentView.vue L230-280，让它从 `useUserStore` 直接读取 `userId`

---

## ⚡ 快速验证 (3 分钟)

### 步骤1: 清理 & 重启
```bash
# 清理浏览器缓存或开隐私模式
# 浏览器中按 Ctrl+Shift+R 硬刷新

# 重启前端（如果需要）
# 终端: Ctrl+C 停止
# 然后: npm run dev
```

### 步骤2: 打开开发工具
按 `F12` 打开浏览器控制台，进入 "Console" 选项卡

### 步骤3: 登录
```
用户名: candidate1
密码: 123456
```

### 步骤4: 查看控制台输出

**✅ 正确的输出应该包含**：
```
【userStore】login 被调用
【AssessmentView】第2层 - 使用 userStore.userId: 2
```

**❌ 错误的输出会包含**：
```
【AssessmentView】无法获取真实 candidateId，使用演示值
```

### 步骤5: 导航到评估页面

点击"开始评估"或在地址栏访问 `http://localhost:5173/assessment`

### 步骤6: 检查关键日志

**✅ 正确的日志**：
```
【AssessmentView】candidateId 计算开始
【AssessmentView】第2层 - 使用 userStore.userId: 2
【ImmersiveRoleDialogue】parsedCandidateId】✅ 使用 props 中的值: 2
【JobRequirementsManager】props.candidateId: {value: 2, type: 'number', isValid: true}
```

**❌ 错误的日志**：
```
【parsedCandidateId】无法获取有效的 candidateId，returning null
NaN
```

### 步骤7: 测试应聘操作

1. 进入 "多角色对话" 步骤
2. 选择一个岗位
3. 点击 "确认应聘"

**✅ 预期结果**：
- 控制台无 NaN 错误
- 应该看到 "应聘成功" 消息或岗位详情

**❌ 失败表现**：
- 控制台显示 NaN
- 收到 422 或 500 错误

---

## 📊 数据流示意

```
登录 (candidate1)
  ↓
userStore 保存 userId = 2
  ↓
localStorage['user_id'] = '2'
  ↓
进入 /assessment
  ↓
AssessmentView.candidateId computed
  ├─ 从 userStore.userId 读取 ✅ (修复点)
  └─ 返回 "2"
  ↓
ImmersiveRoleDialogue :candidate-id="2"
  ├─ parsedCandidateId = parseInt("2") = 2 ✅
  └─ 传递给 JobRequirementsManager
  ↓
JobRequirementsManager
  ├─ props.candidateId = 2 ✅
  └─ 可以正常应聘
```

---

## 🛠️ 修改确认

验证以下文件已修改：

1. **AssessmentView.vue**
   - [ ] 第4行：导入了 `import { useUserStore } from '@/stores/user'`
   - [ ] 第246行：`const userStore = useUserStore()`
   - [ ] 第250-260行：第2层从 `userStore.userId` 读取

2. **ImmersiveRoleDialogue.vue**
   - [ ] L745行：改进了 localStorage 查找逻辑（查找 'user_id' 而不是 'candidateId'）

---

## 📞 仍有问题？

如果修复后仍然看到错误：

1. **检查 AssessmentView.vue 是否保存**
   - 编辑器中查看第4行和第246行是否有更改

2. **浏览器完全刷新**
   ```
   Ctrl + Shift + Del  # 打开清除浏览数据
   选择 "所有时间"，勾选 "缓存"、"存储数据"
   点击清除
   ```

3. **测试后端登录接口**
   ```bash
   curl -X POST http://127.0.0.1:8000/auth/login \
     -d "username=candidate1&password=123456"
   
   # 检查响应中是否有 "user_id" 字段
   ```

4. **查看 userStore 真实状态**
   在浏览器控制台运行：
   ```javascript
   localStorage.getItem('user_id')  // 应该返回 '2' 或其他数字
   ```
