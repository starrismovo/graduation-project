# 前后端集成说明文档

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 + TypeScript)                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ HomeView.vue (主页)                                      │  │
│  │ ├─ 顶部欢迎区                                            │  │
│  │ ├─ 面试统计卡片                                          │  │
│  │ ├─ 筛选条件区 (岗位类型、城市、薪资)                    │  │
│  │ ├─ 热门岗位推荐区                                        │  │
│  │ ├─ 快速入口区 (立即面试、我的报告等)                    │  │
│  │ └─ 底部信息区                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓↑                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API 请求层 (src/utils/request.ts)                      │  │
│  │ └─ getHomePageData()  [主要使用]                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            HTTP
┌─────────────────────────────────────────────────────────────────┐
│                     后端 (FastAPI + SQLAlchemy)                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 路由层 (routers/)                                        │  │
│  │ ├─ auth.py (认证)                                        │  │
│  │ ├─ job.py (岗位管理 + 推荐)                              │  │
│  │ └─ interview.py (面试管理)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↓↑                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 模型层 (models/)                                         │  │
│  │ ├─ User (用户)                                           │  │
│  │ ├─ Job (岗位)                                            │  │
│  │ └─ Interview (面试)                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│           ↓↑                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 数据库 (MySQL)                                           │  │
│  │ ├─ users 表                                              │  │
│  │ ├─ jobs 表                                               │  │
│  │ └─ interviews 表                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 数据流向

### 1. 用户加载主页

```
时间序列：
1. 用户登录成功 → 跳转到 /home
2. HomeView.vue 组件挂载 (onMounted)
3. 调用 getHomePageData() 
   └─ HTTP GET http://localhost:8000/jobs/home/data
4. 后端接收请求 (GET /jobs/home/data)
   ├─ 查询当前用户的面试统计
   ├─ 查询推荐岗位列表（支持筛选）
   └─ 返回聚合数据
5. 前端接收响应，更新 UI
   ├─ interviewStats 显示统计信息
   └─ recommendedJobs 显示岗位卡片
```

### 2. 用户筛选岗位

```
时间序列：
1. 用户选择筛选条件（岗位类型、城市、薪资）
2. 触发 onFilterChange() 事件
3. 再次调用 getHomePageData(filters)
   └─ HTTP GET /jobs/home/data?category=技术岗&city=杭州&salary_range=25k-35k
4. 后端根据过滤条件返回岗位
5. 前端更新 recommendedJobs 列表
```

### 3. 用户开始面试

```
时间序列：
1. 用户点击岗位卡片的 "开始面试" 按钮
2. 调用 goToInterview(jobId)
3. 发起 POST /interviews/ 请求
   └─ Body: { job_id: 1 }
4. 后端创建面试记录
   └─ 返回: { id: 1, candidate_id: X, job_id: 1, status: "started", ... }
5. 前端获取 interviewId
6. 跳转到面试页面: /interview/{interviewId}
```

### 4. 用户随机开始面试

```
时间序列：
1. 用户点击 "立即面试" 按钮
2. 调用 randomInterview()
3. 随机选择 recommendedJobs 中的一个岗位
4. 调用 goToInterview(randomJob.id)
5. 同上...
```

---

## API 调用清单

### 已实现的 API 端点

| 方法 | 路由 | 功能 | 前端使用 |
|------|------|------|---------|
| GET | `/jobs/home/data` | 获取主页所有数据（推荐） | ✅ HomeView.vue |
| GET | `/jobs/recommended/cards` | 获取推荐岗位卡片 | ⚠️ 如需单独调用 |
| GET | `/jobs/stats/candidate` | 获取面试统计 | ⚠️ 如需单独调用 |
| GET | `/jobs/` | 岗位列表（支持筛选） | 🔮 未来使用 |
| GET | `/jobs/{id}` | 岗位详情 | 🔮 未来使用 |
| POST | `/interviews/` | 开始面试 | ✅ HomeView.vue |
| GET | `/interviews/{id}` | 面试详情 | 🔮 未来使用 |
| GET | `/interviews/candidate/{id}` | 候选人所有面试 | 🔮 我的报告页 |
| PUT | `/interviews/{id}` | 提交面试结果 | 🔮 面试结束后 |
| DELETE | `/interviews/{id}` | 删除面试记录 | 🔮 未来使用 |

**图例**：
- ✅ 已在前端使用
- ⚠️ 可选调用（冗余API）
- 🔮 未来开发时使用

---

## 请求/响应格式

### 获取主页数据

**请求**：
```
GET /jobs/home/data?category=技术岗&city=杭州&salary_range=25k-35k
```

**响应** (200 OK):
```json
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
      "company": "阿里巴巴",
      "city": "杭州",
      "category": "技术岗",
      "salary": "25k-35k",
      "description": "负责React框架下的前端业务开发...",
      "applied": true
    },
    ...
  ],
  "user_username": "bob",
  "user_is_hr": false
}
```

### 开始面试

**请求**：
```
POST /interviews/
Content-Type: application/json

{
  "job_id": 1
}
```

**响应** (201 Created):
```json
{
  "id": 10,
  "candidate_id": 2,
  "job_id": 1,
  "status": "started",
  "personality_traits": null,
  "match_score": null,
  "created_at": "2026-02-02T10:30:00",
  "completed_at": null,
  "notes": null
}
```

**错误响应** (400 Bad Request):
```json
{
  "detail": "您已经对该岗位进行过面试"
}
```

---

## 前端代码使用示例

### 1. 在 HomeView.vue 中

```typescript
// 导入API函数
import { getHomePageData, startInterview } from '../utils/request'

// 加载数据
const loadHomeData = async () => {
  try {
    const response = await getHomePageData({
      category: filters.value.jobType || undefined,
      city: filters.value.city || undefined,
      salary_range: filters.value.salary || undefined
    })
    
    // 解构响应数据
    const { stats, recommended_jobs } = response.data
    interviewStats.value = stats
    recommendedJobs.value = recommended_jobs
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

// 开始面试
const goToInterview = async (jobId: number) => {
  try {
    const response = await startInterview(jobId)
    const { id } = response.data  // 面试ID
    router.push(`/interview/${id}`)
  } catch (error) {
    ElMessage.error('开始面试失败')
  }
}
```

### 2. 在其他组件中

```typescript
// 获取候选人的所有面试
import { getCandidateInterviews } from '../utils/request'

const interviews = await getCandidateInterviews(userId, 'completed')

// 获取特定面试的详情
import { getInterviewDetail } from '../utils/request'

const interview = await getInterviewDetail(interviewId)

// 提交面试结果
import { updateInterview } from '../utils/request'

await updateInterview(interviewId, {
  status: 'completed',
  personality_traits: { openness: 7.5, ... },
  match_score: 82.5
})
```

---

## 后端代码关键点

### 1. 数据模型关系

[models/user.py]
```python
class User(Base):
    interviews = relationship("Interview", back_populates="candidate")
```

[models/job.py]
```python
class Job(Base):
    interviews = relationship("Interview", back_populates="job")
```

[models/interview.py]
```python
class Interview(Base):
    candidate = relationship("User", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
```

### 2. 权限验证

```python
def get_current_user(db: Session = Depends(get_db)):
    # TODO: 从JWT token中提取用户ID
    return db.query(User).filter(User.id == 1).first()

# 在API中使用
@router.post("/interviews/")
def start_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_hr == False:  # 候选人检查
        raise HTTPException(status_code=403)
```

### 3. 应用了约束

在 Interview 表中：
```sql
UNIQUE KEY unique_interview (candidate_id, job_id)
```

确保同一候选人对同一岗位只能有一个面试记录。

---

## 环境配置

### 前端 (.env.local 或 vite.config.ts)

```typescript
// 在 src/utils/request.ts 中硬编码
const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 15000
})
```

### 后端 (.env)

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/hr_matching?charset=utf8mb4
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 运行步骤

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python init_test_data.py      # 初始化测试数据
uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看API文档

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 打开应用

### 3. 测试流程

1. 使用测试用户登录
   - 用户名: bob
   - 密码: password123

2. 进入主页，查看：
   - 面试统计信息（应从后端获取）
   - 推荐岗位列表（应从后端获取）

3. 筛选岗位（选择类别、城市、薪资）

4. 点击 "开始面试"
   - 应该调用 POST /interviews/
   - 跳转到面试页面（暂未实现）

---

## 常见问题

### Q: 为什么 getHomePageData 只调用一个API？
A: 这是前后端协议设计的优化。后端的 `/jobs/home/data` 端点一次性返回所有主页需要的数据（统计信息 + 推荐岗位），而不需要前端分别调用多个API。这样：
- 减少网络请求次数
- 减少前端逻辑复杂度
- 后端可以高效地批量查询数据

### Q: 当前用户是如何确定的？
A: 目前在 `get_current_user()` 函数中硬编码为 ID=1。在实现完整认证时，需要从JWT token中提取用户ID。

### Q: 怎样实现真正的权限控制？
A: 
1. 登录时返回JWT token
2. 前端存储token
3. 前端每次请求时在header中添加token
4. 后端验证token并提取用户信息

### Q: 如何处理岗位不存在的情况？
A: 后端会返回 404 错误，前端需要捕获并显示错误信息。

### Q: 同一用户能否对同一岗位多次面试？
A: 不能。数据库中有UNIQUE约束，防止重复。如果尝试会返回 400 错误。

---

## 未来扩展

### 短期（第一阶段）
- [ ] 实现完整JWT认证
- [ ] 创建面试页面和答题功能
- [ ] 实现AI题目生成

### 中期（第二阶段）
- [ ] 创建报告页面
- [ ] 实现自动评分和匹配算法
- [ ] 创建HR后台管理系统

### 长期（第三阶段）
- [ ] 实现大五人格心理测评
- [ ] 实现图表统计功能
- [ ] 部署到生产环境

---

## 调试技巧

### 1. 查看网络请求

浏览器开发者工具 → Network 标签
- 查看请求URL
- 查看请求参数
- 查看响应数据

### 2. 查看后端日志

```
INFO:     127.0.0.1:60848 - "GET /jobs/home/data HTTP/1.1" 200 OK
```

### 3. 使用Swagger测试API

访问 http://localhost:8000/docs

### 4. 使用curl测试

```bash
curl -X GET "http://localhost:8000/jobs/home/data"
```

### 5. 检查数据库

```bash
mysql -u root -p
use hr_matching;
SELECT * FROM jobs;
SELECT * FROM interviews;
```

---

## 最后总结

✅ **已完成的工作**
- 设计了完整的数据模型
- 创建了完整的API端点
- 编写了前端UI和API调用逻辑
- 编写了详细的文档

⚠️ **下一步要做的**
- 测试所有API端点
- 完成面试页面和答题功能
- 实现JWT认证机制
- 完成报告页面
