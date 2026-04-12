"""
HR 邀请 Schema
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class InvitationCreate(BaseModel):
    """创建邀请请求"""
    candidate_id: int
    job_id: int
    message: Optional[str] = None


class InvitationResponse(BaseModel):
    """单条邀请响应"""
    id: int
    hr_id: int
    hr_name: Optional[str] = None
    candidate_id: int
    candidate_name: Optional[str] = None
    job_id: int
    job_name: str
    company: str
    salary: Optional[str] = None
    city: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationListResponse(BaseModel):
    """邀请列表响应"""
    total: int
    items: List[InvitationResponse]

    class Config:
        from_attributes = True
