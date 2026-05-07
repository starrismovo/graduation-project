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
from models.job_requirement import JobSkillRequirement, JobPersonalityFramework
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
import re
import httpx
import logging
from services.personality_scoring import (
    resolve_personality_scores,
    calculate_scenario_traits,
    get_trait_comparison,
)
from services.agent_scoring_fusion import (
    fuse_agent_scores,
    get_agent_weights,
    validate_agent_scores,
    generate_fusion_report,
)
from services.job_requirement_service import matching_engine
from services.report_agent import report_agent
from models.assessment import EvaluationResult
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessment", tags=["assessment"])

TRAIT_KEY_ALIASES = {
    "外向性": "extraversion",
    "extraversion": "extraversion",
    "extroversion": "extraversion",
    "宜人性": "agreeableness",
    "agreeableness": "agreeableness",
    "尽责性": "conscientiousness",
    "conscientiousness": "conscientiousness",
    "神经质": "neuroticism",
    "neuroticism": "neuroticism",
    "开放性": "openness",
    "openness": "openness",
    "情绪稳定性": "neuroticism",
    "emotional_stability": "neuroticism",
}

POSITIVE_TRAITS = {"extraversion", "agreeableness", "conscientiousness", "openness"}
LOWER_IS_BETTER_TRAITS = {"neuroticism"}

INSIGHT_CREATIVE_KEYWORDS = [
    "用户",
    "研究",
    "内容",
    "文案",
    "编辑",
    "策划",
    "新媒体",
    "体验",
    "UX",
    "UI",
    "设计",
    "需求",
    "运营",
]

HARD_TECH_KEYWORDS = [
    "后端",
    "前端",
    "算法",
    "开发",
    "工程师",
    "Java",
    "Python",
    "机器学习",
    "推荐系统",
]


def _coerce_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def _normalize_job_traits(job: Job) -> Dict[str, float]:
    raw_traits = _coerce_dict(job.required_traits)
    if not raw_traits:
        raw_traits = _coerce_dict(getattr(job, "personality_requirements", None))

    normalized: Dict[str, float] = {}
    for raw_key, raw_value in raw_traits.items():
        key = TRAIT_KEY_ALIASES.get(str(raw_key).strip())
        if not key:
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        if str(raw_key).strip() in {"情绪稳定性", "emotional_stability"}:
            value = 10 - value
        normalized[key] = max(0.0, min(10.0, value))
    return normalized


def _profile_traits(profile: CandidatePersonalityProfile) -> Dict[str, float]:
    traits = {
        "extraversion": profile.trait_extroversion,
        "agreeableness": profile.trait_agreeableness,
        "conscientiousness": profile.trait_conscientiousness,
        "neuroticism": profile.trait_neuroticism,
        "openness": profile.trait_openness,
    }
    return {key: float(value) for key, value in traits.items() if value is not None}


def _extract_report_sections(
    evaluation_result: Optional[EvaluationResult],
    match_analysis_record: Optional[AssessmentMatchAnalysis],
) -> Optional[Dict[str, Any]]:
    if evaluation_result and isinstance(evaluation_result.report_content, dict):
        report_content = evaluation_result.report_content
        if isinstance(report_content.get("report_sections"), dict):
            return report_content["report_sections"]
        analysis = report_content.get("analysis")
        if isinstance(analysis, dict) and isinstance(analysis.get("report_sections"), dict):
            return analysis["report_sections"]

    if match_analysis_record and match_analysis_record.detailed_analysis:
        try:
            detail_obj = json.loads(match_analysis_record.detailed_analysis)
        except Exception:
            detail_obj = {}
        structured_report = detail_obj.get("structured_report")
        if isinstance(structured_report, dict):
            return structured_report

    return None


def _job_text(job: Optional[Job], include_description: bool = False) -> str:
    if not job:
        return ""
    values = [job.name, job.category]
    if include_description:
        values.append(job.description)
    return " ".join(str(value or "") for value in values)


def _contains_any(text: str, keywords: List[str]) -> bool:
    folded = text.lower()
    return any(keyword.lower() in folded for keyword in keywords)


def _insight_role_tier(text: str) -> int:
    folded = text.lower()
    primary_keywords = [
        "用户研究",
        "用研",
        "需求分析",
        "体验研究",
        "产品研究",
        "市场研究",
        "内容研究",
    ]
    secondary_keywords = [
        "内容",
        "文案",
        "编辑",
        "新媒体",
        "ux",
        "ui/ux",
        "体验设计",
        "产品经理",
        "产品策划",
        "产品运营",
    ]
    tertiary_keywords = ["策划运营", "营销策划", "活动策划", "策划"]

    if any(keyword.lower() in folded for keyword in primary_keywords):
        return 4
    if any(keyword.lower() in folded for keyword in secondary_keywords):
        return 3
    if "产品" in folded and any(keyword in folded for keyword in ["经理", "策划", "运营", "需求", "用户", "体验"]):
        return 3
    if any(keyword.lower() in folded for keyword in tertiary_keywords):
        return 2
    return 0


def _is_insight_creative_role(text: str) -> bool:
    folded = text.lower()
    if _insight_role_tier(text) > 0:
        return True
    if "产品" in folded and any(keyword in folded for keyword in ["经理", "策划", "运营", "需求", "用户", "体验"]):
        return True
    if "研究" in folded and any(keyword in folded for keyword in ["用户", "产品", "市场", "内容", "体验", "需求"]):
        return True
    return False


def _calculate_role_affinity(
    profile: CandidatePersonalityProfile,
    job: Job,
    source_job: Optional[Job] = None,
) -> float:
    job_text = _job_text(job)
    source_text = _job_text(source_job)
    candidate_traits = _profile_traits(profile)
    score = 50.0

    job_is_insight_creative = _is_insight_creative_role(job_text)
    source_is_insight_creative = _is_insight_creative_role(source_text)
    job_is_hard_tech = _contains_any(job_text, HARD_TECH_KEYWORDS)
    role_tier = _insight_role_tier(job_text)

    if source_job:
        if job.id == source_job.id:
            score += 25
        elif job.category and source_job.category and job.category == source_job.category:
            score += 12
        if source_is_insight_creative and job_is_insight_creative:
            score += role_tier * 8

    if candidate_traits.get("openness", 0) >= 8 and job_is_insight_creative:
        score += 14
    if candidate_traits.get("agreeableness", 0) >= 7 and job_is_insight_creative:
        score += 10
    if candidate_traits.get("conscientiousness", 0) >= 7 and _contains_any(job_text, ["研究", "编辑", "策划", "产品", "内容"]):
        score += 8

    if role_tier == 2 and _contains_any(job_text, ["酒店", "营销"]) and not _contains_any(job_text, ["内容", "用户", "产品", "新媒体"]):
        score -= 14
    if job_is_hard_tech and not _contains_any(job_text, ["用户", "产品", "体验", "设计"]):
        score -= 18
    if candidate_traits.get("extraversion", 5) < 5 and _contains_any(job_text, ["销售", "主持", "直播", "客户经理"]):
        score -= 12

    return round(max(0.0, min(100.0, score)), 1)


def _calculate_recommendation_score(
    profile: CandidatePersonalityProfile,
    job: Job,
    source_job: Optional[Job] = None,
) -> Dict[str, float]:
    match_result = calculate_job_match_score(profile, job)
    role_affinity = _calculate_role_affinity(profile, job, source_job)
    overall = round(match_result["overall"] * 0.65 + role_affinity * 0.35, 1)
    return {
        **match_result,
        "role_affinity": role_affinity,
        "recommendation_score": overall,
    }


def resolve_candidate_user(candidate_identifier: str, db: Session) -> User:
    """Resolve candidate identifier into a concrete User record."""
    raw = str(candidate_identifier or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="candidate_id 不能为空")

    candidate: Optional[User] = None

    # 1) direct numeric id
    if raw.isdigit():
        candidate = db.query(User).filter(User.id == int(raw)).first()
        if candidate:
            return candidate

    # 2) common string formats like user_2 / cand_001
    m = re.match(r"^(?:user|candidate|cand)[_-]?(\d+)$", raw, flags=re.IGNORECASE)
    if m:
        candidate = db.query(User).filter(User.id == int(m.group(1))).first()
        if candidate:
            return candidate

    # 3) username or email
    candidate = db.query(User).filter(User.username == raw).first()
    if candidate:
        return candidate

    if "@" in raw:
        candidate = db.query(User).filter(User.email == raw).first()
        if candidate:
            return candidate

    # 4) fallback: trailing digits in custom id
    tail = re.search(r"(\d+)$", raw)
    if tail:
        candidate = db.query(User).filter(User.id == int(tail.group(1))).first()
        if candidate:
            return candidate

    raise HTTPException(status_code=404, detail=f"候选人不存在: {raw}")


# ============ Helper Functions ============

def calculate_job_match_score(personality_profile: CandidatePersonalityProfile, job: Job) -> Dict[str, float]:
    """
    计算候选人与岗位的匹配度
    返回 {"skill_match": 0-100, "personality_match": 0-100, "overall": 0-100}
    - personality_match: 基于大五人格模型与岗位要求的对齐程度
    - skill_match: 此接口无技能数据，默认 50
    - overall: 0.4 * skill_match + 0.6 * personality_match
    """
    default = {"skill_match": 50.0, "personality_match": 50.0, "overall": 50.0}

    if not personality_profile:
        return default

    candidate_traits = _profile_traits(personality_profile)
    required_traits = _normalize_job_traits(job)
    if not candidate_traits or not required_traits:
        return default

    # personality_match：大五人格匹配（0-100）
    total_score = 0.0
    matched_count = 0
    for trait_name, required_score in required_traits.items():
        if trait_name in candidate_traits and candidate_traits[trait_name] is not None:
            candidate_score = candidate_traits[trait_name]
            if trait_name in LOWER_IS_BETTER_TRAITS:
                gap = max(0.0, candidate_score - required_score)
            elif trait_name in POSITIVE_TRAITS:
                gap = max(0.0, required_score - candidate_score)
            else:
                gap = abs(candidate_score - required_score)
            # 岗位人格需求表示胜任阈值：正向特质达到要求后不额外扣分，神经质低于要求视为稳定性满足。
            similarity = max(0.0, 10 - gap)
            total_score += similarity
            matched_count += 1

    if matched_count == 0:
        personality_match = 50.0
    else:
        personality_match = min(100.0, max(0.0, (total_score / matched_count) * 10))

    # skill_match：此接口仅有人格数据，置为中性值
    skill_match = 50.0

    # overall：人格权重较大（评估场景）
    overall = round(min(100.0, max(0.0, 0.4 * skill_match + 0.6 * personality_match)), 1)

    return {
        "skill_match": round(skill_match, 1),
        "personality_match": round(personality_match, 1),
        "overall": overall,
    }


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
    candidate = resolve_candidate_user(candidate_id, db)
    profile = db.query(CandidatePersonalityProfile).filter_by(
        candidate_id=candidate.id
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
    candidate = resolve_candidate_user(candidate_id, db)

    records = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate.id
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
    candidate = resolve_candidate_user(candidate_id, db)
    profile = db.query(CandidatePersonalityProfile).filter_by(
        candidate_id=candidate.id
    ).first()
    
    # 获取所有岗位
    jobs = db.query(Job).all()
    latest_record = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate.id,
        AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED,
        AssessmentRecord.is_deleted == False
    ).order_by(desc(AssessmentRecord.created_at)).first()
    source_job = None
    if latest_record:
        source_job = db.query(Job).filter(Job.id == latest_record.job_id).first()
    
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
                company=job.company,
                city=job.city,
                category=job.category,
                salary=f"{int(job.salary_min)}k-{int(job.salary_max)}k",
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
        result = _calculate_recommendation_score(profile, job, source_job)
        job_scores.append((job, result["recommendation_score"], result))
    
    # 按匹配度降序排序
    job_scores.sort(
        key=lambda x: (
            x[1],
            1 if source_job and x[0].id == source_job.id else 0,
            x[2]["role_affinity"],
            x[2]["personality_match"],
        ),
        reverse=True,
    )
    
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
            company=job.company,
            city=job.city,
            category=job.category,
            salary=f"{int(job.salary_min)}k-{int(job.salary_max)}k",
            department=job.category,
            level="P6",  # 默认级别
            match_score=score,
            match_reason=(
                f"人格匹配度约 {detail['personality_match']}%，"
                f"岗位方向亲和度约 {detail['role_affinity']}%"
            )
        )
        for job, score, detail in top_jobs
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
    
    job = db.query(Job).filter_by(id=record.job_id).first()
    evaluation_result = db.query(EvaluationResult).filter_by(
        assessment_record_id=record_id
    ).first()

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

    report_sections = _extract_report_sections(evaluation_result, match_analysis_record)

    model_version = None
    if match_analysis_record and match_analysis_record.detailed_analysis:
        try:
            detail_obj = json.loads(match_analysis_record.detailed_analysis)
            model_version = detail_obj.get("model_version")
        except Exception:
            model_version = None

    if not report_sections:
        profile = db.query(CandidatePersonalityProfile).filter_by(
            candidate_id=record.candidate_id
        ).first()
        if profile:
            generated_sections = report_agent.build_report_sections(
                profile=profile,
                job=job,
                match_breakdown={
                    "skill_match": 50.0,
                    "personality_match": record.match_score or 50.0,
                    "overall_score": record.match_score or 50.0,
                },
            )
            report_sections = generated_sections

    if (not recommendations) and report_sections:
        recommendations = [
            item.get("action") or item.get("reason")
            for item in report_sections.get("career_recommendations", [])
            if isinstance(item, dict) and (item.get("action") or item.get("reason"))
        ][:3]
    
    # 构建响应
    details = AssessmentDetails(
        total_rounds=record.total_rounds,
        duration_minutes=record.duration_minutes,
        conversation_depth=record.conversation_depth,
        roles_participated=record.roles_participated,
        overall_impression=record.overall_impression,
        model_version=model_version
    )
    
    report = AssessmentReport(
        id=record.id,
        candidate_id=str(record.candidate_id),
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
        report_sections=report_sections,
        assessement_details=details  # 注意 typo 保持与前端一致
    )
    
    return AssessmentReportResponse(data=report)


# ============ HR 候选人管理端点 ============

@router.get("/hr/candidates", response_model=StandardResponse)
async def get_hr_candidates(
    job_id: Optional[int] = Query(None, description="按岗位筛选"),
    status: Optional[str] = Query(None, description="按状态筛选: completed/pending"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    HR 获取所有已评估候选人列表（跨候选人聚合）
    返回评估记录 + 候选人姓名 + 岗位信息 + 匹配分数
    """
    query = db.query(AssessmentRecord, User).join(
        User, AssessmentRecord.candidate_id == User.id
    )

    if job_id:
        query = query.filter(AssessmentRecord.job_id == job_id)
    if status:
        try:
            query = query.filter(AssessmentRecord.assessment_status == AssessmentStatus(status))
        except ValueError:
            pass

    total = query.count()
    records = query.order_by(desc(AssessmentRecord.created_at)).offset(offset).limit(limit).all()

    items = []
    for record, user in records:
        items.append({
            "record_id": record.id,
            "candidate_id": record.candidate_id,
            "candidate_name": user.real_name or user.nickname or user.username,
            "candidate_email": user.email,
            "job_id": record.job_id,
            "job_title": record.job_title,
            "match_score": record.match_score,
            "assessment_status": record.assessment_status.value if record.assessment_status else "pending",
            "assessment_mode": record.assessment_mode,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "total_rounds": record.total_rounds,
            "duration_minutes": record.duration_minutes,
        })

    return StandardResponse(
        code=200,
        message="success",
        data={"total": total, "items": items}
    )


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
        
        candidate = resolve_candidate_user(request.candidate_id, db)
        
        # 1. 创建评估记录
        job = db.query(Job).filter_by(id=request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="岗位不存在")
        
        record = AssessmentRecord(
            candidate_id=candidate.id,
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
            candidate_id=candidate.id
        ).first()
        
        if not personality_profile:
            personality_profile = CandidatePersonalityProfile(
                candidate_id=candidate.id
            )
            db.add(personality_profile)
        
        # 后端统一计算/解析五大人格（带模型版本）
        personality_scores, scoring_meta = resolve_personality_scores(
            request.all_scores,
            request.personality_scores,
        )

        personality_profile.trait_extroversion = personality_scores.get("外向性", 5)
        personality_profile.trait_agreeableness = personality_scores.get("宜人性", 5)
        personality_profile.trait_conscientiousness = personality_scores.get("尽责性", 5)
        personality_profile.trait_neuroticism = personality_scores.get("神经质", 5)
        personality_profile.trait_openness = personality_scores.get("开放性", 5)
        personality_profile.latest_assessment_id = record.id
        personality_profile.updated_at = datetime.now()
        
        db.flush()
        
        logger.info(f"【save-result】心理画像已保存: {personality_profile.trait_extroversion}, {personality_profile.trait_conscientiousness}, etc")
        
        # 3. 计算岗位匹配度（skill/personality/overall 统一）
        required_skills = db.query(JobSkillRequirement).filter(
            JobSkillRequirement.job_id == request.job_id
        ).all()
        personality_fw = db.query(JobPersonalityFramework).filter(
            JobPersonalityFramework.job_id == request.job_id
        ).first()

        candidate_skills: List[str] = []
        if isinstance(candidate.skills, list):
            candidate_skills = [str(s).strip() for s in candidate.skills if str(s).strip()]
        elif isinstance(candidate.skills, str):
            candidate_skills = [s.strip() for s in candidate.skills.split(",") if s.strip()]
        elif request.candidate_info and isinstance(request.candidate_info.get("skills"), list):
            candidate_skills = [str(s).strip() for s in request.candidate_info.get("skills", []) if str(s).strip()]

        if required_skills and candidate_skills:
            skill_match, matched_skills, missing_skills = matching_engine.calculate_skill_match(
                candidate_skills,
                required_skills,
            )
        else:
            skill_match, matched_skills, missing_skills = 50.0, [], []

        candidate_personality = {
            "openness": (personality_profile.trait_openness or 0) * 10,
            "conscientiousness": (personality_profile.trait_conscientiousness or 0) * 10,
            "extraversion": (personality_profile.trait_extroversion or 0) * 10,
            "agreeableness": (personality_profile.trait_agreeableness or 0) * 10,
            "neuroticism": (personality_profile.trait_neuroticism or 0) * 10,
        }
        if personality_fw:
            personality_match = matching_engine.calculate_personality_match(
                candidate_personality,
                personality_fw,
            )
        else:
            # fallback 到现有岗位特质匹配，避免岗位尚未配置人格框架时退化
            personality_match = calculate_job_match_score(personality_profile, job)["personality_match"]

        overall_score = matching_engine.calculate_overall_match(skill_match, personality_match)
        record.match_score = overall_score

        logger.info(
            f"【save-result】匹配度已计算: overall={overall_score}, "
            f"skill={skill_match}, personality={personality_match}"
        )
        
        # ===== 新增：计算场景人格（论文第4.3.3节） =====
        scenario_traits = None
        trait_comparison = None
        
        # 如果岗位有人格需求配置，则计算场景人格
        if job.personality_requirements:
            try:
                scenario_traits, adjustments = calculate_scenario_traits(
                    basic_traits=personality_scores,
                    job_personality_requirements=job.personality_requirements
                )
                # 生成特质对比报告
                trait_comparison = get_trait_comparison(
                    basic_traits=personality_scores,
                    scenario_traits=scenario_traits,
                    job_requirements=job.personality_requirements
                )
                logger.info(f"【save-result】场景人格已计算: {scenario_traits}")
            except Exception as e:
                logger.warning(f"【save-result】场景人格计算失败: {str(e)}")
                scenario_traits = None
                trait_comparison = None
        
        # ===== 新增：融合Agent评分（论文第4.1.3节） =====
        agent_scores_dict = {}
        fusion_details = None
        fused_score = None
        
        # 如果请求中包含Agent评分数据，则进行融合
        if hasattr(request, 'agent_scores') and request.agent_scores:
            try:
                # 验证Agent评分
                is_valid, warnings = validate_agent_scores(request.agent_scores)
                if not is_valid:
                    logger.warning(f"【save-result】Agent评分验证警告: {warnings}")
                
                # 获取岗位类别，用于权重配置
                job_category = job.category if hasattr(job, 'category') else None
                
                # 融合Agent评分
                fused_score, fusion_details = fuse_agent_scores(
                    agent_scores=request.agent_scores,
                    job_category=job_category
                )
                
                agent_scores_dict = request.agent_scores
                logger.info(f"【save-result】Agent评分已融合: fused_score={fused_score:.1f}")
            except Exception as e:
                logger.warning(f"【save-result】Agent评分融合失败: {str(e)}")
                fusion_details = None
                fused_score = None
        
        # 如果有Agent融合评分，可以将其作为参考
        if fused_score is not None:
            # 可以选择使用融合评分或与现有评分结合
            logger.info(f"【save-result】使用Agent融合评分作为参考: {fused_score:.1f}")
        
        # ===== 新增：创建EvaluationResult（论文第3.5.1节） =====
        evaluation_result = None
        try:
            evaluation_result = EvaluationResult(
                result_id=str(uuid.uuid4()),
                assessment_record_id=record.id,
                candidate_id=candidate.id,
                job_id=request.job_id,
                match_score=overall_score,
                ability_scores=request.all_scores,  # 能力维度评分
                trait_comparison=trait_comparison,   # 特质对比（基础/场景/需求）
                agent_scores=fusion_details,         # Agent评分及权重信息
                strengths=None,  # 稍后填充
                gaps=None,       # 稍后填充
                recommendations=None,  # 稍后填充
                created_at=datetime.now(),
            )
            db.add(evaluation_result)
            db.flush()
            logger.info(f"【save-result】EvaluationResult已创建: result_id={evaluation_result.result_id}")
        except Exception as e:
            logger.warning(f"【save-result】EvaluationResult创建失败: {str(e)}")
            evaluation_result = None
        
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
            trait_score = personality_scores.get(trait_name, 5)
            if trait_score is not None:
                trait_desc = PersonalityTraitDescription(
                    assessment_record_id=record.id,
                    trait_name=trait_name,
                    score=trait_score,
                    description=trait_descriptions.get(trait_name)
                )
                db.add(trait_desc)
        
        db.flush()
        
        logger.info(f"【save-result】特质描述已保存")
        
        # 5. 通过 ReportAgent 生成分析和建议
        analysis_payload = report_agent.build_match_analysis(
            profile=personality_profile,
            job=job,
            scoring_meta=scoring_meta,
            match_breakdown={
                "skill_match": skill_match,
                "personality_match": personality_match,
                "overall_score": overall_score,
            },
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        )

        # 6. 保存匹配分析
        match_analysis = AssessmentMatchAnalysis(
            assessment_record_id=record.id,
            strengths=analysis_payload["strengths"],
            gaps=analysis_payload["gaps"],
            recommendations=analysis_payload["recommendations"],
            detailed_analysis=json.dumps(analysis_payload["detailed_analysis"], ensure_ascii=False),
        )
        db.add(match_analysis)
        
        db.flush()
        
        logger.info(f"【save-result】分析与建议已生成")
        
        # ===== 新增：更新EvaluationResult的分析内容 =====
        if evaluation_result:
            try:
                # 转换strengths、gaps、recommendations为JSON格式
                if isinstance(analysis_payload.get("strengths"), list):
                    strengths_text = "\n".join(analysis_payload["strengths"])
                else:
                    strengths_text = str(analysis_payload.get("strengths", ""))
                
                if isinstance(analysis_payload.get("gaps"), list):
                    gaps_text = "\n".join(analysis_payload["gaps"])
                else:
                    gaps_text = str(analysis_payload.get("gaps", ""))
                
                if isinstance(analysis_payload.get("recommendations"), list):
                    recommendations_text = "\n".join(analysis_payload["recommendations"])
                else:
                    recommendations_text = str(analysis_payload.get("recommendations", ""))
                
                evaluation_result.strengths = strengths_text
                evaluation_result.gaps = gaps_text
                evaluation_result.recommendations = recommendations_text
                
                # 生成完整报告内容
                report_content = {
                    "basic_traits": personality_scores,
                    "scenario_traits": scenario_traits,
                    "trait_comparison": trait_comparison,
                    "ability_scores": request.all_scores,
                    "skill_match": skill_match,
                    "personality_match": personality_match,
                    "overall_score": overall_score,
                    "agent_fusion": fusion_details,
                    "analysis": analysis_payload,
                    "report_sections": analysis_payload.get("report_sections"),
                    "generated_at": datetime.now().isoformat(),
                }
                evaluation_result.report_content = report_content
                evaluation_result.updated_at = datetime.now()
                
                logger.info(f"【save-result】EvaluationResult已更新: result_id={evaluation_result.result_id}")
            except Exception as e:
                logger.warning(f"【save-result】EvaluationResult更新失败: {str(e)}")
        
        # 7. 提交事务
        db.commit()
        
        logger.info(f"【save-result】评估结果保存完成! record_id={record.id}, match_score={overall_score}")
        
        return StandardResponse(
            code=200,
            message="评估结果已保存",
            data={
                "record_id": record.id,
                "evaluation_result_id": evaluation_result.result_id if evaluation_result else None,
                "skill_match": skill_match,
                "personality_match": personality_match,
                "overall_score": overall_score,
                "model_version": scoring_meta.get("model_version"),
                "scoring_source": scoring_meta.get("source"),
                "basic_traits": personality_scores,
                "scenario_traits": scenario_traits,
                "trait_comparison": trait_comparison,
                "agent_scores": agent_scores_dict if agent_scores_dict else None,
                "fused_score": fused_score,
                "fusion_details": fusion_details,
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"【save-result】保存评估结果失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


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


# ============ EvaluationResult API（论文第3.5.1节） ============

@router.get("/evaluation-result/{result_id}", response_model=StandardResponse)
async def get_evaluation_result(
    result_id: str,
    db: Session = Depends(get_db)
):
    """
    查询评估结果（集中存储的完整评估数据）
    
    返回包含：
    - 基础人格 + 场景人格 + 岗位需求对比
    - Agent评分及融合权重
    - 完整的能力评分和分析建议
    """
    try:
        result = db.query(EvaluationResult).filter_by(result_id=result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="评估结果不存在")
        
        return StandardResponse(
            code=200,
            message="评估结果查询成功",
            data=result.to_dict()
        )
    except Exception as e:
        logger.error(f"【get-evaluation-result】查询失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/evaluation-result/by-assessment/{assessment_record_id}", response_model=StandardResponse)
async def get_evaluation_result_by_assessment(
    assessment_record_id: int,
    db: Session = Depends(get_db)
):
    """
    通过评估记录ID查询对应的EvaluationResult
    """
    try:
        result = db.query(EvaluationResult).filter_by(
            assessment_record_id=assessment_record_id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="未找到对应的评估结果")
        
        return StandardResponse(
            code=200,
            message="评估结果查询成功",
            data=result.to_dict()
        )
    except Exception as e:
        logger.error(f"【get-evaluation-result-by-assessment】查询失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/evaluation-results/by-candidate/{candidate_id}", response_model=StandardResponse)
async def get_evaluation_results_by_candidate(
    candidate_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    查询候选人的所有评估结果（分页）
    """
    try:
        candidate = resolve_candidate_user(candidate_id, db)
        
        total = db.query(EvaluationResult).filter_by(
            candidate_id=candidate.id
        ).count()
        
        results = db.query(EvaluationResult).filter_by(
            candidate_id=candidate.id
        ).order_by(desc(EvaluationResult.created_at)).offset(offset).limit(limit).all()
        
        return StandardResponse(
            code=200,
            message="评估结果列表查询成功",
            data={
                "total": total,
                "limit": limit,
                "offset": offset,
                "items": [r.to_dict() for r in results]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"【get-evaluation-results-by-candidate】查询失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


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
    api_base = os.getenv("ROAD2ALL_API_BASE", "https://api.siliconflow.cn/v1").rstrip("/")
    api_url = os.getenv("ROAD2ALL_API_URL", f"{api_base}/chat/completions")
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
    api_base = os.getenv("ROAD2ALL_API_BASE", "https://api.siliconflow.cn/v1").rstrip("/")
    api_url = os.getenv("ROAD2ALL_API_URL", f"{api_base}/chat/completions")
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
# ============ 以下沉浸式对话端点已迁移至 routers/immersive_dialogue.py ============
