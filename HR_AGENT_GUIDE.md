# HR-Agent 模块实现完成指南

## ✅ 已完成的功能

### 1. 后端数据库模型
- ✓ `Scenario` - 情景模板表
- ✓ `InterviewResponse` - 回答记录表
- ✓ `TraitScore` - 特质评分表
- ✓ `ScenarioSummary` - 情景总结表

### 2. 后端 API 接口
```
GET  /api/interview/scenarios/{scenario_id}        - 获取单个情景
GET  /api/interview/scenarios                      - 获取所有情景
POST /api/interview/follow-up-question             - 生成追问问题
POST /api/interview/score-answer                   - 评分回答
POST /api/interview/save-response                  - 保存回答记录
GET  /api/interview/scenario-summary/{cid}/{sid}   - 获取情景总结
```

### 3. LLM 集成（支持本地规则和真实 API）
- ✓ HR-Agent LLM 接口（`backend/prompts/hr_agent_llm.py`）
- ✓ 生成追问问题逻辑
- ✓ 对回答进行特质评分逻辑
- ✓ 本地规则引擎（keyword matching）
- ⚠️ 真实 OpenAI API 集成（待配置 API Key）

### 4. 前端组件（SituationalQA）
- ✓ 情景加载和展示
- ✓ 多轮对话管理
- ✓ 回答提交和评分
- ✓ 动态生成追问问题
- ✓ 实时反馈和消息展示

### 5. 数据库初始化
- ✓ 3 个示例情景：
  - 项目延期应对（责任心、宜人性）
  - 团队冲突处理（情绪稳定性、宜人性）
  - 工作量突增应对（责任心、情绪稳定性）

---

## 📊 数据流架构

```
前端 SituationalQA.vue
  ↓ 加载情景
  ↓ GET /api/interview/scenarios/{scenario_id}
  ↓
后端 routers/hr_agent.py
  ↓ 获取 Scenario 模型
  ↓ 返回情景描述和目标特质
  ↓
用户回答
  ↓ POST /api/interview/save-response
  ↓
后端 hrAgent_llm
  ↓ 调用大模型（或本地规则）
  ↓ 评分用户回答
  ↓ POST /api/interview/score-answer
  ↓
后端保存 TraitScore 到数据库
  ↓
生成追问问题
  ↓ POST /api/interview/follow-up-question
  ↓
循环直到达到最大轮次
  ↓
计算平均分
  ↓ GET /api/interview/scenario-summary/{cid}/{sid}
```

---

## 🎯 特质评分规则

### 目前实现（本地规则）
基于关键词匹配的简单评分规则：

**责任心 (Conscientiousness)**
- 关键词：主动、承担责任、尽快、立即
- 高分：8.0（展现了主动承担责任的态度）
- 低分：5.0（对责任的承诺不够明确）

**宜人性 (Agreeableness)**
- 关键词：沟通、协商、合作、倾听
- 高分：8.0（强调了与他人的沟通和协作）
- 低分：5.0（缺乏对团队协作的强调）

**情绪稳定性 (Emotional Stability)**
- 关键词：冷静、分析、有序、计划
- 高分：8.0（表现出了冷静理性的分析能力）
- 低分：5.0（可能在压力下反应仓促）

### 如何升级到真实 LLM
1. 设置 `OPENAI_API_KEY` 环境变量
2. 在 `hr_agent_llm.py` 中实现 `_call_openai()` 和 `_call_openai_scoring()`
3. 调用 OpenAI Chat Completions API

---

## 🚀 测试流程

### 1. 启动后端
```bash
cd backend
# 确保数据库初始化
python init_scenarios.py

# 启动服务
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 启动前端
```bash
cd frontend
npm run dev
```

### 3. 进行评估
1. 访问 http://localhost:5173
2. 进入评估流程
3. 完成基本信息
4. 进入情境问答
5. 选择情景并开始回答
6. 系统自动生成追问
7. 完成所有轮次

### 4. 查看结果
- 后端数据库中保存了所有回答和评分
- 可以通过 `/api/interview/scenario-summary/{cid}/{sid}` 获取最终结果

---

## 📝 核心代码文件

| 文件 | 功能 | 状态 |
|------|------|------|
| `models/hr_agent.py` | 数据库模型 | ✅ 完成 |
| `schemas/hr_agent.py` | 数据 schemas | ✅ 完成 |
| `prompts/hr_agent_llm.py` | LLM 接口 | ✅ 完成 |
| `routers/hr_agent.py` | API 路由 | ✅ 完成 |
| `frontend/src/views/assessment/components/SituationalQA.vue` | 前端组件 | ✅ 完成 |
| `init_scenarios.py` | 初始化脚本 | ✅ 完成 |

---

## 🔧 后续改进方向

1. **更复杂的追问策略**
   - 基于候选人回答的相似度生成更相关的追问
   - 实现递进式的难度提升

2. **更精细的评分模型**
   - 使用向量化方法计算回答与特质的相似度
   - 集成预训练的情感分析模型

3. **实时学习**
   - 收集评估结果反馈
   - 根据反馈调整评分模型

4. **可视化报告**
   - 生成雷达图对比（理想特质 vs 实际评分）
   - 导出 PDF 报告

5. **多语言支持**
   - 支持中文和英文

6. **A/B 测试**
   - 对比不同的追问策略效果

---

## ⚠️ 已知限制

1. **LLM API 成本**
   - 目前使用本地规则，降低成本
   - 真实 API 调用会有费用

2. **Token 限制**
   - 长对话会超出 LLM 的 token 限制
   - 可以实现对话历史截断策略

3. **评分客观性**
   - 规则基础的评分可能不够准确
   - 需要定期与人工评估对标

4. **响应时间**
   - LLM API 调用会增加延迟（1-3秒）
   - 本地规则则秒级响应

---

## 📊 示例数据库查询

### 查看候选人的所有评分
```python
scores = db.query(TraitScore).filter(
    TraitScore.candidate_id == "demo-001",
    TraitScore.scenario_id == "scenario_001"
).all()

for score in scores:
    print(f"{score.trait_name}: {score.score}/10")
    print(f"理由: {score.reasoning}")
```

### 计算平均分
```python
from collections import defaultdict

trait_scores = defaultdict(list)
for score in scores:
    trait_scores[score.trait_name].append(score.score)

for trait, score_list in trait_scores.items():
    avg = sum(score_list) / len(score_list)
    print(f"{trait} 平均分: {avg:.1f}/10")
```

---

## 🎓 学习资源

- [Pydantic 文档](https://docs.pydantic.dev/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [OpenAI API](https://platform.openai.com/docs/)
- [大五人格评估](https://en.wikipedia.org/wiki/Big_Five_personality_traits)
