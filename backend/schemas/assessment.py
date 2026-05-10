"""
评估系统 API 数据模式
用于前后端数据传输和验证
"""

from pydantic import BaseModel, Field
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
    company: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    salary: Optional[str] = None
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
    model_version: Optional[str] = None


class MatchDimension(BaseModel):
    """结构化匹配维度"""
    label: str
    score: float
    description: Optional[str] = None


class TraitInsight(BaseModel):
    """大五人格结构化解读"""
    name: str
    score: float
    description: Optional[str] = None
    job_requirement: Optional[float] = None
    match_status: str
    summary: str
    advice: Optional[str] = None


class CareerRecommendationItem(BaseModel):
    """职业建议条目"""
    title: str
    fit_level: str
    reason: str
    action: Optional[str] = None


class DevelopmentActionItem(BaseModel):
    """发展建议条目"""
    phase: str
    title: str
    description: str


class ReportSections(BaseModel):
    """报告详情页结构化内容"""
    overview_summary: Optional[str] = None
    personality_summary: Optional[str] = None
    match_dimensions: List[MatchDimension] = Field(default_factory=list)
    trait_insights: List[TraitInsight] = Field(default_factory=list)
    career_recommendations: List[CareerRecommendationItem] = Field(default_factory=list)
    cautious_career_recommendations: List[CareerRecommendationItem] = Field(default_factory=list)
    development_actions: List[DevelopmentActionItem] = Field(default_factory=list)


class PsychologyOverview(BaseModel):
    """心理解读页总体概览"""
    summary: str
    score: float
    highlighted_traits: List[str] = Field(default_factory=list)
    growth_advice: str
    updated_at: Optional[datetime] = None


class PsychologyTraitCard(BaseModel):
    """心理解读页大五人格维度卡片"""
    trait_key: str
    trait_name: str
    english: str
    score: Optional[float] = None
    job_requirement: Optional[float] = None
    match_status: str = "balanced"
    summary: str
    tags: List[str] = Field(default_factory=list)
    advice: str
    bubble_message: str


class PsychologyActionGuide(BaseModel):
    """心理解读页行动建议"""
    title: str
    description: str


class PsychologySourceTrace(BaseModel):
    """心理解读页可回溯来源"""
    assessment_record_id: int
    evaluation_result_id: Optional[str] = None
    candidate_id: int
    job_id: int
    source_fields: List[str] = Field(default_factory=list)


class PsychologyDetail(BaseModel):
    """心理解读页详情数据"""
    assessment_id: int
    evaluation_result_id: Optional[str] = None
    candidate_id: int
    job_id: int
    job_title: str
    overview: PsychologyOverview
    trait_cards: List[PsychologyTraitCard] = Field(default_factory=list)
    action_guides: List[PsychologyActionGuide] = Field(default_factory=list)
    source_trace: PsychologySourceTrace


class PsychologyDetailResponse(BaseModel):
    """心理解读页响应"""
    code: int = 200
    message: str = "success"
    data: PsychologyDetail


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
    report_sections: Optional[ReportSections] = None
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


class SaveAssessmentResultRequest(BaseModel):
    """保存评估结果的请求"""
    candidate_id: str
    job_id: int
    assessment_mode: str = "immersive"  # immersive or standard
    all_scores: Dict[str, float] = Field(default_factory=dict)
    personality_scores: Optional[Dict[str, float]] = None
    situational_scores: Optional[Dict[str, float]] = None
    candidate_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
