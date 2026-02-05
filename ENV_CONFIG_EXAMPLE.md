# HR-Agent LLM 环境配置示例

## 开发环境配置（.env.development）

```env
# 数据库配置（开发使用本地 MySQL 示例）
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/hr_matching?charset=utf8mb4

# LLM 配置 - 开发环境使用模拟模式
LLM_FORCE_MOCK=true
# 不要设置 OPENAI_API_KEY（保持注释状态）
# OPENAI_API_KEY=

# 日志级别
LOG_LEVEL=DEBUG

# 服务器配置
HOST=127.0.0.1
PORT=8000
RELOAD=true

# 前端 URL（用于 CORS）
FRONTEND_URL=http://localhost:5173
```

## 测试环境配置（.env.test）

```env
# 测试数据库（使用独立的 MySQL 测试库）
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/hr_matching_test?charset=utf8mb4

# LLM 配置 - 测试时可选择
LLM_FORCE_MOCK=true
# 或者使用真实 API 进行集成测试
# LLM_FORCE_MOCK=false
# OPENAI_API_KEY=sk-xxx...

# 日志级别
LOG_LEVEL=INFO

# 服务器配置
HOST=127.0.0.1
PORT=8001

# 前端 URL
FRONTEND_URL=http://localhost:5173
```

## 生产环境配置（.env.production）

```env
# 数据库配置（使用 MySQL）
DATABASE_URL=mysql+pymysql://user:password@host:3306/hr_matching

# LLM 配置 - 生产环境使用真实 API
LLM_FORCE_MOCK=false
OPENAI_API_KEY=sk-xxx...  # 从 Kubernetes Secrets 或环境变量注入
# OPENAI_MODEL=gpt-4       # 可选：指定模型版本

# 日志级别
LOG_LEVEL=WARNING

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=false

# 前端 URL
FRONTEND_URL=https://yourdomain.com

# API 限流配置
RATE_LIMIT_PER_MINUTE=60

# 监控和追踪
SENTRY_DSN=https://xxx@sentry.io/xxx  # 可选
```

## 快速切换指南

### 1. 开发环境启动

```bash
# 使用开发配置
cp .env.development .env
python -m uvicorn main:app --reload
```

### 2. 切换到测试 API

```bash
# 修改 .env
LLM_FORCE_MOCK=false
OPENAI_API_KEY=sk-xxx...

# 重启服务
# 系统会自动加载新配置
```

### 3. 生产环境部署

```bash
# 使用 Docker 或云平台
# 通过环境变量注入配置
docker run -e OPENAI_API_KEY=sk-xxx... my-app:latest
```

## 在不同 Python IDE 中配置

### PyCharm

1. File → Settings → Project → Python Interpreter
2. 找到你的项目解释器
3. 点击右下角的齿轮图标
4. 选择 "Environment variables"
5. 添加：
    ```
    LLM_FORCE_MOCK=true
    DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/hr_matching?charset=utf8mb4
    ```

### VS Code

在 `.vscode/settings.json` 中：

```json
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.linting.enabled": true,
    "python.formatting.provider": "black"
}
```

### Anaconda

在激活环境后：

```bash
# 在激活环境的 activate 脚本中添加
export LLM_FORCE_MOCK=true
export DATABASE_URL=sqlite:///./hr_matching.db
```

## 验证配置

### 检查当前配置

```bash
python -c "
import os
print('LLM_FORCE_MOCK:', os.getenv('LLM_FORCE_MOCK', '未设置'))
print('DATABASE_URL:', os.getenv('DATABASE_URL', '未设置'))
print('OPENAI_API_KEY:', 'sk-' + os.getenv('OPENAI_API_KEY', '')[3:7] + '...' if os.getenv('OPENAI_API_KEY') else '未设置')
"
```

### 检查 LLM 模式

```bash
cd backend
python -c "
from prompts.hr_agent_llm import HRAgentLLM
llm = HRAgentLLM()
print('当前模式:', '模拟' if llm.use_mock else 'API')
"
```

## 常见配置问题

### 问题 1：模拟模式不生效

```bash
# 检查环境变量
echo %LLM_FORCE_MOCK%  # Windows
echo $LLM_FORCE_MOCK    # Linux/Mac

# 重新加载 .env 文件
# 重启 IDE 或终端
```

### 问题 2：无法加载 .env 文件

```bash
# 安装 python-dotenv
pip install python-dotenv

# 在代码中加载
from dotenv import load_dotenv
load_dotenv()
```

### 问题 3：API Key 泄露

```bash
# 立即轮换 Key
# https://platform.openai.com/api-keys

# 从 Git 历史中移除
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all

# 添加 .env 到 .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
```

## 推荐的 .gitignore 配置

```
# 环境变量文件
.env
.env.*
!.env.example

# IDE 配置
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# 数据库
*.db
*.sqlite
```

## 示例 .env.example 文件

提交到 Git 供团队参考：

```env
# HR-Agent 环境配置示例
# 使用方法：cp .env.example .env，然后填入实际值

# 数据库 URL
# 开发：sqlite:///./hr_matching.db
# 生产：mysql+pymysql://user:password@host:3306/db
DATABASE_URL=sqlite:///./hr_matching.db

# LLM 配置
# 开发模式：true（使用本地规则引擎）
# 生产模式：false（使用 OpenAI API）
LLM_FORCE_MOCK=true

# OpenAI API Key（仅在生产环境需要）
# 从 https://platform.openai.com/api-keys 获取
# OPENAI_API_KEY=sk-...

# 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=DEBUG

# 服务器配置
HOST=127.0.0.1
PORT=8000
RELOAD=true

# 前端 URL（用于 CORS 配置）
FRONTEND_URL=http://localhost:5173
```

## 总结

| 场景 | 配置 | 说明 |
|------|------|------|
| 本地开发 | LLM_FORCE_MOCK=true | 快速、无成本 |
| 测试集成 | LLM_FORCE_MOCK=false + OPENAI_API_KEY | 真实 API 测试 |
| 毕业演示 | LLM_FORCE_MOCK=true | 稳定、可预测 |
| 生产环境 | LLM_FORCE_MOCK=false + OPENAI_API_KEY | 最佳体验 |
