"""
虚拟面试官业务逻辑模块

包含：
1. chat_with_llm - LLM 对话（支持流式输出）
2. evaluate_candidate - 候选人评估
3. 双轨并行处理
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List, Optional
from datetime import datetime
import logging

from models.interviewer_role import (
    InterviewerRoleManager, 
    InterviewerState, 
    get_role_manager
)

logger = logging.getLogger(__name__)


class InterviewerService:
    """虚拟面试官服务 - 核心业务逻辑"""
    
    def __init__(self):
        self.role_manager = get_role_manager()
        self.session_states: Dict[str, Dict[str, Any]] = {}  # 存储会话状态
        
    # ========================
    # 核心方法 1: LLM 聊天
    # ========================
    
    async def chat_with_llm(
        self,
        interviewer_id: str,
        candidate_message: str,
        round_num: int,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        调用 LLM 进行对话，以流式方式返回结果
        
        参数:
            interviewer_id: 面试官ID
            candidate_message: 候选人的消息
            round_num: 当前轮次
            system_prompt: 自定义 System Prompt（如果为 None 则自动生成）
        
        返回:
            异步生成器，每次 yield 一个 token 或短句子
        """
        
        # 使用自动生成或传入的 System Prompt
        if system_prompt is None:
            system_prompt = self.role_manager.get_system_prompt(
                interviewer_id, 
                round_num
            )
        
        # 这里演示流式返回的模式
        # 实际生产中会调用真实的 LLM API（如 OpenAI, DeepSeek 等）
        
        logger.info(
            f"LLM Chat - Interviewer: {interviewer_id}, "
            f"Round: {round_num}, Message: {candidate_message[:50]}..."
        )
        
        # 构建完整的消息历史
        messages = self._build_message_history(
            interviewer_id,
            candidate_message
        )
        
        # 模拟调用 LLM（真实情况下替换为真实 API 调用）
        llm_response = await self._call_llm_api(
            system_prompt=system_prompt,
            messages=messages,
            temperature=0.7
        )
        
        # 流式返回 token
        buffer = ""
        for char in llm_response:
            buffer += char
            # 如果缓冲区满足某个条件，就 yield 出去（例如达到完整的词或句子）
            if len(buffer) >= 5 or char in ['。', '！', '？', '\n']:
                yield buffer
                buffer = ""
        
        # 返回剩余的缓冲
        if buffer:
            yield buffer
    
    async def _call_llm_api(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        调用真实 LLM API（默认实现，应根据需要修改）
        
        在生产环境中，应该调用：
        - OpenAI GPT-4 / GPT-3.5
        - DeepSeek
        - Claude
        - 其他商用或开源 LLM
        """
        
        # TODO: 实现真实的 LLM 调用
        # 这里是示例实现
        
        # 示例：使用 OpenAI
        # import openai
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     temperature=temperature,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         *messages
        #     ]
        # )
        # return response.choices[0].message.content
        
        # 示例响应
        await asyncio.sleep(0.1)  # 模拟 API 调用延迟
        
        role_config = self.role_manager.get_role(messages[0].get("interviewer_id", ""))
        if not role_config:
            return "很高兴与你交谈。"
        
        return f"感谢你的回答。作为 {role_config.role_name}，我继续对你感兴趣。"
    
    def _build_message_history(
        self,
        interviewer_id: str,
        new_message: str
    ) -> List[Dict[str, str]]:
        """构建消息历史供 LLM 使用"""
        # 从角色状态获取历史
        state = self.role_manager.get_current_state()
        
        messages = []
        if state:
            # 添加之前的对话历史
            for msg in state.conversation_history[-6:]:  # 只保留最近 3 轮对话
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": new_message,
            "interviewer_id": interviewer_id
        })
        
        return messages
    
    # ========================
    # 核心方法 2: 评估候选人
    # ========================
    
    async def evaluate_candidate(
        self,
        candidate_id: str,
        interviewer_id: str,
        candidate_response: str,
        question: str,
        round_num: int
    ) -> Dict[str, Any]:
        """
        后台评估候选人（不阻塞对话流）
        
        参数:
            candidate_id: 候选人ID
            interviewer_id: 面试官ID
            candidate_response: 候选人的回答
            question: 提出的问题
            round_num: 轮次
        
        返回:
            评估结果
        """
        
        logger.info(
            f"Evaluating candidate {candidate_id} "
            f"by {interviewer_id} in round {round_num}"
        )
        
        # 获取面试官配置
        role_config = self.role_manager.get_role(interviewer_id)
        if not role_config:
            return {"error": f"面试官不存在: {interviewer_id}"}
        
        # 调用 LLM 进行评估
        evaluation_prompt = self._build_evaluation_prompt(
            question,
            candidate_response,
            role_config.evaluation_focus,
            round_num
        )
        
        # 模拟评估调用（真实情况下调用专门的评估 LLM）
        evaluation_result = await self._get_llm_evaluation(
            evaluation_prompt
        )
        
        # 更新角色状态中的评分
        state = self.role_manager.get_current_state()
        if state:
            # 更新多个维度的评分
            for dimension, score in evaluation_result.get("scores", {}).items():
                try:
                    state.update_score(dimension, score)
                except ValueError as e:
                    logger.warning(f"无法更新评分: {e}")
        
        return evaluation_result
    
    def _build_evaluation_prompt(
        self,
        question: str,
        response: str,
        evaluation_focus: Dict[str, float],
        round_num: int
    ) -> str:
        """构建评估提示词"""
        
        dimensions = ", ".join(evaluation_focus.keys())
        
        prompt = f"""
请作为一位资深的招聘评估专家，根据以下信息进行多维度评估：

问题：{question}

候选人回答：{response}

评估维度：{dimensions}

请为每个维度提供：
1. 评分（0-10 分）
2. 评估理由（1-2 句）

请返回 JSON 格式的评估结果：
{{
    "scores": {{
        "dimension1": score,
        "dimension2": score
    }},
    "reasoning": "总体评估理由"
}}

轮次: {round_num + 1}
"""
        return prompt
    
    async def _get_llm_evaluation(
        self,
        evaluation_prompt: str
    ) -> Dict[str, Any]:
        """调用 LLM 进行评估"""
        
        # TODO: 调用真实的 LLM 进行评估
        # 这里是示例实现
        
        await asyncio.sleep(0.2)  # 模拟 API 调用
        
        # 示例评估结果
        return {
            "scores": {
                "communication_skills": 8.0,
                "problem_solving": 7.5,
                "teamwork": 8.5
            },
            "reasoning": "候选人的回答思路清晰，具有良好的沟通能力。"
        }
    
    # ========================
    # 双轨并行处理
    # ========================
    
    async def chat_and_evaluate_parallel(
        self,
        interviewer_id: str,
        candidate_id: str,
        candidate_message: str,
        round_num: int,
        system_prompt: Optional[str] = None
    ):
        """
        双轨并行处理：
        - 任务 A：流式返回 LLM 聊天结果
        - 任务 B：后台评估候选人（不阻塞 A）
        
        这是生成器，应该在 FastAPI 的 StreamingResponse 中使用
        """
        
        # 创建用于获取评估结果的队列
        evaluation_queue = asyncio.Queue()
        
        # 任务 A：聊天流
        async def task_a():
            """流式返回对话"""
            async for chunk in self.chat_with_llm(
                interviewer_id, 
                candidate_message,
                round_num,
                system_prompt
            ):
                yield chunk
            yield "\n[CHAT_COMPLETED]"
        
        # 任务 B：后台评估（不阻塞任务 A）
        async def task_b():
            """后台评估任务"""
            try:
                # 这里假设从对话中提取了问题（实际应更复杂）
                question = "请介绍一下你自己"  # 示例
                
                result = await self.evaluate_candidate(
                    candidate_id=candidate_id,
                    interviewer_id=interviewer_id,
                    candidate_response=candidate_message,
                    question=question,
                    round_num=round_num
                )
                
                await evaluation_queue.put(result)
                logger.info(f"评估完成: {result}")
            except Exception as e:
                logger.error(f"评估出错: {e}")
                await evaluation_queue.put({"error": str(e)})
        
        # 并行运行两个任务
        task_b_coroutine = asyncio.create_task(task_b())
        
        # 流式返回任务 A 的结果
        async for chunk in task_a():
            yield chunk
            # 每次 yield 后检查是否有评估完成
            # （这允许前端持续接收数据，同时后台任务继续运行）
        
        # 等待任务 B 完成（但不阻塞前端）
        evaluation_result = None
        try:
            # 等待最多 30 秒的评估结果
            evaluation_result = await asyncio.wait_for(
                evaluation_queue.get(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            evaluation_result = {"warning": "评估超时"}
        
        # 在流结束时，发送评估结果
        yield f"\n[EVALUATION_COMPLETED]:{json.dumps(evaluation_result)}"
    
    # ========================
    # 角色和会话管理
    # ========================
    
    def switch_interviewer(
        self,
        interviewer_id: str,
        candidate_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """切换面试官"""
        
        try:
            # 切换角色
            state = self.role_manager.switch_to_role(interviewer_id)
            
            # 获取 System Prompt
            system_prompt = self.role_manager.get_system_prompt(
                interviewer_id,
                state.current_round
            )
            
            # 更新会话状态
            if session_id not in self.session_states:
                self.session_states[session_id] = {}
            
            self.session_states[session_id].update({
                "current_interviewer_id": interviewer_id,
                "last_switched": datetime.now().isoformat()
            })
            
            role_config = self.role_manager.get_role(interviewer_id)
            
            return {
                "status": "success",
                "interviewer_name": role_config.role_name,
                "system_prompt": system_prompt,
                "role_config": {
                    "role_id": role_config.role_id,
                    "tone": role_config.tone,
                    "focus_areas": role_config.focus_areas
                }
            }
        except Exception as e:
            logger.error(f"切换面试官失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        return self.session_states.get(session_id)
    
    def create_session(self, candidate_id: str, initial_interviewer_id: str) -> str:
        """创建新会话"""
        from uuid import uuid4
        
        session_id = str(uuid4())
        self.switch_interviewer(initial_interviewer_id, candidate_id, session_id)
        
        return session_id
    
    def get_all_available_interviewers(self) -> List[Dict[str, Any]]:
        """获取所有可用的面试官"""
        interviewers = []
        for role_id, role_config in self.role_manager.get_all_roles().items():
            interviewers.append({
                "role_id": role_id,
                "role_name": role_config.role_name,
                "role_type": role_config.role_type.value,
                "tone": role_config.tone,
                "focus_areas": role_config.focus_areas,
                "role_description": role_config.role_description
            })
        return interviewers


# 全局服务实例
_service_instance: Optional[InterviewerService] = None


def get_interviewer_service() -> InterviewerService:
    """获取面试官服务单例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = InterviewerService()
    return _service_instance
