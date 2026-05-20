1# HR 岗位操作功能完整汇总（2026年3月28日）

## 📋 目录
1. [前端页面组件](#前端页面组件)
2. [后端 API 路由](#后端-api-路由)
3. [数据库模型](#数据库模型)
4. [已实现的功能](#已实现的功能)
5. [缺失的功能](#缺失的功能)
6. [API 调用示例](#api-调用示例)

---

## 前端页面组件

### 1. HRHomeView.vue
**位置**: `frontend/src/views/HRHomeView.vue`

**功能**: HR主页 - 岗位管理仪表板

**代码片段**:
```vue
<script setup lang="ts">
// 岗位列表和统计信息
const jobsList = ref<any[]>([])
const loading = ref(true)
const showCreateDialog = ref(false)

// 创建表单数据
const createFormData = ref({
  name: '',
  description: '',
  company: '',
  category: '',
  city: '',
  salary_min: '',
  salary_max: ''
})

// 统计数据
const stats = ref({
  totalJobs: 0,        // 总岗位数
  openJobs: 0,         // 开放岗位数
  totalSubmissions: 0, // 投递总量
  avgMatchScore: 0,    // 平均匹配度
  pendingReports: 0    // 待处理报告
})

// 核心函数
function loadJobs()      // 加载岗位列表
function handleCreateJob() // 创建岗位
function handleEditJob()   // 编辑岗位
function handleDeleteJob() // 删除岗位
```

**已实现**:
- ✅ 显示岗位列表
- ✅ 显示统计卡片（总岗位、开放岗位、投递数、匹配度、待处理报告）
- ✅ 岗位表格展示（岗位信息、状态、投递数、匹配度、操作）
- ✅ 删除确认对话框

**缺失**:
- ❌ 创建岗位对话框实现（`handleCreateJob` 未实现）
- ❌ 编辑岗位功能
- ❌ 删除岗位API调用
- ❌ 更新统计数据的实时刷新

---

### 2. JobManageView.vue
**位置**: `frontend/src/views/position/JobManageView.vue`

**功能**: 岗位管理仪表板 - 用于HR查看和管理岗位

**代码特性**:
```vue
<!-- 页面组成 -->
- 页面头部: 刷新数据按钮、创建岗位按钮
- 统计卡片: 开放岗位、总投递数、平均匹配度、待处理报告
- 岗位列表: 
  - 搜索框
  - 排序方式（最新发布/投递最多/匹配度最高）
  - 岗位表格
  - 操作按钮（查看报告、编辑、删除）
```

**按钮操作**:
- `handleCreateJob()` - 创建岗位（功能开发中）
- `handleEditJob(job)` - 编辑岗位（跳转到 `/views/position/{id}/edit`）
- `handleDeleteJob(job)` - 删除岗位（功能开发中）
- `handleViewReports(job)` - 查看报告
- `handleRefresh()` - 刷新数据

---

### 3. JobRequirementsManager.vue
**位置**: `frontend/src/components/JobRequirementsManager.vue`

**功能**: 岗位需求编辑器 - HR编辑岗位需求，候选人查看岗位需求

**支持两种模式**:

#### HR 模式 (isHR = true)
```vue
<!-- 输入部分 -->
- 岗位名称
- 岗位类别选择（后端/前端/产品/设计/HR/管理）
- 岗位描述(JD)文本区

<!-- 自动生成 -->
- 生成需求按钮 (@click="parseJD")

<!-- 显示部分 -->
1. 所需技能 (filteredSkills.length)
   - 每个技能卡片显示:
     - 技能名称
     - 是否必需（按钮切换）
     - 等级、优先级、经验年数
     - 删除按钮

2. 大五人格要求
   - 5个维度的滑块:
     - 开放性 (Openness)
     - 尽责性 (Conscientiousness)
     - 外向性 (Extraversion)
     - 宜人性 (Agreeableness)
     - 神经质 (Neuroticism)

<!-- 表单数据 -->
formData: {
  jobName: '',
  roleCategory: 'backend',
  jdText: '',
  skills: [],
  personality_framework: {
    openness_min, openness_max,
    conscientiousness_min, conscientiousness_max,
    extraversion_min, extraversion_max,
    agreeableness_min, agreeableness_max,
    neuroticism_min, neuroticism_max
  }
}

<!-- API 调用 -->
- parseJD() - 调用 createJobRequirementsFromJD()
- @click save - 调用 updateJobRequirements()
```

#### 候选人模式 (isHR = false)
```vue
- 显示岗位列表
- 选择岗位
- 查看岗位需求详情
- 应聘按钮 (@click="applyJob")
```

---

## 后端 API 路由

### 文件位置：`backend/routers/job_requirements.py` 和 `backend/routers/job.py`

### 岗位基础操作 (job.py)

#### 1. 创建岗位
```python
@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobResponse
```

**请求**:
```json
{
  "name": "高级 Python 工程师",
  "description": "负责后端系统开发",
  "company": "字节跳动",
  "category": "backend",
  "city": "北京",
  "salary_min": 30,
  "salary_max": 50,
  "required_traits": {
    "openness": 7.0,
    "conscientiousness": 8.0,
    "extraversion": 6.0,
    "agreeableness": 7.0,
    "neuroticism": 3.0
  }
}
```

**响应**: `JobResponse` (包含 id, name, description等)

**权限**: ✅ HR 用户

---

#### 2. 获取岗位列表
```python
@router.get("/", response_model=List[JobResponse])
def get_jobs(
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    salary_min: Optional[float] = Query(None),
    salary_max: Optional[float] = Query(None),
    db: Session = Depends(get_db)
) -> List[JobResponse]
```

**查询参数**:
- `category`: 岗位类别
- `city`: 工作城市
- `salary_min`: 最低薪资
- `salary_max`: 最高薪资

**响应**: 岗位列表数组

---

#### 3. 获取单个岗位
```python
@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
) -> JobResponse
```

**响应**: 单个岗位详情

---

#### 4. 推荐岗位卡片
```python
@router.get("/recommended/cards", response_model=List[JobCardResponse])
def get_recommended_jobs(
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    salary_range: Optional[str] = Query(None),  # e.g. 15k-20k
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[JobCardResponse]
```

---

#### 5. 面试统计
```python
@router.get("/stats/candidate", response_model=InterviewStatsResponse)
def get_interview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> InterviewStatsResponse
```

---

### 岗位需求管理 (job_requirements.py)

#### 6. 从 JD 自动生成需求
```python
@router.post("/requirements/create-from-jd", response_model=dict)
async def create_requirements_from_jd(
    job_id: int = Query(...),
    jd_text: str = Query(...),
    role_category: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict
```

**请求示例**:
```bash
POST /jobs/requirements/create-from-jd?job_id=1&jd_text=我们寻求...&role_category=backend
```

**响应**:
```json
{
  "code": 200,
  "message": "岗位需求已生成",
  "data": {
    "skills_count": 5,
    "tags_count": 3,
    "personality_framework": {...}
  }
}
```

**权限**: ✅ 岗位创建者（HR）

---

#### 7. 手动更新岗位需求
```python
@router.post("/requirements/update", response_model=dict)
async def update_job_requirements(
    request: JobRequirementInputSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict
```

**请求体**:
```json
{
  "job_id": 1,
  "jd_text": "可选的JD文本",
  "skills": [
    {
      "skill_name": "Python",
      "skill_type": "programming_language",
      "required_level": "expert",
      "years_experience": 3,
      "is_must_have": true,
      "priority_score": 9
    }
  ],
  "requirement_tags": [
    {
      "capability_name": "Python 编程",
      "capability_category": "技能",
      "importance_level": "high",
      "proficiency_required": "精通",
      "personality_dimension": "conscientiousness",
      "personality_min": 60,
      "personality_max": 100,
      "personality_weight": 1.5
    }
  ],
  "personality_framework": {
    "openness_min": 50,
    "openness_max": 100,
    "conscientiousness_min": 70,
    "conscientiousness_max": 100,
    "extraversion_min": 60,
    "extraversion_max": 100,
    "agreeableness_min": 40,
    "agreeableness_max": 100,
    "neuroticism_min": 0,
    "neuroticism_max": 50
  }
}
```

**响应**:
```json
{
  "code": 200,
  "message": "岗位需求已更新",
  "data": {
    "job_id": 1,
    "skills_count": 5,
    "tags_count": 3
  }
}
```

**权限**: ✅ 岗位创建者

---

#### 8. 获取岗位需求详情
```python
@router.get("/requirements/{job_id}", response_model=JobRequirementFullSchema)
async def get_job_requirements(
    job_id: int,
    db: Session = Depends(get_db)
) -> JobRequirementFullSchema
```

**响应**:
```json
{
  "job_id": 1,
  "job_name": "高级 Python 工程师",
  "job_description": "...",
  "skills": [...],
  "requirement_tags": [...],
  "personality_framework": {...}
}
```

---

#### 9. 候选人应聘岗位
```python
@router.post("/apply", response_model=CandidateJobApplicationResponseSchema)
async def apply_for_job(
    request: CandidateJobApplicationInputSchema,
    db: Session = Depends(get_db)
) -> CandidateJobApplicationResponseSchema
```

**请求体**:
```json
{
  "candidate_id": 5,
  "job_id": 1,
  "notes": "我很感兴趣"
}
```

---

#### 10. 获取候选人应聘记录
```python
@router.get("/applications/{candidate_id}", response_model=List[CandidateJobApplicationResponseSchema])
async def get_candidate_applications(
    candidate_id: int,
    db: Session = Depends(get_db)
) -> List[CandidateJobApplicationResponseSchema]
```

---

#### 11. 获取岗位和候选人匹配度
```python
@router.get("/match/{candidate_id}/{job_id}", response_model=JobMatchResultSchema)
async def get_job_match(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db)
) -> JobMatchResultSchema
```

---

## 数据库模型

### 1. Job（岗位表）
**文件**: `backend/models/job.py`

```python
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)           # 岗位名称
    description = Column(String(500), nullable=False)    # 岗位描述
    company = Column(String(100), nullable=False)        # 公司名称
    category = Column(String(50), nullable=False)        # 岗位类别
    city = Column(String(50), nullable=False)            # 工作城市
    salary_min = Column(Float, nullable=False)           # 最低薪资(k)
    salary_max = Column(Float, nullable=False)           # 最高薪资(k)
    required_traits = Column(JSON, nullable=False)       # 大五人格需求
    
    # 外键关系
    creator_id = Column(Integer, ForeignKey("users.id")) # 创建者ID(HR)
    creator = relationship("User", back_populates="jobs")
    
    # 反向关系
    interviews = relationship("Interview", cascade="all, delete")
    requirement_tags = relationship("JobRequirementTag", cascade="all, delete")
    skill_requirements = relationship("JobSkillRequirement", cascade="all, delete")
    personality_framework = relationship("JobPersonalityFramework", uselist=False, cascade="all, delete")
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 岗位名称 |
| description | String(500) | 岗位描述 |
| company | String(100) | 公司名称 |
| category | String(50) | 岗位类别：backend/frontend/product/design/hr/management |
| city | String(50) | 工作城市 |
| salary_min | Float | 最低薪资(单位k) |
| salary_max | Float | 最高薪资(单位k) |
| required_traits | JSON | 大五人格预期值 |
| creator_id | Integer | 创建者ID(外键) |

---

### 2. JobSkillRequirement（岗位技能需求表）
**文件**: `backend/models/job_requirement.py`

```python
class JobSkillRequirement(Base):
    __tablename__ = "job_skill_requirements"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    skill_name = Column(String(100), nullable=False)     # 技能名称(Python/React等)
    skill_type = Column(String(50), nullable=False)      # 技能类型
    required_level = Column(String(30))                  # 所需等级: junior/intermediate/expert
    years_experience = Column(Integer, nullable=True)    # 所需经验年数
    is_must_have = Column(Boolean, default=False)        # 是否必需
    priority_score = Column(Float, default=5)            # 优先级分(1-10)
    
    job = relationship("Job", back_populates="skill_requirements")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| skill_name | String | 技能名称，如 Python, React, SQL |
| skill_type | String | 技能类型：programming_language/framework/tool/methodology |
| required_level | String | 等级：junior/intermediate/expert |
| years_experience | Integer | 所需经验年数 |
| is_must_have | Boolean | 是否为必需技能 |
| priority_score | Float | 优先级(1-10) |

---

### 3. JobRequirementTag（岗位需求标签表）
**文件**: `backend/models/job_requirement.py`

```python
class JobRequirementTag(Base):
    __tablename__ = "job_requirement_tags"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # 能力项配置
    capability_name = Column(String(100), nullable=False)         # 能力名称: 需求分析等
    capability_category = Column(String(50), nullable=False)      # 类别: 技能/经验/素质
    importance_level = Column(String(20), default="medium")       # 重要性: high/medium/low
    proficiency_required = Column(String(50))                     # 所需等级: 精通/熟练/了解
    
    # 大五人格期望范围
    personality_dimension = Column(String(50))                    # 人格维度名
    personality_min = Column(Float, default=40)                   # 最小分值(0-100)
    personality_max = Column(Float, default=100)                  # 最大分值(0-100)
    personality_weight = Column(Float, default=1.0)               # 权重
    
    job = relationship("Job", back_populates="requirement_tags")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

### 4. JobPersonalityFramework（岗位大五人格框架表）
**文件**: `backend/models/job_requirement.py`

```python
class JobPersonalityFramework(Base):
    __tablename__ = "job_personality_frameworks"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    
    # 5个人格维度，每个都有:
    # - _min: 最低分值 (0-100)
    # - _max: 最高分值 (0-100)
    # - _weight: 权重 (0.1-5)
    
    openness_min = Column(Float, default=30)
    openness_max = Column(Float, default=100)
    openness_weight = Column(Float, default=1.0)
    
    conscientiousness_min = Column(Float, default=50)
    conscientiousness_max = Column(Float, default=100)
    conscientiousness_weight = Column(Float, default=1.5)
    
    extraversion_min = Column(Float, default=20)
    extraversion_max = Column(Float, default=100)
    extraversion_weight = Column(Float, default=1.0)
    
    agreeableness_min = Column(Float, default=40)
    agreeableness_max = Column(Float, default=100)
    agreeableness_weight = Column(Float, default=1.0)
    
    neuroticism_min = Column(Float, default=0)
    neuroticism_max = Column(Float, default=60)
    neuroticism_weight = Column(Float, default=1.2)
    
    description = Column(Text, nullable=True)  # 框架说明
    
    job = relationship("Job", back_populates="personality_framework", uselist=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**5个人格维度** ($0-100$分):
1. **Openness** (开放性): 想象力、好奇心、对新事物的接受度
2. **Conscientiousness** (尽责性): 有组织性、可靠性、责任感
3. **Extraversion** (外向性): 社交性、热情度、活力
4. **Agreeableness** (宜人性): 友好性、合作精神、同理心
5. **Neuroticism** (神经质): 情绪稳定性（越低越好）

---

### 5. CandidateJobApplication（候选人应聘记录表）
**文件**: `backend/models/job_requirement.py`

```python
class CandidateJobApplication(Base):
    __tablename__ = "candidate_job_applications"
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    application_status = Column(String(50))  # applied/shortlisted/rejected/offered
    match_score = Column(Float, nullable=True)  # 匹配度分数
    match_reason = Column(Text, nullable=True)  # 匹配原因
    notes = Column(Text, nullable=True)  # 应聘备注
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 已实现的功能

### ✅ 后端实现

| 功能 | API 端点 | 方法 | 权限 | 状态 |
|------|---------|------|------|------|
| 创建岗位 | POST `/jobs/` | create_job | HR | ✅ |
| 获取岗位列表 | GET `/jobs/` | get_jobs | 公开 | ✅ |
| 获取单个岗位 | GET `/jobs/{job_id}` | get_job | 公开 | ✅ |
| 获取推荐岗位 | GET `/jobs/recommended/cards` | get_recommended_jobs | 认证用户 | ✅ |
| 从JD生成需求 | POST `/jobs/requirements/create-from-jd` | create_requirements_from_jd | HR | ✅ |
| 手动编辑需求 | POST `/jobs/requirements/update` | update_job_requirements | HR | ✅ |
| 获取需求详情 | GET `/jobs/requirements/{job_id}` | get_job_requirements | 公开 | ✅ |
| 候选人应聘 | POST `/jobs/apply` | apply_for_job | 候选人 | ✅ |
| 获取应聘记录 | GET `/jobs/applications/{candidate_id}` | get_candidate_applications | 候选人 | ✅ |
| 计算匹配度 | GET `/jobs/match/{candidate_id}/{job_id}` | get_job_match | 公开 | ✅ |

### ✅ 前端实现

| 功能 | 组件 | 状态 |
|------|------|------|
| 显示岗位列表 | HRHomeView.vue | ✅ |
| 显示岗位统计卡片 | HRHomeView.vue | ✅ |
| 岗位管理仪表板 | JobManageView.vue | ✅ |
| HR编辑需求 (UI) | JobRequirementsManager.vue | ✅ |
| 从JD解析需求 (UI) | JobRequirementsManager.vue | ✅ |
| 候选人应聘 (UI) | JobRequirementsManager.vue | ✅ |
| 获取岗位推荐 | JobCard.vue | ✅ |

### ✅ 数据库实现

| 表 | 功能 | 状态 |
|----|------|------|
| jobs | 存储岗位基本信息 | ✅ |
| job_skill_requirements | 存储技能需求 | ✅ |
| job_requirement_tags | 存储能力标签 | ✅ |
| job_personality_frameworks | 存储人格框架 | ✅ |
| candidate_job_applications | 存储应聘记录 | ✅ |

---

## 缺失的功能

### 🚫 后端缺失

| 功能 | 预期端点 | 优先级 | 说明 |
|------|---------|------|------|
| **编辑岗位** | PUT/PATCH `/jobs/{job_id}` | 🔴 高 | HR需要能修改岗位基本信息(名称、描述、薪资等) |
| **删除岗位** | DELETE `/jobs/{job_id}` | 🔴 高 | HR需要能删除岗位，且需要级联删除相关需求 |
| **岗位状态更新** | PATCH `/jobs/{job_id}/status` | 🟡 中 | 改变岗位状态 (开放/关闭/暂停等) |
| **岗位搜索** | GET `/jobs/search` | 🟡 中 | 全文搜索岗位 |
| **获取我的岗位** | GET `/jobs/my-jobs` | 🟡 中 | 获取当前HR创建的岗位 |
| **岗位选项列表** | GET `/jobs/categories` | 🟢 低 | 获取可用的岗位类别、城市等选项 |
| **删除技能需求** | DELETE `/jobs/{job_id}/skills/{skill_id}` | 🟢 低 | 删除单个技能 |
| **删除标签需求** | DELETE `/jobs/{job_id}/tags/{tag_id}` | 🟢 低 | 删除单个标签 |
| **更新应聘状态** | PATCH `/jobs/applications/{app_id}/status` | 🟡 中 | 更新候选人应聘状态 |

### 🚫 前端缺失

| 功能 | 组件 | 优先级 | 说明 |
|------|------|------|------|
| **岗位创建对话框** | HRHomeView.vue | 🔴 高 | 实现创建岗位的表单对话框 |
| **岗位编辑页面** | JobEditView.vue | 🔴 高 | 编辑现有岗位的页面 |
| **岗位删除确认** | HRHomeView.vue | 🔴 高 | 实现删除岗位的API调用 |
| **编辑需求更新** | JobRequirementsManager.vue | 🟡 中 | 保存按钮需要调用API |
| **需求生成UI** | JobRequirementsManager.vue | 🟡 中 | JD解析完成后的显示优化 |
| **岗位搜索功能** | JobManageView.vue | 🟡 中 | 实现搜索框的搜索逻辑 |
| **岗位排序功能** | JobManageView.vue | 🟡 中 | 实现排序方式的切换 |
| **岗位统计刷新** | HRHomeView.vue | 🟢 低 | 实时更新统计数据 |

### 🚫 API 集成缺失

**前端 API 文件**: `frontend/src/api/job.ts`

```typescript
// 缺失的 API 调用函数

/**
 * 编辑岗位
 */
export const updateJob = (jobId: number, data: {
  name?: string
  description?: string
  company?: string
  category?: string
  city?: string
  salary_min?: number
  salary_max?: number
}) => {
  return request.put(`/jobs/${jobId}`, data)
}

/**
 * 删除岗位
 */
export const deleteJob = (jobId: number) => {
  return request.delete(`/jobs/${jobId}`)
}

/**
 * 获取当前HR的岗位列表
 */
export const getMyJobs = () => {
  return request.get('/jobs/my-jobs')
}

/**
 * 获取岗位类别和城市选项
 */
export const getJobOptions = () => {
  return request.get('/jobs/options')
}
```

---

## API 调用示例

### 前端调用示例

#### 1. HR 创建岗位
```typescript
import { createJob } from '@/api/job'

// 调用
const response = await createJob({
  name: '高级前端工程师',
  description: '负责前端框架开发',
  company: '阿里巴巴',
  category: 'frontend',
  city: '杭州',
  salary_min: 25,
  salary_max: 40,
  required_traits: {
    openness: 8,
    conscientiousness: 8,
    extraversion: 7,
    agreeableness: 7,
    neuroticism: 3
  }
})
```

#### 2. HR 从JD生成需求
```typescript
import { createJobRequirementsFromJD } from '@/api/job'

const response = await createJobRequirementsFromJD({
  job_id: 1,
  jd_text: '我们需要一名有5年React经验的前端工程师...',
  role_category: 'frontend'
})

// 响应示例
{
  "code": 200,
  "message": "岗位需求已生成",
  "data": {
    "skills_count": 5,
    "tags_count": 3,
    "personality_framework": {
      "openness_min": 50,
      "conscientiousness_min": 70,
      ...
    }
  }
}
```

#### 3. HR 手动编辑需求
```typescript
import { updateJobRequirements } from '@/api/job'

const response = await updateJobRequirements({
  job_id: 1,
  skills: [
    {
      skill_name: 'React',
      skill_type: 'framework',
      required_level: 'expert',
      years_experience: 5,
      is_must_have: true,
      priority_score: 10
    },
    {
      skill_name: 'TypeScript',
      skill_type: 'programming_language',
      required_level: 'expert',
      years_experience: 3,
      is_must_have: true,
      priority_score: 9
    }
  ],
  requirement_tags: [
    {
      capability_name: 'React 开发',
      capability_category: '技能',
      importance_level: 'high',
      proficiency_required: '精通',
      personality_dimension: 'conscientiousness',
      personality_min: 70,
      personality_max: 100,
      personality_weight: 1.5
    }
  ],
  personality_framework: {
    openness_min: 50,
    openness_max: 100,
    conscientiousness_min: 70,
    conscientiousness_max: 100,
    extraversion_min: 60,
    extraversion_max: 100,
    agreeableness_min: 40,
    agreeableness_max: 100,
    neuroticism_min: 0,
    neuroticism_max: 50
  }
})
```

#### 4. 获取岗位需求详情
```typescript
import { getJobRequirements } from '@/api/job'

const requirements = await getJobRequirements(1)
// 返回完整的岗位需求信息
```

#### 5. 候选人应聘岗位
```typescript
import { applyForJob } from '@/api/job'

const response = await applyForJob({
  candidate_id: 5,
  job_id: 1,
  notes: '非常感兴趣这个职位'
})
```

#### 6. 获取候选人应聘记录
```typescript
import { getCandidateApplications } from '@/api/job'

const applications = await getCandidateApplications(candidateId)
// 返回该候选人的所有应聘记录
```

#### 7. 获取匹配度评分
```typescript
import { getJobMatch } from '@/api/job'

const matchResult = await getJobMatch(candidateId, jobId)
// 返回匹配度结果和分析
```

---

## 实现建议

### 🎯 优先级 1（必须实现）

1. **DELETE /jobs/{job_id}** - 删除岗位
   - 后端：验证权限，级联删除相关需求记录
   - 前端：在 HRHomeView 中实现删除按钮的 API 调用

2. **PUT /jobs/{job_id}** - 编辑岗位
   - 后端：更新岗位基本信息
   - 前端：创建 JobEditView 页面

3. **前端岗位创建表单** - HRHomeView 中的创建对话框实现

### 🎯 优先级 2（推荐实现）

1. **GET /jobs/my-jobs** - 获取当前用户的岗位
2. **PATCH /jobs/{job_id}/status** - 修改岗位状态
3. **搜索和排序功能** - JobManageView 中的搜索和排序

### 🎯 优先级 3（优化实现）

1. **岗位选项 API** - 获取类别、城市等下拉列表
2. **细粒度的技能/标签删除** API
3. **应聘状态更新** API

---

## 数据库关系图

```
┌─────────────────┐
│     users       │
│  (HR 用户)       │
└────────┬────────┘
         │
         │ creator_id
         │
         ▼
┌─────────────────────────────┐
│        jobs                 │
│ (岗位基本信息)              │
├─────────────────────────────┤
│ • id (PK)                   │
│ • name                      │
│ • description               │
│ • company                   │
│ • category                  │
│ • city                      │
│ • salary_min/max            │
│ • required_traits (JSON)    │
│ • creator_id (FK)           │
└──┬────────┬────────┬────────┘
   │        │        │
   │        │        └──────────────────────┐
   │        │                               │
   ▼        ▼                               ▼
┌────────────────────┐    ┌──────────────────────────┐    ┌────────────────────┐
│ job_skill_         │    │ job_requirement_tags     │    │ job_personality_   │
│ requirements       │    │ (能力标签)               │    │ frameworks         │
│ (技能需求)        │    │                          │    │ (人格框架)         │
├────────────────────┤    ├──────────────────────────┤    ├────────────────────┤
│ • id (PK)         │    │ • id (PK)               │    │ • id (PK)          │
│ • job_id (FK)     │    │ • job_id (FK)           │    │ • job_id (FK)      │
│ • skill_name      │    │ • capability_name       │    │ • openness_min/max │
│ • skill_type      │    │ • capability_category   │    │ • conscientiousness│
│ • required_level  │    │ • importance_level      │    │ • extraversion     │
│ • years_exp       │    │ • proficiency_required  │    │ • agreeableness    │
│ • is_must_have    │    │ • personality_*         │    │ • neuroticism_*    │
│ • priority_score  │    └──────────────────────────┘    │ • description      │
└────────────────────┘                                   └────────────────────┘

                       candidate_job_applications
                    (候选人应聘记录 - 关联表)
                    ├── candidate_id (FK→users)
                    ├── job_id (FK→jobs)
                    ├── application_status
                    ├── match_score
                    └── created_at
```

---

## 总结

### 全面的岗位管理功能已实现：

✅ **后端基础**：完整的 CRUD API（除了 UPDATE/DELETE）
✅ **前端UI**：岗位管理仪表板和需求编辑器
✅ **数据结构**：5 个相关数据库表
✅ **需求管理**：JD自动解析和结构化需求

### 主要缺陷：

🚫 **编辑岗位** - 需要 PUT API 和对应前端页面
🚫 **删除岗位** - 需要 DELETE API 和前端确认
🚫 **表单提交** - HR 创建/编辑表单的 API 调用实现
🚫 **岗位状态** - 缺少岗位状态流转机制

**建议**：优先实现删除和编辑功能，这是 HR 日常运营的核心需求。

