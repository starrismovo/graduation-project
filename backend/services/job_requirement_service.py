"""
岗位需求解析服务
使用 LLM 将岗位描述（JD）转化为结构化标签
"""

import json
import logging
from typing import Optional, List, Dict, Tuple
from schemas.job_requirement import (
    JobSkillRequirementSchema,
    JobRequirementTagSchema,
    JobPersonalityFrameworkSchema
)

logger = logging.getLogger(__name__)

# 预定义的技能映射库
SKILL_LIBRARY = {
    "python": {"type": "programming_language", "category": "backend"},
    "javascript": {"type": "programming_language", "category": "frontend"},
    "typescript": {"type": "programming_language", "category": "frontend"},
    "java": {"type": "programming_language", "category": "backend"},
    "go": {"type": "programming_language", "category": "backend"},
    "rust": {"type": "programming_language", "category": "backend"},
    "react": {"type": "framework", "category": "frontend"},
    "vue": {"type": "framework", "category": "frontend"},
    "django": {"type": "framework", "category": "backend"},
    "fastapi": {"type": "framework", "category": "backend"},
    "spring": {"type": "framework", "category": "backend"},
    "kubernetes": {"type": "tool", "category": "devops"},
    "docker": {"type": "tool", "category": "devops"},
    "aws": {"type": "tool", "category": "devops"},
    "postgresql": {"type": "tool", "category": "database"},
    "mysql": {"type": "tool", "category": "database"},
    "mongodb": {"type": "tool", "category": "database"},
    "redis": {"type": "tool", "category": "database"},
    "linux": {"type": "tool", "category": "system"},
    "git": {"type": "tool", "category": "methodology"},
    "agile": {"type": "methodology", "category": "methodology"},
    "scrum": {"type": "methodology", "category": "methodology"},
}

# 岗位类别与人格特质的默认映射
ROLE_PERSONALITY_DEFAULTS = {
    "backend": {
        "conscientiousness_min": 70,
        "extraversion_min": 20,
        "neuroticism_max": 50
    },
    "frontend": {
        "conscientiousness_min": 60,
        "extraversion_min": 30,
        "openness_min": 60,
        "neuroticism_max": 60
    },
    "product": {
        "conscientiousness_min": 65,
        "extraversion_min": 60,
        "agreeableness_min": 60,
        "openness_min": 70
    },
    "design": {
        "openness_min": 70,
        "agreeableness_min": 60,
        "conscientiousness_min": 55,
        "neuroticism_max": 65
    },
    "hr": {
        "extraversion_min": 70,
        "agreeableness_min": 75,
        "conscientiousness_min": 65
    },
    "management": {
        "extraversion_min": 65,
        "agreeableness_min": 55,
        "conscientiousness_min": 75,
        "openness_min": 60
    }
}


class JDParser:
    """岗位描述解析器"""
    
    @staticmethod
    def extract_skills_from_text(jd_text: str) -> List[JobSkillRequirementSchema]:
        """从 JD 文本中提取技能需求"""
        skills = []
        jd_text_lower = jd_text.lower()
        
        for skill_name, skill_info in SKILL_LIBRARY.items():
            # 简单的关键词匹配
            if skill_name in jd_text_lower:
                # 判断是否是必需（通过关键词"必须", "需要"等）
                is_must_have = any(w in jd_text_lower for w in ['必须', '必需', 'required', 'must have'])
                
                # 判断经验年数（通过关键词"3年", "5+年"等）
                years = JDParser._extract_years(jd_text, skill_name)
                
                # 判断等级（通过关键词"精通", "熟练"等）
                level = JDParser._extract_proficiency_level(jd_text, skill_name)
                
                priority = 9 if is_must_have else 6
                
                skill_schema = JobSkillRequirementSchema(
                    skill_name=skill_name.capitalize(),
                    skill_type=skill_info.get("type", "tool"),
                    required_level=level,
                    years_experience=years,
                    is_must_have=is_must_have,
                    priority_score=priority
                )
                skills.append(skill_schema)
                logger.info(f"提取技能: {skill_name}")
        
        return skills
    
    @staticmethod
    def _extract_years(text: str, skill_name: str) -> Optional[int]:
        """提取技能所需的年数"""
        # 简单实现：查找 "3+" 或 "3年" 的模式
        import re
        
        # 查找 "3年" "5+"  等模式
        pattern = rf'({skill_name}|经验|年)*\s*(\d+)\s*(\+)?年'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            for match in matches:
                if match[1]:
                    return int(match[1])
        return None
    
    @staticmethod
    def _extract_proficiency_level(text: str, skill_name: str) -> Optional[str]:
        """提取技能所需的等级"""
        text_lower = text.lower()
        
        # 查找技能附近的等级描述
        if any(w in text_lower for w in ['精通', 'expert', 'proficient']):
            return "expert"
        elif any(w in text_lower for w in ['熟练', 'senior', 'advanced']):
            return "intermediate"
        elif any(w in text_lower for w in ['了解', 'basic', 'junior']):
            return "junior"
        
        return "intermediate"  # 默认中级
    
    @staticmethod
    def generate_capability_tags(
        jd_text: str,
        role_category: str = "backend"
    ) -> List[JobRequirementTagSchema]:
        """生成能力项标签"""
        tags = []
        
        # 预定义的能力项映射
        capability_keywords = {
            "需求分析": ["需求", "理解", "沟通", "stakeholder"],
            "代码能力": ["编程", "算法", "代码质量", "refactor"],
            "系统设计": ["架构", "设计", "扩展性", "可维护"],
            "团队协作": ["团队", "沟通", "协作", "code review"],
            "问题解决": ["问题", "debug", "troubleshoot", "解决"],
            "技术学习": ["学习", "研究", "新技术", "持续改进"],
            "项目管理": ["项目", "计划", "风险", "timeline"],
            "客户服务": ["客户", "用户", "服务", "体验"],
        }
        
        jd_text_lower = jd_text.lower()
        
        for capability, keywords in capability_keywords.items():
            # 检查关键词是否出现
            if any(kw in jd_text_lower for kw in keywords):
                tag = JobRequirementTagSchema(
                    capability_name=capability,
                    capability_category="素质" if "协作" in capability or "学习" in capability else "技能",
                    importance_level="high" if any(w in jd_text_lower for w in [capability + "必须", f"{capability}主要"]) else "medium",
                    personality_dimension=None  # 稍后由 HR 手动设置
                )
                tags.append(tag)
                logger.info(f"生成能力标签: {capability}")
        
        return tags
    
    @staticmethod
    def generate_personality_framework(
        role_category: str = "backend"
    ) -> JobPersonalityFrameworkSchema:
        """根据岗位类别生成默认的人格框架"""
        
        defaults = ROLE_PERSONALITY_DEFAULTS.get(role_category.lower(), {})
        
        framework = JobPersonalityFrameworkSchema(
            openness_min=defaults.get("openness_min", 30),
            openness_max=100,
            openness_weight=1.0,
            
            conscientiousness_min=defaults.get("conscientiousness_min", 50),
            conscientiousness_max=100,
            conscientiousness_weight=1.5,
            
            extraversion_min=defaults.get("extraversion_min", 20),
            extraversion_max=100,
            extraversion_weight=1.0,
            
            agreeableness_min=defaults.get("agreeableness_min", 40),
            agreeableness_max=100,
            agreeableness_weight=1.0,
            
            neuroticism_min=0,
            neuroticism_max=defaults.get("neuroticism_max", 60),
            neuroticism_weight=1.2,
            
            description=f"针对 {role_category} 岗位优化的人格特质要求"
        )
        
        logger.info(f"生成 {role_category} 岗位的人格框架")
        return framework
    
    @staticmethod
    def parse_jd_with_llm(
        jd_text: str,
        role_category: str,
        use_llm: bool = False
    ) -> Tuple[List[JobSkillRequirementSchema], List[JobRequirementTagSchema], JobPersonalityFrameworkSchema]:
        """
        使用 LLM 或规则引擎解析 JD
        
        Args:
            jd_text: 原始岗位描述
            role_category: 岗位类别
            use_llm: 是否使用 LLM（暂未实现）
        
        Returns:
            (技能列表, 能力标签列表, 人格框架)
        """
        
        logger.info(f"开始解析 JD，类别: {role_category}")
        
        # Step 1: 提取技能
        skills = JDParser.extract_skills_from_text(jd_text)
        
        # Step 2: 生成能力标签
        tags = JDParser.generate_capability_tags(jd_text, role_category)
        
        # Step 3: 生成人格框架
        personality_framework = JDParser.generate_personality_framework(role_category)
        
        logger.info(f"JD 解析完成: {len(skills)} 个技能, {len(tags)} 个能力标签")
        
        return skills, tags, personality_framework


class MatchingEngine:
    """岗位-候选人匹配引擎"""

    TRAIT_ALIASES = {
        "openness": "openness",
        "开放性": "openness",
        "conscientiousness": "conscientiousness",
        "尽责性": "conscientiousness",
        "责任心": "conscientiousness",
        "extraversion": "extraversion",
        "extroversion": "extraversion",
        "外向性": "extraversion",
        "agreeableness": "agreeableness",
        "宜人性": "agreeableness",
        "neuroticism": "neuroticism",
        "神经质": "neuroticism",
        "emotional_stability": "neuroticism",
        "情绪稳定性": "neuroticism",
    }

    @staticmethod
    def _normalize_percent_score(value: float) -> float:
        score = float(value)
        if score <= 10.0:
            score *= 10.0
        return max(0.0, min(100.0, score))

    @classmethod
    def _normalize_candidate_personality(cls, candidate_personality: Dict[str, float]) -> Dict[str, float]:
        normalized: Dict[str, float] = {}
        for raw_key, raw_value in (candidate_personality or {}).items():
            key_text = str(raw_key).strip()
            trait = cls.TRAIT_ALIASES.get(key_text)
            if not trait:
                continue
            try:
                score = cls._normalize_percent_score(float(raw_value))
            except (TypeError, ValueError):
                continue
            if key_text in {"emotional_stability", "情绪稳定性"}:
                score = 100.0 - score
            normalized[trait] = score
        return normalized

    @staticmethod
    def _range_fit_score(
        candidate_score: float,
        min_val: float,
        max_val: float,
        *,
        lower_is_better: bool = False,
    ) -> float:
        min_val = max(0.0, min(100.0, float(min_val)))
        max_val = max(min_val, min(100.0, float(max_val)))

        if lower_is_better:
            if candidate_score <= max_val:
                span = max(1.0, max_val - min_val)
                return 90.0 + (max_val - candidate_score) / span * 10.0
            return max(0.0, 100.0 - (candidate_score - max_val) * 6.0)

        if candidate_score < min_val:
            return max(0.0, 100.0 - (min_val - candidate_score) * 6.0)
        if candidate_score <= max_val:
            span = max(1.0, max_val - min_val)
            return 90.0 + (candidate_score - min_val) / span * 10.0
        return max(0.0, 100.0 - (candidate_score - max_val) * 4.0)
    
    @staticmethod
    def calculate_skill_match(
        candidate_skills: List[str],
        required_skills: List[JobSkillRequirementSchema]
    ) -> Tuple[float, List[str], List[str]]:
        """
        计算技能匹配度
        
        Returns:
            (匹配度 0-100, 已匹配的技能, 缺失的关键技能)
        """
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        matched = []
        missing = []
        
        total_priority = 0
        matched_priority = 0
        
        for skill_req in required_skills:
            skill_name_lower = skill_req.skill_name.lower()
            total_priority += skill_req.priority_score
            
            if skill_name_lower in candidate_skills_lower:
                matched.append(skill_req.skill_name)
                matched_priority += skill_req.priority_score
            elif skill_req.is_must_have:
                missing.append(skill_req.skill_name)
        
        # 计算匹配度
        match_score = (matched_priority / total_priority * 100) if total_priority > 0 else 0
        
        return round(match_score, 1), matched, missing
    
    @staticmethod
    def calculate_personality_match(
        candidate_personality: Dict[str, float],
        personality_framework: JobPersonalityFrameworkSchema
    ) -> float:
        """
        计算大五人格匹配度
        
        Args:
            candidate_personality: 候选人的大五人格评分 {"openness": 75, ...}
            personality_framework: 岗位要求的人格框架
        
        Returns:
            匹配度 0-100
        """
        
        candidate = MatchingEngine._normalize_candidate_personality(candidate_personality)
        dimensions = [
            ("openness", personality_framework.openness_min, personality_framework.openness_max, personality_framework.openness_weight),
            ("conscientiousness", personality_framework.conscientiousness_min, personality_framework.conscientiousness_max, personality_framework.conscientiousness_weight),
            ("extraversion", personality_framework.extraversion_min, personality_framework.extraversion_max, personality_framework.extraversion_weight),
            ("agreeableness", personality_framework.agreeableness_min, personality_framework.agreeableness_max, personality_framework.agreeableness_weight),
            ("neuroticism", personality_framework.neuroticism_min, personality_framework.neuroticism_max, personality_framework.neuroticism_weight),
        ]
        
        total_weight = 0
        weighted_match = 0
        
        for dimension, min_val, max_val, weight in dimensions:
            candidate_score = candidate.get(dimension)
            if candidate_score is None:
                continue

            fit = MatchingEngine._range_fit_score(
                candidate_score,
                min_val,
                max_val,
                lower_is_better=dimension == "neuroticism",
            )
            
            weighted_match += fit * weight
            total_weight += weight
        
        match_score = weighted_match / total_weight if total_weight > 0 else 50.0
        
        return round(match_score, 1)
    
    @staticmethod
    def calculate_overall_match(
        skill_match: float,
        personality_match: float,
        resume_match: Optional[float] = None
    ) -> float:
        """
        计算综合匹配度
        
        权重分配：
        - 技能匹配: 50%
        - 人格匹配: 30%
        - 简历匹配: 20%（可选）
        """
        
        if resume_match is not None:
            overall = skill_match * 0.5 + personality_match * 0.3 + resume_match * 0.2
        else:
            overall = skill_match * 0.6 + personality_match * 0.4
        
        return round(overall, 1)


# 单例实例
jd_parser = JDParser()
matching_engine = MatchingEngine()
