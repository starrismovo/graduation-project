from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_hr = Column(Boolean, default=False)  # False: 候选人, True: HR
    
    # 关系
    jobs = relationship("Job", back_populates="creator", cascade="all, delete")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete")