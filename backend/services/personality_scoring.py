"""
Versioned Big Five scoring service.

This service centralizes the mapping from interview ability scores to
Big Five personality scores to avoid frontend/backend scoring drift.
"""

from typing import Dict, Any, Tuple


SCORING_MODEL_VERSION = "bigfive_map_v1_2026_04"

BIG_FIVE_TRAITS = ["外向性", "宜人性", "尽责性", "神经质", "开放性"]

BIG_FIVE_TRAIT_ALIASES = {
    "外向性": "外向性",
    "外倾性": "外向性",
    "extroversion": "外向性",
    "extraversion": "外向性",
    "宜人性": "宜人性",
    "亲和性": "宜人性",
    "agreeableness": "宜人性",
    "尽责性": "尽责性",
    "责任心": "尽责性",
    "conscientiousness": "尽责性",
    "神经质": "神经质",
    "neuroticism": "神经质",
    "开放性": "开放性",
    "开放度": "开放性",
    "openness": "开放性",
}

REVERSED_TRAIT_ALIASES = {
    "情绪稳定性": "神经质",
    "emotional_stability": "神经质",
    "stability": "神经质",
}


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


def _normalize_score_scale(value: float) -> float:
    """Accept both 0-10 and 0-100 Big Five inputs, then normalize to 0-10."""
    value = float(value)
    if value > 10.0:
        value = value / 10.0
    return _clamp_score(value)


def normalize_big_five_scores(scores: Dict[str, float] | None) -> Dict[str, float]:
    """Normalize Big Five trait keys to Chinese labels used by reports."""
    normalized: Dict[str, float] = {}
    for raw_key, raw_value in (scores or {}).items():
        key_text = str(raw_key).strip()
        trait = BIG_FIVE_TRAIT_ALIASES.get(key_text)
        is_reversed = False
        if not trait:
            trait = REVERSED_TRAIT_ALIASES.get(key_text)
            is_reversed = trait is not None
        if not trait:
            continue
        try:
            value = _normalize_score_scale(float(raw_value))
        except (TypeError, ValueError):
            continue
        if is_reversed:
            value = 10.0 - value
        normalized[trait] = _clamp_score(value)
    return normalized


def _ability_score(scores: Dict[str, float], key: str) -> float | None:
    if key not in scores:
        return None
    return _clamp_score(scores[key])


def _weighted_average(parts: list[tuple[float | None, float]]) -> float | None:
    valid = [(score, weight) for score, weight in parts if score is not None]
    if not valid:
        return None
    total_weight = sum(weight for _, weight in valid)
    return sum(float(score) * weight for score, weight in valid) / total_weight


def score_big_five_from_abilities(all_scores: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Compute Big Five scores from interview ability dimensions.
    Returns (scores, metadata).
    """
    src = _sanitize_scores(all_scores)

    communication = _ability_score(src, "沟通能力") or _ability_score(src, "表达能力")
    teamwork = _ability_score(src, "团队协作") or _ability_score(src, "团队合作")
    problem = _ability_score(src, "问题解决") or _ability_score(src, "逻辑思维")
    technical = _ability_score(src, "技术深度") or _ability_score(src, "专业能力")
    innovation = _ability_score(src, "创新能力") or _ability_score(src, "创新思维")
    learning = _ability_score(src, "学习能力")

    result: Dict[str, float] = {}
    extraversion = _weighted_average([(communication, 0.5), (teamwork, 0.5)])
    agreeableness = _weighted_average([(teamwork, 0.6), (communication, 0.4)])
    conscientiousness = _weighted_average([(technical, 0.5), (problem, 0.5)])
    stability = _weighted_average([(problem, 0.4), (communication, 0.3), (technical, 0.3)])
    openness = _weighted_average([(innovation, 0.5), (learning, 0.5)])

    if extraversion is not None:
        result["外向性"] = _clamp_score(extraversion)
    if agreeableness is not None:
        result["宜人性"] = _clamp_score(agreeableness)
    if conscientiousness is not None:
        result["尽责性"] = _clamp_score(conscientiousness)
    if stability is not None:
        result["神经质"] = _clamp_score(10.0 - stability)
    if openness is not None:
        result["开放性"] = _clamp_score(openness)

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
        normalized = normalize_big_five_scores(personality_scores)
        return normalized, {
            "model_version": SCORING_MODEL_VERSION,
            "source": "request_personality_scores",
            "input_dimensions": sorted(list((personality_scores or {}).keys())),
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
        basic = normalize_big_five_scores(basic_traits)
        return basic, {
            trait: 0.0 for trait in basic.keys()
        }
    
    basic = normalize_big_five_scores(basic_traits)
    job_req = normalize_big_five_scores(job_personality_requirements)
    
    scenario = {}
    adjustments = {}
    
    for trait in BIG_FIVE_TRAITS:
        if trait not in basic or trait not in job_req:
            continue
        base_score = basic[trait]
        job_need = job_req[trait]
        
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
    basic = normalize_big_five_scores(basic_traits)
    scenario = normalize_big_five_scores(scenario_traits)
    job_req = normalize_big_five_scores(job_requirements or {})
    
    comparison = {}
    
    for trait in BIG_FIVE_TRAITS:
        if trait not in basic and trait not in scenario and trait not in job_req:
            continue
        base = basic.get(trait)
        scene = scenario.get(trait, base)
        job_need = job_req.get(trait)
        if base is None or scene is None or job_need is None:
            continue
        
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
            "gap": round(job_need - scene, 1),  # 与岗位需求的差距（负数表示超出）
        }
    
    return comparison
