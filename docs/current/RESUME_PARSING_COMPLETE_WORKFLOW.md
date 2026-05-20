# 📄 简历解析完整工作流说明

**问题解决时间**: 2026-03-28 16:30  
**状态**: ✅ 语法错误修复完成 + 工作流说明  

---

## 🔄 简历解析的完整调用流程

### 流程图

```
用户上传简历
  ↓
前端 POST /api/candidates/upload_resume
  ↓
后端接收文件 (immersive_dialogue.py)
  ├─ 验证文件大小、类型
  ├─ 保存到临时目录
  └─ 调用 _extract_resume_text()  ← 文本提取
      ↓
      ├─ 检测文件类型 (.txt, .pdf, .docx, .jpg, .png)
      ├─ 如果是 .txt: 直接解码
      ├─ 如果是 .docx: 使用 python-docx
      ├─ 如果是 .pdf: 
      │   ├─ 先用 pdfplumber 提取文本
      │   └─ 如果为空，调用 _ocr_extract_text()  ← OCR 识别
      └─ 如果是 .jpg/.png: 直接调用 _ocr_extract_text()
           ↓
           └─ OCR 识别流程:
               ├─ 尝试 PaddleOCR (优先)
               │   ├─ 初始化模型
               │   ├─ 转换为图片
               │   ├─ 逐页识别
               │   └─ 返回文本
               │
               ├─ 如果 PaddleOCR 失败 → 尝试 EasyOCR (备选)
               │   ├─ 初始化模型
               │   ├─ 识别图片
               │   └─ 返回文本
               │
               └─ 如果全部失败 → 返回降级消息
                   └─ 用户可以手动填写
  
  ↓
调用 resume_parsing_v2.py 提取结构化信息
  ├─ 名字、邮箱、电话
  ├─ 教育背景（学位、专业）
  ├─ 工作经历（公司、职位、年限）
  └─ 技能列表

  ↓
返回给前端
  ├─ 识别的数据
  └─ resume_url (文件存储位置)

  ↓
前端显示识别结果
  ├─ 用户可以修改
  └─ 用户提交
```

---

## 📝 关键代码位置说明

### 1. **简历上传入口**
**文件**: `backend/routers/immersive_dialogue.py`  
**函数**: `/upload_resume` API endpoint (第 ~590 行)

```python
@router.post("/upload_resume")
async def upload_resume(file: UploadFile):
    """
    接收简历文件
    支持: .pdf .docx .doc .txt .jpg .png
    """
    # 1. 验证文件
    # 2. 保存文件
    # 3. 提取文本
    # 4. 解析信息
    # 5. 返回结果
```

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/candidates/upload_resume \
  -F "file=@resume.pdf"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "education": "本科",
    "major": "计算机科学",
    "skills": ["Python", "Java", "SQL"],
    "experience_years": 3,
    "resume_url": "/uploads/resume_xxxxx.pdf"
  }
}
```

---

### 2. **文本提取函数**
**文件**: `backend/routers/immersive_dialogue.py`  
**函数**: `_extract_resume_text(content, file_ext)` (第 ~900 行)

**支持的格式**:

| 格式 | 处理方式 | 状态 |
|------|--------|------|
| `.txt` | UTF-8 解码 | ✅ 支持 |
| `.docx` | python-docx 库 | ✅ 支持 |
| `.pdf` | pdfplumber + OCR | ✅ 支持 |
| `.jpg/.png` | PaddleOCR/EasyOCR | ✅ 支持 |
| `.doc` | 友好提示 | ⏳ 不支持 |

**代码片段**:
```python
def _extract_resume_text(content: bytes, file_ext: str) -> str:
    """从不同格式的文件中提取文本"""
    
    if file_ext == '.txt':
        # 直接解码
        return content.decode('utf-8', errors='ignore')
    
    elif file_ext == '.docx':
        # 使用 python-docx
        from docx import Document
        doc = Document(BytesIO(content))
        return '\n'.join([para.text for para in doc.paragraphs])
    
    elif file_ext == '.pdf':
        # 先用 pdfplumber，为空则 OCR
        try:
            pdf_text = extract_pdf_text(content)
            if pdf_text:
                return pdf_text
            else:
                logger.info("PDF 文档为空，尝试使用 OCR 识别")
                return _ocr_extract_text(content, file_ext)
        except:
            return _ocr_extract_text(content, file_ext)
    
    elif file_ext in ['.jpg', '.jpeg', '.png']:
        # 直接 OCR
        return _ocr_extract_text(content, file_ext)
```

---

### 3. **OCR 识别函数**
**文件**: `backend/routers/immersive_dialogue.py`  
**函数**: `_ocr_extract_text(content, file_ext)` (第 ~713 行)

**三层降级方案**:

```python
def _ocr_extract_text(content: bytes, file_ext: str) -> str:
    """使用 OCR 从图片或扫描版PDF中提取文本"""
    
    # ======== 方案 1: PaddleOCR (优先) ========
    try:
        from paddleocr_local import create_paddleocr
        ocr = create_paddleocr()
        
        if file_ext == '.pdf':
            # PDF 逐页 OCR
            for page in pdf.pages:
                result = ocr.ocr(page_image, cls=False)
                text += extract_from_result(result)
        
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            # 图片 OCR
            result = ocr.ocr(image, cls=False)
            text = extract_from_result(result)
        
        return text if text else "识别失败"
    
    # ======== 方案 2: EasyOCR (备选) ========
    except Exception as paddle_err:
        logger.warning(f"PaddleOCR 失败: {paddle_err}")
        
        try:
            import easyocr
            reader = easyocr.Reader(['ch'], gpu=False)
            
            if file_ext == '.pdf':
                # PDF 逐页识别
                for page in pdf.pages:
                    result = reader.readtext(page_image, detail=0)
                    text += '\n'.join(result)
            
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # 图片识别
                result = reader.readtext(image, detail=0)
                text = '\n'.join(result)
            
            return text if text else "识别失败"
        
        except ImportError:
            logger.warning("EasyOCR 未安装")
        
        except Exception as easy_err:
            logger.warning(f"EasyOCR 也失败: {easy_err}")
    
    # ======== 方案 3: 回退消息 ========
    logger.warning("所有 OCR 方案都失败")
    return "【⚠️ OCR功能暂不可用】\n请选择其他方式：\n1. 使用纯文本或 Word 文档\n2. 手动填写信息\n3. 运行: python fix_paddleocr_issue.py"
```

---

### 4. **信息结构化提取**
**文件**: `backend/services/resume_parsing_v2.py`  
**函数**: `parse_resume_text(text)` 

**提取的字段**:

```python
{
    "name": str,              # 姓名
    "email": str,            # 邮箱
    "phone": str,            # 电话
    "resume_url": str,       # 文件存储路径
    "education": str,        # 教育背景 (本科/硕士/博士)
    "major": str,            # 专业
    "experience_years": int, # 工作年限
    "skills": list,          # 技能列表 (JSON)
    "work_experience": dict  # 工作经历 (JSON)
}
```

**参考实现**:
```python
def parse_resume_text(text: str) -> dict:
    """从提取的文本中解析结构化信息"""
    
    result = {}
    
    # 1. 基本信息 (使用正则表达式)
    name_match = re.search(r'(?:姓名|Name)[:：]\s*(\S+)', text)
    result['name'] = name_match.group(1) if name_match else ""
    
    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    result['email'] = email_match.group(1) if email_match else ""
    
    phone_match = re.search(r'(?:电话|Phone|Phone)[:：]\s*(\d{11}|\d{10})', text)
    result['phone'] = phone_match.group(1) if phone_match else ""
    
    # 2. 教育背景
    if re.search(r'[硕士|Master]', text):
        result['education'] = '硕士'
    elif re.search(r'[博士|PhD]', text):
        result['education'] = '博士'
    else:
        result['education'] = '本科'
    
    # 3. 专业 (可使用 spaCy NLP)
    majors = ['计算机', '软件', '信息', '电子', ...]
    for major in majors:
        if major in text:
            result['major'] = major
            break
    
    # 4. 技能 (正则 + 关键词匹配)
    skills_section = re.search(r'(?:技能|Skills)[-:\s]*([^\n]+(?:\n[^\n]+)*)', text)
    result['skills'] = parse_skills(skills_section.group(1)) if skills_section else []
    
    # 5. 工作年限
    years_match = re.search(r'(\d+)\s*年.*?(?:工作|工作经验)', text)
    result['experience_years'] = int(years_match.group(1)) if years_match else 0
    
    return result
```

---

## 🔌 关于 SSL 问题和本地模型

### 之前的问题
```
SSL: CERTIFICATE_VERIFY_FAILED - 无法验证证书
```

这是因为：
1. PaddleOCR 默认尝试从网络下载模型
2. 网络请求需要 SSL 证书验证
3. 环境可能没有正确配置 SSL 证书

### 解决方案 ✅
通过环境变量禁用远程下载，使用本地模型：

**文件**: `backend/paddleocr_local.py` (第 10-27 行)

```python
# 必须在导入前设置
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'  # 禁用模型源检查
os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'             # 离线模式
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'                   # 不使用子进程
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(Path.home() / ".paddleocr" / "models")  # 本地模型路径
```

这样 PaddleOCR 就会：
1. ✅ 首先查找本地模型
2. ✅ 不尝试从网络下载
3. ✅ 避免 SSL 证书问题

---

## 🚀 现在重启后端

```powershell
# 在后端目录终端
# 1. 如果后端还在运行，按 Ctrl+C 停止

# 2. 重新启动
python main.py

# 3. 如果看到这样的日志，表示成功:
# ✅ Application startup complete
# ✅ PaddleOCR 初始化成功 (或)
# ✅ EasyOCR 模型已加载
```

---

## 🧪 测试简历上传

### 使用 curl 测试

```bash
# 准备一个 PDF 或 Word 文件

# 上传文件
curl -X POST http://localhost:8000/api/candidates/upload_resume \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_resume.pdf"

# 应该看到 JSON 响应
# {
#   "code": 200,
#   "message": "成功",
#   "data": {
#     "name": "...",
#     "email": "...",
#     ...
#   }
# }
```

### 使用浏览器测试

1. 访问 http://localhost:5173
2. 开始评估 → 基本信息步骤
3. 点击简历上传区域
4. 选择一个 PDF 或 Word 文件
5. 等待识别完成
6. 查看自动填充的表单字段

---

## 📊 完整的文件处理流程示意

```
简历文件 (用户上传)
  │
  ├─ .pdf ────→ pdfplumber 提取
  │             │
  │             ├─ 有文本 → 返回
  │             └─ 空白 → PaddleOCR/EasyOCR
  │
  ├─ .docx ───→ python-docx 提取
  │
  ├─ .txt ────→ UTF-8 解码
  │
  └─ .jpg/.png →  PaddleOCR/EasyOCR 直接识别

结构化信息提取
  │
  └─ 正则表达式 + NLP + 关键词匹配
     │
     ├─ 基本信息 (名字、邮箱、电话)
     ├─ 教育背景 (学位、专业)
     ├─ 工作经历 (公司、职位、年限)
     └─ 技能列表

存储和返回
  │
  ├─ 保存到 User 表相关字段
  ├─ 保存文件到 resume_url
  └─ 返回给前端
```

---

## ✅ 完成清单

- [x] 语法错误修复 (AttributeError 块重复问题)
- [x] 简历解析工作流完整说明
- [x] 三层 OCR 降级方案说明
- [x] SSL 问题和本地模型配置说明
- [x] 文件格式支持详情
- [x] API 端点和参数说明
- [x] 测试方法说明

---

## 🎯 下一步

修复完成后：
1. ✅ 重启后端: `python main.py`
2. ✅ 测试简历上传功能
3. ✅ 继续完成其他开发任务

参考: `DEVELOPMENT_PROGRESS_REPORT.md`

---

*最后更新: 2026-03-28 16:45*  
*简历解析完整工作流版本: 1.0*
