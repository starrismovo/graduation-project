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
    answer_length: Optional[int] = None
    is_paste: Optional[bool] = None
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
    """Request to generate a follow-up question."""
    candidate_id: str
    scenario_id: str
    round_num: int
    previous_answers: List[dict]


class FollowUpQuestionResponse(BaseModel):
    """Response containing the generated follow-up question."""
    question: str
    reasoning: Optional[str] = None


class ScoreAnswerRequest(BaseModel):
    """Request to score an answer."""
    candidate_id: str
    scenario_id: str
    response_id: str
    target_traits: List[str]
    answer: str


class ScoreAnswerResponse(BaseModel):
    """Response containing scores for the answer."""
    scores: dict
    reasoning: dict


class ScenarioSummarySchema(BaseModel):
    """Scenario evaluation summary."""
    candidate_id: str
    scenario_id: str
    trait_averages: dict
    summary: str

    class Config:
        from_attributes = True


# ============ DeepSeek/OpenAI-Style Schemas ============

class DeepSeekMessageSchema(BaseModel):
    role: str
    content: Optional[str] = None


class DeepSeekChoiceSchema(BaseModel):
    index: int
    message: Optional[DeepSeekMessageSchema] = None
    finish_reason: Optional[str] = None


class DeepSeekUsageSchema(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class DeepSeekChatCompletionResponseSchema(BaseModel):
    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: Optional[List[DeepSeekChoiceSchema]] = None
    usage: Optional[DeepSeekUsageSchema] = None


class DeepSeekErrorDetailSchema(BaseModel):
    message: str
    type: Optional[str] = None
    param: Optional[str] = None
    code: Optional[str] = None


class DeepSeekErrorResponseSchema(BaseModel):
    error: DeepSeekErrorDetailSchema


class PromptBuildRequestSchema(BaseModel):
    """Inputs for building a model prompt."""
    role_type: str
    round_num: int
    history: List[dict]


class PromptBuildResponseSchema(BaseModel):
    """Built prompt content."""
    prompt: str
