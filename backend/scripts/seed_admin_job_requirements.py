"""Seed structured requirements for admin Job Instances.

The script is idempotent for admin's eight manually published jobs:
- rewrites required_traits and personality_requirements with Chinese Big Five
  keys in 1-10 scale;
- creates/updates JobPersonalityFramework in 0-100 scale;
- replaces JobSkillRequirement rows with deterministic structured skills.
"""

from __future__ import annotations

import json
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)

from database import SessionLocal, engine
from models.job import Job
from models.job_requirement import JobPersonalityFramework, JobSkillRequirement
from models.user import User


TRAIT_ALIASES = {
    "openness": "开放性",
    "conscientiousness": "尽责性",
    "extraversion": "外向性",
    "extroversion": "外向性",
    "agreeableness": "宜人性",
    "neuroticism": "神经质",
    "emotional_stability": "神经质",
    "开放性": "开放性",
    "尽责性": "尽责性",
    "外向性": "外向性",
    "宜人性": "宜人性",
    "神经质": "神经质",
}

CHINESE_TRAITS = ["开放性", "尽责性", "外向性", "宜人性", "神经质"]


@dataclass(frozen=True)
class SkillSpec:
    name: str
    skill_type: str
    level: str
    years: int
    must: bool
    priority: float


JOB_REQUIREMENTS: Dict[str, List[SkillSpec]] = {
    "Java 高级后端工程师": [
        SkillSpec("Java", "programming_language", "expert", 4, True, 10),
        SkillSpec("Spring Boot", "framework", "expert", 3, True, 9),
        SkillSpec("MySQL", "database", "intermediate", 3, True, 8),
        SkillSpec("Redis", "database", "intermediate", 2, True, 8),
        SkillSpec("微服务", "architecture", "intermediate", 3, False, 7),
    ],
    "前端开发工程师（React/Vue）": [
        SkillSpec("React", "framework", "intermediate", 2, True, 9),
        SkillSpec("Vue", "framework", "intermediate", 2, True, 9),
        SkillSpec("TypeScript", "programming_language", "intermediate", 2, True, 8),
        SkillSpec("Element Plus", "framework", "junior", 1, False, 6),
        SkillSpec("用户体验", "methodology", "junior", 1, False, 6),
    ],
    "算法工程师（推荐系统）": [
        SkillSpec("Python", "programming_language", "expert", 3, True, 9),
        SkillSpec("推荐系统", "methodology", "expert", 2, True, 10),
        SkillSpec("机器学习", "methodology", "expert", 3, True, 9),
        SkillSpec("特征工程", "methodology", "intermediate", 2, True, 8),
        SkillSpec("A/B实验", "methodology", "intermediate", 1, False, 7),
    ],
    "产品经理（B端 SaaS）": [
        SkillSpec("产品思维", "methodology", "expert", 3, True, 10),
        SkillSpec("用户研究", "methodology", "intermediate", 2, True, 8),
        SkillSpec("需求分析", "methodology", "expert", 3, True, 9),
        SkillSpec("SQL基础", "tool", "junior", 1, False, 5),
        SkillSpec("数据看板", "tool", "junior", 1, False, 5),
    ],
    "数据分析师": [
        SkillSpec("Python", "programming_language", "intermediate", 2, True, 8),
        SkillSpec("SQL基础", "database", "expert", 2, True, 10),
        SkillSpec("数据看板", "tool", "intermediate", 2, True, 8),
        SkillSpec("A/B实验", "methodology", "intermediate", 1, False, 7),
        SkillSpec("特征工程", "methodology", "junior", 1, False, 5),
    ],
    "UI/UX 设计师": [
        SkillSpec("Figma", "tool", "expert", 2, True, 10),
        SkillSpec("用户研究", "methodology", "intermediate", 2, True, 8),
        SkillSpec("交互设计", "methodology", "expert", 3, True, 9),
        SkillSpec("视觉设计", "methodology", "expert", 3, True, 9),
        SkillSpec("可用性测试", "methodology", "intermediate", 1, False, 7),
    ],
    "运营专员（增长运营）": [
        SkillSpec("用户运营", "methodology", "intermediate", 1, True, 9),
        SkillSpec("活动策划", "methodology", "intermediate", 1, True, 8),
        SkillSpec("数据看板", "tool", "junior", 1, True, 7),
        SkillSpec("Excel", "tool", "intermediate", 1, True, 7),
        SkillSpec("SQL基础", "database", "junior", 1, False, 5),
    ],
    "安全工程师（Web/移动端）": [
        SkillSpec("Java", "programming_language", "intermediate", 2, False, 6),
        SkillSpec("Python", "programming_language", "intermediate", 2, True, 8),
        SkillSpec("安全", "methodology", "expert", 3, True, 10),
        SkillSpec("Web安全", "methodology", "expert", 3, True, 9),
        SkillSpec("移动端安全", "methodology", "intermediate", 2, True, 8),
    ],
}


def clamp_1_10(value: float) -> float:
    return round(max(1.0, min(10.0, float(value))), 1)


def normalize_required_traits(raw: Dict[str, float] | None) -> Dict[str, float]:
    normalized = {trait: 5.0 for trait in CHINESE_TRAITS}
    for key, value in (raw or {}).items():
        trait = TRAIT_ALIASES.get(str(key), str(key))
        if trait not in CHINESE_TRAITS:
            continue
        normalized[trait] = clamp_1_10(value)
    return normalized


def framework_range(score_1_10: float, trait: str) -> tuple[float, float]:
    center = clamp_1_10(score_1_10) * 10
    if trait == "神经质":
        return 0.0, min(100.0, center + 15)
    return max(0.0, center - 15), 100.0


def upsert_framework(db, job: Job, traits: Dict[str, float]) -> JobPersonalityFramework:
    fw = db.query(JobPersonalityFramework).filter(JobPersonalityFramework.job_id == job.id).first()
    if not fw:
        fw = JobPersonalityFramework(job_id=job.id)
        db.add(fw)

    fw.openness_min, fw.openness_max = framework_range(traits["开放性"], "开放性")
    fw.conscientiousness_min, fw.conscientiousness_max = framework_range(traits["尽责性"], "尽责性")
    fw.extraversion_min, fw.extraversion_max = framework_range(traits["外向性"], "外向性")
    fw.agreeableness_min, fw.agreeableness_max = framework_range(traits["宜人性"], "宜人性")
    fw.neuroticism_min, fw.neuroticism_max = framework_range(traits["神经质"], "神经质")

    fw.openness_weight = 1.2 if traits["开放性"] >= 7.5 else 1.0
    fw.conscientiousness_weight = 1.6 if traits["尽责性"] >= 8 else 1.3
    fw.extraversion_weight = 1.2 if traits["外向性"] >= 7 else 1.0
    fw.agreeableness_weight = 1.2 if traits["宜人性"] >= 7 else 1.0
    fw.neuroticism_weight = 1.4 if traits["神经质"] <= 3.5 else 1.1
    fw.description = f"{job.name} 的岗位人格框架由 required_traits 统一换算生成，0-100量纲用于匹配引擎。"
    return fw


def replace_skill_requirements(db, job: Job) -> int:
    specs = JOB_REQUIREMENTS.get(job.name)
    if not specs:
        return 0
    db.query(JobSkillRequirement).filter(JobSkillRequirement.job_id == job.id).delete(synchronize_session=False)
    for spec in specs:
        db.add(JobSkillRequirement(
            job_id=job.id,
            skill_name=spec.name,
            skill_type=spec.skill_type,
            required_level=spec.level,
            years_experience=spec.years,
            is_must_have=spec.must,
            priority_score=spec.priority,
        ))
    return len(specs)


def main() -> int:
    engine.echo = False
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            raise RuntimeError("未找到 username=admin 的 HR 用户")

        jobs = db.query(Job).filter(Job.creator_id == admin.id).order_by(Job.id.asc()).all()
        summary = []
        for job in jobs:
            traits = normalize_required_traits(job.required_traits)
            job.required_traits = traits
            job.personality_requirements = traits
            skill_count = replace_skill_requirements(db, job)
            upsert_framework(db, job, traits)
            summary.append({
                "job_id": job.id,
                "job_name": job.name,
                "skill_requirements": skill_count,
                "required_traits": traits,
            })
        db.commit()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
