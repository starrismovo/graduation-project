from pydantic import BaseModel
from typing import List, Optional


class BasicInfoSchema(BaseModel):
    name: str
    age: int
    education: str
    major: str
    desired_job: str
    experience_years: float
    skills: List[str]


class BasicInfoResponseSchema(BasicInfoSchema):
    id: str
    
    class Config:
        from_attributes = True
