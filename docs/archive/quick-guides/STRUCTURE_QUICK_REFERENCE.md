# 项目快速参考卡片

## 📊 核心数据模型 @5秒速查

### User Model `backend/models/user.py`
```
候选人/HR 统一管理
- user_type: HR | CANDIDATE
- Candidate 字段: age, education, major, desired_job, skills, resume_url
```

### Job Model `backend/models/job.py`
```
岗位信息
- name: 岗位名称
- category: 技术岗/产品岗/设计岗
- required_traits: {"openness": 8, ...} ← 大五人格要求
- creator_id: HR user_id
```

### CandidatePersonalityProfile `backend/models/assessment.py`
```
候选人大五人格评分 (0-10)
- trait_openness: 开放性
- trait_conscientiousness: 尽责性
- trait_extraversion: 外向性
- trait_agreeableness: 宜人性
- trait_neuroticism: 神经质
```

### EvaluationFramework `backend/models/evaluation_framework.py`
```
岗位的评估标准
- target_traits: 目标值 {openness: 0.7, ...}
- trait_weights: 权重 {openness: 0.15, ...}
```

### Interview Model `backend/models/interview.py`
```
面试记录
- candidate_id, job_id
- personality_traits: 评估得分 (JSON)
- status: started/in_progress/completed/...
```

---

## 🌐 主要API路由 @3秒速查

### 岗位管理 `/jobs`
```
POST   /jobs/                    创建岗位
GET    /jobs/                    列表
GET    /jobs/{id}                详情
GET    /jobs/recommended/cards   推荐卡片
```

### 候选人 `/candidates`
```
POST   /candidates/{id}/basic-info    保存基本信息
GET    /candidates/{id}/basic-info    获取基本信息
```

### 评估 `/assessment`  ⭐ 核心
```
GET    /assessment/portrait/{candidate_id}        大五人格结果
GET    /assessment/history/{candidate_id}         评估历史
GET    /assessment/recommended-jobs/{id}          推荐岗位
GET    /assessment/report/{record_id}             详细报告

POST   /assessment/immersive/next-question        沉浸式-获取问题
POST   /assessment/immersive/analyze-response     沉浸式-分析回答
POST   /assessment/immersive/save-session         沉浸式-保存结果
```

### 面试官对话 `/interviewer`
```
GET    /interviewer/interviewers                  面试官列表
POST   /interviewer/session/create                创建session
POST   /interviewer/chat/stream                   流式对话
WebSocket /interviewer/ws/chat/{session_id}      实时WebSocket
```

---

## 🎨 前端关键组件 @2秒速查

### Views (页面)
```
HomePage/HomeView.vue             首页
LoginView.vue                      登录
ProfileView.vue                    个人资料

position/JobManageView.vue         岗位管理 (HR)
position/JobEditView.vue           岗位编辑

assessment/BasicInfo.vue           基本信息表单
assessment/ImmersiveRoleDialogue   沉浸式对话 ⭐
assessment/ReportPage.vue          评估报告
```

### Components (组件)
```
JobCard.vue                  岗位卡片展示
RadarChart.vue              大五人格雷达图 ⭐
VirtualInterviewerChat.vue  虚拟面试官聊天 ⭐
AssessmentHistory.vue       评估历史
UploadInfoDialog.vue         上传对话框
```

---

## 🧠 大五人格特质映射

| 英文 | 中文 | 字段名 | 含义 |
|-----|------|--------|------|
| Openness | 开放性 | trait_openness | 创意、好奇、想象力 |
| Conscientiousness | 尽责性 | trait_conscientiousness | 自律、条理、认真 |
| Extraversion | 外向性 | trait_extraversion | 社交、热情、活力 |
| Agreeableness | 宜人性 | trait_agreeableness | 合作、善良、体谅 |
| Neuroticism | 神经质 | trait_neuroticism | 焦虑、敏感、情绪 |

**评分范围**: 0-10（或0-1标准化）

---

## 📁 文件路径速查

### 后端关键文件
```
backend/models/          ← 所有数据模型
├── user.py (用户)
├── job.py (岗位)
├── assessment.py (评估/人格)
├── evaluation_framework.py (评估框架)
├── interview.py (面试)
└── ...

backend/routers/         ← 所有API路由
├── job.py (岗位API)
├── assessment.py (评估API) ⭐
├── interviewer.py (虚拟对话) ⭐
└── ...

backend/schemas/         ← 数据验证Schema
backend/services/        ← 业务逻辑
backend/main.py          ← 应用入口
```

### 前端关键文件
```
frontend/src/
├── views/               ← 页面
│   ├── position/JobManageView.vue ⭐
│   ├── assessment/ImmersiveRoleDialogue.vue ⭐
│   └── ...
├── components/          ← 组件
│   ├── RadarChart.vue ⭐
│   ├── VirtualInterviewerChat.vue ⭐
│   └── ...
└── ...
```

---

## 🔄 完整评估流程

```
1. 候选人登录
   ↓
2. 填写基本信息 (BasicInfo.vue)
   ↓
3. 选择岗位
   ↓
4. 启动虚拟面试 (ImmersiveRoleDialogue.vue)
   - 面试官进行沉浸式对话
   - 每次回答被LLM分析
   ↓
5. 评估完成
   - 保存 CandidatePersonalityProfile
   - 计算与岗位的匹配度
   ↓
6. 生成报告 (ReportPage.vue)
   - 显示大五人格雷达图 (RadarChart.vue)
   - 显示匹配度分析
   - 推荐其他岗位
```

---

## 🔗 关键外键关系

```
User ────one-to-many───→ Job (creator_id)
User ────one-to-many───→ Interview (candidate_id)
User ────one-to-one────→ CandidatePersonalityProfile

Job ────one-to-many───→ Interview
Job ────one-to-many───→ AssessmentRecord
Job ────one-to-one────→ EvaluationFramework

Interview ────many-to-one───→ User (candidate)
Interview ────many-to-one───→ Job

AssessmentRecord ────many-to-one───→ User (candidate)
AssessmentRecord ────many-to-one───→ Job
```

---

## 📌 岗位示例 & 人格权重

### 岗位示例（Job表）
```json
{
  "name": "前端开发工程师",
  "company": "阿里巴巴",
  "category": "技术岗",
  "city": "杭州",
  "salary_min": 25,
  "salary_max": 35,
  "required_traits": {
    "openness": 8,
    "conscientiousness": 8,
    "extraversion": 7,
    "agreeableness": 6,
    "neuroticism": 3
  }
}
```

### 评估框架权重示例（EvaluationFramework表）
```json
{
  "target_traits": {
    "openness": 0.7,
    "conscientiousness": 0.8,
    "extraversion": 0.6,
    "agreeableness": 0.7,
    "neuroticism": 0.4
  },
  "trait_weights": {
    "openness": 0.15,
    "conscientiousness": 0.25,
    "extraversion": 0.20,
    "agreeableness": 0.20,
    "neuroticism": 0.20
  }
}
```

---

## ⚙️ 用户类型

```
UserType.HR        ← HR人力资源
  - 可创建岗位 (jobs)
  - 可管理评估框架
  - 可查看候选人评估结果

UserType.CANDIDATE ← 候选人
  - 可填写基本信息
  - 可参加评估
  - 可获取评估报告
  - 可查看推荐岗位
```

---

✅ 本文档已同步到 `PROJECT_STRUCTURE_OVERVIEW.md` (详细版)
