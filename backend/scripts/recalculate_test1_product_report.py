"""Recalculate the stored test1 B-end SaaS product manager report.

Default mode is a dry run. Use --apply to update the stored AssessmentSession,
EvaluationResult and AssessmentMatchAnalysis rows.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import desc
from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)
warnings.filterwarnings("ignore", category=UserWarning, module=r"pydantic\._internal\..*")

from database import SessionLocal, engine
from models.assessment import (
    AssessmentMatchAnalysis,
    AssessmentRecord,
    AssessmentStatus,
    CandidatePersonalityProfile,
    EvaluationResult,
)
from models.job import Job
from models.job_requirement import JobPersonalityFramework, JobSkillRequirement
from models.user import User
from routers.assessment import _apply_hard_skill_gate, _get_match_weights, _weighted_match_score
from services.job_requirement_service import matching_engine, skill_name_matches
from services.report_agent import report_agent


TARGET_USERNAME = "test1"
TARGET_JOB_TITLE = "产品经理（B端 SaaS）"

ASSESSMENT_SKILL_EVIDENCE_ALIASES = {
    "产品思维": ["产品思维", "创新能力", "用户洞察", "问题解决"],
    "用户研究": ["用户研究", "用户洞察", "沟通能力"],
    "需求分析": ["需求分析", "问题解决", "逻辑思维", "沟通能力"],
}


def _coerce_score(value: Any) -> Optional[float]:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return score * 10 if 0 < score <= 10 else score


def _assessment_skill_score(scores: Dict[str, Any]) -> Optional[float]:
    skill_dimensions = [
        "产品思维",
        "用户研究",
        "需求分析",
        "专业能力",
        "技术深度",
        "问题解决",
        "逻辑思维",
        "学习能力",
        "创新能力",
        "用户洞察",
        "战略思维",
        "沟通能力",
        "团队协作",
        "团队合作",
        "文化契合",
    ]
    values = [_coerce_score(scores.get(key)) for key in skill_dimensions if key in scores]
    values = [value for value in values if value is not None and value > 0]
    if not values:
        return None
    return round(max(0.0, min(100.0, sum(values) / len(values))), 1)


def _skills_verified_by_assessment(
    required_skills: List[JobSkillRequirement],
    ability_scores: Dict[str, Any],
    evidence: Dict[str, Any],
) -> List[str]:
    verified_from_evidence = [
        str(item).strip()
        for item in (evidence.get("verified_skills") or [])
        if str(item).strip()
    ]
    verified: List[str] = []
    for skill_req in required_skills:
        skill_name = skill_req.skill_name
        related_scores = [
            _coerce_score(ability_scores.get(dimension))
            for dimension in ASSESSMENT_SKILL_EVIDENCE_ALIASES.get(skill_name, [skill_name])
            if dimension in ability_scores
        ]
        related_scores = [score for score in related_scores if score is not None and score > 0]
        if related_scores and (sum(related_scores) / len(related_scores)) >= 60:
            verified.append(skill_name)
            continue
        if any(skill_name_matches(item, skill_name) for item in verified_from_evidence):
            verified.append(skill_name)
    return list(dict.fromkeys(verified))


def _extract_evidence(report_content: Dict[str, Any]) -> Dict[str, Any]:
    evidence = report_content.get("assessment_evidence")
    if isinstance(evidence, dict):
        return evidence
    sections = report_content.get("report_sections")
    if isinstance(sections, dict):
        summary = sections.get("evidence_summary")
        if isinstance(summary, dict):
            return summary
    return {}


def _candidate_skills(candidate: User, evidence: Dict[str, Any]) -> List[str]:
    skills: List[str] = []
    if isinstance(candidate.skills, list):
        skills.extend(str(item).strip() for item in candidate.skills if str(item).strip())
    elif isinstance(candidate.skills, str):
        skills.extend(item.strip() for item in candidate.skills.split(",") if item.strip())
    skills.extend(str(item).strip() for item in (evidence.get("verified_skills") or []) if str(item).strip())
    return list(dict.fromkeys(skills))


def _personality_scores(profile: CandidatePersonalityProfile) -> Dict[str, float]:
    return {
        key: value * 10
        for key, value in {
            "openness": profile.trait_openness,
            "conscientiousness": profile.trait_conscientiousness,
            "extraversion": profile.trait_extroversion,
            "agreeableness": profile.trait_agreeableness,
            "neuroticism": profile.trait_neuroticism,
        }.items()
        if value is not None
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recalculate the stored test1 product manager report.")
    parser.add_argument("--apply", action="store_true", help="Write recalculated values to the database.")
    parser.add_argument("--record-id", type=int, default=None, help="Specific AssessmentRecord id to recalculate.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    engine.echo = False
    db = SessionLocal()
    try:
        candidate = db.query(User).filter(User.username == TARGET_USERNAME).first()
        if not candidate:
            print(f"ERROR: user {TARGET_USERNAME!r} not found")
            return 1

        query = db.query(AssessmentRecord).filter(
            AssessmentRecord.candidate_id == candidate.id,
            AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED,
            AssessmentRecord.is_deleted == False,
        )
        if args.record_id:
            query = query.filter(AssessmentRecord.id == args.record_id)
        else:
            query = query.filter(AssessmentRecord.job_title == TARGET_JOB_TITLE)
        record = query.order_by(desc(AssessmentRecord.created_at)).first()
        if not record:
            print("ERROR: target AssessmentRecord not found")
            return 1

        job = db.query(Job).filter(Job.id == record.job_id).first()
        profile = db.query(CandidatePersonalityProfile).filter(
            CandidatePersonalityProfile.candidate_id == candidate.id
        ).first()
        evaluation_result = db.query(EvaluationResult).filter(
            EvaluationResult.assessment_record_id == record.id,
            EvaluationResult.candidate_id == candidate.id,
        ).first()
        if not job or not profile or not evaluation_result:
            print("ERROR: missing job, personality profile, or evaluation result")
            return 1

        report_content = evaluation_result.report_content if isinstance(evaluation_result.report_content, dict) else {}
        ability_scores = evaluation_result.ability_scores or report_content.get("ability_scores") or {}
        evidence = _extract_evidence(report_content)
        required_skills = db.query(JobSkillRequirement).filter(JobSkillRequirement.job_id == job.id).all()
        personality_fw = db.query(JobPersonalityFramework).filter(JobPersonalityFramework.job_id == job.id).first()

        resume_skill_match, matched_skills, missing_skills = matching_engine.calculate_skill_match(
            _candidate_skills(candidate, evidence),
            required_skills,
        )
        assessment_skill_match = _assessment_skill_score(ability_scores)
        candidate_skill_values = _candidate_skills(candidate, evidence)
        if assessment_skill_match is not None:
            skill_match = (
                round(resume_skill_match * 0.5 + assessment_skill_match * 0.5, 1)
                if candidate_skill_values
                else assessment_skill_match
            )
        else:
            skill_match = resume_skill_match

        assessment_verified = _skills_verified_by_assessment(required_skills, ability_scores, evidence)
        if assessment_verified:
            matched_skills = list(dict.fromkeys([*matched_skills, *assessment_verified]))
            missing_skills = [
                skill
                for skill in missing_skills
                if not any(skill_name_matches(verified, skill) for verified in assessment_verified)
            ]

        personality = _personality_scores(profile)
        personality_match = (
            matching_engine.calculate_personality_match(personality, personality_fw)
            if personality_fw and personality
            else 50.0
        )
        match_weights = _get_match_weights(job)
        base_overall = _weighted_match_score(skill_match, personality_match, match_weights)
        hard_skill_gate = _apply_hard_skill_gate(
            score=base_overall,
            skill_match=skill_match,
            missing_skills=missing_skills,
            required_skills=required_skills,
            job=job,
        )
        overall_score = hard_skill_gate["score"]

        analysis_payload = report_agent.build_match_analysis(
            profile=profile,
            job=job,
            scoring_meta={
                "model_version": report_content.get("model_version") or "big_five_backend_v2",
                "source": report_content.get("scoring_source") or "recalculated",
                "input_dimensions": list(ability_scores.keys()),
            },
            match_breakdown={
                "skill_match": skill_match,
                "personality_match": personality_match,
                "overall_score": overall_score,
                "weights": match_weights,
                "hard_skill_gate": hard_skill_gate,
            },
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            evidence=evidence,
        )

        print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
        print(f"Record: id={record.id}, job={record.job_title}, created_at={record.created_at}")
        print(f"Old score: record={record.match_score}, evaluation={evaluation_result.match_score}")
        print(f"New score: overall={overall_score}, skill={skill_match}, personality={personality_match}")
        print(f"Matched skills: {matched_skills}")
        print(f"Missing skills: {missing_skills}")
        print(f"Hard gate: {hard_skill_gate}")

        if not args.apply:
            db.rollback()
            print("Dry run only. Re-run with --apply to write changes.")
            return 0

        now = datetime.now()
        record.match_score = overall_score
        record.feedback_result = hard_skill_gate.get("recommendation") if hard_skill_gate.get("applied") else "recommended"
        record.updated_at = now

        evaluation_result.match_score = overall_score
        evaluation_result.strengths = "\n".join(analysis_payload.get("strengths") or [])
        evaluation_result.gaps = "\n".join(analysis_payload.get("gaps") or [])
        evaluation_result.recommendations = "\n".join(analysis_payload.get("recommendations") or [])
        evaluation_result.updated_at = now

        updated_content = dict(report_content)
        updated_content.update(
            {
                "ability_scores": ability_scores,
                "skill_match": skill_match,
                "personality_match": personality_match,
                "overall_score": overall_score,
                "match_weights": match_weights,
                "hard_skill_gate": hard_skill_gate,
                "assessment_evidence": {
                    "verified_skills": analysis_payload.get("detailed_analysis", {}).get("skill_evidence", {}).get("matched_skills", []),
                    "missing_must_have_skills": analysis_payload.get("detailed_analysis", {}).get("skill_evidence", {}).get("missing_skills", []),
                    "personality_evidence": analysis_payload.get("detailed_analysis", {}).get("personality_evidence", {}),
                    "evidence_quote": analysis_payload.get("detailed_analysis", {}).get("evidence_quote", []),
                },
                "analysis": analysis_payload,
                "report_sections": analysis_payload.get("report_sections"),
                "generated_at": now.isoformat(),
                "recalculated_at": now.isoformat(),
            }
        )
        evaluation_result.report_content = updated_content

        match_analysis = db.query(AssessmentMatchAnalysis).filter(
            AssessmentMatchAnalysis.assessment_record_id == record.id
        ).first()
        if match_analysis:
            match_analysis.strengths = analysis_payload["strengths"]
            match_analysis.gaps = analysis_payload["gaps"]
            match_analysis.recommendations = analysis_payload["recommendations"]
            match_analysis.detailed_analysis = json.dumps(analysis_payload["detailed_analysis"], ensure_ascii=False)
            match_analysis.updated_at = now

        db.commit()
        print("Applied successfully.")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
