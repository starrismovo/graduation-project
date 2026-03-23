from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 岗位名称
    description = Column(String(500), nullable=False)  # 岗位描述
    company = Column(String(100), nullable=False)  # 公司名称
    category = Column(String(50), nullable=False)  # 岗位类别：技术岗、产品岗、设计岗等
    city = Column(String(50), nullable=False)  # 工作地点
    salary_min = Column(Float, nullable=False)  # 薪资下限（单位：k）
    salary_max = Column(Float, nullable=False)  # 薪资上限（单位：k）
    
    required_traits = Column(JSON, nullable=False)  # 大五人格预期值
    
    # 外键：谁创建的这个岗位（HR）
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="jobs")
    
    # 反向关系
    interviews = relationship("Interview", back_populates="job", cascade="all, delete")
    evaluation_framework = relationship("EvaluationFramework", back_populates="job", uselist=False, cascade="all, delete")
