from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ============ Scenario Schemas ============

class ScenarioSchema(BaseModel):
    id: str
    title: str
    description: str
    target_traits: List[str]
    max_rounds: int = 3
    instructions: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============ Interview Response Schemas ============

class InterviewResponseCreateSchema(BaseModel):
    candidate_id: str
    scenario_id: str
    round_num: int
    question: str
    answer: str
    answer_latency: Optional[float] = None
    emotion: Optional[str] = None


class InterviewResponseSchema(InterviewResponseCreateSchema):
    id: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ Trait Score Schemas ============

class TraitScoreCreateSchema(BaseModel):
    response_id: str
    candidate_id: str
    scenario_id: str
    trait_name: str
    score: float  # 1-10
    reasoning: Optional[str] = None


class TraitScoreSchema(TraitScoreCreateSchema):
    id: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ HR-Agent Request/Response Schemas ============

class FollowUpQuestionRequest(BaseModel):
    """生成追问问题的请求"""
    candidate_id: str
    scenario_id: str
    round_num: int
    previous_answers: List[dict]  # 历史回答


class FollowUpQuestionResponse(BaseModel):
    """生成追问问题的响应"""
    question: str
    reasoning: Optional[str] = None


class ScoreAnswerRequest(BaseModel):
    """评分回答的请求"""
    candidate_id: str
    scenario_id: str
    response_id: str
    target_traits: List[str]  # 要评分的特质
    answer: str


class ScoreAnswerResponse(BaseModel):
    """评分回答的响应"""
    scores: dict  # {"特质名": 分数, ...}
    reasoning: dict  # {"特质名": 理由, ...}


class ScenarioSummarySchema(BaseModel):
    """情境评估总结"""
    candidate_id: str
    scenario_id: str
    trait_averages: dict  # {"特质名": 平均分, ...}
    summary: str
    
    class Config:
        from_attributes = True
