# 🚀 快速重启&测试指南

**修复完成**: ✅ 语法错误已解决

---

## ⚡ 立即重启 (1 分钟)

### Step 1: 停止当前后端

在运行后端的 PowerShell 窗口中按:
```
Ctrl + C
```

### Step 2: 确认虚拟环境

```powershell
# 应该看到 (venv) 前缀
# 如果没有，运行:
venv\Scripts\activate
```

### Step 3: 重启后端

```powershell
python main.py
```

### Step 4: 验证启动

应该看到:
```
INFO:     Application startup complete.
```

**而不是**:
```
SyntaxError: expected 'except' or 'finally' block
```

---

## 🧪 测试简历上传 (3-5 分钟)

### 方法 1: 浏览器测试 (推荐)

1. **打开前端**:
   ```
   访问: http://localhost:5173
   ```

2. **登录或注册**:
   - 如果是新用户，先完成注册

3. **开始评估**:
   - 点击 "开始评估" 或 "Start Assessment"

4. **进入基本信息步骤**:
   - 第一个步骤就是填写基本信息

5. **上传简历**:
   - 看到 "拖拽简历" 或 "上传简历" 区域
   - 拖拽或点击选择一个 PDF/Word 文件
   - 等待上传完成

6. **验证结果**:
   - 表单自动填充: 姓名、邮箱、电话等
   - 查看后台日志确认 OCR 成功

### 方法 2: 命令行测试 (快速诊断)

准备一个简历文件 (假设在 `D:\resume.pdf`):

```bash
# 测试上传
curl -X POST http://localhost:8000/api/candidates/upload_resume \
  -F "file=@D:\resume.pdf"

# 应该看到 JSON 回复:
# {
#   "code": 200,
#   "message": "成功",
#   "data": {
#     "name": "张三",
#     "email": "zhangsan@example.com",
#     "phone": "13800138000",
#     "resume_url": "/uploads/resume_xxxxx.pdf",
#     "education": "本科",
#     "major": "计算机科学",
#     "experience_years": 3,
#     "skills": ["Python", "Java", "SQL"]
#   }
# }
```

---

## 📊 预期效果

### ✅ 修复成功的标志

**后端日志**:
```
2026-03-28 16:50:00 INFO     Uvicorn running on http://127.0.0.1:8000
2026-03-28 16:50:01 INFO     Application startup complete.
2026-03-28 16:50:15 INFO     POST /api/candidates/upload_resume HTTP/1.1" 200 OK
```

**浏览器显示**:
- 简历上传区域可见
- 上传文件后显示进度
- 文字识别成功，表单自动填充

---

## ❌ 如果还有问题

### 问题 1: 仍然看到语法错误

```
SyntaxError: expected 'except' or 'finally' block
```

**解决方案**:
1. 检查是否保存了主要的修复
2. 重新运行修复脚本
3. 查看 immersive_dialogue.py 第 790-810 行是否正确

### 问题 2: OCR 还是失败

```
❌ PaddleOCR 初始化失败: AttributeError...
❌ EasyOCR 未安装
```

**解决方案**:
```powershell
# 运行修复工具
python fix_paddleocr_issue.py

# 或手动安装
pip install --upgrade paddleocr paddlepaddle
```

### 问题 3: 上传时 500 错误

```
Internal Server Error
```

**诊断步骤**:
1. 查看后端控制台的完整错误信息
2. 确认文件格式正确 (.pdf, .docx, .txt, .jpg, .png)
3. 确认文件大小 < 10MB
4. 检查 `/uploads` 目录是否存在和可写

### 问题 4: 识别结果为空或不准确

**可能的原因**:
- PDF 是扫描版本 (图片) 需要 OCR
- 文字是图片形式 PaddleOCR/EasyOCR 需要学习

**解决方案**:
- 确保 PaddleOCR 或 EasyOCR 正确安装
- 尝试上传 Word 文档 (.docx) 代替
- 手动调整识别结果

---

## 📚 完整参考

| 文档 | 用途 |
|------|------|
| `RESUME_PARSING_COMPLETE_WORKFLOW.md` | 完整的解析工作流 |
| `PADDLEOCR_FIX_GUIDE.md` | OCR 问题修复 |
| `NEXT_STEPS_IMPLEMENTATION_PLAN.md` | 下周开发计划 |
| `DEVELOPMENT_PROGRESS_REPORT.md` | 项目进度报告 |

---

## ✅ 快速检查清单

- [ ] 后端成功启动 (见 "Application startup complete")
- [ ] 前端可访问 (http://localhost:5173)
- [ ] 可以登录/注册
- [ ] 可以开始评估流程
- [ ] 简历上传区域显示
- [ ] 上传文件成功
- [ ] OCR 识别成功 (表单自动填充)
- [ ] 查看后端日志无错误

完成后，继续本周的开发任务！

---

*修复完成时间: 2026-03-28*  
*重启难度: 极简单 (1 分钟)*  
*测试难度: 简单 (3-5 分钟)*
