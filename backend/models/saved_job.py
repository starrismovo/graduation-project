"""
候选人心动岗位模型
用于存储候选人收藏的岗位
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class SavedJob(Base):
    """候选人心动岗位（收藏）"""
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    # 关联关系
    candidate = relationship("User", foreign_keys=[candidate_id])
    job = relationship("Job", foreign_keys=[job_id], lazy="joined")

    # 时间戳
    saved_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 确保一个候选人只能收藏一个岗位一次
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="unique_candidate_job_save"),
    )

    class Config:
        schema_extra = {
            "example": {
                "candidate_id": 5,
                "job_id": 1,
                "saved_at": "2024-01-20T10:30:00Z"
            }
        }
