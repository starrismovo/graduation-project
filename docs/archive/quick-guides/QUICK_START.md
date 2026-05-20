# 🚀 HR-Agent 快速启动指南

## 项目结构总览

```
graduation-project/
├── backend/
│   ├── models/
│   │   ├── candidate.py          ✅ 候选人模型
│   │   ├── hr_agent.py           ✅ HR-Agent 模型（Scenario、InterviewResponse 等）
│   │   ├── interview.py          原有面试模型
│   │   ├── job.py                岗位模型
│   │   └── user.py               用户模型
│   ├── schemas/
│   │   ├── candidate.py          ✅ 候选人 schemas
│   │   └── hr_agent.py           ✅ HR-Agent schemas
│   ├── routers/
│   │   ├── candidate.py          ✅ 候选人路由
│   │   ├── hr_agent.py           ✅ HR-Agent 路由
│   │   ├── auth.py               认证路由
│   │   ├── job.py                岗位路由
│   │   └── interview.py          面试路由
│   ├── prompts/
│   │   └── hr_agent_llm.py       ✅ LLM 集成工具
│   ├── main.py                   ✅ FastAPI 主应用
│   ├── database.py               ✅ 数据库配置（已改进 SQLite 支持）
│   ├── init_scenarios.py         ✅ 初始化示例情景脚本
│   ├── .env                      ✅ 环境配置（已改为 SQLite）
│   └── requirements.txt          依赖列表
├── frontend/
│   ├── src/
│   │   ├── views/assessment/
│   │   │   ├── BasicInfo.vue     ✅ 基本信息（已改进）
│   │   │   ├── AssessmentView.vue ✅ 评估主容器（已连接 candidateId）
│   │   │   └── components/
│   │   │       ├── SituationalQA.vue      ✅ 情境问答（已重写）
│   │   │       ├── CognitiveTask.vue      认知任务
│   │   │       ├── PersonalityScale.vue   特质量表
│   │   │       └── ReportGenerate.vue     报告生成
│   │   ├── api/
│   │   │   └── candidate.ts      ✅ API 接口
│   │   └── utils/
│   │       └── request.ts        HTTP 请求工具
│   └── package.json
└── 文档
    ├── HR_AGENT_GUIDE.md         ✅ 详细实现指南
    ├── BASICINFO_CHECKLIST.md    ✅ BasicInfo 对接清单
    └── START_HERE.md
```

---

## 🎯 快速开始

### 步骤 1：启动后端

```bash
cd backend

# 方式 A：初始化数据库（首次运行）
python init_scenarios.py

# 方式 B：启动 FastAPI 服务
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**期望输出：**
```
Uvicorn running on http://127.0.0.1:8000
```

### 步骤 2：启动前端

```bash
cd frontend
npm run dev
```

**期望输出：**
```
  VITE v4.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### 步骤 3：打开应用

访问 http://localhost:5173，开始评估流程。

---

## 📋 评估流程演示

### 用户看到的界面顺序

```
1️⃣ 首页 (IndexView)
   ↓
2️⃣ 评估入口 (AssessmentView)
   ↓
3️⃣ Step 1: 基本信息 (BasicInfo)
   → 填写：姓名、年龄、学历、期望岗位、技能等
   → 数据保存到 /api/candidates/{candidateId}/basic-info
   ↓
4️⃣ Step 2: 情境问答 (SituationalQA)
   → 选择情景（从后端加载）
   → 阅读情景描述
   → 初始回答 + 最多 2 轮追问
   → 每次回答自动评分
   ↓
5️⃣ Step 3: 认知任务 (CognitiveTask)
   → 记忆测试
   ↓
6️⃣ Step 4: 特质量表 (PersonalityScale)
   → 大五人格量表
   ↓
7️⃣ Step 5: 报告生成 (ReportGenerate)
   → 综合报告展示
   → 可下载 PDF
```

---

## 🔌 核心 API 端点

### 候选人模块
```bash
# 保存基本信息
POST /api/candidates/{candidateId}/basic-info
Body: {
  "name": "张三",
  "age": 28,
  "education": "本科",
  "major": "计算机科学",
  "desired_job": "前端工程师",
  "experience_years": 3,
  "skills": ["JavaScript", "Vue"]
}

# 获取基本信息
GET /api/candidates/{candidateId}/basic-info
```

### HR-Agent 模块
```bash
# 获取情景列表
GET /api/interview/scenarios

# 获取单个情景
GET /api/interview/scenarios/{scenario_id}
Response: {
  "id": "scenario_001",
  "title": "项目延期应对",
  "description": "...",
  "target_traits": ["责任心", "宜人性"],
  "max_rounds": 3
}

# 保存回答
POST /api/interview/save-response
Body: {
  "candidate_id": "demo-001",
  "scenario_id": "scenario_001",
  "round_num": 1,
  "question": "...",
  "answer": "...",
  "answer_latency": 2.5,
  "emotion": "neutral"
}

# 评分回答
POST /api/interview/score-answer
Body: {
  "candidate_id": "demo-001",
  "scenario_id": "scenario_001",
  "response_id": "resp_xxx",
  "target_traits": ["责任心", "宜人性"],
  "answer": "..."
}
Response: {
  "scores": {"责任心": 7.5, "宜人性": 8.0},
  "reasoning": {"责任心": "展现了...", "宜人性": "强调了..."}
}

# 生成追问
POST /api/interview/follow-up-question
Body: {
  "candidate_id": "demo-001",
  "scenario_id": "scenario_001",
  "round_num": 2,
  "previous_answers": [...]
}
Response: {
  "question": "请具体说明你会如何...",
  "reasoning": "深入了解..."
}

# 获取情景总结
GET /api/interview/scenario-summary/{candidate_id}/{scenario_id}
Response: {
  "candidate_id": "demo-001",
  "scenario_id": "scenario_001",
  "trait_averages": {"责任心": 7.5, "宜人性": 8.0},
  "trait_reasonings": {...},
  "summary": "..."
}
```

---

## 🗄️ 数据库表说明

### 关键表

| 表名 | 功能 | 主要字段 |
|------|------|--------|
| `candidates` | 候选人基本信息 | id, name, age, education, skills |
| `scenarios` | 评估情景 | id, title, description, target_traits |
| `interview_responses` | 面试回答记录 | id, candidate_id, scenario_id, question, answer |
| `trait_scores` | 特质评分 | id, response_id, candidate_id, trait_name, score |
| `scenario_summaries` | 情景总结 | candidate_id, scenario_id, trait_name, average_score |

---

## 🎓 特质评分规则

目前实现了基于关键词匹配的评分规则：

```python
# 示例：如何进行评分

答案中包含"主动"、"承担责任"等关键词
  ↓
责任心得分 = 8.0
理由 = "展现了主动承担责任的态度"

答案中包含"沟通"、"协作"等关键词
  ↓
宜人性得分 = 8.0
理由 = "强调了与他人的沟通和协作"
```

---

## 🔧 故障排查

### 1. 后端启动错误：ModuleNotFoundError
**原因：** 缺少依赖  
**解决：**
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
```

### 2. 前端无法连接后端
**原因：** 后端未启动或 CORS 配置问题  
**检查：**
- 确保后端运行在 http://127.0.0.1:8000
- 检查 main.py 中的 CORS 配置

### 3. 数据库文件权限问题
**原因：** SQLite 文件被锁定  
**解决：** 删除 `hr_matching.db`，重新初始化

### 4. 前端提交失败：timeout
**原因：** 后端响应慢或未启动  
**排查：**
```bash
# 在另一个终端测试后端
curl http://127.0.0.1:8000/api/interview/scenarios
```

---

## 📊 数据库查询示例

```python
# 查看所有情景
from database import SessionLocal
from models.hr_agent import Scenario

db = SessionLocal()
scenarios = db.query(Scenario).all()
for s in scenarios:
    print(f"{s.id}: {s.title}")

# 查看候选人的所有评分
from models.hr_agent import TraitScore

scores = db.query(TraitScore).filter(
    TraitScore.candidate_id == "demo-001"
).all()

for score in scores:
    print(f"{score.trait_name}: {score.score}/10")

db.close()
```

---

## 🎯 下一步优化方向

1. **连接真实 LLM**
   - 配置 OpenAI API Key
   - 实现 `_call_openai()` 方法

2. **前端体验改进**
   - 添加加载动画
   - 实现自动滚动到最新消息
   - 添加错误重试机制

3. **后端性能优化**
   - 缓存情景数据
   - 异步处理 LLM 调用
   - 实现评分批量操作

4. **可视化增强**
   - 实现雷达图组件
   - 添加数据图表
   - 生成 PDF 报告

---

## 📞 获取帮助

- 查看 `HR_AGENT_GUIDE.md` - 详细实现细节
- 查看 `BASICINFO_CHECKLIST.md` - BasicInfo 对接说明
- 检查后端日志 - 查看 SQLAlchemy 调试输出
- 使用 http://127.0.0.1:8000/docs - Swagger UI 文档

---

## ✅ 验证清单

- [ ] 后端启动成功，无错误
- [ ] 数据库初始化完成（3 个情景已插入）
- [ ] 前端启动成功
- [ ] 可以访问首页
- [ ] 可以进入评估流程
- [ ] 基本信息可以保存
- [ ] 情景可以加载和显示
- [ ] 可以提交回答
- [ ] 收到评分结果
- [ ] 可以完成整个流程

---

祝你的毕业设计顺利！🎉
