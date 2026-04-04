# ✅ 前端白屏诊断和修复

## 🔴 问题状态

前端页面出现空白/白屏，Vite 在 http://localhost:5174 运行。

## 🔍 已执行的修复步骤

### 1. ✅ 删除旧的编译输出文件
- `frontend/src/utils/request.js` - 已删除（重复导致模块冲突）
- 所有 `src/**/*.js` 编译输出文件 - 已删除（34 个文件）

### 2. ✅ 清理缓存
- npm install - 已完成（重新安装依赖）
- .vite 缓存目录 - 已删除
- dist 构建目录 - 已删除

### 3. ✅ 重新启动 Vite
- 服务器状态: 正常运行在 http://localhost:5174
- 无编译错误在控制台中显示
- HMR (热模块替换) 运行正常

## 📋 诊断步骤

### 浏览器中需要做的事：

**1. 打开浏览器开发者工具 (F12 或 右键 → 检查)**

**2. 查看 Console 标签 (控制台)**
   - 寻找任何红色错误信息
   - 截图或记录错误内容

**3. 查看 Network 标签 (网络)**
   ```
   查找:
   - index.html: 状态码应为 200
   - main.ts: 状态码应为 200
   - 其他资源: 状态码应为 200
   
   如果状态码是 404 或其他错误:
   - 重新启动 Vite
   - 清除浏览器缓存 (Ctrl+Shift+Delete)
   ```

**4. 查看 Elements/Inspector 标签 (元素检查)**
   ```
   验证 DOM 结构：
   <html>
     <body>
       <div id="app">
         <!-- 应该有内容在这里 -->
       </div>
       <script type="module" src="/src/main.ts"></script>
     </body>
   </html>
   ```

## 🧪 快速测试

### 方法 1: 硬刷新浏览器
```
按键:  Ctrl + Shift + R (或 Cmd + Shift + R on Mac)
效果: 绕过浏览器缓存，重新加载所有文件
```

### 方法 2: 清除浏览器缓存
```
按键: Ctrl + Shift + Delete (或 Cmd + Shift + Delete on Mac)
操作:
  1. 选择 "All time" 时间范围
  2. 勾选 "Cookies" 和 "Cached images"
  3. 点击 "Clear data"
  4. 刷新页面
```

### 方法 3: 使用隐私浏览模式
```
快捷键:
  - Windows/Linux: Ctrl + Shift + N
  - Mac: Cmd + Shift + N
效果: 打开新的隐私窗口，不使用缓存
操作: 访问 http://localhost:5174
```

## 🔧 后端验证

验证后端是否正常运行：

```bash
# 在新终端运行
cd D:\Desktop\graduation-project\backend

# 启动后端
python main.py

# 应该看到:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 📊 现在应该看到的

### 登录页面应包含：
- 左侧: AI系统logo和品牌信息
- 右侧: 登录表单
  ```
  用户名: _________
  密码:   _________
  [登录] 按钮
  ```

### 若还是空白，可能的原因：

| 原因 | 解决方案 |
|------|---------|
| 浏览器缓存 | Ctrl+Shift+R (硬刷新) |
| 后端未运行 | 启动后端: `python main.py` |
| Node 模块问题 | 重装依赖: `npm install` |
| TypeScript 错误 | 检查控制台,查看具体错误 |
| 端口被占用 | Vite 自动尝试 5174, 如果还是被占用，关闭占用该端口的程序 |

## 💡 进阶诊断

### 检查 Vite 终端日志
```
查看运行 npm run dev 的终端:
- 应该看到: "VITE v7.3.1 ready in XXX ms"
- 不应该看到: "error" 或 "failed"
```

### 检查网络代理
```
如果 API 调用失败:
1. 打开浏览器控制台 Network 标签
2. 进行任何会发起 API 的操作
3. 查找 /assessment/ 或 /api/ 请求
4. 应该被代理到: http://localhost:8000
```

### 手动测试 API
```bash
# 测试后端是否响应
curl http://localhost:8000/

# 应该返回 JSON 响应 (不是 404)
```

## 🚀 完整启动流程

如果上述步骤都没有改善，请按以下流程重新启动：

### 1. 停止所有进程
```bash
# 停止 Vite (在运行 npm run dev 的终端中按 Ctrl+C)
# 停止后端 (在运行 python main.py 的终端中按 Ctrl+C)
```

### 2. 清理环境
```bash
cd D:\Desktop\graduation-project\frontend
npm cache clean --force
rm -r node_modules (或 Remove-Item node_modules -Recurse)
npm install
```

### 3. 重新启动
```bash
# 终端 1 - 后端
cd D:\Desktop\graduation-project\backend
python main.py

# 终端 2 - 前端
cd D:\Desktop\graduation-project\frontend
npm run dev

# 浏览器
http://localhost:5174
```

### 4. 测试
```
1. 页面应该显示登录页面
2. 输入用户名: candidate1
3. 输入密码: 123456
4. 点击登录
5. 应该进入首页
```

## 📝 日志收集

如果问题仍未解决，请收集以下信息：

```
1. 浏览器控制台的完整错误信息
2. Vite 终端的输出 (npm run dev 的窗口)
3. 后端服务器的输出 (python main.py 的窗口)
4. 浏览器 Network 标签中失败的请求
5. 系统信息 (操作系统、Node 版本、npm 版本)
```

### 获取系统信息
```bash
node --version      # 应该 >= 16
npm --version       # 应该 >= 7
python --version    # 应该 >= 3.8
```

## ✅ 验收标准

前端修复成功的标志：
- ✅ 登录页面显示正常
- ✅ 可以输入用户名和密码
- ✅ 点击登录后导航到首页
- ✅ 首页显示用户信息和菜单
- ✅ 可以点击"报告中心"进入报告列表
- ✅ 浏览器控制台无红色错误

---

**状态**: 前端服务器正常运行，等待诊断和验证  
**当前端口**: http://localhost:5174  
**后端端口**: http://localhost:8000 (需要启动)
