from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.candidate import Candidate
from ..schemas.candidate import BasicInfoSchema, BasicInfoResponseSchema
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

@router.post("/{candidate_id}/basic-info", response_model=BasicInfoResponseSchema)
async def save_basic_info(
    candidate_id: str,
    data: BasicInfoSchema,
    db: Session = Depends(get_db)
):
    """保存或更新候选人基本信息"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        # 新建候选人
        candidate = Candidate(id=candidate_id)
        db.add(candidate)

    # 更新数据
    candidate.name = data.name
    candidate.age = data.age
    candidate.education = data.education
    candidate.major = data.major
    candidate.desired_job = data.desired_job
    candidate.experience_years = data.experience_years
    candidate.skills = data.skills

    db.commit()
    db.refresh(candidate)
    return candidate

@router.get("/{candidate_id}/basic-info", response_model=BasicInfoResponseSchema)
async def get_basic_info(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """获取候选人基本信息"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    return candidate