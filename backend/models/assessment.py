"""
评估记录数据模型
存储候选人的评估历史、心理特质、匹配分析等
"""

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum


class AssessmentStatus(str, Enum):
    """评估状态"""
    PENDING = "pending"        # 进行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


class AssessmentRecord(Base):
    """评估记录表 - 存储候选人对岗位的一次完整评估"""
    __tablename__ = "assessment_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 外键关系 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 哪个 HR 创建的这个评估
    
    # ===== 关系 =====
    candidate = relationship("User", foreign_keys=[candidate_id], back_populates="assessments")
    job = relationship("Job")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="created_assessments")
    responses = relationship("InterviewResponse", back_populates="assessment", cascade="all, delete-orphan")
    match_analysis = relationship("AssessmentMatchAnalysis", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    trait_descriptions = relationship("PersonalityTraitDescription", back_populates="assessment", cascade="all, delete-orphan")
    conversation_turns = relationship("ConversationTurn", cascade="all, delete-orphan")
    conversation_analysis = relationship("ConversationAnalysis", uselist=False, cascade="all, delete-orphan")
    
    job_title = Column(String(255), nullable=False)
    
    # ===== 评估过程 =====
    assessment_status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.PENDING, index=True)
    assessment_mode = Column(String(50), default="immersive", index=True)  # immersive, traditional, etc.
    
    # ===== 评估结果 =====
    match_score = Column(Float, nullable=True)  # 匹配分数：0-100
    
    # ===== 评估统计 =====
    conversation_summary = Column(Text, nullable=True)  # AI生成的对话总结
    total_rounds = Column(Integer, default=0)  # 总对话轮次
    duration_minutes = Column(Float, nullable=True)  # 评估耗时（分钟）
    conversation_depth = Column(Float, nullable=True)  # 对话深度评分（0-10）
    roles_participated = Column(JSON, nullable=True)  # 参与的角色列表 ["hr", "tech_lead", "product"]
    overall_impression = Column(Text, nullable=True)  # 整体印象
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ===== 审计和软删除 =====
    is_deleted = Column(Boolean, default=False, index=True)  # 软删除标记
    deleted_at = Column(DateTime, nullable=True)  # 删除时间
    
    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_title": self.job_title,
            "match_score": self.match_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "assessment_status": self.assessment_status.value if self.assessment_status else None,
            "assessment_mode": self.assessment_mode,
            "is_deleted": self.is_deleted,
        }


class CandidatePersonalityProfile(Base):
    """候选人心理特质聚合表 - 存储候选人的最新心理画像"""
    __tablename__ = "candidate_personality_profiles"

    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    
    # ===== 关系 =====
    candidate = relationship("User", back_populates="personality_profile", foreign_keys=[candidate_id])
    
    # ===== Big Five 人格模型评分（0-10） =====
    trait_extroversion = Column(Float, nullable=True)        # 外向性
    trait_agreeableness = Column(Float, nullable=True)       # 宜人性
    trait_conscientiousness = Column(Float, nullable=True)   # 尽责性
    trait_neuroticism = Column(Float, nullable=True)         # 神经质
    trait_openness = Column(Float, nullable=True)            # 开放性
    
    # ===== 聚合信息 =====
    assessment_count = Column(Integer, default=0)            # 评估次数
    latest_assessment_id = Column(Integer, nullable=True)    # 最新评估ID
    
    # ===== 时间戳 =====
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为前端需要的格式"""
        traits = [
            {"name": "外向性", "score": self.trait_extroversion},
            {"name": "宜人性", "score": self.trait_agreeableness},
            {"name": "尽责性", "score": self.trait_conscientiousness},
            {"name": "神经质", "score": self.trait_neuroticism},
            {"name": "开放性", "score": self.trait_openness},
        ]
        # 过滤掉 None 值
        return [t for t in traits if t["score"] is not None]


class AssessmentMatchAnalysis(Base):
    """评估匹配分析表 - 存储每次评估的详细分析"""
    __tablename__ = "assessment_match_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    assessment_record_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord", back_populates="match_analysis", foreign_keys=[assessment_record_id])
    
    # ===== 分析结果 =====
    strengths = Column(JSON, nullable=True)       # 优势列表 ["能力1", "能力2"]
    gaps = Column(JSON, nullable=True)            # 改进空间 ["能力1"]
    recommendations = Column(JSON, nullable=True) # 建议列表 ["建议1", "建议2"]
    
    # ===== 详细描述 =====
    detailed_analysis = Column(Text, nullable=True)
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PersonalityTraitDescription(Base):
    """心理特质详细描述表 - 为每个特质提供描述文案"""
    __tablename__ = "personality_trait_descriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    assessment_record_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord", back_populates="trait_descriptions", foreign_keys=[assessment_record_id])
    
    # ===== 特质信息 =====
    trait_name = Column(String(50), nullable=False)  # 特质名称
    score = Column(Float, nullable=False)             # 评分（0-10）
    description = Column(Text, nullable=False)        # 描述文案
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow)
