"""心理解读详情服务。

该服务只基于既有 AssessmentRecord / EvaluationResult 组织展示数据，
不参与人格计算、匹配计算或评估主流程。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.assessment import (
    AssessmentMatchAnalysis,
    AssessmentRecord,
    AssessmentStatus,
    CandidatePersonalityProfile,
    EvaluationResult,
)
from models.job import Job


TRAIT_META = [
    {
        "key": "openness",
        "name": "开放性",
        "english": "Openness",
        "tags": ["好奇心强", "创新思维", "学习驱动"],
        "default_summary": "该维度反映个体对新经验、新观点与复杂问题的接纳程度。",
        "default_advice": "建议在学习、探索和表达类任务中主动积累证据，将开放性转化为稳定产出。",
    },
    {
        "key": "conscientiousness",
        "name": "尽责性",
        "english": "Conscientiousness",
        "tags": ["责任心强", "计划性", "自律稳定"],
        "default_summary": "该维度反映个体的计划性、责任意识与持续执行能力。",
        "default_advice": "建议继续保持任务拆解、进度管理和复盘习惯，提升岗位场景中的交付稳定性。",
    },
    {
        "key": "extraversion",
        "name": "外向性",
        "english": "Extraversion",
        "tags": ["社交活跃", "表达力强", "积极乐观"],
        "default_summary": "该维度反映个体在人际互动、主动表达和外部协作中的能量水平。",
        "default_advice": "建议结合目标岗位要求，选择合适场景展示沟通、推动和协作能力。",
    },
    {
        "key": "agreeableness",
        "name": "宜人性",
        "english": "Agreeableness",
        "tags": ["友善包容", "乐于助人", "团队合作"],
        "default_summary": "该维度反映个体在合作、同理心和关系维护方面的稳定倾向。",
        "default_advice": "建议在团队协作中保留支持性优势，同时通过清晰表达边界提升协作效率。",
    },
    {
        "key": "neuroticism",
        "name": "神经质 / 情绪稳定性",
        "english": "Neuroticism / Emotional Stability",
        "tags": ["情绪稳定", "抗压能力", "心理韧性"],
        "default_summary": "该维度反映个体面对压力、反馈和不确定情境时的情绪波动与恢复能力。",
        "default_advice": "建议关注压力情境下的恢复节奏，通过复盘和预案管理增强长期稳定表现。",
    },
]

TRAIT_NAME_ALIASES = {
    "开放性": "openness",
    "openness": "openness",
    "尽责性": "conscientiousness",
    "conscientiousness": "conscientiousness",
    "外向性": "extraversion",
    "extraversion": "extraversion",
    "宜人性": "agreeableness",
    "友好性": "agreeableness",
    "agreeableness": "agreeableness",
    "神经质": "neuroticism",
    "neuroticism": "neuroticism",
    "情绪稳定性": "neuroticism",
    "emotional_stability": "neuroticism",
}


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _extract_report_sections(evaluation_result: Optional[EvaluationResult]) -> Dict[str, Any]:
    if not evaluation_result:
        return {}
    content = _as_dict(evaluation_result.report_content)
    if isinstance(content.get("report_sections"), dict):
        return content["report_sections"]
    analysis = _as_dict(content.get("analysis"))
    if isinstance(analysis.get("report_sections"), dict):
        return analysis["report_sections"]
    return {}


def _profile_score(profile: Optional[CandidatePersonalityProfile], trait_key: str) -> Optional[float]:
    if not profile:
        return None
    mapping = {
        "extraversion": profile.trait_extroversion,
        "agreeableness": profile.trait_agreeableness,
        "conscientiousness": profile.trait_conscientiousness,
        "neuroticism": profile.trait_neuroticism,
        "openness": profile.trait_openness,
    }
    return mapping.get(trait_key)


def _normalize_trait_comparison(raw: Any) -> Dict[str, Dict[str, Any]]:
    normalized: Dict[str, Dict[str, Any]] = {}
    for raw_name, raw_value in _as_dict(raw).items():
        trait_key = TRAIT_NAME_ALIASES.get(str(raw_name).strip())
        if trait_key and isinstance(raw_value, dict):
            normalized[trait_key] = raw_value
    return normalized


def _find_trait_insight(report_sections: Dict[str, Any], trait_name: str) -> Dict[str, Any]:
    for item in report_sections.get("trait_insights") or []:
        if isinstance(item, dict) and item.get("name") == trait_name:
            return item
    return {}


def _match_status_from_comparison(comparison: Dict[str, Any], fallback: str = "balanced") -> str:
    if comparison.get("match_status"):
        return str(comparison["match_status"])
    degree = comparison.get("match_degree")
    try:
        degree_value = float(degree)
    except (TypeError, ValueError):
        return fallback
    if degree_value >= 4:
        return "aligned"
    if degree_value <= 2:
        return "gap"
    return "balanced"


def _score_from_comparison(comparison: Dict[str, Any], profile_score: Optional[float]) -> Optional[float]:
    for key in ("basic_trait", "score", "trait_score"):
        value = comparison.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    return profile_score


def _score_to_percent(score: Optional[float]) -> float:
    if score is None:
        return 0.0
    return round(max(0.0, min(100.0, float(score) * 10)), 1)


def _highlighted_traits(cards: List[Dict[str, Any]]) -> List[str]:
    scored_cards = [card for card in cards if card.get("score") is not None]
    scored_cards.sort(key=lambda item: _score_to_percent(item.get("score")), reverse=True)
    return [item["trait_name"] for item in scored_cards[:3]]


def _action_guides(report_sections: Dict[str, Any], recommendations: Optional[str]) -> List[Dict[str, str]]:
    actions = []
    for item in report_sections.get("development_actions") or []:
        if isinstance(item, dict):
            title = item.get("title") or item.get("phase") or "行动建议"
            description = item.get("description") or item.get("action")
            if description:
                actions.append({"title": title, "description": description})
    if actions:
        return actions[:5]

    if recommendations:
        return [{"title": "后续发展建议", "description": recommendations}]

    return [
        {"title": "自我认知", "description": "结合高分和低分维度，理解自然偏好与压力反应。"},
        {"title": "岗位匹配", "description": "将人格倾向与岗位要求对照，优先选择优势能够被放大的场景。"},
        {"title": "动态更新", "description": "在后续评估中持续观察人格表现趋势，而非只关注单次分数。"},
    ]


def build_psychology_detail(
    db: Session,
    assessment_record_id: Optional[int] = None,
    candidate_id: Optional[int] = None,
) -> Dict[str, Any]:
    if assessment_record_id is not None:
        record = db.query(AssessmentRecord).filter(
            AssessmentRecord.id == assessment_record_id,
            AssessmentRecord.is_deleted == False,
        ).first()
    elif candidate_id is not None:
        record = db.query(AssessmentRecord).filter(
            AssessmentRecord.candidate_id == candidate_id,
            AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED,
            AssessmentRecord.is_deleted == False,
        ).order_by(desc(AssessmentRecord.created_at)).first()
    else:
        record = None

    if not record:
        raise HTTPException(status_code=404, detail="未找到可用于心理解读的评估会话")

    evaluation_result = db.query(EvaluationResult).filter_by(
        assessment_record_id=record.id
    ).first()
    profile = db.query(CandidatePersonalityProfile).filter_by(
        candidate_id=record.candidate_id
    ).first()
    job = db.query(Job).filter_by(id=record.job_id).first()
    match_analysis = db.query(AssessmentMatchAnalysis).filter_by(
        assessment_record_id=record.id
    ).first()

    report_sections = _extract_report_sections(evaluation_result)
    trait_comparison = _normalize_trait_comparison(
        evaluation_result.trait_comparison if evaluation_result else None
    )

    cards: List[Dict[str, Any]] = []
    for meta in TRAIT_META:
        comparison = trait_comparison.get(meta["key"], {})
        insight = _find_trait_insight(report_sections, meta["name"])
        score = _score_from_comparison(comparison, _profile_score(profile, meta["key"]))
        job_requirement = comparison.get("job_requirement") or insight.get("job_requirement")
        try:
            job_requirement = float(job_requirement) if job_requirement is not None else None
        except (TypeError, ValueError):
            job_requirement = None

        summary = insight.get("summary") or comparison.get("summary") or meta["default_summary"]
        advice = insight.get("advice") or comparison.get("advice") or meta["default_advice"]
        bubble = (
            f"你当前关注的是“{meta['name']}”。{summary}"
            f" 结合本次 EvaluationResult，建议：{advice}"
        )

        cards.append({
            "trait_key": meta["key"],
            "trait_name": meta["name"],
            "english": meta["english"],
            "score": score,
            "job_requirement": job_requirement,
            "match_status": _match_status_from_comparison(comparison, insight.get("match_status", "balanced")),
            "summary": summary,
            "tags": meta["tags"],
            "advice": advice,
            "bubble_message": bubble,
        })

    highlighted = _highlighted_traits(cards)
    actions = _action_guides(report_sections, evaluation_result.recommendations if evaluation_result else None)
    overview_summary = (
        report_sections.get("personality_summary")
        or report_sections.get("overview_summary")
        or record.conversation_summary
        or "系统已基于本次评估会话形成大五人格解释，可结合岗位匹配结果理解个人优势与发展方向。"
    )
    growth_advice = actions[0]["description"] if actions else "建议结合评估结果持续完善岗位案例与能力证据。"
    overview_score = (
        evaluation_result.match_score
        if evaluation_result
        else (record.match_score if record.match_score is not None else 0.0)
    )

    source_fields = ["AssessmentRecord"]
    if evaluation_result:
        source_fields.append("EvaluationResult")
    if profile:
        source_fields.append("CandidatePersonalityProfile")
    if match_analysis:
        source_fields.append("AssessmentMatchAnalysis")

    return {
        "assessment_id": record.id,
        "evaluation_result_id": evaluation_result.result_id if evaluation_result else None,
        "candidate_id": record.candidate_id,
        "job_id": record.job_id,
        "job_title": job.name if job else record.job_title,
        "overview": {
            "summary": overview_summary,
            "score": round(float(overview_score or 0.0), 1),
            "highlighted_traits": highlighted,
            "growth_advice": growth_advice,
            "updated_at": evaluation_result.updated_at if evaluation_result else record.updated_at,
        },
        "trait_cards": cards,
        "action_guides": actions,
        "source_trace": {
            "assessment_record_id": record.id,
            "evaluation_result_id": evaluation_result.result_id if evaluation_result else None,
            "candidate_id": record.candidate_id,
            "job_id": record.job_id,
            "source_fields": source_fields,
        },
    }
