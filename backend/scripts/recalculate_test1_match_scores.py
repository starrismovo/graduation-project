"""Recalculate historical AssessmentRecord.match_score for the test1 user only.

Default mode is a dry run. Use --apply to write changes to MySQL.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)
warnings.filterwarnings("ignore", category=UserWarning, module=r"pydantic\._internal\..*")

from database import SessionLocal, engine
from models.assessment import AssessmentRecord, AssessmentStatus, CandidatePersonalityProfile, EvaluationResult
from models.job import Job
from models.user import User
from routers.assessment import calculate_job_match_score


TARGET_USERNAME = "test1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recalculate historical match scores for username test1 only."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write recalculated scores to assessment_records and related evaluation_results.",
    )
    parser.add_argument(
        "--all-statuses",
        action="store_true",
        help="Include non-completed AssessmentSession records. Default updates completed records only.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    engine.echo = False
    db = SessionLocal()

    try:
        candidate = db.query(User).filter(User.username == TARGET_USERNAME).first()
        if not candidate:
            print(f"ERROR: user '{TARGET_USERNAME}' not found.")
            return 1

        profile = db.query(CandidatePersonalityProfile).filter(
            CandidatePersonalityProfile.candidate_id == candidate.id
        ).first()
        if not profile:
            print(f"ERROR: CandidatePersonalityProfile not found for '{TARGET_USERNAME}' (id={candidate.id}).")
            return 1

        query = db.query(AssessmentRecord).filter(
            AssessmentRecord.candidate_id == candidate.id,
            AssessmentRecord.is_deleted == False,
        )
        if not args.all_statuses:
            query = query.filter(AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED)

        records = query.order_by(AssessmentRecord.created_at.asc()).all()
        if not records:
            print(f"No AssessmentRecord rows found for '{TARGET_USERNAME}'.")
            return 0

        print(f"Target user: {TARGET_USERNAME} (id={candidate.id})")
        print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
        print("record_id\tjob_id\tjob_title\told_score\tnew_score\tpersonality_match\tstatus")

        changed = 0
        skipped = 0
        now = datetime.now()

        for record in records:
            job = db.query(Job).filter(Job.id == record.job_id).first()
            if not job:
                skipped += 1
                print(
                    f"{record.id}\t{record.job_id}\t{record.job_title}\t"
                    f"{record.match_score}\tSKIP\tSKIP\tmissing job"
                )
                continue

            scores = calculate_job_match_score(profile, job)
            new_score = scores["overall"]
            old_score = round(float(record.match_score), 1) if record.match_score is not None else None
            will_change = old_score != new_score
            if will_change:
                changed += 1

            print(
                f"{record.id}\t{record.job_id}\t{record.job_title}\t"
                f"{old_score}\t{new_score}\t{scores['personality_match']}\t"
                f"{'change' if will_change else 'same'}"
            )

            if args.apply and will_change:
                record.match_score = new_score
                record.updated_at = now

                evaluation_result = db.query(EvaluationResult).filter(
                    EvaluationResult.assessment_record_id == record.id,
                    EvaluationResult.candidate_id == candidate.id,
                ).first()
                if evaluation_result:
                    evaluation_result.match_score = new_score
                    evaluation_result.updated_at = now

        if args.apply:
            db.commit()
            print(f"Applied. changed={changed}, skipped={skipped}, total={len(records)}")
        else:
            db.rollback()
            print(f"Dry run only. changed={changed}, skipped={skipped}, total={len(records)}")
            print("Run with --apply to write these values.")

        return 0
    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
