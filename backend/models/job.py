from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 岗位名称
    description = Column(String(2000), nullable=False)  # 岗位描述
    company = Column(String(100), nullable=False)  # 公司名称
    category = Column(String(50), nullable=False)  # 岗位类别：技术岗、产品岗、设计岗等
    city = Column(String(50), nullable=False)  # 工作地点
    salary_min = Column(Float, nullable=False)  # 薪资下限（单位：k）
    salary_max = Column(Float, nullable=False)  # 薪资上限（单位：k）
    
    required_traits = Column(JSON, nullable=False)  # 大五人格预期值
    
    # 新增：岗位人格需求（对应论文第4.4节岗位模板设计）
    personality_requirements = Column(JSON, nullable=True)
    # 格式: {
    #   "extroversion": 7.0,        # 外向性期望值 (1-10)
    #   "agreeableness": 8.0,       # 宜人性期望值
    #   "conscientiousness": 8.0,   # 尽责性期望值
    #   "openness": 6.0,            # 开放性期望值
    #   "emotional_stability": 7.0  # 情绪稳定性期望值
    # }
    
    # 新增：工作环境特征（影响场景人格的因素）
    work_environment = Column(JSON, nullable=True)
    # 格式: {
    #   "pace": "fast",             # 工作节奏：fast/medium/slow
    #   "autonomy": "high",         # 自主度：high/medium/low
    #   "collaboration": "high",    # 协作需求：high/medium/low
    #   "innovation_focus": "medium" # 创新关注度：high/medium/low
    # }
    
    # 外键：谁创建的这个岗位（HR）
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="jobs")
    
    # 反向关系
    interviews = relationship("Interview", back_populates="job", cascade="all, delete")
    evaluation_framework = relationship("EvaluationFramework", back_populates="job", uselist=False, cascade="all, delete")
    
    # 新增：岗位需求标签和结构
    requirement_tags = relationship("JobRequirementTag", back_populates="job", cascade="all, delete")
    skill_requirements = relationship("JobSkillRequirement", back_populates="job", cascade="all, delete")
    personality_framework = relationship("JobPersonalityFramework", back_populates="job", uselist=False, cascade="all, delete")
