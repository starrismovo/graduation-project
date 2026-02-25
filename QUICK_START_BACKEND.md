# 🚀 AI 智能面试系统 - 快速开始指南

## 📋 目录

1. [系统要求](#系统要求)
2. [后端启动](#后端启动-5分钟)
3. [前端启动](#前端启动-3分钟)
4. [系统测试](#系统测试)
5. [常见问题](#常见问题)

---

## 💻 系统要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.8+ | 后端运行环境 |
| Node.js | 16+ | 前端构建工具 |
| MySQL | 5.7+ | 数据库 |
| Git | 任意 | 版本控制（可选） |

---

## 🛠️ 后端启动（5分钟）

### 步骤 1: 环境准备

```bash
# 1.1 进入后端目录
cd backend

# 1.2 创建虚拟环境（如果不存在）
python -m venv venv

# 1.3 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 步骤 2: 依赖安装

```bash
# 2.1 升级 pip（可选但推荐）
pip install --upgrade pip

# 2.2 安装项目依赖
pip install -r requirements.txt
```

**安装结果应该包括：**
```
✓ fastapi==0.104.1
✓ uvicorn==0.24.0
✓ sqlalchemy==2.0.23
✓ pymysql==1.1.0
✓ pydantic==2.5.0
✓ python-dotenv==1.0.0
```

### 步骤 3: 数据库配置

编辑 `backend/.env` 文件：

```env
# 示例 MySQL 连接字符串
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/assessment_db

# 如果使用本地默认 MySQL：
DATABASE_URL=mysql+pymysql://root:@localhost:3306/assessment_db
```

**或者创建数据库：**

```sql
-- MySQL 命令行
CREATE DATABASE IF NOT EXISTS assessment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE assessment_db;
```

### 步骤 4: 初始化数据库

```bash
# 4.1 运行初始化脚本
python init_assessment.py

# 4.2 预期输出：
# 🚀 正在初始化评估系统数据库...
# ✅ 数据库表创建完成
# ✅ 成功创建 5 个岗位
# ✅ 成功创建 3 个候选人心理特质记录
# ✅ 成功创建 3 个评估记录
# ✅ 成功创建 3 个匹配分析记录
# ✨ 评估系统初始化完成！
```

### 步骤 5: 启动服务

```bash
# 5.1 启动 Uvicorn 服务器
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5.2 预期输出：
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 步骤 6: 验证后端

在浏览器打开以下地址：

```
http://localhost:8000/
http://localhost:8000/docs          # Swagger UI 
http://localhost:8000/redoc         # ReDoc 文档
```

**应该看到：**
- 主页：`{"message": "人岗匹配心理评估系统后端已启动！"}`
- /docs：可交互的 API 文档，可在线测试所有接口

---

## 🎨 前端启动（3分钟）

### 步骤 1: 环境准备

```bash
# 1.1 返回项目根目录
cd ..

# 1.2 进入前端目录
cd frontend

# 1.3 确认已安装 Node.js 和 npm
npm --version
node --version
```

### 步骤 2: 安装依赖

```bash
# 2.1 安装项目依赖
npm install

# 2.2 预期安装时间：2-5分钟（视网络速度）
# 2.3 应该看到 "up to date" 或类似消息
```

### 步骤 3: 启动开发服务

```bash
# 3.1 启动开发服务器
npm run dev

# 3.2 预期输出类似：
#   VITE v4.x.x  build 0.0.0
#   ➜  Local:   http://localhost:5173/
#   ➜  press h to show help
```

### 步骤 4: 打开应用

在浏览器中打开：

```
http://localhost:5173/
```

**应该看到：**
- 登录页或首页
- 页面加载无明显错误

---

## 🧪 系统测试

### 测试 1: 后端 API 测试

```bash
# 在 backend 目录中运行测试脚本
cd backend
python test_assessment_api.py
```

**预期输出：**
```
============================================================
# AI 智能面试系统 - 后端 API 测试套件
============================================================
📍 服务器地址: http://localhost:8000
⏰ 测试时间: 2026-02-25 10:30:45

============================================================
预检查: 检查服务器连接
============================================================
✅ 服务器正常运行: 人岗匹配心理评估系统后端已启动！

============================================================
测试 1: 获取心理画像 (/assessment/portrait/{candidate_id})
============================================================
✅ GET /assessment/portrait/cand_001
ℹ️  返回 5 个特质评分:
  - 外向性: 7.5/10
  - 宜人性: 6.8/10
  - 尽责性: 8.9/10
  - 神经质: 3.2/10
  - 开放性: 8.1/10

... (更多测试输出)

📊 测试结果总结
总计: 7/7 测试通过

🎉 所有测试通过！后端准备就绪
```

### 测试 2: 使用 Swagger 测试 API

1. 打开 http://localhost:8000/docs
2. 找到 `GET /assessment/portrait/{candidate_id}` 接口
3. 点击 "Try it out"
4. 输入 candidate_id: `cand_001`
5. 点击 "Execute"
6. 应该看到成功的响应数据

### 测试 3: 前端功能测试

1. 访问 http://localhost:5173
2. 如果需要登录，使用测试账号：
   ```
   username: test_cand
   password: 123456
   ```
3. 进入首页应该看到：
   - 心理画像雷达图
   - 历史评估记录
   - 推荐岗位卡片

---

## ✅ 完整检查清单

系统启动后，请按以下清单验证：

### 后端检查

- [ ] `http://localhost:8000/` 能访问
- [ ] `http://localhost:8000/docs` Swagger UI 可用
- [ ] MySQL 数据库已创建并有数据
- [ ] 运行 `python test_assessment_api.py` 全部通过
- [ ] 能访问示例数据：
  - `GET /assessment/portrait/cand_001` 返回 5 个特质评分
  - `GET /assessment/history/cand_001` 返回 2 条历史记录
  - `GET /assessment/recommended-jobs/cand_001` 返回推荐岗位

### 前端检查

- [ ] `http://localhost:5173` 能访问
- [ ] 页面正常加载，无 JavaScript 错误
- [ ] 能看到首页组件（HomeView）
- [ ] 心理画像雷达图能渲染
- [ ] 点击"开始新评估"能跳转

### 集成检查

- [ ] 前端能成功调用后端 API
- [ ] 网络请求成功（F12 Console 无错误）
- [ ] 数据能正确显示在前端

---

## 🔍 常见问题

### 问题 1: "无法连接到 MySQL"

**错误信息：**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) 
[Errno 2003] Can't connect to MySQL server
```

**解决方案：**
1. 确认 MySQL 已启动
2. 检查 `.env` 中的 DATABASE_URL 格式
3. 验证数据库用户和密码
4. 确认 localhost:3306 可访问

```bash
# 测试 MySQL 连接
mysql -h localhost -u root -p

# 如果出现 MySQL 提示符 mysql> 则连接成功
```

---

### 问题 2: "ModuleNotFoundError: No module named 'fastapi'"

**解决方案：**
```bash
# 确保虚拟环境已激活
venv\Scripts\activate  # Windows

# 重新安装依赖
pip install -r requirements.txt

# 验证安装
pip list | grep -i fastapi
```

---

### 问题 3: "CORS 错误" 或 "blocked by CORS policy"

**错误信息：**
```
Access to XMLHttpRequest at 'http://localhost:8000/assessment/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方案：**
1. 确保后端已启动
2. 检查 main.py 中的 CORS 配置是否正确
3. 清除浏览器缓存（Ctrl+Shift+Delete）
4. 使用无痕浏览窗口重试

---

### 问题 4: "端口已被占用"

**错误信息：**
```
OSError: [Errno 48] Address already in use
```

**解决方案：**

```bash
# 方法 1: 使用不同端口
python -m uvicorn main:app --port 8001

# 方法 2: 杀死占用端口的进程 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 方法 2: 杀死占用端口的进程 (macOS/Linux)
lsof -i :8000
kill -9 <PID>
```

---

### 问题 5: "npm install 很慢"

**解决方案：**
```bash
# 使用 cnpm (淘宝源)
npm install -g cnpm --registry=https://registry.npm.taobao.org
cnpm install

# 或者配置 npm 源
npm config set registry https://registry.npmmirror.com
npm install
```

---

### 问题 6: "前端无法调用后端 API"

**现象：** F12 Console 中看到网络请求失败

**解决方案：**
1. 检查后端是否运行：`http://localhost:8000/`
2. 检查 CORS 配置
3. 检查网络请求 URL 是否正确
4. 检查浏览器控制台错误信息

---

## 🎯 下一步

系统启动成功后，您可以：

1. **浏览 API 文档**
   - 访问 http://localhost:8000/docs
   - 了解所有可用接口

2. **测试完整流程**
   - 使用测试账号登录
   - 浏览首页数据
   - 点击"开始新评估"（如果已集成对话）

3. **查看源代码**
   - `backend/routers/assessment.py` - 后端 API 实现
   - `frontend/src/views/HomeView.vue` - 前端首页
   - `frontend/src/utils/request.ts` - API 调用函数

4. **修改配置**
   - `.env` - 数据库连接
   - `.env.local` - 前端配置
   - `package.json` - 前端依赖

---

## 📞 技术支持

若遇到问题：

1. **查阅文档**
   - BACKEND_INTEGRATION_GUIDE.md（后端详细指南）
   - FRONTEND_BACKEND_INTEGRATION.md（集成指南）
   - BACKEND_API_SPECIFICATION.md（API 规范）

2. **检查日志**
   - 控制台输出
   - 浏览器开发者工具（F12）
   - MySQL 日志

3. **验证环境**
   ```bash
   python --version
   pip list
   node --version
   npm --version
   mysql --version
   ```

---

## ✨ 成功标志

当您看到以下现象时，说明系统已成功启动：

```
✅ 后端服务运行在 http://localhost:8000
✅ 前端应用运行在 http://localhost:5173
✅ 数据库数据已初始化
✅ API 文档可在 http://localhost:8000/docs 访问
✅ 所有测试用例通过
✅ 前端能正常显示数据
✅ 网络请求无错误
```

---

**开发完成时间：** 2026-02-25  
**质量等级：** ✨ Production Ready  
**文档版本：** 1.0.0

祝开发愉快！🎉
