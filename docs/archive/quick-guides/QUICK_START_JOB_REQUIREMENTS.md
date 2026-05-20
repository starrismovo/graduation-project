# ⚡ 快速启动指南 (5分钟)

## 一键启动步骤

### 1️⃣ 验证系统 (30秒)

```bash
cd backend
python verify_job_requirements.py
```

✅ 应该看到: `🎉 所有验证都通过了!`

### 2️⃣ 启动后端 (1分钟)

```bash
cd backend
python main.py
```

✅ 应该看到: `...application startup complete`

### 3️⃣ 启动前端 (1分钟)

```bash
cd frontend
npm run dev
```

✅ 应该看到: `Local: http://localhost:5173`

### 4️⃣ 测试功能 (2分钟)

#### A. HR 测试
```
1. 登录为 HR (username: hr_admin, password: 123456)
2. 进入"岗位管理"
3. 选择一个岗位
4. 点击"编辑岗位需求"
5. 粘贴下面的 JD 文本:

---
【JD 示例文本】
职位: 高级 Python 工程师

岗位描述:
我们需要一名 5+ 年经验的高级 Python 工程师
- 精通 Python，至少 5 年经验
- 熟悉 FastAPI, Django 框架
- 深入掌握 PostgreSQL, Redis
- 熟悉 Docker, Kubernetes 容器化
- 具有团队协作和问题解决能力
- 对代码质量有追求，熟悉 TDD

岗位要求:
- 大专及以上学历
- 北京或远程工作
- 年薪 25-40k
---

6. 点击"生成需求" → 系统自动解析
7. 查看生成的技能和人格框架
8. 点击"保存岗位需求" ✅
```

#### B. 候选人测试
```
1. 登录为候选人 (username: cand_001, password: 123456)
2. 进入"选择岗位"
3. 浏览显示的岗位列表
4. 点击某个岗位，查看详细需求
   - 显示所需技能
   - 显示大五人格要求
5. 点击"确认应聘" ✅
   - 系统计算人格匹配度
   - 显示匹配分析
6. 进入"应聘记录"查看历史 ✅
```

---

## 📋 验收清单

- [ ] 后端启动无错误
- [ ] 前端可访问
- [ ] HR 能生成岗位需求
- [ ] 候选人能看到岗位列表
- [ ] 能成功应聘岗位
- [ ] 显示匹配度分析

---

## 🎯 关键 API 测试

### 获取岗位需求

```bash
curl http://localhost:8000/jobs/requirements/1 \
  -H "Authorization: Bearer <token>"
```

### 计算匹配度

```bash
curl http://localhost:8000/jobs/match/123/1 \
  -H "Authorization: Bearer <token>"
```

---

## ❓ 常见问题

### Q: "后端无法启动"
**A:** 
- 检查数据库连接: `mysql -u root -p`
- 确保依赖已安装: `pip list | grep fastapi`
- 清理缓存: `rm -rf __pycache__`

### Q: "前端看不到岗位"
**A:**
- F12 打开控制台检查网络错误
- 确保 `VITE_API_URL` 正确
- 后端是否启动了?

### Q: "应聘失败"
**A:**
- 检查候选人 ID 是否存在
- 坚持完成了心理评估吗?
- 查看后端日志找错误信息

### Q: "JD 解析没有结果"
**A:**
- 检查 JD 是否包含关键技能词汇
- 尝试用标准格式重写
- 查看 SKILL_LIBRARY 是否包含该技能

---

## 📚 相关文档

- **完整实现指南**: [JOB_REQUIREMENTS_IMPLEMENTATION.md](JOB_REQUIREMENTS_IMPLEMENTATION.md)
- **交付总结**: [JOB_REQUIREMENTS_DELIVERY_SUMMARY.md](JOB_REQUIREMENTS_DELIVERY_SUMMARY.md)
- **API 文档**: http://localhost:8000/docs (启动后自动生成)

---

## 🚀 下一步

### 立即尝试
```bash
# 1. 验证系统
python backend/verify_job_requirements.py

# 2. 启动
python backend/main.py &
cd frontend && npm run dev

# 3. 打开浏览器
# http://localhost:5173
```

### 完成集成
- [ ] 在现有岗位管理页面中导入 `JobRequirementsManager.vue`
- [ ] 配置前端路由导向
- [ ] 测试完整的应聘流程

---

**⏱️ 预计时间: 5分钟**

**🎉 准备好了吗? 让我们开始吧!**
