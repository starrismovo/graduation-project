from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Scenario(Base):
    """情境模板表 - 存储评估情景"""
    __tablename__ = "scenarios"
    
    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)  # 详细情景描述
    target_traits = Column(JSON, nullable=False)  # 目标特质数组，如 ["责任心", "宜人性"]
    max_rounds = Column(Integer, default=3)  # 最多追问几轮
    instructions = Column(Text)  # HR-Agent的系统指令
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class InterviewResponse(Base):
    """面试回答记录表 - 存储每一轮的回答"""
    __tablename__ = "interview_responses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 关键外键：关联到具体的评估 =====
    assessment_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # ===== 其他外键 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(String(50), ForeignKey("scenarios.id"), nullable=False, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord", back_populates="responses", foreign_keys=[assessment_id])
    candidate = relationship("User", back_populates="interview_responses", foreign_keys=[candidate_id])
    scenario = relationship("Scenario")
    
    # ===== 回答内容 =====
    round_num = Column(Integer, nullable=False)  # 第几轮（1, 2, 3...）
    question = Column(Text, nullable=False)  # HR-Agent问题
    answer = Column(Text, nullable=False)  # 候选人回答
    
    # ===== 行为分析 =====
    answer_latency = Column(Float, nullable=True)  # 回答耗时（秒）
    emotion = Column(String(50), nullable=True)  # 检测到的情感（中性、焦虑、自信等）
    answer_length = Column(Integer, nullable=True)  # 回答长度（字数）
    is_paste = Column(Boolean, default=False)  # 是否粘贴回答
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ===== 关联的评分 =====
    trait_scores = relationship("TraitScore", back_populates="response", cascade="all, delete-orphan")


class TraitScore(Base):
    """特质评分表 - 存储每一轮对特质的评分"""
    __tablename__ = "trait_scores"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 外键 =====
    response_id = Column(Integer, ForeignKey("interview_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ===== 关系 =====
    response = relationship("InterviewResponse", back_populates="trait_scores", foreign_keys=[response_id])
    
    # ===== 上下文信息 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(String(50), ForeignKey("scenarios.id"), nullable=False)
    
    # ===== 评分信息 =====
    trait_name = Column(String(50), nullable=False)  # 特质名称（如"责任心"）
    score = Column(Float, nullable=False)  # 评分 0-10
    reasoning = Column(Text, nullable=True)  # 评分理由
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow)


class ScenarioSummary(Base):
    """情境评估总结表 - 存储一个情境的最终评分"""
    __tablename__ = "scenario_summaries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 外键 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(String(50), ForeignKey("scenarios.id"), nullable=False, index=True)
    
    # ===== 评分信息 =====
    trait_name = Column(String(50), nullable=False)  # 特质名称
    average_score = Column(Float, nullable=True)  # 所有轮次的平均分
    summary = Column(Text, nullable=True)  # 总体评价
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
