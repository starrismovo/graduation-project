from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_hr = Column(Boolean, default=False)  # False: 候选人, True: HR
    
    # 个人资料字段
    nickname = Column(String(50), nullable=True)  # 显示昵称
    real_name = Column(String(100), nullable=True)  # 真实姓名
    phone = Column(String(20), nullable=True)  # 电话
    bio = Column(Text, nullable=True)  # 自我介绍
    avatar_url = Column(Text, nullable=True)  # 头像 Base64 (LONGTEXT 支持最大2MB图片)
    delivery_privacy = Column(Integer, default=2)  # 1=实名, 2=昵称, 3=匿名
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    jobs = relationship("Job", back_populates="creator", cascade="all, delete")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete")