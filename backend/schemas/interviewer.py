"""
虚拟面试官 API 数据验证模型
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求模型 ====================

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息发送者角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class InterviewerChatRequest(BaseModel):
    """虚拟面试官聊天请求"""
    interviewer_id: str = Field(..., description="面试官ID，如: hr_liming")
    candidate_id: str = Field(..., description="候选人ID")
    candidate_message: str = Field(..., description="候选人的消息内容")
    round_num: int = Field(default=0, description="当前轮次（从0开始）")
    session_id: Optional[str] = Field(None, description="会话ID，用于跟踪")


class EvaluationRequest(BaseModel):
    """评估请求（后台任务）"""
    candidate_id: str = Field(..., description="候选人ID")
    interviewer_id: str = Field(..., description="面试官ID")
    candidate_response: str = Field(..., description="候选人的回答")
    question: str = Field(..., description="提出的问题")
    round_num: int = Field(default=0, description="轮次")


class SwitchInterviewerRequest(BaseModel):
    """切换面试官请求"""
    interviewer_id: str = Field(..., description="新的面试官ID")
    candidate_id: str = Field(..., description="候选人ID")
    session_id: Optional[str] = Field(None, description="会话ID")


# ==================== 响应模型 ====================

class TraitScore(BaseModel):
    """特质评分"""
    dimension: str = Field(..., description="评估维度名称")
    score: float = Field(..., description="评分（0-10）")
    weight: float = Field(default=0.0, description="权重")


class EvaluationResult(BaseModel):
    """单次评估结果"""
    dimension: str = Field(..., description="评估维度")
    score: float = Field(..., description="评分")
    reasoning: str = Field(..., description="评估理由")
    timestamp: datetime = Field(default_factory=datetime.now)


class InterviewerRoleInfo(BaseModel):
    """面试官角色信息"""
    role_id: str = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    role_type: str = Field(..., description="角色类型")
    tone: str = Field(..., description="语气风格")
    focus_areas: List[str] = Field(..., description="关注领域")
    role_description: str = Field(..., description="角色描述")
    evaluation_focus: Dict[str, float] = Field(..., description="评估维度及权重")


class InterviewerStateResponse(BaseModel):
    """面试官状态响应"""
    role_name: str
    role_type: str
    current_round: int
    conversation_history: List[Dict[str, Any]]
    questions_asked: List[str]
    candidate_responses: List[str]
    scores: Dict[str, float]
    created_at: str


class ChatResponse(BaseModel):
    """普通聊天响应"""
    status: str = Field(default="success", description="状态: success 或 error")
    message: str = Field(..., description="响应消息")
    interviewer_name: str = Field(..., description="面试官名称")
    next_question: Optional[str] = Field(None, description="下一个问题（如有）")


class ChatStreamEvent(BaseModel):
    """SSE 流式事件"""
    type: str = Field(..., description="事件类型: start, content, end, error")
    data: str = Field(..., description="事件数据")
    timestamp: datetime = Field(default_factory=datetime.now)


class EvaluationScore(BaseModel):
    """评估分数"""
    dimension: str = Field(..., description="维度名称")
    score: float = Field(..., description="分数")
    weight: float = Field(..., description="权重")


class InterviewSessionState(BaseModel):
    """面试会话状态"""
    session_id: str = Field(..., description="会话ID")
    candidate_id: str = Field(..., description="候选人ID")
    current_interviewer_id: str = Field(..., description="当前面试官ID")
    current_interviewer_name: str = Field(..., description="当前面试官名称")
    current_round: int = Field(..., description="当前轮次")
    total_messages: int = Field(..., description="总消息数")
    all_scores: Dict[str, Dict[str, float]] = Field(..., description="所有面试官的评分")
    last_updated: datetime = Field(..., description="最后更新时间")


class EvaluationCompleted(BaseModel):
    """评估完成事件"""
    type: str = Field(default="evaluation_completed")
    dimension: str = Field(..., description="评估维度")
    score: float = Field(..., description="评分")
    reasoning: str = Field(..., description="评估理由")
    interviewer_id: str = Field(..., description="评估者ID")


class RoundTransitionRequest(BaseModel):
    """轮次转换请求"""
    candidate_id: str = Field(..., description="候选人ID")
    session_id: str = Field(..., description="会话ID")
    next_interviewer_id: str = Field(..., description="下一个面试官ID")


class RoundTransitionResponse(BaseModel):
    """轮次转换响应"""
    status: str = Field(default="success")
    session_id: str
    new_interviewer: InterviewerRoleInfo
    current_round: int
    opening_message: str = Field(..., description="新面试官的开场白")


class BatchEvaluationRequest(BaseModel):
    """批量评估请求"""
    candidate_id: str = Field(..., description="候选人ID")
    responses: List[Dict[str, str]] = Field(..., description="回答列表")
    interviewers: List[str] = Field(..., description="参与评估的面试官ID列表")


class ComprehensiveReport(BaseModel):
    """综合评估报告"""
    candidate_id: str
    session_id: str
    total_rounds: int
    all_interviews: List[InterviewSessionState]
    final_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    overall_score: float
    created_at: datetime
