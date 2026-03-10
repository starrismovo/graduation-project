"""
沉浸式对话服务 - LLM 集成核心
支持多角色对话、特质评估、岗位匹配
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

from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import json
import asyncio

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.assessment import AssessmentRecord
from models.hr_agent import Scenario, InterviewResponse, TraitScore
from prompts.immersive_roles import (
    HR_SYSTEM_PROMPT,
    TECH_LEAD_SYSTEM_PROMPT,
    PRODUCT_SYSTEM_PROMPT,
    CTO_SYSTEM_PROMPT,
    ASSESSMENT_EVALUATOR_PROMPT
)
from utils.llm_client import LLMClient
from utils.trait_evaluator import TraitEvaluator


class AssessmentPhaseType(str, Enum):
    """评估阶段枚举"""
    OPENING = "opening"  # 破冰与背景
    TECHNICAL = "technical"  # 技术深度
    PRODUCT_THINKING = "product_thinking"  # 产品思维
    MULTI_PERSPECTIVE = "multi_perspective"  # 多方讨论
    STRATEGIC = "strategic"  # 战略层面


class RoleType(str, Enum):
    """角色枚举"""
    HR = "hr"
    TECH_LEAD = "tech_lead"
    PRODUCT = "product"
    CTO = "cto"


# 角色配置
ROLE_CONFIG = {
    RoleType.HR: {
        "name": "李明",
        "title": "HR 经理",
        "system_prompt": HR_SYSTEM_PROMPT,
        "focus_traits": ["沟通能力", "团队协作", "文化契合"],
        "conversation_depth": 2
    },
    RoleType.TECH_LEAD: {
        "name": "张伟",
        "title": "技术总监",
        "system_prompt": TECH_LEAD_SYSTEM_PROMPT,
        "focus_traits": ["技术深度", "问题解决", "系统思维"],
        "conversation_depth": 4
    },
    RoleType.PRODUCT: {
        "name": "王芳",
        "title": "产品经理",
        "system_prompt": PRODUCT_SYSTEM_PROMPT,
        "focus_traits": ["产品思维", "用户洞察", "创新能力"],
        "conversation_depth": 6
    },
    RoleType.CTO: {
        "name": "刘强",
        "title": "CTO",
        "system_prompt": CTO_SYSTEM_PROMPT,
        "focus_traits": ["战略思维", "领导力", "决策能力"],
        "conversation_depth": 10
    }
}


class ImmersiveDialogueService:
    """沉浸式对话服务主类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = LLMClient()
        self.trait_evaluator = TraitEvaluator()
        self.assessment_record = None
    
    # ==================== 核心对话流程 ====================
    
    async def generate_next_question(
        self,
        id: str,
        candidate_name: str,
        current_role: RoleType,
        conversation_history: List[Dict[str, str]],
        conversation_depth: int,
        target_position: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成下一个问题
        
        Args:
            id: 候选人ID
            candidate_name: 候选人名字
            current_role: 当前提问角色
            conversation_history: 对话历史
            conversation_depth: 对话深度（0-10）
            target_position: 目标岗位
            
        Return:
            {
                "question": "问题内容",
                "tags": ["标签1", "标签2"],
                "suggestions": ["建议1", "建议2"],
                "context": "建议文字",
                "focus_area": "重点评估区域",
                "expected_traits": ["特质1", "特质2"]
            }
        """
        try:
            role_config = ROLE_CONFIG.get(current_role)
            if not role_config:
                raise HTTPException(status_code=400, detail="无效的角色")
            
            # 1. 构建对话上下文
            context = self._build_conversation_context(
                id=id,
                candidate_name=candidate_name,
                conversation_history=conversation_history,
                conversation_depth=conversation_depth,
                target_position=target_position
            )
            
            # 2. 调用 LLM 生成问题
            system_prompt = role_config["system_prompt"]
            user_prompt = self._build_question_prompt(
                context=context,
                conversation_depth=conversation_depth,
                focus_traits=role_config["focus_traits"]
            )
            
            response = await self.llm_client.call_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            # 3. 解析 LLM 响应
            question_data = self._parse_llm_response(response.content)
            
            # 4. 生成智能建议
            suggestions = await self._generate_smart_suggestions(
                question=question_data.get("question"),
                role=current_role,
                conversation_depth=conversation_depth
            )
            
            return {
                "question": question_data.get("question", ""),
                "tags": question_data.get("tags", []),
                "suggestions": suggestions,
                "context": question_data.get("context"),
                "focus_area": question_data.get("focus_area"),
                "expected_traits": role_config["focus_traits"]
            }
            
        except Exception as e:
            print(f"生成问题失败: {e}")
            # 返回备用问题
            return self._get_fallback_question(current_role)
    
    async def analyze_candidate_response(
        self,
        id: str,
        candidate_name: str,
        current_speaker: RoleType,
        candidate_response: str,
        conversation_history: List[Dict[str, str]],
        conversation_depth: int,
        target_position: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        分析候选人回答
        
        Return:
            {
                "scores": {
                    "沟通能力": 7.5,
                    "问题解决": 8.0,
                    ...
                },
                "sentiment": {
                    "emotion": "自信",
                    "confidence": 85
                },
                "patterns": [
                    {
                        "name": "结构化思维",
                        "description": "回答...",
                        "confidence": 78,
                        "color": "#67c23a"
                    }
                ],
                "feedback": "实时反馈文字",
                "next_action": "continue|switch_role|end_phase"
            }
        """
        try:
            role_config = ROLE_CONFIG.get(current_speaker)
            if not role_config:
                raise HTTPException(status_code=400, detail="无效的角色")
            
            # 1. 调用 LLM 评估回答
            evaluation = await self._evaluate_response_with_llm(
                current_speaker=current_speaker,
                candidate_response=candidate_response,
                conversation_history=conversation_history,
                conversation_depth=conversation_depth,
                focus_traits=role_config["focus_traits"]
            )
            
            # 2. 提取特质评分
            scores = self.trait_evaluator.extract_scores(evaluation)
            
            # 3. 分析情绪与表达
            sentiment = await self._analyze_sentiment(candidate_response)
            
            # 4. 识别行为模式
            patterns = self.trait_evaluator.detect_patterns(
                response=candidate_response,
                evaluation=evaluation
            )
            
            # 5. 决定下一步行动
            next_action = self._determine_next_action(
                conversation_depth=conversation_depth,
                scores=scores
            )
            
            # 6. 生成实时反馈
            feedback = evaluation.get("feedback", "")
            
            return {
                "scores": scores,
                "sentiment": sentiment,
                "patterns": patterns,
                "feedback": feedback,
                "next_action": next_action,
                "raw_evaluation": evaluation  # 用于调试
            }
            
        except Exception as e:
            print(f"分析回答失败: {e}")
            # 返回默认评价
            return self._get_fallback_analysis()
    
    # ==================== LLM 调用逻辑 ====================
    
    def _build_conversation_context(
        self,
        id: str,
        candidate_name: str,
        conversation_history: List[Dict[str, str]],
        conversation_depth: int,
        target_position: Optional[str] = None
    ) -> str:
        """构建对话执行上下文"""
        
        history_text = "\n".join([
            f"{'角色' if msg['role'] != 'candidate' else '候选人'}: {msg['content']}"
            for msg in conversation_history[-5:]  # 只保留最近5条
        ])
        
        context = f"""
【候选人信息】
- 姓名: {candidate_name}
- ID: {id}
- 目标岗位: {target_position or '未指定'}
- 对话深度: {conversation_depth}/10

【最近对话历史】
{history_text if history_text else '(暂无历史记录)'}
"""
        return context
    
    def _build_question_prompt(
        self,
        context: str,
        conversation_depth: int,
        focus_traits: List[str]
    ) -> str:
        """构建生成问题的用户提示"""
        
        return f"""
{context}

【任务】
作为评估者，请根据以上上下文，生成一个深具洞察力的追问。

【要求】
1. 根据对话深度（当前 {conversation_depth}/10）调整问题难度
2. 重点评估以下特质: {', '.join(focus_traits)}
3. 确保问题开放式，鼓励候选人深入思考
4. 避免重复之前问过的问题
5. 逐步提高问题复杂度

【输出格式】
请按以下 JSON 格式回复（仅返回 JSON，不要有其他文字）：
{{
    "question": "问题文本",
    "tags": ["重点1", "重点2"],
    "context": "为什么这个问题很重要的简短说明",
    "focus_area": "重点评估领域"
}}
"""
    
    async def _evaluate_response_with_llm(
        self,
        current_speaker: RoleType,
        candidate_response: str,
        conversation_history: List[Dict[str, str]],
        conversation_depth: int,
        focus_traits: List[str]
    ) -> Dict[str, Any]:
        """使用 LLM 评估候选人回答"""
        
        system_prompt = ASSESSMENT_EVALUATOR_PROMPT
        
        user_prompt = f"""
【评估任务】
请深入分析候选人的这个回答，评估其特质表现。

【候选人回答】
"{candidate_response}"

【重点评估特质】
{json.dumps(focus_traits, ensure_ascii=False, indent=2)}

【上下文信息】
- 当前提问角色: {ROLE_CONFIG[current_speaker]['name']}
- 对话深度: {conversation_depth}/10
- 提问次数: {len([m for m in conversation_history if m['role'] != 'candidate'])}

【评估维度】
1. 每个评估特质的评分（1-10）
2. 关键优势点（最多3个）
3. 改进方向（如果有）
4. 一句反馈（用于前端实时显示）

【输出格式】
{{
    "scores": {{
        "沟通能力": 8,
        "问题解决": 7.5,
        ...
    }},
    "strengths": ["优点1", "优点2", "优点3"],
    "improvements": ["改进方向1", "改进方向2"],
    "feedback": "简短的鼓励性反馈"
}}
"""
        
        response = await self.llm_client.call_async(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5,  # 降低温度，提高评估的一致性
            max_tokens=500
        )
        
        return self._parse_json_response(response.content)
    
    async def _generate_smart_suggestions(
        self,
        question: str,
        role: RoleType,
        conversation_depth: int
    ) -> List[str]:
        """生成智能建议"""
        
        prompt = f"""
基于以下问题，为候选人生成 2-3 个简短的建议或开场想法。
这些建议应该帮助候选人更好地理解问题并给出有质量的回答。

【问题】
{question}

【要求】
- 每条建议控制在 15-20 个字以内
- 建议应该是开放式的，启发而非应该
- 难度应该与对话深度 ({conversation_depth}/10) 匹配

只返回一个 JSON 数组，格式：["建议1", "建议2", "建议3"]
"""
        
        response = await self.llm_client.call_async(
            system_prompt="你是一个经验丰富的面试官，善于帮助候选人回答问题。",
            user_prompt=prompt,
            temperature=0.6,
            max_tokens=200
        )
        
        try:
            suggestions = json.loads(response.content)
            return suggestions if isinstance(suggestions, list) else []
        except:
            return []
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情绪"""
        
        prompt = f"""
分析以下文本的情绪和表达自信度。

【文本】
{text}

请返回 JSON 格式（仅 JSON）：
{{
    "emotion": "情绪类型 (自信|谨慎|激情|思考中|紧张)",
    "confidence": 「自信度百分比，0-100」
}}
"""
        
        response = await self.llm_client.call_async(
            system_prompt="你是一个专业的情绪分析师。",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        return self._parse_json_response(response.content)
    
    # ==================== 辅助方法 ====================
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """解析 LLM 响应（JSON 格式）"""
        try:
            # 找到 JSON 部分
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        return {}
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        try:
            start = content.find('{')
            if start >= 0:
                end = content.rfind('}') + 1
                return json.loads(content[start:end])
        except:
            pass
        try:
            start = content.find('[')
            if start >= 0:
                end = content.rfind(']') + 1
                return json.loads(content[start:end])
        except:
            pass
        return {}
    
    def _determine_next_action(
        self,
        conversation_depth: int,
        scores: Dict[str, float]
    ) -> str:
        """决定下一步行动"""
        if conversation_depth >= 10:
            return "end_phase"
        elif conversation_depth % 2 == 0 and conversation_depth > 0:
            return "switch_role"
        else:
            return "continue"
    
    def _get_fallback_question(self, role: RoleType) -> Dict[str, Any]:
        """获取备用问题"""
        fallback_questions = {
            RoleType.HR: {
                "question": "请简单介绍一下你自己及你的职业背景？",
                "tags": ["背景了解", "自我认知"],
                "suggestions": ["我叫...，毕业于...", "我有...年的工作经验"],
                "context": "这是一个开放性问题，轻松回答即可"
            },
            RoleType.TECH_LEAD: {
                "question": "请描述一个你最近解决的复杂技术问题？",
                "tags": ["问题解决", "技术深度"],
                "suggestions": ["我遇到了...", "我的解决方案是..."],
                "context": "尽量具体说明技术细节"
            },
            RoleType.PRODUCT: {
                "question": "如果让你设计一个新功能，你会如何思考整个过程？",
                "tags": ["产品思维"],
                "suggestions": ["首先理解用户需求", "然后分析市场"],
                "context": "展示你的产品思维框架"
            },
            RoleType.CTO: {
                "question": "你对未来 3-5 年的职业规划和目标是什么？",
                "tags": ["战略思维"],
                "suggestions": ["我的目标是...", "为此我计划..."],
                "context": "这是最后一道题，认真思考"
            }
        }
        return fallback_questions.get(role, fallback_questions[RoleType.HR])
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """获取备用分析"""
        return {
            "scores": {
                "沟通能力": 7.0,
                "问题解决": 7.0,
                "团队协作": 7.0,
                "创新能力": 7.0
            },
            "sentiment": {
                "emotion": "自信",
                "confidence": 70
            },
            "patterns": [],
            "feedback": "回答不错，继续保持",
            "next_action": "continue"
        }
    
    # ==================== 会话保存 ====================
    
    async def save_assessment_session(
        self,
        id: str,
        assessment_id: int,
        messages: List[Dict[str, str]],
        scores: Dict[str, float],
        patterns: List[Dict[str, Any]],
        duration_seconds: int,
        conversation_depth: int,
        total_rounds: int,
        highlights: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """保存评估会话"""
        
        try:
            # 计算总体评分
            overall_score = sum(scores.values()) / len(scores) if scores else 0
            
            # 创建评估记录
            assessment = AssessmentRecord(
                id=int(id),
                assessment_type="immersive_dialogue",
                session_data={
                    "messages": messages,
                    "conversation_depth": conversation_depth,
                    "total_rounds": total_rounds,
                    "duration_seconds": duration_seconds,
                    "patterns": patterns
                },
                scores=scores,
                overall_score=overall_score,
                summary="\n".join(highlights),
                created_at=datetime.utcnow()
            )
            
            self.db.add(assessment)
            self.db.commit()
            
            return {
                "success": True,
                "assessment_id": assessment.id,
                "session_id": f"session_{assessment.id}",
                "overall_score": overall_score
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"保存会话失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
