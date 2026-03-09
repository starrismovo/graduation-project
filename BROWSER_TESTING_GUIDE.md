# 🌐 浏览器功能测试指南

## 前置条件
- ✅ 后端已启动: http://127.0.0.1:8000
- ✅ 前端已启动: http://localhost:5173
- ✅ MySQL 数据库正常运行

---

## 📋 测试清单

### 1. 打开应用首页
```
1. 在浏览器中访问: http://localhost:5173
2. 验证页面是否正常加载（无白屏或错误）
3. 查看 F12 开发者工具的 Console 标签，确认没有红色错误
```

**预期结果**: ✅ 页面加载成功，无JavaScript错误

---

### 2. 用户注册流程
```
1. 点击 "注册" 或 "Sign Up" 按钮
2. 填写表单：
   - 用户名: testuser123
   - 邮箱: test@example.com
   - 密码: TestPass123
   - 确认密码: TestPass123
3. 点击 "注册" 按钮
4. 查看 F12 中的 Network 标签，确认请求发送到: http://127.0.0.1:8000/auth/register
5. 验证响应状态码为 200 或 201
```

**预期结果**: ✅ 注册成功，显示成功提示或跳转到登录页

**常见问题**:
- 如果看到错误"用户名已存在"，换一个用户名重试
- 如果看到 CORS 错误，后端 CORS 配置有问题

---

### 3. 用户登录流程
```
1. 在登录页面输入上述用户名和密码
2. 点击 "登录" 按钮
3. 查看 F12 的 Network 标签，确认：
   - 请求URL: http://127.0.0.1:8000/auth/login
   - 请求方法: POST
   - 响应状态: 200
4. 查看 Storage 标签，确认本地存储中保存了 token
5. 验证页面是否跳转到应用首页
```

**预期结果**: ✅ 登录成功，页面显示已登录状态

---

### 4. API 请求监控
```
1. 打开 F12 开发者工具
2. 切换到 "Network" 标签
3. 刷新页面，或执行某个操作
4. 观察所有 API 请求:
   - 请求都应该来自 http://127.0.0.1:8000
   - 响应状态应该是 2xx（成功）或合理的错误码
   - 不应该有 CORS 相关错误 (红色错误)
```

**预期结果**: 
- ✅ 所有请求都成功完成
- ❌ 没有 red text 错误信息

---

### 5. 数据库集成测试
```
1. 执行上述注册和登录流程
2. 使用以下MySQL命令验证数据已保存:

   mysql -u root -p -D hr_matching
   
   // 查看用户表
   SELECT * FROM users;
   
   // 查看是否有刚注册的用户
   SELECT id, username, email FROM users ORDER BY id DESC LIMIT 5;
```

**预期结果**: ✅ 能查看到新注册的用户

---

## 🔧 调试技巧

### 查看详细的请求/响应信息
```
F12 -> Network 标签 -> 点击具体请求 :
- Headers: 查看请求头和响应头
- Preview: 查看格式化的响应内容
- Response: 查看原始响应
```

### 查看存储的 Token（用于认证）
```
F12 -> Application/Storage 标签 :
- Local Storage -> http://localhost:5173
- 应该能看到 `token` 或 `auth_token` 等键值对
```

### 查看浏览器控制台错误
```
F12 -> Console 标签 :
- ❌ 红色错误: 影响功能的严重错误
- ⚠️ 黄色警告: 可能的问题，通常不影响功能
- ℹ️ 蓝色信息: 调试信息
```

### 监视网络延迟
```
F12 -> Network 标签 :
- 红色条: 等待时间（TTFB）
- 绿色条: 下载时间
- 正常情况下，单个 API 请求应该 < 100ms（本地）
```

---

## 📱 跨浏览器测试

推荐在以下浏览器测试：

| 浏览器 | 推荐于 | 备注 |
|--------|--------|------|
| Chrome | ✅ 首选 | 最佳开发者工具 |
| Firefox | ✅ 推荐 | 良好的兼容性 |
| Edge | ✅ 可用 | 基于Chromium |
| Safari | ⚠️ 可能有问题 | 某些JS特性不支持 |

---

## 📝 测试报告模板

当完成所有测试后，填写以下报告：

```
测试日期: _______________
测试人员: _______________
浏览器版本: _______________

✅ 通过的测试:
  □ 页面加载
  □ 用户注册
  □ 用户登录
  □ API 请求
  □ 数据持久化
  □ 其他: _______________

❌ 失败的测试:
  □ _______________
  □ _______________

⚠️ 需要改进:
  □ _______________
  □ _______________

总体评分: ___ / 10
备注: _______________
```

---

## 🚨 常见错误及解决方案

### 错误 1: CORS Policy Error
```
错误信息: 
"Access to XMLHttpRequest at 'http://127.0.0.1:8000/auth/register' 
from origin 'http://localhost:5173' has been blocked by CORS policy"

解决方案:
1. 检查后端 main.py 的 allow_origins 列表
2. 确保 "http://localhost:5173" 在列表中
3. 重启后端服务
```

### 错误 2: Token Expired
```
错误信息: "401 Unauthorized" 或 "Token expired"

解决方案:
1. 清空浏览器本地存储: F12 -> Storage -> Clear All
2. 重新登录
3. 检查 .env 中的 TOKEN_EXPIRE_MINUTES 设置
```

### 错误 3: Database Connection Error
```
错误信息: "Error connecting to database" 或 "Connection refused"

解决方案:
1. 检查 MySQL 是否运行: tasklist | findstr mysql
2. 检查 .env 中的 DATABASE_URL 是否正确
3. 确保用户名和密码正确 (root:root)
4. 确保数据库存在: hr_matching
```

### 错误 4: 404 Not Found
```
错误信息: "404 Not Found" 响应

解决方案:
1. 访问 http://127.0.0.1:8000/docs 查看正确的 API 路由
2. 检查请求 URL 中的路由前缀是否正确
3. 检查是否有 typo 或拼写错误
```

---

## ✨ 高级调试

### 监视 API 请求/响应
```javascript
// 在浏览器 Console 中运行，可以看到所有 API 调用
// 打开 Network 标签 -> 选择一个请求 -> 复制为 cURL
```

### 模拟慢速网络
```
F12 -> Network 标签 -> 左上角 "No throttling" 下拉菜单
选择 "Fast 3G" 或 "Slow 3G" 来模拟慢速网络
```

### 禁用缓存
```
F12 -> Settings -> Network 部分
勾选 "Disable cache (while DevTools is open)"
```

---

## 📞 需要帮助?

如果测试失败，收集以下信息：
1. 完整的错误信息（截图或文本）
2. 浏览器类型和版本
3. 后端控制台的错误日志
4. F12 Network 标签中的失败请求详情
5. F12 Console 中的错误信息

---

**状态**: 准备好进行测试！🚀
