"""
心动岗位（收藏岗位）API 路由
用于管理候选人的收藏岗位列表
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from database import get_db
from models.saved_job import SavedJob
from models.user import User, UserType
from models.job import Job
from schemas.saved_job import SavedJobResponse, SavedJobListResponse
from typing import Optional
from datetime import datetime, time

router = APIRouter(prefix="/api/saved-jobs", tags=["saved-jobs"])


def format_job_salary(job: Job) -> Optional[str]:
    """统一岗位薪资展示。"""
    if job.salary_min is None or job.salary_max is None:
        return None
    return f"{job.salary_min}k-{job.salary_max}k"


def get_current_user(db: Session = Depends(get_db), candidate_id: Optional[int] = None) -> User:
    """
    验证候选人身份（简化版，实际应从 token 获取）
    """
    if not candidate_id:
        raise HTTPException(status_code=400, detail="候选人 ID 不能为空")
    
    user = db.query(User).filter(
        User.id == candidate_id,
        User.user_type == UserType.CANDIDATE
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="未授权的候选人")
    
    return user


@router.post("/{candidate_id}/add/{job_id}", response_model=SavedJobResponse)
async def add_saved_job(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    添加心动岗位
    
    Args:
        candidate_id: 候选人 ID
        job_id: 岗位 ID
    
    Returns:
        SavedJobResponse: 新保存的岗位信息
    """
    # 验证候选人和岗位
    get_current_user(db, candidate_id)
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 检查是否已经收藏过
    existing = db.query(SavedJob).filter(
        SavedJob.candidate_id == candidate_id,
        SavedJob.job_id == job_id
    ).first()
    
    if existing:
        return SavedJobResponse(
            id=existing.id,
            candidate_id=existing.candidate_id,
            job_id=existing.job_id,
            job_name=job.name,
            company=job.company,
            salary=format_job_salary(job),
            city=job.city,
            saved_at=existing.saved_at
        )
    
    # 创建新的收藏记录
    saved_job = SavedJob(
        candidate_id=candidate_id,
        job_id=job_id
    )
    db.add(saved_job)
    db.commit()
    db.refresh(saved_job)
    
    return SavedJobResponse(
        id=saved_job.id,
        candidate_id=saved_job.candidate_id,
        job_id=saved_job.job_id,
        job_name=job.name,
        company=job.company,
        salary=format_job_salary(job),
        city=job.city,
        saved_at=saved_job.saved_at
    )


@router.delete("/{candidate_id}/remove/{job_id}")
async def remove_saved_job(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    移除心动岗位
    
    Args:
        candidate_id: 候选人 ID
        job_id: 岗位 ID
    
    Returns:
        dict: 删除结果
    """
    get_current_user(db, candidate_id)
    
    saved_job = db.query(SavedJob).filter(
        SavedJob.candidate_id == candidate_id,
        SavedJob.job_id == job_id
    ).first()
    
    if not saved_job:
        raise HTTPException(status_code=404, detail="未找到此收藏岗位")
    
    db.delete(saved_job)
    db.commit()
    
    return {"message": "已删除收藏岗位", "job_id": job_id}


@router.get("/{candidate_id}", response_model=SavedJobListResponse)
async def get_saved_jobs(
    candidate_id: int,
    sort_by: str = Query("latest", pattern="^(latest|salary_high|salary_low)$"),
    db: Session = Depends(get_db)
):
    """
    获取候选人的心动岗位列表
    
    Args:
        candidate_id: 候选人 ID
        sort_by: 排序方式 - latest(最新), salary_high(高薪), salary_low(低薪)
    
    Returns:
        SavedJobListResponse: 收藏岗位列表
    """
    get_current_user(db, candidate_id)
    
    # 获取收藏的岗位
    query = db.query(SavedJob).filter(SavedJob.candidate_id == candidate_id)
    
    # 排序
    if sort_by == "salary_high":
        query = query.join(Job).order_by(desc(func.coalesce(Job.salary_max, Job.salary_min, 0)))
    elif sort_by == "salary_low":
        query = query.join(Job).order_by(asc(func.coalesce(Job.salary_min, Job.salary_max, 0)))
    else:  # latest
        query = query.order_by(desc(SavedJob.saved_at))
    
    saved_jobs = query.all()
    
    # 构建响应
    items = []
    for saved_job in saved_jobs:
        job = saved_job.job
        items.append(SavedJobResponse(
            id=saved_job.id,
            candidate_id=saved_job.candidate_id,
            job_id=saved_job.job_id,
            job_name=job.name,
            company=job.company,
            salary=format_job_salary(job),
            city=job.city,
            saved_at=saved_job.saved_at
        ))
    
    return SavedJobListResponse(
        total=len(items),
        items=items
    )


@router.get("/{candidate_id}/check/{job_id}")
async def check_saved_job(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    检查某个岗位是否已被收藏
    
    Args:
        candidate_id: 候选人 ID
        job_id: 岗位 ID
    
    Returns:
        dict: 是否已收藏
    """
    get_current_user(db, candidate_id)
    
    saved_job = db.query(SavedJob).filter(
        SavedJob.candidate_id == candidate_id,
        SavedJob.job_id == job_id
    ).first()
    
    return {"is_saved": saved_job is not None}


@router.get("/{candidate_id}/stats")
async def get_saved_jobs_stats(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    获取候选人心动岗位的统计信息
    
    Returns:
        dict: 统计数据
    """
    get_current_user(db, candidate_id)
    
    total = db.query(SavedJob).filter(
        SavedJob.candidate_id == candidate_id
    ).count()
    
    # 今天新增的
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, time.min)
    today_count = db.query(SavedJob).filter(
        SavedJob.candidate_id == candidate_id,
        SavedJob.saved_at >= today_start
    ).count()
    
    return {
        "total": total,
        "today_added": today_count
    }
