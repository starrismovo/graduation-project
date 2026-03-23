# 数据库迁移验证和 API 测试指南

完整的测试和验证流程，用于确保数据库迁移成功、ORM 模型正确映射、API 端点工作正常。

## 📋 概述

数据库迁移后需要执行三层验证：
1. **ORM CRUD 测试** - 验证数据库连接和基本操作
2. **数据一致性测试** - 验证外键约束和级联删除
3. **API 集成测试** - 验证端点和新字段映射

## 🚀 快速开始

```bash
# 1. 进入后端目录
cd backend

# 2. 运行 ORM CRUD 测试
python test_orm_crud.py

# 3. 运行数据一致性测试
python test_data_consistency.py

# 4. 启动后端服务
python main.py

# （在另一个终端）
# 5. 运行 API 集成测试
python test_api_integration.py

# 6. 浏览 API 文档
# 访问: http://localhost:8000/docs
```

---

## 📊 测试脚本详解

### 1️⃣ ORM CRUD 测试 (`test_orm_crud.py`)

**目的**: 验证所有 ORM 模型能够正确读写新字段

**测试覆盖**:
- ✅ User 模型 (包含 user_type, age, education, desired_job 等新字段)
- ✅ Interview 模型 (包含 is_deleted, deleted_at)
- ✅ AssessmentRecord 模型 (包含 is_deleted, deleted_at, created_by)
- ✅ InterviewResponse 模型 (包含 assessment_id)
- ✅ Job 模型 (包含 creator 关系)
- ✅ 所有关系映射验证

**运行方式**:
```bash
python test_orm_crud.py
```

**预期输出**:
```
✅ 创建候选人用户成功
✅ 候选人用户字段验证成功
✅ 创建 HR 用户成功
✅ HR 用户字段验证成功
✅ 创建面试记录成功
✅ 面试记录关系验证成功
...
✅ 所有 CRUD 测试通过
```

**成功标准**:
- 所有 6 个测试部分都显示 ✅
- 没有异常错误
- 所有新字段都能读写

---

### 2️⃣ 数据一致性测试 (`test_data_consistency.py`)

**目的**: 验证数据库约束和级联删除正确工作

**测试覆盖**:
- ✅ 级联删除 - 删除候选人时级联删除相关面试
- ✅ 外键约束 - 验证无效 FK 会被拒绝
- ✅ 软删除隔离 - is_deleted=1 的记录不被查询
- ✅ 孤立记录检查 - 检测是否有破损的 FK 引用
- ✅ 索引性能 - 验证新索引是否存在

**运行方式**:
```bash
python test_data_consistency.py
```

**预期输出**:
```
测试 1: 级联删除
✅ 删除前面试数: 2
✅ 级联删除成功，删除后面试数: 0

测试 2: 外键约束验证
✅ 无效 FK 被正确拒绝 (异常类型: IntegrityError)

测试 3: 软删除隔离
✅ 未删除记录数: 1
✅ 软删除工作正常

测试 4: 孤立记录检查
✅ 未发现孤立记录

测试 5: 索引性能
✅ idx_users_type 索引存在
```

**成功标准**:
- 所有 5 个测试都显示 ✅
- 没有意外错误
- 外键约束生效

---

### 3️⃣ API 集成测试 (`test_api_integration.py`)

**目的**: 验证 API 端点能够正确处理新字段

**测试覆盖**:
- ✅ 用户注册 (is_hr 字段)
- ✅ 用户登录 (返回 user_type)
- ✅ 获取个人信息 (返回新字段)
- ✅ 更新个人信息 (支持新字段)
- ✅ API 文档访问 (/docs, /redoc)

**运行方式**:
```bash
# 1. 启动后端服务
python main.py &

# 2. 在另一个终端运行 API 测试
python test_api_integration.py
```

**预期输出**:
```
🚀 API 集成测试

测试 1️⃣: 用户注册
✅ 候选人注册成功 - ID: 101
✅ HR 用户注册成功 - ID: 102

测试 2️⃣: 用户登录
✅ 候选人登录成功
   Token: eyJhbGciOiJIUzI1NiIsInR5...

测试 3️⃣: 获取和更新用户信息
✅ 成功获取个人信息
✅ 成功更新个人信息

测试 4️⃣: FastAPI 自动文档
✅ Swagger 文档可访问: http://localhost:8000/docs
✅ ReDoc 文档可访问: http://localhost:8000/redoc
```

**成功标准**:
- 所有注册/登录返回 200 状态码
- 个人信息包含 age, education, major 等字段
- /docs 和 /redoc 返回 200

---

## 🔍 手动验证清单

### 使用 Postman 或 FastAPI Swagger 验证

#### 1. 访问 API 文档
```
URL: http://localhost:8000/docs
```

#### 2. 注册端点验证
```
POST /auth/register

请求体:
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "TestPass123",
  "is_hr": false  // 验证是否支持
}

期望响应:
{
  "user_id": 123,
  "username": "test_user",
  "is_hr": false,
  "user_type": "candidate"  // 验证自动设置
}

验证项:
[ ] is_hr 字段被接受
[ ] user_type 自动设置为 'candidate' 或 'hr'
[ ] 用户被成功创建
```

#### 3. 登录端点验证
```
POST /auth/login

请求体 (form-data):
{
  "username": "test_user",
  "password": "TestPass123"
}

期望响应:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "username": "test_user",
    "user_type": "candidate"  // 验证返回
  }
}

验证项:
[ ] 返回有效的 JWT token
[ ] user 对象包含 user_type
```

#### 4. 个人信息端点验证
```
GET /user/profile
Header: Authorization: Bearer {token}

期望响应:
{
  "user_id": 123,
  "username": "test_user",
  "email": "test@example.com",
  "user_type": "candidate",
  // 新字段
  "age": 28,
  "education": "本科",
  "major": "计算机科学",
  "desired_job": "后端工程师",
  "experience_years": 3.5,
  "skills": ["Python", "Java"],
  // 其他字段
  "real_name": "张三",
  "phone": "13800138000"
}

验证项:
[ ] 返回 user_type 字段
[ ] 返回 age, education, major 等新字段
[ ] 返回 experience_years, skills 字段
[ ] 没有返回 hashed_password
```

#### 5. 更新个人信息端点验证
```
PATCH /user/profile
Header: Authorization: Bearer {token}

请求体:
{
  "age": 29,
  "education": "硕士",
  "major": "人工智能",
  "desired_job": "AI 工程师",
  "experience_years": 4.5,
  "skills": ["Python", "PyTorch", "TensorFlow"],
  "bio": "专注 AI 领域"
}

期望响应:
{
  "message": "Profile updated successfully",
  "user": {
    "age": 29,
    "education": "硕士",
    "major": "人工智能",
    ...
  }
}

验证项:
[ ] 端点返回 200
[ ] 所有新字段都被更新
[ ] 数据库确实更新了（通过第二次 GET 验证）
```

#### 6. 删除用户端点验证（级联删除）
```
DELETE /user/{user_id}
Header: Authorization: Bearer {admin_token}

期望行为:
1. 删除用户
2. 关联的 interview 记录应被级联删除
3. 关联的 assessment_record 应被软删除（is_deleted=1）

验证项:
[ ] 用户被成功删除（或软删除）
[ ] 删除后无法查询用户信息
[ ] 查询该用户的面试: 应返回空
[ ] 检查数据库: interviews 表中无相关记录
```

---

## 🐛 常见问题和排查

### 问题 1: ORM CRUD 测试失败 - 找不到模块

**错误信息**: `ModuleNotFoundError: No module named 'models'`

**原因**: 不在正确的目录

**解决**:
```bash
cd backend
python test_orm_crud.py
```

### 问题 2: ORM 测试失败 - 数据库连接错误

**错误信息**: `OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")`

**原因**: MySQL 服务未运行

**解决**:
```bash
# Windows
net start MySQL80
# 或 Mac
brew services start mysql
# 验证
mysql -u root -p
```

### 问题 3: API 测试失败 - 后端不可用

**错误信息**: `Connection error: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded`

**原因**: 后端服务未启动

**解决**:
```bash
cd backend
python main.py
# 验证
curl http://localhost:8000/
```

### 问题 4: 注册失败 - 用户已存在

**错误信息**: `{"detail": "User already exists"}`

**原因**: 测试用户已存在

**解决**:
```bash
# 修改 test_api_integration.py 中的用户名
test_candidate = {
    "username": "test_candidate_api_2",  # 改变用户名
    ...
}
```

### 问题 5: user_type 字段找不到

**错误信息**: `AttributeError: 'User' object has no attribute 'user_type'`

**原因**: ORM 模型未更新或数据库列未添加

**解决**:
```bash
# 检查数据库
mysql> DESC users;
# 应该显示 user_type 列

# 检查 models/user.py
grep "user_type" models/user.py

# 如果没有，需要重新运行迁移
python fix_migration.py
```

---

## ✅ 完整验证流程

按顺序执行以下步骤确保完整验证：

### 第 1 阶段: 数据库层验证

```bash
# 1. 运行 ORM CRUD 测试
cd backend
python test_orm_crud.py
# 预期: ✅ 所有 6 个部分通过

# 2. 运行数据一致性测试  
python test_data_consistency.py
# 预期: ✅ 所有 5 个测试通过
```

**检查点**:
- [ ] User CRUD 正常工作
- [ ] Interview CRUD 正常工作
- [ ] AssessmentRecord 有 audit 字段
- [ ] 外键约束生效
- [ ] 级联删除正常
- [ ] 索引存在

### 第 2 阶段: API 层验证

```bash
# 1. 启动后端
python main.py
# 应显示: INFO:     Uvicorn running on http://127.0.0.1:8000

# 2. 运行 API 集成测试（新终端）
python test_api_integration.py
# 预期: ✅ 注册、登录、信息获取成功
```

**检查点**:
- [ ] 注册返回 user_id 和 user_type
- [ ] 登录返回有效 token
- [ ] 个人信息包含新字段
- [ ] 能更新新字段值

### 第 3 阶段: 手动功能测试

```
1. 打开浏览器访问 http://localhost:8000/docs
2. 按照"手动验证清单"中的步骤进行测试
3. 验证所有核心接口
4. 特别关注 user_type 字段流向
```

**检查点**:
- [ ] 注册时可选择 is_hr
- [ ] user_type 正确转换
- [ ] 登录响应包含 user_type
- [ ] 个人档案显示所有候选人字段
- [ ] 能更新候选人特定字段

### 如果所有测试通过 ✅

可以进行最后的清理：

```bash
# 1. 删除备份表（可选，保留以防万一）
# cd backend
# python -c "from db import engine; engine.execute('DROP TABLE users_backup'); engine.execute('DROP TABLE candidates_backup')"

# 2. 删除测试脚本（可选，可保留用于未来回归测试）
# rm test_orm_crud.py test_data_consistency.py test_api_integration.py

# 3. 更新 API 路由以完全支持新字段
# 编辑 routers/auth.py, routers/user.py 等文件
```

---

## 📝 API 端点需要更新的列表

根据数据库迁移，以下端点需要调整：

### auth.py
- [ ] `/auth/register` - 添加 user_type 返回
- [ ] `/auth/login` - 返回中包含 user_type

### user.py
- [ ] `GET /user/profile` - 添加新字段到响应
- [ ] `PATCH /user/profile` - 支持更新新字段
- [ ] 创建 UserResponse schema 包含新字段

### candidate.py
- [ ] 重构为使用 User 表（is_hr=false）而非 Candidate 表
- [ ] 更新查询过滤条件为 user_type='candidate'

### interview.py
- [ ] 验证 FK 映射为 users 表而非 candidates 表
- [ ] 添加 is_deleted 过滤到查询

### assessment.py
- [ ] 添加 created_by 字段支持
- [ ] 添加 is_deleted 过滤到查询

---

## 🔗 相关文档

- [DATABASE_STRUCTURE_ANALYSIS.md](DATABASE_STRUCTURE_ANALYSIS.md) - 数据库结构分析
- [BACKEND_IMPLEMENTATION_SUMMARY.md](BACKEND_IMPLEMENTATION_SUMMARY.md) - 实现总结
- [MIGRATION_REPORT.md](MIGRATION_REPORT.md) - 迁移执行报告

---

## 🎯 成功标准总结

| 层级 | 测试项 | 状态 |
|-----|--------|------|
| 数据库 | ORM CRUD | [ ] |
| 数据库 | 数据一致性 | [ ] |
| API | 注册/登录 | [ ] |
| API | 个人信息 | [ ] |
| API | 字段映射 | [ ] |
| 集成 | 完整流程 | [ ] |

所有 ✅ 通过后，迁移完成！

---

**更新时间**: 2024-01-15
**版本**: 1.0
