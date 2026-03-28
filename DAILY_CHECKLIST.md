# ✅ 立即行动检查清单

**目标**: 本周内完成 Task 1.1 - Task 1.3  
**预期结果**: 系统去除 Mock 数据，完全可用

---

## 🚀 今天就可以开始的工作

### ✅ Task 1.1: 简历上传 UI (预估 2-3 小时)

```typescript
// 第一步: 创建新的上传组件
// 文件: frontend/src/components/ResearchResumeUpload.vue
// 内容: 见 NEXT_STEPS_IMPLEMENTATION_PLAN.md 中的代码块
```

**检查清单**:
- [ ] 创建 `ResearchResumeUpload.vue` 文件
- [ ] 拷贝组件代码
- [ ] 导入到 `BasicInfo.vue`
- [ ] 在浏览器测试 (F12 看是否有错误)
- [ ] 测试文件上传 → 检查后端日志

**快速验证**:
```bash
# 后端是否正确返回解析结果
curl -X POST http://localhost:8000/api/candidates/upload_resume \
  -F "file=@test_resume.pdf"

# 应该返回:
# {
#   "name": "...",
#   "email": "...",
#   "phone": "...",
#   "resume_url": "/uploads/xxx.pdf"
# }
```

---

### ✅ Task 1.2: LLM 集成 (预估 2-3 小时)

```bash
# 第一步: 准备 API Key
# 选择一个 (优先级顺序):
# 1. OpenAI (最容易集成)
#    - 访问 https://platform.openai.com/api-keys
#    - 创建 API Key
#    - 复制 Key

# 2. Claude (Anthropic)
#    - 访问 https://console.anthropic.com/
#    - 创建 API Key

# 3. 本地模型 (如果 GPU 足够)
#    - 使用 Ollama 或 GPT4All
```

**检查清单**:
- [ ] 获取 LLM API Key
- [ ] 编辑 `backend/.env`，添加 Key
- [ ] 创建 `backend/services/llm_client.py`
- [ ] 修改 `backend/services/immersive_dialogue.py`
- [ ] 运行测试: `pytest backend/tests/test_llm_integration.py`
- [ ] 在浏览器测试完整评估流程

**快速调试**:
```python
# 在 Python 中测试 LLM 是否连接正常
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"

import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

---

### ✅ Task 1.3: 表单验证 (预估 1-2 小时)

```typescript
// 在 frontend/src/views/assessment/BasicInfo.vue 中添加
// 代码见上面的参考实现

const validateBasicInfo = () => {
  // 检查所有必填字段
  // 返回错误列表或 true
}

const handleNext = async () => {
  const validation = validateBasicInfo()
  if (validation !== true) {
    ElMessage.error(validation.join('；'))
    return
  }
  // 继续
}
```

**检查清单**:
- [ ] 为每个评估步骤添加验证函数
- [ ] 在提交前调用验证
- [ ] 显示清晰的错误提示
- [ ] 手工测试各种错误情况 (空值、格式错误等)

---

## 📊 实时进度跟踪

| 任务 | 状态 | 完成度 | 预计完成时间 |
|------|------|--------|------------|
| 1.1 简历上传 UI | ⏳ 进行中 | 0% | 今天 × 2h |
| 1.2 LLM 集成 | ⏳ 进行中 | 0% | 明天 × 3h |
| 1.3 表单验证 | ❌ 未开始 | 0% | 明后 × 1h |
| **本周小计** | | | **6-7 小时** |
| 2.1 集成测试 | ❌ 未开始 | 0% | 周五 × 2h |
| 2.2 数据库优化 | ❌ 未开始 | 0% | 周末 × 1h |
| 2.3 前端优化 | ❌ 未开始 | 0% | 周末 × 1h |

---

## 🔧 快速问题排除

### 问题 1: 前端修改后不显示更新

**解决方案**:
```bash
# 清除浏览器缓存
# 前端: Ctrl + Shift + R (硬刷新)

# 或清除 npm 缓存
npm cache clean --force
npm run dev  # 重启开发服务器
```

### 问题 2: LLM API 返回 401 (认证失败)

**解决方案**:
```bash
# 检查 API Key 是否正确
echo $OPENAI_API_KEY  # 应该看到 sk-xxx

# 检查 .env 文件是否正确格式
# 应该是:
# OPENAI_API_KEY=sk-xxx
# 不应该有引号或空格
```

### 问题 3: 上传文件后没有反应

**解决方案**:
```bash
# 检查后端日志
# 确认 POST /upload_resume 被调用

# 检查文件大小 (应 < 10MB)
ls -lh resume.pdf

# 检查文件格式 (应是 PDF/DOC 等)
file resume.pdf
```

### 问题 4: 数据库连接失败

**解决方案**:
```bash
# 确认 MySQL 正在运行
mysql -u root -p -e "SELECT 1"

# 检查 .env 中的数据库连接字符串
# 应该是: DATABASE_URL=mysql://user:pwd@localhost/db_name
```

---

## 📱 前端测试清单

**完整流程测试** (10 分钟):

1. **注册页面**
   - [ ] 填写用户名、密码
   - [ ] 点击"注册"
   - [ ] 重定向到登录页

2. **登录页面**
   - [ ] 用刚注册的账号登录
   - [ ] 重定向到首页

3. **首页**
   - [ ] 显示候选人信息
   - [ ] "开始评估"按钮可点击
   - [ ] "我的评估"页签显示评估历史 (初始为空)

4. **基本信息步骤**
   - [ ] 可填写/编辑所有表单字段
   - [ ] 简历上传区域显示
   - [ ] 上传文件后自动识别
   - [ ] 可编辑识别的字段
   - [ ] "下一步"按钮有效

5. **AI 对话步骤**
   - [ ] 显示问题 (来自 LLM，不是硬编码)
   - [ ] 可输入回答
   - [ ] 点击发送后显示下一个问题
   - [ ] 对话历史显示正确

6. **其他步骤** (快速验证)
   - [ ] 认知任务: 可完成
   - [ ] 人格评估: 可选择
   - [ ] 最终报告: 可生成和查看

---

## 🐍 后端测试清单

**API 测试** (使用 curl 或 Postman):

```bash
# 1. 认证
POST /auth/register
POST /auth/login

# 2. 候选人信息
GET /api/candidates/me
PUT /api/candidates/me

# 3. 简历上传
POST /api/candidates/upload_resume

# 4. 启动评估
POST /api/assessments/start
GET /api/assessments/{id}

# 5. 对话系统
POST /api/assessments/{id}/get-questions
POST /api/assessments/{id}/analyze-answer

# 6. 报告
GET /api/assessments/{id}/reports
```

**数据库检查** (使用 MySQL):

```sql
-- 检查数据是否正确存储
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM assessments;
SELECT COUNT(*) FROM conversation_turns;
SELECT * FROM conversation_turns LIMIT 5;

-- 检查关键字段
SELECT id, assessment_id, speaker, message, emotion, confidence_score 
FROM conversation_turns 
WHERE assessment_id = 'test_id'
LIMIT 5;
```

---

## 🎯 每日目标

### 今天 (Day 1)
- [ ] Task 1.1 开始: 创建简历上传组件
- [ ] Task 1.2 开始: 准备 LLM API Key
- [ ] 预期进度: 30-40%

### 明天 (Day 2)
- [ ] Task 1.1 完成: 简历上传功能可用
- [ ] Task 1.2 进行中: LLM 集成 50%
- [ ] 预期进度: 60-70%

### 后天 (Day 3)
- [ ] Task 1.2 完成: LLM 集成可用
- [ ] Task 1.3 完成: 表单验证完善
- [ ] Task 2.1 开始: 集成测试
- [ ] 预期进度: 90-95%

### 周末
- [ ] Task 2.1 完成: 所有功能验证通过
- [ ] Task 2.2/2.3: 性能优化
- [ ] 预期进度: 98-100%

---

## 🚨 高优先级 Bug 修复

**当前已知的需修复项**:
- [ ] 简历上传 UI 组件还不够优美，需要用 Element UI 增强
- [ ] LLM 返回的对话有时格式混乱，需要 JSON 解析验证
- [ ] 对话记录有时缺少时间戳，需要在前端补充

**每次修改后必做**:
1. 前端浏览器硬刷新 (Ctrl+Shift+R)
2. 后端日志查看是否有错误
3. 数据库查询验证数据完整性
4. 提交一条测试数据，追踪完整流程

---

## 📞 获取帮助

**遇到问题时**:

1. **查看已有文档**:
   - `BACKEND_COMPLETION_REPORT.md` - 后端API完整说明
   - `FRONTEND_INTEGRATION_COMPLETE.md` - 前端集成现状
   - `API_REFERENCE.md` - API 参数详解

2. **查看后端日志**:
   ```bash
   # 在启动后端时查看实时日志
   cd backend
   python main.py
   # 任何 API 错误都会显示在终端
   ```

3. **查看浏览器控制台**:
   ```bash
   # F12 打开开发者工具
   # 查看 Network 标签 - 如果 API 调用失败会显示红色
   # 查看 Console 标签 - JavaScript 错误会显示
   ```

4. **查看数据库**:
   ```bash
   # 确保数据确实被存储了
   mysql -u root -p
   USE graduation_project;
   SELECT * FROM assessment_records ORDER BY created_at DESC LIMIT 1;
   ```

---

## 🎉 完成标志

**当以下条件全部满足，表示本周工程完成**:

1. ✅ 简历上传功能完全可用 (UI + 数据存储)
2. ✅ LLM 集成完成 (所有 API 返回真实数据，无 Mock)
3. ✅ 完整评估流程可跑通 (注册 → 评估 → 报告)
4. ✅ 数据完整性验证通过 (所有数据正确存储)
5. ✅ 性能达到可接受水平 (无明显卡顿)
6. ✅ 没有 JavaScript 错误 (浏览器 Console 清爽)
7. ✅ 所有 API 返回状态码 200 (无 500 错误)

**当以上全部完成，系统已可上线**。

---

*最后更新: 2026-03-28*  
*使用此清单追踪每日进度*
