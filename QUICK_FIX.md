# 🔧 快速修复指南

## 问题诊断

❌ **CORS 错误** + **500 内部服务器错误**

### 根本原因
后端 Interview 模型在 MySQL 中使用了 SQLAlchemy 的 Enum 类型，但 MySQL 对 Enum 的支持有兼容性问题。

## ✅ 已修复

1. **Interview 模型** - 从 SQLEnum 改为 String
2. **所有状态检查** - 从枚举值改为字符串比对
3. **路由文件** - 移除枚举导入

## 现在需要做的

### 步骤 1: 安装依赖

```bash
cd backend

# 尝试这些方法之一：

# 方法 A: pip（推荐）
pip install fastapi uvicorn sqlalchemy pymysql python-jose passlib pydantic python-dotenv

# 方法 B: conda（如果pip有问题）
conda install -c conda-forge fastapi uvicorn sqlalchemy pymysql

# 方法 C: 使用alembic镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 步骤 2: 初始化数据库

**确保 MySQL 正在运行**，然后在MySQL客户端执行：

```sql
CREATE DATABASE IF NOT EXISTS hr_matching DEFAULT CHARSET=utf8mb4;
USE hr_matching;

-- 表会由 SQLAlchemy 自动创建
-- 您只需要数据库存在即可
```

### 步骤 3: 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看API文档

如果看到 Swagger UI 界面，说明后端正确启动！

### 步骤 4: 初始化测试数据

后端启动后，可以运行初始化脚本创建测试数据：

```bash
python init_test_data.py

# 或者如果上面失败，用纯SQL版本：
python init_simple.py
```

### 步骤 5: 启动前端

```bash
cd ../frontend
npm run dev
```

访问 http://localhost:5173

## 常见问题

### Q: 后端启动报错 "No module named 'fastapi'"
**A**: 说明依赖没有安装。运行 `pip install -r requirements.txt`

### Q: MySQL 连接失败
**A**: 
1. 检查 MySQL 服务是否运行：`mysql -u root -p`
2. 检查 .env 文件中的 DATABASE_URL 是否正确
3. 确保数据库存在：`CREATE DATABASE hr_matching`

### Q: 初始化脚本失败
**A**: 使用纯SQL版本：
```bash
python init_simple.py  # 需要 mysql-connector-python 或 PyMySQL
```

或手动创建初始数据：
1. 登录 MySQL
2. 运行初始化 SQL（见下方）

### Q: CORS 错误仍然存在
**A**: 
1. 确保前端确实在 http://localhost:5173
2. 检查 main.py 中的 CORS 配置
3. 清除浏览器缓存并重新启动

### Q: 前端仍然无法加载数据
**A**: 
1. 打开浏览器开发者工具 (F12)
2. 查看 Network 标签
3. 查看请求 URL 和响应状态码
4. 如果是 404，检查 API 路由是否正确

## 数据库初始化 SQL

如果自动初始化脚本失败，可以手动运行：

```sql
USE hr_matching;

-- 创建users表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_hr BOOLEAN DEFAULT 0
) DEFAULT CHARSET=utf8mb4;

-- 创建jobs表
CREATE TABLE IF NOT EXISTS jobs (
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
) DEFAULT CHARSET=utf8mb4;

-- 创建interviews表
CREATE TABLE IF NOT EXISTS interviews (
  id INT PRIMARY KEY AUTO_INCREMENT,
  candidate_id INT NOT NULL,
  job_id INT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'started',
  personality_traits JSON,
  match_score FLOAT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  notes VARCHAR(500),
  FOREIGN KEY (candidate_id) REFERENCES users(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id),
  UNIQUE KEY unique_interview (candidate_id, job_id)
) DEFAULT CHARSET=utf8mb4;

-- 插入测试用户
INSERT INTO users (username, email, hashed_password, is_hr) VALUES
('alice', 'alice@company.com', '$2b$12$test', 1),
('bob', 'bob@example.com', '$2b$12$test', 0);

-- 插入测试岗位（来自HR用户 alice）
INSERT INTO jobs (name, description, company, category, city, salary_min, salary_max, required_traits, creator_id) VALUES
('前端开发工程师', '负责React/Vue框架下的前端业务开发', '阿里巴巴', '技术岗', '杭州', 25, 35, JSON_OBJECT('openness', 8, 'conscientiousness', 8, 'extraversion', 7), 1),
('后端开发工程师', '开发高并发分布式后端系统', '字节跳动', '技术岗', '北京', 30, 50, JSON_OBJECT('openness', 7, 'conscientiousness', 9, 'extraversion', 5), 1),
('Python数据分析师', '使用Python进行数据分析和可视化', '腾讯', '技术岗', '深圳', 22, 32, JSON_OBJECT('openness', 8, 'conscientiousness', 9, 'extraversion', 4), 1),
('产品经理', '负责产品规划和迭代', '美团', '产品岗', '北京', 25, 40, JSON_OBJECT('openness', 9, 'conscientiousness', 8, 'extraversion', 8), 1),
('视觉设计师', '设计UI/UX界面，提升用户体验', '网易', '设计岗', '杭州', 18, 28, JSON_OBJECT('openness', 9, 'conscientiousness', 7, 'extraversion', 6), 1),
('运营专员', '负责社区运营和用户增长', '快手', '运营岗', '上海', 15, 25, JSON_OBJECT('openness', 8, 'conscientiousness', 7, 'extraversion', 9), 1),
('机器学习工程师', '开发和优化机器学习模型', '百度', '技术岗', '北京', 35, 60, JSON_OBJECT('openness', 9, 'conscientiousness', 9, 'extraversion', 4), 1),
('市场营销经理', '制定营销策略，管理营销团队', '小米', '市场岗', '深圳', 20, 35, JSON_OBJECT('openness', 8, 'conscientiousness', 7, 'extraversion', 8), 1);
```

## 验证步骤

### 1. 后端是否启动
```bash
curl http://127.0.0.1:8000/
```
应该返回：
```json
{"message": "人岗匹配心理评估系统后端已启动！", "docs": "/docs"}
```

### 2. 数据库是否有数据
```bash
mysql -u root -p
use hr_matching;
select count(*) from users;  -- 应该返回 2
select count(*) from jobs;   -- 应该返回 8
```

### 3. API 是否可用
访问 http://127.0.0.1:8000/docs，应该看到 Swagger UI

### 4. 前端是否连接成功
打开前端应用，登录后应该看到岗位卡片和统计信息

## 总结

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1 | `pip install -r requirements.txt` | 安装依赖 |
| 2 | 在 MySQL 创建数据库 | `CREATE DATABASE hr_matching` |
| 3 | `python init_test_data.py` | 初始化数据 |
| 4 | `uvicorn main:app --reload` | 启动后端 |
| 5 | `npm run dev` | 启动前端 |

✅ 这样就能正常使用了！

## 需要帮助？

如果仍然有问题，请提供：
1. 错误消息的完整内容
2. 执行的命令
3. 您使用的操作系统和Python版本
