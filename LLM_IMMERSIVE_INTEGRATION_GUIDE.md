% LLM 集成方案 - 沉浸式多轮对话评估系统

# 🚀 沉浸式对话 LLM 集成完整方案

## 📊 架构总览

```
前端（Vue 3 + TypeScript）
    ↓ fetchNextQuestion、analyzeResponse
后端 API 网关
    ↓
LLM 对话引擎
├─ 多角色提示词 (HR、技术总监、产品经理、CTO)
├─ 对话历史管理
├─ 实时评分计算
└─ 模式识别引擎
    ↓
特质评估器
├─ 关键词提取
├─ 分数推导
├─ 模式检测
└─ 岗位匹配
    ↓
数据库持久化
├─ 评估记录
├─ 对话日志
└─ 特质档案
```

---

## 🔧 实现步骤

### 第 1 步：后端依赖安装

```bash
cd backend

# 添加必要 Python 包到 requirements.txt
pip install httpx  # 用于异步 HTTP 调用
pip install python-dotenv  # 环境变量管理

# 更新环境变量 (.env)
# 添加：
# ROAD2ALL_API_KEY=sk-xxxxxx
# ROAD2ALL_MODEL=gpt-4o
# ROAD2ALL_API_BASE=https://api.road2all.tech/v1
```

### 第 2 步：注册后端路由

编辑 `backend/main.py`，添加新的路由：

```python
from routers.immersive_dialogue import router as immersive_router

# 在 app.include_router() 部分添加：
app.include_router(immersive_router)
```

### 第 3 步：更新前端 API 调用

修改 `ImmersiveRoleDialogue.vue` 中的 API 调用部分（已大部分完成，需微调）：

```typescript
// 已有的调用示例（verify）
const response = await fetch(
  'http://127.0.0.1:8000/assessment/immersive/next-question?...',
  {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  }
)
```

### 第 4 步：测试集成

#### 4.1 测试问题生成
```bash
curl -X POST "http://localhost:8000/assessment/immersive/next-question?" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -G \
  -d "candidate_id=1" \
  -d "role_id=hr" \
  -d "conversation_depth=0"
```

#### 4.2 测试响应分析
```bash
curl -X POST "http://localhost:8000/assessment/immersive/analyze-response?" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -G \
  -d "candidate_id=1" \
  -d "current_speaker=hr" \
  -d "candidate_response=我是一个善于沟通的工程师"
```

---

## 🎯 核心功能详解

### 1. 多角色对话系统

每个角色都有独特的：
- **系统提示词** - 定义角色人设和提问风格
- **评估重点** - 关注的特质维度
- **提问策略** - 问题难度和深度递进

#### 角色对应表

| 角色 | 名字 | 重点特质 | 对话深度 |
|------|------|--------|---------|
| HR | 李明 | 沟通、团队、文化 | 2 |
| 技术总监 | 张伟 | 技术深度、问题解决 | 4 |
| 产品经理 | 王芳 | 产品思维、用户洞察 | 6 |
| CTO | 刘强 | 战略思维、领导力 | 10 |

### 2. 特质评估系统

#### 2.1 特质维度（10 个）

```
核心特质:
✓ 沟通能力 - 清晰表达、逻辑清晰
✓ 问题解决 - 分析能力、方案设计
✓ 技术深度 - 专业知识、深度思考
✓ 团队协作 - 配合意识、沟通反馈
✓ 创新能力 - 新想法、打破常规

高层特质:
✓ 学习能力 - 快速掌握、自我反思
✓ 领导力 - 决策力、影响力
✓ 战略思维 - 眼光远、全局观
✓ 用户洞察 - 需求理解、同理心
✓ 文化契合 - 价值观一致、长期承诺
```

#### 2.2 评分机制

1. **LLM 直接评分**
   ```json
   {
     "scores": {
       "沟通能力": 8.0,
       "问题解决": 7.5
     }
   }
   ```

2. **关键词推导**（如 LLM 未给出直接评分）
   - 通过回答中的关键词出现次数
   - 计算每个特质的关键词密度
   - 推导 1-10 的评分

3. **平滑更新**
   ```
   新评分 = 当前评分 × 0.7 + 此次评分 × 0.3
   ```

### 3. 对话深度管理

```
深度 0-2: 破冰阶段（HR）
├─ 认识候选人
├─ 了解背景
└─ 建立信任

深度 2-4: 专业深度（技术总监）
├─ 技术细节
├─ 问题解决能力
└─ 架构思维

深度 4-6: 产品视角（产品经理）
├─ 用户思维
├─ 创新能力
└─ 市场理解

深度 6-8: 综合视角（多角色）
├─ 综合素质
├─ 跨领域能力
└─ 多角度评估

深度 8-10: 战略高度（CTO）
├─ 战略眼光
├─ 领导力
└─ 长期规划
```

### 4. 行为模式识别

系统自动检测的模式：
- 结构化思维 - "首先...其次...最后..."
- 实例驱动 - 用具体案例支撑
- 系统思维 - 从全局考虑
- 用户导向 - 以用户为中心
- 创新思维 - 新颖想法
- 团队意识 - 强调协作
- 自我反思 - 认识不足
- 持续学习 - 追求进步

---

## 📈 特质提取算法

### 步骤 1：收集候选人回答
```python
response = "首先，我会理解需求。其次，分析市场。最后，设计方案。
例如，在我前公司的项目中..."
```

### 步骤 2：关键词匹配
```python
# 对于每个特质维度
沟通能力特质词 = ["清晰", "表达", "沟通", "说明"]
匹配数 = count(response, 特质词)

# 对于指标词
指标词 = ["逻辑清晰", "用词恰当", "举例生动"]
指标数 = count(response, 指标词)

分数 = 5.0 + 匹配数 × 0.5 + 指标数 × 1.0
分数 = min(10.0, 分数)
```

### 步骤 3：LLM 深度评估

如果关键词匹配不充分，调用 LLM：
```json
系统角色提示 + 评估指南 + 候选人回答
  → LLM 评估
  → {scores: {...}, analysis: "..."}
```

### 步骤 4：动态更新

```python
# 平滑更新（防止评分剧烈波动）
new_score = current_score × 0.7 + evaluated_score × 0.3
```

---

## 🎨 前端优化建议

### 1. 实时评分可视化

```typescript
// 使用 ECharts 雷达图实时更新
watch(latestScores, () => {
  renderRadarChart(latestScores)
}, { deep: true })
```

### 2. 消息流优化

```typescript
// 保持滚动到最新消息
async function scrollToBottom() {
  await nextTick()
  messageStream.value.scrollTop = messageStream.value.scrollHeight
}
```

### 3. 错误处理和降级

```typescript
// API 失败时使用本地备用
try {
  response = await fetchFromAPI()
} catch (error) {
  response = getLocalFallback()
}
```

---

## 🔐 环境配置

### .env 文件配置

```env
# Road2All API（推荐）
ROAD2ALL_API_KEY=sk-xxxxxxxxxxxxxx
ROAD2ALL_MODEL=gpt-4o
ROAD2ALL_API_BASE=https://api.road2all.tech/v1

# 或使用 OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
```

### 获取 API Key

1. **Road2All** （推荐，国内可用）
   - 访问: https://api.road2all.tech
   - 注册并获取 API Key
   - 模型支持: gpt-4o, gpt-4-turbo, gpt-3.5-turbo

2. **OpenAI** （国外用户）
   - 访问: https://platform.openai.com
   - 创建 API Key
   - 需要国外支付方式

---

## 📝 API 文档

### POST `/assessment/immersive/next-question`

生成下一个评估问题。

**请求参数:**
```
candidate_id: string  (必需) - 候选人ID
role_id: string       (必需) - 角色ID (hr/tech_lead/product/cto)
conversation_depth: int - 对话深度 (0-10)
history: string       - 对话历史 (JSON格式)
target_position: string - 目标岗位
```

**响应示例:**
```json
{
  "code": 200,
  "data": {
    "question": "请描述一个你最近解决的复杂技术问题",
    "tags": ["问题解决", "技术深度"],
    "suggestions": ["我遇到了...", "我的方案是..."],
    "context": "展示深度思考的好机会",
    "expected_traits": ["技术深度", "问题解决", "系统思维"]
  }
}
```

### POST `/assessment/immersive/analyze-response`

分析候选人的回答。

**请求参数:**
```
candidate_id: string
candidate_name: string - 候选人名字
current_speaker: string - 当前提问者角色
candidate_response: string - 候选人回答
conversation_depth: int
previous_messages: string - 历史消息 (JSON)
target_position: string - 目标岗位
```

**响应示例:**
```json
{
  "code": 200,
  "data": {
    "scores": {
      "沟通能力": 7.5,
      "问题解决": 8.0,
      "技术深度": 7.8
    },
    "sentiment": {
      "emotion": "自信",
      "confidence": 85
    },
    "patterns": [
      {
        "name": "结构化思维",
        "description": "回答展示清晰逻辑",
        "confidence": 78,
        "color": "#67c23a"
      }
    ],
    "feedback": "很好的回答，思路清晰",
    "next_action": "continue"
  }
}
```

### POST `/assessment/immersive/save-session`

保存评估会话。

**请求体:**
```json
{
  "candidate_id": "1",
  "assessment_id": 123,
  "messages": [...],
  "scores": {
    "沟通能力": 7.5,
    ...
  },
  "duration_seconds": 1200,
  "conversation_depth": 10,
  "total_rounds": 15,
  "highlights": ["优点1", "优点2"]
}
```

### GET `/assessment/immersive/roles`

获取所有可用角色列表。

---

## ⚡ 性能优化

### 1. 缓存策略

```python
# 缓存常用问题
@cache(expires=3600)
def get_question_bank(role_id: str):
    return QUESTION_BANK[role_id]
```

### 2. 并行处理

```python
# 同时进行多个评估任务
tasks = [
  evaluate_response(response),
  detect_patterns(response),
  analyze_sentiment(response)
]
results = await asyncio.gather(*tasks)
```

### 3. Token 优化

- 使用较短的 system prompt
- 减少对话历史的上下文窗口
- 合理设置 max_tokens

---

## 🐛 常见问题排查

### 问题 1: LLM API 调用超时

```python
# 增加超时时间
timeout = 120  # 秒

# 或实现重试机制
@retry(max_attempts=3)
async def call_llm():
    ...
```

### 问题 2: JSON 解析失败

```python
# 使用更健壮的解析
def parse_llm_response(content):
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        return json.loads(content[start:end])
    except:
        return {}  # 返回备用值
```

### 问题 3: 评分不稳定

```python
# 使用平滑更新
score = current × 0.7 + new × 0.3

# 限制单次变化
max_change = 1.0  # 单次最多变化 1 分
```

---

## 📚 参考资源

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Road2All API 文档](https://api.road2all.tech/docs)
- [FastAPI 异步编程](https://fastapi.tiangolo.com/async/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq/)

---

## ✅ 验收检查清单

- [ ] 已安装所有必要的 Python 包
- [ ] 配置了正确的 LLM API Key
- [ ] 后端路由已注册
- [ ] 前端 URL 已正确配置
- [ ] 测试了问题生成接口
- [ ] 测试了回答分析接口
- [ ] 测试了会话保存接口
- [ ] 前端能正确显示分数和模式
- [ ] 对话历史正确保存
- [ ] 支持多角色轮转

---

## 🚀 下一步计划

1. **完善特质提取** - 调整关键词权重，提高准确性
2. **岗位匹配优化** - 实现更精准的岗位-候选人匹配
3. **报告生成** - 自动生成评估报告
4. **数据分析** - 大规模候选人数据分析
5. **A/B 测试** - 优化对话流程和问题质量

---

## 📞 支持

如遇到技术问题，请检查：
1. 环境变量是否正确配置
2. API Key 是否有效且有余额
3. 网络连接是否正常
4. 后端日志中的错误信息
