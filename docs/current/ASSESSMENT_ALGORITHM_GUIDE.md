# 面试评估 → 大五人格 → 岗位推荐 完整算法指南

## 1. 整体流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    沉浸式面试 (对话系统)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. 面试官提问（HR/技术总监/产品经理/CTO 四个角色轮流） │   │
│  │ 2. 候选人回答                                          │   │
│  │ 3. EvaluatorAgent 评分回答                             │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│   收集 all_scores (能力维度评分)  │
│   - 表达能力 (0-10)              │
│   - 团队合作 (0-10)              │
│   - 专业能力 (0-10)              │
│   - 逻辑思维 (0-10)              │
│   - 创新思维 (0-10)              │
│   - 学习能力 (0-10)              │
└────────────┬─────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│   score_big_five_from_abilities()        │
│   （映射算法 v1_2026_04）                │
│   将能力维度 → 大五人格评分 (0-10)      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│   大五人格评分 (trait_*)                     │
│   - trait_extroversion (外向性)             │
│   - trait_agreeableness (宜人性)            │
│   - trait_conscientiousness (尽责性)        │
│   - trait_neuroticism (神经质)              │
│   - trait_openness (开放性)                 │
│   存入 CandidatePersonalityProfile           │
└────────────┬────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│   岗位推荐算法 (两套)               │
│   ├─ 评估场景 (assessment.py)      │
│   │  └─ 0.4×skill + 0.6×personality
│   │                                 │
│   └─ 推荐列表 (recommendation.py)   │
│      └─ 0.5×skill + 0.3×personality
│         + 0.2×(城市/薪资)           │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────┐
│   推荐岗位列表（按匹配分降序）  │
│   [岗位A: 78分, 岗位B: 65分]   │
└──────────────────────────────┘
```

---

## 2. 能力维度 → 大五人格 映射公式

**文件**: `backend/services/personality_scoring.py`  
**函数**: `score_big_five_from_abilities(all_scores)`  
**模型版本**: `bigfive_map_v1_2026_04`

### 映射矩阵

| 大五人格 | 计算公式 | 权重说明 |
|---------|---------|---------|
| **外向性 (Extraversion)** | `表达能力×0.5 + 团队合作×0.5` | 表达和社交均等重要 |
| **宜人性 (Agreeableness)** | `团队合作×0.6 + 表达能力×0.4` | 协作优于表达 |
| **尽责性 (Conscientiousness)** | `专业能力×0.5 + 逻辑思维×0.5` | 专业水准和思维严密等同 |
| **神经质 (Neuroticism)** | `10.0 - (逻辑思维×0.4 + 表达能力×0.3 + 专业能力×0.3)` | 反向指标：逻辑清晰的人神经质低 |
| **开放性 (Openness)** | `创新思维×0.5 + 学习能力×0.5` | 创新和学习均衡 |

### 关键特性

1. **所有评分绝对值范围**: 0-10（通过 `_clamp_score()` 钳制）
2. **神经质反向**: 这是唯一的反向指标，即逻辑清晰/表达有力的人神经质评分较低
3. **缺失能力维度处理**: 若某维度未评分，默认填充 5.0（中等水平）
4. **确定性**: 同一输入始终产出相同结果（无随机性）

### 计算示例

**场景**: 候选人面试评分

```
输入 all_scores:
{
  "表达能力": 7.5,
  "团队合作": 8.0,
  "专业能力": 6.5,
  "逻辑思维": 7.0,
  "创新思维": 6.0,
  "学习能力": 8.0
}

输出大五人格:
{
  "外向性": 7.75 = (7.5×0.5 + 8.0×0.5)
  "宜人性": 7.7  = (8.0×0.6 + 7.5×0.4)
  "尽责性": 6.75 = (6.5×0.5 + 7.0×0.5)
  "神经质": 2.5  = 10.0 - (7.0×0.4 + 7.5×0.3 + 6.5×0.3) = 10.0 - 7.3 = 2.7 → clamped to [0,10]
  "开放性": 7.0  = (6.0×0.5 + 8.0×0.5)
}
```

---

## 3. 岗位推荐的两套算法

### 3.1 评估场景 (assessment.py)

**调用位置**: `POST /assessment/save-result`  
**使用场景**: 候选人完成评估后，生成个性化的岗位推荐

**算法**:
```python
def calculate_job_match_score(personality_profile, job):
    # personality_match: 大五人格与岗位要求的吻合度（0-100）
    personality_match = 0
    for trait_name, required_score in job.required_traits.items():
        candidate_score = personality_profile.get_trait(trait_name)  # 0-10
        similarity = 10 - abs(candidate_score - required_score)
        personality_match += similarity
    personality_match = (personality_match / matched_count) * 10
    
    # skill_match: 无技能数据，置为 50（中性值）
    skill_match = 50.0
    
    # overall: 人格权重较大（60%）
    overall = 0.4 * skill_match + 0.6 * personality_match
    
    return {
        "skill_match": 50.0,
        "personality_match": personality_match,
        "overall": overall
    }
```

**权重分配**:
- 人格匹配: 60%（因为有人格评估数据）
- 技能匹配: 40%（无数据，默认值）

**示例**:
```
候选人大五人格: [外向性:7.5, 宜人性:7.7, 尽责性:6.75, 神经质:2.5, 开放性:7.0]

岗位A需求: {
  "外向性": 7.0,
  "宜人性": 6.0,
  "尽责性": 7.5,
  "神经质": 3.0,
  "开放性": 6.5
}

计算:
- 外向性相似度: 10 - |7.5-7.0| = 9.5
- 宜人性相似度: 10 - |7.7-6.0| = 8.3
- 尽责性相似度: 10 - |6.75-7.5| = 9.25
- 神经质相似度: 10 - |2.5-3.0| = 9.5
- 开放性相似度: 10 - |7.0-6.5| = 9.5
- 平均相似度: (9.5+8.3+9.25+9.5+9.5)/5 = 9.21 → personality_match = 92.1

overall = 0.4×50 + 0.6×92.1 = 20 + 55.26 = 75.26 ≈ 75.3
```

---

### 3.2 推荐列表场景 (recommendation.py)

**调用位置**: 岗位列表页展示匹配分，或 HR 寻找候选人推荐

**算法**:
```python
def calculate_job_match_score(candidate, job):
    # ─ skill_match: 60%技能关键词+40%工作经验 ─
    candidate_skills = set(candidate.skills.split(","))
    required_skills = set(job.required_traits.keys())
    skill_match = (len(candidate_skills ∩ required_skills) / len(required_skills)) * 60
    experience_years = min(candidate.work_experience, 15)
    skill_match += (experience_years / 15) * 40
    
    # ─ personality_match: 无人格数据，置为 50 ─
    personality_match = 50.0
    
    # ─ other_factor: 城市50% + 薪资50% ─
    other_factor = 0
    if candidate.city == job.city:
        other_factor += 50
    else:
        other_factor += 20
    
    salary_match = 0
    if job.salary_min <= candidate.salary <= job.salary_max:
        salary_match = 50
    elif candidate.salary < job.salary_min:
        gap_ratio = (job.salary_min - candidate.salary) / job.salary_min
        salary_match = max(0, 50 - gap_ratio * 50)
    else:
        gap_ratio = (candidate.salary - job.salary_max) / job.salary_max
        salary_match = max(0, 50 - gap_ratio * 30)
    other_factor = (other_factor + salary_match) / 2
    
    # ─ overall ─
    overall = 0.5*skill_match + 0.3*personality_match + 0.2*other_factor
    
    return {
        "skill_match": skill_match,
        "personality_match": 50.0,
        "overall": overall
    }
```

**权重分配**:
- 技能匹配: 50%（最重要）
- 人格匹配: 30%（无数据）
- 其他因素（城市/薪资）: 20%

**示例**:
```
候选人数据:
- skills: ["Python", "React", "SQL"]
- work_experience: 3 年
- city: "北京"
- salary_expectation: 15k

岗位数据:
- required_traits: {"Python": 1, "React": 1, "Node.js": 1}
- city: "北京"
- salary_min: 12k, salary_max: 18k

计算:
- 技能匹配: (2/3)×60 + (3/15)×40 = 40 + 8 = 48
- 人格匹配: 50.0 (默认)
- 城市: 50 (完全匹配)
- 薪资: (15k 在 12-18k 范围内) = 50
- other_factor: (50 + 50) / 2 = 50

overall = 0.5×48 + 0.3×50 + 0.2×50 = 24 + 15 + 10 = 49

匹配等级: "一般" (因为 < 50)
```

---

## 4. 匹配等级解释

| 等级 | 分数范围 | 含义 |
|-----|---------|------|
| 极佳 | 80-100 | 候选人人格特质和技能与岗位高度契合，强烈推荐面试 |
| 良好 | 65-79 | 候选人基本符合岗位要求，值得深入考察 |
| 一般 | 50-64 | 候选人部分指标匹配，存在改进空间 |
| 较低 | 0-49 | 候选人与岗位匹配度有限，建议继续寻找其他候选人 |

---

## 5. 关键决策点和限制

### 5.1 数据来源优先级

1. **大五人格评分**（来自面试）→ 最优先
2. **简历技能信息** → 备选方案
3. **默认值** (50.0) → 当无任何数据时

### 5.2 边界情况处理

| 情况 | 处理方式 |
|-----|---------|
| 面试评分缺失某维度 | 该维度默认 5.0（中等） |
| 岗位未配置人格要求 | 跳过人格匹配，仅看技能/其他因素 |
| 候选人无技能信息 | skill_match 直接置为 50.0 |
| 薪资超出范围 | 按超出比例线性扣分，但超高薪资扣分较轻 |

### 5.3 算法限制

1. **没有学习机制**: 匹配分数完全由输入决定，不会因为历史结果改变
2. **岗位特定性**: 推荐结果完全依赖岗位的 `required_traits` 配置质量
3. **人格稳定假设**: 假设候选人的大五人格在评估后保持稳定

---

## 6. 扩展可能性

### 6.1 可调参数

如果要优化推荐效果，可修改的参数：

```python
# 在 recommendation.py 中的权重
overall = (
    0.5 * skill_match +      # ← 可调
    0.3 * personality_match +  # ← 可调
    0.2 * other_factor         # ← 可调
)

# 在 assessment.py 中的权重
overall = (
    0.4 * skill_match +      # ← 可调
    0.6 * personality_match    # ← 可调
)

# 在 score_big_five_from_abilities 中的映射权重
extraversion = (
    表达能力 * 0.5 +          # ← 可调
    团队合作 * 0.5             # ← 可调
)
```

### 6.2 未来增强

1. **动态权重**: 基于岗位类型（如销售岗可增加外向性权重）
2. **岗位聚类**: 相似岗位共享推荐模型
3. **反馈学习**: 根据候选人最终入职表现调整权重
4. **技能树匹配**: 将零散的技能关键词组织成技能树，支持隐式匹配

---

## 7. 数据存储

### 关键表

| 表名 | 作用 | 关键字段 |
|------|------|---------|
| `candidate_personality_profiles` | 存储最新的大五人格评分 | trait_extroversion, trait_agreeableness, ... |
| `assessment_records` | 存储评估过程 | match_score, assessment_status |
| `assessment_match_analyses` | 存储匹配分析详情 | strengths, gaps, recommendations, detailed_analysis (JSON) |
| `job_personality_frameworks` | 存储岗位的人格要求 | openness_min/max, conscientiousness_min/max, ... |
| `job_skill_requirements` | 存储岗位的技能要求 | skill_name, required_level, priority_score |

---

## 8. 调试和验证

### 快速测试脚本

```python
# 测试映射公式
from services.personality_scoring import score_big_five_from_abilities

all_scores = {
    "表达能力": 7.5,
    "团队合作": 8.0,
    "专业能力": 6.5,
    "逻辑思维": 7.0,
    "创新思维": 6.0,
    "学习能力": 8.0
}

result, meta = score_big_five_from_abilities(all_scores)
print(result)  # 看大五人格评分
print(meta)    # 看元数据（模型版本、输入维度）
```

```python
# 测试岗位推荐
from routers.assessment import calculate_job_match_score
from models.assessment import CandidatePersonalityProfile
from models.job import Job

profile = CandidatePersonalityProfile(
    trait_extroversion=7.5,
    trait_agreeableness=7.7,
    ...
)

job = Job(
    required_traits={
        "外向性": 7.0,
        "宜人性": 6.0,
        ...
    }
)

match = calculate_job_match_score(profile, job)
print(match)  # {"skill_match": 50.0, "personality_match": 92.1, "overall": 75.3}
```
