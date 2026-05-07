"""Reset test1 assessment data and simulate one complete assessment flow.

This script is intentionally scoped to username ``test1``. It deletes that
user's historical AssessmentSession-derived data, saves a new simulated result,
then verifies portrait, history, report, and recommended Job Instance outputs.
"""

from __future__ import annotations

import asyncio
import json
import sys
import warnings
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)
warnings.filterwarnings("ignore", category=UserWarning, module=r"pydantic\._internal\..*")

from database import SessionLocal, engine
from models.assessment import (
    AssessmentMatchAnalysis,
    AssessmentRecord,
    CandidatePersonalityProfile,
    EvaluationResult,
    PersonalityTraitDescription,
)
from models.conversation import ConversationAnalysis, ConversationTurn
from models.hr_agent import InterviewResponse, ScenarioSummary, TraitScore
from models.interview import Interview
from models.job import Job
from models.user import User
from routers.assessment import (
    get_history,
    get_portrait,
    get_recommended_jobs,
    get_report,
    save_assessment_result,
)
from schemas.assessment import SaveAssessmentResultRequest


TARGET_USERNAME = "test1"
TARGET_JOB_KEYWORDS = ["用户研究师", "内容运营", "产品经理", "文案策划"]
RESUME_PATH = Path(r"D:\下载\简历产品 _畅新悦.pdf")


def find_target_job(db) -> Job:
    for keyword in TARGET_JOB_KEYWORDS:
        job = db.query(Job).filter(Job.name.like(f"%{keyword}%")).first()
        if job:
            return job
    job = db.query(Job).order_by(Job.id.asc()).first()
    if not job:
        raise RuntimeError("No Job Instance rows found.")
    return job


def clear_test1_history(db, candidate: User) -> dict:
    record_ids = [
        row[0]
        for row in db.query(AssessmentRecord.id)
        .filter(AssessmentRecord.candidate_id == candidate.id)
        .all()
    ]

    counts = {
        "assessment_records": len(record_ids),
        "evaluation_results": 0,
        "match_analyses": 0,
        "trait_descriptions": 0,
        "conversation_turns": 0,
        "conversation_analyses": 0,
        "interview_responses": 0,
        "trait_scores": 0,
        "scenario_summaries": 0,
        "candidate_profile": 0,
        "interviews": 0,
    }

    if record_ids:
        counts["conversation_turns"] = db.query(ConversationTurn).filter(
            ConversationTurn.assessment_id.in_(record_ids)
        ).delete(synchronize_session=False)
        counts["conversation_analyses"] = db.query(ConversationAnalysis).filter(
            ConversationAnalysis.assessment_id.in_(record_ids)
        ).delete(synchronize_session=False)
        counts["evaluation_results"] = db.query(EvaluationResult).filter(
            EvaluationResult.assessment_record_id.in_(record_ids)
        ).delete(synchronize_session=False)
        counts["match_analyses"] = db.query(AssessmentMatchAnalysis).filter(
            AssessmentMatchAnalysis.assessment_record_id.in_(record_ids)
        ).delete(synchronize_session=False)
        counts["trait_descriptions"] = db.query(PersonalityTraitDescription).filter(
            PersonalityTraitDescription.assessment_record_id.in_(record_ids)
        ).delete(synchronize_session=False)

    response_ids = [
        row[0]
        for row in db.query(InterviewResponse.id)
        .filter(InterviewResponse.candidate_id == candidate.id)
        .all()
    ]
    if response_ids:
        counts["trait_scores"] = db.query(TraitScore).filter(
            TraitScore.response_id.in_(response_ids)
        ).delete(synchronize_session=False)

    counts["interview_responses"] = db.query(InterviewResponse).filter(
        InterviewResponse.candidate_id == candidate.id
    ).delete(synchronize_session=False)
    counts["scenario_summaries"] = db.query(ScenarioSummary).filter(
        ScenarioSummary.candidate_id == candidate.id
    ).delete(synchronize_session=False)

    if record_ids:
        db.query(AssessmentRecord).filter(
            AssessmentRecord.id.in_(record_ids)
        ).delete(synchronize_session=False)

    counts["candidate_profile"] = db.query(CandidatePersonalityProfile).filter(
        CandidatePersonalityProfile.candidate_id == candidate.id
    ).delete(synchronize_session=False)
    counts["interviews"] = db.query(Interview).filter(
        Interview.candidate_id == candidate.id
    ).delete(synchronize_session=False)

    db.commit()
    return counts


def build_request(candidate: User, job: Job) -> SaveAssessmentResultRequest:
    return SaveAssessmentResultRequest(
        candidate_id=candidate.username,
        job_id=job.id,
        assessment_mode="immersive",
        all_scores={
            "表达能力": 8.6,
            "团队合作": 7.8,
            "专业能力": 8.7,
            "逻辑思维": 8.5,
            "创新思维": 9.3,
            "学习能力": 9.0,
        },
        personality_scores={
            "外向性": 4.6,
            "宜人性": 8.7,
            "尽责性": 8.1,
            "神经质": 4.2,
            "开放性": 9.4,
        },
        candidate_info={
            "resume_file": str(RESUME_PATH),
            "resume_file_exists": RESUME_PATH.exists(),
            "portfolio_focus": "深度文字作品、长文分析、复杂叙事、人性解析",
            "interview_positioning": "问题定义者；能共情、能看见隐藏需求、能梳理复杂逻辑",
            "designed_answers": {
                "weakness": "曾经过度共情，现在通过边界感保持稳定输出。",
                "career_plan": "成长为能定义问题的专业型人才。",
                "why_company": "关注产品背后的深层情感需求，并以文字与洞察能力服务于此。",
            },
            "skills": ["用户研究", "内容分析", "长文写作", "需求洞察", "产品思维"],
        },
    )


async def run_flow() -> int:
    engine.echo = False
    db = SessionLocal()
    try:
        candidate = db.query(User).filter(User.username == TARGET_USERNAME).first()
        if not candidate:
            print(f"ERROR: user {TARGET_USERNAME!r} not found.")
            return 1

        before_counts = clear_test1_history(db, candidate)
        after_history = await get_history(candidate.username, 20, 0, db)

        job = find_target_job(db)
        request = build_request(candidate, job)
        save_result = await save_assessment_result(request, db)
        record_id = save_result.data["record_id"]

        portrait = await get_portrait(candidate.username, db)
        history = await get_history(candidate.username, 20, 0, db)
        report = await get_report(record_id, db)
        recommendations = await get_recommended_jobs(candidate.username, 5, db)

        print("CLEAR_COUNTS")
        print(json.dumps(before_counts, ensure_ascii=False, indent=2))
        print(f"HISTORY_AFTER_CLEAR={len(after_history.data)}")
        print("SIMULATED_JOB")
        print(json.dumps({
            "id": job.id,
            "name": job.name,
            "company": job.company,
            "category": job.category,
            "city": job.city,
            "required_traits": job.required_traits,
        }, ensure_ascii=False, indent=2))
        print("SAVE_RESULT")
        print(json.dumps(save_result.data, ensure_ascii=False, indent=2))
        print("PORTRAIT")
        print(json.dumps([item.model_dump() for item in portrait.data], ensure_ascii=False, indent=2))
        print("HISTORY")
        print(json.dumps([item.model_dump(mode="json") for item in history.data], ensure_ascii=False, indent=2))
        print("REPORT_SUMMARY")
        print(json.dumps({
            "record_id": report.data.id,
            "job_title": report.data.job_title,
            "match_score": report.data.match_score,
            "trait_count": len(report.data.personality_trait),
            "strengths": report.data.match_analysis.strengths if report.data.match_analysis else [],
            "gaps": report.data.match_analysis.gaps if report.data.match_analysis else [],
            "recommendations": report.data.recommendations,
        }, ensure_ascii=False, indent=2))
        print("RECOMMENDED_TOP5")
        print(json.dumps([
            {
                "id": item.id,
                "title": item.title,
                "company": item.company,
                "city": item.city,
                "category": item.category,
                "salary": item.salary,
                "match_score": item.match_score,
                "match_reason": item.match_reason,
            }
            for item in recommendations.data
        ], ensure_ascii=False, indent=2))

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_flow()))
