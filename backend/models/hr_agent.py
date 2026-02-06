from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, Boolean
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InterviewResponse(Base):
    """面试回答记录表 - 存储每一轮的回答"""
    __tablename__ = "interview_responses"
    
    id = Column(String(100), primary_key=True, index=True)
    candidate_id = Column(String(100), nullable=False, index=True)
    scenario_id = Column(String(50), nullable=False)
    round_num = Column(Integer, nullable=False)  # 第几轮（1, 2, 3...）
    question = Column(Text, nullable=False)  # HR-Agent问题
    answer = Column(Text, nullable=False)  # 候选人回答
    answer_latency = Column(Float)  # 回答耗时（秒）
    emotion = Column(String(50))  # 检测到的情感（中性、焦虑、自信等）
    answer_length = Column(Integer)
    is_paste = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TraitScore(Base):
    """特质评分表 - 存储每一轮对特质的评分"""
    __tablename__ = "trait_scores"
    
    id = Column(String(100), primary_key=True, index=True)
    response_id = Column(String(100), nullable=False, index=True)
    candidate_id = Column(String(100), nullable=False, index=True)
    scenario_id = Column(String(50), nullable=False)
    trait_name = Column(String(50), nullable=False)  # 特质名称（如"责任心"）
    score = Column(Float, nullable=False)  # 评分 1-10
    reasoning = Column(Text)  # 评分理由
    created_at = Column(DateTime, default=datetime.utcnow)


class ScenarioSummary(Base):
    """情境评估总结表 - 存储一个情境的最终评分"""
    __tablename__ = "scenario_summaries"
    
    id = Column(String(100), primary_key=True, index=True)
    candidate_id = Column(String(100), nullable=False, index=True)
    scenario_id = Column(String(50), nullable=False)
    trait_name = Column(String(50), nullable=False)
    average_score = Column(Float)  # 所有轮次的平均分
    summary = Column(Text)  # 总体评价
    created_at = Column(DateTime, default=datetime.utcnow)
