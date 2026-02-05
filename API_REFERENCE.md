# 后端API快速参考

## 主页数据 ⭐ 最常用

```http
GET /jobs/home/data?category=技术岗&city=杭州&salary_range=25k-35k
```

**响应**：
```json
{
  "stats": { "completed": 2, "in_progress": 1, "total": 5, "passed": 1 },
  "recommended_jobs": [
    { "id": 1, "name": "...", "company": "...", "salary": "25k-35k", "applied": false },
    ...
  ],
  "user_username": "bob",
  "user_is_hr": false
}
```

---

## 面试相关

### 开始面试
```http
POST /interviews/
Content-Type: application/json

{ "job_id": 1 }
```

**响应**：
```json
{ "id": 10, "candidate_id": 2, "job_id": 1, "status": "started", ... }
```

### 获取面试详情
```http
GET /interviews/{interview_id}
```

### 提交面试结果
```http
PUT /interviews/{interview_id}
Content-Type: application/json

{
  "status": "completed",
  "personality_traits": {
    "openness": 7.5,
    "conscientiousness": 8.2,
    "extraversion": 6.1,
    "agreeableness": 7.8,
    "neuroticism": 3.5
  },
  "match_score": 82.5,
  "notes": "表现不错"
}
```

### 获取候选人所有面试
```http
GET /interviews/candidate/{candidate_id}?status=completed
```

### 删除面试记录
```http
DELETE /interviews/{interview_id}
```

---

## 岗位相关

### 获取岗位列表
```http
GET /jobs/?category=技术岗&city=杭州&salary_min=25&salary_max=35
```

### 获取推荐岗位卡片
```http
GET /jobs/recommended/cards?category=技术岗&city=杭州
```

### 获取单个岗位
```http
GET /jobs/{job_id}
```

### 获取面试统计
```http
GET /jobs/stats/candidate
```

**响应**：
```json
{
  "completed": 2,
  "in_progress": 1,
  "total": 5,
  "passed": 1
}
```

---

## 认证相关（已有）

### 注册
```http
POST /auth/register
Form-Data:
  username=bob
  email=bob@example.com
  password=password123
  is_hr=false
```

### 登录
```http
POST /auth/login
Form-Data:
  username=bob
  password=password123
```

---

## 前端调用示例

```typescript
import { 
  getHomePageData, 
  startInterview, 
  getInterviewDetail,
  updateInterview 
} from '../utils/request'

// 1. 加载主页数据
const data = await getHomePageData({ category: '技术岗', city: '杭州' })

// 2. 开始面试
const interview = await startInterview(jobId)

// 3. 获取面试详情
const detail = await getInterviewDetail(interviewId)

// 4. 提交面试结果
await updateInterview(interviewId, {
  status: 'completed',
  personality_traits: { ... },
  match_score: 75.5
})
```

---

## 数据库表结构速览

### users 表
```
id (PK) | username | email | hashed_password | is_hr
```

### jobs 表
```
id (PK) | name | description | company | category | city | 
salary_min | salary_max | required_traits (JSON) | creator_id (FK)
```

### interviews 表
```
id (PK) | candidate_id (FK) | job_id (FK) | status | 
personality_traits (JSON) | match_score | created_at | 
completed_at | notes
```

**约束**：
- UNIQUE(candidate_id, job_id) 在 interviews 表

---

## 状态码速查表

| 状态码 | 含义 | 例子 |
|--------|------|------|
| 200 | 成功 | 获取数据成功 |
| 201 | 创建成功 | 创建面试记录成功 |
| 400 | 请求错误 | 已对该岗位面试过 |
| 401 | 未授权 | 未登录 |
| 403 | 禁止访问 | HR不能参加面试 |
| 404 | 资源不存在 | 岗位/面试不存在 |
| 500 | 服务器错误 | 数据库连接失败 |

---

## 部署清单

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python init_test_data.py
uvicorn main:app --reload --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 测试用户
- 用户名: `bob`
- 密码: `password123`
- 角色: 候选人

---

## 测试岗位数据

系统自带8个测试岗位：

1. **前端开发工程师** - 阿里巴巴 - 杭州 - 25k-35k
2. **后端开发工程师** - 字节跳动 - 北京 - 30k-50k
3. **Python数据分析师** - 腾讯 - 深圳 - 22k-32k
4. **产品经理** - 美团 - 北京 - 25k-40k
5. **视觉设计师** - 网易 - 杭州 - 18k-28k
6. **运营专员** - 快手 - 上海 - 15k-25k
7. **机器学习工程师** - 百度 - 北京 - 35k-60k
8. **市场营销经理** - 小米 - 深圳 - 20k-35k

---

## 关键文件位置

### 后端
```
backend/
├── main.py                    # 入口
├── database.py                # 数据库配置
├── API_DESIGN.md             # 详细API设计
├── DEVELOPMENT.md            # 开发说明
├── init_test_data.py         # 初始化脚本
├── models/
│   ├── user.py
│   ├── job.py
│   └── interview.py          # ⭐ 新增
├── routers/
│   ├── auth.py
│   ├── job.py                # ⭐ 已更新
│   └── interview.py          # ⭐ 新增
└── schemas/
    └── schemas.py            # ⭐ 新增
```

### 前端
```
frontend/src/
├── views/
│   └── HomeView.vue          # ⭐ 已更新
├── utils/
│   └── request.ts            # ⭐ 已更新
├── stores/
│   └── user.ts
└── ...
```

### 项目根目录
```
graduation-project/
├── INTEGRATION_GUIDE.md      # ⭐ 集成文档
├── API_REFERENCE.md          # ⭐ 本文件
├── backend/
└── frontend/
```

---

## 常见错误排查

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 400: "您已经对该岗位进行过面试" | 重复申请 | 检查该岗位是否已面试 |
| 403: "HR用户无法参加面试" | 用户角色错误 | 使用候选人账户登录 |
| 404: "岗位不存在" | 岗位ID错误 | 检查岗位ID是否有效 |
| CORS错误 | 跨域问题 | 检查后端CORS配置 |
| 连接超时 | 后端未运行 | 确认后端已启动在8000端口 |

---

## 下次开发任务

1. **面试页面** (`/interview/:id`)
   - 显示岗位信息
   - 问题列表
   - 答题界面
   - 提交按钮 → 调用 `updateInterview()`

2. **报告页面** (`/reports`)
   - 调用 `getCandidateInterviews()`
   - 显示历史面试列表
   - 点击查看详情 → `getInterviewDetail()`

3. **完整认证**
   - 实现JWT token
   - 修改 `get_current_user()` 函数
   - 前端存储和发送token

4. **数据持久化**
   - 测试所有CRUD操作
   - 验证数据库约束
   - 处理并发问题
