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
    import os
    from io import BytesIO
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"启用 OCR 识别，文件格式: {file_ext}")
        
        # 导入本地模型配置
        from paddleocr_local import create_paddleocr
        # 导入本地模型配置
        from paddleocr_local import create_paddleocr
        
        # 尝试方案 1: PaddleOCR
        try:
            from PIL import Image
            
            logger.info("尝试使用 PaddleOCR...")
            
            if file_ext == '.pdf':
                logger.info("PDF OCR: 转换为图片进行识别")
                try:
                    import pdfplumber
                    with pdfplumber.open(BytesIO(content)) as pdf:
                        all_text = []
                        for page_num, page in enumerate(pdf.pages):
                            logger.info(f"正在OCR识别第 {page_num + 1}/{len(pdf.pages)} 页...")
                            im = page.to_image(resolution=300)
                            pil_image = im.original
                            
                            try:
                                logger.info(f"  初始化 PaddleOCR 模型...")
                                ocr = create_paddleocr()
                                
                                logger.info(f"  执行 OCR 识别...")
                                result = ocr.ocr(pil_image, cls=True)
                                
                                page_text = '\n'.join([line[0] for line in result[0]]) if result else ""
                                all_text.append(page_text)
                                logger.info(f"  第 {page_num + 1} 页识别完成，长度: {len(page_text)}")
                            except Exception as page_err:
                                logger.warning(f"  第 {page_num + 1} 页识别失败: {page_err}")
                                all_text.append("")
                                continue
                        
                        full_text = '\n'.join(all_text).strip()
                        if full_text:
                            logger.info(f"PaddleOCR 成功，总长度: {len(full_text)}")
                            return full_text
                except Exception as e:
                    logger.warning(f"PaddleOCR PDF 处理失败: {e}")
                    raise
            
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                logger.info(f"PaddleOCR 图片识别: {file_ext}")
                try:
                    from PIL import Image
                    image = Image.open(BytesIO(content))
                    
                    logger.info(f"  初始化 PaddleOCR 模型...")
                    ocr = create_paddleocr()
                    
                    logger.info(f"  执行 OCR 识别...")
                    result = ocr.ocr(image, cls=True)
                    text = '\n'.join([line[0] for line in result[0]]) if result else ""
                    
                    if text.strip():
                        logger.info(f"PaddleOCR 成功，长度: {len(text)}")
                        return text
                except Exception as e:
                    logger.warning(f"PaddleOCR 图片处理失败: {e}")
                    raise
        
        except Exception as paddle_err:
            logger.warning(f"PaddleOCR 不可用，尝试 EasyOCR: {paddle_err}")
            
            # 尝试方案 2: EasyOCR (备选)
            try:
                import easyocr
                from PIL import Image
                
                logger.info("尝试使用 EasyOCR...")
                reader = easyocr.Reader(['ch'], gpu=False)
                
                if file_ext == '.pdf':
                    import pdfplumber
                    with pdfplumber.open(BytesIO(content)) as pdf:
                        all_text = []
                        for page_num, page in enumerate(pdf.pages):
                            logger.info(f"EasyOCR 识别第 {page_num + 1}/{len(pdf.pages)} 页...")
                            im = page.to_image(resolution=300)
                            pil_image = im.original
                            result = reader.readtext(pil_image, detail=0)
                            page_text = '\n'.join(result) if result else ""
                            all_text.append(page_text)
                        
                        full_text = '\n'.join(all_text).strip()
                        if full_text:
                            logger.info(f"EasyOCR 成功，总长度: {len(full_text)}")
                            return full_text
                
                elif file_ext in ['.jpg', '.jpeg', '.png']:
                    logger.info(f"EasyOCR 图片识别...")
                    image = Image.open(BytesIO(content))
                    result = reader.readtext(image, detail=0)
                    text = '\n'.join(result) if result else ""
                    if text.strip():
                        logger.info(f"EasyOCR 成功，长度: {len(text)}")
                        return text
                
            except Exception as easy_err:
                logger.warning(f"EasyOCR 也不可用: {easy_err}")
                
                # 方案 3: 回退处理
                logger.warning("OCR 处理不可用，返回回退消息")
                return "【⚠️ OCR功能暂不可用】\n系统暂无法进行自动识别（网络或模型问题）。\n\n请采取以下方案之一：\n1️⃣ 继续使用该系统：手动在表单中填写信息\n2️⃣ 尝试上传其他格式：Word(.docx) 或纯文本文件(.txt)\n3️⃣ 联系管理员：获取配置帮助\n\n提示：您仍然可以手动完成所有信息的输入"
    
    except Exception as e:
        logger.error(f"OCR 处理异常: {e}", exc_info=True)
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
