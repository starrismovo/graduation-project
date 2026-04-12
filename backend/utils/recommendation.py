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
) -> float:
    """
    计算候选人与岗位的匹配分数（0-100）
    
    Args:
        candidate: 候选人对象
        job: 岗位对象
    
    Returns:
        float: 匹配分数 (0-100)
    """
    if not candidate or not job:
        return 50.0  # 默认中等分数
    
    score = 0.0
    max_score = 0.0
    
    # 1. 城市匹配 (权重: 15%)
    max_score += 15
    if hasattr(candidate, 'city') and candidate.city and job.city == candidate.city:
        score += 15
    elif hasattr(candidate, 'city') and candidate.city:
        score += 7  # 不同城市但有意向
    
    # 2. 职位级别匹配 (权重: 20%)
    max_score += 20
    if hasattr(candidate, 'job_level') and candidate.job_level and job.category:
        if candidate.job_level.lower() in job.category.lower():
            score += 20
        else:
            score += 10
    
    # 3. 薪资期望匹配 (权重: 25%)
    max_score += 25
    if hasattr(candidate, 'salary_expectation') and candidate.salary_expectation:
        candidate_salary = candidate.salary_expectation
        job_min = job.salary_min or 0
        job_max = job.salary_max or 999
        
        if job_min <= candidate_salary <= job_max:
            score += 25  # 完美匹配
        elif candidate_salary < job_min:
            gap_ratio = (job_min - candidate_salary) / job_min
            score += max(0, 25 - gap_ratio * 25)
        else:
            gap_ratio = (candidate_salary - job_max) / job_max
            score += max(0, 25 - gap_ratio * 15)  # 超薪资不扣那么多分
    
    # 4. 技能匹配 (权重: 20%)
    max_score += 20
    if hasattr(candidate, 'skills') and candidate.skills and job.required_traits:
        try:
            candidate_skills = set(s.strip().lower() for s in candidate.skills.split(',') if s.strip())
            required_skills = set(s.strip().lower() for s in job.required_traits.split(',') if s.strip())
            
            if required_skills:
                matched = len(candidate_skills & required_skills)
                match_ratio = matched / len(required_skills)
                score += 20 * match_ratio
        except:
            score += 10  # 默认部分匹配
    
    # 5. 工作经验 (权重: 20%)
    max_score += 20
    if hasattr(candidate, 'work_experience') and candidate.work_experience:
        exp_years = min(candidate.work_experience, 15)  # 15年上限
        score += (exp_years / 15) * 20
    
    # 归一化到 0-100
    if max_score > 0:
        normalized_score = (score / max_score) * 100
    else:
        normalized_score = 50.0
    
    return min(100.0, max(0.0, normalized_score))


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
    match_score = calculate_job_match_score(candidate, job) if candidate else 50.0
    
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
