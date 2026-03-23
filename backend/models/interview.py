from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 外键 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ===== 关系 =====
    candidate = relationship("User", back_populates="interviews", foreign_keys=[candidate_id])
    job = relationship("Job", back_populates="interviews")
    
    # ===== 面试信息 =====
    status = Column(String(20), default="started", index=True)  # started/in_progress/completed/passed/failed/withdrawn
    
    # ===== 面试结果（大五人格得分） =====
    personality_traits = Column(JSON, nullable=True)  # {"openness": 6.5, "conscientiousness": 8.0, ...}
    match_score = Column(Float, nullable=True)  # 匹配度 0-100
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ===== 审计和软删除 =====
    is_deleted = Column(Boolean, default=False, index=True)  # 软删除标记
    deleted_at = Column(DateTime, nullable=True)  # 删除时间
    
    # ===== 其他信息 =====
    notes = Column(String(500), nullable=True)
    
    def get_duration_minutes(self):
        """计算面试耗时（分钟）"""
        if self.completed_at and self.created_at:
            duration = (self.completed_at - self.created_at).total_seconds() / 60
            return round(duration, 2)
        return None
