# 📋 简历解析模块 - 问题诊断与测试指南

## 快速诊断表

### 症状排查矩阵

| 症状 | 可能原因 | 优先级 | 检查步骤 |
|------|--------|--------|---------|
| 上传后无反应 | 1. 后端未启动 2. 网络问题 3. 大文件 | 🔴 高 | [检查1](#检查1后端服务) |
| 返回"不支持的格式" | 1. 文件扩展名不对 2. 上传前缀被截断 | 🟡 中 | [检查2](#检查2文件格式) |
| "文件大小超过限制" | 文件 > 10MB | 🟢 低 | 分割文件或压缩 |
| 返回【】开头的消息 | 1. 文本提取失败 2. 依赖库缺失 | 🔴 高 | [检查3](#检查3依赖库) |
| OCR 完全不工作 | 1. PaddleOCR 版本不兼容 2. 模型加载失败 | 🔴 高 | [检查4](#检查4ocr-状态) |
| PDF 识别结果为空 | 1. PDF 确实无文本 2. OCR 不可用 3. 页面全白 | 🟡 中 | [检查5](#检查5pdf-处理) |
| 邮箱/电话提取错误 | 1. 格式非标准 2. 正则表达式局限 | 🟢 低 | [检查6](#检查6信息解析) |
| 评估维度缺失 | 技能识别不完美 | 🟢 低 | [检查7](#检查7软技能识别) |

---

## 详细检查步骤

### 检查1：后端服务

#### 1.1 验证后端是否运行

```bash
# 检查进程
ps aux | grep "python main.py"

# 或检查端口
netstat -an | grep 8000
lsof -i :8000
```

#### 1.2 查看后端日志

```bash
# 实时查看日志
tail -f backend.log

# 查看最后100行
tail -n 100 backend.log

# 过滤简历相关日志
grep -i "resume\|上传\|简历" backend.log | tail -20
```

#### 1.3 测试 API 连接

```bash
# 简单的 ping 测试
curl http://localhost:8000/docs

# 返回 Swagger UI 表示后端正常

# 或测试任何通用端点
curl http://localhost:8000/
```

---

### 检查2：文件格式

#### 2.1 验证文件扩展名

```bash
# 检查上传的文件
ls -la /path/to/uploaded/file

# 确认扩展名
file /path/to/uploaded/file

# 常见正确格式
✅ resume.pdf
✅ resume.docx
✅ resume.txt
✅ resume.jpg
❌ resume.PDF  (应该是小写)
❌ resume      (无扩展名)
```

#### 2.2 测试支持的格式

```python
# 在后端虚拟环境中测试
python -c "
from routers.immersive_dialogue import _extract_resume_text

# 测试 TXT
with open('test.txt', 'rb') as f:
    result = _extract_resume_text(f.read(), '.txt')
    print('✅ TXT:', len(result), 'chars')

# 测试 DOCX
with open('test.docx', 'rb') as f:
    result = _extract_resume_text(f.read(), '.docx')
    print('✅ DOCX:', len(result), 'chars')

# 测试 PDF
with open('test.pdf', 'rb') as f:
    result = _extract_resume_text(f.read(), '.pdf')
    print('✅ PDF:', len(result), 'chars')
"
```

---

### 检查3：依赖库

#### 3.1 检查必需库

```bash
# 在虚拟环境中
. venv/Scripts/activate

# 检查各库版本
pip show python-docx pdfplumber pillow paddleocr

# 完整依赖检查
pip list | grep -E "docx|pdf|paddle|easyocr"
```

#### 3.2 依赖库安装

```bash
# 必需库
pip install python-docx
pip install pdfplumber
pip install pillow

# PaddleOCR (通常已安装)
pip install paddleocr

# 可选但推荐
pip install easyocr
```

#### 3.3 测试导入

```python
python -c "
import sys
sys.path.insert(0, 'backend')

try:
    from docx import Document
    print('✅ python-docx OK')
except ImportError as e:
    print('❌ python-docx:', e)

try:
    import pdfplumber
    print('✅ pdfplumber OK')
except ImportError as e:
    print('❌ pdfplumber:', e)

try:
    from PIL import Image
    print('✅ pillow OK')
except ImportError as e:
    print('❌ pillow:', e)

try:
    import paddleocr
    print('✅ paddleocr OK')
except ImportError as e:
    print('❌ paddleocr:', e)

try:
    import easyocr
    print('✅ easyocr OK')
except ImportError as e:
    print('⚠️  easyocr (可选):', e)
"
```

---

### 检查4：OCR 状态

#### 4.1 测试 PaddleOCR 初始化

```bash
cd backend
python test_paddleocr.bat  # Windows
# 或
./test_paddleocr.sh        # Linux
```

预期输出：
```
✅✅✅ PaddleOCR 初始化成功！
```

#### 4.2 诊断 PaddleOCR 问题

```python
python -c "
import sys
sys.path.insert(0, 'backend')

from paddleocr_local import create_paddleocr

try:
    print('尝试初始化 PaddleOCR...')
    ocr = create_paddleocr()
    print('✅ PaddleOCR 初始化成功')
    
    # 测试简单识别
    from PIL import Image
    import numpy as np
    
    # 创建测试图片
    test_img = Image.fromarray(np.ones((100, 100, 3), dtype=np.uint8) * 255)
    result = ocr.ocr(test_img, cls=False)
    print(f'✅ OCR 可运行，接口正常')
    
except AttributeError as e:
    if 'set_optimization_level' in str(e):
        print('❌ set_optimization_level 问题（应该已修复）')
        print('   解决：重新启动后端')
    else:
        print(f'❌ AttributeError: {e}')
        
except ImportError as e:
    print(f'❌ ImportError: {e}')
    print('   解决：pip install paddleocr')
    
except Exception as e:
    print(f'❌ {type(e).__name__}: {e}')
    print('   检查环境变量和模型文件')
"
```

#### 4.3 切换到 EasyOCR

```bash
# 安装 EasyOCR
pip install easyocr

# 如果 PaddleOCR 不可用，系统会自动使用 EasyOCR
# 重启后端即可生效
python main.py
```

---

### 检查5：PDF 处理

#### 5.1 检查 PDF 类型

```python
import pdfplumber
from io import BytesIO

with open('resume.pdf', 'rb') as f:
    content = f.read()

with pdfplumber.open(BytesIO(content)) as pdf:
    print(f"PDF 有 {len(pdf.pages)} 页")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"第 {i+1} 页: {len(text) if text else 0} 字")
        
        if not text:
            print(f"  第 {i+1} 页无可提取文本，需要 OCR")
```

#### 5.2 测试 PDF 的 OCR 转换

```python
from paddleocr_local import create_paddleocr
import pdfplumber
from io import BytesIO

ocr = create_paddleocr()

with open('resume.pdf', 'rb') as f:
    content = f.read()

with pdfplumber.open(BytesIO(content)) as pdf:
    for i, page in enumerate(pdf.pages):
        # 转换为图片
        im = page.to_image(resolution=300)  # 300 DPI
        pil_image = im.original
        
        # OCR 识别
        result = ocr.ocr(pil_image, cls=False)
        text = "\n".join([line[1][0] for line in result[0]])
        
        print(f"第 {i+1} 页 OCR 结果: {len(text)} 字")
        if text:
            print(f"  样本: {text[:100]}")
```

---

### 检查6：信息解析

#### 6.1 测试信息提取

```python
from routers.immersive_dialogue import _parse_resume_info

sample_text = """
姓名：Alice Chen
邮箱：alice@example.com
电话：13800138000
教育背景：本科
工作经验：
- 5年 Python 开发
- 3年 JavaScript 前端
技能：Vue.js, React, Django
"""

result = _parse_resume_info(sample_text)

print("提取结果：")
for key, value in result.items():
    print(f"  {key}: {value}")
```

#### 6.2 调整正则表达式

如果提取效果不好，编辑：[routers/immersive_dialogue.py](../backend/routers/immersive_dialogue.py#L980)

```python
# 例如，改进电话号码识别
phone_pattern = r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}|tel[:：]\s*(\d+[-\d]*)'

# 例如，改进邮箱识别
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|email[:：]\s*([^\s]+)'
```

---

### 检查7：软技能识别

#### 7.1 查看软技能库

```python
# backend/services/resume_parsing_v2.py 第 100-120 行
SOFT_SKILLS_LIBRARY = {
    "沟通能力": ["沟通", "表达", "演讲", "汇报"],
    "团队合作": ["团队", "合作", "协作"],
    "解决问题": ["解决", "调试", "修复", "优化"],
    ...
}

# 如需扩展，在此处添加新的软技能或关键词
```

#### 7.2 测试软技能识别

```python
text_examples = [
    "带领团队完成项目",  # → "团队合作"
    "解决了复杂的并发问题",  # → "解决问题"
    "在公众面前做过多次技术演讲",  # → "沟通能力"
]

for text in text_examples:
    result = _parse_resume_info(text)
    soft_skills = result.get('soft_skills', [])
    print(f"{text}\n  识别: {soft_skills}\n")
```

---

## 完整测试流程

### 场景 1：本地测试（无需前端）

```bash
# 1. 准备测试文件
cp ~/Documents/my_resume.pdf ./test_resume.pdf

# 2. 在后端启动测试脚本
cd backend
python -c "
import sys
sys.path.insert(0, '.')

from routers.immersive_dialogue import upload_resume, _extract_resume_text, _parse_resume_info
from io import BytesIO

# 读取文件
with open('../test_resume.pdf', 'rb') as f:
    content = f.read()

# 1️⃣ 提取文本
text = _extract_resume_text(content, '.pdf')
print('✅ 文本提取:', len(text), '字')

# 2️⃣ 解析信息
info = _parse_resume_info(text)
print('✅ 信息解析:')
print(f'   姓名: {info[\"name\"]}')
print(f'   邮箱: {info[\"email\"]}')
print(f'   电话: {info[\"phone\"]}')
print(f'   学历: {info[\"education\"]}')
print(f'   技能: {info[\"technical_skills\"]}')
"
```

### 场景 2：API 测试（使用 curl）

```bash
# 1. 启动后端
cd backend && python main.py

# 2. 在另一个终端（Windows PowerShell）
$file = Get-Item "./test_resume.pdf"
$filePath = $file.FullName
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)

$form = @{
    file = $fileBytes
    candidate_id = "test_candidate_123"
}

$response = Invoke-WebRequest `
    -Uri "http://localhost:8000/assessment/immersive/upload-resume?candidate_id=test_123" `
    -Method POST `
    -Form $form

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 4 | Write-Host
```

### 场景 3：完整端到端测试（前端 + 后端）

1. 启动后端: `python main.py`
2. 启动前端: `npm run dev`
3. 打开浏览器: `http://localhost:3000/assessment/upload-resume`
4. 上传测试简历
5. 检查表单是否自动填充
6. 打开浏览器开发者工具 (F12)
7. 查看 Network 标签中的请求/响应

---

## 调试技巧

### 启用详细日志

编辑 `backend/routers/immersive_dialogue.py`:

```python
import logging

# 在文件开头设置日志级别
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
```

### 使用 pdb 调试

```python
# 在 _parse_resume_info 函数中添加断点
def _parse_resume_info(text: str) -> Dict[str, Any]:
    import pdb; pdb.set_trace()  # 调试断点
    
    # 然后运行后端，访问 API 会在此暂停
    # 使用 pdb 命令：print(text[:100]), n(下一步), c(继续)
```

### 生成测试简历

```python
# backend/generate_test_resume.py
test_resume = """
姓名：张三
邮箱：zhangsan@example.com
电话：13900001111

教育背景：
本科，计算机科学与技术

工作经验：
5年软件开发经验
- Python / JavaScript 全栈工程师
- 云原生应用开发
- 团队负责人

技能：
- 后端：Python, FastAPI, Django
- 前端：Vue.js, React
- 数据库：MySQL, MongoDB
- 工具：Docker, Kubernetes

软技能：
- 沟通表达能力强
- 团队协作经验丰富
- 带领过5人以上的技术团队
"""

with open('test_resume.txt', 'w') as f:
    f.write(test_resume)
```

---

## 常见错误及解决方案

### ❌ "ModuleNotFoundError: No module named 'docx'"
```bash
# 解决
pip install python-docx
```

### ❌ "AttributeError: module 'pdfplumber' has no attribute 'open'"
```bash
# 可能是导入错误，检查：
python -c "import pdfplumber; print(pdfplumber.__file__)"

# 重新安装
pip install --upgrade pdfplumber
```

### ❌ "PaddleOCR not found 或 'paddleocr' has no attribute 'PaddleOCR'"
```bash
# 检查是否导入正确
from paddleocr import PaddleOCR  # ✅ 正确
from paddleocr_local import create_paddleocr  # ✅ 也正确

# 重装
pip install --upgrade paddleocr
```

### ❌ "OCR 结果为空"
```python
# 可能原因：
1. 图片过小或太模糊
2. OCR 模型未完全加载
3. 内存不足

# 解决：
1. 确保图片 DPI ≥ 200
2. 增加等待时间
3. 检查可用内存
```

### ❌ "文件编码错误"  
```python
# TXT 文件编码问题
# 当前代码已处理，但仍有问题则检查：
content.decode('utf-8', errors='ignore')  # 已自动忽略错误

# 如需保留错误信息：
content.decode('utf-8', errors='replace')
```

---

## 性能优化建议

### 瓶颈分析

| 操作 | 耗时 | 优化方向 |
|------|------|---------|
| PaddleOCR 初始化 | 2-5秒 | ✅ 已使用缓存（首次后快速） |
| PDF 多页 OCR | 5-15秒 | ⏳ 可并行处理 |
| 正则表达式匹配 | 50-100ms | ✅ 已编译 |
| 文件 I/O | 100-500ms | ⏳ 可异步处理 |

### 快速优化

1. **使用连接池**
```python
# 已支持，无需改动
```

2. **启用异步处理**
```python
# 计划：将 upload_resume 改为 async
async def upload_resume(...):
    extracted_text = await asyncio.to_thread(_extract_resume_text, content, file_ext)
```

3. **缓存技能库**
```python
@lru_cache(maxsize=128)
def get_tech_skills_set():
    return set(TECH_SKILLS_LIBRARY)
```

---

## 下一步行动

- [ ] 验证所有检查通过
- [ ] 运行完整测试流程
- [ ] 记录问题和解决方案
- [ ] 优化性能（如需）
- [ ] 部署到生产环境

---

**文档版本**: 1.0  
**最后更新**: 2026-03-28  
**需要帮助**: 查看 [RESUME_PARSING_COMPLETE_ANALYSIS.md](RESUME_PARSING_COMPLETE_ANALYSIS.md)
