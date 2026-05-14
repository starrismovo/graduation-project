# 系统功能设计与架构文档

## 📋 目录

1. [系统概述](#系统概述)
2. [用户角色与流程](#用户角色与流程)
3. [系统架构](#系统架构)
4. [核心模块设计](#核心模块设计)
5. [数据流动与交互](#数据流动与交互)
6. [面试页面详细设计](#面试页面详细设计)
7. [后端 API 接口](#后端-api-接口)
8. [系统特色与创新](#系统特色与创新)

---

## 系统概述

### 项目名称

**基于AI智能体的人岗匹配心理特质评估系统**

### 核心价值

本系统是一个企业招聘与人才评估平台，通过**多Agent协同**的方式实现智能化面试和个性化评估。系统核心目标：

- **智能化**：用AI面试官替代部分人工环节，降低招聘成本
- **客观化**：基于大五人格模型进行科学评估，规避主观偏见
- **可解释性**：提供完整的人岗匹配证据链和评估建议

### 系统用户

| 用户类型 | 角色 | 主要功能 |
|---------|------|---------|
| **候选人** | 求职者 | 查看岗位、参加AI面试、查看评估报告 |
| **HR** | 招聘人员 | 创建岗位、查看候选人评估、管理邀请、数据分析 |

---

## 用户角色与流程

### 1. 候选人流程

```
登录/注册
   ↓
首页浏览
   ├─ 查看个人心理画像（如已评估过）
   ├─ 查看历史评估记录
   ├─ 浏览推荐岗位
   └─ 查看评估报告
   ↓
选择岗位
   ↓
上传简历/填写基本信息
   ↓
进入沉浸式面试 (ImmersiveRoleDialogue.vue)
   ├─ 第0步：岗位确认
   ├─ 第1步：简历解析
   ├─ 第2步：面试启动
   ├─ 第3步：多轮AI面试
   └─ 第4步：评估报告生成
   ↓
查看评估结果
   ├─ 个人人格评分
   ├─ 与岗位的匹配度
   ├─ 核心优势和改进空间
   └─ 专业建议
```

### 2. HR流程

```
登录/注册（is_hr=true）
   ↓
HR首页 (HRHomeView.vue)
   ├─ 岗位管理标签
   │  ├─ 查看岗位列表及统计
   │  ├─ 创建/编辑岗位
   │  └─ 查看岗位匹配的候选人
   │
   └─ 候选人管理标签
      ├─ 查看已评估候选人
      ├─ 邀请候选人参加评估
      └─ 查看评估报告
   ↓
候选人管理 (CandidateManageView.vue)
   ├─ 选择岗位
   ├─ 查看该岗位的已评估候选人
   ├─ 查看智能推荐候选人
   └─ 发送邀请
   ↓
岗位管理 (JobManageView.vue)
   ├─ 查看所有岗位
   ├─ 创建/编辑岗位
   └─ 查看岗位的应聘/评估情况
   ↓
数据分析 (AnalyticsView.vue)
   ├─ 岗位总体指标
   ├─ 候选人匹配分布
   ├─ 评估进度统计
   └─ 各岗位详细数据
```

---

## 系统架构

### 1. 整体分层架构

```
┌─────────────────────────────────────────────────────┐
│                   前端层 (Vue 3 + TS)                 │
├─────────────────────────────────────────────────────┤
│ 页面层      │ 组件层          │ 状态管理 │ API层       │
│ ·Views     │ ·Components     │ ·Pinia  │ ·api/      │
│ ·Routing   │ ·RadarChart     │ ·Store  │ ·request   │
└─────────────────────────────────────────────────────┘
                          ↕
              HTTP REST API + WebSocket
                          ↕
┌─────────────────────────────────────────────────────┐
│               后端层 (FastAPI + Python)               │
├─────────────────────────────────────────────────────┤
│ 路由层      │ 服务层          │ 数据层  │ 外部服务    │
│ ·routers   │ ·immersive_     │ ·models │ ·LLM API   │
│ ·assessment│  dialogue       │ ·schemas│ ·OCR       │
│ ·job       │ ·personality_   │ ·db     │            │
│ ·hr_*      │  scoring        │         │            │
└─────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────┐
│               数据层 (MySQL + SQLAlchemy)             │
├─────────────────────────────────────────────────────┤
│ ·User            ·Job                ·AssessmentRecord │
│ ·HRProfile       ·JobRequirement     ·TraitScore      │
│ ·CandidateProfile ·Scenario          ·EvaluationResult │
└─────────────────────────────────────────────────────┘
```

### 2. 多Agent架构设计

面试评估系统采用**三Agent协同**方案：

```
┌────────────────────────────────────────────────┐
│          统一接口 POST /assessment/immersive/  │
│              agent/execute                     │
└────────────────────────────────────────────────┘
              ↓
    ┌─────────┴─────────┬─────────────┐
    ↓                   ↓             ↓
┌─────────────┐  ┌─────────────┐ ┌────────────┐
│  Interviewer│  │  Evaluator  │ │  Decision  │
│    Agent    │  │    Agent    │ │   Agent    │
└─────────────┘  └─────────────┘ └────────────┘
    ↓                   ↓             ↓
生成面试问题      分析回答内容    决策面试流程
评估表现          提取人格特征    判断是否结束
维持对话流        计算分数        生成建议
```

**各Agent职责**：

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **InterviewerAgent** | 生成智能问题，维持面试流程 | 对话历史、候选人背景、岗位信息 | 下一个问题、对话标签 |
| **EvaluatorAgent** | 分析候选人回答，提取人格特征和维度分数 | 回答内容、问题、对话历史 | 维度评分、情感分析、模式识别 |
| **DecisionAgent** | 决定是否继续/结束面试，生成综合评价 | 累计评分、对话深度、回答质量 | 面试建议、结束信号、综合评分 |

---

## 核心模块设计

### 1. 候选人首页 (HomeView.vue)

**功能概述**：候选人的个人中心，展示评估结果、应聘历史、岗位推荐

**页面构成**：

```
┌────────────────────────────────────────────┐
│           Hero Banner (个人欢迎区)           │
│  头像、姓名、个人概述、快速操作按钮         │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│      个人心理画像 (PsychologyDetail)        │
│  • 大五人格雷达图                          │
│  • 均匀分布展示各维度                      │
│  • 个性化文案说明                          │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│         2列主内容区                        │
├────────────────┬──────────────────────────┤
│ 左列：历史记录  │ 右列：岗位推荐 & 洞察    │
│ • 评估记录列表 │ • 推荐岗位卡片           │
│ • 显示得分     │ • 人格优势/弱点          │
│ • 查看报告链接 │ • 发展方向               │
└────────────────┴──────────────────────────┘
```

**关键数据源**：

```javascript
// 1. 心理画像数据
GET /assessment/portrait/{candidateId}
// Response: [{name, score}, ...]

// 2. 历史评估记录
GET /assessment/history/{candidateId}
// Response: [{id, jobTitle, matchScore, createdAt}, ...]

// 3. 推荐岗位
GET /assessment/recommended-jobs/{candidateId}
// Response: [{id, title, matchScore, matchReason}, ...]

// 4. 评估报告详情
GET /assessment/report/{recordId}
// Response: {personalityScores, matchAnalysis, recommendations, ...}
```

### 2. HR首页 (HRHomeView.vue)

**功能概述**：HR的仪表板，展示岗位和候选人管理、邀请跟进、数据总览

**页面构成**：

```
┌────────────────────────────────────────────┐
│     岗位管理 Tab / 候选人管理 Tab           │
└────────────────────────────────────────────┘

【岗位管理 Tab】
  ┌─────────────────────────────────────────┐
  │ KPI卡片：开放岗位数、总应聘、平均匹配度  │
  └─────────────────────────────────────────┘
  ┌─────────────────────────────────────────┐
  │ 岗位聚焦 (Spotlight Grid)：4个精选岗位    │
  │ 显示：岗位名、应聘数、评估人数、匹配度   │
  └─────────────────────────────────────────┘
  ┌─────────────────────────────────────────┐
  │ 2列布局                                  │
  ├──────────────────┬──────────────────────┤
  │ 左：优先队列      │ 右侧卡片：           │
  │ 待邀请候选人      │ • 关键洞察           │
  │                  │ • 快速操作           │
  │ 中：最近岗位      │ • 待处理统计         │
  └──────────────────┴──────────────────────┘

【候选人管理 Tab】
  ┌─────────────────────────────────────────┐
  │ 筛选：岗位筛选、状态筛选、刷新按钮        │
  └─────────────────────────────────────────┘
  ┌─────────────────────────────────────────┐
  │ 候选人表格：姓名、应聘岗位、匹配度、      │
  │ 评估状态、操作（查看报告）               │
  └─────────────────────────────────────────┘
```

### 3. 候选人管理 (CandidateManageView.vue)

**功能概述**：HR针对特定岗位的候选人筛选和邀请管理

**页面构成**：

```
┌────────────────────────────────────────────┐
│  页头：选择岗位下拉框、刷新按钮             │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│  Focus Banner：岗位焦点，显示岗位信息      │
│  & 快速操作（创建岗位、查看报告等）        │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│  运营优先级卡片 (ops-priority-card)        │
│  3列KPI：待邀请数、就绪报告数、邀请目标    │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│           2列主体布局                      │
├────────────────┬──────────────────────────┤
│ 左：候选人表格  │ 右：侧栏卡片             │
│ • 已评估候选人 │ • 待邀请列表            │
│ • 匹配度分数   │ • 智能推荐候选人        │
│ • 评估状态     │ • 邀请目标              │
│ • 分页         │                        │
└────────────────┴──────────────────────────┘
```

**关键功能**：

- **岗位选择**：从下拉框选择岗位，触发数据重载
- **候选人列表**：展示该岗位的已评估候选人，可按匹配度排序
- **推荐候选人**：调用 `getHRRecommendedCandidates(jobId)` 获得智能推荐
- **邀请管理**：显示已发送邀请列表、邀请状态（pending/accepted/rejected）
- **快速操作**：查看报告、发送邀请、管理邀请

### 4. 岗位管理 (JobManageView.vue)

**功能概述**：HR的岗位CRUD管理，展示应聘统计和匹配分析

**页面构成**：

```
┌────────────────────────────────────────────┐
│  页头：标题、创建按钮、操作按钮             │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│  统计网格：4个指标卡片                     │
│  • 开放岗位数                             │
│  • 总应聘人数                             │
│  • 平均匹配度                             │
│  • 待审核报告数                           │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│  岗位列表                                  │
│  ┌──────────────────────────────────────┐ │
│  │ 岗位名 │状态│应聘数│匹配度│待报告│操作  │ │
│  ├──────────────────────────────────────┤ │
│  │ 前端工程师 │招聘中│15│78%│2│⋯│ │
│  │ 后端工程师 │招聘中│12│82%│1│⋯│ │
│  │ 产品经理 │已暂停│8│65%│0│⋯│ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

### 5. 数据分析 (AnalyticsView.vue)

**功能概述**：招聘漏斗和候选人评估的数据可视化

**页面构成**：

```
┌────────────────────────────────────────────┐
│  KPI卡片 (4列)：                          │
│  • 开放岗位 │ 总评估数 │ 已完成 │ 平均匹配度  │
└────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│     2列图表布局                            │
├────────────────┬──────────────────────────┤
│ 左：各岗位评估 │ 右：匹配度分布            │
│ 人数柱状图     │ (优秀/良好/一般/较差)    │
│ (TOP 10岗位)   │ 甜甜圈或环形图           │
└────────────────┴──────────────────────────┘
       ↓
┌────────────────────────────────────────────┐
│  各岗位详情表格                            │
│  岗位名│总数│已完成│待审│平均分│高分占比   │
└────────────────────────────────────────────┘
```

---

## 数据流动与交互

### 1. 候选人参加面试的完整流程

```
前端流程 (ImmersiveRoleDialogue.vue)
│
├─ 第0步：岗位确认
│  ├─ GET /assessment/immersive/check-resume/{candidateId}
│  │  查询是否有历史简历（PersonalityProfile）
│  ├─ GET /assessment/immersive/check-progress/{candidateId}
│  │  查询是否有进行中的评估
│  └─ 显示快速开始选项或继续评估选项
│
├─ 第1步：简历解析 & 信息确认
│  ├─ [可选] 上传简历 → 后端 OCR/文本提取
│  │   POST /assessment/immersive/upload-resume
│  ├─ 提交候选人信息 (名字、邮箱、学历、技能)
│  │   POST /assessment/immersive/confirm-info
│  └─ 自动填充 candidateInfo 表单
│
├─ 第2步：面试启动准备
│  ├─ GET 岗位详情（如已选择）
│  ├─ 构建 resumeInfo & jobInfo
│  └─ 自动进阶到第3步，显示面试说明
│
├─ 第3步：多轮AI面试 (核心环节)
│  ├─ 初始化对话状态
│  ├─ startTime = Date.now()
│  ├─ 循环调用 analyzeAndGetNextQuestion：
│  │
│  │  POST /assessment/immersive/agent/execute
│  │  {
│  │    operation: "analyze_and_next",
│  │    candidate_id: candidateId,
│  │    candidate_response: userInput,
│  │    conversation_depth: currentDepth,
│  │    history: messages[],
│  │    job_info: { id, title, description },
│  │    resume_info: { name, education, skills }
│  │  }
│  │
│  │  ↓ 后端处理 ↓
│  │  • EvaluatorAgent 分析回答 → 提取评分
│  │  • InterviewerAgent 生成下一题
│  │  • DecisionAgent 判断是否继续
│  │  
│  │  ← 返回 {
│  │    next_question: "...",
│  │    evaluation: {
│  │      scores: { trait1: 7.5, trait2: 8 },
│  │      sentiment: { emotion, confidence },
│  │      patterns: [{...}]
│  │    },
│  │    decision: {
│  │      should_continue: true,
│  │      reason: "...",
│  │      overall_score: 75
│  │    }
│  │  }
│  │
│  │  ↓ 前端更新 ↓
│  │  • 更新 messages[] 添加新消息
│  │  • 更新 latestScores
│  │  • 更新 detectedPatterns
│  │  • 判断 shouldEndInterview
│  │
│  │  用户继续回答 → 循环
│  │
│  └─ 面试结束条件：
│     • shouldEndInterview = true
│     • 或用户手动结束
│     • 或达到最大轮数
│
└─ 第4步：评估报告生成
   ├─ 汇总所有评分数据
   ├─ POST /assessment/save-result
   │  {
   │    candidate_id,
   │    job_id,
   │    all_scores: { trait1, trait2, ... },
   │    personality_scores: { bigfive分数 },
   │    candidate_info: candidateInfo
   │  }
   │
   │  ← 返回 { record_id, report_id }
   │
   ├─ GET /assessment/report/{recordId}
   │  获取完整报告
   │
   └─ 显示报告内容
      • 基础信息（耗时、回答数等）
      • 人格评分 (Big Five)
      • 表现评分（维度得分）
      • 优势和改进空间
      • 岗位匹配度
      • 专业建议
```

### 2. HR邀请候选人流程

```
HR端 (CandidateManageView.vue)
│
├─ 选择岗位 → currentJobId
│  └─ 触发数据重载
│
├─ 加载该岗位的候选人
│  └─ GET /assessment/hr/candidates?job_id={jobId}
│
├─ 显示智能推荐候选人
│  └─ GET /assessment/recommended/{jobId}
│
├─ 发送邀请
│  ├─ 点击推荐候选人卡片或操作按钮
│  ├─ 打开邀请对话框
│  ├─ 预填邀请消息模板
│  └─ POST /invitation/send
│     {
│       hr_id,
│       candidate_id,
│       job_id,
│       message,
│       method: "email" // 或 sms
│     }
│
├─ 跟踪邀请状态
│  ├─ GET /invitation/list
│  │  返回已发送邀请列表，按状态筛选
│  ├─ 显示：待回复、已接受、已拒绝
│  └─ 可重新发送或取消邀请
│
└─ 查看评估报告
   └─ GET /assessment/report/{recordId}
```

### 3. 岗位数据交互

```
创建岗位流程
│
├─ HR 填写岗位基本信息
│  ├─ 岗位名、描述、公司、城市
│  ├─ 薪资范围、岗位分类
│  └─ 文化需求 (Big Five 特征)
│
├─ POST /jobs/
│  {
│    name, description, company, city,
│    salary_min, salary_max,
│    category, required_traits: {
│      extraversion: {min, max},
│      agreeableness: {min, max},
│      ...
│    }
│  }
│
├─ 后端创建岗位记录
│  └─ Job 表 + JobPersonalityFramework
│
└─ 返回岗位 ID + 详情

─────────────────────────────────────

查看岗位流程
│
├─ GET /jobs/
│  获取列表（支持筛选）
│
├─ GET /jobs/{jobId}
│  获取单个岗位详情
│
├─ GET /jobs/stats/candidate
│  获取候选人面试统计（仅候选人）
│
└─ GET /jobs/home/data
   聚合端点：获取主页所有数据（已评估岗位、推荐岗位等）
```

### 4. 数据库核心表关系

```
User (用户)
├─ id, username, email, password
├─ is_hr (HR flag)
├─ created_at
└─ 1:N → HRProfile / CandidateProfile

HRProfile (HR个人资料)
├─ id, user_id, company, department
└─ 1:N → Job, HRInvitation

Job (岗位)
├─ id, name, description, company, city
├─ salary_min, salary_max, category
├─ hr_id
├─ required_traits (JSON: Big Five需求)
└─ 1:N → JobRequirement, AssessmentRecord

JobRequirement (岗位需求详情)
├─ id, job_id
├─ skills[], requirement_tags[]
├─ personality_framework
└─ match_criteria

CandidateProfile (候选人信息)
├─ id, user_id
├─ name, email, education, phone
├─ avatar, bio
└─ 1:N → AssessmentRecord, PersonalityProfile

AssessmentRecord (评估记录)
├─ id, candidate_id, job_id
├─ session_id, status
├─ start_time, end_time
├─ conversation_depth, total_rounds
├─ duration_seconds
└─ 1:1 → EvaluationResult

EvaluationResult (评估结果)
├─ id, assessment_id
├─ match_score (0-100)
├─ personality_scores (JSON: Big Five)
├─ situational_scores (JSON: 场景人格)
├─ match_analysis (JSON: 优势、缺陷、建议)
└─ recommendation_text

PersonalityProfile (心理画像)
├─ id, candidate_id
├─ big_five_scores (JSON)
├─ assessment_count
├─ latest_assessment_id
└─ last_updated

TraitScore (维度评分)
├─ id, assessment_id
├─ trait_name, score, confidence
├─ extraction_method
└─ created_at

HRInvitation (邀请记录)
├─ id, hr_id, candidate_id, job_id
├─ message, method (email/sms)
├─ status (pending/accepted/rejected)
├─ created_at, sent_at, responded_at
└─ response_message
```

---

## 面试页面详细设计

### 概述

**ImmersiveRoleDialogue.vue** 是系统最复杂、最关键的组件，实现了**沉浸式AI面试**功能。通过**多步流程**和**三Agent协同**，实现动态的、个性化的面试评估。

### 页面结构

```
┌─────────────────────────────────────────────────────┐
│              ImmersiveRoleDialogue.vue               │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │     左侧面板 (left-panel)                   │    │
│  │  • SVG欢迎图片 / 流程提示                   │    │
│  │  • 面试进度可视化                          │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │     中央对话区 (conversation-area)          │    │
│  │  • Step 0: 岗位确认                        │    │
│  │  • Step 1: 简历解析                        │    │
│  │  • Step 2: 面试说明                        │    │
│  │  • Step 3: 多轮AI对话                      │    │
│  │  • Step 4: 评估报告                        │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │     输入区 (input-area)                     │    │
│  │  • 多行文本框                              │    │
│  │  • 提交按钮                                │    │
│  │  • Ctrl+Enter 快捷键                       │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │  对话框 (el-dialog)                         │    │
│  │  • 简历上传和信息填写                      │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### 流程控制 (currentStep)

#### Step 0: 岗位选择与初始化

**作用**：让用户选择要评估的岗位或选择"简历综合评估"

**显示内容**：

```vue
<div class="step-0-wrapper">
  <!-- 岗位选择界面 -->
  <div class="job-select-panel">
    <h3>选择岗位</h3>
    <p>您可以针对特定岗位进行评估</p>
    
    <!-- 岗位列表（通过 GET /jobs/ 获取） -->
    <div class="job-list">
      <div class="job-item" v-for="job in jobList">
        {{ job.title }} - {{ job.company }}
        <button @click="selectJob(job.id)">开始评估</button>
      </div>
    </div>
    
    <!-- 快速选项 -->
    <div class="quick-options">
      <button @click="startResumeAssessment">
        简历综合评估（不限岗位）
      </button>
    </div>
  </div>
</div>
```

**数据交互**：

- `loadJobs()` → GET `/jobs/` 获取岗位列表
- `selectJob(jobId)` → 设置 `selectedJobId`, `selectedJobTitle`
- `startResumeAssessment()` → 设置 `assessmentMode = 'resume'`
- 自动进阶 currentStep → 1

#### Step 1: 简历解析与信息确认

**作用**：让用户上传简历或填写基本信息，系统自动提取和识别

**显示内容**：

```vue
<div class="step-1-wrapper resume-parsing">
  <!-- 有历史简历时 -->
  <div v-if="hasExistingResume" class="existing-resume-panel">
    <h4>检测到您已有评估信息</h4>
    <div class="resume-info-display">
      <p>姓名：{{ existingResumeInfo.name }}</p>
      <p>邮箱：{{ existingResumeInfo.email }}</p>
      <p>学历：{{ existingResumeInfo.education }}</p>
      <p>技能：{{ existingResumeInfo.skills.join(', ') }}</p>
    </div>
    <button @click="useExistingResume">使用已有信息</button>
    <button @click="openUploadDialog">上传新简历</button>
  </div>
  
  <!-- 无历史简历时 -->
  <div v-else class="starter-content">
    <h4>{{ introScene.title }}</h4>
    <p>{{ introScene.lines[0] }}</p>
    <p>{{ introScene.lines[1] }}</p>
    <button @click="openUploadDialog">📋 上传简历并开始</button>
  </div>
  
  <!-- 解析中的进度指示 -->
  <div v-if="isAnalyzing" class="parsing-indicator">
    正在解析简历...
  </div>
</div>
```

**简历解析流程**：

```javascript
handleResumeUpload(file) {
  // 1. 读取文件
  const formData = new FormData()
  formData.append('file', file)
  
  // 2. 发送到后端解析
  POST /assessment/immersive/upload-resume
  
  // 3. 后端返回解析结果
  {
    candidate_info: {
      name: "张三",
      email: "zhangsan@company.com",
      education: "本科",
      experience_level: "3-5年",
      technical_skills: ["JavaScript", "Python", "Vue"],
      soft_skills: ["沟通", "学习能力"]
    },
    extraction_method: "ocr" | "text_extract",
    assessed_dimensions: ["技术能力", "问题解决", "沟通能力", "团队协作"]
  }
  
  // 4. 前端显示解析结果
  parsedResumeData = response.data
  
  // 5. 自动填充表单
  candidateInfo.name = parsedResumeData.candidate_info.name
  candidateInfo.email = parsedResumeData.candidate_info.email
  ...
}
```

**对话框内容**（el-dialog）：

```vue
<!-- 简历上传区 -->
<el-upload
  drag
  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
  @change="handleResumeUpload"
/>

<!-- 信息填写表单 -->
<el-form>
  <el-form-item label="姓名 *">
    <el-input v-model="candidateInfo.name" />
  </el-form-item>
  <el-form-item label="邮箱 *">
    <el-input v-model="candidateInfo.email" type="email" />
  </el-form-item>
  <el-form-item label="学历 *">
    <el-select v-model="candidateInfo.education">
      <el-option label="高中" value="高中" />
      <el-option label="本科" value="本科" />
      ...
    </el-select>
  </el-form-item>
  <el-form-item label="技能标签">
    <el-input v-model="candidateInfo.skills"
      placeholder="JavaScript, Vue.js, Python（用逗号分隔）"
    />
  </el-form-item>
  <el-form-item label="项目经验">
    <el-input v-model="candidateInfo.projects" type="textarea" />
  </el-form-item>
</el-form>

<!-- 确认按钮 -->
<el-button type="primary" @click="proceedToStep1">
  确认并继续
</el-button>
```

**数据交互**：

```javascript
async proceedToStep1() {
  if (!candidateInfo.name || !candidateInfo.email) {
    ElMessage.error('请填写必填项')
    return
  }
  
  // 提交信息到后端
  POST /assessment/immersive/confirm-info
  {
    candidate_id: candidateId,
    candidate_name: candidateInfo.name,
    candidate_email: candidateInfo.email,
    education: candidateInfo.education,
    skills: candidateInfo.skills,
    projects: candidateInfo.projects,
    resume_data: parsedResumeData // 若有
  }
  
  // 后端返回确认
  infoConfirmed = true
  
  // 自动进阶
  currentStep = 2
  // 2秒后自动进入 Step 2
  setTimeout(() => currentStep = 2, FLOW_AUTO_ADVANCE_DELAY)
}
```

#### Step 2: 面试启动与说明

**作用**：展示面试计划和注意事项，为用户心理建设

**显示内容**：

```vue
<div class="step-2-wrapper interview-briefing">
  <div class="greeting-avatar">
    <img :src="aiInterviewerAvatar" />
  </div>
  
  <h4>{{ introScene.title }}</h4>
  <p>{{ introScene.lines[0] }}</p>
  
  <div class="briefing-content">
    <!-- 面试计划 -->
    <div class="interview-plan">
      <div class="plan-item">
        <div class="plan-icon">1️⃣</div>
        <div class="plan-detail">
          <div class="plan-title">破冰与背景了解</div>
          <p>从工作经验和背景开始交流</p>
        </div>
      </div>
      <div class="plan-item">
        <div class="plan-icon">2️⃣</div>
        <div class="plan-detail">
          <div class="plan-title">技术深度探索</div>
          <p>深入讨论技术能力和问题解决</p>
        </div>
      </div>
      <div class="plan-item">
        <div class="plan-icon">3️⃣</div>
        <div class="plan-detail">
          <div class="plan-title">综合素质评估</div>
          <p>评价沟通能力和团队协作精神</p>
        </div>
      </div>
    </div>
    
    <!-- 面试统计 -->
    <div class="interview-stats">
      <div class="stat-item">
        <div class="stat-label">预计时长</div>
        <div class="stat-value">6分钟</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">问题数量</div>
        <div class="stat-value">{{ interviewPlan.totalQuestions }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">评估维度</div>
        <div class="stat-value">5</div>
      </div>
    </div>
  </div>
  
  <p class="starter-tip">{{ introScene.lines[1] }}</p>
  <div class="auto-progress-tip">
    <el-icon class="is-loading">⏳</el-icon>
    <span>{{ introScene.status }}</span>
  </div>
</div>
```

**数据交互**：

- 无额外API调用
- 2秒后自动进阶 → currentStep = 3
- 同时调用 `startInterview()` 初始化面试状态

#### Step 3: 多轮AI对话 (核心环节)

**作用**：进行真正的AI面试，实时互动和评估

**显示内容**：

```vue
<div class="step-3-wrapper interview-session">
  <!-- 消息列表 -->
  <div class="messages-container" ref="messageStream">
    <div v-for="(msg, idx) in messages" :key="idx"
      :class="['message-item', msg.role === 'ai' ? 'from-ai' : 'from-candidate']">
      
      <!-- AI消息 -->
      <div v-if="msg.role === 'ai'" class="ai-message">
        <div class="message-avatar">
          <img :src="aiInterviewerAvatar" />
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="speaker-name">AI 面试官</span>
            <span class="timestamp">{{ msg.time }}</span>
          </div>
          <div class="message-body">
            <p>{{ msg.content }}</p>
            <!-- 问题标签 -->
            <div v-if="msg.tags" class="message-tags">
              <el-tag v-for="tag in msg.tags" :key="tag" type="info">
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 候选人消息 -->
      <div v-else class="candidate-message">
        <div class="message-content">
          <div class="message-header">
            <span class="timestamp">{{ msg.time }}</span>
            <span class="response-metrics" v-if="msg.responseTime">
              ⏱️ {{ msg.responseTime }}秒
            </span>
          </div>
          <div class="message-body">
            <p>{{ msg.content }}</p>
          </div>
          <!-- AI反馈 -->
          <div v-if="msg.aiFeedback" class="ai-feedback">
            <span>{{ msg.aiFeedback }}</span>
          </div>
        </div>
        <div class="message-avatar">
          <div class="candidate-avatar">You</div>
        </div>
      </div>
    </div>
    
    <!-- 打字中指示器 -->
    <div v-if="isTyping" class="typing-indicator">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
    
    <!-- 回答分析中 -->
    <div v-if="isProcessing" class="analysis-indicator">
      <p>{{ processingStatusText }}</p>
    </div>
  </div>
  
  <!-- 输入区 -->
  <div class="input-area">
    <!-- 上下文提示 -->
    <div v-if="contextHint" class="context-hint">
      <el-icon><i class="el-icon-info"></i></el-icon>
      <span>{{ contextHint }}</span>
    </div>
    
    <!-- 输入框 -->
    <div class="input-wrapper">
      <el-input
        ref="inputRef"
        v-model="userInput"
        type="textarea"
        :placeholder="dynamicPlaceholder"
        :rows="3"
        :disabled="isProcessing || currentStep < 3"
        @keydown.ctrl.enter="submitMessage"
      />
    </div>
    
    <!-- 控制按钮 -->
    <div class="input-controls">
      <div class="control-hints">
        <span>💡 Ctrl+Enter 快速发送</span>
      </div>
      <div class="control-buttons">
        <el-button
          type="primary"
          @click="submitMessage"
          :loading="isProcessing"
          :disabled="!canSubmit"
        >
          发送回答
        </el-button>
      </div>
    </div>
  </div>
</div>
```

**核心交互流程**：

```javascript
async submitMessage() {
  if (!canSubmit) return
  
  // 1. 记录用户输入
  const userContent = userInput.value.trim()
  const responseStartTime = Date.now()
  
  // 2. 显示用户消息
  messages.push({
    role: 'candidate',
    content: userContent,
    time: formatTime(new Date()),
    responseTime: responseStartTime - lastAIMessageTime
  })
  
  userInput.value = ''
  isProcessing.value = true
  respondedCount.value++
  
  // 3. 调用后端：分析+生成下一题（合并请求）
  const response = await analyzeAndGetNextQuestion({
    candidate_id: parsedCandidateId.value,
    candidate_name: candidateInfo.name,
    candidate_response: userContent,
    conversation_depth: respondedCount.value,
    history: messages,
    target_position: selectedJobTitle.value,
    job_info: {
      id: selectedJobId.value,
      title: selectedJobTitle.value,
      description: "..." // 从岗位详情获取
    },
    resume_info: parsedResumeData.value?.candidate_info || {
      name: candidateInfo.name,
      education: candidateInfo.education,
      skills: candidateInfo.skills
    }
  })
  
  // 4. 处理响应
  if (response.code === 200) {
    const { evaluation, next_question, decision } = response.data
    
    // 4a. 显示AI消息
    isTyping.value = true
    await typewriterEffect(next_question.content)
    isTyping.value = false
    
    messages.push({
      role: 'ai',
      content: next_question.content,
      time: formatTime(new Date()),
      tags: next_question.tags || []
    })
    
    // 4b. 更新评分数据
    if (evaluation.scores) {
      updateScores(evaluation.scores)
    }
    
    // 4c. 更新模式识别
    if (evaluation.patterns) {
      updatePatterns(evaluation.patterns)
    }
    
    // 4d. 检查是否应该结束
    if (decision.should_continue === false) {
      shouldEndInterview.value = true
      // 自动进阶到报告生成
      await new Promise(r => setTimeout(r, 2000))
      completeInterview()
      return
    }
  } else {
    // 4e. 降级处理：使用本地fallback
    const fallbackQuestion = getLocalFallbackQuestion()
    messages.push({
      role: 'ai',
      content: fallbackQuestion,
      time: formatTime(new Date()),
      tags: []
    })
  }
  
  isProcessing.value = false
  lastAIMessageTime = Date.now()
  
  // 5. 自动滚动到底部
  nextTick(() => {
    messageStream.value?.scrollIntoView({ behavior: 'smooth' })
  })
}
```

**数据流动细节**：

```
┌─────────────────────────────────────────┐
│  Step 3: AI 多轮对话                     │
├─────────────────────────────────────────┤
│                                         │
│ 1. startInterview()                     │
│    ├─ startTime = Date.now()           │
│    ├─ 获取第一个问题                   │
│    │  POST /assessment/immersive/      │
│    │    agent/execute                  │
│    │    { operation: "next_question" } │
│    │                                   │
│    │  ← { next_question, tags }       │
│    │                                   │
│    └─ 显示第一个问题                   │
│       messages = [{                    │
│         role: 'ai',                    │
│         content: "你好，...",         │
│         time: "14:30",                 │
│         tags: ["自我介绍"]             │
│       }]                               │
│                                         │
│ 2. 用户输入回答 & submitMessage()      │
│    ├─ messages += [{                  │
│    │   role: 'candidate',             │
│    │   content: "我是...",            │
│    │   time: "14:31"                  │
│    │ }]                                │
│    │                                   │
│    ├─ isProcessing = true              │
│    └─ POST /assessment/immersive/      │
│         agent/execute                  │
│         {                              │
│           operation: "analyze_and_next",
│           candidate_response: "我是...",│
│           conversation_depth: 1,       │
│           history: [消息数组],         │
│           job_info: {...},             │
│           resume_info: {...}           │
│         }                              │
│                                         │
│ 3. 后端处理（3Agent协同）              │
│    ├─ EvaluatorAgent分析回答          │
│    │  提取：评分、情感、模式           │
│    │  返回：{ scores, sentiment,       │
│    │          patterns }               │
│    │                                   │
│    ├─ InterviewerAgent生成下一题      │
│    │  考虑：对话历史、回答质量、       │
│    │       岗位需求                    │
│    │  返回：{ next_question, tags,     │
│    │          suggestions }            │
│    │                                   │
│    └─ DecisionAgent做决策              │
│       考虑：已评估维度数、评分分布、   │
│           对话深度                     │
│       返回：{                          │
│         should_continue: true|false,   │
│         reason: "...",                 │
│         overall_score: 75              │
│       }                                │
│                                         │
│ 4. 前端处理响应                         │
│    ├─ 显示AI消息（带打字效果）        │
│    ├─ 更新 latestScores               │
│    ├─ 更新 detectedPatterns           │
│    ├─ 检查 shouldEndInterview         │
│    ├─ 如果 true → 进阶到 Step 4      │
│    └─ 否则继续对话                    │
│                                         │
│ 5. 循环 2-4 步骤                       │
│    直到满足以下条件之一：              │
│    • shouldEndInterview = true         │
│    • respondedCount > maxRounds (8)    │
│    • 用户手动点击"完成面试"           │
│                                         │
└─────────────────────────────────────────┘
```

#### Step 4: 评估报告生成

**作用**：展示面试结果、人格评分、岗位匹配度分析

**显示内容**：

```vue
<div class="step-4-wrapper report-section">
  <div class="greeting-avatar">
    <img :src="aiInterviewerAvatar" />
  </div>
  <h4>📊 评估报告</h4>
  
  <!-- 加载中 -->
  <div v-if="reportLoading" class="report-loading">
    <el-icon class="is-loading">⏳</el-icon>
    <p>正在生成评估报告，请稍候...</p>
  </div>
  
  <!-- 报告内容 -->
  <div v-else-if="reportData" class="report-detail">
    
    <!-- 面试概览 -->
    <div class="report-card">
      <div class="info-header">📋 面试概览</div>
      <div class="report-stats">
        <div class="stat-item">
          <div class="stat-label">面试时长</div>
          <div class="stat-value">{{ formatDuration(elapsedTime) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">回答题数</div>
          <div class="stat-value">{{ respondedCount }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">匹配度</div>
          <div class="stat-value match-score">
            {{ Math.round(reportData.match_score || 0) }}%
          </div>
        </div>
      </div>
    </div>
    
    <!-- 五大人格评分 -->
    <div class="report-card" v-if="reportData.personality_traits?.length">
      <div class="info-header">🧠 人格特质评估</div>
      <div class="trait-list">
        <div v-for="trait in reportData.personality_traits" :key="trait.name"
          class="trait-row">
          <span class="trait-name">{{ trait.name }}</span>
          <el-progress
            :percentage="(trait.score || 0) * 10"
            :color="getTraitProgressColor(trait.score)"
            :show-text="false"
            :stroke-width="10"
            style="flex: 1; margin: 0 12px;"
          />
          <span class="trait-score">{{ (trait.score || 0).toFixed(1) }}</span>
        </div>
      </div>
    </div>
    
    <!-- 面试表现评分 -->
    <div class="report-card">
      <div class="info-header">⚡ 面试表现评分</div>
      <div class="trait-list">
        <div v-for="(score, name) in latestScores" :key="name"
          class="trait-row">
          <span class="trait-name">{{ name }}</span>
          <el-progress
            :percentage="score * 10"
            :color="getTraitProgressColor(score)"
            :show-text="false"
            :stroke-width="10"
            style="flex: 1; margin: 0 12px;"
          />
          <span class="trait-score">{{ score.toFixed(1) }}</span>
        </div>
      </div>
    </div>
    
    <!-- 核心优势 -->
    <div class="report-card" v-if="reportData.match_analysis?.strengths?.length">
      <div class="info-header">✅ 核心优势</div>
      <ul class="analysis-list">
        <li v-for="(item, idx) in reportData.match_analysis.strengths"
          :key="idx">
          {{ item }}
        </li>
      </ul>
    </div>
    
    <!-- 改进空间 -->
    <div class="report-card" v-if="reportData.match_analysis?.gaps?.length">
      <div class="info-header">📈 改进空间</div>
      <ul class="analysis-list">
        <li v-for="(item, idx) in reportData.match_analysis.gaps"
          :key="idx">
          {{ item }}
        </li>
      </ul>
    </div>
    
    <!-- 专业建议 -->
    <div class="report-card" v-if="reportData.recommendations?.length">
      <div class="info-header">💡 专业建议</div>
      <ul class="analysis-list">
        <li v-for="(item, idx) in reportData.recommendations"
          :key="idx">
          {{ item }}
        </li>
      </ul>
    </div>
    
    <!-- 操作按钮 -->
    <div class="report-actions">
      <el-button type="primary" size="large" @click="finishAndClose">
        ✓ 完成评估
      </el-button>
    </div>
  </div>
</div>
```

**报告生成流程**：

```javascript
async completeInterview() {
  // 1. 汇总评分数据
  const allScores = { ...latestScores.value }
  const personalityScores = getFallbackBigFive(allScores)
  const overallScore = calculateOverallScore(allScores)
  
  // 2. 保存评估结果并生成报告
  reportLoading.value = true
  
  try {
    const response = await saveAssessmentResult({
      candidate_id: parsedCandidateId.value,
      job_id: selectedJobId.value || null,
      assessment_mode: assessmentMode.value,
      all_scores: allScores,
      personality_scores: personalityScores,
      candidate_info: candidateInfo
    })
    
    // 3. 获取完整报告
    if (response.record_id) {
      reportRecordId.value = response.record_id
      
      const reportResponse = await fetchReport(response.record_id)
      
      if (reportResponse.code === 200) {
        reportData.value = reportResponse.data
      }
    }
  } catch (error) {
    // 降级：生成本地报告
    reportData.value = buildLocalReport(personalityScores, overallScore)
  } finally {
    reportLoading.value = false
    currentStep.value = 4
  }
}
```

### 关键状态管理

#### 响应式状态

```typescript
// 流程控制
const currentStep = ref<0|1|2|3|4>(0)        // 当前步骤
const assessmentMode = ref<'job'|'resume'|null>(null)  // 评估模式
const selectedJobId = ref<number|null>(null)  // 选中的岗位
const selectedJobTitle = ref<string>('')      // 岗位名称

// 用户信息
const candidateInfo = ref<CandidateInfo>({
  name: '', email: '', education: '', skills: '', projects: ''
})
const parsedResumeData = ref<any>(null)       // OCR解析结果

// 对话状态
const messages = ref<Message[]>([])           // 对话消息
const userInput = ref<string>('')             // 用户输入框
const isProcessing = ref<boolean>(false)      // 处理中
const isTyping = ref<boolean>(false)          // 打字中

// 评估数据
const latestScores = ref<Record<string, number>>({
  '专业能力': 0, '逻辑思维': 0, ...
})
const detectedPatterns = ref<Pattern[]>([])   // 行为模式
const respondedCount = ref<number>(0)         // 回答数

// 报告数据
const reportData = ref<any>(null)             // 生成的报告
const reportLoading = ref<boolean>(false)     // 报告生成中

// 决策数据
const shouldEndInterview = ref<boolean>(false)  // 是否结束
const latestDecision = ref<any>(null)         // 最新决策
```

#### 计算属性

```typescript
const canSubmit = computed(() => {
  return !isProcessing.value && 
         currentStep.value >= 3 && 
         userInput.value.trim().length > 0
})

const dynamicPlaceholder = computed(() => {
  if (isProcessing.value) return '正在分析中...'
  if (currentStep.value < 3) return '请先完成前置步骤...'
  return '请详细描述你的想法和经验...'
})

const processingStatusText = computed(() => {
  if (respondedCount.value <= 2) 
    return '系统正在提取关键信息并评估作答质量，请稍候...'
  return '系统正在更新评估轨迹并生成下一题，请稍候...'
})
```

### 关键方法

#### 1. startInterview() - 启动面试

```typescript
async function startInterview() {
  try {
    startTime.value = Date.now()
    
    // 获取第一个问题
    const response = await getNextQuestion({
      candidate_id: parsedCandidateId.value,
      role_id: 'hr',
      conversation_depth: 0,
      history: [],
      target_position: selectedJobTitle.value,
      job_info: { id: selectedJobId.value, title: selectedJobTitle.value },
      resume_info: parsedResumeData.value?.candidate_info
    })
    
    if (response.next_question) {
      messages.value.push({
        role: 'ai',
        content: response.next_question.content,
        time: formatTime(new Date()),
        tags: response.next_question.tags || []
      })
      
      currentStep.value = 3
      nextTick(() => inputRef.value?.focus())
    }
  } catch (error) {
    ElMessage.error('启动面试失败，请刷新重试')
  }
}
```

#### 2. analyzeAndGetNextQuestion() - 合并API调用

```typescript
async function analyzeAndGetNextQuestion(payload: {
  candidate_id: string
  candidate_response: string
  conversation_depth: number
  history: Message[]
  job_info: any
  resume_info: any
}) {
  const response = await fetch('/assessment/immersive/agent/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      operation: 'analyze_and_next',
      ...payload
    })
  })
  
  return response.json()
}
```

这个接口的设计目的是：**合并两个操作（分析+生成）为一个API调用**，减少网络往返次数，提高交互流畅度。

---

## 后端 API 接口

### 1. 认证接口

```http
POST /auth/register
Content-Type: application/json

{
  "username": "candidate_001",
  "email": "user@example.com",
  "password": "secure_password",
  "is_hr": false
}

← 201
{
  "code": 200,
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user_id": 123,
    "is_hr": false
  }
}
```

```http
POST /auth/login
Content-Type: application/json

{
  "username": "candidate_001",
  "password": "secure_password"
}

← 200
{
  "code": 200,
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user_id": 123,
    "is_hr": false,
    "username": "candidate_001"
  }
}
```

### 2. 岗位接口

```http
GET /jobs/
Params: category?, city?, salary_min?, salary_max?, limit=20, offset=0

← 200
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "前端工程师",
        "description": "...",
        "company": "ABC公司",
        "city": "杭州",
        "salary_min": 25000,
        "salary_max": 35000,
        "category": "技术岗",
        "required_traits": {
          "extraversion": {"min": 5, "max": 10},
          "conscientiousness": {"min": 6, "max": 10}
        },
        "created_at": "2026-05-01T10:00:00",
        "status": "active"
      }
    ],
    "total": 42,
    "limit": 20,
    "offset": 0
  }
}
```

```http
POST /jobs/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "后端工程师",
  "description": "Python/Go后端开发",
  "company": "XYZ公司",
  "city": "北京",
  "salary_min": 30000,
  "salary_max": 40000,
  "category": "技术岗",
  "required_traits": {
    "conscientiousness": {"min": 7, "max": 10},
    "openness": {"min": 6, "max": 10}
  }
}

← 201
{
  "code": 201,
  "data": {
    "id": 100,
    "name": "后端工程师",
    ...
  }
}
```

### 3. 面试/评估接口

```http
POST /assessment/immersive/agent/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "operation": "analyze_and_next",
  "candidate_id": "123",
  "candidate_name": "张三",
  "candidate_response": "我在之前的项目中...",
  "conversation_depth": 2,
  "history": [
    { "role": "ai", "content": "..." },
    { "role": "candidate", "content": "..." }
  ],
  "target_position": "前端工程师",
  "job_info": {
    "id": 1,
    "title": "前端工程师",
    "description": "..."
  },
  "resume_info": {
    "name": "张三",
    "education": "本科",
    "skills": "JavaScript, Vue.js, Python"
  }
}

← 200
{
  "code": 200,
  "data": {
    "next_question": {
      "content": "你在项目中遇到过什么挑战吗？",
      "tags": ["问题解决", "经验"]
    },
    "evaluation": {
      "scores": {
        "专业能力": 7.5,
        "逻辑思维": 7.0,
        "沟通能力": 8.0
      },
      "sentiment": {
        "emotion": "positive",
        "confidence": 0.85
      },
      "patterns": [
        {
          "id": "p1",
          "name": "系统思维",
          "description": "候选人展现了良好的系统思维",
          "confidence": 0.8
        }
      ]
    },
    "decision": {
      "should_continue": true,
      "reason": "还有评估维度未覆盖",
      "overall_score": 72
    }
  }
}
```

```http
POST /assessment/save-result
Authorization: Bearer <token>
Content-Type: application/json

{
  "candidate_id": "123",
  "job_id": 1,
  "assessment_mode": "job",
  "all_scores": {
    "专业能力": 7.8,
    "逻辑思维": 7.2,
    "沟通能力": 8.1,
    "学习能力": 7.9,
    "团队合作": 7.5,
    "创新思维": 7.3
  },
  "personality_scores": {
    "extraversion": 7.2,
    "agreeableness": 7.8,
    "conscientiousness": 8.0,
    "neuroticism": 3.5,
    "openness": 8.2
  },
  "candidate_info": {
    "name": "张三",
    "email": "zhangsan@company.com",
    "education": "本科",
    "skills": "JavaScript, Vue.js"
  }
}

← 201
{
  "code": 201,
  "data": {
    "record_id": 456,
    "assessment_id": 789,
    "match_score": 78,
    "created_at": "2026-05-10T14:30:00"
  }
}
```

```http
GET /assessment/report/{recordId}
Authorization: Bearer <token>

← 200
{
  "code": 200,
  "data": {
    "record_id": 456,
    "candidate_name": "张三",
    "job_title": "前端工程师",
    "match_score": 78,
    "completed_at": "2026-05-10T14:30:00",
    "duration_seconds": 360,
    "total_rounds": 6,
    
    "personality_traits": [
      { "name": "外向性", "score": 7.2 },
      { "name": "宜人性", "score": 7.8 },
      { "name": "尽责性", "score": 8.0 },
      { "name": "神经质", "score": 3.5 },
      { "name": "开放性", "score": 8.2 }
    ],
    
    "performance_scores": {
      "专业能力": 7.8,
      "逻辑思维": 7.2,
      "沟通能力": 8.1,
      "学习能力": 7.9,
      "团队合作": 7.5,
      "创新思维": 7.3
    },
    
    "match_analysis": {
      "strengths": [
        "技术基础扎实，有深度思考能力",
        "沟通表达清晰，能很好地阐述想法",
        "学习意愿强，对新技术有热情"
      ],
      "gaps": [
        "实战经验可进一步深化",
        "在复杂系统设计方面有提升空间"
      ]
    },
    
    "recommendations": [
      "建议加强系统设计能力的学习",
      "可以参与更多复杂的项目以积累经验",
      "继续保持学习热情和开放心态"
    ]
  }
}
```

### 4. 候选人首页接口

```http
GET /assessment/portrait/{candidateId}
Authorization: Bearer <token>

← 200
{
  "code": 200,
  "data": [
    { "name": "外向性", "score": 7.2 },
    { "name": "宜人性", "score": 7.8 },
    { "name": "尽责性", "score": 8.0 },
    { "name": "神经质", "score": 3.5 },
    { "name": "开放性", "score": 8.2 }
  ]
}
```

```http
GET /assessment/history/{candidateId}
Authorization: Bearer <token>
Params: limit=20, offset=0

← 200
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "job_title": "前端工程师",
        "match_score": 78,
        "created_at": "2026-05-10T14:30:00",
        "assessment_status": "completed"
      },
      {
        "id": 2,
        "job_title": "全栈工程师",
        "match_score": 72,
        "created_at": "2026-05-09T10:15:00",
        "assessment_status": "completed"
      }
    ],
    "total": 5
  }
}
```

```http
GET /assessment/recommended-jobs/{candidateId}
Authorization: Bearer <token>

← 200
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "前端工程师",
        "company": "ABC公司",
        "match_score": 78,
        "reason": "你的技术能力和学习热情与岗位需求高度匹配"
      },
      {
        "id": 3,
        "title": "全栈工程师",
        "company": "DEF公司",
        "match_score": 75,
        "reason": "你的Python和JavaScript技能都很不错"
      }
    ]
  }
}
```

### 5. HR邀请接口

```http
POST /invitation/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "hr_id": 456,
  "candidate_id": 123,
  "job_id": 1,
  "message": "诚邀您参加我们的评估",
  "method": "email"
}

← 201
{
  "code": 201,
  "data": {
    "invitation_id": 789,
    "status": "pending",
    "sent_at": "2026-05-10T15:00:00"
  }
}
```

```http
GET /invitation/list
Authorization: Bearer <token>
Params: status?, limit=20, offset=0

← 200
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 789,
        "candidate_name": "张三",
        "job_title": "前端工程师",
        "status": "pending",
        "sent_at": "2026-05-10T15:00:00"
      }
    ],
    "total": 3
  }
}
```

### 6. HR候选人管理接口

```http
GET /assessment/hr/candidates
Authorization: Bearer <token>
Params: job_id?, status?, limit=20, offset=0

← 200
{
  "code": 200,
  "data": {
    "items": [
      {
        "candidate_id": 123,
        "name": "张三",
        "email": "zhangsan@company.com",
        "job_title": "前端工程师",
        "job_id": 1,
        "assessment_status": "completed",
        "match_score": 78,
        "completed_at": "2026-05-10T14:30:00"
      }
    ],
    "total": 42
  }
}
```

```http
GET /assessment/recommended/{jobId}
Authorization: Bearer <token>

← 200
{
  "code": 200,
  "data": {
    "items": [
      {
        "candidate_id": 234,
        "name": "李四",
        "match_score": 82,
        "source_job": "全栈工程师"
      }
    ]
  }
}
```

### 7. 简历解析接口

```http
POST /assessment/immersive/upload-resume
Content-Type: multipart/form-data

candidate_id: 123
file: <PDF/Word/Image文件>

← 200
{
  "code": 200,
  "data": {
    "candidate_info": {
      "name": "张三",
      "email": "zhangsan@company.com",
      "education": "本科 计算机科学",
      "experience_level": "3-5年",
      "technical_skills": ["JavaScript", "Vue.js", "Python", "Kubernetes"],
      "soft_skills": ["项目管理", "团队合作", "沟通能力"]
    },
    "extraction_method": "ocr" | "text_extract",
    "assessed_dimensions": ["技术能力", "问题解决", "沟通能力", "团队协作"]
  }
}
```

---

## 系统特色与创新

### 1. 多Agent协同评估

**三Agent分工协作**：

- **InterviewerAgent**：负责对话流程，生成动态问题
- **EvaluatorAgent**：分析候选人回答，提取人格特征
- **DecisionAgent**：决策面试进度，判断何时结束

**优势**：
- 各Agent各司其职，提高评估准确性
- 动态调整问题难度和方向
- 科学判断何时停止面试

### 2. 基础人格 + 场景人格双维度评估

**Big Five人格评分**：
- 外向性、宜人性、尽责性、神经质、开放性
- 反映候选人的稳定个性特征

**场景人格评分**：
- 在面试场景中表现出的特定维度
- 技术能力、逻辑思维、沟通能力、团队协作、创新思维
- 反映岗位相关的核心能力

**优势**：
- 全面评估候选人特征
- 提高岗位匹配的准确性

### 3. 岗位模板 + 岗位实例双层设计

**Role Template（岗位模板）**：
- 定义通用的岗位类别（如"前端工程师"）
- 包含该类岗位的通用需求
- 复用性强，便于岗位创建

**Job Instance（岗位实例）**：
- 特定企业/团队的具体岗位
- 包含公司定制化需求
- 与候选人的匹配计算基于实例

### 4. 可解释性报告

**报告内容**：
- 个人心理画像（Big Five评分）
- 面试表现评分（维度得分）
- 与岗位的匹配度百分比
- 核心优势（数据驱动）
- 改进空间（量化分析）
- 专业建议（AI生成）

**优势**：
- 完整的证据链，支持HR决策
- 候选人可理解的反馈
- 降低招聘的主观偏见

### 5. 渐进式评估与本地降级

**渐进式交互**：
- 多步流程，逐步引导用户
- 信息逐层补充，提高准确性

**本地降级**：
- 后端不可用时，前端可生成基础报告
- 确保业务连续性
- 提高系统鲁棒性

---

## 总结

本系统通过**前后端分离、多Agent协同、双维度评估、可解释性输出**等创新设计，实现了一个**智能化、科学化、可信的人岗匹配评估平台**。

**核心价值**：
- **智能化**：AI面试官替代部分人工
- **客观化**：心理学模型支撑的科学评估
- **可解释性**：完整的评估证据和建议
- **用户友好**：沉浸式、多步引导的交互

**技术亮点**：
- 三Agent协同的智能决策
- OCR + LLM的简历智能解析
- 大五人格模型 + 场景维度的双维度评估
- 本地降级机制确保系统容错性

