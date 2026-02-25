# 🚀 五分钟快速开始

**预计时间：** 5 分钟  
**难度：** 🟢 非常简单  
**目标：** 让系统正常运行起来

---

## ⚡ 最快的开始方式

### Windows 用户（推荐 ✨）

**第 1 步：** 打开 PowerShell

在项目根目录执行：
```powershell
.\startup.ps1
```

**第 2 步：** 选择启动选项

```
请选择操作：
1. 仅启动后端 (http://localhost:8000)
2. 同时启动后端和前端 (推荐) ← 选这个
3. 显示启动说明
```

输入 `2` 然后按 Enter

**第 3 步：** 等待启动完成

脚本会自动：
- ✅ 检查 Python 环境
- ✅ 检查 Node.js 环境
- ✅ 启动后端服务
- ✅ 启动前端应用
- ✅ 打开浏览器

**第 4 步：** 尽享应用

```
后端地址：  http://localhost:8000
前端地址：  http://localhost:5173 ← 自动打开
API 文档：  http://localhost:8000/docs
```

---

## 🖥️ 如果脚本不工作

### 手动启动（2 个终端）

**终端 1：启动后端**
```bash
cd backend
python -m uvicorn main:app --reload
```

等待看到：
```
Uvicorn running on http://127.0.0.1:8000
```

**终端 2：启动前端**
```bash
cd frontend
npm install
npm run dev
```

等待看到：
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

然后访问 http://localhost:5173

---

## ✅ 验证一切正常

### 检查清单

在浏览器中访问以下地址，确保都能打开：

- [ ] http://localhost:5173 (前端) ✅
- [ ] http://localhost:8000 (后端) ✅
- [ ] http://localhost:8000/docs (API 文档) ✅

---

## 🧪 测试系统工作

### 使用演示数据登录

**演示用户：** 已自动创建

访问前端应用后：

1. **如果看到登录页面**
   - 任何用户名密码组合通常可以登录（演示模式）
   - 或使用系统预设的演示账户

2. **登录后应该看到：**
   - 心理画像（雷达图）
   - 评估历史（列表）
   - 推荐岗位（卡片）

3. **检查浏览器控制台（F12）**
   - 打开 F12 → Network 标签
   - 应该看到这些 API 请求：
     ```
     GET /assessment/portrait/xxx     ✅
     GET /assessment/history/xxx      ✅
     GET /assessment/recommended-jobs/xxx ✅
     ```
   - 所有请求状态码应该是 200

---

## 🎯 首次使用流程

```
1. 开启应用
   ↓
2. 看到登录页面
   ↓
3. 输入任意用户名和密码
   ↓
4. 点击登录
   ↓
5. 进入首页
   ↓
6. 看到：
   ✅ 心理画像面板
   ✅ 历史评估记录
   ✅ 推荐岗位列表
```

---

## ❌ 遇到问题？

### 问题 1：无法运行 startup.ps1

**错误信息：**
```
startup.ps1 : 因为在此系统上禁止运行脚本
```

**解决方案：**
```powershell
# 打开 PowerShell（管理员模式）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# 选择 Y (Yes) 确认
# 再次运行
.\startup.ps1
```

### 问题 2：后端启动失败

**错误显示：** Address already in use 或 port 8000 occupied

**解决方案：**
```bash
# 找到占用 8000 端口的进程并关闭
# 或使用其他端口
cd backend
python -m uvicorn main:app --reload --port 8001
```

### 问题 3：前端白屏或报错

**错误显示：** Cannot GET / 或 Vite error

**解决方案：**
```bash
cd frontend
# 清除依赖
rm -r node_modules
# 重新安装（Windows 用 del 替代 rm）
npm install
# 重新启动
npm run dev
```

### 问题 4：API 返回 404

**原因：** 前端找不到后端

**解决方案：**
查看文件：`frontend/src/utils/request.ts`

确保第 5 行是：
```typescript
const baseURL = 'http://127.0.0.1:8000'
```

或检查后端是否在运行：
```bash
curl http://127.0.0.1:8000
```

### 问题 5：数据库连接错误

**错误显示：** MySQL connection failed 或 database error

**解决方案：**
```bash
# 检查 backend/database.py 中的连接字符串
# 默认值：
DATABASE_URL = "mysql+pymysql://root:password@localhost/interview_system"

# 确保 MySQL 在运行
# Windows: 在服务中检查 MySQL80
# macOS: brew services list | grep mysql
# Linux: sudo systemctl status mysql
```

---

## 📚 需要详细帮助？

查看这些文件获取完整的故障排除：

- **快速开始指南：** [FRONTEND_QUICK_START.md](./FRONTEND_QUICK_START.md)
- **前端集成完成：** [FRONTEND_INTEGRATION_COMPLETE.md](./FRONTEND_INTEGRATION_COMPLETE.md)
- **后端 API 规范：** [BACKEND_API_SPECIFICATION.md](./BACKEND_API_SPECIFICATION.md)
- **完整项目报告：** [PROJECT_FINAL_REPORT.md](./PROJECT_FINAL_REPORT.md)

---

## 🎉 完成！

现在您可以：

✅ 看到系统运行  
✅ 验证功能工作  
✅ 查看数据流动  
✅ 交互使用应用  

**下一步？** 阅读其他文档了解更多细节，或开始定制系统！

🚀 **祝您使用愉快！**
