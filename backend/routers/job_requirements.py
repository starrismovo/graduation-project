"""
岗位需求管理 API 路由
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from database import get_db
from models import (
    Job, JobRequirementTag, JobSkillRequirement, JobPersonalityFramework,
    CandidateJobApplication, User, CandidatePersonalityProfile
)
from schemas.job_requirement import (
    JobRequirementInputSchema,
    JobSkillRequirementSchema,
    JobRequirementTagSchema,
    JobPersonalityFrameworkSchema,
    CandidateJobApplicationInputSchema,
    CandidateJobApplicationResponseSchema,
    JobRequirementFullSchema,
    JobMatchResultSchema
)
from services.job_requirement_service import jd_parser, matching_engine
from routers.user import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["job_requirements"])


# ==================== 岗位需求管理 ====================

class CreateFromJDRequest(BaseModel):
    """从JD创建岗位需求的请求体"""
    job_id: int
    jd_text: str
    role_category: str

@router.post("/requirements/create-from-jd", response_model=dict)
async def create_requirements_from_jd(
    body: CreateFromJDRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    从岗位描述文本自动生成结构化需求
    
    Args:
        body.job_id: 岗位 ID
        body.jd_text: 原始 JD 文本
        body.role_category: 岗位类别（backend/frontend/product/design等）
    
    Returns:
        生成的需求结构
    """
    job_id = body.job_id
    jd_text = body.jd_text
    role_category = body.role_category
    
    # 验证岗位存在
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 验证权限（只有 HR 或岗位创建者可以修改）
    user_id = current_user.id if hasattr(current_user, 'id') else current_user.get("id")
    if job.creator_id != user_id:
        raise HTTPException(status_code=403, detail="无权修改此岗位需求")
    
    try:
        logger.info(f"开始从 JD 生成需求: job_id={job_id}")
        
        # 使用 JD 解析器
        skills, tags, personality_framework = jd_parser.parse_jd_with_llm(
            jd_text=jd_text,
            role_category=role_category,
            use_llm=False  # 暂不使用 LLM，使用规则引擎
        )
        
        # 清空旧的需求（可选）
        db.query(JobSkillRequirement).filter(JobSkillRequirement.job_id == job_id).delete()
        db.query(JobRequirementTag).filter(JobRequirementTag.job_id == job_id).delete()
        db.query(JobPersonalityFramework).filter(JobPersonalityFramework.job_id == job_id).delete()
        
        # 创建新的技能需求
        for skill in skills:
            skill_req = JobSkillRequirement(
                job_id=job_id,
                skill_name=skill.skill_name,
                skill_type=skill.skill_type,
                required_level=skill.required_level,
                years_experience=skill.years_experience,
                is_must_have=skill.is_must_have,
                priority_score=skill.priority_score
            )
            db.add(skill_req)
        
        # 创建能力标签
        for tag in tags:
            req_tag = JobRequirementTag(
                job_id=job_id,
                capability_name=tag.capability_name,
                capability_category=tag.capability_category,
                importance_level=tag.importance_level,
                proficiency_required=tag.proficiency_required,
                personality_dimension=tag.personality_dimension,
                personality_min=tag.personality_min,
                personality_max=tag.personality_max,
                personality_weight=tag.personality_weight
            )
            db.add(req_tag)
        
        # 创建人格框架
        pf = JobPersonalityFramework(
            job_id=job_id,
            openness_min=personality_framework.openness_min,
            openness_max=personality_framework.openness_max,
            openness_weight=personality_framework.openness_weight,
            conscientiousness_min=personality_framework.conscientiousness_min,
            conscientiousness_max=personality_framework.conscientiousness_max,
            conscientiousness_weight=personality_framework.conscientiousness_weight,
            extraversion_min=personality_framework.extraversion_min,
            extraversion_max=personality_framework.extraversion_max,
            extraversion_weight=personality_framework.extraversion_weight,
            agreeableness_min=personality_framework.agreeableness_min,
            agreeableness_max=personality_framework.agreeableness_max,
            agreeableness_weight=personality_framework.agreeableness_weight,
            neuroticism_min=personality_framework.neuroticism_min,
            neuroticism_max=personality_framework.neuroticism_max,
            neuroticism_weight=personality_framework.neuroticism_weight,
            description=personality_framework.description
        )
        db.add(pf)
        
        db.commit()
        logger.info(f"岗位需求生成成功: {len(skills)} 技能, {len(tags)} 标签")
        
        return {
            "code": 200,
            "message": "岗位需求已生成",
            "data": {
                "skills_count": len(skills),
                "tags_count": len(tags),
                "personality_framework": personality_framework.dict()
            }
        }
    
    except Exception as e:
        logger.error(f"JD 解析失败: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成需求失败: {str(e)}")


@router.post("/requirements/update", response_model=dict)
async def update_job_requirements(
    request: JobRequirementInputSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    手动更新岗位需求（HR 编辑）
    """
    
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 验证权限
    user_id2 = current_user.id if hasattr(current_user, 'id') else current_user.get("id")
    if job.creator_id != user_id2:
        raise HTTPException(status_code=403, detail="无权修改此岗位需求")
    
    try:
        # 清空旧的需求
        db.query(JobSkillRequirement).filter(JobSkillRequirement.job_id == request.job_id).delete()
        db.query(JobRequirementTag).filter(JobRequirementTag.job_id == request.job_id).delete()
        db.query(JobPersonalityFramework).filter(JobPersonalityFramework.job_id == request.job_id).delete()
        
        # 添加新的技能
        for skill in request.skills:
            skill_req = JobSkillRequirement(
                job_id=request.job_id,
                skill_name=skill.skill_name,
                skill_type=skill.skill_type,
                required_level=skill.required_level,
                years_experience=skill.years_experience,
                is_must_have=skill.is_must_have,
                priority_score=skill.priority_score
            )
            db.add(skill_req)
        
        # 添加能力标签
        for tag in request.requirement_tags:
            req_tag = JobRequirementTag(
                job_id=request.job_id,
                capability_name=tag.capability_name,
                capability_category=tag.capability_category,
                importance_level=tag.importance_level,
                proficiency_required=tag.proficiency_required,
                personality_dimension=tag.personality_dimension,
                personality_min=tag.personality_min,
                personality_max=tag.personality_max,
                personality_weight=tag.personality_weight
            )
            db.add(req_tag)
        
        # 添加人格框架
        if request.personality_framework:
            pf = JobPersonalityFramework(
                job_id=request.job_id,
                **request.personality_framework.dict()
            )
            db.add(pf)
        
        db.commit()
        logger.info(f"岗位需求已更新: job_id={request.job_id}")
        
        return {
            "code": 200,
            "message": "岗位需求已更新",
            "data": {
                "job_id": request.job_id,
                "skills_count": len(request.skills),
                "tags_count": len(request.requirement_tags)
            }
        }
    
    except Exception as e:
        logger.error(f"更新岗位需求失败: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.get("/requirements/{job_id}", response_model=JobRequirementFullSchema)
async def get_job_requirements(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    获取岗位的完整需求信息
    """
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 获取相关的需求数据
    skills = db.query(JobSkillRequirement).filter(JobSkillRequirement.job_id == job_id).all()
    tags = db.query(JobRequirementTag).filter(JobRequirementTag.job_id == job_id).all()
    personality_fw = db.query(JobPersonalityFramework).filter(JobPersonalityFramework.job_id == job_id).first()
    
    # 转换为 Schema
    skills_schema = [
        JobSkillRequirementSchema(
            skill_name=s.skill_name,
            skill_type=s.skill_type,
            required_level=s.required_level,
            years_experience=s.years_experience,
            is_must_have=s.is_must_have,
            priority_score=s.priority_score
        )
        for s in skills
    ]
    
    tags_schema = [
        JobRequirementTagSchema(
            capability_name=t.capability_name,
            capability_category=t.capability_category,
            importance_level=t.importance_level,
            proficiency_required=t.proficiency_required,
            personality_dimension=t.personality_dimension,
            personality_min=t.personality_min,
            personality_max=t.personality_max,
            personality_weight=t.personality_weight
        )
        for t in tags
    ]
    
    personality_schema = None
    if personality_fw:
        personality_schema = JobPersonalityFrameworkSchema(
            openness_min=personality_fw.openness_min,
            openness_max=personality_fw.openness_max,
            openness_weight=personality_fw.openness_weight,
            conscientiousness_min=personality_fw.conscientiousness_min,
            conscientiousness_max=personality_fw.conscientiousness_max,
            conscientiousness_weight=personality_fw.conscientiousness_weight,
            extraversion_min=personality_fw.extraversion_min,
            extraversion_max=personality_fw.extraversion_max,
            extraversion_weight=personality_fw.extraversion_weight,
            agreeableness_min=personality_fw.agreeableness_min,
            agreeableness_max=personality_fw.agreeableness_max,
            agreeableness_weight=personality_fw.agreeableness_weight,
            neuroticism_min=personality_fw.neuroticism_min,
            neuroticism_max=personality_fw.neuroticism_max,
            neuroticism_weight=personality_fw.neuroticism_weight,
            description=personality_fw.description
        )
    
    return JobRequirementFullSchema(
        job_id=job.id,
        job_name=job.name,
        job_description=job.description,
        skills=skills_schema,
        requirement_tags=tags_schema,
        personality_framework=personality_schema
    )


# ==================== 候选人应聘管理 ====================

@router.post("/apply", response_model=CandidateJobApplicationResponseSchema)
async def apply_for_job(
    request: CandidateJobApplicationInputSchema,
    db: Session = Depends(get_db)
):
    """
    候选人应聘岗位
    
    流程：
    1. 记录应聘信息
    2. 仅当候选人已有人格评估时，计算匹配度
    3. 返回应聘确认
    
    注意：该端点不需要认证，因为 candidate_id 已在请求体中
    """
    
    # 验证候选人存在
    candidate = db.query(User).filter(User.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 验证岗位
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 检查是否已申请
    existing_app = db.query(CandidateJobApplication).filter(
        CandidateJobApplication.candidate_id == request.candidate_id,
        CandidateJobApplication.job_id == request.job_id
    ).first()
    
    if existing_app:
        raise HTTPException(status_code=400, detail="已申请过此岗位")
    
    try:
        # 创建应聘记录
        application = CandidateJobApplication(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            application_status="applied",
            notes=request.notes
        )
        
        # 如果候选人有人格评估，计算匹配度
        personality_profile = db.query(CandidatePersonalityProfile).filter(
            CandidatePersonalityProfile.candidate_id == request.candidate_id
        ).first()
        
        if personality_profile:
            # 获取岗位需求
            personality_fw = db.query(JobPersonalityFramework).filter(
                JobPersonalityFramework.job_id == request.job_id
            ).first()
            
            if personality_fw:
                # 计算人格匹配度
                candidate_personality = {
                    "openness": (personality_profile.trait_openness or 0) * 10,
                    "conscientiousness": (personality_profile.trait_conscientiousness or 0) * 10,
                    "extraversion": (personality_profile.trait_extroversion or 0) * 10,
                    "agreeableness": (personality_profile.trait_agreeableness or 0) * 10,
                    "neuroticism": (personality_profile.trait_neuroticism or 0) * 10,
                }
                
                personality_match = matching_engine.calculate_personality_match(
                    candidate_personality,
                    personality_fw
                )
                
                application.personality_match_score = personality_match
                application.application_status = "personality_assessed"
        
        db.add(application)
        db.commit()
        
        logger.info(f"候选人应聘: candidate_id={request.candidate_id}, job_id={request.job_id}")
        
        return CandidateJobApplicationResponseSchema.from_orm(application)
    
    except Exception as e:
        logger.error(f"应聘失败: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"应聘失败: {str(e)}")


@router.get("/applications/{candidate_id}", response_model=List[CandidateJobApplicationResponseSchema])
async def get_candidate_applications(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    获取候选人的应聘记录
    """
    
    applications = db.query(CandidateJobApplication).filter(
        CandidateJobApplication.candidate_id == candidate_id
    ).all()
    
    result = []
    for app in applications:
        app_dict = {
            "id": app.id,
            "candidate_id": app.candidate_id,
            "job_id": app.job_id,
            "application_status": app.application_status,
            "match_score": app.match_score,
            "resume_match_score": app.resume_match_score,
            "personality_match_score": app.personality_match_score,
            "overall_score": app.overall_score,
            "notes": app.notes,
            "applied_at": app.applied_at,
            "updated_at": app.updated_at,
            "job": {
                "id": app.job.id,
                "name": app.job.name,
                "company": app.job.company,
                "salary_min": app.job.salary_min,
                "salary_max": app.job.salary_max
            } if app.job else None
        }
        result.append(app_dict)
    
    return result


@router.get("/match/{candidate_id}/{job_id}", response_model=JobMatchResultSchema)
async def calculate_job_match(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    计算候选人与岗位的匹配度
    
    Returns:
        详细的匹配分析结果
    """
    
    # 获取岗位
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 获取候选人人格评估
    personality_profile = db.query(CandidatePersonalityProfile).filter(
        CandidatePersonalityProfile.candidate_id == candidate_id
    ).first()
    
    if not personality_profile:
        raise HTTPException(status_code=400, detail="候选人未完成人格评估")
    
    try:
        # 获取岗位需求
        skills = db.query(JobSkillRequirement).filter(
            JobSkillRequirement.job_id == job_id
        ).all()
        
        personality_fw = db.query(JobPersonalityFramework).filter(
            JobPersonalityFramework.job_id == job_id
        ).first()
        
        # 获取候选人技能信息（User.skills）
        candidate = db.query(User).filter(User.id == candidate_id).first()
        candidate_skills = candidate.skills if isinstance(candidate.skills, list) else []
        if not candidate_skills and isinstance(candidate.skills, str):
            candidate_skills = [s.strip() for s in candidate.skills.split(",") if s.strip()]
        
        # 计算各项匹配度
        skill_match_score, matched_skills, missing_skills = matching_engine.calculate_skill_match(
            candidate_skills,
            skills
        )
        
        # 计算人格匹配度
        candidate_personality = {
            "openness": (personality_profile.trait_openness or 0) * 10,
            "conscientiousness": (personality_profile.trait_conscientiousness or 0) * 10,
            "extraversion": (personality_profile.trait_extroversion or 0) * 10,
            "agreeableness": (personality_profile.trait_agreeableness or 0) * 10,
            "neuroticism": (personality_profile.trait_neuroticism or 0) * 10,
        }
        
        personality_match_score = 50  # 默认值
        if personality_fw:
            personality_match_score = matching_engine.calculate_personality_match(
                candidate_personality,
                personality_fw
            )
        
        # 计算综合匹配度
        overall_score = matching_engine.calculate_overall_match(
            skill_match_score,
            personality_match_score
        )
        
        # 生成推荐
        if overall_score >= 75:
            recommendation = "high_match"
            explanation = "候选人技能和人格特质与岗位需求高度匹配，强烈推荐进入面试"
        elif overall_score >= 60:
            recommendation = "medium_match"
            explanation = "候选人基本符合岗位需求，可以考虑进入面试"
        else:
            recommendation = "low_match"
            explanation = "候选人与岗位需求不够匹配，建议继续寻找其他候选人"
        
        logger.info(f"匹配度计算完成: {candidate_id} vs {job_id}, 综合分={overall_score}")
        
        return JobMatchResultSchema(
            job_id=job.id,
            job_name=job.name,
            candidate_id=candidate_id,
            resume_match_score=50,  # 简历匹配度暂未实现
            skill_match_score=skill_match_score,
            personality_match_score=personality_match_score,
            overall_match_score=overall_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            personality_fit_analysis=f"大五人格匹配度: {personality_match_score}%",
            recommendation=recommendation,
            explanation=explanation
        )
    
    except Exception as e:
        logger.error(f"计算匹配度失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")
