"""
简历解析模块 - 优化版本
改进点：
1. 参数验证（Pydantic模型）
2. 统一 candidate_id 处理
3. 自定义异常体系
4. 工厂模式提取器
5. 性能优化
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

logger = logging.getLogger(__name__)


# ==================== Pydantic 验证模型 ====================

class CandidateIDValidator:
    """候选人ID验证器"""
    
    MAX_LENGTH = 100
    
    @staticmethod
    def validate(candidate_id: str) -> str:
        """验证并规范化 candidate_id
        
        支持格式：
        - 纯数字：123
        - UUID：cand_abc123, user_12345
        - 任何非空字符串（最多100字符）
        """
        if not candidate_id:
            raise ValueError("候选人ID不能为空")
        
        normalized = candidate_id.strip()
        
        if len(normalized) > CandidateIDValidator.MAX_LENGTH:
            raise ValueError(f"候选人ID长度不能超过 {CandidateIDValidator.MAX_LENGTH}")
        
        if not normalized:
            raise ValueError("候选人ID不能为空格")
        
        return normalized


class ResumeParseRequest(BaseModel):
    """简历解析请求模型"""
    candidate_id: str = Field(..., description="候选人ID", min_length=1, max_length=100)
    candidate_name: str = Field(..., description="候选人姓名", min_length=1, max_length=50)
    candidate_email: Optional[str] = Field(None, description="候选人邮箱", max_length=100)
    education: Optional[str] = Field(None, description="教育背景", max_length=20)
    skills: Optional[str] = Field(None, description="技能标签（逗号分隔）", max_length=500)
    projects: Optional[str] = Field(None, description="项目经验", max_length=2000)
    
    @validator('candidate_id')
    def validate_candidate_id(cls, v):
        return CandidateIDValidator.validate(v)
    
    @validator('candidate_name')
    def validate_name(cls, v):
        """验证姓名"""
        if not v or len(v.strip()) == 0:
            raise ValueError("姓名不能为空")
        return v.strip()
    
    @validator('candidate_email')
    def validate_email(cls, v):
        """验证邮箱格式"""
        if v:
            if '@' not in v or len(v) > 100:
                raise ValueError("邮箱格式不正确")
        return v
    
    @validator('education')
    def validate_education(cls, v):
        """验证教育背景"""
        if v:
            valid_options = ['高中', '大专', '本科', '硕士', '博士']
            if v not in valid_options:
                raise ValueError(f"教育背景必须是以下之一: {valid_options}")
        return v


class ResumeUploadRequest(BaseModel):
    """简历上传请求模型"""
    candidate_id: str = Field(..., description="候选人ID")
    
    @validator('candidate_id')
    def validate_candidate_id(cls, v):
        return CandidateIDValidator.validate(v)


# ==================== 自定义异常体系 ====================

class ResumeProcessingException(Exception):
    """简历处理异常基类"""
    
    def __init__(self, code: str, message: str, details: Optional[Dict] = None, status_code: int = 400):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_response(self) -> Dict[str, Any]:
        """转换为 API 响应"""
        return {
            "code": self.status_code,
            "error_code": self.code,
            "message": self.message,
            "details": self.details
        }


class InvalidFileFormatException(ResumeProcessingException):
    """无效的文件格式异常"""
    
    def __init__(self, file_ext: str, allowed: List[str]):
        super().__init__(
            code="INVALID_FILE_FORMAT",
            message=f"不支持的文件格式: {file_ext}",
            details={"provided": file_ext, "allowed": allowed},
            status_code=400
        )


class FileTooLargeException(ResumeProcessingException):
    """文件过大异常"""
    
    def __init__(self, size_bytes: int, limit_bytes: int = 10 * 1024 * 1024):
        size_mb = size_bytes / 1024 / 1024
        limit_mb = limit_bytes / 1024 / 1024
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"文件大小 {size_mb:.1f}MB 超过限制 {limit_mb:.1f}MB",
            details={"size": size_bytes, "limit": limit_bytes},
            status_code=413
        )


class TextExtractionException(ResumeProcessingException):
    """文本提取异常"""
    
    def __init__(self, file_ext: str, original_error: Exception):
        super().__init__(
            code="TEXT_EXTRACTION_FAILED",
            message=f"提取 {file_ext} 文件内容失败",
            details={"file_type": file_ext, "error": str(original_error)},
            status_code=422
        )


class OCRProcessingException(ResumeProcessingException):
    """OCR 处理异常"""
    
    def __init__(self, original_error: Exception):
        super().__init__(
            code="OCR_PROCESSING_FAILED",
            message="OCR 识别失败或模型不可用",
            details={"error": str(original_error)},
            status_code=503
        )


class InfoParsingException(ResumeProcessingException):
    """信息解析异常"""
    
    def __init__(self, original_error: Exception):
        super().__init__(
            code="INFO_PARSING_FAILED",
            message="解析简历信息失败",
            details={"error": str(original_error)},
            status_code=422
        )


# ==================== 常量定义 ====================

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 8192  # 文件读取块大小

EDUCATION_MAPPING = {
    "高中": "初级",
    "大专": "初级",
    "本科": "中级",
    "硕士": "高级",
    "博士": "专家级"
}

TECH_SKILLS_LIBRARY = [
    # Web 前端
    "JavaScript", "TypeScript", "HTML", "CSS", "Vue", "Vue.js", "React", 
    "Angular", "jQuery", "Webpack", "Node.js", "NPM",
    
    # 后端
    "Python", "Java", "Go", "Rust", "C++", "C#", "PHP", "Ruby", "Rails",
    "Django", "Flask", "FastAPI", "Spring", "Spring Boot",
    
    # 数据库
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQL",
    
    # 开发工具与平台
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins",
    "Git", "Linux", "REST API", "GraphQL", "Kafka", "RabbitMQ"
]

SOFT_SKILLS_LIBRARY = {
    "沟通能力": ["沟通", "表达", "演讲", "汇报", "协调", "报告"],
    "团队合作": ["团队", "合作", "协作", "配合", "集体"],
    "创新思维": ["创新", "创意", "想法", "方案", "设计"],
    "解决问题": ["解决", "调试", "修复", "优化", "改进"],
    "领导力": ["领导", "负责", "主导", "带领", "管理"],
    "学习能力": ["学习", "探索", "研究", "掌握", "快速"],
}


# ==================== 性能优化：OCR 模型缓存 ====================

class OCRModelCache:
    """OCR 模型单例缓存"""
    
    _instance = None
    _model = None
    _lock = asyncio.Lock()
    _initialized = False
    
    @classmethod
    async def get_model(cls):
        """获取或创建 OCR 实例
        
        使用单例模式避免重复初始化。
        采用双检查锁定确保线程安全。
        """
        if cls._model is not None:
            return cls._model
        
        async with cls._lock:
            if cls._model is None:
                try:
                    logger.info("初始化 OCR 模型（首次调用，可能耗时2-5秒）...")
                    from paddleocr_local import create_paddleocr
                    cls._model = create_paddleocr()
                    logger.info("OCR 模型初始化完成")
                    cls._initialized = True
                except Exception as e:
                    logger.error(f"OCR 模型初始化失败: {e}")
                    raise OCRProcessingException(e)
        
        return cls._model
    
    @classmethod
    def is_available(cls) -> bool:
        """检查 OCR 是否可用"""
        return cls._initialized or cls._model is not None
    
    @classmethod
    def clear(cls):
        """清理缓存"""
        cls._model = None
        cls._initialized = False


# ==================== 工厂模式：提取器 ====================

class ResumeTextExtractor:
    """简历文本提取器（工厂模式）"""
    
    _extractors = {}
    _executor = ThreadPoolExecutor(max_workers=2)
    
    @classmethod
    def register(cls, ext: str):
        """注册提取器装饰器"""
        def decorator(func):
            cls._extractors[ext] = func
            logger.info(f"注册提取器: {ext}")
            return func
        return decorator
    
    @classmethod
    async def extract(cls, content: bytes, file_ext: str) -> str:
        """提取文本
        
        Args:
            content: 文件内容字节
            file_ext: 文件扩展名（如 '.pdf'）
        
        Returns:
            提取的文本内容
        
        Raises:
            InvalidFileFormatException: 不支持的文件格式
            TextExtractionException: 提取失败
        """
        if file_ext not in cls._extractors:
            raise InvalidFileFormatException(file_ext, list(cls._extractors.keys()))
        
        try:
            logger.info(f"开始提取 {file_ext} 文件...")
            
            # 使用线程池执行同步操作，避免阻塞
            loop = asyncio.get_event_loop()
            extractor_func = cls._extractors[file_ext]
            text = await loop.run_in_executor(
                cls._executor,
                extractor_func,
                content
            )
            
            if text:
                logger.info(f"{file_ext} 提取成功，长度: {len(text)}")
            else:
                logger.warning(f"{file_ext} 提取为空")
            
            return text
        
        except Exception as e:
            if isinstance(e, (InvalidFileFormatException, TextExtractionException)):
                raise
            logger.error(f"提取 {file_ext} 失败: {e}", exc_info=True)
            raise TextExtractionException(file_ext, e)


# ==================== 具体提取器实现 ====================

@ResumeTextExtractor.register('.txt')
def extract_txt(content: bytes) -> str:
    """提取 TXT 文件"""
    logger.debug("提取 TXT 文件...")
    return content.decode('utf-8', errors='ignore')


@ResumeTextExtractor.register('.docx')
def extract_docx(content: bytes) -> str:
    """提取 DOCX 文件"""
    logger.debug("提取 DOCX 文件...")
    try:
        from docx import Document
        from io import BytesIO
        
        doc = Document(BytesIO(content))
        text = '\n'.join([para.text for para in doc.paragraphs])
        
        if not text:
            logger.warning("DOCX 文档为空")
            raise TextExtractionException('.docx', Exception("文档为空"))
        
        return text
    
    except ImportError:
        logger.error("python-docx 库未安装")
        raise TextExtractionException('.docx', Exception("缺少依赖: python-docx"))


@ResumeTextExtractor.register('.pdf')
def extract_pdf(content: bytes) -> str:
    """提取 PDF 文件（支持自动回退到 OCR）"""
    logger.debug("提取 PDF 文件...")
    try:
        import pdfplumber
        from io import BytesIO
        
        with pdfplumber.open(BytesIO(content)) as pdf:
            text_parts = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ''
                if page_text:
                    text_parts.append(page_text)
                logger.debug(f"PDF 页面 {page_num} 提取: {len(page_text)} 字符")
            
            text = '\n'.join(text_parts)
            if text.strip():
                return text
            else:
                logger.warning("PDF 文本提取为空，应触发 OCR")
                # 返回特殊标记，表示需要 OCR 处理
                return "【REQUIRE_OCR】"
    
    except ImportError:
        logger.error("pdfplumber 库未安装")
        raise TextExtractionException('.pdf', Exception("缺少依赖: pdfplumber"))


@ResumeTextExtractor.register('.jpg')
@ResumeTextExtractor.register('.jpeg')
@ResumeTextExtractor.register('.png')
def extract_image(content: bytes) -> str:
    """提取图片文件（需要 OCR）"""
    logger.debug("检测到图片文件，标记为需要 OCR...")
    return "【REQUIRE_OCR】"


@ResumeTextExtractor.register('.doc')
def extract_doc(content: bytes) -> str:
    """提取旧版 Word 文件"""
    logger.warning("检测到旧版 Word97-2003 格式")
    raise TextExtractionException('.doc', Exception("旧版Word格式不支持，请转换为.docx"))


# ==================== 信息解析器 ====================

class ResumeInfoParser:
    """改进的简历信息解析器"""
    
    @staticmethod
    def extract_education(text: str) -> str:
        """智能提取教育背景"""
        import re
        
        text_lower = text.lower()
        
        patterns = {
            r'(?:phd|博士|ph\.?d)': '博士',
            r'(?:master|硕士|mba|m\.?a)': '硕士',
            r'(?:bachelor|本科|undergraduate|degree)': '本科',
            r'(?:associate|大专|diploma)': '大专',
            r'(?:high school|高中|中专|secondary)': '高中',
        }
        
        for pattern, education in patterns.items():
            if re.search(pattern, text_lower):
                logger.debug(f"识别到教育背景: {education}")
                return education
        
        logger.debug("未识别教育背景")
        return '未填写'
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """智能提取技能"""
        import re
        
        skills = set()
        
        for skill in TECH_SKILLS_LIBRARY:
            # 使用单词边界匹配，避免误匹配
            pattern = rf'\b{re.escape(skill)}\b'
            if re.search(pattern, text, re.IGNORECASE):
                skills.add(skill)
        
        result = list(skills)
        logger.debug(f"识别到技能: {result}")
        return result
    
    @staticmethod
    def extract_soft_skills(text: str) -> List[str]:
        """提取软技能"""
        soft_skills = set()
        
        for skill_name, keywords in SOFT_SKILLS_LIBRARY.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                soft_skills.add(skill_name)
        
        result = list(soft_skills)
        logger.debug(f"识别到软技能: {result}")
        return result
    
    @staticmethod
    def extract_name(text: str) -> Optional[str]:
        """提取姓名"""
        import re
        
        patterns = [
            r'(?:^|\n)\s*姓名[:\s：]+([^\n\r，,]+)',
            r'(?:^|\n)\s*名字[:\s：]+([^\n\r，,]+)',
            r'(?:Name[:\s]+([^\n\r,]+))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if name and len(name) <= 50 and not any(c in name for c in '【】《》</'):
                    logger.debug(f"识别到姓名: {name}")
                    return name
        
        logger.debug("未识别姓名")
        return None
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """提取邮箱"""
        import re
        
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        
        if match:
            email = match.group()
            logger.debug(f"识别到邮箱: {email}")
            return email
        
        logger.debug("未识别邮箱")
        return None
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """提取电话号码"""
        import re
        
        pattern = r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}'
        match = re.search(pattern, text)
        
        if match:
            phone = match.group()
            logger.debug(f"识别到电话: {phone}")
            return phone
        
        logger.debug("未识别电话")
        return None
    
    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        """统一解析接口"""
        logger.info("开始解析简历信息...")
        
        info = {
            "name": cls.extract_name(text) or "未提取",
            "email": cls.extract_email(text) or "",
            "phone": cls.extract_phone(text) or "",
            "education": cls.extract_education(text),
            "technical_skills": cls.extract_skills(text),
            "soft_skills": cls.extract_soft_skills(text),
            "work_experience": "未填写"  # 需要更复杂的 NLP
        }
        
        logger.info(f"简历解析完成: {info}")
        return info


# ==================== 文件验证工具 ====================

class FileValidator:
    """文件验证工具"""
    
    @staticmethod
    def validate_extension(filename: str) -> str:
        """验证文件扩展名"""
        import os
        
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileFormatException(ext, list(ALLOWED_EXTENSIONS))
        
        logger.debug(f"文件扩展名验证通过: {ext}")
        return ext
    
    @staticmethod
    def validate_size(size_bytes: int) -> None:
        """验证文件大小"""
        if size_bytes > MAX_FILE_SIZE:
            raise FileTooLargeException(size_bytes, MAX_FILE_SIZE)
        
        logger.debug(f"文件大小验证通过: {size_bytes} bytes")


# ==================== 使用示例和导出 ====================

__all__ = [
    # 验证模型
    'CandidateIDValidator',
    'ResumeParseRequest',
    'ResumeUploadRequest',
    
    # 异常类
    'ResumeProcessingException',
    'InvalidFileFormatException',
    'FileTooLargeException',
    'TextExtractionException',
    'OCRProcessingException',
    'InfoParsingException',
    
    # 工具类
    'ResumeTextExtractor',
    'OCRModelCache',
    'ResumeInfoParser',
    'FileValidator',
    
    # 常量
    'ALLOWED_EXTENSIONS',
    'MAX_FILE_SIZE',
    'TECH_SKILLS_LIBRARY',
]
