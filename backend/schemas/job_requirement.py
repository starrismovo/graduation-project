"""
岗位需求 Pydantic Schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


class JobSkillRequirementSchema(BaseModel):
    """技能需求"""
    skill_name: str = Field(..., description="技能名称，如 Python")
    skill_type: str = Field(..., description="技能类型: programming_language/framework/tool/methodology")
    required_level: Optional[str] = Field(None, description="所需等级: junior/intermediate/expert")
    years_experience: Optional[int] = Field(None, description="所需经验年数")
    is_must_have: bool = Field(False, description="是否必需")
    priority_score: float = Field(5, ge=1, le=10, description="优先级分，1-10")
    
    class Config:
        schema_extra = {
            "example": {
                "skill_name": "Python",
                "skill_type": "programming_language",
                "required_level": "expert",
                "years_experience": 3,
                "is_must_have": True,
                "priority_score": 9
            }
        }


class JobRequirementTagSchema(BaseModel):
    """岗位需求标签"""
    capability_name: str = Field(..., description="能力项，如 需求分析")
    capability_category: str = Field(..., description="能力类别: 技能/经验/素质")
    importance_level: str = Field("medium", description="重要性: high/medium/low")
    proficiency_required: Optional[str] = Field(None, description="所需等级")
    
    # 大五人格期望
    personality_dimension: Optional[str] = Field(None, description="人格维度: openness/conscientiousness/extraversion/agreeableness/neuroticism")
    personality_min: float = Field(40, ge=0, le=100, description="最小分值")
    personality_max: float = Field(100, ge=0, le=100, description="最大分值")
    personality_weight: float = Field(1.0, ge=0.1, le=5, description="权重")
    
    class Config:
        schema_extra = {
            "example": {
                "capability_name": "Python 编程",
                "capability_category": "技能",
                "importance_level": "high",
                "personality_dimension": "conscientiousness",
                "personality_min": 60,
                "personality_max": 100
            }
        }


class JobPersonalityFrameworkSchema(BaseModel):
    """岗位大五人格框架"""
    openness_min: float = Field(30, ge=0, le=100)
    openness_max: float = Field(100, ge=0, le=100)
    openness_weight: float = Field(1.0, ge=0.1, le=5)
    
    conscientiousness_min: float = Field(50, ge=0, le=100)
    conscientiousness_max: float = Field(100, ge=0, le=100)
    conscientiousness_weight: float = Field(1.5, ge=0.1, le=5)
    
    extraversion_min: float = Field(20, ge=0, le=100)
    extraversion_max: float = Field(100, ge=0, le=100)
    extraversion_weight: float = Field(1.0, ge=0.1, le=5)
    
    agreeableness_min: float = Field(40, ge=0, le=100)
    agreeableness_max: float = Field(100, ge=0, le=100)
    agreeableness_weight: float = Field(1.0, ge=0.1, le=5)
    
    neuroticism_min: float = Field(0, ge=0, le=100)
    neuroticism_max: float = Field(60, ge=0, le=100)
    neuroticism_weight: float = Field(1.2, ge=0.1, le=5)
    
    description: Optional[str] = Field(None, description="框架说明")
    
    class Config:
        schema_extra = {
            "example": {
                "conscientiousness_min": 70,
                "conscientiousness_max": 100,
                "extraversion_min": 60,
                "description": "此岗位需要高度责任心"
            }
        }


class JobRequirementInputSchema(BaseModel):
    """HR 输入岗位需求的完整结构"""
    job_id: int = Field(..., description="岗位 ID")
    jd_text: Optional[str] = Field(None, description="原始岗位描述文本（可选，用于自动解析）")
    
    # 手动输入（或通过 AI 解析填充）
    skills: List[JobSkillRequirementSchema] = Field(default=[], description="所需技能列表")
    requirement_tags: List[JobRequirementTagSchema] = Field(default=[], description="能力项标签")
    personality_framework: Optional[JobPersonalityFrameworkSchema] = Field(None, description="大五人格框架")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": 1,
                "jd_text": "我们需要一位有3年以上Python经验的后端工程师...",
                "skills": [
                    {
                        "skill_name": "Python",
                        "skill_type": "programming_language",
                        "required_level": "expert",
                        "is_must_have": True,
                        "priority_score": 9
                    }
                ],
                "personality_framework": {
                    "conscientiousness_min": 70,
                    "conscientiousness_max": 100
                }
            }
        }


class CandidateJobApplicationInputSchema(BaseModel):
    """候选人应聘岗位"""
    candidate_id: int = Field(..., description="候选人 ID")
    job_id: int = Field(..., description="岗位 ID")
    notes: Optional[str] = Field(None, description="应聘备注")
    
    class Config:
        schema_extra = {
            "example": {
                "candidate_id": "cand_123",
                "job_id": 1,
                "notes": "对这个岗位很感兴趣"
            }
        }


class CandidateJobApplicationResponseSchema(BaseModel):
    """候选人应聘记录响应"""
    id: int
    candidate_id: int
    job_id: int
    application_status: str
    match_score: Optional[float]
    resume_match_score: Optional[float]
    personality_match_score: Optional[float]
    overall_score: Optional[float]
    notes: Optional[str]
    applied_at: datetime
    updated_at: Optional[datetime]
    
    # 关联数据
    job: Optional[Dict] = None
    
    @field_validator('job', mode='before')
    @classmethod
    def convert_job_object(cls, v):
        """将 SQLAlchemy Job 对象转换为字典"""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        # 假设是 SQLAlchemy 对象
        try:
            return {
                'id': v.id,
                'name': v.name,
                'company': v.company,
                'category': v.category,
                'city': v.city,
                'salary_min': v.salary_min,
                'salary_max': v.salary_max,
            }
        except:
            return None
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "candidate_id": "cand_123",
                "job_id": 1,
                "application_status": "applied",
                "match_score": 75.5
            }
        }


class JobRequirementFullSchema(BaseModel):
    """完整的岗位需求信息（用于任务前端展示）"""
    job_id: int
    job_name: str
    job_description: str
    
    skills: List[JobSkillRequirementSchema]
    requirement_tags: List[JobRequirementTagSchema]
    personality_framework: Optional[JobPersonalityFrameworkSchema]
    
    class Config:
        from_attributes = True


class JobMatchResultSchema(BaseModel):
    """候选人与岗位的匹配结果"""
    job_id: int
    job_name: str
    candidate_id: int
    
    # 匹配分数
    resume_match_score: float = Field(..., description="简历匹配度 0-100")
    skill_match_score: float = Field(..., description="技能匹配度 0-100")
    personality_match_score: float = Field(..., description="人格匹配度 0-100")
    overall_match_score: float = Field(..., description="综合匹配度 0-100")
    
    # 详细反馈
    matched_skills: List[str] = Field(default=[], description="已匹配的技能")
    missing_skills: List[str] = Field(default=[], description="缺失的必需技能")
    personality_fit_analysis: Optional[str] = Field(None, description="人格契合度分析")
    recommendation: str = Field(..., description="推荐意见: high_match/medium_match/low_match")
    explanation: str = Field(..., description="详细解释")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": 1,
                "job_name": "高级 Python 工程师",
                "candidate_id": "cand_123",
                "resume_match_score": 85,
                "skill_match_score": 80,
                "personality_match_score": 78,
                "overall_match_score": 81,
                "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
                "missing_skills": ["Kubernetes"],
                "recommendation": "high_match",
                "explanation": "候选人具备所需的核心技能和良好的人格特质，推荐进入面试阶段"
            }
        }
