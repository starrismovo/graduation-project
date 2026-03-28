# 🔍 简历解析模块完整逻辑梳理分析

**日期**: 2026-03-28  
**版本**: 2.0 (优化版本)  
**状态**: 已部署

---

## 📋 目录

1. [模块概览](#模块概览)
2. [处理流程](#处理流程)
3. [API端点](#api端点)
4. [核心函数](#核心函数)
5. [数据模型](#数据模型)
6. [错误处理](#错误处理)
7. [问题诊断](#问题诊断)

---

## 模块概览

### 功能定位
简历解析模块负责：
✅ 接收多种格式的简历文件（PDF、Word、图片、纯文本）  
✅ 自动提取文本内容  
✅ 使用 OCR 识别扫描版/图片简历  
✅ 从文本中解析候选人信息  
✅ 返回结构化的候选人数据  

### 核心技术栈
```
文件处理: python-docx (Word) + pdfplumber (PDF)
文本识别: PaddleOCR (主) + EasyOCR (备选)
数据验证: Pydantic
数据库: SQLAlchemy (MySQL)
```

---

## 处理流程

### 完整处理管道

```
┌─────────────────────────────────────────────────────────────┐
│                  POST /upload-resume                         │
│                    (文件上传端点)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  1️⃣ 文件验证                 │
        ├─────────────────────────────┤
        │ • 扩展名检查                  │
        │ • 文件大小检查 (≤10MB)        │
        │ • 候选人ID验证               │
        └────────┬────────────────────┘
                 │ 通过 ✅
                 ▼
        ┌─────────────────────────────┐
        │  2️⃣ 文件内容读取             │
        ├─────────────────────────────┤
        │ • 异步读取文件               │
        │ • 计算文件大小               │
        └────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────────────────┐
        │  3️⃣ 文本提取 (_extract_resume_text)         │
        ├─────────────────────────────────────────────┤
        │ ┌───────────────┐                          │
        │ │ .txt 格式     │  → 直接 UTF-8 解码       │
        │ ├───────────────┤                          │
        │ │ .docx 格式    │  → python-docx 解析      │
        │ ├───────────────┤                          │
        │ │ .pdf 格式     │  → pdfplumber 提取       │
        │ │               │     ↓ (失败则用 OCR)     │
        │ ├───────────────┤                          │
        │ │ .jpg/.png     │  → 直接使用 OCR          │
        │ ├───────────────┤                          │
        │ │ .doc 旧格式   │  → 降级处理              │
        │ └───────────────┘                          │
        └────────┬────────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────────────────┐
        │  4️⃣ OCR 识别 (_ocr_extract_text)            │
        │     (如需要)                                │
        ├─────────────────────────────────────────────┤
        │ ┌────────────────────┐                      │
        │ │ 方案1: PaddleOCR   │                      │
        │ │ (如果可用)          │ ──→ 提取文本        │
        │ └────────────────────┘     ↓ (失败)        │
        │ ┌────────────────────┐     │               │
        │ │ 方案2: EasyOCR     │←────┘               │
        │ │ (备选)             │ ──→ 提取文本        │
        │ └────────────────────┘     ↓ (失败)        │
        │ ┌────────────────────┐     │               │
        │ │ 方案3: 回退消息    │←────┘               │
        │ │ (用户友好提示)      │                      │
        │ └────────────────────┘                      │
        └────────┬────────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────┐
        │  5️⃣ 信息解析 (_parse_resume_info) │
        ├─────────────────────────────────┤
        │ • 提取：姓名                     │
        │ • 提取：邮箱                     │
        │ • 提取：电话号码                 │
        │ • 提取：教育背景                 │
        │ • 提取：技术技能                 │
        │ • 提取：软技能                   │
        │ • 提取：工作经历                 │
        └────────┬────────────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │  6️⃣ 数据关联与补充       │
        ├──────────────────────────┤
        │ • 计算信息完整性          │
        │ • 推断经验水平            │
        │ • 生成评估维度            │
        │ • 提取关键词              │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │  7️⃣ 返回结果             │
        └──────────────────────────┘
```

### 每个步骤的详细说明

#### 1️⃣ **文件验证** (upload_resume 开始)

```python
# 验证内容
allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
file_ext = '.' + file.filename.split('.')[-1].lower()

# 验证1：扩展名
if file_ext not in allowed_extensions:
    return {"code": 400, "message": "不支持的文件格式"}

# 验证2：候选人ID
candidate_id = _validate_candidate_id(candidate_id)  # 必须 1-100 字符

# 验证3：文件大小
if file_size > 10 * 1024 * 1024:
    return {"code": 400, "message": "文件大小超过10MB限制"}
```

#### 2️⃣ **文本提取** (_extract_resume_text)

根据文件格式调用对应的提取器：

| 格式 | 处理方式 | 库 / 方法 | 备注 |
|------|--------|---------|------|
| `.txt` | 直接解码 | `content.decode('utf-8')` | 最简单 |
| `.docx` | 解析文档结构 | `python-docx` | 如果失败→降级处理 |
| `.pdf` | 提取文本层 | `pdfplumber` | 如果为空→使用 OCR |
| `.jpg/.jpeg/.png` | 直接 OCR | `ocr.ocr()` | 必须使用 OCR |
| `.doc` | 降级处理 | 纯文本查找 | 提示用户升级格式 |

#### 3️⃣ **OCR 识别** (_ocr_extract_text)

**三层保障机制**:

```python
# 第1层：PaddleOCR (主方案)
try:
    ocr = create_paddleocr()  # 延迟加载，只在需要时初始化
    result = ocr.ocr(image, cls=False)
    text = "\n".join([line[1][0] for line in result[0]])
    if text.strip():
        return text  ✅ 成功

except AttributeError/ValueError/Exception as e:
    # 第2层：EasyOCR (备选)
    try:
        reader = easyocr.Reader(['ch'], gpu=False)
        result = reader.readtext(image, detail=0)
        text = '\n'.join(result)
        if text.strip():
            return text  ✅ 成功
    
    except ImportError:
        logger.info("EasyOCR 未安装")
    
    except Exception as easy_err:
        logger.error(f"EasyOCR 失败: {easy_err}")

# 第3层：回退消息
return "【⚠️ OCR功能暂时不可用】\n..." ⚠️ 降级
```

#### 4️⃣ **信息解析** (_parse_resume_info)

从文本中使用**正则表达式**提取结构化信息：

```python
info = {
    "name": "未提取",           # 姓名
    "email": "",                # 邮箱（正则匹配）
    "phone": "",                # 电话（支持多种格式）
    "education": "",            # 学历（关键词搜索）
    "technical_skills": [],     # 技术技能（库匹配）
    "work_experience": "",      # 工作经历（关键词提取）
    "soft_skills": []           # 软技能（语义识别）
}

# 示例提取规则
姓名:      r'(?:^|\n)\s*姓名[:\s：]+([^\n\r，,]+)'
邮箱:      r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
电话:      r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}'
学历:      使用关键词 ["本科", "硕士", "博士", "Bachelor", "Master", ...]
技能:      从技能库 (TECH_SKILLS_LIBRARY) 中查找匹配
```

#### 5️⃣ **数据关联与补充**

```python
# 基于学历推断经验水平
education_mapping = {
    "高中": "初级",
    "大专": "初级",
    "本科": "中级",
    "硕士": "高级",
    "博士": "专家级"
}

# 计算信息完整性 (0-1)
completed_fields = sum([
    bool(name),
    bool(email),
    bool(education),
    bool(technical_skills),
    bool(work_experience)
])
profile_completeness = completed_fields / 5.0

# 生成评估维度
assessed_dimensions = ["技术能力"]
if technical_skills:
    assessed_dimensions.append("技术深度")
if soft_skills:
    assessed_dimensions.extend(soft_skills)
if experience_level in ["高级", "专家级"]:
    assessed_dimensions.extend(["领导力", "战略思维"])
```

---

## API端点

### POST `/assessment/immersive/upload-resume`

**请求头**:
```http
POST /assessment/immersive/upload-resume?candidate_id=123 HTTP/1.1
Content-Type: multipart/form-data
```

**请求体**:
```
file: <二进制文件内容>
candidate_id: 候选人ID
```

**响应成功 (200)**:
```json
{
  "code": 200,
  "message": "简历解析成功",
  "data": {
    "filename": "resume.pdf",
    "file_size": 102400,
    "extracted_text": "前500字预览...",
    "extraction_method": "native" | "ocr",
    "candidate_info": {
      "name": "张三",
      "email": "zhang@example.com",
      "phone": "13800138000",
      "education": "本科",
      "experience_level": "中级",
      "technical_skills": ["Python", "JavaScript", "Vue"],
      "soft_skills": ["沟通能力", "团队协作"],
      "work_experience": "5年开发经验..."
    },
    "extracted_keywords": ["Python", "JavaScript", "沟通能力", "学历:本科"],
    "profile_completeness": 0.8,
    "assessed_dimensions": ["技术能力", "技术深度", "沟通能力", "团队协作"]
  }
}
```

**响应失败 - 文件格式错误 (400)**:
```json
{
  "code": 400,
  "message": "不支持的文件格式: .exe",
  "data": null
}
```

**响应部分成功 - OCR 不可用 (200)**:
```json
{
  "code": 200,
  "message": "【⚠️ OCR功能暂时不可用】...",
  "data": {
    "extraction_method": "native",
    "candidate_info": {
      "name": "未提取",
      "technical_skills": [],
      ...
    }
  }
}
```

---

## 核心函数

### 1. upload_resume (主入口)

**位置**: `backend/routers/immersive_dialogue.py:535`

**职责**:
- 接收文件上传请求
- 验证文件和候选人ID
- 协调整个处理流程
- 返回规范化结果

**流程**:
1. 验证文件类型和大小
2. 读取文件内容
3. 调用 `_extract_resume_text()` 提取文本
4. 调用 `_parse_resume_info()` 解析信息
5. 生成评估维度和关键词
6. 返回完整结果

### 2. _extract_resume_text (文本提取)

**位置**: `backend/routers/immersive_dialogue.py:858`

**职责**:
- 根据文件格式调用合适的提取器
- 处理各类异常和降级

**处理逻辑**:
```python
if file_ext == '.txt':
    return content.decode('utf-8', errors='ignore')

elif file_ext == '.docx':
    from docx import Document
    doc = Document(BytesIO(content))
    return '\n'.join([para.text for para in doc.paragraphs])

elif file_ext == '.pdf':
    try:
        import pdfplumber
        with pdfplumber.open(BytesIO(content)) as pdf:
            text = '\n'.join([page.extract_text() or '' for page in pdf.pages])
        if text:
            return text
        else:
            # PDF 无文本内容，使用 OCR
            ocr_text = _ocr_extract_text(content, file_ext)
            return f"【OCR识别】{ocr_text}" if ocr_text else "【PDF文档已上传但无可识别内容】"
    except ImportError:
        return "【PDF文件已上传】请安装: pip install pdfplumber"

elif file_ext in ['.jpg', '.jpeg', '.png']:
    ocr_text = _ocr_extract_text(content, file_ext)
    return f"【OCR识别】{ocr_text}" if ocr_text else "【图片文件无可识别内容】"

elif file_ext == '.doc':
    return "【Word 97-2003格式已上传】请转换为 .docx 格式"
```

### 3. _ocr_extract_text (OCR识别)

**位置**: `backend/routers/immersive_dialogue.py:714`

**职责**:
- 使用 PaddleOCR 或 EasyOCR 识别文本
- 处理多页 PDF
- 提供多层备选方案

**三层方案**:

```
PaddleOCR (主)
    ↓ 失败
EasyOCR (备选)
    ↓ 都失败
返回用户友好的提示
```

**PDF 处理**:
```python
import pdfplumber
with pdfplumber.open(BytesIO(content)) as pdf:
    for page_num, page in enumerate(pdf.pages):
        # 每页转换为 300DPI 图片
        im = page.to_image(resolution=300)
        pil_image = im.original
        
        # OCR 识别
        result = ocr.ocr(pil_image, cls=False)
        
        # 提取文本
        page_text = "\n".join([line[1][0] for line in result[0]])
        all_text.append(page_text)
```

### 4. _parse_resume_info (信息解析)

**位置**: `backend/routers/immersive_dialogue.py:950`

**职责**:
- 从文本中提取候选人关键信息
- 进行数据清洗和验证
- 返回结构化数据

**提取的字段**:

| 字段 | 提取方法 | 示例 |
|------|--------|------|
| name | 正则匹配 | "张三"、"Zhang San" |
| email | 正则匹配 | "zhang@example.com" |
| phone | 正则匹配 | "13800138000", "010-12345678" |
| education | 关键词搜索 | "本科", "Bachelor" |
| technical_skills | 库匹配 + 文本搜索 | ["Python", "JavaScript"] |
| work_experience | 文本提取 | "5年工作经验..." |
| soft_skills | 关键词聚类 | ["沟通能力", "团队协作"] |

---

## 数据模型

### 1. ResumeParseRequest (Pydantic)

```python
class ResumeParseRequest(BaseModel):
    candidate_id: str          # 候选人ID (1-100字符)
    candidate_name: str        # 姓名 (1-50字符)
    candidate_email: Optional[str]  # 邮箱
    education: Optional[str]   # 学历 (高中|大专|本科|硕士|博士)
    skills: Optional[str]      # 技能 (逗号分隔)
    projects: Optional[str]    # 项目经验 (最多2000字符)
```

### 2. 候选人信息结构

```python
{
    "name": str,                          # 姓名
    "email": str,                         # 邮箱
    "phone": str,                         # 电话
    "education": str,                     # 学历
    "experience_level": str,              # 经验水平
    "technical_skills": List[str],        # 技术技能
    "soft_skills": List[str],             # 软技能
    "work_experience": str,               # 工作经历
}
```

### 3. API 响应结构

```python
{
    "code": int,                          # HTTP状态码
    "message": str,                       # 业务消息
    "data": {
        "filename": str,
        "file_size": int,
        "extracted_text": str,            # 前500字预览
        "extraction_method": str,         # "native" 或 "ocr"
        "candidate_info": {...},          # 候选人信息
        "extracted_keywords": List[str],  # 关键词
        "profile_completeness": float,    # 0.0-1.0
        "assessed_dimensions": List[str]  # 评估维度
    }
}
```

---

## 错误处理

### 异常体系 (resume_parsing_v2.py)

```python
ResumeProcessingException (基类)
├── InvalidFileFormatException      # 不支持的格式
├── FileTooLargeException           # 文件过大
├── TextExtractionException         # 文本提取失败
├── OCRProcessingException          # OCR 识别失败
└── InfoParsingException            # 信息解析失败
```

### 错误响应示例

#### 文件格式错误
```json
{
  "code": 400,
  "error_code": "INVALID_FILE_FORMAT",
  "message": "不支持的文件格式: .exe",
  "details": {
    "provided": ".exe",
    "allowed": [".pdf", ".docx", ".txt", ...]
  }
}
```

#### 文件过大
```json
{
  "code": 413,
  "error_code": "FILE_TOO_LARGE",
  "message": "文件大小 15.5MB 超过限制 10.0MB",
  "details": {
    "size": 16252928,
    "limit": 10485760
  }
}
```

#### OCR 不可用
```json
{
  "code": 200,
  "message": "【⚠️ OCR功能暂时不可用】\n所有OCR方案都失败，请尝试其他格式或手动填写",
  "data": {...}
}
```

---

## 问题诊断

### 🔍 当前已知问题

#### 问题 1: set_optimization_level 兼容性 ✅ 已修复
- **症状**: `AttributeError: set_optimization_level`
- **原因**: PaddleOCR + PaddlePaddle 版本不兼容
- **解决**: 
  - PaddleX 补丁 (static_infer.py)
  - PaddleOCR 延迟加载

#### 问题 2: EasyOCR 未安装
- **症状**: OCR 完全失败
- **原因**: EasyOCR 未在 requirements.txt 中
- **解决**: 可选安装 `pip install easyocr`

#### 问题 3: PDF 提取为空
- **症状**: PDF 上传成功但无文本内容
- **原因**: 1) PDF 确实无文本层 2) OCR 不可用
- **解决**: 使用扫描为图片的 PDF，确保 OCR 可用

### 📊 性能瓶颈

| 操作 | 耗时 | 瓶颈 |
|------|------|------|
| 文件读取 | < 100ms | 网络带宽 |
| 文本提取 (PDF) | 200-500ms | I/O 操作 |
| OCR 识别 (首次) | 2000-5000ms | 模型加载 |
| OCR 识别 (缓存后) | 500-1500ms | CPU 计算 |
| 信息解析 | 50-100ms | 正则表达式 |

### 🚀 优化建议

1. **OCR 模型缓存** ✅ (已实现)
   - 使用 `OCRModelCache` 单例模式
   - 避免重复加载

2. **异步处理** ⏳ (计划中)
   - 长文件使用后台任务
   - 实现进度回调

3. **精度优化** ⏳ (计划中)
   - 改进正则表达式
   - 增加软技能识别
   - 使用 NLP 模型提取

4. **缓存策略** ⏳ (计划中)
   - 技能库预加载
   - 正则表达式编译缓存

---

## 📞 支持信息

### 测试简历文件

推荐测试格式：
- ✅ `.docx` - 最可靠
- ✅ `.txt` - 最快
- ⚠️ `.pdf` - 需要 pdfplumber
- ⚠️ `.jpg` - 需要 OCR

### 常见命令

```bash
# 安装依赖
pip install python-docx pdfplumber pillow

# 可选：安装 EasyOCR
pip install easyocr

# 测试 PaddleOCR
python test_paddleocr.bat

# 查看日志
tail -f backend.log | grep "简历"
```

### 文档参考

- [PADDLEOCR_SETOPTIMIZATION_FIX.md](PADDLEOCR_SETOPTIMIZATION_FIX.md) - OCR 兼容性修复
- [PADDLEOCR_FIX_GUIDE.md](PADDLEOCR_FIX_GUIDE.md) - 完整故障排除
- [resume_parsing_v2.py](../backend/services/resume_parsing_v2.py) - 优化版实现

---

**上次更新**: 2026-03-28  
**主要贡献者**: AI Assistant  
**状态**: 生产就绪 ✅
