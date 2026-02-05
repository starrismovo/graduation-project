from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import get_db
from models.user import User
from models.job import Job
from models.interview import Interview
from schemas.schemas import (
    InterviewCreate, InterviewUpdate, InterviewResponse, 
    InterviewDetailResponse
)
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/interviews", tags=["面试管理"])

# 依赖：获取当前登录用户
def get_current_user(db: Session = Depends(get_db)):
    # 演示用：假设当前是 id=1 的用户
    return db.query(User).filter(User.id == 1).first()

@router.post("/", response_model=InterviewResponse)
def start_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    候选人开始一个岗位的面试
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")
    
    if current_user.is_hr:
        raise HTTPException(status_code=403, detail="HR用户无法参加面试")
    
    # 检查岗位是否存在
    job = db.query(Job).filter(Job.id == interview.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 检查是否已经面试过该岗位
    existing = db.query(Interview).filter(
        and_(
            Interview.candidate_id == current_user.id,
            Interview.job_id == interview.job_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="您已经对该岗位进行过面试")
    
    # 创建面试记录
    new_interview = Interview(
        candidate_id=current_user.id,
        job_id=interview.job_id,
        status="started"
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    
    return new_interview

@router.get("/{interview_id}", response_model=InterviewDetailResponse)
def get_interview_detail(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取面试详情"""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    
    # 权限检查：只能查看自己的面试记录或自己发布的岗位的面试
    if interview.candidate_id != current_user.id and interview.job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限查看此面试记录")
    
    job_info = db.query(Job).filter(Job.id == interview.job_id).first()
    candidate_name = current_user.username if interview.candidate_id == current_user.id else None
    
    return InterviewDetailResponse(
        id=interview.id,
        candidate_id=interview.candidate_id,
        job_id=interview.job_id,
        status=interview.status,
        personality_traits=interview.personality_traits,
        match_score=interview.match_score,
        created_at=interview.created_at,
        completed_at=interview.completed_at,
        notes=interview.notes,
        job=job_info,
        candidate_name=candidate_name
    )

@router.get("/candidate/{candidate_id}", response_model=List[InterviewResponse])
def get_candidate_interviews(
    candidate_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取候选人的所有面试记录"""
    # 权限检查
    if candidate_id != current_user.id and not current_user.is_hr:
        raise HTTPException(status_code=403, detail="无权限查看他人面试记录")
    
    query = db.query(Interview).filter(Interview.candidate_id == candidate_id)
    
    if status:
        query = query.filter(Interview.status == status)
    
    return query.all()

@router.put("/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: int,
    update_data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新面试记录（提交面试结果）
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    
    # 权限检查：只有候选人或HR可以更新
    if interview.candidate_id != current_user.id and interview.job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限更新此面试记录")
    
    # 更新字段
    if update_data.status:
        interview.status = update_data.status
    if update_data.personality_traits:
        interview.personality_traits = update_data.personality_traits
    if update_data.match_score is not None:
        interview.match_score = update_data.match_score
    if update_data.notes:
        interview.notes = update_data.notes
    
    # 如果状态为completed，记录完成时间
    if update_data.status == "completed":
        interview.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(interview)
    
    return interview

@router.delete("/{interview_id}")
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除面试记录（只有候选人可以）"""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    
    if interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的面试记录")
    
    db.delete(interview)
    db.commit()
    
    return {"message": "面试记录已删除"}
