"""
岗位匹配和推荐算法
用于计算候选人与岗位的匹配分数
"""

from typing import Optional, Dict, Any
from models.job import Job
from models.user import User
import math


def calculate_job_match_score(
    candidate: Optional[User],
    job: Job
) -> Dict[str, float]:
    """
    计算候选人与岗位的匹配分数
    返回 {"skill_match": 0-100, "personality_match": 0-100, "overall": 0-100}

    - skill_match:       技能关键词匹配 + 工作年限（权重 50%）
    - personality_match: 无人格数据时默认 50（权重 30%）
    - overall:           skill_match×0.5 + personality_match×0.3 + 其他因素×0.2
    """
    default = {"skill_match": 50.0, "personality_match": 50.0, "overall": 50.0}
    if not candidate or not job:
        return default

    # ── 1. skill_match：技能匹配 60% + 工作经验 40% ─────────────────────────
    skill_score = 0.0
    skill_max = 100.0

    # 技能关键词匹配（占 skill 总分 60%）
    if hasattr(candidate, "skills") and candidate.skills and job.required_traits:
        try:
            if isinstance(job.required_traits, dict):
                required_skills = {k.strip().lower() for k in job.required_traits.keys()}
            else:
                required_skills = {s.strip().lower() for s in str(job.required_traits).split(",") if s.strip()}
            candidate_skills = {s.strip().lower() for s in candidate.skills.split(",") if s.strip()}
            if required_skills:
                match_ratio = len(candidate_skills & required_skills) / len(required_skills)
                skill_score += 60 * match_ratio
        except Exception:
            skill_score += 30  # 解析失败时部分分

    # 工作经验（占 skill 总分 40%）
    if hasattr(candidate, "work_experience") and candidate.work_experience:
        exp_years = min(float(candidate.work_experience), 15)
        skill_score += (exp_years / 15) * 40

    skill_match = min(100.0, max(0.0, skill_score))

    # ── 2. personality_match：此函数无人格画像，置为中性 ──────────────────────
    personality_match = 50.0

    # ── 3. 其他因素（城市 50% + 薪资 50%）────────────────────────────────────
    other_score = 0.0
    other_max = 100.0

    # 城市匹配
    if hasattr(candidate, "city") and candidate.city:
        other_score += 50 if job.city == candidate.city else 20

    # 薪资期望匹配
    if hasattr(candidate, "salary_expectation") and candidate.salary_expectation:
        c_sal = float(candidate.salary_expectation)
        j_min = float(job.salary_min or 0)
        j_max = float(job.salary_max or 999)
        if j_min <= c_sal <= j_max:
            other_score += 50
        elif c_sal < j_min:
            gap = (j_min - c_sal) / max(j_min, 1)
            other_score += max(0, 50 - gap * 50)
        else:
            gap = (c_sal - j_max) / max(j_max, 1)
            other_score += max(0, 50 - gap * 30)

    other_factor = min(100.0, max(0.0, other_score))

    # ── 4. overall ────────────────────────────────────────────────────────────
    overall = min(100.0, max(0.0,
        0.5 * skill_match + 0.3 * personality_match + 0.2 * other_factor
    ))

    return {
        "skill_match": round(skill_match, 1),
        "personality_match": round(personality_match, 1),
        "overall": round(overall, 1),
    }


def calculate_recommendation_index(
    job: Job,
    candidate_count: int = 0,
    saved_count: int = 0,
    applied_count: int = 0
) -> float:
    """
    计算岗位的推荐指数（基于热度和互动）
    
    Args:
        job: 岗位对象
        candidate_count: 关注此岗位的候选人数
        saved_count: 收藏此岗位的候选人数
        applied_count: 应聘此岗位的候选人数
    
    Returns:
        float: 推荐指数 (0-100)
    """
    index = 50.0  # 基础分
    
    # 根据收藏数增加指数
    if saved_count > 0:
        index += min(20, saved_count * 2)
    
    # 根据应聘数增加指数
    if applied_count > 0:
        index += min(15, applied_count * 1.5)
    
    # 根据关注度增加指数  
    if candidate_count > 0:
        index += min(15, math.log(candidate_count + 1) * 5)
    
    return min(100.0, index)


def get_job_display_data(job: Job, candidate: Optional[User] = None) -> Dict[str, Any]:
    """
    获取岗位的完整展示数据（包含匹配分数等）
    
    Returns:
        dict: 包含所有展示信息的字典
    """
    match_score = calculate_job_match_score(candidate, job)["overall"] if candidate else 50.0
    
    return {
        "id": job.id,
        "name": job.name,
        "company": job.company,
        "city": job.city,
        "category": job.category,
        "salary": job.salary,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "description": job.description,
        "required_traits": job.required_traits,
        "match_score": round(match_score, 1),
        "match_level": get_match_level(match_score),
    }


def get_match_level(score: float) -> str:
    """根据匹配分数获取匹配等级"""
    if score >= 80:
        return "极佳"
    elif score >= 65:
        return "良好"
    elif score >= 50:
        return "一般"
    else:
        return "较低"
