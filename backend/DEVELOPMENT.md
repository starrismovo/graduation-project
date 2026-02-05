# 后端开发说明文档

## 文件结构

```
backend/
├── main.py                  # FastAPI应用主入口
├── database.py              # 数据库连接配置
├── requirements.txt         # 项目依赖
├── API_DESIGN.md           # API设计文档
├── init_test_data.py       # 测试数据初始化脚本
├── .env                    # 环境变量配置
├── models/
│   ├── __init__.py
│   ├── user.py             # 用户模型
│   ├── job.py              # 岗位模型
│   └── interview.py        # 面试模型（新增）
├── routers/
│   ├── auth.py             # 认证路由
│   ├── job.py              # 岗位路由（已更新）
│   └── interview.py        # 面试路由（新增）
├── schemas/
│   └── schemas.py          # Pydantic模型定义（新增）
└── prompts/
    └── (AI提示词配置，暂未实现)
```

---

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置 .env 文件

确保 `.env` 文件包含以下配置：

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/hr_matching?charset=utf8mb4
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. 初始化数据库

```bash
python init_test_data.py
```

这会创建：
- 测试用户（HR + 候选人）
- 8个示例岗位
- 完整的数据库表结构

### 4. 启动后端服务

```bash
python -m uvicorn main:app --reload --port 8000
```

访问 `http://localhost:8000/docs` 查看 Swagger API 文档

---

## 数据模型关系图

```
User (用户)
├─ jobs → Job (岗位)
└─ interviews → Interview (面试)

Job (岗位)
├─ creator → User (创建者)
└─ interviews → Interview (面试)

Interview (面试)
├─ candidate → User (候选人)
└─ job → Job (岗位)
```

---

## 新增功能说明

### Interview 模型（面试）

**作用**：记录候选人对岗位的面试过程和结果

**字段**：
- `id`: 面试记录唯一ID
- `candidate_id`: 候选人ID（外键→User）
- `job_id`: 岗位ID（外键→Job）
- `status`: 面试状态（started/in_progress/completed/passed/failed）
- `personality_traits`: 候选人的大五人格得分
- `match_score`: 岗位匹配度（0-100）
- `created_at`: 创建时间
- `completed_at`: 完成时间
- `notes`: 备注信息

**约束**：
- 同一候选人对同一岗位只能有一个面试记录（UNIQUE约束）

### 岗位模型更新（Job）

新增字段：
- `company`: 公司名称
- `category`: 岗位类别（技术岗、产品岗、设计岗等）
- `city`: 工作城市
- `salary_min`: 最低薪资（k）
- `salary_max`: 最高薪资（k）

这些字段用于前端的筛选和岗位卡片展示。

---

## 重要 API 端点

### 获取主页数据（推荐）
```
GET /jobs/home/data
```
一次请求获取：
- 面试统计信息
- 推荐岗位列表（支持筛选）
- 用户信息

**使用场景**：前端加载主页时调用

### 开始面试
```
POST /interviews/
Body: { "job_id": 1 }
```

### 获取面试详情
```
GET /interviews/{interview_id}
```

### 提交面试结果
```
PUT /interviews/{interview_id}
Body: {
  "status": "completed",
  "personality_traits": {...},
  "match_score": 78.5
}
```

---

## 与前端的集成

### 前端调用路径

1. **登录后加载主页**
   ```typescript
   // 调用这个API
   GET /jobs/home/data?category=技术岗&city=杭州
   
   // 返回的数据结构
   {
     stats: { completed, in_progress, total, passed },
     recommended_jobs: [ { id, name, company, city, category, salary, description, applied }, ... ],
     user_username: "张三",
     user_is_hr: false
   }
   ```

2. **用户点击"开始面试"按钮**
   ```typescript
   // 调用这个API
   POST /interviews/
   Body: { job_id: 1 }
   
   // 返回面试ID，跳转到面试页面
   ```

3. **进行面试答题**
   - 前端收集候选人的心理测试答题数据
   - 计算大五人格得分和匹配度

4. **提交面试结果**
   ```typescript
   // 调用这个API
   PUT /interviews/{interview_id}
   Body: {
     status: "completed",
     personality_traits: { ... },
     match_score: 78.5
   }
   ```

---

## 权限控制说明

### 当前实现
- 所有API都假设当前用户ID为1
- 这是临时实现，用于开发测试

### 未来改进
需要实现完整的JWT认证：
1. 在登录时返回JWT token
2. 前端在请求头中携带token
3. 后端从token提取用户信息

**Token提取函数示例**：
```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: int = payload.get("sub")
    # 从数据库查询用户
    return db.query(User).filter(User.id == user_id).first()
```

---

## 常见开发任务

### 1. 添加新的API端点

在对应的路由文件中添加：

```python
@router.post("/some-endpoint")
def some_endpoint(data: SomeSchema, db: Session = Depends(get_db)):
    # 实现逻辑
    pass
```

### 2. 修改数据模型

编辑 `models/*.py` 文件，然后运行：
```bash
python init_test_data.py
```

### 3. 生成新的测试数据

编辑 `init_test_data.py`，修改 `jobs_data` 列表，然后运行脚本。

### 4. 调试API

访问 `http://localhost:8000/docs` 使用Swagger UI测试API

或使用curl：
```bash
curl -X GET "http://localhost:8000/jobs/home/data"
```

---

## 数据校验和错误处理

### 响应状态码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权/未登录
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器错误

### 错误响应格式

```json
{
  "detail": "错误信息描述"
}
```

---

## 性能优化建议

1. **添加数据库索引**
   - user.username
   - user.email
   - job.category
   - job.city
   - interview.candidate_id
   - interview.job_id

2. **添加分页功能**
   ```python
   skip: int = Query(0, ge=0),
   limit: int = Query(10, ge=1, le=100)
   ```

3. **缓存常用数据**
   - 岗位列表（变化不频繁）
   - 用户统计信息（定期更新）

4. **异步处理**
   - 面试结果生成报告
   - 邮件通知

---

## 部署注意事项

### 生产环境配置

1. **禁用调试模式**
   ```python
   # main.py
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

2. **使用生产级数据库驱动**
   - 不要使用 `echo=True`
   - 配置连接池

3. **实现完整认证**
   - JWT token机制
   - 刷新token逻辑

4. **添加日志系统**
   - 记录所有API请求
   - 记录错误堆栈

5. **安全配置**
   - 不在代码中硬编码密钥
   - 使用环境变量
   - 启用HTTPS

---

## 常见问题

### Q: 如何修改某个岗位的信息？
A: 当前API没有实现PUT更新端点。可以添加：
```python
@router.put("/{job_id}")
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(get_db)):
    ...
```

### Q: 如何支持分页？
A: 在GET端点添加查询参数：
```python
skip: int = Query(0), limit: int = Query(10)
query = query.offset(skip).limit(limit)
```

### Q: 如何删除岗位？
A: 类似添加PUT端点，增加DELETE端点

### Q: 如何生成面试报告？
A: 在 `InterviewUpdate` 请求时，后端可以调用AI服务生成报告

---

## 下一步工作

- [ ] 实现完整的JWT认证
- [ ] 添加分页功能
- [ ] 实现AI面试问题生成
- [ ] 实现自动评分和报告生成
- [ ] 添加邮件通知功能
- [ ] 实现HR面试管理后台
- [ ] 添加数据分析和统计功能
