# 🎯 HR-Agent LLM 配置指南

## 概述

HR-Agent 支持 **两种工作模式**：

1. **模拟模式（Mock）**：使用本地规则引擎
   - 快速响应，无需 API 调用
   - 完全可控和可解释
   - 适合开发、测试、演示

2. **真实 API 模式**：调用实际的 LLM API
   - 更精准的评分和追问
   - 需要 API 密钥和网络连接
   - 适合生产环境

---

## 🚀 快速开始

### 方式 1：自动检测（推荐）

**无需任何配置**，系统会自动判断：

```python
from backend.prompts.hr_agent_llm import HRAgentLLM

# 自动检测：没有 OPENAI_API_KEY 时使用模拟模式
llm = HRAgentLLM()
```

✅ **当环境变量不存在时**：自动使用模拟模式  
✅ **当设置 OPENAI_API_KEY 时**：自动使用真实 API

---

### 方式 2：手动强制模拟模式（开发时推荐）

明确指定使用模拟模式，这样即使有 API Key 也会使用本地规则：

```python
from backend.prompts.hr_agent_llm import HRAgentLLM

# 强制使用模拟模式
llm = HRAgentLLM(force_mock=True)
```

---

### 方式 3：强制使用真实 API

指定 API 密钥和强制 API 模式：

```python
from backend.prompts.hr_agent_llm import HRAgentLLM

# 强制使用真实 API
llm = HRAgentLLM(api_key="sk-xxx...", force_mock=False)
```

---

## 📝 环境变量配置

### 方案 A：设置 OPENAI_API_KEY

在系统环境变量中设置：

```bash
# Windows (PowerShell)
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-xxx...", "User")

# Linux / macOS
export OPENAI_API_KEY="sk-xxx..."
```

或在项目根目录的 `.env` 文件中：

```env
OPENAI_API_KEY=sk-xxx...
LLM_FORCE_MOCK=false
```

### 方案 B：强制使用模拟模式

添加环境变量 `LLM_FORCE_MOCK`：

```env
# .env 文件
LLM_FORCE_MOCK=true      # 强制模拟模式
# 或
LLM_FORCE_MOCK=yes       # 等价表示
# 或
LLM_FORCE_MOCK=1         # 等价表示
```

此时即使存在 `OPENAI_API_KEY` 也会使用模拟模式。

---

## 🔄 工作流程对比

### 模拟模式流程

```
用户回答
  ↓
本地规则引擎（即时）
  ├─ 关键词匹配
  ├─ 长度评估
  └─ 规则评分
  ↓
返回评分结果（毫秒级）
```

**特点**：⚡ 快速 | 💰 免费 | 🎯 可控 | 🔍 可解释

---

### 真实 API 模式流程

```
用户回答
  ↓
构建 LLM 提示词
  ↓
调用 OpenAI API
  ├─ 网络请求
  └─ LLM 处理
  ↓
解析 API 响应
  ↓
返回评分结果（秒级）
```

**特点**：🧠 智能 | 💸 付费 | 🌐 需网络 | 📊 更准确

---

## 📊 模拟模式评分规则

### 规则库结构

```python
trait_rules = {
    "责任心": {
        "high_keywords": ["主动", "承担责任", "尽快", "立即", ...],
        "medium_keywords": ["会", "应该", "可以"],
        "base_score": 5.0,
        "high_score": 8.5,
    },
    "宜人性": { ... },
    "情绪稳定性": { ... },
    "学习能力": { ... },
    "创新能力": { ... }
}
```

### 评分算法

```
基础分数 = 5.0（中等）

如果包含高优先级关键词：
  分数 = 8.5
  额外奖励 = (关键词个数 - 1) × 0.3  （上限 9.5）
否则如果包含中等优先级关键词：
  分数 = 6.5 + (关键词个数 - 1) × 0.5
否则：
  分数 = 5.0

长度奖励 = min(1.0, 回答字数 / 100) × 0.5

最终分数 = min(10.0, 分数 + 长度奖励)
```

### 评分示例

| 回答内容 | 包含关键词 | 字数 | 基础分 | 长度奖励 | 最终分 |
|---------|----------|------|--------|---------|--------|
| "我会立即主动承担责任" | 3 | 12 | 9.1 | 0.06 | 9.2 |
| "我会尽快处理" | 2 | 8 | 8.8 | 0.04 | 8.8 |
| "我会处理这个问题" | 0 | 10 | 5.0 | 0.05 | 5.1 |

---

## 🔧 配置优先级

系统会按以下顺序决定使用哪种模式：

```
1. force_mock 参数（代码级别）
   ├─ True  → 使用模拟模式
   └─ False → 使用真实 API（需 api_key）

2. 若 force_mock 为 None，检查环境变量 LLM_FORCE_MOCK
   ├─ true/1/yes → 使用模拟模式
   └─ 其他      → 进入第 3 步

3. 检查是否存在 API Key
   ├─ 存在 OPENAI_API_KEY → 使用真实 API
   └─ 不存在            → 使用模拟模式
```

---

## 💡 开发建议

### 阶段 1：开发和测试

**推荐配置**：强制使用模拟模式

```python
# backend/main.py
from backend.prompts.hr_agent_llm import HRAgentLLM

# 在开发期间使用模拟模式
llm = HRAgentLLM(force_mock=True)
```

**优点**：
- ✅ 快速开发（无网络延迟）
- ✅ 节省 API 成本
- ✅ 便于调试（可预测的输出）
- ✅ 支持离线开发

---

### 阶段 2：集成测试

**推荐配置**：自动检测

```python
# 使用环境变量进行切换
# 开发：LLM_FORCE_MOCK=true
# 测试：不设置该变量，自动检测
```

**步骤**：
1. 设置 `.env` 中 `LLM_FORCE_MOCK=false`
2. 配置真实的 `OPENAI_API_KEY`
3. 运行完整的集成测试

---

### 阶段 3：生产环境

**推荐配置**：使用真实 API

```python
# 设置环境变量
OPENAI_API_KEY=sk-xxx...
LLM_FORCE_MOCK=false  # 或不设置此变量
```

**注意事项**：
- 🔐 安全存储 API Key（不要提交到 Git）
- 💰 监控 API 使用成本
- ⚠️ 实施请求速率限制
- 📊 记录 API 调用日志

---

## 🧪 测试模式

### 验证模拟模式

```bash
cd backend
python -c "
from prompts.hr_agent_llm import HRAgentLLM

llm = HRAgentLLM(force_mock=True)

# 测试追问生成
follow_up = llm.generate_follow_up_question(
    scenario_description='项目延期',
    target_traits=['责任心', '宜人性'],
    previous_answers=[],
    round_num=1
)
print('追问问题:', follow_up['question'])

# 测试评分
score = llm.score_answer(
    scenario_description='项目延期',
    target_traits=['责任心'],
    current_answer='我会立即主动承担责任，尽快制定补救方案',
    all_answers=[]
)
print('评分:', score['scores'])
"
```

### 验证真实 API 模式

```bash
cd backend
OPENAI_API_KEY=sk-xxx python -c "
from prompts.hr_agent_llm import HRAgentLLM

llm = HRAgentLLM(force_mock=False)

# 测试 API 调用
follow_up = llm.generate_follow_up_question(
    scenario_description='项目延期',
    target_traits=['责任心'],
    previous_answers=[],
    round_num=1
)
print('API 返回结果:', follow_up)
"
```

---

## 🔌 OpenAI API 集成（待实现）

当需要切换到真实 API 时，实现以下方法：

```python
# backend/prompts/hr_agent_llm.py

def _call_openai(self, messages: List[Dict]) -> Dict[str, Any]:
    """调用 OpenAI Chat Completions API"""
    from openai import OpenAI
    
    client = OpenAI(api_key=self.api_key)
    response = client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    content = response.choices[0].message.content
    # 解析 JSON 或提取问题
    return {"question": content, "reasoning": "..."}

def _call_openai_scoring(self, prompt: str) -> Dict[str, Any]:
    """调用 OpenAI 进行特质评分"""
    from openai import OpenAI
    
    client = OpenAI(api_key=self.api_key)
    response = client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # 更确定的回答
        max_tokens=1000
    )
    
    content = response.choices[0].message.content
    # 解析 JSON 格式的评分结果
    return json.loads(content)
```

---

## 📋 常见问题

### Q1: 我应该在开发阶段使用哪种模式？
**A**: 强烈推荐使用 **模拟模式**（force_mock=True）
- 快速反馈
- 节省成本
- 便于调试

### Q2: 如何在开发和生产环境间切换？
**A**: 使用环境变量
```env
# .env.development
LLM_FORCE_MOCK=true

# .env.production
LLM_FORCE_MOCK=false
OPENAI_API_KEY=sk-xxx...
```

### Q3: 模拟模式的评分准确吗？
**A**: 模拟模式使用关键词匹配，适合：
- ✅ 快速原型验证
- ✅ 功能流程测试
- ✅ 性能压测

不适合：
- ❌ 精准人力评估
- ❌ 生产决策

### Q4: 切换到真实 API 需要修改代码吗？
**A**: **不需要**！只需设置环境变量
```bash
export OPENAI_API_KEY="sk-xxx..."
# 系统会自动使用 API，无需修改代码
```

### Q5: 真实 API 的成本是多少？
**A**: 取决于你的使用量和模型选择
- GPT-3.5-turbo: ~¥0.0007 / 1K tokens
- GPT-4: ~¥0.03 / 1K tokens

建议在生产环境设置使用限制和监控。

---

## 📚 相关文档

- [HR_AGENT_GUIDE.md](HR_AGENT_GUIDE.md) - HR-Agent 架构详解
- [API_REFERENCE.md](API_REFERENCE.md) - API 端点参考
- [QUICK_START.md](QUICK_START.md) - 快速启动指南

---

## 🎓 总结

| 特性 | 模拟模式 | 真实 API |
|------|--------|---------|
| 速度 | ⚡⚡⚡ | ⚡⚡ |
| 成本 | 💰 | 💸💸 |
| 准确度 | 🎯 | 🎯🎯🎯 |
| 配置难度 | ✨ | ⚠️ |
| 网络依赖 | 否 | 是 |
| 推荐用途 | 开发/测试 | 生产 |

**开发阶段**：使用模拟模式快速迭代  
**生产环境**：集成真实 API 获得最佳体验
