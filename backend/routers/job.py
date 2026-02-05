from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.job import Job
from models.interview import Interview
from schemas.schemas import (
    JobCreate, JobResponse, JobCardResponse,
    InterviewStatsResponse, HomeDataResponse
)
from typing import List, Optional
from sqlalchemy import and_

router = APIRouter(prefix="/jobs", tags=["岗位管理"])

# 依赖：获取当前登录用户（后续改成真实 JWT 验证）
def get_current_user(db: Session = Depends(get_db)):
    # 演示用：假设当前是 id=1 的用户
    return db.query(User).filter(User.id == 1).first()

@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """HR创建岗位"""
    if not current_user or not current_user.is_hr:
        raise HTTPException(status_code=403, detail="只有HR可以创建岗位")
    
    new_job = Job(
        name=job.name,
        description=job.description,
        company=job.company,
        category=job.category,
        city=job.city,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        required_traits=job.required_traits,
        creator_id=current_user.id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/", response_model=List[JobResponse])
def get_jobs(
    category: Optional[str] = Query(None, description="岗位类别"),
    city: Optional[str] = Query(None, description="工作城市"),
    salary_min: Optional[float] = Query(None, description="最低薪资"),
    salary_max: Optional[float] = Query(None, description="最高薪资"),
    db: Session = Depends(get_db)
):
    """获取岗位列表（支持筛选）"""
    query = db.query(Job)
    
    if category:
        query = query.filter(Job.category == category)
    if city:
        query = query.filter(Job.city == city)
    if salary_min:
        query = query.filter(Job.salary_max >= salary_min)
    if salary_max:
        query = query.filter(Job.salary_min <= salary_max)
    
    return query.all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取岗位详情"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return job

@router.get("/recommended/cards", response_model=List[JobCardResponse])
def get_recommended_jobs(
    category: Optional[str] = Query(None, description="岗位类别"),
    city: Optional[str] = Query(None, description="工作城市"),
    salary_range: Optional[str] = Query(None, description="薪资范围 e.g. 15k-20k"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取推荐岗位卡片（用于前端主页展示）
    支持筛选条件
    """
    query = db.query(Job)
    
    # 应用筛选条件
    if category:
        query = query.filter(Job.category == category)
    if city:
        query = query.filter(Job.city == city)
    
    # 解析薪资范围
    if salary_range:
        try:
            min_salary, max_salary = salary_range.split('-')
            min_salary = float(min_salary.replace('k', ''))
            max_salary = float(max_salary.replace('k', ''))
            query = query.filter(
                and_(Job.salary_min >= min_salary, Job.salary_max <= max_salary)
            )
        except:
            pass
    
    jobs = query.limit(6).all()  # 最多返回6个推荐岗位
    
    # 转换为前端卡片格式
    result = []
    for job in jobs:
        # 检查当前用户是否已对该岗位面试
        applied = db.query(Interview).filter(
            and_(
                Interview.candidate_id == current_user.id,
                Interview.job_id == job.id
            )
        ).first() is not None
        
        result.append(JobCardResponse(
            id=job.id,
            name=job.name,
            company=job.company,
            city=job.city,
            category=job.category,
            salary=f"{int(job.salary_min)}k-{int(job.salary_max)}k",
            description=job.description,
            applied=applied
        ))
    
    return result

@router.get("/stats/candidate", response_model=InterviewStatsResponse)
def get_interview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取候选人的面试统计信息"""
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")
    
    # 查询当前用户的所有面试
    interviews = db.query(Interview).filter(
        Interview.candidate_id == current_user.id
    ).all()
    
    completed = sum(1 for i in interviews if i.status == "completed")
    in_progress = sum(1 for i in interviews if i.status == "in_progress")
    passed = sum(1 for i in interviews if i.status == "passed")
    
    return InterviewStatsResponse(
        completed=completed,
        in_progress=in_progress,
        total=len(interviews),
        passed=passed
    )

@router.get("/home/data", response_model=HomeDataResponse)
def get_home_page_data(
    category: Optional[str] = Query(None, description="岗位类别筛选"),
    city: Optional[str] = Query(None, description="城市筛选"),
    salary_range: Optional[str] = Query(None, description="薪资范围筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取主页所需的所有数据（整合版）
    包括：统计信息 + 推荐岗位
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")
    
    # 1. 获取统计信息
    interviews = db.query(Interview).filter(
        Interview.candidate_id == current_user.id
    ).all()
    
    stats = InterviewStatsResponse(
        completed=sum(1 for i in interviews if i.status == "completed"),
        in_progress=sum(1 for i in interviews if i.status == "in_progress"),
        total=len(interviews),
        passed=sum(1 for i in interviews if i.status == "passed")
    )
    
    # 2. 获取推荐岗位
    query = db.query(Job)
    
    if category:
        query = query.filter(Job.category == category)
    if city:
        query = query.filter(Job.city == city)
    
    if salary_range:
        try:
            min_salary, max_salary = salary_range.split('-')
            min_salary = float(min_salary.replace('k', ''))
            max_salary = float(max_salary.replace('k', ''))
            query = query.filter(
                and_(Job.salary_min >= min_salary, Job.salary_max <= max_salary)
            )
        except:
            pass
    
    jobs = query.limit(6).all()
    
    recommended_jobs = []
    for job in jobs:
        applied = db.query(Interview).filter(
            and_(
                Interview.candidate_id == current_user.id,
                Interview.job_id == job.id
            )
        ).first() is not None
        
        recommended_jobs.append(JobCardResponse(
            id=job.id,
            name=job.name,
            company=job.company,
            city=job.city,
            category=job.category,
            salary=f"{int(job.salary_min)}k-{int(job.salary_max)}k",
            description=job.description,
            applied=applied
        ))
    
    return HomeDataResponse(
        stats=stats,
        recommended_jobs=recommended_jobs,
        user_username=current_user.username,
        user_is_hr=current_user.is_hr
    )
