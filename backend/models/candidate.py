from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from database import Base
from datetime import datetime


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    education = Column(String(50), nullable=True)  # 大专、本科、硕士、博士
    major = Column(String(100), nullable=True)
    desired_job = Column(String(100), nullable=True)
    experience_years = Column(Float, nullable=True)
    skills = Column(JSON, nullable=True)  # 存储列表
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)