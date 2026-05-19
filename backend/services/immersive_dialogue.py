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
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.assessment import AssessmentRecord, AssessmentStatus
from models.conversation import ConversationTurn, Speaker
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

logger = logging.getLogger(__name__)


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
ROLE_CONFIG_BY_ID = {role.value: config for role, config in ROLE_CONFIG.items()}


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
            actual_role_id = result.get("role_id") or role_id
            if actual_role_id != role_id:
                try:
                    current_role = RoleType(actual_role_id)
                    role_config = ROLE_CONFIG.get(current_role, role_config)
                    role_id = actual_role_id
                except ValueError:
                    actual_role_id = role_id
            interview_state.current_role = actual_role_id

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
                "current_role": actual_role_id,
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

            # 提取上一个问题
            last_question = ""
            last_question_info = {}
            for msg in reversed(conversation_history or []):
                if msg.get("role") != "candidate" and msg.get("scoreable", True) is not False:
                    last_question = self._extract_question_text(msg)
                    question_meta = self._extract_question_metadata(msg)
                    last_question_info = {
                        "focus_area": question_meta.get("focus_area", interview_state.current_focus_skill or "综合"),
                        "question": last_question,
                        "tags": question_meta.get("tags", []),
                        "expected_traits": question_meta.get("expected_traits", []),
                        "role_id": question_meta.get("role_id", current_speaker.value),
                    }
                    break
            question_tags = last_question_info.get("tags", [])
            expected_traits = last_question_info.get("expected_traits", [])
            question_role_id = last_question_info.get("role_id") or current_speaker.value
            if question_role_id in ROLE_CONFIG_BY_ID:
                interview_state.current_role = question_role_id
            state_context = interview_state.to_context_dict()

            # ===== Step 1: EvaluatorAgent 评估（含技能差距识别）=====
            eval_result = await self.evaluator_agent.evaluate(
                candidate_response=candidate_response,
                last_question=last_question,
                role_id=question_role_id,
                job_info=job_info,
                resume_info=resume_info,
                conversation_history=conversation_history,
                depth=conversation_depth,
                interview_state_context=state_context,
                question_tags=question_tags,
                expected_traits=expected_traits,
            )
            if self._is_low_information_response(candidate_response):
                eval_result["feedback"] = "谢谢你的补充。这个回答信息较少，我会换一个更具体、容易展开的岗位情境。"
                eval_result["depth_assessment"] = {
                    "answer_depth": "shallow",
                    "specificity": "vague",
                    "confidence_indicator": "uncertain",
                }

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
                max_questions=8,
                allow_llm=False,
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
            else:
                role_id = decision.get("suggested_role", current_speaker.value)
                next_question = await self._generate_agent_next_question_after_decision(
                    role_id=role_id,
                    evaluation_result=eval_result,
                    decision=decision,
                    interview_state=interview_state,
                    job_info=job_info,
                    resume_info=resume_info,
                    conversation_history=conversation_history,
                    candidate_response=candidate_response,
                    last_question=last_question,
                    conversation_depth=conversation_depth + 1,
                )
                result["next_question"] = next_question

            return result
            
        except Exception as e:
            print(f"分析回答失败: {e}")
            return self._get_fallback_analysis()

    async def _generate_agent_next_question_after_decision(
        self,
        *,
        role_id: str,
        evaluation_result: Dict[str, Any],
        decision: Dict[str, Any],
        interview_state,
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        candidate_response: str,
        last_question: str,
        conversation_depth: int,
    ) -> Dict[str, Any]:
        """Generate the next question with InterviewerAgent after DecisionAgent routing."""
        try:
            interview_state.current_role = role_id
            directive = dict(decision.get("directive", {}) or {})
            directive.setdefault("action", decision.get("action", "continue"))
            directive.setdefault("reasoning", decision.get("reasoning", ""))
            directive.setdefault("priority_gaps", decision.get("priority_gaps", []))

            enriched_history = list(conversation_history or [])
            if candidate_response:
                enriched_history.append({
                    "role": "candidate",
                    "content": candidate_response,
                })

            next_question = await self.interviewer_agent.generate_question(
                role_id=role_id,
                job_info=job_info,
                resume_info=resume_info,
                conversation_history=enriched_history,
                depth=conversation_depth,
                round_number=interview_state.total_questions + 1,
                total_rounds=8,
                decision_directive=directive,
                interview_state_context=interview_state.to_context_dict(),
            )
            actual_role_id = next_question.get("role_id") or role_id
            if actual_role_id != role_id and actual_role_id in ROLE_CONFIG_BY_ID:
                role_id = actual_role_id
            interview_state.current_role = role_id

            focus_area = next_question.get("focus_area") or ""
            if focus_area:
                interview_state.current_focus_skill = focus_area

            try:
                role = RoleType(role_id)
            except ValueError:
                role = RoleType.HR

            next_question["suggestions"] = await self._generate_smart_suggestions(
                question=next_question.get("question"),
                role=role,
                conversation_depth=conversation_depth,
            )
            next_question["interview_state"] = {
                "difficulty_level": interview_state.difficulty_level.value,
                "performance_trend": interview_state.performance_trend.value,
                "total_questions": interview_state.total_questions,
                "coverage": interview_state.get_coverage_summary(),
                "current_role": role_id,
                "decision_action": decision.get("action", "continue"),
                "decision_reasoning": decision.get("reasoning", ""),
                "personality_coverage_rate": interview_state.get_personality_coverage_rate(),
                "missing_personality_traits": interview_state.get_missing_personality_traits(),
            }
            return next_question
        except Exception as e:
            logger.warning(
                "InterviewerAgent 下一题生成失败，回退到规则修正: type=%s str=%s",
                type(e).__name__,
                str(e),
                exc_info=True,
            )
            return self._build_fast_next_question(
                evaluation_result=evaluation_result,
                decision=decision,
                role_id=role_id,
                interview_state=interview_state,
                job_info=job_info,
                resume_info=resume_info,
                candidate_response=candidate_response,
                last_question=last_question,
                conversation_depth=conversation_depth,
            )

    def _build_fast_next_question(
        self,
        *,
        evaluation_result: Dict[str, Any],
        decision: Dict[str, Any],
        role_id: str,
        interview_state,
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        candidate_response: str,
        last_question: str,
        conversation_depth: int,
    ) -> Dict[str, Any]:
        """Build next question without an extra LLM call for real-time interview."""
        directive = decision.get("directive", {}) or {}
        action = decision.get("action", "continue")
        resume_anchor = self._pick_resume_anchor(resume_info)
        job_anchor = self._pick_job_anchor(job_info)
        answer_anchor = self._extract_answer_anchor(candidate_response)
        role_meta = {
            "hr": {"phase": "opening", "traits": ["沟通能力", "团队协作", "文化契合"]},
            "tech_lead": {"phase": "technical", "traits": ["技术深度", "问题解决", "系统思维"]},
            "product": {"phase": "product_thinking", "traits": ["产品思维", "用户洞察", "创新能力"]},
            "cto": {"phase": "strategic", "traits": ["战略思维", "领导力", "决策能力"]},
        }.get(role_id, {"phase": "multi_perspective", "traits": ["综合能力"]})

        question_draft = evaluation_result.get("suggested_next_question") or {}
        focus_area = question_draft.get("focus_area") or role_meta["traits"][0]
        question = question_draft.get("question") or ""
        tags = question_draft.get("tags") if isinstance(question_draft.get("tags"), list) else []
        context = question_draft.get("context") or question_draft.get("intent") or ""
        difficulty = question_draft.get("difficulty") or "medium"

        if action == "switch_topic":
            topic = directive.get("new_topic") or focus_area
            focus_area = topic
            if "低信息" in str(directive.get("reason", "")) or topic == "销售场景适应性":
                question = self._build_low_info_sales_question(job_anchor)
            elif not question:
                question = self._build_integrated_question(
                    anchor=job_anchor,
                    resume_anchor=answer_anchor or resume_anchor,
                    trait=topic,
                )
            tags = list(dict.fromkeys((tags or []) + ["心理特质评估", topic, "行为情境"]))
            context = directive.get("hint", "补齐 Scenario Personality 证据")
            difficulty = "medium"
        elif action == "fill_gap":
            targets = directive.get("target_skills") or []
            target = targets[0] if targets else job_anchor
            focus_area = str(target)
            question = self._build_integrated_question(
                anchor=str(target),
                resume_anchor=resume_anchor,
                trait=interview_state.get_missing_personality_traits()[0] if interview_state.get_missing_personality_traits() else "尽责性",
            )
            tags = ["技能匹配", "心理特质评估", str(target)]
            context = directive.get("hint", "通过岗位技能情境同时补齐技能匹配与 Scenario Personality 证据")
        elif action == "switch_role":
            question = question or "接下来换一个视角。请描述一次你在跨角色协作中推动问题解决的经历，你如何平衡技术、业务和团队诉求？"
            tags = tags or ["多Agent面试", "综合潜力"]
            context = directive.get("hint", context)

        if not question:
            question = "请结合一个具体经历，说明你在岗位相关情境下如何做出判断、采取行动并复盘结果。"
            tags = tags or ["行为情境", "心理特质评估"]

        validation = self._validate_question_draft(
            question=question,
            focus_area=focus_area,
            tags=tags,
            action=action,
            conversation_depth=conversation_depth,
            last_question=last_question,
            answer_anchor=answer_anchor,
        )
        if not validation["valid"]:
            fallback = self._repair_question_draft(
                focus_area=focus_area,
                action=action,
                directive=directive,
                job_info=job_info,
                resume_info=resume_info,
                answer_anchor=answer_anchor,
                missing_traits=interview_state.get_missing_personality_traits(),
                reason=validation["reason"],
            )
            question = fallback["question"]
            tags = fallback["tags"]
            context = fallback["context"]
            focus_area = fallback["focus_area"]
            difficulty = fallback["difficulty"]

        interview_state.current_focus_skill = focus_area
        expected_traits = self._extract_expected_traits_from_tags(tags, focus_area)
        return {
            "question": question,
            "intent": question_draft.get("intent", context or "补充评估证据"),
            "difficulty": difficulty,
            "resume_anchor": "",
            "tags": tags,
            "focus_area": focus_area,
            "context": context,
            "expected_traits": expected_traits,
            "role_id": role_id,
            "phase": role_meta["phase"],
            "interview_state": {
                "difficulty_level": interview_state.difficulty_level.value,
                "performance_trend": interview_state.performance_trend.value,
                "total_questions": interview_state.total_questions,
                "coverage": interview_state.get_coverage_summary(),
                "current_role": role_id,
                "decision_action": decision.get("action", "continue"),
                "personality_coverage_rate": interview_state.get_personality_coverage_rate(),
                "missing_personality_traits": interview_state.get_missing_personality_traits(),
            },
        }

    def _validate_question_draft(
        self,
        *,
        question: str,
        focus_area: str,
        tags: List[str],
        action: str,
        conversation_depth: int,
        last_question: str = "",
        answer_anchor: str = "",
    ) -> Dict[str, Any]:
        """Validate LLM next-question draft without another model call."""
        text = (question or "").strip()
        if len(text) < 12:
            return {"valid": False, "reason": "问题过短，无法形成有效评估"}
        if len(text) > 180:
            return {"valid": False, "reason": "问题过长，候选人负担较高"}
        question_marks = text.count("？") + text.count("?")
        if question_marks > 1 or any(marker in text for marker in ["；你还会", "，以及你", "同时请"]):
            return {"valid": False, "reason": "一次包含多个问题"}
        if self._is_same_question(text, last_question):
            return {"valid": False, "reason": "问题与上一题重复"}
        banned = ["工资", "婚育", "宗教", "政治", "籍贯", "家庭情况", "星座"]
        if any(word in text for word in banned):
            return {"valid": False, "reason": "包含不适合面试评估的个人信息"}
        generic_starters = [
            "请结合一个具体经历",
            "请描述一次",
            "能否分享一次",
        ]
        if conversation_depth >= 2 and answer_anchor and any(text.startswith(s) for s in generic_starters):
            if "你刚才提到" not in text and answer_anchor[:8] not in text:
                return {"valid": False, "reason": "问题没有承接候选人上一回答"}
        if action == "switch_topic":
            personality_markers = ["经历", "情境", "压力", "分歧", "协作", "学习", "风险", "复盘", "判断"]
            if not any(word in text for word in personality_markers):
                return {"valid": False, "reason": "切换心理特质时未形成行为情境题"}
        if conversation_depth >= 2:
            trait_markers = ["经历", "情境", "压力", "分歧", "协作", "学习", "风险", "质量", "复盘", "判断", "取舍", "沟通", "推进"]
            has_trait_tag = "心理特质评估" in tags or "行为情境" in tags
            if not has_trait_tag and not any(word in text for word in trait_markers):
                return {"valid": False, "reason": "多轮评估后问题缺少心理特质观察点"}
        return {"valid": True, "reason": "ok"}

    def _is_low_information_response(self, text: str) -> bool:
        normalized = (text or "").strip().lower()
        if not normalized:
            return True
        short_low_info = {"无", "没有", "没", "不会", "不知道", "不清楚", "不了", "哦", "嗯", "ok", "no"}
        return normalized in short_low_info or len(normalized) <= 3

    def _is_same_question(self, question: str, last_question: str) -> bool:
        def normalize(text: str) -> str:
            for ch in [" ", "\n", "\t", "？", "?", "。", "，", ",", "；", ";", "：", ":"]:
                text = text.replace(ch, "")
            return text.strip()

        current = normalize(question)
        previous = normalize(last_question or "")
        if not current or not previous:
            return False
        return current == previous or current in previous or previous in current

    def _build_low_info_sales_question(self, job_anchor: str) -> str:
        return (
            f"没关系，我们换一个更具体的销售场景。假设你要向一位第一次接触产品的客户介绍{job_anchor}，"
            "但对方一开始兴趣不高，你会先问什么问题来了解需求，并如何继续沟通？"
        )

    def _repair_question_draft(
        self,
        *,
        focus_area: str,
        action: str,
        directive: Dict[str, Any],
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        answer_anchor: str,
        missing_traits: List[str],
        reason: str,
    ) -> Dict[str, Any]:
        topic = directive.get("new_topic") or focus_area or "综合心理特质"
        resume_anchor = self._pick_resume_anchor(resume_info)
        if answer_anchor:
            resume_anchor = answer_anchor
        job_anchor = self._pick_job_anchor(job_info)
        templates = {
            "开放性": "请描述一次你需要快速学习新技术或适应新方案的经历。你如何判断学习重点，并把它应用到项目中？",
            "尽责性": "请描述一次你为了保证交付质量主动发现并处理风险的经历。你做了哪些具体动作，最后结果如何？",
            "外向性": "请描述一次你主动发起沟通、推动他人达成一致的经历。你当时如何表达自己的观点？",
            "宜人性": "请描述一次你和团队成员出现分歧的经历。你如何理解对方立场，并推动问题解决？",
            "情绪稳定性": "请描述一次线上问题、延期或多方催促带来压力的经历。你当时如何安排优先级并稳定推进？",
            "压力应对": "请描述一次高压情境下处理复杂问题的经历。你如何控制节奏、同步信息并复盘结果？",
        }
        question = templates.get(topic)
        if question and answer_anchor:
            question = f"你刚才提到“{answer_anchor}”。在这个基础上，{question}"
        if not question:
            if action == "fill_gap":
                targets = directive.get("target_skills") or []
                target = targets[0] if targets else job_anchor
                topic = str(target)
                question = self._build_integrated_question(
                    anchor=topic,
                    resume_anchor=answer_anchor or resume_anchor,
                    trait=missing_traits[0] if missing_traits else "尽责性",
                )
                tags = ["技能匹配", "心理特质评估", topic]
            else:
                question = self._build_integrated_question(
                    anchor=job_anchor,
                    resume_anchor=answer_anchor or resume_anchor,
                    trait=missing_traits[0] if missing_traits else "综合心理特质",
                )
                tags = ["行为情境", "心理特质评估", job_anchor]
        else:
            tags = ["心理特质评估", topic, "行为情境"]
        return {
            "question": question,
            "focus_area": topic,
            "tags": tags,
            "context": "请结合真实经历，重点说明你的判断过程和行动结果。",
            "debug_context": f"问题草案已规则修正：{reason}",
            "difficulty": "medium",
        }

    def _pick_resume_anchor(self, resume_info: Dict[str, Any]) -> str:
        skills = resume_info.get("skills") or []
        if isinstance(skills, list) and skills:
            return str(skills[0])
        if isinstance(skills, str) and skills.strip():
            return skills.split(",")[0].split("，")[0].strip()
        projects = resume_info.get("projects") or resume_info.get("experience_summary")
        if projects:
            return str(projects)[:30]
        return "简历中的相关经历"

    def _pick_job_anchor(self, job_info: Dict[str, Any]) -> str:
        skills = job_info.get("required_skills") or job_info.get("skills") or []
        if isinstance(skills, list) and skills:
            return str(skills[0]).split("(")[0]
        if isinstance(skills, str) and skills.strip():
            return skills.split(",")[0].split("，")[0].strip()
        return str(job_info.get("title") or job_info.get("name") or "岗位核心能力")

    def _extract_answer_anchor(self, candidate_response: str) -> str:
        text = (candidate_response or "").strip()
        if not text:
            return ""
        separators = ["。", "\n", "；", ";"]
        chunks = [text]
        for sep in separators:
            next_chunks = []
            for chunk in chunks:
                next_chunks.extend(part.strip() for part in chunk.split(sep) if part.strip())
            chunks = next_chunks
        keywords = ["结果", "判断", "行动", "团队", "压力", "方案", "数据", "客户", "推广", "沟通", "复盘"]
        for chunk in chunks:
            if any(word in chunk for word in keywords) and 8 <= len(chunk) <= 45:
                return chunk
        for chunk in chunks:
            if 8 <= len(chunk) <= 45:
                return chunk
        return text[:40]

    def _build_integrated_question(self, *, anchor: str, resume_anchor: str, trait: str) -> str:
        trait_prompts = {
            "开放性": "你如何学习、迁移并验证新方案",
            "尽责性": "你如何识别风险、保证质量并完成交付",
            "外向性": "你如何主动沟通并推动他人形成共识",
            "宜人性": "你如何处理分歧、理解对方并推进协作",
            "情绪稳定性": "你如何在压力下安排优先级并稳定推进",
        }
        trait_part = trait_prompts.get(trait, "你如何做出判断、采取行动并复盘结果")
        if resume_anchor and resume_anchor != "简历中的相关经历":
            return (
                f"你刚才提到“{resume_anchor}”。结合岗位要求里的{anchor}，"
                f"请进一步说明一个关键场景，重点谈谈{trait_part}？"
            )
        return (
            f"结合你简历中的{resume_anchor}经历，围绕岗位要求里的{anchor}，"
            f"请讲一个具体场景，重点说明{trait_part}？"
        )
    
    # ==================== 数据加载（简历 + 岗位） ====================

    def _load_job_info(self, job_id: int, existing: Dict[str, Any]) -> Dict[str, Any]:
        """从数据库加载岗位信息，合并到 existing dict"""
        try:
            from models.job import Job
            from models.job_requirement import JobRequirementTag, JobSkillRequirement, JobPersonalityFramework

            job = self.db.query(Job).filter(Job.id == int(job_id)).first()
            if job:
                existing.setdefault("title", job.name)
                existing.setdefault("name", job.name)
                existing.setdefault("description", job.description or "")
                existing.setdefault("company", job.company or "")
                existing.setdefault("category", job.category or "")
                if getattr(job, "personality_requirements", None):
                    existing.setdefault("personality_requirements", job.personality_requirements)
                if getattr(job, "required_traits", None):
                    existing.setdefault("required_traits", job.required_traits)

                # 加载技能需求
                skill_reqs = self.db.query(JobSkillRequirement).filter(
                    JobSkillRequirement.job_id == int(job_id)
                ).all()
                if skill_reqs:
                    existing.setdefault("required_skills", [
                        f"{s.skill_name}({'必需' if s.is_must_have else '加分'})"
                        for s in skill_reqs
                    ])

                requirement_tags = self.db.query(JobRequirementTag).filter(
                    JobRequirementTag.job_id == int(job_id)
                ).all()
                if requirement_tags:
                    existing.setdefault("requirement_tags", [
                        {
                            "capability_name": tag.capability_name,
                            "capability_category": tag.capability_category,
                            "importance_level": tag.importance_level,
                            "proficiency_required": tag.proficiency_required,
                            "personality_dimension": tag.personality_dimension,
                            "personality_min": tag.personality_min,
                            "personality_max": tag.personality_max,
                            "personality_weight": tag.personality_weight,
                        }
                        for tag in requirement_tags
                    ])

                framework = self.db.query(JobPersonalityFramework).filter(
                    JobPersonalityFramework.job_id == int(job_id)
                ).first()
                if framework:
                    existing.setdefault("personality_framework", {
                        "openness": {
                            "min": framework.openness_min,
                            "max": framework.openness_max,
                            "weight": framework.openness_weight,
                        },
                        "conscientiousness": {
                            "min": framework.conscientiousness_min,
                            "max": framework.conscientiousness_max,
                            "weight": framework.conscientiousness_weight,
                        },
                        "extraversion": {
                            "min": framework.extraversion_min,
                            "max": framework.extraversion_max,
                            "weight": framework.extraversion_weight,
                        },
                        "agreeableness": {
                            "min": framework.agreeableness_min,
                            "max": framework.agreeableness_max,
                            "weight": framework.agreeableness_weight,
                        },
                        "neuroticism": {
                            "min": framework.neuroticism_min,
                            "max": framework.neuroticism_max,
                            "weight": framework.neuroticism_weight,
                        },
                        "description": framework.description,
                    })

                personality_lines = []
                if existing.get("personality_requirements"):
                    personality_lines.append(f"岗位人格需求: {existing['personality_requirements']}")
                if existing.get("personality_framework"):
                    personality_lines.append(f"岗位大五人格框架: {existing['personality_framework']}")
                if existing.get("requirement_tags"):
                    high_tags = [
                        tag["capability_name"]
                        for tag in existing["requirement_tags"]
                        if tag.get("importance_level") == "high"
                    ][:5]
                    if high_tags:
                        personality_lines.append(f"高优先级岗位标签: {', '.join(high_tags)}")
                if personality_lines:
                    existing["description"] = "\n".join([
                        existing.get("description", ""),
                        *personality_lines,
                    ]).strip()
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

    def _extract_question_metadata(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """从前端历史消息中提取上一题元数据，兼容扁平字段和 data/metadata 包装。"""
        containers = [msg]
        for key in ("content", "message", "question"):
            raw = msg.get(key)
            if isinstance(raw, str) and raw.strip().startswith("{"):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        containers.append(parsed)
                except Exception:
                    pass
        if isinstance(msg.get("data"), dict):
            containers.append(msg["data"])
        if isinstance(msg.get("metadata"), dict):
            containers.append(msg["metadata"])

        metadata: Dict[str, Any] = {}
        for source in containers:
            for key in ("tags", "expected_traits"):
                if key in source and isinstance(source[key], list):
                    metadata[key] = [
                        str(item).strip()
                        for item in source[key]
                        if str(item or "").strip()
                    ]
            for key in ("focus_area", "role_id"):
                if source.get(key):
                    metadata[key] = str(source[key]).strip()

        if not metadata.get("role_id"):
            role = msg.get("agentRole") or msg.get("agent_role") or msg.get("speaker_role")
            if role:
                metadata["role_id"] = str(role).strip()
        return metadata

    def _extract_question_text(self, msg: Dict[str, Any]) -> str:
        """Extract question text, including JSON-string ConversationTurn.message."""
        for key in ("question", "content", "message"):
            raw = msg.get(key)
            if isinstance(raw, dict):
                text = str(raw.get("question") or raw.get("content") or "").strip()
                if text:
                    return text
            if isinstance(raw, str) and raw.strip():
                text = raw.strip()
                if text.startswith("{") or text.startswith("["):
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, dict):
                            return str(parsed.get("question") or parsed.get("content") or text).strip()
                    except Exception:
                        pass
                return text
        return ""

    def _extract_expected_traits_from_tags(self, tags: List[str], focus_area: str) -> List[str]:
        big_five_traits = {"开放性", "尽责性", "外向性", "宜人性", "情绪稳定性", "神经质"}
        traits = [
            str(tag).strip()
            for tag in (tags or [])
            if str(tag).strip() in big_five_traits
        ]
        if focus_area in big_five_traits and focus_area not in traits:
            traits.insert(0, focus_area)
        return traits or ([focus_area] if focus_area in big_five_traits else [])
    
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
            score_coverage = kwargs.get("score_coverage") if isinstance(kwargs.get("score_coverage"), dict) else {}
            observed_scores = self._filter_observed_scores(scores, score_coverage)

            # 计算总体评分
            average_score = sum(observed_scores.values()) / len(observed_scores) if observed_scores else 0
            overall_score = average_score * 10 if average_score <= 10 else average_score
            
            summary_parts = []
            if highlights:
                summary_parts.append("\n".join(highlights))
            summary_parts.append(f"完成{total_rounds}轮沉浸式多Agent面试")
            if patterns:
                summary_parts.append(f"识别行为模式{len(patterns)}项")

            roles_participated = sorted({
                str(
                    self._extract_question_metadata(message).get("role_id")
                    or message.get("agentRole")
                    or message.get("agent_role")
                    or message.get("role")
                )
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
                    "scores": observed_scores,
                    "score_coverage": score_coverage,
                    "patterns": patterns,
                    "message_count": len(messages),
                },
                ensure_ascii=False,
            )
            assessment.match_score = overall_score
            assessment.updated_at = datetime.utcnow()
            self._persist_conversation_turns(assessment.id, messages)
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

    def _filter_observed_scores(
        self,
        scores: Dict[str, float],
        score_coverage: Dict[str, Any],
    ) -> Dict[str, float]:
        if not score_coverage:
            return {
                str(key): float(value)
                for key, value in (scores or {}).items()
                if value is not None
            }
        observed = {
            str(key)
            for key, status in score_coverage.items()
            if status == "observed"
        }
        return {
            str(key): float(value)
            for key, value in (scores or {}).items()
            if key in observed and value is not None
        }

    def _persist_conversation_turns(
        self,
        assessment_id: int,
        messages: List[Dict[str, Any]],
    ) -> None:
        """保存对话回合；面试官问题元数据以 JSON 形式随 message 保留，避免新增表结构。"""
        if not messages:
            return
        self.db.query(ConversationTurn).filter(
            ConversationTurn.assessment_id == assessment_id
        ).delete(synchronize_session=False)

        for index, message in enumerate(messages, start=1):
            role = str(message.get("role") or "").strip()
            speaker = Speaker.CANDIDATE if role == "candidate" else Speaker.INTERVIEWER
            text = (
                message.get("content")
                or message.get("question")
                or message.get("message")
                or ""
            )
            metadata = self._extract_question_metadata(message) if speaker == Speaker.INTERVIEWER else {}
            stored_message = str(text)
            if metadata:
                stored_message = json.dumps(
                    {
                        "content": stored_message,
                        "role_id": metadata.get("role_id"),
                        "tags": metadata.get("tags", []),
                        "expected_traits": metadata.get("expected_traits", []),
                        "focus_area": metadata.get("focus_area"),
                        "scoreable": message.get("scoreable", True) is not False,
                    },
                    ensure_ascii=False,
                )

            self.db.add(ConversationTurn(
                assessment_id=assessment_id,
                round_num=int(message.get("round") or message.get("round_num") or index),
                turn_num=int(message.get("turn") or message.get("turn_num") or 1),
                speaker=speaker,
                message=stored_message,
                message_length=len(str(text)),
            ))
