"""
Big Five rubric for Multi-Agent Interview.

The service keeps personality scoring in the backend and gives agents a
stable theory layer for Basic Personality and Scenario Personality.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


BIG_FIVE_DIMENSIONS: List[Dict[str, Any]] = [
    {
        "key": "openness",
        "name": "开放性",
        "aliases": ["openness", "开放性", "创新性", "学习开放性"],
        "indicators": ["学习新技术", "抽象思考", "接受变化", "创新表达", "迁移能力"],
    },
    {
        "key": "conscientiousness",
        "name": "尽责性",
        "aliases": ["conscientiousness", "尽责性", "责任心", "计划性", "质量意识"],
        "indicators": ["计划性", "责任感", "细节意识", "交付稳定性", "规范意识"],
    },
    {
        "key": "extraversion",
        "name": "外向性",
        "aliases": ["extraversion", "外向性", "表达主动性", "沟通主动性"],
        "indicators": ["表达主动性", "沟通舒适度", "协作参与度", "影响他人"],
    },
    {
        "key": "agreeableness",
        "name": "宜人性",
        "aliases": ["agreeableness", "宜人性", "合作性", "团队协作", "共情"],
        "indicators": ["合作意愿", "共情", "冲突处理", "团队适配", "支持他人"],
    },
    {
        "key": "emotional_stability",
        "name": "情绪稳定性",
        "aliases": ["emotional_stability", "情绪稳定性", "压力应对", "抗压", "稳定性"],
        "indicators": ["压力应对", "受挫反应", "风险情境稳定程度", "情绪调节"],
    },
]

TRAIT_ALIASES: Dict[str, str] = {}
for item in BIG_FIVE_DIMENSIONS:
    for alias in item["aliases"]:
        TRAIT_ALIASES[alias.lower()] = item["name"]
        TRAIT_ALIASES[alias] = item["name"]

# The legacy report model stores neuroticism. Convert emotional stability to
# neuroticism only at persistence/report boundaries when needed.
EMOTIONAL_STABILITY_NAME = "情绪稳定性"
NEUROTICISM_NAME = "神经质"


def clamp_score(value: Any, default: float = 5.0) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = default
    return round(max(0.0, min(10.0, score)), 2)


def rubric_text() -> str:
    lines = []
    for item in BIG_FIVE_DIMENSIONS:
        lines.append(f"- {item['name']}：{ '、'.join(item['indicators']) }")
    return "\n".join(lines)


def normalize_trait_name(name: Any) -> str | None:
    if name is None:
        return None
    raw = str(name).strip()
    if not raw:
        return None
    return TRAIT_ALIASES.get(raw, TRAIT_ALIASES.get(raw.lower()))


def normalize_trait_scores(scores: Dict[str, Any] | None, default: float | None = None) -> Dict[str, float]:
    normalized: Dict[str, float] = {}
    for raw_name, raw_score in (scores or {}).items():
        trait = normalize_trait_name(raw_name)
        if trait:
            normalized[trait] = clamp_score(raw_score, default=default if default is not None else 5.0)
    if default is not None:
        for item in BIG_FIVE_DIMENSIONS:
            normalized.setdefault(item["name"], clamp_score(default))
    return normalized


def emotional_stability_to_neuroticism(scores: Dict[str, Any] | None) -> Dict[str, float]:
    normalized = normalize_trait_scores(scores)
    result = {k: v for k, v in normalized.items() if k != EMOTIONAL_STABILITY_NAME}
    if EMOTIONAL_STABILITY_NAME in normalized:
        result[NEUROTICISM_NAME] = clamp_score(10.0 - normalized[EMOTIONAL_STABILITY_NAME])
    return result


def neuroticism_to_emotional_stability(scores: Dict[str, Any] | None) -> Dict[str, float]:
    result = normalize_trait_scores(scores)
    raw_neuroticism = None
    for key, value in (scores or {}).items():
        if str(key).strip() in {NEUROTICISM_NAME, "neuroticism"}:
            raw_neuroticism = value
            break
    if raw_neuroticism is not None and EMOTIONAL_STABILITY_NAME not in result:
        result[EMOTIONAL_STABILITY_NAME] = clamp_score(10.0 - clamp_score(raw_neuroticism))
    return result


def derive_trait_scores_from_response(
    *,
    candidate_response: str,
    depth_assessment: Dict[str, Any] | None = None,
    ability_scores: Dict[str, Any] | None = None,
    question_tags: List[str] | None = None,
    expected_traits: List[str] | None = None,
) -> Tuple[Dict[str, float], Dict[str, str], float]:
    """
    Conservative fallback scoring when the LLM does not return numeric Big Five.
    It is not a psychometric test; it only turns observable interview evidence
    into a bounded Scenario Personality estimate for this AssessmentSession.
    """
    text = candidate_response or ""
    depth_assessment = depth_assessment or {}
    ability_scores = ability_scores or {}
    question_tags = question_tags or []
    expected_traits = expected_traits or []

    base = 5.0
    if depth_assessment.get("answer_depth") == "deep":
        base += 0.8
    elif depth_assessment.get("answer_depth") == "shallow":
        base -= 0.7
    if depth_assessment.get("specificity") in {"specific", "detailed"}:
        base += 0.5
    elif depth_assessment.get("specificity") == "vague":
        base -= 0.5

    scores: Dict[str, float] = {}
    evidence: Dict[str, str] = {}

    def observe(raw_trait: str, delta: float, reason: str) -> None:
        trait = normalize_trait_name(raw_trait) or raw_trait
        if not trait:
            return
        scores[trait] = clamp_score(max(scores.get(trait, base), base + delta))
        evidence[trait] = reason

    if any(word in text for word in ["规范", "类型", "维护", "同步", "质量", "稳定", "复盘", "计划"]):
        observe("尽责性", 1.2, "回答体现规范意识、质量意识或复盘意识")
    if any(word in text for word in ["学习", "迁移", "新技术", "React", "Vue", "抽象", "创新"]):
        observe("开放性", 0.9, "回答体现学习迁移、创新或接受新方法的倾向")
    if any(word in text for word in ["团队", "协作", "共享", "成员", "PR", "评审", "说服", "相关方"]):
        observe("宜人性", 0.8, "回答体现协作意识、相关方理解或冲突协调")
    if any(word in text for word in ["沟通", "推动", "对齐", "共识", "汇报", "表达"]):
        observe("外向性", 0.5, "回答体现主动沟通、推动共识或表达影响")
    if any(word in text for word in ["压力", "不确定", "风险", "冲突", "紧急", "回滚", "止损"]):
        observe("情绪稳定性", 0.6, "回答体现压力或不确定情境下的判断与应对")

    star_markers = sum(
        1
        for word in ["背景", "当时", "问题", "行动", "方案", "权衡", "取舍", "结果", "指标", "上线", "%"]
        if word in text
    )
    if len(text) >= 90 and star_markers >= 4:
        for raw_trait in expected_traits + question_tags:
            trait = normalize_trait_name(raw_trait)
            if trait and trait not in scores:
                observe(trait, 0.7, "回答包含具体场景、行动步骤、取舍逻辑或结果指标，可形成该维度的场景人格线索")

    if ability_scores:
        ability_to_trait = {
            "沟通能力": "外向性",
            "学习能力": "开放性",
            "团队协作": "宜人性",
            "产品思维": "开放性",
            "用户洞察": "宜人性",
            "问题解决": "情绪稳定性",
        }
        for ability, trait in ability_to_trait.items():
            if ability in ability_scores and trait in scores:
                scores[trait] = clamp_score((scores[trait] + clamp_score(ability_scores[ability])) / 2)

    observed = len(evidence)
    confidence = clamp_score(4.0 + observed * 1.0 + (0.8 if len(text) > 80 else 0.0))
    return scores, evidence, confidence


def build_personality_observation(
    raw_observation: Dict[str, Any] | None,
    *,
    candidate_response: str,
    depth_assessment: Dict[str, Any] | None,
    ability_scores: Dict[str, Any] | None,
    question_tags: List[str] | None = None,
    expected_traits: List[str] | None = None,
) -> Dict[str, Any]:
    raw_observation = raw_observation or {}
    raw_basic = raw_observation.get("basic_trait_scores") or raw_observation.get("trait_scores") or {}
    raw_scenario = raw_observation.get("scenario_trait_scores") or {}

    basic_scores = normalize_trait_scores(raw_basic)
    scenario_scores = normalize_trait_scores(raw_scenario)
    fallback_scores, fallback_evidence, confidence = derive_trait_scores_from_response(
        candidate_response=candidate_response,
        depth_assessment=depth_assessment,
        ability_scores=ability_scores,
        question_tags=question_tags,
        expected_traits=expected_traits,
    )

    for trait, score in fallback_scores.items():
        basic_scores.setdefault(trait, score)
        scenario_scores.setdefault(trait, score)

    raw_evidence = raw_observation.get("trait_evidence") or {}
    trait_evidence: Dict[str, str] = {}
    for item in BIG_FIVE_DIMENSIONS:
        trait = item["name"]
        raw_text = str(raw_evidence.get(trait) or "").strip()
        fallback_text = fallback_evidence.get(trait, "")
        if raw_text:
            trait_evidence[trait] = raw_text
        elif fallback_text:
            trait_evidence[trait] = fallback_text

    observed_traits = [
        trait for trait, evidence in trait_evidence.items()
        if evidence
        and "暂无充分证据" not in evidence
        and not evidence.startswith("基于回答深度")
    ]
    missing_traits = [
        item["name"] for item in BIG_FIVE_DIMENSIONS
        if item["name"] not in observed_traits
    ]
    scenario_summary = raw_observation.get("scenario_personality")
    if not scenario_summary:
        if observed_traits:
            top_traits = "、".join(observed_traits[:3])
            scenario_summary = f"当前回答主要呈现出{top_traits}相关的场景人格线索，仍需结合后续问题补充验证。"
        else:
            scenario_summary = "当前回答的心理特质证据仍不充分，后续需要通过岗位情境问题继续观察。"

    return {
        "basic_trait_scores": basic_scores,
        "scenario_trait_scores": scenario_scores,
        "trait_evidence": trait_evidence,
        "observed_traits": observed_traits,
        "confidence": clamp_score(raw_observation.get("confidence", confidence)),
        "missing_trait_dimensions": missing_traits,
        "basic_personality": raw_observation.get("basic_personality", {}),
        "scenario_personality": scenario_summary,
        "evidence": raw_observation.get("evidence", candidate_response[:120]),
        "rubric_version": "big_five_rubric_v1_2026_05",
    }
