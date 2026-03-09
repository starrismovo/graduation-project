"""
沉浸式对话 API 路由
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from services.immersive_dialogue import (
    ImmersiveDialogueService,
    RoleType,
    ROLE_CONFIG
)


router = APIRouter(prefix="/assessment/immersive", tags=["沉浸式对话"])


# ==================== 核心对话接口 ====================

@router.post("/next-question")
async def get_next_question(
    candidate_id: str = Query(..., description="候选人ID"),
    role_id: str = Query(..., description="提问角色ID"),
    role_name: Optional[str] = Query(None, description="角色名称"),
    conversation_depth: int = Query(0, description="对话深度"),
    history: str = Query("[]", description="对话历史 JSON"),
    target_position: Optional[str] = Query(None, description="目标岗位"),
    db: Session = Depends(get_db)
):
    """
    生成下一个问题
    
    Args:
        candidate_id: 候选人ID
        role_id: 角色ID (hr/tech_lead/product/cto)
        conversation_depth: 对话深度 (0-10)
    
    Returns:
        {
            "code": 200,
            "data": {
                "question": "问题文本",
                "tags": ["标签1", "标签2"],
                "suggestions": ["建议1", "建议2"],
                "context": "背景说明",
                "expected_traits": ["特质1", "特质2"]
            }
        }
    """
    
    try:
        import json
        conversation_history = json.loads(history) if history else []
        
        service = ImmersiveDialogueService(db)
        
        result = await service.generate_next_question(
            candidate_id=candidate_id,
            candidate_name="",  # 可从数据库获取
            current_role=RoleType(role_id),
            conversation_history=conversation_history,
            conversation_depth=conversation_depth,
            target_position=target_position
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "问题生成成功"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的角色: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成问题失败: {str(e)}")


@router.post("/analyze-response")
async def analyze_candidate_response(
    candidate_id: str = Query(..., description="候选人ID"),
    candidate_name: Optional[str] = Query(None),
    current_speaker: str = Query(..., description="提问者角色"),
    candidate_response: str = Query(..., description="候选人回答"),
    conversation_depth: int = Query(0),
    previous_messages: str = Query("[]", description="历史消息 JSON"),
    target_position: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    分析候选人的回答
    
    Returns:
        {
            "code": 200,
            "data": {
                "scores": {
                    "沟通能力": 7.5,
                    "问题解决": 8.0,
                    ...
                },
                "sentiment": {
                    "emotion": "自信",
                    "confidence": 85
                },
                "patterns": [...],
                "feedback": "实时反馈",
                "next_action": "continue|switch_role|end_phase"
            }
        }
    """
    
    try:
        import json
        messages = json.loads(previous_messages) if previous_messages else []
        
        service = ImmersiveDialogueService(db)
        
        result = await service.analyze_candidate_response(
            candidate_id=candidate_id,
            candidate_name=candidate_name or "候选人",
            current_speaker=RoleType(current_speaker),
            candidate_response=candidate_response,
            conversation_history=messages,
            conversation_depth=conversation_depth,
            target_position=target_position
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "分析成功"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的角色: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


# ==================== 会话管理接口 ====================

@router.post("/save-session")
async def save_assessment_session(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    保存评估会话
    
    Args:
        request_data: {
            "candidate_id": "123",
            "assessment_id": 456,
            "messages": [...],
            "scores": {...},
            "patterns": [...],
            "duration_seconds": 1200,
            "conversation_depth": 8,
            "total_rounds": 10,
            "highlights": [...]
        }
    """
    
    try:
        service = ImmersiveDialogueService(db)
        
        result = await service.save_assessment_session(
            candidate_id=request_data.get("candidate_id"),
            assessment_id=request_data.get("assessment_id"),
            messages=request_data.get("messages", []),
            scores=request_data.get("scores", {}),
            patterns=request_data.get("patterns", []),
            duration_seconds=request_data.get("duration_seconds", 0),
            conversation_depth=request_data.get("conversation_depth", 0),
            total_rounds=request_data.get("total_rounds", 0),
            highlights=request_data.get("highlights", [])
        )
        
        if result.get("success"):
            return {
                "code": 200,
                "data": {
                    "assessment_id": result.get("assessment_id"),
                    "session_id": result.get("session_id"),
                    "overall_score": result.get("overall_score")
                },
                "message": "会话已保存"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


# ==================== 信息接口 ====================

@router.get("/roles")
async def get_all_roles():
    """获取所有可用的角色列表"""
    
    roles = []
    
    for role_id, config in ROLE_CONFIG.items():
        roles.append({
            "id": role_id.value,
            "name": config["name"],
            "title": config["title"],
            "focus_traits": config["focus_traits"],
            "conversation_depth": config["conversation_depth"]
        })
    
    return {
        "code": 200,
        "data": roles,
        "message": "角色列表获取成功"
    }


@router.get("/role/{role_id}")
async def get_role_details(role_id: str):
    """获取特定角色的详细信息"""
    
    try:
        role = RoleType(role_id)
        config = ROLE_CONFIG[role]
        
        return {
            "code": 200,
            "data": {
                "id": role_id,
                "name": config["name"],
                "title": config["title"],
                "focus_traits": config["focus_traits"],
                "conversation_depth": config["conversation_depth"]
            },
            "message": "角色信息获取成功"
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的角色ID: {role_id}")


@router.get("/assessment-phases")
async def get_assessment_phases():
    """获取评估阶段信息"""
    
    phases = [
        {
            "id": "opening",
            "title": "破冰与背景了解",
            "description": "HR 与候选人建立联系，收集基础信息",
            "roles": ["hr"],
            "target_depth": 2
        },
        {
            "id": "technical",
            "title": "技术深度探索",
            "description": "技术总监评估专业能力与问题解决",
            "roles": ["tech_lead"],
            "target_depth": 4
        },
        {
            "id": "product_thinking",
            "title": "产品思维对话",
            "description": "产品经理考察用户视角与创新意识",
            "roles": ["product"],
            "target_depth": 6
        },
        {
            "id": "multi_perspective",
            "title": "多方圆桌讨论",
            "description": "多角色联合提问，考察综合素质",
            "roles": ["hr", "tech_lead", "product"],
            "target_depth": 8
        },
        {
            "id": "strategic",
            "title": "战略层面交流",
            "description": "CTO 最终评估与战略匹配度",
            "roles": ["cto"],
            "target_depth": 10
        }
    ]
    
    return {
        "code": 200,
        "data": phases,
        "message": "评估阶段信息获取成功"
    }


# ==================== 统计接口 ====================

@router.get("/candidate/{candidate_id}/sessions")
async def get_candidate_sessions(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """获取候选人的所有对话会话"""
    
    try:
        from models.assessment import AssessmentRecord
        
        sessions = db.query(AssessmentRecord).filter(
            AssessmentRecord.candidate_id == int(candidate_id),
            AssessmentRecord.assessment_type == "immersive_dialogue"
        ).all()
        
        return {
            "code": 200,
            "data": [
                {
                    "id": s.id,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "overall_score": s.overall_score,
                    "summary": s.summary
                }
                for s in sessions
            ],
            "message": "会话列表获取成功",
            "total": len(sessions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/session/{session_id}/details")
async def get_session_details(
    session_id: int,
    db: Session = Depends(get_db)
):
    """获取会话的详细信息"""
    
    try:
        from models.assessment import AssessmentRecord
        
        session = db.query(AssessmentRecord).filter(
            AssessmentRecord.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "code": 200,
            "data": {
                "id": session.id,
                "candidate_id": session.candidate_id,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "scores": session.scores,
                "overall_score": session.overall_score,
                "summary": session.summary,
                "session_data": session.session_data
            },
            "message": "会话详情获取成功"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
