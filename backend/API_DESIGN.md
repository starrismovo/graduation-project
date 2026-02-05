# 后端 API 设计方案

## 概述
为前端候选人主页和面试功能设计的完整后端 API。

---

## 数据模型

### 1. User（用户）
```
id: int (主键)
username: str (用户名，唯一)
email: str (邮箱，唯一)
hashed_password: str (密码哈希)
is_hr: bool (是否为HR用户，False=候选人，True=HR)
```

**关系：**
- 一个用户可以创建多个岗位（如果是HR）
- 一个用户可以参加多个面试（如果是候选人）

---

### 2. Job（岗位）
```
id: int (主键)
name: str (岗位名称，如"前端开发工程师")
description: str (岗位描述)
company: str (公司名称)
category: str (岗位类别：技术岗、产品岗、设计岗、运营岗等)
city: str (工作城市)
salary_min: float (最低薪资，单位k)
salary_max: float (最高薪资，单位k)
required_traits: json (大五人格需求，如{"openness": 8, ...})
creator_id: int (创建者ID，外键)
```

**关系：**
- 每个岗位由一个HR用户创建
- 一个岗位可以有多个面试记录

---

### 3. Interview（面试）
```
id: int (主键)
candidate_id: int (候选人ID，外键)
job_id: int (岗位ID，外键)
status: enum (面试状态：started/in_progress/completed/passed/failed)
personality_traits: json (候选人的大五人格得分，如{"openness": 6.5, ...})
match_score: float (岗位匹配度，0-100)
created_at: datetime (创建时间)
completed_at: datetime (完成时间，可空)
notes: str (备注)
```

**关系：**
- 每个面试关联一个候选人和一个岗位
- 候选人和岗位的唯一性约束：一个候选人对一个岗位最多只能有一个面试记录

---

## API 端点设计

### 认证相关 `/auth`
> 已有实现，保持不变

#### POST `/auth/register`
注册新用户
```json
请求：
{
  "username": "string",
  "email": "string",
  "password": "string",
  "is_hr": boolean (可选，默认false)
}

响应：
{
  "access_token": "string",
  "token_type": "bearer"
}
```

#### POST `/auth/login`
用户登录
```json
请求：
{
  "username": "string",
  "password": "string"
}

响应：
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

### 岗位管理 `/jobs`

#### POST `/jobs/`
HR创建岗位
```json
请求：
{
  "name": "前端开发工程师",
  "description": "负责React框架下的前端业务开发",
  "company": "阿里巴巴",
  "category": "技术岗",
  "city": "杭州",
  "salary_min": 25,
  "salary_max": 35,
  "required_traits": {
    "openness": 8,
    "conscientiousness": 9,
    "extraversion": 7,
    "agreeableness": 6,
    "neuroticism": 3
  }
}

响应：
{
  "id": 1,
  "name": "前端开发工程师",
  ...
  "creator_id": 1
}
```

#### GET `/jobs/`
获取岗位列表（支持筛选）
```
查询参数：
- category: string (可选，岗位类别)
- city: string (可选，工作城市)
- salary_min: float (可选，最低薪资)
- salary_max: float (可选，最高薪资)

响应：
[
  {
    "id": 1,
    "name": "前端开发工程师",
    ...
  },
  ...
]
```

#### GET `/jobs/{job_id}`
获取单个岗位详情
```
路径参数：
- job_id: int

响应：
{
  "id": 1,
  "name": "前端开发工程师",
  ...
}
```

#### GET `/jobs/recommended/cards` ⭐ 前端主页使用
获取推荐岗位卡片（用于主页展示）
```
查询参数：
- category: string (可选)
- city: string (可选)
- salary_range: string (可选，格式如"15k-20k")

响应：
[
  {
    "id": 1,
    "name": "前端开发工程师",
    "company": "阿里巴巴",
    "city": "杭州",
    "category": "技术岗",
    "salary": "25k-35k",
    "description": "负责React框架下的前端业务开发",
    "applied": false  // 是否已应聘
  },
  ...
]
```

#### GET `/jobs/stats/candidate` ⭐ 前端主页使用
获取候选人的面试统计信息
```
响应：
{
  "completed": 2,      // 已完成的面试数
  "in_progress": 1,    // 进行中的面试数
  "total": 5,          // 总应聘数
  "passed": 1          // 通过筛选数
}
```

#### GET `/jobs/home/data` ⭐ 前端主页使用（推荐）
一次性获取主页所需的所有数据
```
查询参数：
- category: string (可选)
- city: string (可选)
- salary_range: string (可选，如"15k-20k")

响应：
{
  "stats": {
    "completed": 2,
    "in_progress": 1,
    "total": 5,
    "passed": 1
  },
  "recommended_jobs": [
    {
      "id": 1,
      "name": "前端开发工程师",
      ...
      "applied": false
    },
    ...
  ],
  "user_username": "张三",
  "user_is_hr": false
}
```

---

### 面试管理 `/interviews`

#### POST `/interviews/`
候选人开始一个岗位的面试
```json
请求：
{
  "job_id": 1
}

响应：
{
  "id": 1,
  "candidate_id": 1,
  "job_id": 1,
  "status": "started",
  "personality_traits": null,
  "match_score": null,
  "created_at": "2026-02-02T10:00:00",
  "completed_at": null,
  "notes": null
}
```

#### GET `/interviews/{interview_id}`
获取面试详情
```
路径参数：
- interview_id: int

响应：
{
  "id": 1,
  "candidate_id": 1,
  "job_id": 1,
  "status": "completed",
  "personality_traits": {
    "openness": 6.5,
    "conscientiousness": 8.0,
    ...
  },
  "match_score": 78.5,
  "created_at": "2026-02-02T10:00:00",
  "completed_at": "2026-02-02T10:30:00",
  "notes": "表现不错",
  "job": { ... },
  "candidate_name": "张三"
}
```

#### GET `/interviews/candidate/{candidate_id}`
获取候选人的所有面试记录
```
路径参数：
- candidate_id: int

查询参数：
- status: string (可选，筛选状态)

响应：
[
  {
    "id": 1,
    "candidate_id": 1,
    "job_id": 1,
    ...
  },
  ...
]
```

#### PUT `/interviews/{interview_id}`
更新面试记录（提交面试结果）
```json
请求：
{
  "status": "completed",
  "personality_traits": {
    "openness": 6.5,
    "conscientiousness": 8.0,
    "extraversion": 7.2,
    "agreeableness": 5.8,
    "neuroticism": 4.1
  },
  "match_score": 78.5,
  "notes": "表现良好"
}

响应：
{
  "id": 1,
  ...
  "status": "completed",
  ...
}
```

#### DELETE `/interviews/{interview_id}`
删除面试记录（只有候选人可以）
```
路径参数：
- interview_id: int

响应：
{
  "message": "面试记录已删除"
}
```

---

## 前端调用示例

### 获取主页数据（推荐方式）
```typescript
// 一个请求获取所有主页数据
const response = await fetch('http://localhost:8000/jobs/home/data?category=技术岗&city=杭州')
const data = await response.json()

// 使用数据
console.log(data.stats)              // 面试统计
console.log(data.recommended_jobs)  // 推荐岗位
console.log(data.user_username)     // 用户名
```

### 开始面试
```typescript
const response = await fetch('http://localhost:8000/interviews/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ job_id: 1 })
})
const interview = await response.json()
```

### 提交面试结果
```typescript
const response = await fetch(`http://localhost:8000/interviews/${interview_id}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    status: 'completed',
    personality_traits: { ... },
    match_score: 75.5
  })
})
```

---

## 数据库 Schema

### users 表
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_hr BOOLEAN DEFAULT 0
);
```

### jobs 表
```sql
CREATE TABLE jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NOT NULL,
    company VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    salary_min FLOAT NOT NULL,
    salary_max FLOAT NOT NULL,
    required_traits JSON NOT NULL,
    creator_id INT NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);
```

### interviews 表
```sql
CREATE TABLE interviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    personality_traits JSON,
    match_score FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    notes VARCHAR(500),
    FOREIGN KEY (candidate_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    UNIQUE KEY unique_interview (candidate_id, job_id)
);
```

---

## 说明

1. **默认用户**: 当前所有API都假设当前用户的ID为1，实际生产中应该通过JWT token获取当前用户信息。

2. **筛选功能**: 
   - 岗位列表支持按类别、城市、薪资筛选
   - 前端主页的筛选条件会自动传递到后端

3. **权限控制**:
   - HR用户可以创建岗位
   - 候选人可以参加面试
   - 只能查看/删除自己的面试记录

4. **推荐的前端调用**:
   - 使用 `/jobs/home/data` 一次性获取主页所需数据
   - 而不是分别调用多个API

5. **后续扩展**:
   - 实现完整的JWT认证机制
   - 添加 AI 面试问题生成和评分
   - 添加报告生成功能
   - 添加搜索和分页功能
