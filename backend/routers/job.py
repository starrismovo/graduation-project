from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.job import Job
from models.interview import Interview
from models.assessment import AssessmentRecord, CandidatePersonalityProfile, AssessmentStatus
from models.evaluation_framework import EvaluationFramework
from models.job_requirement import JobRequirementTag, JobSkillRequirement, JobPersonalityFramework, CandidateJobApplication
from models.hr_invitation import HRInvitation
from models.saved_job import SavedJob
from schemas.schemas import (
    JobCreate, JobResponse, JobCardResponse,
    InterviewStatsResponse, HomeDataResponse
)
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func
from routers.user import get_current_user

router = APIRouter(prefix="/jobs", tags=["岗位管理"])

TRAIT_KEY_ALIASES = {
    "openness": "openness",
    "开放性": "openness",
    "conscientiousness": "conscientiousness",
    "尽责性": "conscientiousness",
    "extraversion": "extraversion",
    "外向性": "extraversion",
    "agreeableness": "agreeableness",
    "宜人性": "agreeableness",
    "neuroticism": "neuroticism",
    "神经质": "neuroticism",
}


def _normalize_job_traits(required_traits: Optional[Dict[str, Any]]) -> Dict[str, float]:
    normalized: Dict[str, float] = {}
    for raw_key, raw_value in (required_traits or {}).items():
        key = TRAIT_KEY_ALIASES.get(str(raw_key))
        if not key:
            continue
        try:
            normalized[key] = float(raw_value)
        except (TypeError, ValueError):
            continue
    return normalized


def _profile_traits(profile: Optional[CandidatePersonalityProfile]) -> Dict[str, float]:
    if not profile:
        return {}
    traits = {
        "extraversion": profile.trait_extroversion,
        "agreeableness": profile.trait_agreeableness,
        "conscientiousness": profile.trait_conscientiousness,
        "neuroticism": profile.trait_neuroticism,
        "openness": profile.trait_openness,
    }
    return {key: float(value) for key, value in traits.items() if value is not None}


def _calculate_trait_match(job_traits: Dict[str, float], candidate_traits: Dict[str, float]) -> float:
    if not job_traits or not candidate_traits:
        return 0.0

    scores: List[float] = []
    for key, job_value in job_traits.items():
        candidate_value = candidate_traits.get(key)
        if candidate_value is None:
            continue
        # 0-10 分制差距映射到 0-100 的接近度。
        closeness = max(0.0, 100 - abs(job_value - candidate_value) * 10)
        scores.append(closeness)

    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 1)


def _build_recommendation_reasons(
    recommendation_score: float,
    trait_match_score: float,
    source_match_score: float,
    source_job_title: str,
) -> List[str]:
    reasons = [f"该候选人在“{source_job_title}”岗位已有 {source_match_score}% 的历史评估结果。"]

    if trait_match_score > 0:
        reasons.append(f"候选人的人格画像与当前岗位画像匹配度约为 {trait_match_score}%。")

    if recommendation_score >= 85:
        reasons.append("综合分较高，建议优先邀请进入当前岗位评估流程。")
    elif recommendation_score >= 70:
        reasons.append("综合分稳定，可作为当前岗位的重点复用候选人。")
    else:
        reasons.append("可作为补充候选人进入当前岗位候选池进一步观察。")

    return reasons

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
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(50, ge=1, le=200, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取岗位列表（支持筛选与分页）。HR 只能看自己创建的岗位，候选人可浏览全部。"""
    query = db.query(Job)

    # HR 只查自己的岗位
    if current_user.is_hr or getattr(current_user, 'is_hr_user', False):
        query = query.filter(Job.creator_id == current_user.id)

    if category:
        query = query.filter(Job.category == category)
    if city:
        query = query.filter(Job.city == city)
    if salary_min:
        query = query.filter(Job.salary_max >= salary_min)
    if salary_max:
        query = query.filter(Job.salary_min <= salary_max)

    return query.offset(skip).limit(limit).all()

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
    sort_by: str = Query("latest", regex="^(latest|recommended|salary_high|salary_low)$", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(12, ge=1, le=48, description="每页数量"),
    db: Session = Depends(get_db)
):
    """搜索岗位（支持关键词、筛选、排序、分页）"""
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
    
    # 总数（在排序前获取）
    total = query.count()
    
    # 排序
    if sort_by == "salary_high":
        # 按薪资最高值降序
        query = query.order_by(Job.salary_max.desc().nullslast(), Job.salary_min.desc().nullslast())
    elif sort_by == "salary_low":
        # 按薪资最低值升序
        query = query.order_by(Job.salary_min, Job.salary_max)
    elif sort_by == "recommended":
        # 按 match_score 或推荐指数排序（需要关联性数据）
        # 暂时按 ID 倒序（最新的假定为推荐的）
        query = query.order_by(Job.id.desc())
    else:  # latest
        # 按最新发布时间（使用 ID 作为代理）
        query = query.order_by(Job.id.desc())
    
    # 分页
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
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


@router.get("/hr/list")
def get_hr_job_list(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(20, ge=1, le=200, description="每页条数"),
    search: Optional[str] = Query(None, description="按岗位名搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HR专用岗位列表，含投递数、平均匹配度、待处理报告统计"""
    if not (current_user.is_hr or getattr(current_user, 'is_hr_user', False)):
        raise HTTPException(status_code=403, detail="仅HR可访问")

    # 子查询：每个岗位的总投递数
    applications_sq = (
        db.query(Interview.job_id, func.count(Interview.id).label('cnt'))
        .filter(Interview.is_deleted == False)
        .group_by(Interview.job_id)
        .subquery()
    )
    # 子查询：每个岗位的平均匹配分
    avg_sq = (
        db.query(Interview.job_id, func.avg(Interview.match_score).label('avg_score'))
        .filter(Interview.is_deleted == False, Interview.match_score.isnot(None))
        .group_by(Interview.job_id)
        .subquery()
    )
    # 子查询：每个岗位待处理报告数（已完成但HR未阅）
    pending_sq = (
        db.query(Interview.job_id, func.count(Interview.id).label('pending'))
        .filter(Interview.is_deleted == False, Interview.status == 'completed')
        .group_by(Interview.job_id)
        .subquery()
    )

    query = (
        db.query(
            Job,
            func.coalesce(applications_sq.c.cnt, 0).label('applications'),
            func.coalesce(avg_sq.c.avg_score, 0).label('avg_match'),
            func.coalesce(pending_sq.c.pending, 0).label('pending_reports'),
        )
        .outerjoin(applications_sq, Job.id == applications_sq.c.job_id)
        .outerjoin(avg_sq, Job.id == avg_sq.c.job_id)
        .outerjoin(pending_sq, Job.id == pending_sq.c.job_id)
        .filter(Job.creator_id == current_user.id)
    )

    if search:
        query = query.filter(Job.name.ilike(f'%{search}%'))

    total = query.count()
    rows = query.order_by(Job.id.desc()).offset(skip).limit(limit).all()

    items = []
    for row in rows:
        job = row[0]
        items.append({
            'id': job.id,
            'name': job.name,
            'company': job.company,
            'category': job.category,
            'city': job.city,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'description': job.description,
            'applications': int(row[1]),
            'avg_match_rate': round(float(row[2]), 1) if row[2] else 0,
            'pending_reports': int(row[3]),
            'status': 'active',
        })

    # 汇总统计
    total_applications = sum(i['applications'] for i in items)
    avg_match = round(sum(i['avg_match_rate'] for i in items) / len(items), 1) if items else 0
    total_pending = sum(i['pending_reports'] for i in items)

    return {
        'total': total,
        'items': items,
        'summary': {
            'open_jobs': total,
            'total_applications': total_applications,
            'avg_match_rate': avg_match,
            'pending_reports': total_pending,
        }
    }


@router.get("/hr/{job_id}/recommended-candidates")
def get_hr_recommended_candidates(
    job_id: int,
    limit: int = Query(8, ge=1, le=30, description="返回推荐候选人数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HR 按岗位获取跨岗位/跨候选池的候选人推荐"""
    if not (current_user.is_hr or getattr(current_user, 'is_hr_user', False)):
        raise HTTPException(status_code=403, detail="仅HR可访问")

    job = db.query(Job).filter(Job.id == job_id, Job.creator_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在或无权限访问")

    target_job_traits = _normalize_job_traits(job.required_traits)

    existing_candidate_ids = {
        candidate_id
        for (candidate_id,) in db.query(AssessmentRecord.candidate_id)
        .filter(
            AssessmentRecord.job_id == job_id,
            AssessmentRecord.is_deleted == False,
        )
        .distinct()
        .all()
    }

    existing_invitation_status = {
        inv.candidate_id: inv.status.value if hasattr(inv.status, 'value') else str(inv.status)
        for inv in db.query(HRInvitation)
        .filter(HRInvitation.hr_id == current_user.id, HRInvitation.job_id == job_id)
        .all()
    }

    rows = (
        db.query(AssessmentRecord, User, CandidatePersonalityProfile)
        .join(User, AssessmentRecord.candidate_id == User.id)
        .outerjoin(CandidatePersonalityProfile, CandidatePersonalityProfile.candidate_id == AssessmentRecord.candidate_id)
        .filter(
            AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED,
            AssessmentRecord.is_deleted == False,
            AssessmentRecord.job_id != job_id,
        )
        .order_by(func.coalesce(AssessmentRecord.match_score, -1).desc(), AssessmentRecord.created_at.desc())
        .all()
    )

    recommended_by_candidate: Dict[int, Dict[str, Any]] = {}
    for record, candidate, profile in rows:
        candidate_id = int(record.candidate_id)
        if candidate_id in existing_candidate_ids:
            continue

        profile_traits = _profile_traits(profile)
        trait_match_score = _calculate_trait_match(target_job_traits, profile_traits)
        source_match_score = round(float(record.match_score or 0), 1)

        if trait_match_score > 0:
            recommendation_score = round(source_match_score * 0.55 + trait_match_score * 0.45, 1)
        else:
            recommendation_score = source_match_score

        candidate_name = candidate.real_name or candidate.nickname or candidate.username
        candidate_email = candidate.email
        existing = recommended_by_candidate.get(candidate_id)
        if existing and existing["recommendation_score"] >= recommendation_score:
            continue

        recommended_by_candidate[candidate_id] = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "record_id": record.id,
            "source_job_id": record.job_id,
            "source_job_title": record.job_title,
            "source_match_score": source_match_score,
            "trait_match_score": trait_match_score,
            "recommendation_score": recommendation_score,
            "assessment_mode": record.assessment_mode,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "invite_status": existing_invitation_status.get(candidate_id),
            "recommendation_reasons": _build_recommendation_reasons(
                recommendation_score,
                trait_match_score,
                source_match_score,
                record.job_title,
            ),
        }

    items = sorted(
        recommended_by_candidate.values(),
        key=lambda item: (item["recommendation_score"], item["source_match_score"]),
        reverse=True,
    )[:limit]

    return {
        "job_id": job.id,
        "job_name": job.name,
        "total": len(items),
        "items": items,
    }


# 注意：动态路径参数路由必须放在所有固定路径路由之后
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取岗位详情"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HR编辑岗位信息"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    if job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能编辑自己创建的岗位")

    job.name = job_data.name
    job.description = job_data.description
    job.company = job_data.company
    job.category = job_data.category
    job.city = job_data.city
    job.salary_min = job_data.salary_min
    job.salary_max = job_data.salary_max
    if job_data.required_traits is not None:
        job.required_traits = job_data.required_traits

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """HR删除岗位（显式清理子表，避免懒加载/外键约束问题）"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    if job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己创建的岗位")

    # 按依赖顺序显式删除子表记录，避免 ORM 懒加载触发 MissingGreenlet 错误
    db.query(SavedJob).filter(SavedJob.job_id == job_id).delete(synchronize_session=False)
    db.query(CandidateJobApplication).filter(CandidateJobApplication.job_id == job_id).delete(synchronize_session=False)
    db.query(HRInvitation).filter(HRInvitation.job_id == job_id).delete(synchronize_session=False)
    db.query(JobRequirementTag).filter(JobRequirementTag.job_id == job_id).delete(synchronize_session=False)
    db.query(JobSkillRequirement).filter(JobSkillRequirement.job_id == job_id).delete(synchronize_session=False)
    db.query(JobPersonalityFramework).filter(JobPersonalityFramework.job_id == job_id).delete(synchronize_session=False)
    db.query(EvaluationFramework).filter(EvaluationFramework.job_id == job_id).delete(synchronize_session=False)
    db.query(Interview).filter(Interview.job_id == job_id).delete(synchronize_session=False)
    db.query(Job).filter(Job.id == job_id).delete(synchronize_session=False)
    db.commit()
    return {"message": "岗位已删除", "id": job_id}

