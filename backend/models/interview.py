from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # 外键
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # 关系
    candidate = relationship("User", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    
    # 面试信息
    status = Column(String(20), default="started")  # started/in_progress/completed/passed/failed
    
    # 面试结果（大五人格得分）
    personality_traits = Column(JSON, nullable=True)  # {"openness": 6.5, "conscientiousness": 8.0, ...}
    match_score = Column(Float, nullable=True)  # 匹配度 0-100
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # 其他备注
    notes = Column(String(500), nullable=True)
