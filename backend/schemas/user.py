from pydantic import BaseModel, EmailStr
from typing import Optional
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

