"""
沉浸式对话 API 路由
"""

# ⚠️ 在导入任何依赖库前设置环境变量，确保本地OCR模型
import os
from pathlib import Path

os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
os.environ['PADDLE_PDX_OFFLINE_MODE'] = 'True'
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(Path.home() / ".paddleocr" / "models")
os.environ['PADDLE_REPO'] = ''
os.environ['PADDLEOCR_HOME'] = str(Path.home() / ".paddleocr")

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.immersive_dialogue import (
    ImmersiveDialogueService,
    RoleType,
    ROLE_CONFIG
)


router = APIRouter(prefix="/assessment/immersive", tags=["沉浸式对话"])


# ==================== 请求体模型 ====================

class NextQuestionRequest(BaseModel):
    candidate_id: str
    role_id: str = "hr"
    role_name: Optional[str] = None
    conversation_depth: int = 0
    history: List[Dict[str, Any]] = []
    target_position: Optional[str] = None


class AnalyzeResponseRequest(BaseModel):
    candidate_id: str
    candidate_name: Optional[str] = None
    current_speaker: str = "hr"
    candidate_response: str
    conversation_depth: int = 0
    previous_messages: List[Dict[str, Any]] = []
    target_position: Optional[str] = None


# ==================== candidate_id 验证器 ====================

def _validate_candidate_id(candidate_id: str) -> str:
    """验证并规范化 candidate_id（字符串格式）
    
    候选人 ID 在数据库中存储为 String(100)，支持：
    - 纯数字：\"123\"
    - UUID 字符串：\"cand_abc123\", \"user_12345\"
    - 任何非空字符串（最多 100 字符）
    """
    if not candidate_id:
        raise ValueError("候选人 ID 不能为空")
    
    normalized = candidate_id.strip()
    
    if not normalized:
        raise ValueError("候选人 ID 不能为空格")
    
    if len(normalized) > 100:
        raise ValueError(f"候选人 ID 长度不能超过 100 字符")
    
    return normalized


# ==================== 核心对话接口 ====================

@router.post("/next-question")
async def get_next_question(
    request: NextQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    生成下一个问题
    
    Args:
        request: NextQuestionRequest JSON body
    
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
        # ✅ 验证 candidate_id
        candidate_id = _validate_candidate_id(request.candidate_id)
        
        # 解析角色，无效时默认 HR
        try:
            role = RoleType(request.role_id)
        except ValueError:
            role = RoleType.HR
        
        service = ImmersiveDialogueService(db)
        
        result = await service.generate_next_question(
            id=candidate_id,
            candidate_name="",  # 可从数据库获取
            current_role=role,
            conversation_history=request.history,
            conversation_depth=request.conversation_depth,
            target_position=request.target_position
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "问题生成成功"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"参数无效: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成问题失败: {str(e)}")


@router.post("/analyze-response")
async def analyze_candidate_response(
    request: AnalyzeResponseRequest,
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
        # ✅ 验证 candidate_id
        candidate_id = _validate_candidate_id(request.candidate_id)
        
        # 解析角色，无效时默认 HR
        try:
            role = RoleType(request.current_speaker)
        except ValueError:
            role = RoleType.HR
        
        service = ImmersiveDialogueService(db)
        
        result = await service.analyze_candidate_response(
            id=candidate_id,
            candidate_name=request.candidate_name or "候选人",
            current_speaker=role,
            candidate_response=request.candidate_response,
            conversation_history=request.previous_messages,
            conversation_depth=request.conversation_depth,
            target_position=request.target_position
        )
        
        return {
            "code": 200,
            "data": result,
            "message": "分析成功"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"参数无效: {e}")
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
        # ✅ 验证 candidate_id
        if "candidate_id" in request_data:
            request_data["candidate_id"] = _validate_candidate_id(request_data["candidate_id"])
        
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
        # ✅ 验证 candidate_id
        candidate_id = _validate_candidate_id(candidate_id)
        
        from models.assessment import AssessmentRecord
        
        sessions = db.query(AssessmentRecord).filter(
            AssessmentRecord.candidate_id == candidate_id,
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


# ==================== 简历/进度检查接口 ====================

@router.get("/check-resume/{candidate_id}")
async def check_resume(candidate_id: str, db: Session = Depends(get_db)):
    """检查候选人是否已有简历/个人信息数据"""
    try:
        candidate_id = _validate_candidate_id(candidate_id)
        
        from models.user import User
        user = db.query(User).filter(User.id == int(candidate_id)).first()
        
        if not user:
            return {"code": 200, "data": {"has_resume": False}}
        
        has_resume = bool(user.resume_url) or bool(user.skills) or bool(user.education)
        
        return {
            "code": 200,
            "data": {
                "has_resume": has_resume,
                "resume_info": {
                    "name": user.real_name or user.username or "",
                    "email": user.email or "",
                    "education": user.education or "",
                    "skills": user.skills or [],
                    "resume_url": user.resume_url or "",
                } if has_resume else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/check-progress/{candidate_id}")
async def check_progress(candidate_id: str, db: Session = Depends(get_db)):
    """检查候选人是否有进行中的评估"""
    try:
        candidate_id = _validate_candidate_id(candidate_id)
        
        from models.assessment import AssessmentRecord, AssessmentStatus
        
        pending = db.query(AssessmentRecord).filter(
            AssessmentRecord.candidate_id == int(candidate_id),
            AssessmentRecord.assessment_status == AssessmentStatus.PENDING,
            AssessmentRecord.is_deleted == False
        ).order_by(AssessmentRecord.updated_at.desc()).first()
        
        if pending:
            return {
                "code": 200,
                "data": {
                    "has_progress": True,
                    "assessment_id": pending.id,
                    "job_id": pending.job_id,
                    "job_title": pending.job_title,
                    "created_at": pending.created_at.isoformat() if pending.created_at else None,
                    "updated_at": pending.updated_at.isoformat() if pending.updated_at else None,
                    "total_rounds": pending.total_rounds or 0,
                }
            }
        
        return {"code": 200, "data": {"has_progress": False}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/update-progress")
async def update_assessment_progress(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    保存/更新评估进度（自动保存和手动保存通用）
    
    Args:
        request_data: {
            "candidate_id": "123",
            "assessment_id": 456 (可选, 更新已有记录时传入),
            "job_id": 1,
            "job_title": "前端工程师",
            "status": "pending" | "completed",
            "total_rounds": 5,
            "duration_minutes": 3.5,
            "conversation_depth": 5,
            "conversation_summary": "...",
            "match_score": 78.5
        }
    """
    try:
        from models.assessment import AssessmentRecord, AssessmentStatus
        
        candidate_id = request_data.get("candidate_id")
        if candidate_id:
            candidate_id = _validate_candidate_id(str(candidate_id))
        
        assessment_id = request_data.get("assessment_id")
        status_str = request_data.get("status", "pending")
        
        status_map = {
            "pending": AssessmentStatus.PENDING,
            "completed": AssessmentStatus.COMPLETED,
            "failed": AssessmentStatus.FAILED,
        }
        status = status_map.get(status_str, AssessmentStatus.PENDING)
        
        if assessment_id:
            # 更新已有记录
            record = db.query(AssessmentRecord).filter(
                AssessmentRecord.id == int(assessment_id)
            ).first()
            if not record:
                raise HTTPException(status_code=404, detail="评估记录不存在")
            
            record.assessment_status = status
            record.total_rounds = request_data.get("total_rounds", record.total_rounds)
            record.duration_minutes = request_data.get("duration_minutes", record.duration_minutes)
            record.conversation_depth = request_data.get("conversation_depth", record.conversation_depth)
            record.conversation_summary = request_data.get("conversation_summary", record.conversation_summary)
            if request_data.get("match_score") is not None:
                record.match_score = request_data["match_score"]
        else:
            # 创建新记录
            record = AssessmentRecord(
                candidate_id=int(candidate_id),
                job_id=request_data.get("job_id", 0),
                job_title=request_data.get("job_title", "未知岗位"),
                assessment_status=status,
                assessment_mode="immersive",
                total_rounds=request_data.get("total_rounds", 0),
                duration_minutes=request_data.get("duration_minutes", 0),
                conversation_depth=request_data.get("conversation_depth", 0),
                conversation_summary=request_data.get("conversation_summary", ""),
                match_score=request_data.get("match_score"),
            )
            db.add(record)
        
        db.commit()
        db.refresh(record)
        
        return {
            "code": 200,
            "data": {
                "assessment_id": record.id,
                "status": record.assessment_status.value if record.assessment_status else None,
            },
            "message": "进度已保存"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存进度失败: {str(e)}")


# ==================== 简历解析接口 ====================

@router.post("/parse-resume")
async def parse_resume(
    candidate_id: str = Query(..., description="候选人ID"),
    candidate_name: str = Query(..., description="候选人姓名"),
    candidate_email: str = Query(..., description="候选人邮箱"),
    education: Optional[str] = Query(None, description="教育背景"),
    skills: Optional[str] = Query(None, description="技能标签"),
    projects: Optional[str] = Query(None, description="项目经验"),
    db: Session = Depends(get_db)
):
    """
    解析候选人简历和个人信息，提取关键数据
    
    Args:
        candidate_id: 候选人ID
        candidate_name: 候选人姓名
        candidate_email: 邮箱地址
        education: 教育背景（高中|大专|本科|硕士|博士）
        skills: 技能标签（逗号分隔）
        projects: 项目经验描述
    
    Returns:
        {
            "code": 200,
            "data": {
                "candidate_info": {
                    "name": "...",
                    "email": "...",
                    "education": "本科",
                    "technical_skills": ["JavaScript", "Python", ...],
                    "soft_skills": ["沟通", "团队协作", ...],
                    "experience_summary": "..."
                },
                "extracted_keywords": [...],
                "profile_completeness": 0.85,
                "assessed_dimensions": ["技术能力", "学习能力", ...]
            }
        }
    """
    try:
        service = ImmersiveDialogueService(db)
        
        # 解析技能标签
        technical_skills = [s.strip() for s in (skills or "").split(",")] if skills else []
        technical_skills = [s for s in technical_skills if s]
        
        # 提取软技能关键词
        soft_skills = []
        project_desc = projects or ""
        soft_skill_keywords = {
            "沟通": ["沟通", "presentation", "汇报", "表达"],
            "团队协作": ["团队", "协作", "合作", "沟通", "协调"],
            "领导力": ["领导", "负责", "主导", "带领", "管理"],
            "问题解决": ["解决", "调试", "修复", "优化", "改进"],
            "学习能力": ["学习", "探索", "研究", "掌握", "快速"],
        }
        
        for skill, keywords in soft_skill_keywords.items():
            if any(kw.lower() in project_desc.lower() for kw in keywords):
                soft_skills.append(skill)
        
        # 计算信息完整性
        completed_fields = sum([
            bool(candidate_name),
            bool(candidate_email),
            bool(education),
            bool(skills),
            bool(projects)
        ])
        profile_completeness = completed_fields / 5.0
        
        # 根据教育背景推断经验水平
        education_mapping = {
            "高中": "初级",
            "大专": "初级",
            "本科": "中级",
            "硕士": "高级",
            "博士": "专家级"
        }
        experience_level = education_mapping.get(education, "未知")
        
        # 生成评估维度
        assessed_dimensions = ["技术能力"]
        if technical_skills:
            assessed_dimensions.append("技术深度")
        if soft_skills:
            assessed_dimensions.extend(soft_skills)
        if experience_level in ["高级", "专家级"]:
            assessed_dimensions.extend(["领导力", "战略思维"])
        
        # 提取关键词
        extracted_keywords = technical_skills + soft_skills
        if education:
            extracted_keywords.append(f"学历:{education}")
        extracted_keywords = list(set(extracted_keywords))  # 去重
        
        return {
            "code": 200,
            "data": {
                "candidate_info": {
                    "name": candidate_name,
                    "email": candidate_email,
                    "education": education or "未填写",
                    "experience_level": experience_level,
                    "technical_skills": technical_skills,
                    "soft_skills": soft_skills,
                    "experience_summary": projects or "未填写"
                },
                "extracted_keywords": extracted_keywords,
                "profile_completeness": profile_completeness,
                "assessed_dimensions": list(set(assessed_dimensions))  # 去重
            },
            "message": "简历解析成功"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(..., description="简历文件"),
    candidate_id: str = Query(..., description="候选人ID"),
    db: Session = Depends(get_db)
):
    """
    上传并解析简历文件
    
    支持格式: PDF, Word (.doc, .docx), 图片 (jpg, png)
    
    Returns:
        {
            "code": 200,
            "data": {
                "filename": "resume.pdf",
                "file_size": 102400,
                "extracted_text": "...",
                "candidate_info": {
                    "name": "提取的姓名",
                    "email": "提取的邮箱",
                    "phone": "提取的电话",
                    "education": "本科",
                    "technical_skills": [...],
                    "work_experience": "..."
                }
            }
        }
    """
    import logging
    import time
    logger = logging.getLogger(__name__)
    
    try:
        # 验证文件类型
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        logger.info(f"上传简历: candidate_id={candidate_id}, filename={file.filename}, ext={file_ext}")
        
        if file_ext not in allowed_extensions:
            logger.warning(f"不支持的文件格式: {file_ext}")
            return {
                "code": 400,
                "message": f"不支持的文件格式: {file_ext}。支持格式: .pdf, .docx, .doc, .txt, .jpg, .jpeg, .png",
                "data": None
            }
        
        # 读取文件内容
        logger.info(f"正在读取文件内容...")
        content = await file.read()
        file_size = len(content)
        
        logger.info(f"文件大小: {file_size} bytes")
        
        # 验证文件大小（最大10MB）
        if file_size > 10 * 1024 * 1024:
            logger.warning(f"文件大小超过限制: {file_size} bytes")
            return {
                "code": 400,
                "message": f"文件大小超过10MB限制（当前: {file_size / 1024 / 1024:.1f}MB）",
                "data": None
            }
        
        # 文本提取
        logger.info(f"开始提取文本...")
        extracted_text = _extract_resume_text(content, file_ext)
        logger.info(f"提取文本成功，长度: {len(extracted_text)}")
        
        # 判断是否使用了OCR识别
        is_ocr = extracted_text.startswith("【OCR识别】")
        if is_ocr:
            extracted_text = extracted_text[7:]  # 移除 【OCR识别】 前缀 (共7个字符)
        
        # 如果提取失败（返回的是提示消息），直接返回
        if extracted_text.startswith("【"):
            logger.warning(f"文本提取失败或不支持: {extracted_text[:50]}")
            return {
                "code": 200,
                "message": extracted_text,
                "data": {
                    "filename": file.filename,
                    "file_size": file_size,
                    "extracted_text": extracted_text,
                    "extraction_method": "ocr" if is_ocr else "native",
                    "candidate_info": {
                        "name": "未提取",
                        "email": "",
                        "phone": "",
                        "education": "",
                        "technical_skills": [],
                        "work_experience": "",
                        "soft_skills": []
                    }
                }
            }
        
        # 解析关键信息
        logger.info(f"开始解析简历信息...")
        candidate_info = _parse_resume_info(extracted_text)
        logger.info(f"解析完成: {candidate_info}")
        
        # 计算额外的评估数据（与parse_resume保持一致）
        technical_skills = candidate_info.get('technical_skills', [])
        soft_skills = candidate_info.get('soft_skills', [])
        education = candidate_info.get('education', '')
        
        # 根据教育背景推断经验水平
        education_mapping = {
            "高中": "初级",
            "大专": "初级",
            "本科": "中级",
            "硕士": "高级",
            "博士": "专家级"
        }
        experience_level = education_mapping.get(education, "未知")
        candidate_info["experience_level"] = experience_level
        
        # 生成评估维度
        assessed_dimensions = ["技术能力"]
        if technical_skills:
            assessed_dimensions.append("技术深度")
        if soft_skills:
            assessed_dimensions.extend(soft_skills)
        if experience_level in ["高级", "专家级"]:
            assessed_dimensions.extend(["领导力", "战略思维"])
        
        assessed_dimensions = list(set(assessed_dimensions))  # 去重
        
        # 计算信息完整性
        completed_fields = sum([
            bool(candidate_info.get('name')),
            bool(candidate_info.get('email')),
            bool(education),
            bool(technical_skills),
            bool(candidate_info.get('work_experience'))
        ])
        profile_completeness = completed_fields / 5.0
        
        # 提取关键词
        extracted_keywords = technical_skills + soft_skills
        if education:
            extracted_keywords.append(f"学历:{education}")
        extracted_keywords = list(set(extracted_keywords))
        
        return {
            "code": 200,
            "message": "简历解析成功",
            "data": {
                "filename": file.filename,
                "file_size": file_size,
                "extracted_text": extracted_text[:500],  # 返回前500字作为预览
                "extraction_method": "ocr" if is_ocr else "native",
                "candidate_info": candidate_info,
                "extracted_keywords": extracted_keywords,
                "profile_completeness": profile_completeness,
                "assessed_dimensions": assessed_dimensions
            }
        }
    
    except ValueError as e:
        logger.error(f"文件验证失败: {str(e)}")
        return {
            "code": 400,
            "message": f"文件验证失败: {str(e)}",
            "data": None
        }
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}", exc_info=True)
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"详细错误信息:\n{error_detail}")
        return {
            "code": 500,
            "message": f"文件处理失败: {str(e)}",
            "error_detail": str(e),
            "data": None
        }


def _ocr_extract_text(content: bytes, file_ext: str) -> str:
    """使用 OCR 从图片或扫描版PDF中提取文本
    
    支持三种模式：
    1. PaddleOCR (如果可用)
    2. EasyOCR (备选)
    3. 回退模式：返回包含指导信息的标记
    """
    import logging
    from io import BytesIO
    logger = logging.getLogger(__name__)
    
    # ⏱️ 超时保护
    timeout_per_page = 30  # 每页最多 30 秒
    total_timeout = 300    # 总超时 5 分钟
    start_time = time.time()
    
    try:
        logger.info(f"启用 OCR 识别，文件格式: {file_ext}")
        
        # 尝试方案 1: PaddleOCR
        try:
            logger.info("尝试使用 PaddleOCR...")
            from paddleocr_local import create_paddleocr
            from PIL import Image
            
            # 在函数开始就初始化一次，而不是每页都初始化
            ocr = create_paddleocr()
            logger.info("✅ PaddleOCR 模型已加载")
            
            if file_ext == '.pdf':
                logger.info("PDF OCR: 转换为图片进行识别")
                try:
                    import pdfplumber
                    with pdfplumber.open(BytesIO(content)) as pdf:
                        all_text = []
                        for page_num, page in enumerate(pdf.pages):
                            # 检查总超时
                            if time.time() - start_time > total_timeout:
                                logger.error(f"⏱️ PDF OCR 总超时 ({total_timeout}秒)，已处理 {page_num}/{len(pdf.pages)} 页")
                                all_text.append("[超时: 文件过大，已自动停止]")
                                break
                            
                            logger.info(f"正在OCR识别第 {page_num + 1}/{len(pdf.pages)} 页...")
                            try:
                                # 每页超时控制
                                page_start = time.time()
                                im = page.to_image(resolution=300)
                                
                                if time.time() - page_start > timeout_per_page:
                                    logger.warning(f"⏱️ 第 {page_num + 1} 页转换超时 ({timeout_per_page}秒)")
                                    all_text.append("[超时: 页面过大]")
                                    continue
                                
                                pil_image = im.original
                                
                                logger.debug(f"  执行 OCR 识别...")
                                ocr_start = time.time()
                                result = ocr.ocr(pil_image, cls=False)
                                ocr_time = time.time() - ocr_start
                                
                                if ocr_time > timeout_per_page:
                                    logger.warning(f"⏱️ 第 {page_num + 1} 页 OCR 超时 ({ocr_time:.1f}秒)")
                                    all_text.append("[超时: OCR 处理缓慢]")
                                    continue
                                
                                page_text = ""
                                if result and result[0]:
                                    page_text = "\n".join([line[1][0] for line in result[0]])
                                all_text.append(page_text)
                                logger.info(f"  第 {page_num + 1} 页: {len(page_text)} 字")
                            except Exception as page_err:
                                logger.warning(f"  第 {page_num + 1} 页识别失败: {page_err}")
                                all_text.append("")
                                continue
                        
                        full_text = '\n'.join(all_text).strip()
                        if full_text:
                            logger.info(f"✅ PaddleOCR PDF 成功，总长度: {len(full_text)}")
                            return full_text
                        else:
                            logger.warning("PDF 所有页面识别结果为空")
                except Exception as e:
                    logger.warning(f"PaddleOCR PDF 处理失败: {e}")
                    raise
            
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                logger.info(f"PaddleOCR 图片识别: {file_ext}")
                try:
                    image = Image.open(BytesIO(content))
                    
                    logger.debug(f"  执行 OCR 识别...")
                    result = ocr.ocr(image, cls=False)
                    text = "\n".join([line[1][0] for line in result[0]]) if result and result[0] else ""
                    
                    if text.strip():
                        logger.info(f"✅ PaddleOCR 图片成功，长度: {len(text)}")
                        return text
                except Exception as e:
                    logger.warning(f"PaddleOCR 图片处理失败: {e}")
                    raise
        
        except Exception as paddle_err:
            # 处理所有 PaddleOCR 异常（包括 AttributeError、其他异常等）
            logger.warning(f"❌ PaddleOCR 不可用: {type(paddle_err).__name__}: {paddle_err}")
            
            if isinstance(paddle_err, AttributeError):
                logger.error(f"PaddleOCR 版本兼容性问题: {paddle_err}")
                logger.warning("💡 建议: 运行 python fix_paddleocr_issue.py 修复版本问题")
            
            # 尝试方案 2: EasyOCR (备选)
            try:
                logger.info("尝试使用 EasyOCR...")
                import easyocr
                from PIL import Image
                
                reader = easyocr.Reader(['ch'], gpu=False)
                logger.info("✅ EasyOCR 模型已加载")
                
                if file_ext == '.pdf':
                    import pdfplumber
                    with pdfplumber.open(BytesIO(content)) as pdf:
                        all_text = []
                        for page_num, page in enumerate(pdf.pages):
                            logger.info(f"EasyOCR 识别第 {page_num + 1}/{len(pdf.pages)} 页...")
                            try:
                                im = page.to_image(resolution=300)
                                pil_image = im.original
                                result = reader.readtext(pil_image, detail=0)
                                page_text = '\n'.join(result) if result else ""
                                all_text.append(page_text)
                                logger.info(f"  第 {page_num + 1} 页: {len(page_text)} 字")
                            except Exception as e:
                                logger.warning(f"  第 {page_num + 1} 页识别失败: {e}")
                                all_text.append("")
                                continue
                        
                        full_text = '\n'.join(all_text).strip()
                        if full_text:
                            logger.info(f"✅ EasyOCR PDF 成功，总长度: {len(full_text)}")
                            return full_text
                
                elif file_ext in ['.jpg', '.jpeg', '.png']:
                    logger.info(f"EasyOCR 图片识别...")
                    image = Image.open(BytesIO(content))
                    result = reader.readtext(image, detail=0)
                    text = '\n'.join(result) if result else ""
                    if text.strip():
                        logger.info(f"✅ EasyOCR 图片成功，长度: {len(text)}")
                        return text
                
                logger.warning("EasyOCR 识别结果为空")
            
            except ImportError as import_err:
                logger.warning(f"⚠️ EasyOCR 未安装: {import_err}")
                logger.info("💡 要安装 EasyOCR，请运行: pip install easyocr")
            except AttributeError as easy_err:
                logger.warning(f"❌ EasyOCR 版本问题: {easy_err}")
            except Exception as easy_err:
                logger.warning(f"❌ EasyOCR 失败: {type(easy_err).__name__}: {easy_err}")
            
            # 方案 3: 回退处理
            logger.warning("所有 OCR 方案都失败，返回回退消息")
            return "【⚠️ OCR功能暂时不可用】\n\n目前无法自动识别您上传的文件。这可能是因为：\n• PaddleOCR 版本不兼容\n• EasyOCR 未安装\n• 模型初始化失败\n\n您有以下选择：\n1️⃣ 继续手动填写表单中的信息\n2️⃣ 尝试上传纯文本(.txt)或Word文档(.docx)\n3️⃣ 运行修复: python fix_paddleocr_issue.py\n4️⃣ 安装 EasyOCR: pip install easyocr\n\n✨ 系统仍然可以正常使用，只需手动补全信息即可"
    
    except Exception as e:
        logger.error(f"OCR 处理异常: {type(e).__name__}: {e}", exc_info=True)
        return "【⚠️ 系统错误】请重试或手动填写表单"


def _extract_resume_text(content: bytes, file_ext: str) -> str:
    """从不同格式的文件中提取文本"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if file_ext == '.txt':
            logger.info("提取 TXT 格式文件")
            return content.decode('utf-8', errors='ignore')
        
        elif file_ext == '.docx':
            logger.info("尝试提取 DOCX 格式文件")
            try:
                from docx import Document
                from io import BytesIO
                doc = Document(BytesIO(content))
                text = '\n'.join([para.text for para in doc.paragraphs])
                if text:
                    logger.info(f"DOCX 提取成功，长度: {len(text)}")
                    return text
                else:
                    logger.warning("DOCX 文档为空")
                    return "【Word文档已上传但内容为空】"
            except ImportError as e:
                logger.warning(f"python-docx 库未安装: {e}")
                # 降级处理：尝试基本的文本查找（可能找到部分文本）
                try:
                    text = content.decode('utf-8', errors='ignore')
                    if text:
                        return f"【Word文件内容预览】\n{text[:1000]}"
                except:
                    return "【Word文档已上传】系统暂无法提取内容，请确保安装: pip install python-docx"
            except Exception as e:
                logger.error(f"DOCX 提取出错: {e}")
                return f"【Word文档解析失败】{str(e)}"
        
        elif file_ext == '.pdf':
            logger.info("尝试提取 PDF 格式文件")
            try:
                import pdfplumber
                from io import BytesIO
                with pdfplumber.open(BytesIO(content)) as pdf:
                    text = '\n'.join([page.extract_text() or '' for page in pdf.pages])
                if text:
                    logger.info(f"PDF 提取成功，长度: {len(text)}")
                    return text
                else:
                    logger.warning("PDF 文档为空，尝试使用 OCR 识别")
                    ocr_text = _ocr_extract_text(content, file_ext)
                    if ocr_text and not ocr_text.startswith("【"):
                        logger.info(f"OCR 识别成功，长度: {len(ocr_text)}")
                        return f"【OCR识别】{ocr_text}"
                    else:
                        logger.warning("OCR 识别也失败")
                        return "【PDF文档已上传但无可识别内容】"
            except ImportError as e:
                logger.warning(f"pdfplumber 库未安装: {e}")
                return "【PDF文件已上传】系统暂无法提取内容，请确保安装: pip install pdfplumber"
            except Exception as e:
                logger.error(f"PDF 提取出错: {e}")
                return f"【PDF文档解析失败】{str(e)}"
        
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            logger.info("检测到图片文件，使用 OCR 识别")
            ocr_text = _ocr_extract_text(content, file_ext)
            if ocr_text and not ocr_text.startswith("【"):
                logger.info(f"OCR 识别成功，长度: {len(ocr_text)}")
                return f"【OCR识别】{ocr_text}"
            else:
                logger.warning("图片 OCR 识别失败")
                return "【图片文件已上传但无可识别内容】"
        
        elif file_ext == '.doc':
            logger.info("检测到旧版Word文件")
            return "【Word 97-2003格式已上传】建议转换为 .docx 格式获得更好的兼容性，或请手动填写表单"
        
        else:
            logger.warning(f"未知格式: {file_ext}")
            return f"【{file_ext}格式文件已上传】请手动填写表单补充信息"
    
    except Exception as e:
        logger.error(f"文本提取异常: {e}", exc_info=True)
        return f"【文件处理出错】{str(e)}"


def _parse_resume_info(text: str) -> Dict[str, Any]:
    """从简历文本中解析关键信息"""
    import re
    import logging
    logger = logging.getLogger(__name__)
    
    info = {
        "name": "未提取",
        "email": "",
        "phone": "",
        "education": "",
        "technical_skills": [],
        "work_experience": "",
        "soft_skills": []
    }
    
    try:
        # 处理空文本或仅包含提示信息的情况
        if not text or text.startswith("【"):
            logger.info(f"文本为空或仅包含提示信息，返回默认值")
            return info
        
        logger.info(f"开始解析简历文本，长度: {len(text)}")
        
        # 尝试提取姓名 (支持多种格式)
        name_patterns = [
            r'(?:^|\n)\s*姓名[:\s：]+([^\n\r，,]+)',  # 姓名: 张三 (支持缩进)
            r'(?:^|\n)\s*名字[:\s：]+([^\n\r，,]+)',  # 名字: 张三 (支持缩进)
            r'(?:^|\n)\s*Name[:\s]+([^\n\r,]+)',      # Name: Zhang San (支持缩进)
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if name_match:
                extracted_name = name_match.group(1).strip()
                # 过滤掉非法的名字（太长或包含特殊字符）
                if extracted_name and len(extracted_name) <= 20 and not any(c in extracted_name for c in '【】《》<>/'):
                    info["name"] = extracted_name
                    logger.info(f"提取姓名: {info['name']}")
                    break
        
        # 尝试提取邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        if email_match:
            info["email"] = email_match.group()
            logger.info(f"提取邮箱: {info['email']}")
        
        # 尝试提取电话
        phone_pattern = r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            info["phone"] = phone_match.group()
            logger.info(f"提取电话: {info['phone']}")
        
        # 尝试提取学位信息
        education_keywords = ["本科", "硕士", "博士", "大专", "高中", "Associate", "Bachelor", "Master", "PhD"]
        for keyword in education_keywords:
            if keyword in text:
                info["education"] = keyword
                logger.info(f"提取学历: {keyword}")
                break
        
        # 尝试提取技能关键词
        skill_keywords = [
            "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "PHP",
            "TypeScript", "Vue", "React", "Angular", "Node.js", "Django", "Flask",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "Git", "Linux", "SQL", "REST API", "GraphQL"
        ]
        info["technical_skills"] = [skill for skill in skill_keywords if skill in text]
        if info["technical_skills"]:
            logger.info(f"提取技能: {info['technical_skills']}")
        
        # 提取工作经验
        if any(kw in text for kw in ["工作经验", "工作经历", "Experience", "employment"]):
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if "工作" in line or "experience" in line.lower():
                    info["work_experience"] = '\n'.join(lines[i:min(i+3, len(lines))])
                    logger.info(f"提取工作经验: {info['work_experience'][:100]}")
                    break
        
        # 提取软技能（基于关键词匹配）
        soft_skill_keywords = {
            "通信能力": ["沟通", "表达", "演讲", "汇报", "协调"],
            "团队合作": ["团队", "合作", "协作", "配合", "集体"],
            "创新思维": ["创新", "创意", "想法", "方案", "设计"],
            "解决问题": ["解决", "调试", "修复", "优化", "改进"],
            "领导力": ["领导", "负责", "主导", "带领", "管理"],
            "学习能力": ["学习", "探索", "研究", "掌握", "快速"],
        }
        
        work_exp_text = info.get("work_experience", "") + text
        for skill_name, keywords in soft_skill_keywords.items():
            if any(kw in work_exp_text for kw in keywords):
                info["soft_skills"].append(skill_name)
        
        if info["soft_skills"]:
            logger.info(f"提取软技能: {info['soft_skills']}")
        
        logger.info(f"简历解析完成: {info}")
        return info
    
    except Exception as e:
        logger.error(f"解析简历时出错: {e}", exc_info=True)
        return info
