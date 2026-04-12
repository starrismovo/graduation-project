"""
HR 邀请模型
HR 可以邀请候选人参加指定岗位的评估面试
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum


class InvitationStatus(str, Enum):
    """邀请状态"""
    PENDING = "pending"        # 待处理
    ACCEPTED = "accepted"      # 已接受
    DECLINED = "declined"      # 已拒绝
    EXPIRED = "expired"        # 已过期


class HRInvitation(Base):
    """HR 邀请候选人评估表"""
    __tablename__ = "hr_invitations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 邀请方 (HR)
    hr_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # 被邀请方 (候选人)
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # 邀请岗位
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # 邀请消息
    message = Column(Text, nullable=True)
    # 邀请状态
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False, index=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime, nullable=True)  # 候选人响应时间

    # 关系
    hr = relationship("User", foreign_keys=[hr_id])
    candidate = relationship("User", foreign_keys=[candidate_id])
    job = relationship("Job")

    __table_args__ = (
        UniqueConstraint("hr_id", "candidate_id", "job_id", name="uq_hr_candidate_job"),
    )
