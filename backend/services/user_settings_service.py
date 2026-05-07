from datetime import datetime, timedelta

from sqlalchemy import func, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from models.assessment import (
    AssessmentRecord,
    AssessmentStatus,
    CandidatePersonalityProfile,
)
from models.hr_invitation import HRInvitation, InvitationStatus
from models.interview import Interview
from models.job import Job
from models.user import User


NOTIFICATION_COLUMNS = {
    "notify_interview_reminder": "ALTER TABLE users ADD COLUMN notify_interview_reminder BOOLEAN NOT NULL DEFAULT TRUE",
    "notify_assessment_completed": "ALTER TABLE users ADD COLUMN notify_assessment_completed BOOLEAN NOT NULL DEFAULT TRUE",
    "notify_report_ready": "ALTER TABLE users ADD COLUMN notify_report_ready BOOLEAN NOT NULL DEFAULT TRUE",
    "notify_job_recommendation": "ALTER TABLE users ADD COLUMN notify_job_recommendation BOOLEAN NOT NULL DEFAULT TRUE",
    "notify_candidate_delivery": "ALTER TABLE users ADD COLUMN notify_candidate_delivery BOOLEAN NOT NULL DEFAULT TRUE",
    "notify_candidate_assessment_completed": "ALTER TABLE users ADD COLUMN notify_candidate_assessment_completed BOOLEAN NOT NULL DEFAULT TRUE",
}


def ensure_notification_columns(engine: Engine) -> None:
    """为已存在的 users 表补齐通知设置字段。"""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    missing_columns = [
        column_name
        for column_name in NOTIFICATION_COLUMNS
        if column_name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for column_name in missing_columns:
            connection.execute(text(NOTIFICATION_COLUMNS[column_name]))


def build_notification_settings(user: User) -> dict:
    return {
        "notify_interview_reminder": bool(user.notify_interview_reminder),
        "notify_assessment_completed": bool(user.notify_assessment_completed),
        "notify_report_ready": bool(user.notify_report_ready),
        "notify_job_recommendation": bool(user.notify_job_recommendation),
        "notify_candidate_delivery": bool(user.notify_candidate_delivery),
        "notify_candidate_assessment_completed": bool(user.notify_candidate_assessment_completed),
    }


def build_notification_summary(user: User, db: Session) -> dict:
    items = []
    now = datetime.utcnow()

    if getattr(user, "is_hr_user", False) or user.is_hr:
        if user.notify_candidate_delivery:
            application_count = (
                db.query(func.count(Interview.id))
                .join(Job, Job.id == Interview.job_id)
                .filter(Job.creator_id == user.id, Interview.is_deleted == False)
                .scalar()
                or 0
            )
            if application_count > 0:
                items.append(
                    {
                        "id": "hr-applications",
                        "type": "candidate_delivery",
                        "title": "新的候选人投递",
                        "content": f"当前招聘岗位共收到 {application_count} 份投递，建议及时进入候选人列表查看与筛选。",
                        "action_path": "/home/candidates",
                        "action_label": "查看候选人",
                        "priority": "high",
                        "created_at": now.isoformat(),
                    }
                )

        if user.notify_candidate_assessment_completed or user.notify_report_ready:
            pending_reports = (
                db.query(func.count(Interview.id))
                .join(Job, Job.id == Interview.job_id)
                .filter(
                    Job.creator_id == user.id,
                    Interview.is_deleted == False,
                    Interview.status == "completed",
                )
                .scalar()
                or 0
            )
            if pending_reports > 0:
                items.append(
                    {
                        "id": "hr-pending-reports",
                        "type": "report_ready",
                        "title": "评估报告待查看",
                        "content": f"有 {pending_reports} 份候选人评估报告已生成，建议优先查看最新结果并推进招聘决策。",
                        "action_path": "/home/candidates",
                        "action_label": "进入查看",
                        "priority": "high",
                        "created_at": now.isoformat(),
                    }
                )

        if user.notify_interview_reminder:
            pending_invitations = (
                db.query(func.count(HRInvitation.id))
                .filter(
                    HRInvitation.hr_id == user.id,
                    HRInvitation.status == InvitationStatus.PENDING,
                )
                .scalar()
                or 0
            )
            if pending_invitations > 0:
                items.append(
                    {
                        "id": "hr-pending-invitations",
                        "type": "interview_reminder",
                        "title": "面试邀请待反馈",
                        "content": f"您已发出的 {pending_invitations} 条面试邀请仍在等待反馈，可继续跟进候选人响应情况。",
                        "action_path": "/home/candidates",
                        "action_label": "查看邀请",
                        "priority": "medium",
                        "created_at": now.isoformat(),
                    }
                )
    else:
        if user.notify_interview_reminder:
            pending_invitations = (
                db.query(func.count(HRInvitation.id))
                .filter(
                    HRInvitation.candidate_id == user.id,
                    HRInvitation.status == InvitationStatus.PENDING,
                )
                .scalar()
                or 0
            )
            if pending_invitations > 0:
                items.append(
                    {
                        "id": "candidate-pending-invitations",
                        "type": "interview_reminder",
                        "title": "收到新的面试邀请",
                        "content": f"您有 {pending_invitations} 条待处理的面试邀请，请及时确认后续安排。",
                        "action_path": "/home/interviews",
                        "action_label": "查看邀请",
                        "priority": "high",
                        "created_at": now.isoformat(),
                    }
                )

            active_interviews = (
                db.query(func.count(Interview.id))
                .filter(
                    Interview.candidate_id == user.id,
                    Interview.is_deleted == False,
                    Interview.status.in_(["started", "in_progress"]),
                )
                .scalar()
                or 0
            )
            if active_interviews > 0:
                items.append(
                    {
                        "id": "candidate-active-interviews",
                        "type": "interview_reminder",
                        "title": "面试流程进行中",
                        "content": f"当前有 {active_interviews} 个面试流程尚未完成，您可以继续作答并生成最新评估结果。",
                        "action_path": "/home/interviews",
                        "action_label": "继续面试",
                        "priority": "medium",
                        "created_at": now.isoformat(),
                    }
                )

        latest_assessment = (
            db.query(AssessmentRecord)
            .filter(
                AssessmentRecord.candidate_id == user.id,
                AssessmentRecord.is_deleted == False,
                AssessmentRecord.assessment_status == AssessmentStatus.COMPLETED,
            )
            .order_by(AssessmentRecord.updated_at.desc(), AssessmentRecord.created_at.desc())
            .first()
        )

        if latest_assessment and user.notify_report_ready:
            items.append(
                {
                    "id": f"candidate-report-{latest_assessment.id}",
                    "type": "report_ready",
                    "title": "评估报告已生成",
                    "content": f"岗位“{latest_assessment.job_title}”的评估报告已可查看，建议及时阅读匹配分析与建议。",
                    "action_path": f"/home/report/{latest_assessment.id}",
                    "action_label": "查看报告",
                    "priority": "high",
                    "created_at": latest_assessment.updated_at.isoformat()
                    if latest_assessment.updated_at
                    else now.isoformat(),
                }
            )

        if latest_assessment and user.notify_assessment_completed:
            recent_threshold = now - timedelta(days=7)
            if latest_assessment.updated_at and latest_assessment.updated_at >= recent_threshold:
                items.append(
                    {
                        "id": f"candidate-completed-{latest_assessment.id}",
                        "type": "assessment_completed",
                        "title": "最近一次评估已完成",
                        "content": "系统已完成您最近一次面试评估，建议结合人格画像与岗位建议继续完善投递策略。",
                        "action_path": "/home/reports",
                        "action_label": "查看报告列表",
                        "priority": "medium",
                        "created_at": latest_assessment.updated_at.isoformat(),
                    }
                )

        if user.notify_job_recommendation:
            has_profile = (
                db.query(CandidatePersonalityProfile)
                .filter(CandidatePersonalityProfile.candidate_id == user.id)
                .first()
            )
            recommendation_count = (
                db.query(func.count(Job.id)).filter(Job.required_traits.isnot(None)).scalar()
                or 0
            )
            if has_profile and recommendation_count > 0:
                items.append(
                    {
                        "id": "candidate-job-recommendation",
                        "type": "job_recommendation",
                        "title": "岗位推荐已更新",
                        "content": "系统已结合您的最新评估结果更新岗位推荐，可返回首页查看更适合的岗位方向。",
                        "action_path": "/home",
                        "action_label": "查看推荐岗位",
                        "priority": "low",
                        "created_at": has_profile.updated_at.isoformat()
                        if has_profile.updated_at
                        else now.isoformat(),
                    }
                )

    priority_weight = {"high": 0, "medium": 1, "low": 2}
    items.sort(
        key=lambda item: (
            priority_weight.get(item["priority"], 9),
            item["created_at"],
        ),
        reverse=False,
    )

    return {
        "unread_count": len(items),
        "items": items[:6],
        "generated_at": now.isoformat(),
    }
