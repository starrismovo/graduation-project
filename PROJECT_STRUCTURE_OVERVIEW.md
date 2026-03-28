# 项目结构全面概览（2026年3月28日）

## 📊 1. 数据模型（Backend Models）

### 核心模型位置
`backend/models/` 目录下包含以下核心模型：

#### **1.1 User 模型** (`models/user.py`)
**用途**：统一用户管理（候选人和HR）
- **主要字段**：
  - `id`：主键
  - `username`, `email`, `hashed_password`：认证信息
  - `user_type`：用户类型（`HR` | `CANDIDATE`）
  - `real_name`, `nickname`, `avatar_url`：个人资料
  - `age`, `education`, `major`, `desired_job`, `experience_years`：候选人专属字段
  - `skills`：JSON格式的技能列表
  - `resume_url`：简历路径
  - `delivery_privacy`：隐私设置（1=实名, 2=昵称, 3=匿名）

- **关系**：
  - ↔ Jobs（一对多）
  - ↔ Interviews（一对多）
  - ↔ AssessmentRecords（一对多）
  - ↔ CandidatePersonalityProfile（一对一）
  - ↔ InterviewResponses（一对多）

#### **1.2 Job 模型** (`models/job.py`)
**用途**：岗位/职位管理
- **主要字段**：
  - `id`：主键
  - `name`：岗位名称（如"前端开发工程师"）
  - `description`：岗位描述
  - `company`：公司名称
  - `category`：岗位类别（技术岗、产品岗、设计岗等）
  - `city`：工作地点
  - `salary_min`, `salary_max`：薪资范围（单位：k）
  - **`required_traits`**：大五人格预期值（JSON格式）
  - `creator_id`：创建者（HR的user_id）

- **关系**：
  - ← User（多对一，creator）
  - ↔ Interviews（一对多）
  - ↔ EvaluationFramework（一对一）

- **示例岗位及其人格要求**：
  ```python
  # 前端开发工程师
  {"openness": 8, "conscientiousness": 8, "extraversion": 7, 
   "agreeableness": 6, "neuroticism": 3}
  
  # 后端开发工程师
  {"openness": 7, "conscientiousness": 9, "extraversion": 5,
   "agreeableness": 6, "neuroticism": 2}
  
  # 产品经理
  {"openness": 9, "conscientiousness": 8, "extraversion": 8,
   "agreeableness": 7, "neuroticism": 3}
  ```

#### **1.3 Assessment & Personality Models**

##### **CandidatePersonalityProfile** (`models/assessment.py`)
**用途**：存储候选人的大五人格评估结果
- **主要字段**：
  - `id`, `candidate_id`：主键与候选人关联
  - **`trait_openness`**：开放性（0-10）
  - **`trait_conscientiousness`**：尽责性（0-10）
  - **`trait_extraversion`**：外向性（0-10）
  - **`trait_agreeableness`**：宜人性（0-10）
  - **`trait_neuroticism`**：神经质（0-10）
  - `created_at`, `updated_at`：时间戳
  - `is_deleted`, `deleted_at`：软删除

- **方法**：
  - `to_big_five_list()`：返回格式化的大五人格列表及分数

##### **AssessmentRecord** (`models/assessment.py`)
**用途**：评估历史记录
- **主要字段**：
  - `candidate_id`, `job_id`：关联候选人和岗位
  - `job_title`：岗位名称快照
  - `match_score`：匹配度
  - `assessment_status`：评估状态
  - `assessment_mode`：评估模式
  - `created_at`, `updated_at`

##### **PersonalityTraitDescription** (`models/assessment.py`)
**用途**：人格特质描述
- 存储每个特质的详细描述和分析

#### **1.4 EvaluationFramework 模型** (`models/evaluation_framework.py`)
**用途**：定义每个岗位的大五人格评估标准和权重
- **主要字段**：
  - `id`, `job_id`：主键与岗位关联
  - **`target_traits`**：目标特质值（JSON）
  ```python
  {
    "openness": 0.7,
    "conscientiousness": 0.8,
    "extraversion": 0.6,
    "agreeableness": 0.7,
    "neuroticism": 0.4
  }
  ```
  - **`trait_weights`**：权重配置（JSON）
  ```python
  {
    "openness": 0.15,
    "conscientiousness": 0.25,
    "extraversion": 0.20,
    "agreeableness": 0.20,
    "neuroticism": 0.20
  }
  ```
  - `created_at`, `updated_at`

#### **1.5 Interview 模型** (`models/interview.py`)
**用途**：面试记录
- **主要字段**：
  - `candidate_id`, `job_id`：关联候选人和岗位
  - `status`：面试状态（started/in_progress/completed/passed/failed/withdrawn）
  - **`personality_traits`**：面试评估的大五人格得分（JSON）
  - `match_score`：匹配度
  - `created_at`, `completed_at`, `updated_at`

#### **1.6 其他模型**
- `Conversation` (`models/conversation.py`)：对话记录
- `InterviewerRole` (`models/interviewer_role.py`)：面试官角色
- `HRAgent` (`models/hr_agent.py`)：HR代理配置

---

## 🛣️ 2. API 路由结构（Backend Routers）

### 路由文件位置
`backend/routers/` 目录下的路由分布：

#### **2.1 认证路由** (`routers/auth.py`)
```
POST   /api/auth/register          # 用户注册
POST   /api/auth/login             # 用户登录
```

#### **2.2 用户路由** (`routers/user.py`)
```
GET    /api/users/profile          # 获取用户资料
PATCH  /api/users/profile          # 更新用户资料
POST   /api/users/avatar           # 上传头像
DELETE /api/users/assessments      # 删除评估历史
```

#### **2.3 候选人路由** (`routers/candidate.py`)
```
POST   /api/candidates/{candidate_id}/basic-info     # 保存基本信息
GET    /api/candidates/{candidate_id}/basic-info     # 获取基本信息
```

#### **2.4 岗位路由** (`routers/job.py`) ⭐ 重要
```
POST   /jobs/                                      # 创建岗位（HR）
GET    /jobs/                                      # 获取岗位列表
GET    /jobs/{job_id}                              # 获取岗位详情
GET    /jobs/recommended/cards                     # 推荐岗位卡片
GET    /jobs/stats/candidate                       # 候选人面试统计
GET    /jobs/home/data                             # 首页数据
```

#### **2.5 评估路由** (`routers/assessment.py`) ⭐ 核心
```
评估相关：
GET    /assessment/portrait/{candidate_id}         # 获取心理画像（大五人格结果）
GET    /assessment/history/{candidate_id}          # 评估历史记录
GET    /assessment/recommended-jobs/{candidate_id} # 推荐岗位
GET    /assessment/report/{record_id}              # 评估报告详情

记录管理：
POST   /assessment/records                         # 创建评估记录
PATCH  /assessment/records/{record_id}             # 更新评估记录
DELETE /assessment/records/{record_id}             # 删除评估记录

沉浸式对话：
POST   /assessment/immersive/next-question         # 获取下一个问题
POST   /assessment/immersive/analyze-response      # 分析回答
POST   /assessment/immersive/save-session          # 保存session
```

#### **2.6 面试路由** (`routers/interview.py`)
```
POST   /interviews/                                # 创建面试
GET    /interviews/{interview_id}                  # 获取面试详情
GET    /interviews/candidate/{candidate_id}       # 获取候选人的面试
PUT    /interviews/{interview_id}                  # 更新面试
DELETE /interviews/{interview_id}                  # 删除面试
```

#### **2.7 面试官路由** (`routers/interviewer.py`) ⭐ 沉浸式对话
```
面试官管理：
GET    /interviewer/interviewers                   # 获取所有面试官
POST   /interviewer/session/create                 # 创建面试session

对话交互：
POST   /interviewer/chat/stream                    # 流式对话
POST   /interviewer/interviewer/switch             # 切换面试官
GET    /interviewer/session/{session_id}/state     # 获取session状态
POST   /interviewer/session/{session_id}/next-round# 下一轮
GET    /interviewer/session/{session_id}/summary   # 面试总结
POST   /interviewer/evaluate/background            # 背景评估
WebSocket /interviewer/ws/chat/{session_id}       # WebSocket实时对话
```

#### **2.8 HR代理路由** (`routers/hr_agent.py`)
```
GET    /hr_agent/scenarios/{scenario_id}           # 获取场景
GET    /hr_agent/scenarios                         # 获取所有场景
POST   /hr_agent/follow-up-question                # 后续问题
POST   /hr_agent/score-answer                      # 评分回答
POST   /hr_agent/save-response                     # 保存回答
GET    /hr_agent/scenario-summary/{candidate_id}/{scenario_id}  # 场景总结
```

#### **2.9 沉浸对话路由** (`routers/immersive_dialogue.py`)
```
问题流程：
POST   /immersive_dialogue/next-question           # 获取下一个问题
POST   /immersive_dialogue/analyze-response        # 分析回答
POST   /immersive_dialogue/save-session            # 保存session

角色和配置：
GET    /immersive_dialogue/roles                   # 获取所有角色
GET    /immersive_dialogue/role/{role_id}          # 获取角色详情
GET    /immersive_dialogue/assessment-phases       # 获取评估阶段

会话管理：
GET    /immersive_dialogue/candidate/{candidate_id}/sessions  # 候选人会话列表
GET    /immersive_dialogue/session/{session_id}/details       # 会话详情

简历处理：
POST   /immersive_dialogue/parse-resume            # 解析简历
POST   /immersive_dialogue/upload-resume           # 上传简历
```

---

## 🎨 3. 前端 UI 组件和页面结构

### 前端目录结构
`frontend/src/` 内容：

#### **3.1 页面（Views）** - `src/views/`

##### 主要页面：
```
views/
├── HomePage.vue / IndexView.vue          # 首页
├── LoginView.vue                         # 登录页
├── ProfileView.vue                       # 个人资料页
├── HomeView.vue / HRHomeView.vue         # 首页/HR首页
├── AssessmentView.vue                    # 评估页面
├── position/
│   ├── JobManageView.vue                # 岗位管理（HR）
│   └── JobEditView.vue                  # 岗位编辑
├── assessment/
│   ├── BasicInfo.vue                    # 基本信息表单
│   ├── ReportPage.vue                   # 评估报告页面
│   ├── ImmersiveRoleDialogue.vue        # 沉浸式对话
│   └── components/                      # 评估相关子组件
```

#### **3.2 组件（Components）** - `src/components/`
```
components/
├── AssessmentHistory.vue                 # 评估历史组件
├── EmptyState.vue                        # 空状态提示
├── JobCard.vue                           # 岗位卡片（显示岗位基本信息）
├── RadarChart.vue                        # 雷达图（显示大五人格结果）
├── UploadInfoDialog.vue                  # 信息上传对话框
├── VirtualInterviewerChat.vue            # 虚拟面试官聊天组件
└── HelloWorld.vue                        # Demo组件
```

#### **3.3 其他前端模块** - `src/`
```
src/
├── api/                                  # API调用层
├── router/                               # 路由配置
├── stores/                               # Pinia状态管理
├── types/                                # TypeScript类型定义
├── utils/                                # 工具函数
├── assets/                               # 静态资源
├── App.vue                               # 根组件
└── main.ts                               # 入口文件
```

---

## 🧠 4. 大五人格（Big Five）相关代码

### 4.1 模型支持
- **主表**：`CandidatePersonalityProfile` 表
  - 存储5个浮点字段（0-10分）：`trait_openness`, `trait_conscientiousness`, `trait_extraversion`, `trait_agreeableness`, `trait_neuroticism`
  
- **岗位要求**：`Job` 表的 `required_traits` (JSON字段)
  - 每个岗位定义期望的大五人格值

- **评估框架**：`EvaluationFramework` 表
  - `target_traits`：目标值
  - `trait_weights`：权重配置

### 4.2 API 端点（获取和更新大五人格）
```
GET  /assessment/portrait/{candidate_id}
     ↓ 返回 CandidatePersonalityProfile 的5个trait分数

POST /assessment/immersive/save-session
     ↓ 评估完成后保存结果到 CandidatePersonalityProfile

GET  /assessment/recommended-jobs/{candidate_id}
     ↓ 基于候选人的大五人格与岗位 required_traits 匹配
```

### 4.3 前端展示
- **RadarChart.vue**：雷达图表显示5个维度的分数
- **ReportPage.vue**：详细报告页面显示评估结果

### 4.4 评估流程中的大五人格计算
1. 候选人参与沉浸式对话（虚拟面试官交互）
2. 系统通过LLM分析回答内容
3. 计算并保存大五人格评分
4. 与岗位要求进行匹配度计算

---

## 🎯 5. 岗位/职位相关代码

### 5.1 岗位模型 (Job Model)
**完整字段**：
```python
id                  # 主键
name               # 岗位名称（e.g., "前端开发工程师"）
description        # 岗位描述
company            # 公司名称
category           # 岗位类别（技术岗/产品岗/设计岗/等）
city               # 工作地点
salary_min         # 薪资下限
salary_max         # 薪资上限
required_traits    # 大五人格要求（JSON）
creator_id         # HR创建者ID
```

### 5.2 岗位相关API
```
创建岗位（仅HR）：
POST   /jobs/ 
       请求体: { name, description, company, category, city, 
                 salary_min, salary_max, required_traits }

查询岗位：
GET    /jobs/                    # 列表（支持按category/city过滤）
GET    /jobs/{job_id}            # 详情
GET    /jobs/recommended/cards   # 推荐岗位卡片

前端流程：
GET    /jobs/home/data           # 首页数据
GET    /jobs/stats/candidate     # 面试统计
```

### 5.3 岗位与评估的关联
```
Job ←→ Interview         (一对多关系)
Job ←→ AssessmentRecord  (一对多关系)
Job ←→ EvaluationFramework (一对一关系)
```

### 5.4 岗位创建示例（初始化脚本）
`backend/init_simple.py` 中预置的岗位：
```python
('前端开发工程师', '..描述..', '阿里巴巴', '技术岗', '杭州', 25, 35, 
 {"openness": 8, "conscientiousness": 8, ...})

('后端开发工程师', '...', '字节跳动', '技术岗', '北京', 30, 50, 
 {"openness": 7, "conscientiousness": 9, ...})

('产品经理', '...', '美团', '产品岗', '北京', 25, 40, 
 {"openness": 9, "conscientiousness": 8, ...})

('视觉设计师', '...', '网易', '设计岗', '杭州', 18, 28, 
 {"openness": 9, "conscientiousness": 7, ...})
```

### 5.5 前端岗位管理页面
```
views/position/
├── JobManageView.vue      # 岗位列表管理
└── JobEditView.vue        # 岗位编辑/创建

components/
└── JobCard.vue            # 岗位卡片展示
```

---

## 📂 6. 完整的文件路径参考

### 后端关键文件
```
backend/
├── models/
│   ├── user.py                          ⭐ User 模型（候选人+HR）
│   ├── job.py                           ⭐ Job 模型（岗位）
│   ├── assessment.py                    ⭐ CandidatePersonalityProfile/AssessmentRecord
│   ├── evaluation_framework.py          ⭐ 评估框架
│   ├── interview.py                     ⭐ Interview 模型
│   ├── candidate.py                     # 备用候选人模型
│   ├── conversation.py
│   ├── hr_agent.py
│   ├── interviewer_role.py
│   └── __init__.py
│
├── routers/
│   ├── auth.py                          # 认证
│   ├── user.py                          # 用户管理
│   ├── candidate.py                     # 候选人信息
│   ├── job.py                           ⭐ 岗位API
│   ├── assessment.py                    ⭐ 评估API
│   ├── interview.py                     # 面试API
│   ├── interviewer.py                   # 面试官/虚拟对话
│   ├── hr_agent.py                      # HR代理
│   ├── immersive_dialogue.py            # 沉浸式对话
│   └── __pycache__/
│
├── schemas/
│   └── schemas.py                       # Pydantic schemas
│
├── services/                            # 业务逻辑层
├── utils/                               # 工具函数
├── prompts/                             # LLM提示词
├── main.py                              # 应用入口
├── database.py                          # 数据库配置
└── requirements.txt                     # 依赖
```

### 前端关键文件
```
frontend/
├── src/
│   ├── views/
│   │   ├── HomePage.vue / HomeView.vue
│   │   ├── LoginView.vue
│   │   ├── ProfileView.vue
│   │   ├── HRHomeView.vue
│   │   ├── AssessmentView.vue
│   │   ├── IndexView.vue
│   │   ├── position/
│   │   │   ├── JobManageView.vue        ⭐ 岗位管理
│   │   │   └── JobEditView.vue
│   │   └── assessment/
│   │       ├── BasicInfo.vue
│   │       ├── ImmersiveRoleDialogue.vue
│   │       ├── ReportPage.vue
│   │       └── components/
│   │
│   ├── components/
│   │   ├── JobCard.vue                  ⭐ 岗位展示
│   │   ├── RadarChart.vue               ⭐ 大五人格图表
│   │   ├── AssessmentHistory.vue
│   │   ├── VirtualInterviewerChat.vue   ⭐ 虚拟对话
│   │   ├── UploadInfoDialog.vue
│   │   └── EmptyState.vue
│   │
│   ├── router/                          # 前端路由
│   ├── stores/                          # Pinia store
│   ├── api/                             # API调用
│   ├── types/                           # TypeScript类型
│   ├── utils/                           # 工具
│   ├── assets/                          # 资源
│   ├── App.vue
│   └── main.ts
│
├── public/                              # 静态文件
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 🔄 7. 核心业务流程关联图

```
用户认证
    ↓
User (HR/Candidate)
    ├── HR: 创建岗位 (Job)
    │   ├── 岗位包含大五人格要求 (required_traits)
    │   └── 创建评估框架 (EvaluationFramework)
    │
    └── Candidate: 参与评估
        ├── 保存基本信息 (User.profile)
        ├── 上传简历
        ├── 参加沉浸式对话 (Interview)
        │   ├── 虚拟面试官交互
        │   ├── LLM分析回答
        │   └── 计算大五人格评分
        ├── 生成CandidatePersonalityProfile
        └── 生成AssessmentRecord
            └── 与岗位required_traits匹配
                └── 推荐合适岗位
```

---

## 📋 8. 快速数据对应表

| 功能模块 | 核心模型 | 主要API | 前端组件 |
|---------|--------|--------|--------|
| 岗位管理 | Job, EvaluationFramework | /jobs/* | JobManageView, JobCard |
| 候选人信息 | User (CANDIDATE) | /candidates/* | BasicInfo, ProfileView |
| 评估流程 | Interview, AssessmentRecord | /assessment/* | ImmersiveRoleDialogue |
| 大五人格 | CandidatePersonalityProfile | /assessment/portrait | RadarChart, ReportPage |
| 面试对话 | Interview, Conversation | /interviewer/chat/* | VirtualInterviewerChat |
| 用户认证 | User | /auth/* | LoginView |

---

## 🚀 9. 关键注意事项

1. **大五人格维度**（5个特质）：
   - Openness（开放性）
   - Conscientiousness（尽责性）
   - Extraversion（外向性）
   - Agreeableness（宜人性）
   - Neuroticism（神经质）

2. **岗位分类**：技术岗、产品岗、设计岗等

3. **用户类型**：通过 `User.user_type` 区分 (HR/CANDIDATE)

4. **软删除**：所有主表都支持 `is_deleted` 和 `deleted_at` 软删除

5. **评估状态**：AssessmentRecord.assessment_status 追踪评估进度

6. **隐私设置**：Candidate.delivery_privacy 控制信息展示方式

---

生成于：2026年3月28日
