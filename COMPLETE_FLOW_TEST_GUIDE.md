# 🔄 完整流程测试指南（修复版）

## ✅ 正确的流程

```
1️⃣ 首页（HomeView）
   ↓ 点 "开始新评估" 按钮
   
2️⃣ 沉浸式对话（/immersive）
   ├─ ImmersiveRoleDialogue.vue 独立页面
   ├─ 自动获取 userStore.userId 作为 candidateId
   └─ 与 4 个角色对话
   ↓ 对话完成 → 点 "生成完整报告"
   
3️⃣ 保存数据
   ├─ POST /assessment/save
   ├─ 后端创建 AssessmentRecord
   ├─ 后端更新 CandidatePersonalityProfile
   └─ 返回 success
   ↓ 成功后返回首页
   
4️⃣ 首页刷新数据
   ├─ watch 检测路由变化
   ├─ loadData() 重新加载
   ├─ fetchPortrait(candidateId) → 获取心理画像
   ├─ fetchHistory(candidateId) → 获取历史记录
   └─ fetchJobs(candidateId) → 获取推荐岗位
   ↓
   
5️⃣ 首页显示结果
   ├─ ✅ 心理画像（五大特质雷达图）
   ├─ ✅ 历史评估记录（包含刚才的评估）
   └─ ✅ 岗位推荐（基于心理画像）
```

---

## 🧪 分步测试

### 前置条件

```bash
# 1️⃣ 启动后端
cd backend
python main.py
# 检查：http://127.0.0.1:8000/docs 可访问

# 2️⃣ 启动前端
cd frontend
npm run dev
# 访问：http://localhost:5173/home
```

### 测试步骤

#### 第 1 步：首页加载

```
✓ 打开 http://localhost:5173/home
✓ 看到欢迎栏："欢迎，[用户名]"
✓ 看到"开始新评估"按钮
✓ 如果是新用户，看到欢迎对话框
```

#### 第 2 步：进入对话

```
✓ 点击"开始新评估"
✓ 路由跳转到 /immersive
✓ 看到 4 个角色卡片（HR、技术总监、产品经理、CTO）
✓ 看到聊天输入框
```

#### 第 3 步：完成对话

```
✓ 输入几条消息（例如："你好，我叫张三"）
✓ 点击"发送回答"
✓ 看到角色回复
✓ 重复几次
✓ 当对话足够长时，看到"完成评估"按钮
```

#### 第 4 步：保存数据

```
✓ 点击"完成评估"
✓ 看到完成对话框，显示：
  - 交互轮次：N 次
  - 总用时：X 分 Y 秒
  - 亮点总结
✓ 点击"生成完整报告"
```

#### 第 5 步：验证后端保存

```
浏览器控制台应该看到：
"✅ 评估数据已保存到后端"

如果看到以下任一消息，说明成功：
- "✅ 评估数据已保存到后端"
- "⚠️ 后端保存失败，使用本地存储"（降级模式）
- "保存失败但继续返回首页"（降级模式）
```

#### 第 6 步：返回首页

```
✓ 自动跳转回 http://localhost:5173/home
✓ 看到成功提示："评估已完成，心理画像已生成！"
```

#### 第 7 步：验证首页数据

```
✓ 首页应该显示：

【我的心理画像】
├─ 雷达图（五大特质）
│  ├─ 外向性：8.5/10
│  ├─ 宜人性：7.2/10
│  ├─ 尽责性：8.0/10
│  ├─ 神经质：3.5/10（低分为好）
│  └─ 开放性：7.8/10
└─ 文字总结：
   ├─ 优势：...
   └─ 改进空间：...

【历史评估记录】
├─ 时间：今天
├─ 岗位：评估候选人
├─ 匹配度：65-85%
└─ [查看详情]

【推荐岗位】
├─ 岗位 1：匹配度 XX%
├─ 岗位 2：匹配度 XX%
└─ 岗位 3：匹配度 XX%
```

---

## 🐛 常见问题排查

### 问题 1：返回首页后仍然没有图表

**排查步骤**:

```javascript
// 浏览器控制台
1. 检查用户 ID
console.log(localStorage.getItem('user_id'))

2. 检查本地存储的评估数据
const candidateId = localStorage.getItem('user_id')
console.log(localStorage.getItem(`assessment_${candidateId}`))

3. 检查 API 返回数据
fetch('http://127.0.0.1:8000/assessment/portrait/YOUR_USER_ID')
  .then(r => r.json())
  .then(d => console.log(d))

4. 检查数据库中的评估记录
# 在后端终端执行
python
from database import SessionLocal
from models.assessment import AssessmentRecord
db = SessionLocal()
records = db.query(AssessmentRecord).all()
for r in records:
    print(f"{r.candidate_id}: {r.job_title} - {r.match_score}")
```

### 问题 2：保存失败，只有本地存储

**这是正常的降级行为**:

```
当后端不可用时，系统会：
✓ 警告用户
✓ 使用本地存储保存数据
✓ 仍然返回首页
✓ 显示本地存储中的数据（如果有的话）
```

### 问题 3：首页加载很慢

**可能原因**:

```
1. 后端响应慢 → 检查数据库
2. 网络延迟 → 检查网络连接
3. API 超时 → request.ts 中已设置 30 秒超时

解决方案：
- 检查后端是否在运行
- 检查数据库是否有大量记录
- 查看浏览器控制台是否有错误
```

---

## 📊 数据流验证清单

在完整测试前，验证以下内容：

- [ ] 用户已登录（localStorage 有 user_token 和 user_id）
- [ ] 后端 API `/assessment/save` 可访问（Swagger 页面）
- [ ] 数据库连接正常（后端启动无错误）
- [ ] 前端能够访问 /immersive 页面
- [ ] 首页能够加载（不报错）

---

## 🎯 成功标志

当看到以下任一情况，说明流程正常：

✅ **快速路径**：完成对话 → 自动返回首页 → 显示心理画像  
✅ **降级路径**：数据保存到本地存储 → 返回首页 → 显示本地数据  
✅ **部分加载**：首页显示部分数据（心理画像或历史记录其中之一）  

❌ **失败标志**：
- 长时间停留在加载页面
- 返回首页后仍然是空白
- 浏览器控制台有明显的 JavaScript 错误
- API 返回 HTTP 500+ 错误

---

## 🔧 快速修复

如果出现问题，按以下顺序尝试：

```bash
# 1️⃣ 重启后端
cd backend
python main.py

# 2️⃣ 清除浏览器缓存
# 打开开发者工具 → 存储 → 清除所有

# 3️⃣ 重启前端
cd frontend
npm run dev

# 4️⃣ 检查数据库
# 通过 SQLite 浏览器打开 backend/assessment.db

# 5️⃣ 查看日志
# 后端终端应该有详细的请求日志
```

---

## 📝 日志检查点

### 前端（浏览器控制台）

```
✓ "✅ 评估数据已保存到后端"  → 成功
✗ "⚠️ 后端保存失败"          → 降级模式或网络问题
✗ 任何 CORS 或网络错误       → 跨域或连接问题
```

### 后端（终端输出）

```
✓ "POST /assessment/save" 请求被接收
✓ "评估结果已保存" 响应返回
✓ "200 OK" 状态码
✗ "500 Internal Server Error"  → 数据库或业务逻辑错误
```

---

**测试时间**: 预期 5-10 分钟  
**成功率**: 应该达到 95% 以上（除非有网络问题）

