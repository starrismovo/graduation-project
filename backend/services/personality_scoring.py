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
