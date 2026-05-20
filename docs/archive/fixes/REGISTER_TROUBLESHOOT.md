## 注册错误排查清单

如果遇到 CORS 错误或 500 错误，请按以下步骤检查：

### 1️⃣ 检查后端是否运行

```bash
cd backend
python test_db.py
```

应该看到:
```
✓ 成功导入 database 模块
✓ 成功连接到数据库
✓ 数据库查询正常: (1,)
```

### 2️⃣ 启动后端服务

```bash
cd backend
uvicorn main:app --reload --port 8000
```

应该看到:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 3️⃣ 测试 /docs API 文档

浏览器打开: http://127.0.0.1:8000/docs

应该看到 Swagger UI，包含 `/auth/register` 和 `/auth/login` 端点

### 4️⃣ 前端启动

```bash
cd frontend
npm run dev
```

### 5️⃣ 在浏览器打开

http://localhost:5173

### 常见错误及解决方案

#### ❌ CORS 错误: "No 'Access-Control-Allow-Origin' header"
- **原因**: 后端没有运行
- **解决**: 确保后端在 http://127.0.0.1:8000 运行

#### ❌ 500 Internal Server Error
- **原因**: 数据库连接失败或其他服务器错误
- **解决**:
  1. 运行 `python test_db.py` 检查数据库
  2. 检查后端控制台的错误信息
  3. 确保 MySQL 服务运行，database_url 正确

#### ❌ "用户名已存在" 错误
- **原因**: 该用户已注册
- **解决**: 使用不同的用户名

#### ❌ "邮箱已被注册" 错误
- **原因**: 该邮箱已被注册
- **解决**: 使用不同的邮箱

### 测试账户 (如果数据库初始化成功)

- 用户名: bob
- 密码: password123
- 身份: 候选人

- 用户名: hr_admin
- 密码: hr123456
- 身份: HR

### 如果以上都不工作

1. 清空浏览器 localStorage: 
   - 按 F12 → Application → Local Storage → 清空所有

2. 重启后端和前端

3. 查看浏览器控制台 (F12) 的具体错误信息

4. 查看后端终端的完整错误栈
