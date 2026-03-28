"""
岗位需求结构化模型
======================

将 JD（职位描述）转化为结构化标签，包含：
- 所需能力项 (Competency Requirements)
- 大五人格理想区间 (Big Five Personality Ranges)
- 技能优先级 (Skill Priority)
"""

from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
from typing import Optional, List, Dict


class JobRequirementTag(Base):
    """岗位需求标签"""
    __tablename__ = "job_requirement_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # 能力项配置
    capability_name = Column(String(100), nullable=False)  # 如 "需求分析", "代码能力"
    capability_category = Column(String(50), nullable=False)  # 如 "技能", "经验", "素质"
    importance_level = Column(String(20), default="medium")  # high/medium/low
    proficiency_required = Column(String(50))  # 所需等级如 "精通", "熟练", "了解"
    
    # 大五人格期望范围 (0-100 分，100为最高)
    personality_dimension = Column(String(50))  # openness/conscientiousness/extraversion/agreeableness/neuroticism
    personality_min = Column(Float, default=40)  # 最小分值
    personality_max = Column(Float, default=100)  # 最大分值
    personality_weight = Column(Float, default=1.0)  # 这个维度的权重
    
    # 关联关系
    job = relationship("Job", back_populates="requirement_tags")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    class Config:
        schema_extra = {
            "example": {
                "capability_name": "Python 编程",
                "capability_category": "技能",
                "importance_level": "high",
                "proficiency_required": "精通",
                "personality_dimension": "conscientiousness",
                "personality_min": 60,
                "personality_max": 100,
                "personality_weight": 1.5
            }
        }


class JobSkillRequirement(Base):
    """岗位技能需求（细粒度）"""
    __tablename__ = "job_skill_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    skill_name = Column(String(100), nullable=False)  # 如 "Python", "React", "SQL"
    skill_type = Column(String(50), nullable=False)  # "programming_language"/"framework"/"tool"/"methodology"
    required_level = Column(String(30))  # "junior"/"intermediate"/"expert"
    years_experience = Column(Integer, nullable=True)  # 所需经验年数
    is_must_have = Column(Boolean, default=False)  # 是否必需
    priority_score = Column(Float, default=5)  # 1-10 优先级分
    
    # 关联
    job = relationship("Job", back_populates="skill_requirements")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    class Config:
        schema_extra = {
            "example": {
                "skill_name": "Python",
                "skill_type": "programming_language",
                "required_level": "expert",
                "years_experience": 3,
                "is_must_have": True,
                "priority_score": 9
            }
        }


class JobPersonalityFramework(Base):
    """岗位大五人格评估框架"""
    __tablename__ = "job_personality_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    
    # 各维度期望范围（0-100）
    openness_min = Column(Float, default=30)  # 开放性最低
    openness_max = Column(Float, default=100)
    openness_weight = Column(Float, default=1.0)
    
    conscientiousness_min = Column(Float, default=50)  # 尽责性最低
    conscientiousness_max = Column(Float, default=100)
    conscientiousness_weight = Column(Float, default=1.5)
    
    extraversion_min = Column(Float, default=20)  # 外向性最低
    extraversion_max = Column(Float, default=100)
    extraversion_weight = Column(Float, default=1.0)
    
    agreeableness_min = Column(Float, default=40)  # 宜人性最低
    agreeableness_max = Column(Float, default=100)
    agreeableness_weight = Column(Float, default=1.0)
    
    neuroticism_min = Column(Float, default=0)  # 神经质最低
    neuroticism_max = Column(Float, default=60)  # 神经质最高（越低越好）
    neuroticism_weight = Column(Float, default=1.2)
    
    # 说明
    description = Column(Text, nullable=True)  # 为什么这个岗位需要这样的人格特质
    
    job = relationship("Job", back_populates="personality_framework", uselist=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    class Config:
        schema_extra = {
            "example": {
                "openness_min": 50,
                "openness_max": 100,
                "conscientiousness_min": 70,
                "conscientiousness_max": 100,
                "extraversion_min": 60,
                "extraversion_max": 100,
                "agreeableness_min": 40,
                "agreeableness_max": 100,
                "neuroticism_min": 0,
                "neuroticism_max": 50,
                "description": "此岗位需要高度责任心和开放心态"
            }
        }


class CandidateJobApplication(Base):
    """候选人应聘记录"""
    __tablename__ = "candidate_job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # 应聘状态
    application_status = Column(String(50), default="applied")  # applied/interviewing/passed/rejected/offer
    match_score = Column(Float, nullable=True)  # 与岗位的匹配度 0-100
    
    # 评估结果
    resume_match_score = Column(Float, nullable=True)  # 简历匹配分
    personality_match_score = Column(Float, nullable=True)  # 人格匹配分
    overall_score = Column(Float, nullable=True)  # 综合评分
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 关联关系
    candidate = relationship("User", foreign_keys=[candidate_id])
    job = relationship("Job", foreign_keys=[job_id])
    
    # 时间戳
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    class Config:
        schema_extra = {
            "example": {
                "candidate_id": "cand_123",
                "job_id": 1,
                "application_status": "interviewing",
                "match_score": 78.5
            }
        }
