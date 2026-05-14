"""
沉浸式对话服务 - LLM 集成核心
支持多角色对话、特质评估、岗位匹配
"""

# ⚠️ 在导入任何依赖库前设置环境变量，确保本地OCR模型
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
OCR_CACHE_DIR = BACKEND_DIR / ".ocr_cache"
PADDLEX_CACHE_DIR = OCR_CACHE_DIR / "paddlex"
PADDLEOCR_HOME_DIR = OCR_CACHE_DIR / "paddleocr"
PADDLEOCR_MODEL_DIR = PADDLEOCR_HOME_DIR / "models"

for cache_dir in (PADDLEX_CACHE_DIR, PADDLEOCR_HOME_DIR, PADDLEOCR_MODEL_DIR):
    cache_dir.mkdir(parents=True, exist_ok=True)

os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = '1'
os.environ['PADDLEOCR_USE_LAUNCH'] = '0'
os.environ['PADDLE_PDX_CACHE_HOME'] = str(PADDLEX_CACHE_DIR)
os.environ['PADDLE_OCR_LOCAL_MODEL_PATH'] = str(PADDLEOCR_MODEL_DIR)
os.environ['PADDLEOCR_HOME'] = str(PADDLEOCR_HOME_DIR)
os.environ['PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT'] = 'False'
os.environ['PADDLE_PDX_DISABLE_MKLDNN_MODEL_BL'] = 'True'

from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import json
import asyncio

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.assessment import AssessmentRecord, AssessmentStatus
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
from services.agents.interviewer_agent import InterviewerAgent
from services.agents.evaluator_agent import EvaluatorAgent
from services.agents.decision_agent import DecisionAgent
from services.agents.interview_state import AdaptiveInterviewState


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
    """沉浸式对话服务主类 - 三 Agent 协同架构"""
    
    # 类级别的面试状态缓存（按 AssessmentSession 维度存储）
    _interview_states: Dict[str, AdaptiveInterviewState] = {}
    # 类级别的最新决策缓存
    _latest_decisions: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = LLMClient()
        self.trait_evaluator = TraitEvaluator()
        self.interviewer_agent = InterviewerAgent(self.llm_client)
        self.evaluator_agent = EvaluatorAgent(self.llm_client)
        self.decision_agent = DecisionAgent(self.llm_client)
        self.assessment_record = None

    def _build_session_key(
        self,
        candidate_id: str,
        assessment_id: Optional[int] = None,
        job_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """构建 AssessmentSession 级别的状态隔离键。"""
        if assessment_id:
            return f"assessment:{assessment_id}"

        job_id = (job_info or {}).get("id")
        if job_id:
            return f"candidate:{candidate_id}:job:{job_id}"

        job_title = (job_info or {}).get("title") or (job_info or {}).get("name")
        if job_title:
            return f"candidate:{candidate_id}:job_title:{job_title}"

        return f"candidate:{candidate_id}:ad_hoc"

    def _get_or_create_state(
        self,
        candidate_id: str,
        job_info: Optional[Dict[str, Any]] = None,
        assessment_id: Optional[int] = None,
    ) -> AdaptiveInterviewState:
        """获取或创建面试状态"""
        session_key = self._build_session_key(candidate_id, assessment_id, job_info)
        if session_key not in self._interview_states:
            state = AdaptiveInterviewState()
            # 初始化岗位需求技能
            if job_info:
                skills_raw = job_info.get("required_skills", job_info.get("skills", []))
                if isinstance(skills_raw, list):
                    # 去除括号内的标注如 "Python(必需)" → "Python"
                    clean_skills = []
                    for s in skills_raw:
                        name = s.split("(")[0].strip() if "(" in s else s.strip()
                        if name:
                            clean_skills.append(name)
                    state.init_required_skills(clean_skills)
            self._interview_states[session_key] = state
        return self._interview_states[session_key]
    
    # ==================== 核心对话流程 ====================
    
    async def generate_next_question(
        self,
        id: str,
        candidate_name: str,
        current_role: RoleType,
        conversation_history: List[Dict[str, str]],
        conversation_depth: int,
        target_position: Optional[str] = None,
        job_info: Optional[Dict[str, Any]] = None,
        resume_info: Optional[Dict[str, Any]] = None,
        assessment_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成下一个问题（三 Agent 协同模式）
        
        流程：
        1. 获取面试状态
        2. 获取 DecisionAgent 上一轮决策指令（如有）
        3. 将决策指令传递给 InterviewerAgent
        4. InterviewerAgent 生成自适应问题
        """
        try:
            role_config = ROLE_CONFIG.get(current_role)
            if not role_config:
                raise HTTPException(status_code=400, detail="无效的角色")
            
            # 补充信息
            if job_info is None:
                job_info = {}
            if not job_info.get("title") and target_position:
                job_info["title"] = target_position
            if resume_info is None:
                resume_info = {}
            if not resume_info.get("name") and candidate_name:
                resume_info["name"] = candidate_name

            # 加载数据库数据
            if not job_info.get("description") and job_info.get("id"):
                job_info = self._load_job_info(job_info["id"], job_info)
            if not resume_info.get("skills") and id:
                resume_info = self._load_resume_info(id, resume_info)

            # ===== 获取面试状态 =====
            session_key = self._build_session_key(id, assessment_id, job_info)
            interview_state = self._get_or_create_state(id, job_info, assessment_id)
            
            # 同步角色信息
            role_id = current_role.value
            # 如果 DecisionAgent 建议切换角色，使用建议角色
            latest_decision = self._latest_decisions.get(session_key, {})
            suggested_role = latest_decision.get("suggested_role")
            if suggested_role and suggested_role != role_id:
                try:
                    current_role = RoleType(suggested_role)
                    role_id = suggested_role
                    role_config = ROLE_CONFIG.get(current_role, role_config)
                except ValueError:
                    pass
            interview_state.current_role = role_id

            # ===== 获取决策指令 =====
            decision_directive = latest_decision.get("directive", {})
            state_context = interview_state.to_context_dict()

            # ===== 调用 InterviewerAgent（携带决策指令）=====
            result = await self.interviewer_agent.generate_question(
                role_id=role_id,
                job_info=job_info,
                resume_info=resume_info,
                conversation_history=conversation_history,
                depth=conversation_depth,
                round_number=len([m for m in conversation_history if m.get("role") != "candidate"]) + 1,
                total_rounds=12,
                decision_directive=decision_directive,
                interview_state_context=state_context,
            )
            
            # 更新当前关注技能
            focus_area = result.get("focus_area", "")
            if focus_area:
                interview_state.current_focus_skill = focus_area

            # 生成智能建议
            suggestions = await self._generate_smart_suggestions(
                question=result.get("question"),
                role=current_role,
                conversation_depth=conversation_depth
            )
            
            result["suggestions"] = suggestions
            # 附加面试状态信息给前端
            result["interview_state"] = {
                "difficulty_level": interview_state.difficulty_level.value,
                "performance_trend": interview_state.performance_trend.value,
                "total_questions": interview_state.total_questions,
                "coverage": interview_state.get_coverage_summary(),
                "current_role": role_id,
                "decision_action": latest_decision.get("action", "continue"),
            }
            return result
            
        except Exception as e:
            print(f"生成问题失败: {e}")
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
        job_info: Optional[Dict[str, Any]] = None,
        resume_info: Optional[Dict[str, Any]] = None,
        assessment_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        分析候选人回答（三 Agent 协同模式）
        
        流程：
        1. EvaluatorAgent 评估回答（含技能差距识别）
        2. 更新 AdaptiveInterviewState
        3. DecisionAgent 根据评估结果和状态做出决策
        4. 缓存决策，供下次 generate_next_question 使用
        """
        try:
            role_config = ROLE_CONFIG.get(current_speaker)
            if not role_config:
                raise HTTPException(status_code=400, detail="无效的角色")
            
            if job_info is None:
                job_info = {}
            if not job_info.get("title") and target_position:
                job_info["title"] = target_position
            if resume_info is None:
                resume_info = {}
            if not resume_info.get("name") and candidate_name:
                resume_info["name"] = candidate_name

            # 加载数据库数据
            if not job_info.get("description") and job_info.get("id"):
                job_info = self._load_job_info(job_info["id"], job_info)
            if not resume_info.get("skills") and id:
                resume_info = self._load_resume_info(id, resume_info)

            # ===== 获取面试状态 =====
            session_key = self._build_session_key(id, assessment_id, job_info)
            interview_state = self._get_or_create_state(id, job_info, assessment_id)
            state_context = interview_state.to_context_dict()

            # 提取上一个问题
            last_question = ""
            last_question_info = {}
            for msg in reversed(conversation_history or []):
                if msg.get("role") != "candidate":
                    last_question = msg.get("content", "")
                    last_question_info = {
                        "focus_area": msg.get("focus_area", interview_state.current_focus_skill or "综合"),
                    }
                    break

            # ===== Step 1: EvaluatorAgent 评估（含技能差距识别）=====
            eval_result = await self.evaluator_agent.evaluate(
                candidate_response=candidate_response,
                last_question=last_question,
                role_id=current_speaker.value,
                job_info=job_info,
                resume_info=resume_info,
                conversation_history=conversation_history,
                depth=conversation_depth,
                interview_state_context=state_context,
            )

            # ===== Step 2: 更新面试状态 =====
            interview_state.update_after_evaluation(
                evaluation_result=eval_result,
                question_info=last_question_info,
            )

            # ===== Step 3: DecisionAgent 做出下一步决策 =====
            decision = await self.decision_agent.decide(
                evaluation_result=eval_result,
                interview_state=interview_state,
                job_info=job_info,
                resume_info=resume_info,
                max_questions=12,
            )

            # ===== Step 4: 缓存决策供下轮使用 =====
            self._latest_decisions[session_key] = decision

            # 构建返回结果（保持向后兼容）
            result = eval_result.copy()
            result["decision"] = {
                "action": decision.get("action", "continue"),
                "reasoning": decision.get("reasoning", ""),
                "priority_gaps": decision.get("priority_gaps", []),
                "suggested_difficulty": decision.get("suggested_difficulty", 3),
                "suggested_role": decision.get("suggested_role", current_speaker.value),
                "should_end": decision.get("should_end", False),
            }
            result["interview_state"] = interview_state.to_context_dict()

            # 如果 DecisionAgent 建议结束，更新 next_action
            if decision.get("should_end"):
                result["next_action"] = "end_phase"

            return result
            
        except Exception as e:
            print(f"分析回答失败: {e}")
            return self._get_fallback_analysis()
    
    # ==================== 数据加载（简历 + 岗位） ====================

    def _load_job_info(self, job_id: int, existing: Dict[str, Any]) -> Dict[str, Any]:
        """从数据库加载岗位信息，合并到 existing dict"""
        try:
            from models.job import Job
            from models.job_requirement import JobSkillRequirement

            job = self.db.query(Job).filter(Job.id == int(job_id)).first()
            if job:
                existing.setdefault("title", job.name)
                existing.setdefault("name", job.name)
                existing.setdefault("description", job.description or "")
                existing.setdefault("company", job.company or "")
                existing.setdefault("category", job.category or "")

                # 加载技能需求
                skill_reqs = self.db.query(JobSkillRequirement).filter(
                    JobSkillRequirement.job_id == int(job_id)
                ).all()
                if skill_reqs:
                    existing.setdefault("required_skills", [
                        f"{s.skill_name}({'必需' if s.is_must_have else '加分'})"
                        for s in skill_reqs
                    ])
        except Exception as e:
            print(f"加载岗位信息失败: {e}")
        return existing

    def _load_resume_info(self, candidate_id: str, existing: Dict[str, Any]) -> Dict[str, Any]:
        """从数据库加载候选人简历信息，合并到 existing dict"""
        try:
            from models.user import User

            user = self.db.query(User).filter(User.id == int(candidate_id)).first()
            if user:
                existing.setdefault("name", user.real_name or user.username or "")
                existing.setdefault("email", user.email or "")
                existing.setdefault("education", user.education or "")
                existing.setdefault("major", user.major or "")
                existing.setdefault("experience_years", user.experience_years)
                existing.setdefault("desired_job", user.desired_job or "")
                if user.skills and not existing.get("skills"):
                    existing["skills"] = user.skills if isinstance(user.skills, list) else []
        except Exception as e:
            print(f"加载简历信息失败: {e}")
        return existing

    # ==================== LLM 调用逻辑（旧版保留兼容） ====================
    
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
        """生成智能建议（本地规则，无需 LLM 调用）"""
        if not question:
            return ["可以结合自身经历来回答", "尝试用STAR模型组织回答"]

        role_config = ROLE_CONFIG.get(role, ROLE_CONFIG[RoleType.HR])
        focus = role_config.get("focus_traits", ["综合能力"])[0]

        suggestions_pool = {
            "hr": [
                "先简要概括，再展开细节",
                "结合具体案例来说明",
                "可以提到团队合作的经历",
            ],
            "tech_lead": [
                "描述你的技术方案选择理由",
                "可以对比不同方案的优劣",
                "说明遇到的挑战和解决过程",
            ],
            "product": [
                "从用户需求出发进行分析",
                "可以列举具体的数据支持",
                "描述你的决策思考过程",
            ],
            "cto": [
                "从全局视角分析利弊",
                "可以谈谈长期规划和愿景",
                "结合行业趋势来阐述",
            ],
        }

        pool = suggestions_pool.get(role.value, suggestions_pool["hr"])
        # 根据深度偏移选择
        start = conversation_depth % len(pool)
        return pool[start:] + pool[:start]
    
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
        candidate_id: str,
        assessment_id: Optional[int],
        messages: List[Dict[str, str]],
        scores: Dict[str, float],
        patterns: List[Dict[str, Any]],
        duration_seconds: int,
        conversation_depth: int,
        total_rounds: int,
        highlights: List[str],
        job_id: Optional[int] = None,
        job_title: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """保存评估会话"""
        
        try:
            # 计算总体评分
            average_score = sum(scores.values()) / len(scores) if scores else 0
            overall_score = average_score * 10 if average_score <= 10 else average_score
            
            summary_parts = []
            if highlights:
                summary_parts.append("\n".join(highlights))
            summary_parts.append(f"完成{total_rounds}轮沉浸式多Agent面试")
            if patterns:
                summary_parts.append(f"识别行为模式{len(patterns)}项")

            roles_participated = sorted({
                str(message.get("role"))
                for message in messages
                if message.get("role") and message.get("role") != "candidate"
            })

            assessment = None
            if assessment_id:
                assessment = self.db.query(AssessmentRecord).filter(
                    AssessmentRecord.id == int(assessment_id)
                ).first()

            if assessment is None:
                if not job_id:
                    return {
                        "success": False,
                        "error": "缺少 job_id，无法创建新的 AssessmentSession",
                    }
                assessment = AssessmentRecord(
                    candidate_id=int(candidate_id),
                    job_id=int(job_id),
                    job_title=job_title or "未知岗位",
                    assessment_mode="immersive",
                    assessment_status=AssessmentStatus.PENDING,
                    created_at=datetime.utcnow(),
                )
                self.db.add(assessment)

            assessment.total_rounds = total_rounds
            assessment.duration_minutes = duration_seconds / 60 if duration_seconds else 0
            assessment.conversation_depth = conversation_depth
            assessment.roles_participated = roles_participated
            assessment.conversation_summary = "\n".join(summary_parts)
            assessment.overall_impression = json.dumps(
                {
                    "scores": scores,
                    "patterns": patterns,
                    "message_count": len(messages),
                },
                ensure_ascii=False,
            )
            assessment.match_score = overall_score
            assessment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(assessment)
            
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
