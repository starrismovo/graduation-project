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
    StandardResponse,
    NextQuestionResponse,
    AnalyzeResponseRequest,
    AnalyzeResponseResponse,
    SaveSessionRequest,
    SaveSessionResponse,
    SaveAssessmentResultRequest  # 新增
)
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import json
import httpx
import logging

logger = logging.getLogger(__name__)

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


# ============ Save Assessment Result (新增端点) ============

@router.post("/save-result", response_model=StandardResponse)
async def save_assessment_result(
    request: SaveAssessmentResultRequest,
    db: Session = Depends(get_db)
):
    """
    保存评估结果并生成报告
    
    请求示例:
    {
      "candidate_id": "user_2",
      "job_id": 1,
      "assessment_mode": "immersive",
      "all_scores": {...},
      "personality_scores": {"外向性": 7, "宜人性": 6.5, ...},
      "candidate_info": {...}
    }
    """
    try:
        logger.info(f"【save-result】保存评估结果: candidate_id={request.candidate_id}, job_id={request.job_id}")
        
        # 1. 创建评估记录
        job = db.query(Job).filter_by(id=request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="岗位不存在")
        
        record = AssessmentRecord(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            job_title=job.name,
            assessment_mode=request.assessment_mode,
            assessment_status=AssessmentStatus.COMPLETED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(record)
        db.flush()
        
        logger.info(f"【save-result】评估记录已创建: record_id={record.id}")
        
        # 2. 创建或更新候选人心理画像
        personality_profile = db.query(CandidatePersonalityProfile).filter_by(
            candidate_id=request.candidate_id
        ).first()
        
        if not personality_profile:
            personality_profile = CandidatePersonalityProfile(
                candidate_id=request.candidate_id
            )
            db.add(personality_profile)
        
        # 更新五大人格评分
        personality_profile.trait_extroversion = request.personality_scores.get("外向性", request.personality_scores.get("extraversion", 5))
        personality_profile.trait_agreeableness = request.personality_scores.get("宜人性", request.personality_scores.get("agreeableness", 5))
        personality_profile.trait_conscientiousness = request.personality_scores.get("尽责性", request.personality_scores.get("conscientiousness", 5))
        personality_profile.trait_neuroticism = request.personality_scores.get("神经质", request.personality_scores.get("neuroticism", 5))
        personality_profile.trait_openness = request.personality_scores.get("开放性", request.personality_scores.get("openness", 5))
        personality_profile.latest_assessment_id = record.id
        personality_profile.updated_at = datetime.now()
        
        db.flush()
        
        logger.info(f"【save-result】心理画像已保存: {personality_profile.trait_extroversion}, {personality_profile.trait_conscientiousness}, etc")
        
        # 3. 计算岗位匹配度
        match_score = calculate_job_match_score(personality_profile, job)
        record.match_score = match_score
        
        logger.info(f"【save-result】匹配度已计算: {match_score}")
        
        # 4. 保存特质描述
        trait_names = ["外向性", "宜人性", "尽责性", "神经质", "开放性"]
        trait_descriptions = {
            "外向性": "个人在社交互动和人际关系中的倾向程度",
            "宜人性": "个人与他人合作和妥协的倾向程度",
            "尽责性": "个人的组织性、自律性和责任意识程度",
            "神经质": "个人处理应激和压力的能力程度",
            "开放性": "个人对新经验和创意的开放程度"
        }
        
        for trait_name in trait_names:
            trait_score = request.personality_scores.get(trait_name, 5)
            if trait_score:
                trait_desc = PersonalityTraitDescription(
                    assessment_record_id=record.id,
                    trait_name=trait_name,
                    score=trait_score,
                    description=trait_descriptions.get(trait_name)
                )
                db.add(trait_desc)
        
        db.flush()
        
        logger.info(f"【save-result】特质描述已保存")
        
        # 5. 生成分析和建议
        strengths = generate_default_analysis("strengths", personality_profile)
        gaps = generate_default_analysis("gaps", personality_profile)
        recommendations = generate_default_recommendations(personality_profile, job)
        
        # 6. 保存匹配分析
        match_analysis = AssessmentMatchAnalysis(
            assessment_record_id=record.id,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations
        )
        db.add(match_analysis)
        
        db.flush()
        
        logger.info(f"【save-result】分析与建议已生成")
        
        # 7. 提交事务
        db.commit()
        
        logger.info(f"【save-result】评估结果保存完成! record_id={record.id}, match_score={match_score}")
        
        return StandardResponse(
            code=200,
            message="评估结果已保存",
            data={"record_id": record.id}
        )
    except Exception as e:
        db.rollback()
        logger.error(f"【save-result】保存评估结果失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


# ============ Helper Functions for Analysis ============

def generate_default_analysis(analysis_type: str, profile: CandidatePersonalityProfile) -> List[str]:
    """生成默认的强项或改进空间分析"""
    if analysis_type == "strengths":
        analysis = []
        if profile.trait_conscientiousness and profile.trait_conscientiousness >= 7:
            analysis.append("责任心强，执行力强")
        if profile.trait_openness and profile.trait_openness >= 7:
            analysis.append("思维开放，学习能力强")
        if profile.trait_extraversion and profile.trait_extraversion >= 7:
            analysis.append("沟通能力强，团队协作意识强")
        if profile.trait_agreeableness and profile.trait_agreeableness >= 7:
            analysis.append("同理心强，合作意识强")
        if not analysis:
            analysis.append("表现均衡，基础素质扎实")
        return analysis
    else:  # gaps
        analysis = []
        if not profile.trait_conscientiousness or profile.trait_conscientiousness < 6:
            analysis.append("需要提升执行力和自律性")
        if not profile.trait_openness or profile.trait_openness < 6:
            analysis.append("建议加强学习心态和创新意识")
        if not profile.trait_extraversion or profile.trait_extraversion < 6:
            analysis.append("可以加强沟通和表达能力")
        if not profile.trait_neuroticism or profile.trait_neuroticism < 5:
            analysis.append("需要加强压力管理和情绪控制")
        if not analysis:
            analysis.append("继续保持和完善各项能力")
        return analysis


def generate_default_recommendations(profile: CandidatePersonalityProfile, job: Job) -> List[str]:
    """根据岗位生成专业建议"""
    recommendations = []
    
    # 基础建议
    recommendations.append("根据评估结果，建议职业发展方向明确")
    recommendations.append("持续提升专业技能，增强岗位胜任力")
    
    # 根据岗位类别定制
    if job.category and "engineer" in job.category.lower():
        recommendations.append("建议参加技术领导力或架构设计培训")
    elif job.category and "product" in job.category.lower():
        recommendations.append("建议加强用户研究和数据分析能力")
    elif job.category and "manager" in job.category.lower():
        recommendations.append("建议参加团队领导力或项目管理培训")
    else:
        recommendations.append("建议参加相关领域的专业培训课程")
    
    recommendations.append("定期反思和改进，制定个人发展计划")
    
    return recommendations


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


# ==================== 沉浸式对话 API ====================

async def call_llm_for_question(
    role_id: str,
    role_name: str,
    conversation_history: List[Dict[str, str]],
    candidate_background: Optional[str] = None,
    conversation_depth: Optional[int] = None
) -> Dict[str, Any]:
    """
    使用 LLM 生成下一个问题（基于角色和对话历史）
    """
    api_key = os.getenv("ROAD2ALL_API_KEY")
    api_url = os.getenv("ROAD2ALL_API_URL", "https://api.road2all.com/v1/chat/completions")
    model = os.getenv("ROAD2ALL_MODEL", "gpt4o")
    
    # 构建提示词
    role_prompts = {
        "hr": "你是一名资深的HR面试官。你需要基于候选人的背景和对话历史，提出一个自然、深入的问题。问题应该帮助了解候选人的沟通能力、团队协作和文化契合度。",
        "tech_lead": "你是一名技术总监。根据对话历史，提出一个关于技术深度、问题解决能力或系统思维的问题。",
        "product": "你是一名产品经理。提出一个关于产品思维、用户洞察或创新能力的问题。",
        "cto": "你是一名CTO。从战略和领导力的角度，提出一个深刻的问题。"
    }
    
    role_prompt = role_prompts.get(role_id, role_prompts["hr"])
    
    # 构建对话历史文本
    history_text = ""
    if conversation_history:
        for msg in conversation_history[-4:]:  # 只取最近4条
            role = msg.get("role", "").replace("role", role_name)
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"
    
    system_message = f"""{role_prompt}

对话深度: {conversation_depth or 1}/10
候选人背景: {candidate_background or '未提供'}

对话历史:
{history_text}

现在请提出下一个问题。返回格式必须是JSON:
{{
    "question": "具体的问题",
    "focus_areas": ["关注点1", "关注点2"],
    "follow_up_suggestions": ["建议回答角度1", "建议回答角度2"],
    "context_hint": "对候选人的简要提示或建议"
}}"""
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                api_url,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": "请根据上述信息生成下一个问题。"}
                    ],
                    "temperature": 0.7
                },
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code != 200:
                logger.warning(f"LLM API 返回错误: {response.status_code}")
                return _generate_fallback_question(role_id)
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 尝试解析 JSON
            try:
                question_data = json.loads(content)
                return {
                    "content": question_data.get("question", ""),
                    "tags": question_data.get("focus_areas", []),
                    "suggestions": question_data.get("follow_up_suggestions", []),
                    "context": question_data.get("context_hint")
                }
            except json.JSONDecodeError:
                # 如果无法解析 JSON，直接返回内容
                return {
                    "content": content,
                    "tags": [],
                    "suggestions": [],
                    "context": None
                }
    
    except Exception as e:
        logger.error(f"LLM API 错误: {e}")
        return _generate_fallback_question(role_id)


def _generate_fallback_question(role_id: str) -> Dict[str, Any]:
    """生成备用问题（当 LLM 不可用时）"""
    fallback_questions = {
        "hr": {
            "content": "请介绍一下你自己，包括你的工作经历和此前的成就。",
            "tags": ["背景了解", "自我认知"],
            "suggestions": ["我叫...，有...年经验", "最大的成就是..."],
            "context": "这是一个开放性问题，轻松回答即可"
        },
        "tech_lead": {
            "content": "描述一个你最近解决的复杂技术问题，以及你的解决方案。",
            "tags": ["问题解决", "技术深度"],
            "suggestions": ["遇到了...问题", "我通过...技术解决"],
            "context": "尽量具体描述技术细节"
        },
        "product": {
            "content": "如果你需要设计一个新功能，你会如何思考和规划？",
            "tags": ["产品思维", "用户洞察"],
            "suggestions": ["首先了解用户需求", "然后分析竞品"],
            "context": "展示你的产品思维过程"
        },
        "cto": {
            "content": "你对未来3-5年的职业发展有什么规划？",
            "tags": ["战略思维", "目标导向"],
            "suggestions": ["我的目标是...", "为此我计划..."],
            "context": "这是一个关键问题，认真思考"
        }
    }
    
    return fallback_questions.get(role_id, fallback_questions["hr"])


async def call_llm_for_analysis(
    role_id: str,
    speaker_name: str,
    candidate_name: str,
    candidate_response: str,
    question_asked: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用 LLM 分析候选人的回答
    返回: {scores: {...}, sentiment: {...}, patterns: [...]}
    """
    api_key = os.getenv("ROAD2ALL_API_KEY")
    api_url = os.getenv("ROAD2ALL_API_URL", "https://api.road2all.com/v1/chat/completions")
    model = os.getenv("ROAD2ALL_MODEL", "gpt4o")
    
    analysis_prompts = {
        "hr": "评估候选人的沟通能力(0-10)、团队协作(0-10)、文化契合(0-10)。",
        "tech_lead": "评估候选人的技术深度(0-10)、问题解决(0-10)、系统思维(0-10)。",
        "product": "评估候选人的产品思维(0-10)、用户洞察(0-10)、创新能力(0-10)。",
        "cto": "评估候选人的战略思维(0-10)、领导力(0-10)、决策能力(0-10)。"
    }
    
    system_message = f"""你是一名专业的招聘评估专家。
{analysis_prompts.get(role_id, analysis_prompts["hr"])}

同时分析候选人的情绪状态（自信/谨慎/积极/思考中）和回答的置信度(0-100)。

识别回答中的行为模式，如结构化思维、实例驱动、深度思考等。

候选人: {candidate_name}
提问者: {speaker_name}
提出的问题: {question_asked or '(未提供)'}
候选人的回答: {candidate_response}

返回格式必须是JSON，示例:
{{
    "scores": {{
        "项目1": 8.5,
        "项目2": 7.2
    }},
    "sentiment": {{
        "emotion": "自信",
        "confidence": 85
    }},
    "patterns": [
        {{
            "id": "p1",
            "name": "结构化思维",
            "description": "回答展现了清晰的逻辑结构",
            "confidence": 85,
            "color": "#67c23a"
        }}
    ]
}}"""
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                api_url,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": "请根据上述信息进行分析。"}
                    ],
                    "temperature": 0.7
                },
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code != 200:
                logger.warning(f"LLM API 返回错误: {response.status_code}")
                return _generate_fallback_analysis(role_id)
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            try:
                analysis_data = json.loads(content)
                return {
                    "scores": analysis_data.get("scores", {}),
                    "sentiment": analysis_data.get("sentiment", {"emotion": "思考中", "confidence": 70}),
                    "patterns": analysis_data.get("patterns", [])
                }
            except json.JSONDecodeError:
                return _generate_fallback_analysis(role_id)
    
    except Exception as e:
        logger.error(f"LLM 分析错误: {e}")
        return _generate_fallback_analysis(role_id)


def _generate_fallback_analysis(role_id: str) -> Dict[str, Any]:
    """生成备用分析（当 LLM 不可用时）"""
    trait_scores = {
        "hr": {"沟通能力": 7.5, "团队协作": 7.0, "文化契合": 7.5},
        "tech_lead": {"技术深度": 7.5, "问题解决": 8.0, "系统思维": 7.0},
        "product": {"产品思维": 7.0, "用户洞察": 7.5, "创新能力": 7.5},
        "cto": {"战略思维": 7.5, "领导力": 7.0, "决策能力": 7.5}
    }
    
    return {
        "scores": trait_scores.get(role_id, trait_scores["hr"]),
        "sentiment": {"emotion": "self-confident", "confidence": 75},
        "patterns": [
            {
                "id": "p1",
                "name": "结构化思维",
                "description": "回答展现了清晰的逻辑结构",
                "confidence": 78,
                "color": "#67c23a"
            },
            {
                "id": "p2",
                "name": "实例驱动",
                "description": "善于用具体案例支撑观点",
                "confidence": 72,
                "color": "#409eff"
            }
        ]
    }


@router.post("/immersive/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    candidate_id: str = Query(..., description="候选人ID"),
    role_id: str = Query(..., description="角色ID"),
    role_name: str = Query(..., description="角色名称"),
    conversation_depth: int = Query(1, description="对话深度 1-10"),
    candidate_background: Optional[str] = Query(None, description="候选人背景"),
    history: Optional[str] = Query(None, description="对话历史 JSON 字符串")
):
    """
    获取沉浸式对话的下一个问题
    
    - 使用 LLM 基于对话历史生成智能问题
    - 支持 HR、技术总监、产品经理、CTO 四个角色
    """
    try:
        conversation_history = []
        if history:
            try:
                conversation_history = json.loads(history)
            except:
                pass
        
        question_data = await call_llm_for_question(
            role_id=role_id,
            role_name=role_name,
            conversation_history=conversation_history,
            candidate_background=candidate_background,
            conversation_depth=conversation_depth
        )
        
        return NextQuestionResponse(
            code=200,
            message="success",
            data=question_data
        )
    
    except Exception as e:
        logger.error(f"获取问题失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/immersive/analyze-response", response_model=AnalyzeResponseResponse)
async def analyze_candidate_response(request: AnalyzeResponseRequest):
    """
    分析候选人的回答
    
    - 评估多个维度的得分
    - 分析情绪和置信度
    - 识别行为模式
    """
    try:
        analysis_result = await call_llm_for_analysis(
            role_id=request.current_speaker,
            speaker_name=request.speaker_name,
            candidate_name=request.candidate_name,
            candidate_response=request.candidate_response,
            question_asked=None
        )
        
        return AnalyzeResponseResponse(
            code=200,
            message="success",
            data=analysis_result
        )
    
    except Exception as e:
        logger.error(f"分析回答失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/immersive/save-session", response_model=SaveSessionResponse)
async def save_immersive_session(
    request: SaveSessionRequest,
    db: Session = Depends(get_db)
):
    """
    保存沉浸式对话的整个会话数据
    
    - 存储对话消息
    - 记录评分和模式
    - 创建评估记录
    """
    try:
        # 创建或更新评估记录
        assessment_record = None
        
        if request.assessment_id:
            assessment_record = db.query(AssessmentRecord).filter_by(
                id=request.assessment_id
            ).first()
        
        if not assessment_record:
            assessment_record = AssessmentRecord(
                candidate_id=request.candidate_id,
                job_id=request.job_id,
                assessment_mode="immersive_dialogue",
                assessment_status=AssessmentStatus.COMPLETED.value
            )
            db.add(assessment_record)
            db.flush()
        
        # 存储对话数据和评分到 per_turn_results
        per_turn_results = {
            "messages": request.messages,
            "scores_history": request.scores,
            "patterns": request.patterns or [],
            "highlights": request.highlights or [],
            "duration_seconds": request.duration_seconds,
            "conversation_depth": request.conversation_depth,
            "total_rounds": request.total_rounds,
            "saved_at": datetime.utcnow().isoformat()
        }
        
        assessment_record.per_turn_results = per_turn_results
        assessment_record.match_score = sum(request.scores.values()) / len(request.scores) if request.scores else 50.0
        assessment_record.conversation_summary = f"沉浸式对话，{request.total_rounds}轮交互，深度{request.conversation_depth}/10"
        assessment_record.updated_at = datetime.utcnow()
        
        db.commit()
        
        return SaveSessionResponse(
            code=200,
            message="success",
            data={
                "assessment_id": assessment_record.id,
                "session_id": f"session_{assessment_record.id}_{int(datetime.utcnow().timestamp())}"
            }
        )
    
    except Exception as e:
        logger.error(f"保存会话失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
