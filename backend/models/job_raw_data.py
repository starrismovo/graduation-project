"""原始招聘数据表模型 - 存储 1255 万条智联数据"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index, BigInteger
from sqlalchemy.sql import func
from database import Base


class JobRawData(Base):
    """原始招聘数据表 - 存储来自招聘网站的原始数据"""
    __tablename__ = "boss_raw_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    
    # 基本信息
    company_name = Column(String(300), nullable=False, index=True)  # 企业名称
    position_name = Column(String(200), nullable=False, index=True)  # 招聘岗位
    city = Column(String(50), nullable=True, index=True)  # 工作城市
    district = Column(String(100), nullable=True)  # 工作区域
    
    # 薪资
    salary_min = Column(Float, nullable=True)  # 最低月薪（元）
    salary_max = Column(Float, nullable=True)  # 最高月薪（元）
    
    # 详细信息
    job_description = Column(Text, nullable=True)  # 职位描述（完整 JD）
    education = Column(String(50), nullable=True)  # 学历要求
    experience = Column(String(100), nullable=True)  # 要求经验
    recruit_count = Column(Integer, nullable=True)  # 招聘人数
    job_category = Column(String(100), nullable=True)  # 招聘类别
    job_type = Column(String(100), nullable=True)  # 初级分类
    
    # 地址信息
    company_location = Column(String(300), nullable=True)  # 公司地点
    work_location = Column(String(300), nullable=True)  # 工作地点
    
    # 时间戳
    publish_date = Column(DateTime, nullable=True)  # 招聘发布日期
    end_date = Column(DateTime, nullable=True)  # 招聘结束日期
    publish_year = Column(Integer, nullable=True, index=True)  # 招聘发布年份
    end_year = Column(Integer, nullable=True)  # 招聘结束年份
    
    # 来源
    source = Column(String(50), nullable=True, default='zhilian')  # 来源平台
    source_id = Column(String(200), nullable=True, unique=True, index=True)  # 原始ID（用于去重）
    
    # 系统字段
    created_at = Column(DateTime, server_default=func.now())  # 导入时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_processed = Column(Integer, default=0, index=True)  # 是否已处理到 jobs 表（0/1）
    
    # 索引优化查询速度
    __table_args__ = (
        Index('idx_city_year', 'city', 'publish_year'),
        Index('idx_position_city', 'position_name', 'city'),
        Index('idx_processed', 'is_processed'),
    )
