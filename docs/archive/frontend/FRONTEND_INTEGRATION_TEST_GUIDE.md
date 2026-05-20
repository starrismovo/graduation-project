# 前端集成测试指南

## 📋 测试环境准备

### 1. 启动后端服务

```bash
cd backend
python main.py
```

预期输出：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. 启动前端开发服务器

```bash
cd frontend
npm install  # 如果未安装依赖
npm run dev
```

预期输出：
```
  VITE v... ready in ... ms

  ➜  Local:   http://localhost:5173/
```

### 3. 访问测试页面

在浏览器中打开：
```
http://localhost:5173
```

---

## 🧪 测试步骤

### Step 1: 基本信息填写

**预期行为：**
- [ ] 页面加载正常，显示表单
- [ ] 输入框可以输入文本
- [ ] "下一步" 按钮可以点击

**测试数据：**
```
姓名: 测试用户
邮箱: test@example.com
电话: 13800138000
```

### Step 2: 情境面试

**预期行为：**
- [ ] 加载场景数据（异步加载，显示加载指示）
- [ ] 左侧面板动态显示场景信息
- [ ] 显示场景标题、描述、目标特质
- [ ] 显示面试问题
- [ ] 可以输入回答

**关键验证点：**
```javascript
// 浏览器开发者工具 → Console
// 验证情境数据是否正确传输
console.log('currentScenario:', currentScenario)
// 应该看到：{title, description, target_traits, max_rounds, ...}
```

**回答示例：**
- 问题1: "请描述一次你处理客户投诉的经历"
- 回答: "当客户反映产品质量问题时，我立即..."

**提交后预期：**
- [ ] 显示 AI 评分（5个特质）
- [ ] 评分范围 0-10
- [ ] 显示 AI 评价（reasoning）

### Step 3: 认知任务 ⭐ 关键测试

#### 3.1 验证推荐任务

**根据 HR 评分的推荐结果：**

| 场景 | HR 评分 | 预期推荐 | 难度 |
|------|--------|--------|------|
| **高分情景** | 责任心>7 且情绪稳定性>7 | 逻辑推理 | 3 |
| **低分情景** | 责任心<5 | 反应时 | 1 |
| **中等情景** | 其他 | N-Back | 2 |

**验证方法：**
```javascript
// 浏览器 Console
console.log('hrScores:', latestScores)
console.log('recommendedTaskId:', recommendedTaskId)
console.log('taskDifficulty:', taskDifficulty)
```

#### 3.2 N-Back 任务测试（如果推荐）

**预期界面：**
- 显示大数字（居中）
- 显示进度条（0/20, 0/30, 或 0/40）
- 显示按钮或键盘提示

**操作步骤：**
1. 按 Y 键：表示当前数字与 N 步前的数字匹配
2. 按 N 键：表示不匹配
3. 重复直到完成所有试验

**预期数据收集：**
```javascript
{
  accuracy: 75.5,        // %
  avgReactionTime: 850,  // ms
  consistency: 82.3,     // %
  correctCount: 15,      // 正确数
  totalTrials: 20        // 总试次
}
```

#### 3.3 反应时任务测试（如果推荐）

**预期界面：**
- 初始显示"等待..."
- 随机出现红色圆点
- 点击圆点或按空格

**操作步骤：**
1. 看到红色圆点时，尽快点击或按空格
2. 重复 15-25 次试验

**预期数据收集：**
```javascript
{
  avgReactionTime: 450,  // ms
  minReactionTime: 250,  // ms
  maxReactionTime: 800,  // ms
  consistency: 88.5,     // % (越高越稳定)
  totalTrials: 15
}
```

#### 3.4 逻辑推理任务测试（如果推荐）

**预期界面：**
- 显示几何图案
- 显示 4 个选项（A、B、C、D）
- 进度条显示"1/5"、"2/5" 等

**操作步骤：**
1. 观察图案规律
2. 选择最合理的下一个图案
3. 重复 5-10 题

**预期数据收集：**
```javascript
{
  accuracy: 80,           // %
  avgTime: 18.5,          // 秒
  correctCount: 4,        // 正确数
  totalProblems: 5,       // 总题数
  score: 85               // 综合评分
}
```

#### 3.5 验证任务结果显示

**完成任务后预期：**
- [ ] 显示"任务完成"提示
- [ ] 显示详细指标
- [ ] 显示 AI 分析（accuracy, speed, reasoning等）
- [ ] 可以返回选择其他任务或继续

---

## 🔍 浏览器开发者工具检查

### Console 检查

打开浏览器开发者工具（F12），进入 Console 标签页，输入以下命令验证：

#### 检查 HR 评分：
```javascript
// 应该看到一个对象，包含5个特质的评分
console.log('HR Scores:', latestScores)

// 示例输出：
// {
//   "责任心": 8.5,
//   "宜人性": 6.5,
//   "情绪稳定性": 7.5,
//   "经验开放性": 7,
//   "外向性": 6
// }
```

#### 检查当前情景：
```javascript
// 应该看到情景对象，包含 title, description 等
console.log('Current Scenario:', currentScenario)

// 示例输出：
// {
//   "id": "scenario_001",
//   "title": "客户投诉处理",
//   "description": "你正在处理一个...",
//   "target_traits": ["责任心", "宜人性"],
//   "max_rounds": 3
// }
```

#### 检查认知任务状态：
```javascript
// 检查是否正确识别推荐任务
console.log('Recommended Task:', recommendedTaskId)  // 应该是：n-back, reaction-time, 或 logic
console.log('Task Difficulty:', taskDifficulty)      // 应该是：1, 2, 或 3
```

### Network 检查

1. 打开 DevTools → Network 标签页
2. 完成情境面试
3. 查找 POST 请求到 `/api/interview/save-response`
4. 检查响应数据：
   ```json
   {
     "response_id": "resp_xxx",
     "scores": {
       "责任心": 8.5,
       ...
     },
     "reasoning": "...",
     "saved": true
   }
   ```

---

## ❌ 常见问题排查

### 问题 1: HR 评分为空或未定义

**症状：**
```
Uncaught TypeError: Cannot read property 'get' of undefined
```

**排查步骤：**
1. 检查 SituationalQA 是否正确 emit HR 评分
2. 在 AssessmentView 的 `handleUpdateAnswers` 中添加 console.log：
   ```javascript
   function handleUpdateAnswers(data) {
     console.log('Received answers:', data)
     // 应该包含 scores
   }
   ```

3. 确保后端 `/api/interview/score-answer` 返回正确格式

### 问题 2: 推荐任务为 undefined

**症状：**
```
Error: Cannot render undefined task
```

**排查步骤：**
1. 检查 `recommendedTaskId` computed 是否正确
2. 在浏览器 console 验证：
   ```javascript
   console.log(recommendedTaskId.value)  // 应该是字符串
   ```

3. 确保 `tasks` 数组中的 id 与推荐逻辑中的 id 匹配

### 问题 3: 任务键盘快捷键无效（N-Back）

**症状：**
按下 Y/N 键没有反应

**排查步骤：**
1. 检查输入焦点：任务区域应该被选中
2. 在浏览器 console 添加监听：
   ```javascript
   document.addEventListener('keydown', (e) => {
     console.log('Key pressed:', e.key)
   })
   ```

3. 确保组件正确绑定了 `@keydown` 事件

### 问题 4: 反应时任务的红点不出现

**症状：**
页面显示"等待..."但没有出现红点

**排查步骤：**
1. 检查 CSS 是否正确定义红点样式
2. 在浏览器 DevTools 中检查元素是否存在
3. 检查 setTimeout 是否正确执行

### 问题 5: 逻辑推理题目不显示

**症状：**
只看到空白或加载指示

**排查步骤：**
1. 检查 `logicProblems` 数组是否正确初始化
2. 在 console 验证：
   ```javascript
   console.log('Logic problems:', logicProblems.value)
   ```

3. 确保模板中的循环正确：`v-for="(problem, index) in logicProblems"`

---

## 📊 性能检查

### 加载时间

使用浏览器 DevTools → Performance 标签页：

1. 点击"Record"
2. 执行一个完整的任务
3. 停止录制
4. 查看"Timing"面板

**预期指标：**
- 页面加载：< 2s
- 任务切换：< 500ms
- 反馈显示：< 100ms

### 内存使用

在 Console 中执行：
```javascript
// 检查内存使用
console.memory.jsHeapSizeLimit / 1048576  // MB
```

**预期值：** < 200MB

---

## ✅ 完整测试检查清单

### 基本功能
- [ ] SituationalQA 显示场景
- [ ] 场景数据动态显示在左侧面板
- [ ] 提交回答后显示 HR 评分

### 推荐系统
- [ ] 高分→推荐逻辑推理，难度3
- [ ] 低分→推荐反应时，难度1
- [ ] 中等分→推荐N-Back，难度2

### 任务执行
- [ ] N-Back 任务：Y/N 键工作，进度显示，反馈显示
- [ ] 反应时任务：红点出现，鼠标/空格响应，反应时计算
- [ ] 逻辑推理：题目显示，选项可点击，答案显示正确

### 数据收集
- [ ] 准确率正确计算
- [ ] 反应时数据准确
- [ ] 稳定性/一致性计算合理

### UI/UX
- [ ] 布局美观，无错位
- [ ] 颜色对比充分
- [ ] 进度条清晰
- [ ] 反馈及时

### 集成流程
- [ ] 所有5个步骤都能完成
- [ ] 数据在步骤间正确传递
- [ ] 没有控制台错误或警告

---

## 📝 测试报告模板

```markdown
# 认知任务系统测试报告

## 环境信息
- 浏览器：
- 操作系统：
- 后端版本：
- 前端版本：

## 测试用例

### 1. 情境面试 → 认知任务数据流
- [ ] 通过
- [ ] 失败（描述问题）

### 2. HR 评分推荐算法
- [ ] 高分场景推荐正确
- [ ] 低分场景推荐正确
- [ ] 中等场景推荐正确

### 3. 任务执行
- [ ] N-Back：[ ] 通过 [ ] 失败
- [ ] 反应时：[ ] 通过 [ ] 失败
- [ ] 逻辑推理：[ ] 通过 [ ] 失败

### 4. 数据准确性
- [ ] 准确率计算正确
- [ ] 反应时计算正确
- [ ] 一致性计算正确

## 发现的问题

| 问题 | 严重程度 | 备注 |
|------|--------|------|
| | 高/中/低 | |

## 总体评分

- 功能完整性：___ / 10
- UI/UX 质量：___ / 10
- 性能表现：___ / 10
- **总体评分：___ / 10**

## 建议

- ...
```

---

## 🚀 下一步

测试通过后：
1. 修复发现的问题
2. 记录测试结果
3. 准备进入下一阶段（PersonalityScale）
4. 规划第二阶段智能增强

---

**文档版本：** 1.0  
**最后更新：** 2026-02-02
