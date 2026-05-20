# 简历文件解析功能配置指南

## 功能概述

用户可以上传 PDF 或 Word 文档，系统会自动解析并填入表单字段（姓名、邮箱、学历、技能等）。

## 支持的文件格式

- ✅ **PDF** (.pdf) - 需要 `pdfplumber`
- ✅ **Word** (.docx, .doc) - 需要 `python-docx`
- ✅ **纯文本** (.txt) - 无需额外库
- ✅ **图片** (.jpg, .png) - 需要 OCR（暂不支持）

## 后端依赖安装

### 方式一：pip 安装（推荐）

```bash
# 进入后端目录
cd backend

# 安装 PDF 解析库
pip install pdfplumber

# 安装 Word 解析库  
pip install python-docx
```

### 方式二：从 requirements.txt 安装

```bash
# 已自动添加到 requirements.txt 中
pip install -r requirements.txt
```

### 如果 SSL 证书错误

```bash
# 方式1：临时禁用SSL验证（不推荐用于生产环境）
pip install --trusted-host pypi.python.org -i http://pypi.python.org/simple pdfplumber python-docx

# 方式2：升级 pip 和 certifi
pip install --upgrade pip certifi
pip install pdfplumber python-docx

# 方式3：使用国内镜像源
pip install -i https://mirrors.aliyun.com/pypi/simple pdfplumber python-docx
```

## 前端功能

### 功能流程

1. 用户点击上传区域选择或拖拽 PDF/Word 文件
2. 前端自动调用后端 API：`POST /assessment/immersive/upload-resume`
3. 后端解析文件内容，提取关键信息
4. 解析结果自动填入表单字段（如果有内容）
5. 用户可以编辑或补充信息，然后继续

### 自动识别的字段

- **姓名**：通过正则表达式和名字库识别
- **邮箱**：提取所有邮箱地址
- **电话**：识别手机号和座机号
- **学历**：匹配学位关键词（本科、硕士、博士等）
- **技能**：识别常见的技术栈关键词
- **工作经验**：提取工作经历相关段落

### 前端提示

- 自动填入的字段会显示 **"✓ 已自动填入"** 提示
- 上传过程中显示加载动画
- 解析失败时显示友好的错误提示

## API 端点

### 1. 简历文件上传解析

**端点**: `POST /assessment/immersive/upload-resume`

**请求参数**:
- `file`: 简历文件 (FormData)
- `candidate_id`: 候选人ID (Query)

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "filename": "resume.pdf",
    "file_size": 102400,
    "extracted_text": "...",
    "candidate_info": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "phone": "13800138000",
      "education": "本科",
      "technical_skills": ["JavaScript", "Python", "Vue.js"],
      "work_experience": "..."
    }
  },
  "message": "简历解析成功"
}
```

### 2. 候选人信息解析

**端点**: `POST /assessment/immersive/parse-resume`

**请求参数**:
- `candidate_id`: 候选人ID
- `candidate_name`: 候选人姓名
- `candidate_email`: 邮箱地址
- `education`: 教育背景
- `skills`: 技能标签 (逗号分隔)
- `projects`: 项目经验

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "candidate_info": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "education": "本科",
      "experience_level": "中级",
      "technical_skills": ["JavaScript", "Python"],
      "soft_skills": ["团队协作", "沟通"]
    },
    "profile_completeness": 0.8,
    "assessed_dimensions": ["技术能力", "沟通能力"]
  },
  "message": "简历解析成功"
}
```

## 故障排除

### 问题1: ImportError 提示缺少库

**解决**: 安装相应的库
```bash
pip install pdfplumber python-docx
```

### 问题2: PDF 文件无法解析

**检查**:
- 确认 PDF 是否已加密
- 检查 PDF 是否为扫描版本（不支持）
- 尝试更新 pdfplumber：`pip install --upgrade pdfplumber`

### 问题3: Word 文件解析失败

**检查**:
- 确认文件格式是否为 .docx（不是 .doc）
- 尝试在 Word 中重新保存一次
- 检查文件是否损坏

### 问题4: 自动填入信息不准确

**原因**:
- 简历格式不标准
- 信息位置过于复杂

**解决**:
- 用户可以手动编辑表单
- 提供更规范格式的简历

## 开发调试

### 测试本地文件解析

```python
# 在后端测试文件解析
with open('path/to/resume.pdf', 'rb') as f:
    content = f.read()
    text = _extract_resume_text(content, '.pdf')
    print(text)
```

### 查看提取的关键词

```python
from routers.immersive_dialogue import _parse_resume_info

text = "..."
info = _parse_resume_info(text)
print(info)
```

## 文件大小限制

- 最大上传大小：**10MB**
- 前端限制
- 后端验证

## 安全考虑

- ✅ 文件类型验证
- ✅ 文件大小限制
- ✅ 临时存储（不保存原文件）
- ✅ 信息脱敏处理

## 后续改进

- [ ] 支持图片 OCR 识别
- [ ] 支持更多文件格式 (.doc, .xls 等)
- [ ] 智能去重和冲突处理
- [ ] 用户反馈学习文件格式

## 联系支持

如有问题，请检查：
1. 后端日志输出
2. 浏览器开发者工具的网络标签
3. 前端控制台错误信息
