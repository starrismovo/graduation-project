# 简历解析流程优化方案

## 📋 问题分析

### 1️⃣ **candidate_id 参数问题**（🔴 严重）

#### 当前状态
- 前端传递：`URLSearchParams` 中 `candidate_id` 为字符串
- 后端接收：`candidate_id: str = Query(...)` 
- 数据库查询：某些地方期望整数类型
  ```python
  # 在 /candidate/{candidate_id}/sessions 中
  AssessmentRecord.candidate_id == int(candidate_id)  # ❌ 类型转换但没有验证
  ```

#### 风险
- 无效的数字字符串会导致 `ValueError`
- 类型不一致导致数据库查询失败
- 不清楚是否应该支持 UUID、纯数字或其他格式

#### 解决方案
✅ **统一 candidate_id 格式和验证**
```python
from pydantic import validator

class CandidateIDValidator:
    """候选人ID验证器"""
    
    @staticmethod
    def validate(candidate_id: str) -> str:
        """验证并规范化 candidate_id"""
        if not candidate_id or not candidate_id.strip():
            raise ValueError("候选人ID不能为空")
        
        normalized = candidate_id.strip()
        
        # 支持两种格式：
        # 1. 纯数字: "123" -> 存储为字符串 "123"
        # 2. UUID或文本: "cand_abc123" -> 原样保留
        
        return normalized
```

---

### 2️⃣ **代码重复和结构问题**（🟡 中等）

#### 当前问题
- `_extract_resume_text` 中的错误处理重复代码多
- 每个文件格式都有类似的 try-except 结构
- PDF 处理逻辑复杂且嵌套层级深

#### 优化方案
```python
# ✅ 提取器工厂模式
class ResumeTextExtractor:
    """简历文本提取器（工厂模式）"""
    
    extractors = {}
    
    @classmethod
    def register(cls, ext: str):
        """注册提取器"""
        def decorator(func):
            cls.extractors[ext] = func
            return func
        return decorator
    
    @classmethod
    async def extract(cls, content: bytes, file_ext: str) -> str:
        """提取文本"""
        if file_ext not in cls.extractors:
            raise ValueError(f"不支持的格式: {file_ext}")
        
        return await cls.extractors[file_ext](content)

# 使用示例
@ResumeTextExtractor.register('.txt')
async def extract_txt(content: bytes) -> str:
    return content.decode('utf-8', errors='ignore')

@ResumeTextExtractor.register('.pdf')
async def extract_pdf(content: bytes) -> str:
    # 具体实现
    pass
```

---

### 3️⃣ **OCR 模型重复初始化**（🟡 中等）

#### 当前问题
```python
# ❌ 每次都重新初始化模型（耗时 2-5 秒）
for page in pdf.pages:
    ocr = create_paddleocr()  # 多次初始化！
    result = ocr.ocr(pil_image)
```

#### 优化方案
```python
# ✅ 单例模式缓存 OCR 实例
class OCRModelCache:
    """OCR 模型单例缓存"""
    _instance = None
    _model = None
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_model(cls):
        """获取或创建 OCR 实例"""
        if cls._model is None:
            async with cls._lock:
                if cls._model is None:
                    logger.info("初始化 OCR 模型...")
                    cls._model = create_paddleocr()
        return cls._model
    
    @classmethod
    def clear(cls):
        """清理缓存"""
        cls._model = None

# 使用
ocr = await OCRModelCache.get_model()
result = ocr.ocr(image)
```

---

### 4️⃣ **参数验证不完备**（🟡 中等）

#### 当前问题
- 文件大小验证在多个地方重复
- 文件类型验证没有完整的白名单
- 候选人信息字段没有验证

#### 优化方案
```python
# ✅ 使用 Pydantic 统一验证
from pydantic import BaseModel, validator

class ResumeUploadRequest(BaseModel):
    """简历上传请求模型"""
    candidate_id: str
    
    @validator('candidate_id')
    def validate_candidate_id(cls, v):
        if not v or len(v) > 100:
            raise ValueError("候选人ID长度不合法")
        return v.strip()

class ResumeParseRequest(BaseModel):
    """简历解析请求模型"""
    candidate_id: str
    candidate_name: str
    candidate_email: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    projects: Optional[str] = None
    
    @validator('candidate_name')
    def validate_name(cls, v):
        if not v or len(v) > 50:
            raise ValueError("姓名长度不合法")
        return v.strip()
    
    @validator('candidate_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError("邮箱格式不正确")
        return v
```

---

### 5️⃣ **错误处理缺陷**（🟡 中等）

#### 当前问题
- 某些异常被忽略或没有正确传播
- 日志级别不一致（info/warning/error混乱）
- 用户无法了解详细的错误原因

#### 优化方案
```python
# ✅ 自定义异常体系
class ResumeProcessingException(Exception):
    """简历处理异常基类"""
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

class FileTooLargeException(ResumeProcessingException):
    def __init__(self, size: int, limit: int):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"文件大小 {size}MB 超过限制 {limit}MB",
            details={"size": size, "limit": limit}
        )

# 异常处理中间件
@app.exception_handler(ResumeProcessingException)
async def handle_resume_exception(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )
```

---

### 6️⃣ **性能问题**（🟡 中等）

#### 当前问题
- 大文件处理同步阻塞
- 信息解析使用正则表达式效率低
- 多页 PDF 逐页处理，没有并发

#### 优化方案
```python
# ✅ 异步处理与线程池
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncResumeProcessor:
    """异步简历处理器"""
    
    executor = ThreadPoolExecutor(max_workers=4)
    
    @staticmethod
    async def process_file(file_content: bytes, file_ext: str) -> str:
        """异步处理大文件"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            AsyncResumeProcessor.executor,
            _extract_resume_text,
            file_content,
            file_ext
        )
    
    @staticmethod
    async def process_multi_page_pdf(pdf_content: bytes) -> str:
        """并发处理多页 PDF"""
        loop = asyncio.get_event_loop()
        # 使用 asyncio.gather 并发处理页面
        tasks = [
            loop.run_in_executor(
                AsyncResumeProcessor.executor,
                _process_pdf_page,
                page_data
            )
            for page_data in pages
        ]
        results = await asyncio.gather(*tasks)
        return ''.join(results)
```

---

### 7️⃣ **信息解析精度**（🟡 中等）

#### 当前问题
- 正则表达式不够完善
- 软技能提取基于关键字匹配，准确度低
- 学历字段只有固定几个选项

#### 优化方案
```python
# ✅ 改进的信息解析

class ResumeInfoParser:
    """改进的简历信息解析器"""
    
    # 更完善的教育背景映射
    EDUCATION_PATTERNS = {
        r'(?:phd|博士|ph\.d)': '博士',
        r'(?:master|masters?|硕士|mba)': '硕士',
        r'(?:bachelor|本科|undergraduate)': '本科',
        r'(?:associate|大专|junior)': '大专',
        r'(?:high school|高中|中专)': '高中',
    }
    
    # 技能库（更完善）
    TECH_SKILLS = {
        'web': ['JavaScript', 'TypeScript', 'HTML', 'CSS', 'Vue', 'React', 'Angular'],
        'backend': ['Python', 'Java', 'Go', 'C#', 'Node.js', 'Django', 'Spring'],
        'data': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Spark'],
        'devops': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Jenkins'],
    }
    
    @classmethod
    def extract_education(cls, text: str) -> str:
        """智能提取教育背景"""
        text_lower = text.lower()
        for pattern, education in cls.EDUCATION_PATTERNS.items():
            if re.search(pattern, text_lower):
                return education
        return '未填写'
    
    @classmethod
    def extract_skills(cls, text: str) -> List[str]:
        """智能提取技能"""
        skills = []
        for skill in cls.TECH_SKILLS['web'] + cls.TECH_SKILLS['backend'] + \
                     cls.TECH_SKILLS['data'] + cls.TECH_SKILLS['devops']:
            if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
                skills.append(skill)
        return list(set(skills))
```

---

## 🛠️ 实现步骤

### Phase 1: 参数验证层（优先级：🔴 高）
- [ ] 添加 Pydantic 验证模型
- [ ] 统一 candidate_id 处理逻辑
- [ ] 更新现有接口

### Phase 2: 代码重构（优先级：🟡 中）
- [ ] 提取器工厂模式重构
- [ ] 异常体系设计
- [ ] 错误处理中间件

### Phase 3: 性能优化（优先级：🟡 中）
- [ ] OCR 模型单例缓存
- [ ] 异步处理集成
- [ ] 并发处理 PDF

### Phase 4: 精度提升（优先级：🟢 低）
- [ ] 信息解析器改进
- [ ] 技能库扩展
- [ ] 测试用例补充

---

## ⏱️ 预期影响

| 优化项 | 改进 | 工程量 | 优先级 |
|-------|------|------|-------|
| candidate_id 验证 | 消除类型错误 | 1h | 🔴 高 |
| 工厂模式重构 | 代码减少 40% | 3h | 🟡 中 |
| OCR 缓存 | 多次识别快 5 倍 | 2h | 🟡 中 |
| 异步处理 | 大文件响应快 50% | 3h | 🟡 中 |
| 信息精度 | 准确度提升 15% | 2h | 🟢 低 |

**总工作量**: ~11 小时

---

## 📝 下一步建议

1. **立即修复**：candidate_id 参数验证（防止数据错误）
2. **短期优化**：工厂模式重构 + 异常处理
3. **中期优化**：OCR 缓存 + 异步处理
4. **长期改进**：信息解析精度提升

