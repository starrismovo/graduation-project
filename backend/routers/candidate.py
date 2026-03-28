from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, UserType
from schemas.candidate import BasicInfoSchema, BasicInfoResponseSchema
from datetime import datetime

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.post("/{candidate_id}/basic-info", response_model=BasicInfoResponseSchema)
async def save_basic_info(
    candidate_id: int,
    data: BasicInfoSchema,
    db: Session = Depends(get_db)
):
    """保存或更新候选人基本信息"""
    # 从 User 表查询候选人
    user = db.query(User).filter(
        User.id == candidate_id,
        User.user_type == UserType.CANDIDATE
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="候选人不存在")

    # 更新候选人信息
    user.real_name = data.name
    user.age = data.age
    user.education = data.education
    user.major = data.major
    user.desired_job = data.desired_job
    user.experience_years = data.experience_years
    user.skills = data.skills
    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)
    
    return BasicInfoResponseSchema(
        id=user.id,
        name=user.real_name or "",
        age=user.age or 0,
        education=user.education or "",
        major=user.major or "",
        desired_job=user.desired_job or "",
        experience_years=user.experience_years or 0,
        skills=user.skills or []
    )


@router.get("/{candidate_id}/basic-info", response_model=BasicInfoResponseSchema)
async def get_basic_info(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """获取候选人基本信息"""
    # 从 User 表查询候选人
    user = db.query(User).filter(
        User.id == candidate_id,
        User.user_type == UserType.CANDIDATE
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="候选人不存在")

    return BasicInfoResponseSchema(
        id=user.id,
        name=user.real_name or "",
        age=user.age or 0,
        education=user.education or "",
        major=user.major or "",
        desired_job=user.desired_job or "",
        experience_years=user.experience_years or 0,
        skills=user.skills or []
    )
