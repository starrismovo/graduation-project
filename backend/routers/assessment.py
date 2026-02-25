"""
评估系统 API 路由
提供心理画像、历史记录、岗位推荐、报告详情等接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db
from models.assessment import (
    AssessmentRecord, 
    CandidatePersonalityProfile, 
    AssessmentMatchAnalysis,
    PersonalityTraitDescription,
    AssessmentStatus
)
from models.hr_agent import TraitScore
from models.job import Job
from models.user import User
from schemas.assessment import (
    PortraitResponse,
    HistoryResponse,
    RecommendedJobsResponse,
    AssessmentReportResponse,
    TraitScore as TraitScoreSchema,
    TraitScoreWithDescription,
    AssessmentHistoryItem,
    JobRecommendation,
    MatchAnalysis,
    AssessmentDetails,
    AssessmentReport,
    UpdateAssessmentRequest,
    StandardResponse
)
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/assessment", tags=["assessment"])


# ============ Helper Functions ============

def calculate_job_match_score(personality_profile: CandidatePersonalityProfile, job: Job) -> float:
    """
    计算候选人与岗位的匹配度
    基于大五人格模型与岗位要求的对齐程度
    """
    if not personality_profile or not job.required_traits:
        return 50.0  # 默认分数
    
    candidate_traits = {
        "外向性": personality_profile.trait_extroversion,
        "宜人性": personality_profile.trait_agreeableness,
        "尽责性": personality_profile.trait_conscientiousness,
        "神经质": personality_profile.trait_neuroticism,
        "开放性": personality_profile.trait_openness,
    }
    
    required_traits = job.required_traits  # 期望是个 dict
    
    if not isinstance(required_traits, dict):
        return 50.0
    
    # 计算匹配度
    total_score = 0.0
    matched_count = 0
    
    for trait_name, required_score in required_traits.items():
        if trait_name in candidate_traits and candidate_traits[trait_name] is not None:
            candidate_score = candidate_traits[trait_name]
            # 差值越小，分数越高（0-10 scale）
            # 完全匹配（差值为0）= 10分
            # 最大差值（差值为10）= 0分
            similarity = 10 - abs(candidate_score - required_score)
            total_score += similarity
            matched_count += 1
    
    if matched_count == 0:
        return 50.0
    
    # 转换为百分比
    average_score = (total_score / matched_count)  # 0-10
    match_score = average_score * 10  # 0-100
    
    return min(100, max(0, match_score))


def aggregate_personality_profile(candidate_id: str, db: Session) -> Optional[CandidatePersonalityProfile]:
    """
    从最新的评估记录聚合候选人的心理特质
    """
    # 获取候选人最新的已完成评估记录
    latest_record = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate_id,
        AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED
    ).order_by(desc(AssessmentRecord.created_at)).first()
    
    if not latest_record:
        return None
    
    # 从 TraitScore 表中查询该记录的评分
    trait_scores = db.query(TraitScore).filter(
        TraitScore.candidate_id == candidate_id
    ).all()
    
    if not trait_scores:
        return None
    
    # 聚合评分（按特质求平均）
    traits_dict = {}
    trait_counts = {}
    
    for score in trait_scores:
        trait_name = score.trait_name
        score_value = score.score
        
        if trait_name not in traits_dict:
            traits_dict[trait_name] = 0.0
            trait_counts[trait_name] = 0
        
        traits_dict[trait_name] += score_value
        trait_counts[trait_name] += 1
    
    # 计算平均分
    for trait_name in traits_dict:
        traits_dict[trait_name] /= trait_counts[trait_name]
    
    # 映射到 Big Five 模型
    profile = db.query(CandidatePersonalityProfile).filter_by(
        candidate_id=candidate_id
    ).first()
    
    if not profile:
        profile = CandidatePersonalityProfile(candidate_id=candidate_id)
        db.add(profile)
    
    # 更新评分
    profile.trait_extroversion = traits_dict.get("外向性")
    profile.trait_agreeableness = traits_dict.get("宜人性")
    profile.trait_conscientiousness = traits_dict.get("尽责性")
    profile.trait_neuroticism = traits_dict.get("神经质")
    profile.trait_openness = traits_dict.get("开放性")
    profile.latest_assessment_id = latest_record.id
    profile.assessment_count = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate_id,
        AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED
    ).count()
    
    db.commit()
    db.refresh(profile)
    return profile


# ============ API Endpoints ============

@router.get("/portrait/{candidate_id}", response_model=PortraitResponse)
async def get_portrait(candidate_id: str, db: Session = Depends(get_db)):
    """
    获取候选人的心理画像
    返回五大人格特质的评分
    
    - **candidate_id**: 候选人ID
    - **返回**: 五大人格特质及评分
    """
    profile = db.query(CandidatePersonalityProfile).filter_by(
        candidate_id=candidate_id
    ).first()
    
    if not profile or not any([
        profile.trait_extroversion,
        profile.trait_agreeableness,
        profile.trait_conscientiousness,
        profile.trait_neuroticism,
        profile.trait_openness
    ]):
        # 新用户，返回空数组
        return PortraitResponse(data=[])
    
    # 转换为响应格式
    data = profile.to_dict()
    return PortraitResponse(data=data)


@router.get("/history/{candidate_id}", response_model=HistoryResponse)
async def get_history(
    candidate_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    获取候选人的历史评估记录
    
    - **candidate_id**: 候选人ID
    - **limit**: 返回的最大记录数（默认10）
    - **offset**: 分页偏移量（默认0）
    - **返回**: 按时间倒序的评估历史
    """
    records = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate_id
    ).order_by(
        desc(AssessmentRecord.created_at)
    ).offset(offset).limit(limit).all()
    
    data = [
        AssessmentHistoryItem(
            id=record.id,
            job_id=record.job_id,
            job_title=record.job_title,
            match_score=record.match_score,
            created_at=record.created_at,
            assessment_status=record.assessment_status.value if record.assessment_status else "pending",
            assessment_mode=record.assessment_mode
        )
        for record in records
    ]
    
    return HistoryResponse(data=data)


@router.get("/recommended-jobs/{candidate_id}", response_model=RecommendedJobsResponse)
async def get_recommended_jobs(
    candidate_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    获取为候选人推荐的岗位
    基于候选人的心理特质与岗位胜任力模型匹配
    
    - **candidate_id**: 候选人ID
    - **limit**: 返回的推荐岗位数（默认5）
    - **返回**: 按匹配度排序的岗位列表
    """
    profile = db.query(CandidatePersonalityProfile).filter_by(
        candidate_id=candidate_id
    ).first()
    
    # 获取所有岗位
    jobs = db.query(Job).all()
    
    if not profile or not any([
        profile.trait_extroversion,
        profile.trait_agreeableness,
        profile.trait_conscientiousness,
        profile.trait_neuroticism,
        profile.trait_openness
    ]):
        # 新用户或没有评估，返回热门岗位
        popular_jobs = jobs[:limit]
        data = [
            JobRecommendation(
                id=job.id,
                title=job.name,
                description=job.description,
                department=job.category,
                level="P6",  # 默认级别
                match_score=75.0,
                match_reason="热门推荐岗位"
            )
            for job in popular_jobs
        ]
        return RecommendedJobsResponse(data=data)
    
    # 计算匹配度并排序
    job_scores = []
    for job in jobs:
        match_score = calculate_job_match_score(profile, job)
        job_scores.append((job, match_score))
    
    # 按匹配度降序排序
    job_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 获取top N
    top_jobs = job_scores[:limit]
    
    match_reasons = {
        "外向性": "沟通与团队协作能力",
        "宜人性": "合作与人际关系处理能力",
        "尽责性": "责任心与执行力",
        "神经质": "情绪管理与抗压能力",
        "开放性": "学习能力与创新思维"
    }
    
    data = [
        JobRecommendation(
            id=job.id,
            title=job.name,
            description=job.description,
            department=job.category,
            level="P6",  # 默认级别
            match_score=score,
            match_reason=f"综合能力与岗位要求高度匹配"
        )
        for job, score in top_jobs
    ]
    
    return RecommendedJobsResponse(data=data)


@router.get("/report/{record_id}", response_model=AssessmentReportResponse)
async def get_report(record_id: int, db: Session = Depends(get_db)):
    """
    获取评估报告详情
    包含完整的心理特质、匹配分析、建议等
    
    - **record_id**: 评估记录ID
    - **返回**: 完整的评估报告
    """
    record = db.query(AssessmentRecord).filter_by(id=record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    
    # 获取特质描述
    trait_descriptions = db.query(PersonalityTraitDescription).filter_by(
        assessment_record_id=record_id
    ).all()
    
    personality_traits = [
        TraitScoreWithDescription(
            name=td.trait_name,
            score=td.score,
            description=td.description
        )
        for td in trait_descriptions
    ]
    
    # 如果没有描述，从候选人聚合数据生成
    if not personality_traits:
        profile = db.query(CandidatePersonalityProfile).filter_by(
            candidate_id=record.candidate_id
        ).first()
        
        if profile:
            personality_traits = profile.to_dict()
            # 转换为 TraitScoreWithDescription
            default_descriptions = {
                "外向性": "个人在社交互动和人际关系中的倾向程度",
                "宜人性": "个人与他人合作和妥协的倾向程度",
                "尽责性": "个人的组织性、自律性和责任意识程度",
                "神经质": "个人处理应激和压力的能力程度",
                "开放性": "个人对新经验和创意的开放程度"
            }
            
            personality_traits = [
                TraitScoreWithDescription(
                    name=t["name"],
                    score=t["score"],
                    description=default_descriptions.get(t["name"])
                )
                for t in personality_traits
            ]
    
    # 获取匹配分析
    match_analysis_record = db.query(AssessmentMatchAnalysis).filter_by(
        assessment_record_id=record_id
    ).first()
    
    match_analysis = None
    recommendations = []
    
    if match_analysis_record:
        match_analysis = MatchAnalysis(
            strengths=match_analysis_record.strengths or [],
            gaps=match_analysis_record.gaps or []
        )
        recommendations = match_analysis_record.recommendations or []
    
    # 构建响应
    details = AssessmentDetails(
        total_rounds=record.total_rounds,
        duration_minutes=record.duration_minutes,
        conversation_depth=record.conversation_depth,
        roles_participated=record.roles_participated,
        overall_impression=record.overall_impression
    )
    
    report = AssessmentReport(
        id=record.id,
        candidate_id=record.candidate_id,
        job_id=record.job_id,
        job_title=record.job_title,
        match_score=record.match_score,
        created_at=record.created_at,
        updated_at=record.updated_at,
        assessment_mode=record.assessment_mode,
        personality_trait=personality_traits,
        conversation_summary=record.conversation_summary,
        match_analysis=match_analysis,
        recommendations=recommendations,
        assessement_details=details  # 注意 typo 保持与前端一致
    )
    
    return AssessmentReportResponse(data=report)


# ============ Admin APIs (用于 HR 后台管理) ============

@router.post("/records", response_model=StandardResponse)
async def create_assessment_record(
    candidate_id: str,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    创建新的评估记录
    """
    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    record = AssessmentRecord(
        candidate_id=candidate_id,
        job_id=job_id,
        job_title=job.name,
        assessment_status=AssessmentStatus.PENDING
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return StandardResponse(
        code=200,
        message="success",
        data={"record_id": record.id, "status": "pending"}
    )


@router.patch("/records/{record_id}", response_model=StandardResponse)
async def update_assessment_record(
    record_id: int,
    data: UpdateAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    更新评估记录（通常由 AI Agent 调用）
    """
    record = db.query(AssessmentRecord).filter_by(id=record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    
    # 更新基本信息
    if data.assessment_status:
        record.assessment_status = AssessmentStatus(data.assessment_status)
    if data.match_score is not None:
        record.match_score = data.match_score
    if data.conversation_summary is not None:
        record.conversation_summary = data.conversation_summary
    if data.total_rounds is not None:
        record.total_rounds = data.total_rounds
    if data.duration_minutes is not None:
        record.duration_minutes = data.duration_minutes
    if data.conversation_depth is not None:
        record.conversation_depth = data.conversation_depth
    if data.roles_participated is not None:
        record.roles_participated = data.roles_participated
    if data.overall_impression is not None:
        record.overall_impression = data.overall_impression
    
    record.updated_at = datetime.utcnow()
    
    # 更新或创建匹配分析
    if data.strengths or data.gaps or data.recommendations:
        analysis = db.query(AssessmentMatchAnalysis).filter_by(
            assessment_record_id=record_id
        ).first()
        
        if not analysis:
            analysis = AssessmentMatchAnalysis(
                assessment_record_id=record_id
            )
            db.add(analysis)
        
        if data.strengths:
            analysis.strengths = data.strengths
        if data.gaps:
            analysis.gaps = data.gaps
        if data.recommendations:
            analysis.recommendations = data.recommendations
    
    # 更新候选人心理特质
    if data.personality_traits:
        profile = db.query(CandidatePersonalityProfile).filter_by(
            candidate_id=record.candidate_id
        ).first()
        
        if not profile:
            profile = CandidatePersonalityProfile(candidate_id=record.candidate_id)
            db.add(profile)
        
        if "外向性" in data.personality_traits:
            profile.trait_extroversion = data.personality_traits["外向性"]
        if "宜人性" in data.personality_traits:
            profile.trait_agreeableness = data.personality_traits["宜人性"]
        if "尽责性" in data.personality_traits:
            profile.trait_conscientiousness = data.personality_traits["尽责性"]
        if "神经质" in data.personality_traits:
            profile.trait_neuroticism = data.personality_traits["神经质"]
        if "开放性" in data.personality_traits:
            profile.trait_openness = data.personality_traits["开放性"]
        
        profile.updated_at = datetime.utcnow()
    
    db.commit()
    
    return StandardResponse(
        code=200,
        message="success",
        data={"record_id": record_id}
    )


@router.delete("/records/{record_id}", response_model=StandardResponse)
async def delete_assessment_record(record_id: int, db: Session = Depends(get_db)):
    """
    删除评估记录（仅管理员）
    """
    record = db.query(AssessmentRecord).filter_by(id=record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="评估记录不存在")
    
    # 删除相关的分析数据
    db.query(AssessmentMatchAnalysis).filter_by(assessment_record_id=record_id).delete()
    db.query(PersonalityTraitDescription).filter_by(assessment_record_id=record_id).delete()
    
    db.delete(record)
    db.commit()
    
    return StandardResponse(
        code=200,
        message="success"
    )
