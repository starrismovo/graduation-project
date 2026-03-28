from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserProfileUpdate(BaseModel):
    """用户个人信息更新请求"""
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None  # Base64 或 URL
    delivery_privacy: Optional[int] = None  # 1=实名, 2=昵称, 3=匿名
    
    # ===== 候选人专属字段 =====
    age: Optional[int] = None  # 年龄
    education: Optional[str] = None  # 教育水平：大专、本科、硕士、博士
    major: Optional[str] = None  # 专业方向
    desired_job: Optional[str] = None  # 期望岗位
    experience_years: Optional[float] = None  # 工作年限
    skills: Optional[List[str]] = None  # 技能列表 ["Python", "JavaScript", ...]
    resume_url: Optional[str] = None  # 简历文件路径或 URL


class UserProfileResponse(BaseModel):
    """用户个人信息响应"""
    id: int
    username: str
    nickname: Optional[str] = None
    real_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    delivery_privacy: int = 2
    user_type: Optional[str] = None  # "HR" 或 "CANDIDATE"
    
    # ===== 候选人专属字段 =====
    age: Optional[int] = None
    education: Optional[str] = None
    major: Optional[str] = None
    desired_job: Optional[str] = None
    experience_years: Optional[float] = None
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfileSimple(BaseModel):
    """简化的用户信息"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class AvatarUploadResponse(BaseModel):
    """头像上传响应"""
    code: int
    message: str
    data: Optional[dict] = None


class StandardResponse(BaseModel):
    """标准响应格式"""
    code: int
    message: str
    data: Optional[dict] = None

