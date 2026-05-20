# 简历上传功能 - 故障排除指南

## 概述

本指南帮助诊断和解决"文件解析失败，请手动填写表单"问题。该错误通常由后端文件处理失败引起。

---

## 🔍 快速诊断步骤

### 第1步：检查后端依赖库

这是最常见的问题原因。

```bash
# 在 backend 目录运行
python check_dependencies.py
```

**预期输出：** 所有库都显示 "已安装"

```
✓ python-docx         - 已安装
✓ pdfplumber          - 已安装
```

**如果显示缺失库，运行安装：**
```bash
pip install python-docx pdfplumber
```

---

### 第2步：运行后端测试

```bash
# 在 backend 目录运行
python test_resume_upload.py
```

**预期输出：**
```
==================================================
简历上传依赖检查工具
==================================================

✓ 所有测试通过!
```

---

### 第3步：使用前端测试工具

1. 启动后端服务：
   ```bash
   cd backend
   python main.py
   ```

2. 在浏览器打开测试页面：
   ```
   frontend/test-resume-upload.html
   ```

3. 在测试工具中：
   - 点击"测试TXT文件"进行最简单的测试
   - 如果TXT成功，逐步尝试PDF和Word

---

## 📋 完整问题排查

### 问题1：后端依赖库缺失

**症状：** 系统日志显示 `ImportError: No module named 'docx'` 或类似错误

**解决：**
```bash
# 方案A: 使用check_dependencies工具
python backend/check_dependencies.py
# 选择 'y' 自动安装

# 方案B: 手动安装
pip install python-docx pdfplumber

# 方案C: 从requirements.txt安装所有依赖
pip install -r backend/requirements.txt
```

---

### 问题2：Python库版本不兼容

**症状：** 库已安装但仍然出现导入错误

**解决：**
```bash
# 升级所有库
pip install --upgrade python-docx pdfplumber

# 或强制重新安装指定版本
pip install python-docx==0.8.11 pdfplumber==0.10.3
```

---

### 问题3：特定文件格式不支持

**症状：** TXT成功，但PDF或Word失败

**排查步骤：**

1. **PDF 失败**
   - 确认 pdfplumber 已安装
   - 尝试用其他PDF工具打开文件（可能损坏）
   - 查看后端日志：`pdfplumber processing failed`

2. **Word 失败**
   - 确认 python-docx 已安装
   - 尝试 .docx 格式（不支持 .doc）
   - 用Word重新保存为.docx后重试

3. **图片失败**
   - 系统不支持OCR，这是正常的
   - 用户需手动填表或转换为PDF

---

### 问题4：网络/API错误

**症状：** 前端显示网络错误，无法连接到后端

**解决步骤：**

1. 检查后端是否运行：
   ```bash
   curl http://localhost:8000/assessment/immersive/status
   ```
   
   应返回成功响应

2. 检查CORS设置（如适用）

3. 确认前端请求URL正确：
   ```javascript
   // 应为
   http://localhost:8000/assessment/immersive/upload-resume
   ```

---

### 问题5：文件大小限制

**症状：** 大文件上传失败

**解决：**
- 最大限制：10MB
- 压缩PDF或Word文件
- 移除图片/嵌入内容减小文件大小

---

## 🧪 完整测试流程

### 场景A：完全从零开始

```bash
# 1. 进入项目目录
cd graduation-project

# 2. 检查依赖
cd backend
python check_dependencies.py
# 如果缺失，选择自动安装或手动运行 pip install ...

# 3. 运行单元测试
python test_resume_upload.py

# 4. 启动后端
python main.py
# 应看到: "Uvicorn running on http://0.0.0.0:8000"

# 5. 打开前端测试工具（新终端/浏览器）
# 浏览器打开: file:///path/to/frontend/test-resume-upload.html
# 点击 "测试TXT文件"

# 6. 检查结果
# ✓ 成功: 看到提取的候选人信息（姓名、邮箱、技能等）
# ✗ 失败: 查看日志部分的错误消息
```

### 场景B：现有系统故障排除

```bash
# 1. 检查依赖
cd backend
python check_dependencies.py

# 2. 查看最近的后端日志
# 查找 "extract_resume_text" 或 "_parse_resume_info" 相关错误

# 3. 清除任何缓存
# 清空 browser cache Ctrl+Shift+Delete

# 4. 重启后端
# 倒掉旧进程，重新运行 python main.py

# 5. 从简单文件开始测试
# 先测试 .txt，再尝试 .pdf/.docx
```

---

## 📁 相关文件位置

| 文件 | 用途 | 位置 |
|------|------|------|
| requirements.txt | 依赖声明 | `backend/` |
| check_dependencies.py | 依赖检查工具 | `backend/` |
| test_resume_upload.py | 完整功能测试 | `backend/` |
| test-resume-upload.html | 前端测试工具 | `frontend/` |
| immersive_dialogue.py | 后端实现 | `backend/routers/` |
| ImmersiveRoleDialogue.vue | 前端组件 | `frontend/src/components/` |

---

## 🔧 手工测试示例

### 使用cURL测试上传

```bash
# 创建测试TXT文件
echo "姓名: 测试
邮箱: test@example.com
技能: Python, JavaScript" > test.txt

# 测试上传
curl -X POST "http://localhost:8000/assessment/immersive/upload-resume?candidate_id=test123" \
  -F "file=@test.txt"

# 预期响应（200 OK）:
# {
#   "code": 200,
#   "data": {
#     "candidate_info": {
#       "email": "test@example.com",
#       "technical_skills": ["Python", "JavaScript"],
#       ...
#     }
#   }
# }
```

### 使用PowerShell测试

```powershell
# 创建测试文件
"姓名: 测试`n邮箱: test@example.com" | Out-File test.txt -Encoding UTF8

# 测试上传
$uri = "http://localhost:8000/assessment/immersive/upload-resume?candidate_id=test123"
$filePath = "test.txt"
$file = [System.IO.File]::ReadAllBytes($filePath)

$form = @{
    'file' = [System.IO.FileInfo]$filePath
}

Invoke-WebRequest -Uri $uri -Method POST -Form $form
```

---

## 📊 日志分析指南

### 成功日志示例

```
[2024-01-15 10:30:45] INFO: 上传简历: candidate_id=test123, filename=resume.txt, ext=.txt
[2024-01-15 10:30:45] INFO: 文件大小: 2048 bytes
[2024-01-15 10:30:45] INFO: 提取 TXT 格式文件
[2024-01-15 10:30:45] INFO: 提取文本成功，长度: 1500
[2024-01-15 10:30:45] INFO: 开始解析简历文本，长度: 1500
[2024-01-15 10:30:45] INFO: 提取邮箱: test@example.com
[2024-01-15 10:30:45] INFO: 解析完成: {'email': 'test@example.com', ...}
```

### 失败日志示例与对应

| 日志内容 | 含义 | 解决方案 |
|---------|------|---------|
| `python-docx 库未安装` | Word库缺失 | `pip install python-docx` |
| `pdfplumber 库未安装` | PDF库缺失 | `pip install pdfplumber` |
| `DOCX 文档为空` | Word文档无内容 | 检查上传的文档 |
| `PDF 文档为空` | PDF无可识别内容 | 尝试重新扫描或转换格式 |
| `文件大小超过10MB` | 文件太大 | 压缩或分割文件 |

---

## 🚀 快速修复清单

若遇到"文件解析失败"，按顺序尝试：

- [ ] 运行 `python check_dependencies.py` 检查依赖
- [ ] 运行 `python test_resume_upload.py` 测试功能
- [ ] 用 `.txt` 文件测试（最简单的格式）
- [ ] 检查后端日志中的实际错误消息
- [ ] 重启后端服务
- [ ] 清除浏览器缓存
- [ ] 检查Python和pip版本（建议Python 3.8+）

---

## 📞 获取更多信息

### 收集诊断信息

若问题未解决，收集以下信息：

```bash
# 1. Python版本
python --version

# 2. 依赖库版本
pip list | grep -E "docx|pdfplumber|fastapi"

# 3. 测试工具输出
python backend/test_resume_upload.py 2>&1 | tee test_output.txt

# 4. 后端日志
# (运行 python main.py 时的完整输出)

# 5. 前端浏览器控制台日志
# (F12 打开开发者工具，查看 Console 标签)
```

---

## 常见问题 (FAQ)

**Q: 为什么TXT成功但PDF失败？**
A: pdfplumber库可能未安装或损坏。尝试 `pip install --upgrade pdfplumber`

**Q: 是否支持.doc格式（旧版Word）？**
A: 建议转换为.docx。.doc需要额外库（python-docx版本有限制）

**Q: 上传后表单未自动填充？**
A: 检查：1) 后端返回200状态码？2) JSON响应是否有效？3) 前端是否成功解析？

**Q: 能否支持图片简历？**
A: 暂不支持OCR。可在后期添加阿里云或Google Vision API支持

**Q: 文件大小有限制吗？**
A: 是的，最大10MB。超过则会收到"文件大小超过限制"错误

---

## 下一步

配置完成后：

1. ✅ 验证依赖已安装
2. ✅ 确认后端可正常上传和解析
3. ✅ 在生产前关闭调试日志
4. ✅ 考虑添加更多文件格式支持
5. ✅ 优化提取和解析算法准确率

---

*最后更新: 2024年*
*此文档对应后端版本 v1.2+*
