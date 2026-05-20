# 修复前端404错误 - 完整步骤

## 问题原因

前端Vite开发服务器缺少对后端API的代理配置，导致：
- 前端请求 `/assessment/immersive/upload-resume`
- 被Vite发送到自己的开发服务器（通常在 `http://localhost:5173`）
- 该路径不存在 → 返回404

## 已实施的修复

### ✅ 修改了 `frontend/vite.config.ts`

添加了代理配置：
```javascript
server: {
  proxy: {
    '/assessment': {
      target: 'http://localhost:8000',  // 后端地址
      changeOrigin: true
    }
  }
}
```

这样前端请求 `/assessment/*` 会被自动转发到后端。

## 立即执行的步骤

### 步骤1：确保后端运行

```powershell
# 在backend目录
cd backend
python main.py
# 应该看到: Uvicorn running on http://0.0.0.0:8000
```

### 步骤2：重启前端开发服务器

**重要！** 由于修改了vite.config.ts，需要重新启动前端：

```powershell
# 先停止现有的前端服务（Ctrl+C）
# 然后重新启动
cd frontend
npm run dev
# 应该看到: Local:   http://localhost:5173
```

### 步骤3：测试上传功能

1. 在浏览器打开前端应用
2. 进入immersive interview流程
3. 尝试上传简历文件 
4. 应该看到：
   - ✓ 成功：文件被后端解析，信息自动填入
   - ✓ 日志显示正确的状态码（200）而不是404

## 验证修复

在浏览器开发者工具中（F12 → Network标签）：

**修复前：**
```
POST /assessment/immersive/upload-resume → 404 Not Found
Response: 前端开发服务器返回不存在页面的HTML
```

**修复后：**
```
POST /assessment/immersive/upload-resume → 200 OK
Response: 后端返回的JSON {code: 200, data: {...}}
```

## 如果仍然失败

### 排查1：检查后端是否真的在运行
```powershell
curl http://localhost:8000/assessment/immersive/status
# 应该返回200状态码和JSON响应
```

### 排查2：检查前端配置是否已加载
```
检查浏览器控制台：
- 请求应该发送到 http://localhost:5173/assessment/...
- 但实际被代理到 http://localhost:8000/assessment/...
- Network标签会显示经过代理的请求
```

### 排查3：确认vite.config.ts已保存
- 文件应该包含 `server: { proxy: {...}}`
- 如果之前在运行 `npm run dev`，需要停止后重新运行

## 相关技术说明

### 为什么需要代理？

Vite开发服务器和FastAPI后端运行在不同的端口：
- 前端：`http://localhost:5173` (Vite dev server)
- 后端：`http://localhost:8000` (FastAPI)

浏览器有 CORS 安全限制，直接跨域请求可能被阻止。通过Vite的代理机制可以：
1. 让浏览器认为请求来自同一源（localhost:5173）
2. Vite负责将请求转发到后端
3. 完全避免CORS问题

### vite.config.ts 代理配置说明

```javascript
proxy: {
  '/assessment': {           // 匹配路径
    target: 'http://localhost:8000',  // 转发到
    changeOrigin: true,      // 修改请求头的Origin
    rewrite: (path) => path  // 保持原始路径不修改
  }
}
```

这样 `/assessment/immersive/upload-resume` 会被转发到 `http://localhost:8000/assessment/immersive/upload-resume`

## 检查清单

- [ ] 后端服务正在运行（`python main.py`）
- [ ] 前端开发服务器已重启（`npm run dev`）
- [ ] vite.config.ts 已保存带有代理配置
- [ ] 浏览器已刷新（Ctrl+R 或 Cmd+R）
- [ ] 浏览器开发者工具中查看Network请求已不再显示404

## 预期结果

修复后上传文件应该：
1. ✓ 前端日志显示：`后端响应状态码: 200`
2. ✓ 自动填入候选人信息（姓名、邮箱、技能等）
3. ✓ 不再显示JSON解析错误

---

**修复完成时间：** 2026年3月10日  
**修复方式：** 添加Vite代理配置  
**所需重启：** 前端开发服务器
