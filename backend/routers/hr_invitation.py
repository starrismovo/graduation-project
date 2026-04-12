"""
HR 邀请 API 路由
HR 邀请候选人参加指定岗位的评估面试
候选人可以查看、接受、拒绝邀请
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models.hr_invitation import HRInvitation, InvitationStatus
from models.user import User, UserType
from models.job import Job
from schemas.hr_invitation import InvitationCreate, InvitationResponse, InvitationListResponse
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/invitations", tags=["invitations"])


def _format_salary(job: Job) -> Optional[str]:
    if job.salary_min is None or job.salary_max is None:
        return None
    return f"{job.salary_min}k-{job.salary_max}k"


def _build_response(inv: HRInvitation) -> InvitationResponse:
    return InvitationResponse(
        id=inv.id,
        hr_id=inv.hr_id,
        hr_name=inv.hr.nickname or inv.hr.real_name or inv.hr.username if inv.hr else None,
        candidate_id=inv.candidate_id,
        candidate_name=inv.candidate.nickname or inv.candidate.real_name or inv.candidate.username if inv.candidate else None,
        job_id=inv.job_id,
        job_name=inv.job.name if inv.job else "未知岗位",
        company=inv.job.company if inv.job else "未知公司",
        salary=_format_salary(inv.job) if inv.job else None,
        city=inv.job.city if inv.job else None,
        message=inv.message,
        status=inv.status.value if isinstance(inv.status, InvitationStatus) else inv.status,
        created_at=inv.created_at,
        responded_at=inv.responded_at,
    )


# ==================== HR 端 ====================

@router.post("/hr/{hr_id}/send", response_model=InvitationResponse)
async def send_invitation(
    hr_id: int,
    body: InvitationCreate,
    db: Session = Depends(get_db),
):
    """HR 向候选人发送邀请"""
    hr = db.query(User).filter(User.id == hr_id).first()
    if not hr or hr.user_type != UserType.HR:
        raise HTTPException(status_code=403, detail="仅 HR 可发送邀请")

    candidate = db.query(User).filter(User.id == body.candidate_id, User.user_type == UserType.CANDIDATE).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    job = db.query(Job).filter(Job.id == body.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    existing = db.query(HRInvitation).filter(
        HRInvitation.hr_id == hr_id,
        HRInvitation.candidate_id == body.candidate_id,
        HRInvitation.job_id == body.job_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="已发送过该邀请")

    inv = HRInvitation(
        hr_id=hr_id,
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        message=body.message,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return _build_response(inv)


@router.get("/hr/{hr_id}/list", response_model=InvitationListResponse)
async def list_hr_invitations(
    hr_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """HR 查看自己发出的邀请列表"""
    q = db.query(HRInvitation).filter(HRInvitation.hr_id == hr_id)
    if status:
        q = q.filter(HRInvitation.status == status)
    items = q.order_by(desc(HRInvitation.created_at)).all()
    return InvitationListResponse(total=len(items), items=[_build_response(i) for i in items])


# ==================== 候选人端 ====================

@router.get("/candidate/{candidate_id}/list", response_model=InvitationListResponse)
async def list_candidate_invitations(
    candidate_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """候选人查看收到的邀请列表"""
    q = db.query(HRInvitation).filter(HRInvitation.candidate_id == candidate_id)
    if status:
        q = q.filter(HRInvitation.status == status)
    items = q.order_by(desc(HRInvitation.created_at)).all()
    return InvitationListResponse(total=len(items), items=[_build_response(i) for i in items])


@router.get("/candidate/{candidate_id}/pending-count")
async def pending_invitation_count(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    """候选人待处理邀请数量"""
    count = db.query(HRInvitation).filter(
        HRInvitation.candidate_id == candidate_id,
        HRInvitation.status == InvitationStatus.PENDING,
    ).count()
    return {"count": count}


@router.put("/candidate/{candidate_id}/respond/{invitation_id}")
async def respond_invitation(
    candidate_id: int,
    invitation_id: int,
    action: str = Query(..., regex="^(accepted|declined)$"),
    db: Session = Depends(get_db),
):
    """候选人接受或拒绝邀请"""
    inv = db.query(HRInvitation).filter(
        HRInvitation.id == invitation_id,
        HRInvitation.candidate_id == candidate_id,
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="邀请不存在")
    if inv.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=400, detail="该邀请已处理")

    inv.status = InvitationStatus(action)
    inv.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(inv)
    return _build_response(inv)
