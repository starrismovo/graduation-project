"""
评估框架数据模型
存储每个岗位的大五人格评估标准和权重
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class EvaluationFramework(Base):
    """
    评估框架表 - 定义每个岗位的人格评估标准和权重
    """
    __tablename__ = "evaluation_frameworks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 关键外键：关联到岗位 =====
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), 
                   nullable=False, unique=True, index=True)
    
    # ===== 关系 =====
    job = relationship("Job", back_populates="evaluation_framework")
    
    # ===== 评估标准 =====
    # 大五人格评估目标值：{'openness': 0.7, 'conscientiousness': 0.8, ...}
    trait_targets = Column(JSON, nullable=False, default={})
    
    # 各特质权重：{'openness': 0.15, 'conscientiousness': 0.2, ...}
    trait_weights = Column(JSON, nullable=False, default={})
    
    # ===== 评估阈值 =====
    min_match_score = Column(Float, default=0.6)  # 最低匹配度要求（0-1）
    ideal_match_score = Column(Float, default=0.8)  # 理想匹配度
    
    # ===== 版本和管理 =====
    version = Column(Integer, default=1)  # 版本号（用于管理标准演变）
    description = Column(String(500), nullable=True)  # 框架描述
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "trait_targets": self.trait_targets,
            "trait_weights": self.trait_weights,
            "min_match_score": self.min_match_score,
            "ideal_match_score": self.ideal_match_score,
            "version": self.version,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @staticmethod
    def default_framework():
        """获取默认的评估框架"""
        return {
            "trait_targets": {
                "openness": 0.7,
                "conscientiousness": 0.8,
                "extraversion": 0.6,
                "agreeableness": 0.7,
                "neuroticism": 0.4
            },
            "trait_weights": {
                "openness": 0.15,
                "conscientiousness": 0.25,
                "extraversion": 0.20,
                "agreeableness": 0.20,
                "neuroticism": 0.20
            }
        }
