# 🎉 后端设计方案总结

## 📋 项目概览

为前端新设计的候选人主页实现完整的后端支持，包括数据模型、API端点、权限控制和集成方案。

---

## ✨ 核心设计原则

1. **RESTful API设计** - 遵循HTTP方法和状态码规范
2. **数据聚合** - `/jobs/home/data` 一个端点获取所有主页数据
3. **权限隔离** - HR和候选人角色分开处理
4. **数据完整性** - 使用数据库约束防止重复面试记录

---

## 🗂️ 新增/修改的文件

### 新增文件

| 文件 | 说明 |
|------|------|
| `backend/models/interview.py` | 面试数据模型 |
| `backend/routers/interview.py` | 面试管理API路由 |
| `backend/schemas/schemas.py` | Pydantic Schema定义 |
| `backend/init_test_data.py` | 测试数据初始化脚本 |
| `backend/API_DESIGN.md` | 详细API设计文档 |
| `backend/DEVELOPMENT.md` | 开发说明文档 |
| `INTEGRATION_GUIDE.md` | 前后端集成指南 |
| `API_REFERENCE.md` | API快速参考 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `backend/main.py` | 添加interview路由 |
| `backend/models/user.py` | 添加interviews关系 |
| `backend/models/job.py` | 新增字段(company, category, city, salary_min/max) |
| `backend/routers/job.py` | 新增推荐/统计/聚合API |
| `backend/requirements.txt` | 补充项目依赖 |
| `frontend/src/utils/request.ts` | 添加API调用函数 |
| `frontend/src/views/HomeView.vue` | 集成实时API调用 |

---

## 🔌 数据模型

### Interview（面试）模型

```python
class Interview(Base):
    # 基础字段
    id: 主键
    candidate_id: 候选人ID (FK→users)
    job_id: 岗位ID (FK→jobs)
    
    # 面试信息
    status: 状态 (started/in_progress/completed/passed/failed)
    personality_traits: 大五人格得分 (JSON)
    match_score: 岗位匹配度 (0-100)
    
    # 时间戳
    created_at: 创建时间
    completed_at: 完成时间
    notes: 备注信息
```

### Job 模型更新

新增字段：
- `company`: 公司名称
- `category`: 岗位类别 (技术岗、产品岗等)
- `city`: 工作地点
- `salary_min`: 最低薪资 (k)
- `salary_max`: 最高薪资 (k)

### User 模型更新

新增关系：
```python
interviews = relationship("Interview", back_populates="candidate")
```

---

## 🔑 重点API端点

### ⭐ GET `/jobs/home/data` - 主页数据聚合

**使用场景**：前端加载主页时调用一次

**参数**（可选）：
- `category`: 岗位类别
- `city`: 城市
- `salary_range`: 薪资范围 (如"25k-35k")

**响应**：
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
      "description": "...",
      "applied": false
    }
  ],
  "user_username": "bob",
  "user_is_hr": false
}
```

### POST `/interviews/` - 开始面试

**请求**：
```json
{ "job_id": 1 }
```

**响应**：
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

### PUT `/interviews/{id}` - 提交面试结果

**请求**：
```json
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
  "notes": "表现良好"
}
```

### GET `/interviews/candidate/{id}` - 获取候选人所有面试

**参数**（可选）：
- `status`: 筛选状态

**响应**：面试记录列表

---

## 📊 前端集成方案

### HomeView.vue 关键改进

```typescript
// 1. 组件挂载时加载数据
onMounted(() => {
  loadHomeData()
})

// 2. 调用主页数据API
const loadHomeData = async () => {
  const response = await getHomePageData({
    category: filters.value.jobType,
    city: filters.value.city,
    salary_range: filters.value.salary
  })
  interviewStats.value = response.data.stats
  recommendedJobs.value = response.data.recommended_jobs
}

// 3. 筛选条件变化时重新加载
const onFilterChange = () => {
  loadHomeData()
}

// 4. 开始面试时创建面试记录
const goToInterview = async (jobId: number) => {
  const response = await startInterview(jobId)
  router.push(`/interview/${response.data.id}`)
}
```

---

## 🚀 快速开始

### 1. 后端初始化

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化测试数据（8个岗位 + 2个用户）
python init_test_data.py

# 启动服务
uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看Swagger文档

### 2. 前端运行

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173

### 3. 测试账户

- **用户名**: bob
- **密码**: password123
- **角色**: 候选人

---

## 📈 技术栈

### 后端
- **框架**: FastAPI (现代、高性能)
- **ORM**: SQLAlchemy
- **数据库**: MySQL
- **认证**: JWT (待完善)
- **校验**: Pydantic

### 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP**: Axios

---

## ✅ 功能清单

### 已实现

- [x] Interview 数据模型
- [x] 所有关键API端点
- [x] 筛选和搜索功能
- [x] 权限验证框架
- [x] 前端集成代码
- [x] 测试数据初始化
- [x] 完整API文档
- [x] 开发指南

### 待实现

- [ ] 完整JWT认证
- [ ] 面试页面和答题功能
- [ ] AI题目生成
- [ ] 报告生成
- [ ] HR后台管理系统
- [ ] 数据分析统计

---

## 🎯 API调用流程

```
用户登录成功
    ↓
进入主页 (/home)
    ↓
HomeView.onMounted()
    ↓
GET /jobs/home/data ← 一次请求获取所有数据
    ↓
显示统计信息和推荐岗位
    ↓
用户筛选条件 → 重新调用 GET /jobs/home/data
    ↓
用户点击"开始面试"
    ↓
POST /interviews/ (创建面试记录)
    ↓
跳转到面试页面 /interview/{id}
    ↓
用户完成答题
    ↓
PUT /interviews/{id} (提交结果)
    ↓
生成报告（未来实现）
```

---

## 📝 文档导航

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [API_DESIGN.md](backend/API_DESIGN.md) | 详细API规范 | 后端开发者 |
| [DEVELOPMENT.md](backend/DEVELOPMENT.md) | 开发指南和技巧 | 后端开发者 |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | 前后端集成 | 全栈开发者 |
| [API_REFERENCE.md](API_REFERENCE.md) | 快速参考卡片 | 快速查询 |

---

## 🔍 数据流可视化

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                       │
│                                                             │
│  HomeView.vue                                              │
│  ├─ 统计卡片 (completed, in_progress, total, passed)      │
│  ├─ 筛选条件 (category, city, salary)                     │
│  ├─ 岗位卡片 (name, company, city, salary, description)   │
│  ├─ 快速入口 (立即面试、我的报告等)                        │
│  └─ 每次筛选条件变化 → getHomePageData()                   │
└─────────────────────────────────────────────────────────────┘
                         ↓↑ HTTP REST API
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│                                                             │
│  /jobs/home/data (核心端点)                                 │
│  ├─ 查询面试统计 → interviews表                            │
│  ├─ 查询推荐岗位 → jobs表 (with 筛选)                      │
│  ├─ 检查是否已应聘 → interviews表                          │
│  └─ 返回聚合数据                                           │
│                                                             │
│  /interviews/ (POST - 开始面试)                            │
│  ├─ 检查重复 (UNIQUE约束)                                  │
│  ├─ 创建记录                                               │
│  └─ 返回 interview_id                                      │
└─────────────────────────────────────────────────────────────┘
                         ↓↑ SQL 查询
┌─────────────────────────────────────────────────────────────┐
│                  Database (MySQL)                           │
│                                                             │
│  users          jobs           interviews                   │
│  ├─ id          ├─ id          ├─ id                        │
│  ├─ username    ├─ name        ├─ candidate_id (FK)        │
│  ├─ email       ├─ company     ├─ job_id (FK)              │
│  ├─ is_hr       ├─ category    ├─ status                    │
│  └─ ...         ├─ city        ├─ match_score              │
│                 ├─ salary_min  └─ created_at               │
│                 ├─ salary_max                              │
│                 └─ required_traits                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 最佳实践

1. **始终使用 `/jobs/home/data`** 而不是分别调用多个API
2. **前端应在 onMounted 时加载数据** 而不是在路由导航前
3. **使用 try-catch 处理所有API调用**
4. **显示loading状态** 提升用户体验
5. **合理处理错误信息** 并反馈给用户

---

## 🔧 部署清单

- [ ] 配置生产环境 `.env`
- [ ] 禁用FastAPI调试模式
- [ ] 配置数据库备份
- [ ] 实现完整JWT认证
- [ ] 添加日志系统
- [ ] 配置HTTPS
- [ ] 性能优化（缓存、索引）
- [ ] 部署到云服务器

---

## 📞 支持

### 常见问题

**Q: 为什么重复点击会报错？**
A: 数据库约束防止同一候选人对同一岗位重复申请。

**Q: 如何测试所有API？**
A: 访问 http://localhost:8000/docs 使用Swagger UI。

**Q: 数据如何持久化？**
A: 所有数据存储在MySQL数据库，自动持久化。

### 调试技巧

- 使用浏览器DevTools的Network标签查看请求/响应
- 查看后端控制台日志了解处理过程
- 使用curl测试API: `curl -X GET http://localhost:8000/jobs/`

---

## 🎓 学习资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM教程](https://docs.sqlalchemy.org/en/20/orm/)
- [RESTful API设计规范](https://restfulapi.net/)
- [Pydantic数据校验](https://docs.pydantic.dev/)

---

**版本**: 1.0  
**最后更新**: 2026年2月2日  
**维护者**: 开发团队
