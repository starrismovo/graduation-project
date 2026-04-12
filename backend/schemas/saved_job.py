"""
心动岗位 Schema
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SavedJobResponse(BaseModel):
    """单个收藏岗位响应"""
    id: int
    candidate_id: int
    job_id: int
    job_name: str
    company: str
    salary: Optional[str]
    city: Optional[str]
    saved_at: datetime

    class Config:
        from_attributes = True


class SavedJobListResponse(BaseModel):
    """收藏岗位列表响应"""
    total: int
    items: List[SavedJobResponse]

    class Config:
        from_attributes = True


class SavedJobStats(BaseModel):
    """收藏岗位统计"""
    total: int
    today_added: int

    class Config:
        from_attributes = True
