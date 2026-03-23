"""
对话历史和分析数据模型
存储评估过程中的对话记录和整体分析
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum


class Speaker(str, Enum):
    """发言者类型"""
    CANDIDATE = "candidate"      # 候选人
    INTERVIEWER = "interviewer"  # 面试官
    SYSTEM = "system"            # 系统消息


class ConversationTurn(Base):
    """对话记录表 - 记录评估过程中的每一条消息"""
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 关键外键：关联到评估 =====
    assessment_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"), 
                          nullable=False, index=True)
    response_id = Column(Integer, ForeignKey("interview_responses.id", ondelete="SET NULL"), 
                        nullable=True, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord")
    response = relationship("InterviewResponse", foreign_keys=[response_id])
    
    # ===== 对话位置 =====
    round_num = Column(Integer, nullable=False)  # 第几轮
    turn_num = Column(Integer, nullable=False)  # 轮内第几条
    
    # ===== 发言信息 =====
    speaker = Column(SQLEnum(Speaker), nullable=False)  # 谁说的：candidate/interviewer/system
    speaker_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 具体是哪个用户/面试官
    message = Column(Text, nullable=False)  # 原始消息内容
    
    # ===== 行为数据 =====
    emotion = Column(String(50), nullable=True)       # 候选人的情感（neutral/anxious/confident）
    sentiment = Column(String(20), nullable=True)     # 情感倾向：positive/neutral/negative
    confidence_score = Column(Float, nullable=True)   # 置信度 (0-1)
    
    # ===== 技术信息 =====
    response_time_ms = Column(Integer, nullable=True)  # 响应时间（毫秒）
    message_length = Column(Integer, nullable=True)    # 消息长度（字数）
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    @property
    def is_candidate_message(self):
        """判断是否为候选人消息"""
        return self.speaker == Speaker.CANDIDATE
    
    @property
    def is_interviewer_message(self):
        """判断是否为面试官消息"""
        return self.speaker == Speaker.INTERVIEWER


class ConversationAnalysis(Base):
    """对话分析表 - 存储一次评估的对话整体分析结果"""
    __tablename__ = "conversation_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 关键外键：唯一关联到评估 =====
    assessment_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"), 
                          nullable=False, unique=True, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord")
    
    # ===== 对话统计 =====
    average_response_time = Column(Float, nullable=True)  # 平均回答时间（秒）
    total_turns = Column(Integer, default=0)  # 总对话轮数
    candidate_emotion_trend = Column(Text, nullable=True)  # 情感变化趋势描述
    
    # ===== 对话质量评分 =====
    communication_clarity = Column(Float, nullable=True)   # 表达清晰度 (0-10)
    engagement_level = Column(Float, nullable=True)        # 参与度 (0-10)
    coherence = Column(Float, nullable=True)               # 逻辑连贯性 (0-10)
    
    # ===== AI 生成的综合评价 =====
    summary = Column(Text, nullable=True)  # 对话总体评价
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "average_response_time": self.average_response_time,
            "total_turns": self.total_turns,
            "communication_clarity": self.communication_clarity,
            "engagement_level": self.engagement_level,
            "coherence": self.coherence,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
