"""
评估系统 API 数据模式
用于前后端数据传输和验证
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TraitScore(BaseModel):
    """心理特质评分"""
    name: str
    score: float
    
    class Config:
        from_attributes = True


class TraitScoreWithDescription(TraitScore):
    """带描述的心理特质"""
    description: Optional[str] = None


class AssessmentHistoryItem(BaseModel):
    """历史评估记录项"""
    id: int
    job_id: int
    job_title: str
    match_score: Optional[float] = None
    created_at: datetime
    assessment_status: str
    assessment_mode: str
    
    class Config:
        from_attributes = True


class JobRecommendation(BaseModel):
    """岗位推荐卡片"""
    id: int
    title: str
    description: str
    department: str
    level: str
    match_score: float
    match_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class PortraitResponse(BaseModel):
    """心理画像响应 - 前端需要的格式"""
    code: int = 200
    message: str = "success"
    data: List[TraitScore]


class HistoryResponse(BaseModel):
    """历史记录响应"""
    code: int = 200
    message: str = "success"
    data: List[AssessmentHistoryItem]


class RecommendedJobsResponse(BaseModel):
    """推荐岗位响应"""
    code: int = 200
    message: str = "success"
    data: List[JobRecommendation]


class MatchAnalysis(BaseModel):
    """匹配分析"""
    strengths: List[str]
    gaps: List[str]
    
    class Config:
        from_attributes = True


class AssessmentDetails(BaseModel):
    """评估详情统计"""
    total_rounds: Optional[int] = None
    duration_minutes: Optional[float] = None
    conversation_depth: Optional[float] = None
    roles_participated: Optional[List[str]] = None
    overall_impression: Optional[str] = None


class AssessmentReport(BaseModel):
    """完整的评估报告"""
    id: int
    candidate_id: str
    job_id: int
    job_title: str
    match_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    assessment_mode: str
    
    personality_trait: List[TraitScoreWithDescription]
    conversation_summary: Optional[str] = None
    match_analysis: Optional[MatchAnalysis] = None
    recommendations: Optional[List[str]] = None
    assessement_details: Optional[AssessmentDetails] = None
    
    class Config:
        from_attributes = True


class AssessmentReportResponse(BaseModel):
    """评估报告响应"""
    code: int = 200
    message: str = "success"
    data: AssessmentReport


class CreateAssessmentRequest(BaseModel):
    """创建评估请求"""
    job_id: int


class UpdateAssessmentRequest(BaseModel):
    """更新评估请求"""
    match_score: Optional[float] = None
    assessment_status: Optional[str] = None
    conversation_summary: Optional[str] = None
    total_rounds: Optional[int] = None
    duration_minutes: Optional[float] = None
    conversation_depth: Optional[float] = None
    roles_participated: Optional[List[str]] = None
    overall_impression: Optional[str] = None
    strengths: Optional[List[str]] = None
    gaps: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    personality_traits: Optional[Dict[str, float]] = None  # {"外向性": 8.5, ...}


class StandardResponse(BaseModel):
    """标准响应格式"""
    code: int
    message: str
    data: Optional[Any] = None


# ==================== 沉浸式对话相关 schemas ====================

class DetailedScore(BaseModel):
    """详细评分"""
    trait_name: str
    score: float  # 0-10
    confidence: float  # 0-100 百分比


class BehaviorPattern(BaseModel):
    """行为模式"""
    id: str
    name: str
    description: str
    confidence: float  # 0-100
    color: str


class SentimentAnalysis(BaseModel):
    """情绪分析"""
    emotion: str  # 自信、谨慎、积极、思考中等
    confidence: float  # 0-100


class NextQuestionResponse(BaseModel):
    """获取下一个问题的响应"""
    code: int = 200
    message: str = "success"
    data: Optional[Dict[str, Any]] = None  # {content, tags, suggestions, context}


class AnalyzeResponseRequest(BaseModel):
    """分析回答的请求"""
    candidate_id: str
    candidate_name: str
    candidate_background: Optional[str] = None
    current_speaker: str  # hr, tech_lead, product, cto
    speaker_name: str
    speaker_title: str
    candidate_response: str
    previous_messages: Optional[List[Dict[str, str]]] = None  # 先前的对话历史
    conversation_depth: Optional[int] = None


class AnalyzeResponseResponse(BaseModel):
    """分析回答的响应"""
    code: int = 200
    message: str = "success"
    data: Optional[Dict[str, Any]] = None  # {scores, sentiment, patterns}


class SaveSessionRequest(BaseModel):
    """保存会话数据的请求"""
    candidate_id: str
    assessment_id: Optional[int] = None
    job_id: Optional[int] = None
    messages: List[Dict[str, Any]]
    scores: Dict[str, float]
    patterns: Optional[List[Dict[str, Any]]] = None
    duration_seconds: int
    conversation_depth: int
    total_rounds: int
    highlights: Optional[List[str]] = None


class SaveSessionResponse(BaseModel):
    """保存会话数据的响应"""
    code: int = 200
    message: str = "success"
    data: Optional[Dict[str, Any]] = None  # {session_id, assessment_id}
