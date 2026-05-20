# API 路由更新快速检验指南

## 🎯 验证步骤

### 步骤 1: 启动后端服务器
```powershell
cd D:\Desktop\graduation-project\backend
# 激活虚拟环境
venv\Scripts\Activate.ps1
# 启动 FastAPI
python main.py
```

### 步骤 2: 打开 Swagger UI 文档
访问: **http://127.0.0.1:8000/docs**

### 步骤 3: 通过 Swagger 测试每个端点

#### ✅ 注册端点测试 (POST /auth/register)

请求:
```json
{
  "username": "test_candidate_2024",
  "email": "test_candidate@example.com",
  "password": "password123",
  "is_hr": false
}
```

**验证点**:
- [ ] 返回 200 状态码
- [ ] 响应包含 `user_id`
- [ ] **新增**: 响应包含 `user_type: "CANDIDATE"`

---

#### ✅ 登录端点测试 (POST /auth/login)

请求:
```json
{
  "username": "test_candidate_2024",
  "password": "password123"
}
```

**验证点**:
- [ ] 返回 200 状态码
- [ ] 响应包含 `access_token`
- [ ] 响应包含 `is_hr: false`
- [ ] **新增**: 响应包含 `user_type: "CANDIDATE"`
- [ ] **新增**: 令牌中包含用户类型信息

---

#### ✅ 获取个人信息 (GET /user/profile)

请求头:
```
Authorization: Bearer <上一步获取的 access_token>
```

**验证点**:
- [ ] 返回 200 状态码
- [ ] 返回基本字段: id, username, email, nickname, real_name, phone, bio
- [ ] **新增**: 返回 `user_type: "CANDIDATE"`
- [ ] **新增**: 返回候选人字段:
  - `age` (int or null)
  - `education` (string or null)
  - `major` (string or null)
  - `desired_job` (string or null)
  - `experience_years` (float or null)
  - `skills` (list or null)
  - `resume_url` (string or null)

---

#### ✅ 更新个人信息 (PATCH /user/profile)

请求头:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

请求体 (所有字段可选):
```json
{
  "nickname": "小张",
  "real_name": "张三",
  "phone": "13800138000",
  "bio": "热爱用 Python 解决问题",
  "age": 28,
  "education": "本科",
  "major": "计算机科学与技术",
  "desired_job": "数据分析师",
  "experience_years": 3.5,
  "skills": ["Python", "SQL", "Excel", "Tableau"],
  "resume_url": "/uploads/resumes/my-resume.pdf"
}
```

**验证点**:
- [ ] 返回 200 状态码
- [ ] 返回更新后的完整用户信息
- [ ] **新增**: 返回包含所有新字段
- [ ] 所有更新的字段保存正确

---

#### ✅ 获取候选人基本信息 (GET /api/candidates/{candidate_id}/basic-info)

将 `{candidate_id}` 替换为实际的用户 ID (如: 14)

**验证点**:
- [ ] 返回 200 状态码 (如果 candidate_id 对应的是 CANDIDATE 类型用户)
- [ ] 返回 404 状态码 (如果 candidate_id 不存在或不是 CANDIDATE)
- [ ] 返回的字段: name, age, education, major, desired_job, experience_years, skills

---

#### ✅ 更新候选人基本信息 (POST /api/candidates/{candidate_id}/basic-info)

将 `{candidate_id}` 替换为实际的用户 ID (如: 14)

请求体:
```json
{
  "name": "李四",
  "age": 26,
  "education": "硕士",
  "major": "人工智能",
  "desired_job": "机器学习工程师",
  "experience_years": 2.0,
  "skills": ["Python", "TensorFlow", "PyTorch"]
}
```

**验证点**:
- [ ] 返回 200 状态码 (如果 candidate_id 对应 CANDIDATE 用户)
- [ ] 返回 404 状态码 (如果不是 CANDIDATE 用户)
- [ ] 返回的数据与请求一致

---

## 🛠️ 命令行快速测试

### 注册测试
```powershell
$data = @{
    username = "quicktest_$(Get-Random)"
    email = "quicktest_$(Get-Random)@example.com"
    password = "password123"
    is_hr = $false
}

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/auth/register" `
    -Method POST `
    -Body $data

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

### 登录测试
```powershell
$data = @{
    username = "test_candidate_2722"
    password = "password123"
}

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $data

$result = $response.Content | ConvertFrom-Json
$result | ConvertTo-Json
$token = $result.access_token
```

### 获取个人信息
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/user/profile" `
    -Method GET `
    -Headers $headers

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

---

## 📊 验证矩阵

| 功能 | 文件 | 状态 | 检验 |
|------|------|------|------|
| 注册返回 user_type | routers/auth.py | ✅ 完成 | [ ] |
| 登录返回 user_type | routers/auth.py | ✅ 完成 | [ ] |
| 个人信息包含新字段 | routers/user.py | ✅ 完成 | [ ] |
| 更新个人信息支持新字段 | routers/user.py | ✅ 完成 | [ ] |
| 候选人 API 迁移到 User 表 | routers/candidate.py | ✅ 完成 | [ ] |
| Schema 定义了新字段 | schemas/user.py | ✅ 完成 | [ ] |

---

## 🐛 常见问题排查

### 问题 1: 登录返回 401
**解决方案**:
- 确认用户名和密码正确
- 确认用户已成功注册
- 检查数据库中用户是否存在

### 问题 2: 返回 user_type 时出现 KeyError
**解决方案**:
- 检查数据库中该用户的 user_type 字段值
- 确认值为 'HR' 或 'CANDIDATE' (大写)
- 运行 `SELECT DISTINCT user_type FROM users;` 查看

### 问题 3: 更新时某些新字段没有保存
**解决方案**:
- 检查 UserProfileUpdate Schema 是否包含该字段
- 检查 routers/user.py 中的更新逻辑
- 检查数据库中对应的列是否存在

### 问题 4: 候选人 API 返回 404
**解决方案**:
- 确认 candidate_id 对应的用户存在
- 确认该用户的 user_type 为 'CANDIDATE'
- 检查数据库中的数据

---

## 📝 测试结果记录

运行日期: ______________

### 测试结果
- 注册: [ ] 通过 [ ] 失败
- 登录: [ ] 通过 [ ] 失败
- 获取个人信息: [ ] 通过 [ ] 失败
- 更新个人信息: [ ] 通过 [ ] 失败
- 候选人 API: [ ] 通过 [ ] 失败

### 备注
_____________________________________

---

✅ **所有验证完成后，API 路由更新可视为成功！**
