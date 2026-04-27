"""
Versioned Big Five scoring service.

This service centralizes the mapping from interview ability scores to
Big Five personality scores to avoid frontend/backend scoring drift.
"""

from typing import Dict, Any, Tuple


SCORING_MODEL_VERSION = "bigfive_map_v1_2026_04"

BIG_FIVE_TRAITS = ["外向性", "宜人性", "尽责性", "神经质", "开放性"]


def _clamp_score(score: float, low: float = 0.0, high: float = 10.0) -> float:
    return max(low, min(high, float(score)))


def _sanitize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    sanitized: Dict[str, float] = {}
    for key, value in (scores or {}).items():
        try:
            sanitized[key] = _clamp_score(float(value))
        except (TypeError, ValueError):
            continue
    return sanitized


def _ability_score(scores: Dict[str, float], key: str, default: float = 5.0) -> float:
    return _clamp_score(scores.get(key, default))


def score_big_five_from_abilities(all_scores: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Compute Big Five scores from interview ability dimensions.
    Returns (scores, metadata).
    """
    src = _sanitize_scores(all_scores)

    extraversion = (
        _ability_score(src, "表达能力") * 0.5 +
        _ability_score(src, "团队合作") * 0.5
    )
    agreeableness = (
        _ability_score(src, "团队合作") * 0.6 +
        _ability_score(src, "表达能力") * 0.4
    )
    conscientiousness = (
        _ability_score(src, "专业能力") * 0.5 +
        _ability_score(src, "逻辑思维") * 0.5
    )
    neuroticism = 10.0 - (
        _ability_score(src, "逻辑思维") * 0.4 +
        _ability_score(src, "表达能力") * 0.3 +
        _ability_score(src, "专业能力") * 0.3
    )
    openness = (
        _ability_score(src, "创新思维") * 0.5 +
        _ability_score(src, "学习能力") * 0.5
    )

    result = {
        "外向性": _clamp_score(extraversion),
        "宜人性": _clamp_score(agreeableness),
        "尽责性": _clamp_score(conscientiousness),
        "神经质": _clamp_score(neuroticism),
        "开放性": _clamp_score(openness),
    }

    metadata = {
        "model_version": SCORING_MODEL_VERSION,
        "source": "derived_from_all_scores",
        "input_dimensions": sorted(list(src.keys())),
    }
    return result, metadata


def resolve_personality_scores(
    all_scores: Dict[str, float],
    personality_scores: Dict[str, float] | None = None,
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Resolve final personality scores.
    - Prefer explicit `personality_scores` when provided (for compatibility).
    - Otherwise derive from `all_scores` using the versioned mapping.
    """
    if personality_scores:
        sanitized = _sanitize_scores(personality_scores)
        normalized = {
            "外向性": sanitized.get("外向性", sanitized.get("extraversion", 5.0)),
            "宜人性": sanitized.get("宜人性", sanitized.get("agreeableness", 5.0)),
            "尽责性": sanitized.get("尽责性", sanitized.get("conscientiousness", 5.0)),
            "神经质": sanitized.get("神经质", sanitized.get("neuroticism", 5.0)),
            "开放性": sanitized.get("开放性", sanitized.get("openness", 5.0)),
        }
        return {
            trait: _clamp_score(score)
            for trait, score in normalized.items()
        }, {
            "model_version": SCORING_MODEL_VERSION,
            "source": "request_personality_scores",
            "input_dimensions": sorted(list(sanitized.keys())),
        }

    return score_big_five_from_abilities(all_scores or {})


def calculate_scenario_traits(
    basic_traits: Dict[str, float],
    job_personality_requirements: Dict[str, float] | None = None,
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    计算场景人格（根据论文第4.3.3节）
    
    公式：p_scene(i) = p_base(i) + Δp(i)
    
    其中：
    - p_base(i)：候选人在第i个维度的基础人格评分（1-10）
    - Δp(i)：岗位需求与候选人基础人格的"调适偏移"，范围为[-2, +2]
    - p_scene(i)：候选人在该岗位情景下的预期人格表现评分
    
    Args:
        basic_traits: 基础人格评分，格式为 {"外向性": 6.0, "宜人性": 7.0, ...}
        job_personality_requirements: 岗位人格需求，格式为 {"外向性": 7.0, "宜人性": 8.0, ...}
    
    Returns:
        (scenario_traits, adjustments)：
        - scenario_traits: 场景人格评分
        - adjustments: 各维度的调适偏移值
    """
    if not job_personality_requirements:
        # 如果没有岗位需求，场景人格 = 基础人格（无调适）
        return _sanitize_scores(basic_traits), {
            trait: 0.0 for trait in _sanitize_scores(basic_traits).keys()
        }
    
    basic = _sanitize_scores(basic_traits)
    job_req = _sanitize_scores(job_personality_requirements)
    
    scenario = {}
    adjustments = {}
    
    for trait in BIG_FIVE_TRAITS:
        base_score = basic.get(trait, 5.0)
        job_need = job_req.get(trait, 5.0)
        
        # 计算调适偏移 Δp(i)
        difference = base_score - job_need
        
        if abs(difference) <= 1.0:
            # 匹配较好：无调适 (-2 < difference < 2)
            adjustment = 0.0
        elif difference > 0:
            # 候选人该维度高于岗位需求：抑制该特质
            # 调适幅度：基础幅度 -0.5，强需求时增强到 -1.0
            adjustment = -0.5 if job_need < 8.0 else -1.0
        else:
            # 候选人该维度低于岗位需求：提升该特质
            # 调适幅度：基础幅度 +0.5，强需求时增强到 +1.0
            adjustment = 0.5 if job_need < 8.0 else 1.0
        
        # 如果岗位对该维度要求极高（≥8分），可以增强调适偏移
        if job_need >= 8.0 and abs(difference) > 1.0:
            adjustment = max(-1.0, min(1.0, adjustment * 1.5))
        
        # 计算场景人格 = 基础人格 + 调适偏移
        scenario_score = _clamp_score(base_score + adjustment)
        
        scenario[trait] = scenario_score
        adjustments[trait] = _clamp_score(adjustment, -2.0, 2.0)
    
    return scenario, adjustments


def get_trait_comparison(
    basic_traits: Dict[str, float],
    scenario_traits: Dict[str, float],
    job_requirements: Dict[str, float] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """
    生成特质对比报告（基础人格 vs 场景人格 vs 岗位需求）
    
    返回格式：
    {
        "外向性": {
            "basic_trait": 6.0,
            "scenario_trait": 6.5,
            "job_requirement": 7.0,
            "match_degree": 4  # 星级匹配度 (1-5)
        },
        ...
    }
    """
    basic = _sanitize_scores(basic_traits)
    scenario = _sanitize_scores(scenario_traits)
    job_req = _sanitize_scores(job_requirements or {})
    
    comparison = {}
    
    for trait in BIG_FIVE_TRAITS:
        base = basic.get(trait, 5.0)
        scene = scenario.get(trait, base)
        job_need = job_req.get(trait, 5.0)
        
        # 计算场景人格与岗位需求的匹配度（1-5星）
        difference = abs(scene - job_need)
        if difference <= 0.5:
            match_degree = 5  # ★★★★★ 完美匹配
        elif difference <= 1.0:
            match_degree = 4  # ★★★★☆ 很好匹配
        elif difference <= 1.5:
            match_degree = 3  # ★★★☆☆ 一般匹配
        elif difference <= 2.0:
            match_degree = 2  # ★★☆☆☆ 较差匹配
        else:
            match_degree = 1  # ★☆☆☆☆ 不匹配
        
        comparison[trait] = {
            "basic_trait": _clamp_score(base),
            "scenario_trait": _clamp_score(scene),
            "job_requirement": _clamp_score(job_need),
            "match_degree": match_degree,
            "gap": _clamp_score(job_need - scene),  # 与岗位需求的差距（负数表示超出）
        }
    
    return comparison
