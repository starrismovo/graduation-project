# 第三章 系统需求分析与总体架构设计

本章分析系统的功能需求与非功能需求，阐述总体架构设计与核心模块划分，为后续的方法设计与实现提供基础支撑。

---

## 3.1 系统目标与设计原则

### 3.1.1 系统目标

系统的总体目标是构建一个面向招聘评估场景的 AI 多智能体心理特质评估与人岗匹配系统（Assessment System for Intelligent Talent Evaluation and Job Matching, AITEJM）。系统需要实现以下三个子目标：

1. **完整的多维评估**：通过多个 AI 智能体的协同评估，从专业能力、沟通与稳定性、岗位适配与发展潜力等多个维度对候选人进行系统评估，克服传统单一面试官的主观性与维度不足问题。

2. **科学的心理特质刻画**：基于大五人格理论构建分层人格模型，将候选人的人格特质分为基础人格（稳定特征）与场景人格（情境相关特征），为人岗匹配提供更精细的心理基础。

3. **精准的人岗匹配支持**：通过岗位模板与岗位实例的双层建模，实现岗位需求的通用表示与个性化刻画，为候选人与企业提供基于多维特征的科学匹配建议。

### 3.1.2 设计原则

系统的设计遵循以下原则：

**原则 1：可解释性优先**

系统的每一个关键决策都应该能够向用户清晰地说明理由。即使是复杂的人格推断或匹配计算，也应该能追溯到原始的面试证据。这不仅提升了系统的可信度，也便于用户对结果进行质证与反馈。

**原则 2：一致性与稳定性保证**

系统应该通过工程机制（如后端集中计算、会话隔离、统一标识）确保评估过程与结果的一致性。同一候选人的重复评估应该得到基本一致的结果，不同会话间的数据应该完全隔离，不存在污染或串扰。

**原则 3：模块化与可扩展性**

系统的各个模块（多 Agent 协同、人格评估、岗位建模、匹配计算）应该相对独立，便于后续的替换、升级或扩展。例如，大语言模型服务的升级不应影响人格计算逻辑；新的岗位类别的加入不应改变系统架构。

**原则 4：用户导向**

系统的设计应该从候选人与企业的实际需求出发。前端交互应该简洁直观，专业术语应该有清晰解释，最终的报告应该既有学术严谨性，也有实践可操作性。

---

## 3.2 功能需求分析

### 3.2.1 用户角色与需求

系统有三类主要用户角色，各有不同的功能需求：

**角色 1：候选人（Candidate）**

用户故事：
> "作为一个求职候选人，我想通过参与多轮结构化面试，获得关于自己的心理特质与岗位适配度的详细报告，这样我可以更全面地了解自己，也能提升求职的针对性。"

需求清单：
- 注册/登录系统
- 浏览岗位列表与岗位详情
- 参与多 Agent 面试评估流程
- 查看个人的心理特质画像（基础人格评分）
- 查看与特定岗位的适配度分析与建议
- 查看历史评估记录

**角色 2：企业招聘人员/HR（HR User）**

用户故事：
> "作为企业的 HR，我希望能够系统地评估候选人，并获得一份既有量化评分又有定性分析的综合报告，这样我可以在招聘委员会中用数据支持我的推荐意见。"

需求清单：
- 创建/编辑岗位（岗位模板与岗位实例）
- 发布招聘公告
- 邀请候选人参与评估
- 查看系统生成的候选人评估报告
- 对比多个候选人的评估结果
- 导出评估数据用于后续分析
- 给出候选人反馈



### 3.2.2 核心功能模块

系统包含以下六大核心功能模块：

**模块 1：用户与身份管理**

功能：
- 用户注册/登录/登出
- 身份验证与权限管理
- 用户角色与权限配置
- 个人信息管理

**模块 2：岗位与招聘管理**

功能：
- 岗位模板的创建与维护
- 岗位实例的创建与发布
- 招聘公告的管理
- 岗位与候选人的关联管理

**模块 3：多 Agent 协同面试引擎**

功能：
- 评估会话的创建与管理
- 三个 Agent（技术、HR、用人主管）的问题生成与评分
- 问答历史的记录与追踪
- 会话级的数据隔离与管理

**模块 4：人格特质评估与建模**

功能：
- 候选人的基础人格推断与评分
- 岗位情景下的场景人格推断
- 人格维度的量化与可视化
- 人格评分历史的管理

**模块 5：人岗匹配评估**

功能：
- 候选人特征与岗位需求的对标分析
- 多维度匹配度计算
- 岗位推荐与候选人推荐
- 匹配分析的可解释性生成

**模块 6：报告生成与展示**

功能：
- 综合评估报告的自动生成
- 心理特质画像的可视化
- 匹配度分析的图表展示
- 报告的导出与分享

### 3.2.3 用户交互流程

**候选人的评估流程**

```
1. 岗位浏览
   候选人登录 → 浏览岗位列表 → 查看岗位详情
   
2. 参与评估
   选择感兴趣的岗位 → 点击"开始评估"
   → 进入多 Agent 面试流程
   
3. 多轮问答
   第1轮：技术 Agent 提问 (2-3 个技术问题)
   第2轮：HR Agent 提问 (2-3 个沟通/协作问题)
   第3轮：用人主管 Agent 提问 (2-3 个岗位适配问题)
   
4. 查看报告
   评估完成 → 系统自动生成报告
   → 查看心理特质画像、匹配度分析、专业建议
```

**企业 HR 的招聘流程**

```
1. 岗位发布
   创建岗位模板 (一次性)
   → 创建岗位实例 (针对具体招聘轮次)
   → 发布招聘公告
   
2. 候选人邀请与评估
   搜索/邀请候选人 
   → 候选人参与评估
   → 系统自动生成评估报告
   
3. 结果分析
   查看单个报告 (心理画像、匹配度)
   → 对比多个候选人的报告
   → 根据报告给出录用建议
```

---

## 3.3 非功能需求分析

### 3.3.1 性能需求

**响应时间**

- 页面加载：< 2 秒
- API 调用平均响应时间：< 2 秒
- 面试问题生成：< 5 秒
- 报告生成：< 10 秒

**吞吐量**

- 支持并发评估会话数：≥ 10
- 单台后端服务器的 QPS（查询/秒）：≥ 100

**数据库性能**

- 单条记录查询时间：< 100 ms
- 批量查询（100 条记录）：< 500 ms

### 3.3.2 可靠性需求

**系统可用性**

- 系统在线时间：≥ 99%
- 数据备份频率：每日至少一次
- 数据恢复时间：≤ 1 小时

**数据一致性**

- 重复测试结果的相关系数：≥ 0.95
- 会话间数据隔离完整性：100%
- 数据库事务一致性：ACID 保证

**错误处理**

- 系统异常时的用户提示：明确、友好
- 错误日志记录：完整、可追踪
- 故障自动恢复机制

### 3.3.3 安全需求

**身份验证与授权**

- 支持用户名/密码登录
- 密码加密存储（SHA-256 或更强）
- 会话管理与超时控制
- 基于角色的访问控制（RBAC）

**数据安全**

- 敏感数据加密存储（如密码、个人隐私信息）
- API 通信采用 HTTPS
- 数据库访问采用最小权限原则

**审计与合规**

- 记录所有用户操作日志
- 评估过程的完整追踪与审计链
- 符合数据保护法规要求（如 GDPR）

### 3.3.4 可维护性与可扩展性需求

**代码质量**

- 模块化设计，低耦合高内聚
- API 文档完整，代码注释清晰
- 单元测试覆盖率 ≥ 80%

**可扩展性**

- 支持新岗位类别的快速添加
- 支持新的 Agent 角色的集成
- 支持大语言模型的切换与升级
- 支持数据库的扩容与迁移

**运维友好**

- 系统配置参数化，便于调整
- 日志系统完整，便于问题诊断
- 监控系统完善，实时告警

---

## 3.4 总体架构设计

### 3.4.1 架构风格与分层

系统采用"前后端分离 + 分层架构"的设计模式。整体划分为三层：

**第一层：展示层（Presentation Layer）**

技术栈：Vue 3 + TypeScript + Element Plus

职责：
- 提供用户交互界面
- 处理用户输入与输出展示
- 调用 API 进行业务操作

模块：
- 岗位浏览与详情
- 评估流程页面（多个步骤）
- 报告展示
- 用户信息管理

**第二层：业务逻辑层（Business Logic Layer）**

技术栈：FastAPI + Python

职责：
- 实现系统的核心业务逻辑
- 协调多个数据模块的交互
- 调用 LLM 服务进行文本分析与评估

模块：
- 用户服务（认证、授权、信息管理）
- 岗位服务（岗位 CRUD、模板管理）
- 评估服务（会话管理、Agent 协调）
- 人格评估服务（人格计算、建模）
- 匹配服务（人岗匹配计算）
- 报告服务（报告生成、数据聚合）

**第三层：数据访问层（Data Access Layer）**

技术栈：SQLAlchemy ORM + MySQL

职责：
- 定义数据模型
- 提供数据 CRUD 操作
- 确保数据的持久化与一致性

模块：
- 用户数据
- 岗位与招聘数据
- 评估会话与问答数据
- 人格评分数据
- 匹配结果数据

### 3.4.2 系统总体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    前端应用层 (Vue 3)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ 岗位列表 │  │ 评估流程 │  │ 报告展示 │  │ 用户管理 │ │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘ │
│        └───────────┬─────────────────┬──────────────┘     │
│                    │                 │                     │
│        ┌───────────▼─────────────────▼────────────┐       │
│        │      API 调用层 (request.ts)              │       │
│        └───────────┬─────────────────┬────────────┘       │
│                    │                 │                     │
└────────────────────┼─────────────────┼──────────────────────┘
                     │ HTTP/REST       │
                     ▼                 ▼
┌──────────────────────────────────────────────────────────┐
│              后端应用层 (FastAPI)                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              路由层 (routers/)                   │   │
│  │  ├─ /auth (认证)                                │   │
│  │  ├─ /users (用户管理)                           │   │
│  │  ├─ /jobs (岗位管理)                            │   │
│  │  ├─ /assessment (评估管理)                      │   │
│  │  ├─ /interview (多Agent面试)                    │   │
│  │  └─ /report (报告生成)                          │   │
│  └──────────────┬────────────────────────────────┘   │
│                 │                                      │
│  ┌──────────────▼────────────────────────────────┐   │
│  │           业务逻辑层 (services/)               │   │
│  │  ├─ UserService                               │   │
│  │  ├─ JobService                                │   │
│  │  ├─ AssessmentService                         │   │
│  │  ├─ PersonalityService                        │   │
│  │  ├─ MatchingService                           │   │
│  │  └─ ReportService                             │   │
│  └──────────────┬────────────────────────────────┘   │
│                 │                                      │
│  ┌──────────────▼────────────────────────────────┐   │
│  │           LLM 集成层 (utils/llm.py)           │   │
│  │  ├─ 文本分析与特征提取                        │   │
│  │  ├─ 问题生成                                  │   │
│  │  ├─ 人格推断                                  │   │
│  │  └─ 可解释性文本生成                          │   │
│  └──────────────┬────────────────────────────────┘   │
│                 │                                      │
│  ┌──────────────▼────────────────────────────────┐   │
│  │           数据访问层 (models/)                 │   │
│  │  ├─ User                                      │   │
│  │  ├─ Job, Role                                 │   │
│  │  ├─ AssessmentSession                         │   │
│  │  ├─ TraitScores                               │   │
│  │  ├─ EvaluationResult                          │   │
│  │  └─ Dialogue History                          │   │
│  └──────────────┬────────────────────────────────┘   │
│                 │                                      │
└─────────────────┼──────────────────────────────────────┘
                  │ ORM/SQL
                  ▼
┌──────────────────────────────────────────────────────────┐
│              数据库层 (MySQL 8.0)                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ├─ users (用户表)                                     │
│  ├─ roles (岗位模板表)                                │
│  ├─ jobs (岗位实例表)                                 │
│  ├─ assessment_sessions (评估会话表)                  │
│  ├─ dialogue_history (对话历史表)                     │
│  ├─ trait_scores (人格评分表)                         │
│  ├─ evaluation_results (评估结果表)                   │
│  └─ [其他支撑表...]                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 3.5 核心数据模型设计

### 3.5.1 关键实体与关系

系统的核心数据模型包括以下七类实体：

**实体 1：User（用户）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| username | String | 用户名 |
| email | String | 邮箱 |
| user_type | Enum | 用户类型 (candidate/hr) |
| hashed_password | String | 密码哈希 |
| created_at | DateTime | 创建时间 |

**实体 2：Role（岗位模板）**

| 字段 | 类型 | 说明 |
|------|------|------|
| role_id | UUID | 主键 |
| role_name | String | 岗位名称 (如"后端工程师") |
| role_category | String | 岗位类别 |
| required_skills | JSON | 必需技能列表 |
| personality_requirements | JSON | 人格需求 (Big Five) |
| work_environment | JSON | 工作环境特征 |

**实体 3：Job（岗位实例）**

| 字段 | 类型 | 说明 |
|------|------|------|
| job_id | UUID | 主键 |
| role_id | FK | 关联的岗位模板 |
| company_name | String | 公司名称 |
| job_title | String | 具体职位 |
| job_description | Text | 岗位描述 |
| adjustments | JSON | 相对模板的调整项 |
| created_by | FK | HR 创建者 |
| created_at | DateTime | 发布时间 |

**实体 4：AssessmentSession（评估会话）**

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | UUID | 主键 (会话隔离) |
| candidate_id | FK | 候选人 |
| job_id | FK | 岗位实例 |
| status | Enum | 会话状态 (ongoing/completed/abandoned) |
| created_at | DateTime | 开始时间 |
| completed_at | DateTime | 完成时间 |

**实体 5：DialogueHistory（对话历史）**

| 字段 | 类型 | 说明 |
|------|------|------|
| dialogue_id | UUID | 主键 |
| session_id | FK | 关联的会话 |
| agent_type | String | Agent 类型 (technical/hr/manager) |
| question | Text | 问题 |
| answer | Text | 候选人回答 |
| timestamp | DateTime | 时间戳 |

**实体 6：TraitScores（人格评分）**

| 字段 | 类型 | 说明 |
|------|------|------|
| score_id | UUID | 主键 |
| session_id | FK | 关联的会话 |
| candidate_id | FK | 候选人 |
| basic_traits | JSON | 基础人格评分 {extroversion, agreeableness, ...} |
| scenario_traits | JSON | 场景人格评分（针对特定岗位） |
| agent_source | String | 来源 Agent |
| timestamp | DateTime | 计算时间 |

**实体 7：EvaluationResult（评估结果）**

| 字段 | 类型 | 说明 |
|------|------|------|
| result_id | UUID | 主键 |
| session_id | FK | 关联的会话 |
| candidate_id | FK | 候选人 |
| job_id | FK | 岗位 |
| match_score | Float | 综合匹配度 (0-100) |
| ability_scores | JSON | 各能力维度评分 |
| trait_comparison | JSON | 基础人格/场景人格 vs 岗位需求 |
| strengths | Text | 优势分析 |
| gaps | Text | 改进空间 |
| recommendations | Text | 个性化建议 |
| report_content | JSON | 完整报告内容 |
| created_at | DateTime | 生成时间 |

### 3.5.2 关系图

```
User (用户)
├── is_candidate_of ──→ AssessmentSession
└── is_hr_of ──────────→ Job

Role (岗位模板)
└── is_instance_of ────→ Job (1:N)

Job (岗位实例)
├── created_by ────────→ User (HR)
├── based_on ──────────→ Role
├── has ───────────────→ AssessmentSession (1:N)
└── evaluated_in ──────→ EvaluationResult (1:N)

AssessmentSession (评估会话)
├── for_candidate ────→ User
├── for_job ──────────→ Job
├── has_dialogues ────→ DialogueHistory (1:N)
├── has_scores ───────→ TraitScores (1:N)
└── produces ─────────→ EvaluationResult (1:1)

DialogueHistory
└── belongs_to ───────→ AssessmentSession

TraitScores
├── belongs_to ───────→ AssessmentSession
└── for_candidate ────→ User

EvaluationResult
└── from_session ─────→ AssessmentSession
```

---

## 3.6 端到端评估流程设计

### 3.6.1 系统流程总览

```
                    ┌─ 审批 ─ HR 发布招聘 ─┐
                    │                     │
HR 创建岗位模板      │                     ▼
      │             │              候选人浏览岗位
      ▼             │              候选人选择参与
  Role Template    │                     │
      │             │                     ▼
      ▼             │          ┌─ 创建 Assessment_Session
  Job Instance ◄───┘           │ (会话隔离)
                               │
                               ▼
                     ┌─ 技术 Agent 对话 ┐
                     │    (2-3 轮)    │
                     ├─ HR Agent 对话    ├─ 累积评分与证据
                     │    (2-3 轮)    │
                     ├─ 主管 Agent 对话 ┤
                     │    (2-3 轮)    │
                     └─ 后端集中人格计算 ┘
                               │
                               ▼
                    ┌─ 融合多源评分 ──┐
                    │ 计算人岗匹配度   ├─ 生成 EvaluationResult
                    │ 生成解释文本    │
                    └──────────┬──────┘
                               │
                               ▼
                    ┌─ 前端展示报告 ──┐
                    │  候选人查看     │
                    │  HR 查看与导出   │
                    └────────────────┘
```

### 3.6.2 核心数据流

**阶段 1：会话初始化**

```
[Input]
candidate_id, job_id, basic_info (学历、经历等)

[Processing]
1. 创建 AssessmentSession (session_id 生成)
2. 加载 Job 信息 + 关联的 Role 模板
3. 初始化 Agent 上下文

[Output]
session_id, job_context, ready_to_start = true
```

**阶段 2：多 Agent 问答**

```
[Loop] 对每个 Agent (按顺序: 技术 → HR → 主管)

[Input]
session_id, agent_type, candidate_context, job_context

[Agent Processing]
1. 基于岗位需求生成问题
2. 等待候选人回答
3. 分析回答，提取能力特征
4. 进行实时评分

[Recording]
INSERT DialogueHistory(session_id, agent_type, question, answer, ...)
UPDATE TraitScores(session_id, agent_source, interim_traits, ...)

[Output]
next_agent (或 evaluation_ready = true)
```

**阶段 3：后端集中计算**

```
[Input]
session_id (所有中间结果已保存)

[Processing]
1. 查询 TraitScores (所有 Agent 的评分)
2. 融合三个 Agent 的评分 → 综合人格评分
3. 推断场景人格 (基于 job_context)
4. 计算人岗匹配度
   - 能力匹配度
   - 人格匹配度
   - 期待匹配度
   - → 综合匹配度

[Storage]
INSERT EvaluationResult(
  session_id, candidate_id, job_id,
  match_score, trait_comparison, ...,
  created_at = NOW()
)

[Output]
result_id, evaluation_data
```

**阶段 4：报告生成与展示**

```
[Input]
result_id (包含完整的评估数据)

[Processing]
1. 可解释性链路生成
   - 决策链路追踪
   - 维度级解释
   - 证据引用
   - 综合建议
2. 报告模板渲染
   - 数据可视化 (雷达图、柱状图)
   - 文本总结

[Output]
report_json, report_html

[Frontend Rendering]
- 心理特质画像展示
- 匹配度分析
- 可解释性详情
```

---

## 3.7 模块划分与职责

### 3.7.1 后端模块结构

```
backend/
├── main.py                          # 应用入口
├── config.py                        # 配置管理
├── database.py                      # 数据库连接
│
├── models/                          # 数据模型
│   ├── __init__.py
│   ├── user.py                     # User 实体
│   ├── job.py                      # Role, Job 实体
│   ├── assessment.py               # 评估相关实体
│   └── trait.py                    # TraitScores 实体
│
├── schemas/                         # 数据验证与序列化
│   ├── user_schema.py
│   ├── job_schema.py
│   ├── assessment_schema.py
│   └── trait_schema.py
│
├── routers/                         # API 路由
│   ├── auth.py                     # 认证相关
│   ├── users.py                    # 用户管理
│   ├── jobs.py                     # 岗位管理
│   ├── assessment.py               # 评估会话管理
│   ├── interview.py                # 多Agent面试
│   └── report.py                   # 报告生成
│
├── services/                        # 业务逻辑
│   ├── user_service.py
│   ├── job_service.py
│   ├── assessment_service.py       # 会话管理
│   ├── personality_service.py      # 人格计算
│   ├── matching_service.py         # 人岗匹配
│   └── report_service.py           # 报告生成
│
├── utils/                           # 工具模块
│   ├── llm_client.py               # LLM 调用
│   ├── text_processing.py          # 文本处理
│   ├── feature_extraction.py       # 特征提取
│   ├── personality_calculator.py   # 人格计算 (后端)
│   └── matching_algorithm.py       # 匹配算法
│
├── middleware/                      # 中间件
│   ├── auth_middleware.py          # 身份认证
│   └── error_handler.py            # 错误处理
│
└── tests/                           # 单元测试
    ├── test_user_service.py
    ├── test_personality_calculation.py
    └── ...
```

### 3.7.2 前端模块结构

```
frontend/
├── src/
│   ├── main.ts                      # 应用入口
│   ├── App.vue                      # 根组件
│   │
│   ├── views/                       # 页面组件
│   │   ├── HomeView.vue            # 首页（岗位列表）
│   │   ├── JobDetailView.vue       # 岗位详情
│   │   ├── AssessmentView.vue      # 评估流程（多步骤）
│   │   ├── ReportView.vue          # 报告展示
│   │   └── UserProfileView.vue     # 用户信息
│   │
│   ├── components/                  # 组件
│   │   ├── MultiAgentInterview.vue # 多Agent面试引擎
│   │   ├── PersonalityRadar.vue    # 人格雷达图
│   │   ├── MatchingAnalysis.vue    # 匹配度分析
│   │   ├── ReportGenerator.vue     # 报告生成
│   │   └── ...
│   │
│   ├── router/                      # 路由配置
│   │   └── index.ts
│   │
│   ├── utils/                       # 工具
│   │   ├── request.ts              # API 调用
│   │   ├── storage.ts              # 本地存储
│   │   └── ...
│   │
│   └── styles/                      # 样式
│       ├── main.css
│       └── ...
│
└── package.json
```

---

## 3.8 本章小结

本章从需求与架构层面阐述了系统的整体设计：

1. **需求分析**：明确了三类用户（候选人、HR、管理员）的需求，定义了六大核心功能模块，为系统设计奠定基础。

2. **架构设计**：采用"前后端分离 + 分层架构"的模式，将系统划分为展示层、业务逻辑层、数据访问层，清晰地分离了关注点。

3. **数据模型**：设计了七类核心实体（User、Role、Job、AssessmentSession、DialogueHistory、TraitScores、EvaluationResult），通过明确的关系定义支撑系统的业务流程。

4. **流程设计**：阐述了从会话初始化、多 Agent 问答、后端集中计算到报告生成的端到端流程，强调了会话隔离、后端集中计算对系统一致性的保证。

这个架构为第四章的方法设计与第五章的实现细节提供了坚实的基础支撑。

