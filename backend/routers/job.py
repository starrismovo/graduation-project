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
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func
from routers.user import get_current_user

router = APIRouter(prefix="/jobs", tags=["岗位管理"])

@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """HR创建岗位"""
    if not current_user or (not current_user.is_hr and not getattr(current_user, 'is_hr_user', False)):
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


@router.get("/filters")
def get_job_filters(db: Session = Depends(get_db)):
    """获取岗位筛选选项（城市列表和类别列表）"""
    cities = db.query(Job.city).distinct().order_by(
        func.count(Job.id).desc()
    ).group_by(Job.city).limit(50).all()
    
    categories = db.query(Job.category).distinct().order_by(
        func.count(Job.id).desc()
    ).group_by(Job.category).limit(30).all()
    
    return {
        "cities": [c[0] for c in cities if c[0]],
        "categories": [c[0] for c in categories if c[0]]
    }


@router.get("/search")
def search_jobs(
    keyword: Optional[str] = Query(None, description="搜索关键词（职位名/公司/描述）"),
    city: Optional[str] = Query(None, description="城市筛选"),
    category: Optional[str] = Query(None, description="类别筛选"),
    salary_min: Optional[float] = Query(None, description="最低薪资(k)"),
    salary_max: Optional[float] = Query(None, description="最高薪资(k)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=48, description="每页数量"),
    db: Session = Depends(get_db)
):
    """搜索岗位（支持关键词、筛选、分页）"""
    query = db.query(Job)
    
    # 关键词搜索
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.name.like(like_pattern),
                Job.company.like(like_pattern),
                Job.description.like(like_pattern),
                Job.city.like(like_pattern)
            )
        )
    
    # 城市筛选
    if city:
        query = query.filter(Job.city == city)
    
    # 类别筛选
    if category:
        query = query.filter(Job.category == category)
    
    # 薪资范围筛选
    if salary_min is not None:
        query = query.filter(Job.salary_max >= salary_min)
    if salary_max is not None:
        query = query.filter(Job.salary_min <= salary_max)
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    items = query.order_by(Job.id.desc()).offset(offset).limit(page_size).all()
    
    # 格式化返回
    job_list = []
    for job in items:
        job_list.append({
            "id": job.id,
            "name": job.name,
            "company": job.company,
            "city": job.city,
            "category": job.category,
            "salary": f"{int(job.salary_min)}k-{int(job.salary_max)}k" if job.salary_min and job.salary_max else None,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description[:120] + "..." if job.description and len(job.description) > 120 else job.description,
        })
    
    return {
        "items": job_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


# 注意：动态路径参数路由必须放在所有固定路径路由之后
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取岗位详情"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return job
