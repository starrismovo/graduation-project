# 后端 API 对接指南 - 候选人首页

## 📋 概述

本文档规范了前端 HomeView（候选人首页重新设计）所需的后端 API 接口。

---

## 🔌 必须实现的 4 个核心 API

### 1️⃣ 获取心理画像

**端点：**
```
GET /assessment/portrait/{candidate_id}
```

**请求示例：**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/assessment/portrait/123
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "name": "外向性",
      "score": 8.5
    },
    {
      "name": "宜人性",
      "score": 7.2
    },
    {
      "name": "尽责性",
      "score": 9.1
    },
    {
      "name": "神经质",
      "score": 3.4
    },
    {
      "name": "开放性",
      "score": 8.8
    }
  ]
}
```

**说明：**
- `score` 范围：0-10
- 五因素必须全部返回（Big Five）
- 如果候选人还未进行任何评估，返回 `data: []` 或五个零分项


---

### 2️⃣ 获取历史评估记录

**端点：**
```
GET /assessment/history/{candidate_id}
```

**请求参数（可选）：**
```
?limit=10&offset=0
?status=completed  // completed, pending, failed
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "job_id": 101,
      "job_title": "前端工程师",
      "match_score": 85,
      "created_at": "2024-02-20T10:30:00Z",
      "assessment_status": "completed",
      "assessment_mode": "immersive"
    },
    {
      "id": 2,
      "job_id": 102,
      "job_title": "高级后端工程师",
      "match_score": 72,
      "created_at": "2024-02-18T14:15:00Z",
      "assessment_status": "completed",
      "assessment_mode": "immersive"
    }
  ]
}
```

**说明：**
- 按时间倒序（最新的在前）
- `match_score` 范围：0-100（百分比）
- `assessment_status` 枚举值：`completed`, `pending`, `failed`
- 新用户返回 `data: []`


---

### 3️⃣ 获取推荐岗位

**端点：**
```
GET /assessment/recommended-jobs/{candidate_id}
```

**请求参数（可选）：**
```
?limit=5
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 101,
      "title": "高级前端工程师",
      "description": "领导前端技术团队，负责核心基础设施建设",
      "department": "技术部",
      "level": "P7",
      "match_score": 88,
      "match_reason": "技术深度与岗位要求高度匹配"
    },
    {
      "id": 102,
      "title": "产品经理",
      "description": "负责C端产品规划与迭代",
      "department": "产品部",
      "level": "P6",
      "match_score": 76,
      "match_reason": "产品思维和沟通能力突出"
    },
    {
      "id": 103,
      "title": "技术负责人",
      "description": "领导技术部门战略规划",
      "department": "技术部",
      "level": "P8",
      "match_score": 82,
      "match_reason": "综合能力和领导潜力符合要求"
    }
  ]
}
```

**说明：**
- 按 `match_score` 降序返回
- 只返回前3-5个高匹配岗位（不要返回所有岗位）
- `match_score` 计算基于候选人的心理特质与岗位胜任力模型
- 如果候选人没有心理画像，可返回空数组或推荐热门岗位


---

### 4️⃣ 获取评估报告详情

**端点：**
```
GET /assessment/report/{record_id}
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "candidate_id": 123,
    "job_id": 101,
    "job_title": "前端工程师",
    "match_score": 85,
    "created_at": "2024-02-20T10:30:00Z",
    "updated_at": "2024-02-20T10:35:00Z",
    "assessment_mode": "immersive",
    
    "personality_trait": [
      {
        "name": "外向性",
        "score": 8.5,
        "description": "具有较强的社交能力和表达欲望"
      },
      {
        "name": "宜人性",
        "score": 7.2,
        "description": "能够很好地与他人合作"
      },
      {
        "name": "尽责性",
        "score": 9.1,
        "description": "高度的自律性和责任意识"
      },
      {
        "name": "神经质",
        "score": 3.4,
        "description": "情绪稳定，心理素质较好"
      },
      {
        "name": "开放性",
        "score": 8.8,
        "description": "充满好奇心，乐于学习和创新"
      }
    ],

    "conversation_summary": "候选人在对话中展现了出色的问题分析能力和技术深度。在与技术总监的讨论中，能够清晰地解释复杂的技术概念。在与产品经理的交流中，表现出很好的用户视角思维...",

    "match_analysis": {
      "strengths": [
        "技术深度扎实，能独立解决复杂技术问题",
        "沟通能力强，能清晰表达和倾听他人观点",
        "学习能力强，对新技术充满热情",
        "责任意识高，对工作质量有严格要求"
      ],
      "gaps": [
        "项目管理经验不足",
        "大团队协作经验相对较少",
        "需要进一步提升系统架构思维"
      ]
    },

    "recommendations": [
      "建议参与更多大型项目的团队合作，积累项目管理经验",
      "推荐学习系统架构和服务设计相关知识",
      "可考虑参与开源项目，扩展技术视野",
      "建议定期参加技术分享和交流活动，分享自己的经验和思考"
    ],

    "assessement_details": {
      "total_rounds": 32,
      "duration_minutes": 18,
      "conversation_depth": 8.5,
      "roles_participated": ["hr", "tech_lead", "product"],
      "overall_impression": "候选人表现出色，强烈推荐进一步沟通"
    }
  }
}
```

**说明：**
- 包含完整的评估数据
- `personality_trait` 必须包含五大人格评分
- `conversation_summary` 是对对话过程的文字总结（AI生成推荐）
- `match_analysis` 包含优势和改进空间
- `recommendations` 是给候选人的建议
- `assessement_details` 包含对话统计


---

## 🔄 数据流程关系

```
候选人
  ├─ 首次登录 (isNewUser=true)
  │   └─ portrait = [] (空)，history = [] (空)，recommended_jobs = [] (默认热门)
  │       └─ 显示欢迎弹窗，空状态雷达图
  │
  └─ 完成一次评估 (isNewUser=false)
      ├─ 调用 /assessment/portrait/{id} → 返回五大人格评分
      ├─ 调用 /assessment/history/{id} → 返回评估记录列表
      ├─ 调用 /assessment/recommended-jobs/{id} → 返回匹配岗位
      └─ 用户点击历史记录 → 调用 /assessment/report/{record_id}
```


---

## 📝 实现建议

### 数据库表结构（参考）

```sql
-- 心理特质评估记录表
CREATE TABLE assessment_records (
  id BIGINT PRIMARY KEY,
  candidate_id BIGINT NOT NULL,
  job_id INT NOT NULL,
  job_title VARCHAR(255),
  match_score INT,  -- 0-100
  assessment_status VARCHAR(50),  -- completed, pending, failed
  assessment_mode VARCHAR(50),  -- immersive, ...
  conversation_summary TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 候选人心理特质评分（缓存或计算）
CREATE TABLE candidate_personality_traits (
  candidate_id BIGINT PRIMARY KEY,
  trait_extroversion DECIMAL(3,1),  -- 0-10
  trait_agreeableness DECIMAL(3,1),
  trait_conscientiousness DECIMAL(3,1),
  trait_neuroticism DECIMAL(3,1),
  trait_openness DECIMAL(3,1),
  updated_at TIMESTAMP
);

-- 匹配分析表
CREATE TABLE assessment_match_analysis (
  record_id BIGINT PRIMARY KEY,
  strengths JSON,  -- 优势列表 ["能力1", "能力2"]
  gaps JSON,       -- 改进空间 ["能力1"]
  recommendations JSON  -- 建议列表
);
```

### 关键计算逻辑

```python
# 伪代码 - Python后端 (FastAPI)

@app.get("/assessment/portrait/{candidate_id}")
async def get_portrait(candidate_id: int):
    """
    逻辑：
    1. 查询该候选人最近的所有评估记录
    2. 对各特质评分进行加权平均（或获取最新评估的评分）
    3. 返回五大人格评分数组
    """
    records = db.query(AssessmentRecord).filter_by(candidate_id=candidate_id).all()
    
    if not records:
        return {"code": 200, "data": []}  # 新用户
    
    # 计算平均或获取最新特质评分
    traits = compute_average_traits(records)
    
    return {
        "code": 200,
        "data": traits
    }


@app.get("/assessment/recommended-jobs/{candidate_id}")
async def get_recommended_jobs(candidate_id: int, limit: int = 5):
    """
    逻辑：
    1. 获取候选人的心理特质
    2. 遍历所有岗位，用匹配算法计算 match_score
    3. 按 match_score 排序，返回前 limit 个
    """
    portrait = get_personality_traits(candidate_id)
    
    if not portrait:
        # 新用户，返回热门岗位
        jobs = db.query(Job).order_by(Job.apply_count.desc()).limit(limit).all()
    else:
        # 计算匹配度
        jobs = compute_job_match(portrait, limit)
    
    return {
        "code": 200,
        "data": jobs_to_dict(jobs)
    }


def compute_job_match(portrait: dict, limit: int) -> List[Job]:
    """
    匹配算法（示例）：
    match_score = 
        0.3 * aligned_traits +           # 特质匹配
        0.3 * similarity_level +         # 级别匹配
        0.2 * skill_match +              # 技能匹配
        0.2 * career_fit                 # 职业路径匹配
    """
    all_jobs = db.query(Job).all()
    
    for job in all_jobs:
        job.match_score = calculate_match_score(portrait, job)
    
    return sorted(all_jobs, key=lambda x: x.match_score, reverse=True)[:limit]
```


---

## ✅ 测试清单

- [ ] GET /assessment/portrait/123 返回有效的五大人格数组
- [ ] GET /assessment/portrait/newuser 返回空数组
- [ ] GET /assessment/history/123 返回倒序的历史记录
- [ ] GET /assessment/history/empty 返回空数组
- [ ] GET /assessment/recommended-jobs/123 返回按匹配度排序的岗位
- [ ] GET /assessment/report/1 返回完整的报告数据
- [ ] GET /assessment/report/invalid 返回 404 或错误码
- [ ] 所有端点都返回 Standard Response 格式
- [ ] 所有端点都要求 Authorization header
- [ ] 超时时间设置在 30 秒以内


---

## 📞 前后端联调

**测试地址：**
```bash
# 本地测试
curl -H "Authorization: Bearer test_token" \
  http://localhost:8000/assessment/portrait/1

# 测试数据 (mock response)
{
  "code": 200,
  "data": [
    { "name": "外向性", "score": 7 },
    { "name": "宜人性", "score": 6 },
    { "name": "尽责性", "score": 8 },
    { "name": "神经质", "score": 4 },
    { "name": "开放性", "score": 7.5 }
  ]
}
```

**前端验收标准：**
- 响应时间 < 2 秒
- 完整性：所有必填字段都有
- 准确性：数据与实际评估一致
- 一致性：多次请求结果相同（缓存）

---

## 🔐 权限与安全

- 所有端点需要 `Authorization: Bearer <token>` header
- 候选人只能访问自己的数据
- 实装速率限制（rate limiting）
- 评估数据不应该泄露给其他用户


---

## 📚 参考文档

- Big Five 人格模型：https://en.wikipedia.org/wiki/Big_Five_personality_traits
- 本项目课题：基于AI智能体的人岗匹配心理特质评估系统
- 前端实现指南：CANDIDATE_HOME_IMPLEMENTATION.md
