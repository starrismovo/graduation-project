from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, Enum as SQLEnum
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum


class UserType(str, Enum):
    """用户类型枚举"""
    HR = "HR"
    CANDIDATE = "CANDIDATE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_hr = Column(Boolean, default=False)  # 保留用于向后兼容
    
    # ===== 用户身份类型 =====
    user_type = Column(SQLEnum(UserType), default=UserType.CANDIDATE, index=True)
    
    # ===== 个人资料字段 =====
    nickname = Column(String(50), nullable=True)  # 显示昵称
    real_name = Column(String(100), nullable=True)  # 真实姓名
    phone = Column(String(20), nullable=True)  # 电话
    bio = Column(Text, nullable=True)  # 自我介绍
    avatar_url = Column(Text, nullable=True)  # 头像 Base64 (LONGTEXT 支持最大2MB图片)
    delivery_privacy = Column(Integer, default=2)  # 1=实名, 2=昵称, 3=匿名
    notify_interview_reminder = Column(Boolean, default=True, nullable=False)
    notify_assessment_completed = Column(Boolean, default=True, nullable=False)
    notify_report_ready = Column(Boolean, default=True, nullable=False)
    notify_job_recommendation = Column(Boolean, default=True, nullable=False)
    notify_candidate_delivery = Column(Boolean, default=True, nullable=False)
    notify_candidate_assessment_completed = Column(Boolean, default=True, nullable=False)
    
    # ===== 候选人专属字段 =====
    age = Column(Integer, nullable=True)  # 年龄
    education = Column(String(50), nullable=True)  # 教育水平：大专、本科、硕士、博士
    major = Column(String(100), nullable=True)  # 专业方向
    desired_job = Column(String(100), nullable=True)  # 期望岗位
    experience_years = Column(Float, nullable=True)  # 工作年限
    skills = Column(JSON, nullable=True)  # 技能列表 ["Python", "JavaScript", ...]
    resume_url = Column(Text, nullable=True)  # 简历文件路径或 URL
    
    # ===== 审计字段 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)  # 软删除标记
    deleted_at = Column(DateTime, nullable=True)  # 删除时间
    
    # ===== 关系 =====
    jobs = relationship("Job", back_populates="creator", cascade="all, delete", foreign_keys="Job.creator_id")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete", foreign_keys="Interview.candidate_id")
    assessments = relationship("AssessmentRecord", back_populates="candidate", cascade="all, delete", foreign_keys="AssessmentRecord.candidate_id")
    personality_profile = relationship("CandidatePersonalityProfile", back_populates="candidate", uselist=False, cascade="all, delete")
    interview_responses = relationship("InterviewResponse", back_populates="candidate", cascade="all, delete", foreign_keys="InterviewResponse.candidate_id")
    created_assessments = relationship("AssessmentRecord", back_populates="created_by_user", foreign_keys="AssessmentRecord.created_by")
    
    @property
    def is_candidate(self):
        """便利属性：判断是否为候选人"""
        return self.user_type == UserType.CANDIDATE
    
    @property
    def is_hr_user(self):
        """便利属性：判断是否为 HR"""
        return self.user_type == UserType.HR
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "nickname": self.nickname,
            "user_type": self.user_type.value if self.user_type else None,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_deleted": self.is_deleted,
        }
        
        # 候选人信息
        if self.is_candidate:
            data.update({
                "age": self.age,
                "education": self.education,
                "major": self.major,
                "experience_years": self.experience_years,
                "skills": self.skills,
                "desired_job": self.desired_job,
            })
        
        # 敏感信息
        if include_sensitive:
            data.update({
                "email": self.email,
                "phone": self.phone,
            })
        
        return data
