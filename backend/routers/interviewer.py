"""
虚拟面试官 API 路由

实现双轨模式：
- SSE 流式返回 LLM 对话
- 后台任务进行候选人评估
"""

import json
import asyncio
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
import logging

from schemas.interviewer import (
    InterviewerChatRequest,
    ChatResponse,
    InterviewerRoleInfo,
    InterviewSessionState,
    SwitchInterviewerRequest,
)
from services.interviewer_service import get_interviewer_service
from models.interviewer_role import get_role_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview", tags=["interviewer"])


# ========================================
# API 1: 获取所有可用的虚拟面试官
# ========================================

@router.get("/interviewers", response_model=list)
async def get_all_interviewers():
    """
    获取所有可用的虚拟面试官列表
    
    返回:
        列表，包含所有面试官的信息
    """
    service = get_interviewer_service()
    interviewers = service.get_all_available_interviewers()
    return interviewers


# ========================================
# API 2: 初始化面试会话
# ========================================

@router.post("/session/create")
async def create_interview_session(
    candidate_id: str = Query(..., description="候选人ID"),
    interviewer_id: str = Query(..., description="初始面试官ID")
):
    """
    创建新的面试会话
    
    参数:
        candidate_id: 候选人ID
        interviewer_id: 初始面试官ID
    
    返回:
        会话ID 和 初始欢迎消息
    """
    service = get_interviewer_service()
    
    try:
        # 创建会话并切换到指定面试官
        session_id = service.create_session(candidate_id, interviewer_id)
        
        # 获取角色信息
        role_manager = get_role_manager()
        role_config = role_manager.get_role(interviewer_id)
        
        if not role_config:
            raise HTTPException(status_code=404, detail="面试官不存在")
        
        # 构建欢迎消息
        opening_message = (
            f"你好，我是 {role_config.role_name}。"
            f"今天很高兴能与你进行这次对话。"
            f"我主要负责评估你的 {', '.join(role_config.focus_areas)}。"
            f"让我们开始吧，请先介绍一下你自己。"
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "interviewer": {
                "role_id": role_config.role_id,
                "role_name": role_config.role_name,
                "tone": role_config.tone,
                "focus_areas": role_config.focus_areas,
            },
            "opening_message": opening_message
        }
    
    except Exception as e:
        logger.error(f"创建会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# API 3: SSE 流式对话（双轨核心）
# ========================================

@router.post("/chat/stream")
async def chat_stream(
    request: InterviewerChatRequest,
    background_tasks: BackgroundTasks
):
    """
    流式聊天 API - 核心的双轨处理实现
    
    双轨模式：
    - 主线程（前端）：接收 SSE 流式对话结果
    - 后台线程：执行候选人评估（不阻塞主线程）
    
    参数:
        request: 聊天请求
        background_tasks: FastAPI 后台任务
    
    返回:
        StreamingResponse，SSE 格式的流式数据
    """
    
    logger.info(
        f"开始流式对话 - "
        f"面试官: {request.interviewer_id}, "
        f"候选人: {request.candidate_id}, "
        f"轮次: {request.round_num}"
    )
    
    service = get_interviewer_service()
    
    # 获取当前面试官的 System Prompt（动态根据轮次生成）
    role_manager = get_role_manager()
    system_prompt = role_manager.get_system_prompt(
        request.interviewer_id,
        request.round_num
    )
    
    # ========== 关键：双轨处理 ==========
    
    # 后台任务：评估候选人（不阻塞对话流）
    async def background_evaluation():
        """后台评估任务"""
        try:
            await service.evaluate_candidate(
                candidate_id=request.candidate_id,
                interviewer_id=request.interviewer_id,
                candidate_response=request.candidate_message,
                question="[前端提供的问题]",  # 实际应从前端传递
                round_num=request.round_num
            )
            logger.info(f"后台评估完成 - 候选人: {request.candidate_id}")
        except Exception as e:
            logger.error(f"后台评估失败: {e}")
    
    # 添加后台任务（这是 FastAPI BackgroundTasks 的方式）
    background_tasks.add_task(background_evaluation)
    
    # 或使用 asyncio.create_task（这是更底层的方式）
    # asyncio.create_task(background_evaluation())
    
    # ========== 主线程：流式返回对话 ==========
    
    async def generate_chat_stream() -> AsyncGenerator[str, None]:
        """生成 SSE 流"""
        
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'interviewer_id': request.interviewer_id})}\n\n"
            
            # 流式返回 LLM 聊天结果
            full_response = ""
            async for chunk in service.chat_with_llm(
                interviewer_id=request.interviewer_id,
                candidate_message=request.candidate_message,
                round_num=request.round_num,
                system_prompt=system_prompt
            ):
                full_response += chunk
                # 以 SSE 格式流式返回
                yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
            
            # 记录对话
            state = role_manager.get_current_state()
            if state:
                state.add_message("assistant", full_response)
                state.add_message("user", request.candidate_message)
            
            # 发送完成事件
            yield f"data: {json.dumps({'type': 'end', 'status': 'success'})}\n\n"
            
        except Exception as e:
            logger.error(f"流式对话出错: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    # 返回 StreamingResponse
    return StreamingResponse(
        generate_chat_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# ========================================
# API 4: 切换面试官
# ========================================

@router.post("/interviewer/switch")
async def switch_interviewer(
    request: SwitchInterviewerRequest
):
    """
    切换到新的虚拟面试官
    
    当需要转到下一位面试官（如从 HR 到技术总监）时调用此 API
    
    参数:
        request.interviewer_id: 新面试官的 ID
        request.candidate_id: 候选人 ID
        request.session_id: 会话 ID
    
    返回:
        新面试官的信息和欢迎消息
    """
    
    logger.info(f"切换面试官到: {request.interviewer_id}")
    
    service = get_interviewer_service()
    
    try:
        result = service.switch_interviewer(
            interviewer_id=request.interviewer_id,
            candidate_id=request.candidate_id,
            session_id=request.session_id or "default"
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        # 获取新面试官的欢迎消息
        role_manager = get_role_manager()
        role_config = role_manager.get_role(request.interviewer_id)
        
        opening_message = (
            f"你好，我是新进来的面试官 {role_config.role_name}。"
            f"现在由我来继续和你的对话。"
            f"我主要关注 {', '.join(role_config.focus_areas)} 方面。"
            f"请继续。"
        )
        
        return {
            "status": "success",
            "interviewer": {
                "role_id": role_config.role_id,
                "role_name": role_config.role_name,
                "tone": role_config.tone,
                "focus_areas": role_config.focus_areas,
            },
            "opening_message": opening_message,
            "current_round": role_manager.get_current_state().current_round if role_manager.get_current_state() else 0
        }
    
    except Exception as e:
        logger.error(f"切换面试官失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# API 5: 获取当前会话评估状态
# ========================================

@router.get("/session/{session_id}/state")
async def get_session_state(session_id: str):
    """
    获取当前会话的评估状态
    
    包含当前面试官、轮次、已有的评分等信息
    """
    
    service = get_interviewer_service()
    role_manager = get_role_manager()
    
    # 获取会话状态
    session_state = service.get_session_state(session_id)
    
    # 获取当前角色状态
    current_state = role_manager.get_current_state()
    
    if not current_state:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "session_id": session_id,
        "current_interviewer": current_state.config.role_name,
        "current_round": current_state.current_round,
        "conversation_count": len(current_state.conversation_history),
        "questions_asked": current_state.questions_asked,
        "scores": current_state.scores,
        "evaluation_focus": current_state.config.evaluation_focus,
        "last_updated": current_state.state_created_at.isoformat()
    }


# ========================================
# API 6: 推进到下一轮
# ========================================

@router.post("/session/{session_id}/next-round")
async def advance_round(
    session_id: str,
    next_interviewer_id: str = Query(...)
):
    """
    推进到下一轮面试（可选切换面试官）
    
    参数:
        session_id: 会话 ID
        next_interviewer_id: 下一个面试官的 ID
    """
    
    service = get_interviewer_service()
    role_manager = get_role_manager()
    
    try:
        # 推进轮次
        role_manager.advance_round()
        
        # 切换面试官
        service.switch_interviewer(
            interviewer_id=next_interviewer_id,
            candidate_id="[from_session]",
            session_id=session_id
        )
        
        # 获取新轮次的 System Prompt
        current_state = role_manager.get_current_state()
        new_system_prompt = role_manager.get_system_prompt(
            next_interviewer_id,
            current_state.current_round
        )
        
        role_config = role_manager.get_role(next_interviewer_id)
        
        return {
            "status": "success",
            "new_round": current_state.current_round,
            "new_interviewer": role_config.role_name,
            "system_prompt": new_system_prompt
        }
    
    except Exception as e:
        logger.error(f"推进轮次失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# API 7: 获取评估摘要
# ========================================

@router.get("/session/{session_id}/summary")
async def get_evaluation_summary(session_id: str):
    """
    获取当前会话的评估摘要
    
    包含：
    - 所有对话的汇总
    - 各维度的评分
    - 主要优势和需改进点
    """
    
    service = get_interviewer_service()
    role_manager = get_role_manager()
    
    # 获取当前评估状态
    summary = role_manager.get_evaluation_summary()
    
    # 获取历史状态
    history = role_manager.get_state_history()
    
    return {
        "session_id": session_id,
        "current_interview": summary,
        "all_interviews_count": len(history) + 1,
        "history": [h.to_dict() for h in history[-3:]],  # 最近 3 个
        "timestamp": str(datetime.now())
    }


# ========================================
# API 8: 异步后台评估（可选）
# ========================================

@router.post("/evaluate/background")
async def evaluate_in_background(
    candidate_id: str = Query(...),
    interviewer_id: str = Query(...),
    response: str = Query(...),
    background_tasks: BackgroundTasks = ...
):
    """
    手动触发后台评估任务
    
    这个端点用于当前端需要显式触发评估时
    """
    
    service = get_interviewer_service()
    
    # 添加后台任务
    background_tasks.add_task(
        service.evaluate_candidate,
        candidate_id=candidate_id,
        interviewer_id=interviewer_id,
        candidate_response=response,
        question="[automatic_evaluation]",
        round_num=0
    )
    
    return {
        "status": "accepted",
        "message": "评估任务已添加到后台队列，将异步执行"
    }


# ========================================
# WebSocket 端点（可选，用于更高级的双向通信）
# ========================================

from fastapi import WebSocket

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket 端点 - 实时双向对话
    
    这提供了比 SSE 更高级的方式实现双轨处理
    """
    
    await websocket.accept()
    service = get_interviewer_service()
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            
            interviewer_id = data.get("interviewer_id")
            candidate_message = data.get("message")
            round_num = data.get("round_num", 0)
            
            logger.info(f"WebSocket 消息 - {interviewer_id}: {candidate_message[:50]}")
            
            # 异步处理：流式发送对话
            full_response = ""
            async for chunk in service.chat_with_llm(
                interviewer_id,
                candidate_message,
                round_num
            ):
                full_response += chunk
                await websocket.send_json({
                    "type": "content",
                    "data": chunk
                })
            
            # 后台评估（不等待）
            asyncio.create_task(
                service.evaluate_candidate(
                    candidate_id=data.get("candidate_id"),
                    interviewer_id=interviewer_id,
                    candidate_response=candidate_message,
                    question="[ws_question]",
                    round_num=round_num
                )
            )
            
            # 发送完成信号
            await websocket.send_json({
                "type": "end",
                "status": "success"
            })
    
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        await websocket.close(code=1000)


# 导入 datetime（如果还没有）
from datetime import datetime
