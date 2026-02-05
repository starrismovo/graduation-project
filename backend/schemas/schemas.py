from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class InterviewStatus(str, Enum):
    """面试状态"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PASSED = "passed"
    FAILED = "failed"

# ========== Job Schemas ==========

class JobCreate(BaseModel):
    """创建岗位请求"""
    name: str
    description: str
    company: str
    category: str
    city: str
    salary_min: float
    salary_max: float
    required_traits: Dict[str, Any]

class JobUpdate(BaseModel):
    """更新岗位请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    company: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    required_traits: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    """岗位响应"""
    id: int
    name: str
    description: str
    company: str
    category: str
    city: str
    salary_min: float
    salary_max: float
    required_traits: Dict[str, Any]
    creator_id: Optional[int] = None

    class Config:
        from_attributes = True

class JobCardResponse(BaseModel):
    """前端岗位卡片响应（用于主页展示）"""
    id: int
    name: str
    company: str
    city: str
    category: str
    salary: str  # 格式化为 "25k-35k"
    description: str
    applied: bool = False  # 是否已应聘

    class Config:
        from_attributes = True

# ========== Interview Schemas ==========

class InterviewCreate(BaseModel):
    """开始面试请求"""
    job_id: int

class InterviewUpdate(BaseModel):
    """更新面试请求"""
    status: Optional[InterviewStatus] = None
    personality_traits: Optional[Dict[str, Any]] = None
    match_score: Optional[float] = None
    notes: Optional[str] = None

class InterviewResponse(BaseModel):
    """面试响应"""
    id: int
    candidate_id: int
    job_id: int
    status: InterviewStatus
    personality_traits: Optional[Dict[str, Any]] = None
    match_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class InterviewDetailResponse(InterviewResponse):
    """面试详情响应（包含岗位和用户信息）"""
    job: Optional[JobResponse] = None
    candidate_name: Optional[str] = None

# ========== Dashboard/Home Page Schemas ==========

class InterviewStatsResponse(BaseModel):
    """面试统计响应"""
    completed: int  # 已完成面试数
    in_progress: int  # 进行中的面试数
    total: int  # 总应聘数
    passed: int  # 通过筛选数

class HomeDataResponse(BaseModel):
    """主页数据聚合响应"""
    stats: InterviewStatsResponse
    recommended_jobs: List[JobCardResponse]
    user_username: str
    user_is_hr: bool

# ========== User Schemas ==========

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_hr: bool

    class Config:
        from_attributes = True
