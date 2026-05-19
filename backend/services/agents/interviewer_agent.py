"""
InterviewerAgent - 面试官提问 Agent（自适应版）
================================================

职责：
  根据岗位要求 + 候选人简历 + 对话历史 + DecisionAgent指令，
  生成自适应面试问题。

  支持：
  - 简历驱动提问
  - 决策指令驱动（追问/填补差距/切换话题）
  - 难度自适应调整
  - 多轮上下文感知

输入：
  - job_info: 岗位名称、描述、核心技能要求
  - resume_info: 候选人姓名、教育、技能、经验、项目
  - conversation_history: 历史对话列表
  - role: 当前面试角色 (HR / 技术总监 / 产品经理 / CTO)
  - depth: 对话深度 (0-10)
  - decision_directive: DecisionAgent 的指令（追问/填补差距等）
  - interview_state_context: 自适应状态上下文

输出：
  {
    "question": "面试问题",
    "intent": "考察点",
    "difficulty": "easy/medium/hard",
    "resume_anchor": "关联的简历要点",
    "tags": [...],
    "focus_area": "评估重点"
  }
"""

import json
import logging
from typing import Optional, Dict, List, Any

from utils.llm_client import LLMClient
from prompts.agent_prompts import build_interviewer_prompt

logger = logging.getLogger(__name__)

BIG_FIVE_TRAITS = ["开放性", "尽责性", "外向性", "宜人性", "情绪稳定性"]


# 角色元信息映射
ROLE_META = {
    "hr": {
        "name": "李明",
        "title": "HR 经理",
        "experience": "15年",
        "specialty": "人才招聘与文化评估",
        "focus_traits": ["沟通能力", "团队协作", "文化契合"],
        "phase": "opening"
    },
    "tech_lead": {
        "name": "张伟",
        "title": "技术总监",
        "experience": "20年",
        "specialty": "技术架构与问题解决",
        "focus_traits": ["技术深度", "问题解决", "系统思维"],
        "phase": "technical"
    },
    "product": {
        "name": "王芳",
        "title": "产品经理",
        "experience": "12年",
        "specialty": "产品创新与用户体验",
        "focus_traits": ["产品思维", "用户洞察", "创新能力"],
        "phase": "product_thinking"
    },
    "cto": {
        "name": "刘强",
        "title": "CTO",
        "experience": "25年",
        "specialty": "技术战略与组织领导",
        "focus_traits": ["战略思维", "领导力", "决策能力"],
        "phase": "strategic"
    }
}


class InterviewerAgent:
    """面试官提问 Agent"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def generate_question(
        self,
        *,
        role_id: str = "hr",
        job_info: Optional[Dict[str, Any]] = None,
        resume_info: Optional[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, str]] = None,
        depth: int = 0,
        round_number: int = 1,
        total_rounds: int = 10,
        decision_directive: Optional[Dict[str, Any]] = None,
        interview_state_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成下一个面试问题（自适应版 - 支持决策指令驱动）

        Args:
            decision_directive: DecisionAgent 的指令，如:
                {"action": "probe_deeper", "probe_skill": "React", "hint": "..."}
                {"action": "fill_gap", "target_skills": ["k8s"], "hint": "..."}
            interview_state_context: 面试状态上下文快照

        Returns:
            {
                "question": str,
                "intent": str,
                "difficulty": str,
                "resume_anchor": str,
                "tags": list,
                "focus_area": str,
                "context": str,
                "expected_traits": list
            }
        """
        conversation_history = conversation_history or []
        job_info = job_info if isinstance(job_info, dict) else {}
        resume_info = resume_info if isinstance(resume_info, dict) else {}
        decision_directive = decision_directive if isinstance(decision_directive, dict) else {}
        interview_state_context = interview_state_context if isinstance(interview_state_context, dict) else {}
        role_id, role_meta = self._resolve_role(role_id, decision_directive)

        # 格式化对话历史
        history_text = self._format_history(conversation_history)

        # 格式化简历技能
        skills_raw = self._as_list(resume_info.get("skills", []))
        candidate_skills = ", ".join(skills_raw) if skills_raw else "未提供"

        # 格式化岗位技能要求
        job_skills_raw = self._as_list(job_info.get("required_skills", job_info.get("skills", [])))
        job_skills = ", ".join(job_skills_raw) if job_skills_raw else "未提供"

        # 格式化决策指令
        directive_text = self._format_directive(decision_directive)

        # 格式化面试状态摘要
        verified_skills_text = self._format_verified_skills(interview_state_context)
        skill_gaps = self._as_list(interview_state_context.get("skill_gaps", []))
        skill_gaps_text = ", ".join(skill_gaps) or "暂无"
        performance_trend = interview_state_context.get("performance_trend", "stable")
        difficulty_level = decision_directive.get("difficulty", interview_state_context.get("difficulty_level", 3))

        # 构建 prompt
        system_prompt, user_prompt = build_interviewer_prompt(
            role_name=role_meta["name"],
            role_title=role_meta["title"],
            role_experience=role_meta["experience"],
            role_specialty=role_meta["specialty"],
            job_title=job_info.get("title", job_info.get("name", "未指定")),
            job_description=job_info.get("description", "未提供"),
            job_skills=job_skills,
            candidate_name=resume_info.get("name", "候选人"),
            candidate_education=resume_info.get("education", "未提供"),
            candidate_skills=candidate_skills,
            candidate_experience=self._format_experience(resume_info),
            candidate_projects=resume_info.get("projects", resume_info.get("experience_summary", "未提供")),
            round_number=round_number,
            total_rounds=total_rounds,
            depth=depth,
            phase=role_meta["phase"],
            focus_traits=", ".join(role_meta["focus_traits"]),
            conversation_history=history_text,
            difficulty_level=difficulty_level,
            decision_directive=directive_text,
            verified_skills=verified_skills_text,
            skill_gaps=skill_gaps_text,
            performance_trend=performance_trend
        )

        logger.info(f"[InterviewerAgent] role={role_id}, depth={depth}, round={round_number}")

        try:
            response = await self.llm.call_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=400
            )

            result = self._parse_json(response.content)
            return self._normalize_question_result(
                result,
                role_id=role_id,
                role_meta=role_meta,
                job_info=job_info,
                resume_info=resume_info,
                conversation_history=conversation_history,
                depth=depth,
                decision_directive=decision_directive,
                interview_state_context=interview_state_context,
            )
        except Exception as e:
            logger.warning(
                "[InterviewerAgent] LLM 调用失败: type=%s repr=%r str=%s, 使用备用问题",
                type(e).__name__,
                e,
                str(e),
                exc_info=True,
            )
            return self._get_fallback(
                role_id,
                job_info,
                resume_info,
                depth,
                decision_directive,
                interview_state_context,
            )

    # ==================== 内部方法 ====================

    def _resolve_role(
        self,
        role_id: str,
        directive: Dict[str, Any],
    ) -> tuple[str, Dict[str, Any]]:
        """根据上游角色和 switch_role 指令确定本轮面试官身份。"""
        resolved_role = role_id
        if directive.get("action") == "switch_role":
            new_role = str(directive.get("new_role") or "").strip()
            if new_role in ROLE_META:
                resolved_role = new_role
        return resolved_role, ROLE_META.get(resolved_role, ROLE_META["hr"])

    def _normalize_question_result(
        self,
        result: Dict[str, Any],
        *,
        role_id: str,
        role_meta: Dict[str, Any],
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        depth: int,
        decision_directive: Dict[str, Any],
        interview_state_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """校验并修复 InterviewerAgent 的结构化输出。"""
        result = result if isinstance(result, dict) else {}
        question = str(result.get("question") or "").strip()
        tags = self._as_list(result.get("tags", []))
        focus_area = str(result.get("focus_area") or "").strip()
        intent = str(result.get("intent") or "").strip() or "综合考察"

        repair_reason = self._get_question_repair_reason(
            question=question,
            tags=tags,
            focus_area=focus_area,
            conversation_history=conversation_history,
            decision_directive=decision_directive,
        )
        if repair_reason:
            logger.info("[InterviewerAgent] 修复问题草案: %s", repair_reason)
            repaired = self._build_directive_question(
                role_id=role_id,
                role_meta=role_meta,
                job_info=job_info,
                resume_info=resume_info,
                depth=depth,
                decision_directive=decision_directive,
                interview_state_context=interview_state_context,
                reason=repair_reason,
            )
            question = repaired["question"]
            tags = repaired["tags"]
            focus_area = repaired["focus_area"]
            intent = repaired["intent"]

        if self._is_repeated_question(question, conversation_history):
            logger.info("[InterviewerAgent] 修复后问题仍重复，切换备用问法")
            if not decision_directive or decision_directive.get("action") == "fill_gap":
                decision_directive = dict(decision_directive or {})
                decision_directive["action"] = "switch_topic"
                missing = self._as_list(interview_state_context.get("missing_personality_traits", []))
                recent_focus = self._recent_focus_areas(conversation_history)
                topic = next((item for item in missing if item not in recent_focus), None)
                if topic:
                    decision_directive["new_topic"] = topic
            deduped = self._build_non_repeated_directive_question(
                role_id=role_id,
                role_meta=role_meta,
                job_info=job_info,
                resume_info=resume_info,
                depth=depth,
                decision_directive=decision_directive,
                interview_state_context=interview_state_context,
                conversation_history=conversation_history,
            )
            question = deduped["question"]
            tags = deduped["tags"]
            focus_area = deduped["focus_area"]
            intent = deduped["intent"]

        if self._has_same_focus_and_tags(
            question=question,
            focus_area=focus_area,
            tags=tags,
            conversation_history=conversation_history,
        ):
            logger.info("[InterviewerAgent] 问题 focus/tags 与历史高度重合，强制切换未覆盖维度")
            switched_directive = dict(decision_directive or {})
            switched_directive["action"] = "switch_topic"
            missing = self._as_list(interview_state_context.get("missing_personality_traits", []))
            recent_focus = self._recent_focus_areas(conversation_history)
            switched_directive["new_topic"] = next(
                (item for item in missing if item not in recent_focus),
                self._pick_personality_trait(missing, role_meta),
            )
            deduped = self._build_non_repeated_directive_question(
                role_id=role_id,
                role_meta=role_meta,
                job_info=job_info,
                resume_info=resume_info,
                depth=depth,
                decision_directive=switched_directive,
                interview_state_context=interview_state_context,
                conversation_history=conversation_history,
            )
            question = deduped["question"]
            tags = deduped["tags"]
            focus_area = deduped["focus_area"]
            intent = deduped["intent"]

        tags = self._ensure_big_five_tags(tags, focus_area, interview_state_context, role_meta)
        focus_area = focus_area or self._pick_focus_area(tags, role_meta, interview_state_context)
        expected_traits = self._resolve_expected_traits(tags, focus_area, role_meta)

        return {
            "question": question,
            "intent": intent,
            "difficulty": self._normalize_difficulty(result.get("difficulty"), decision_directive, depth),
            "resume_anchor": str(result.get("resume_anchor") or ""),
            "tags": tags,
            "focus_area": focus_area,
            "context": str(result.get("context") or intent),
            "expected_traits": expected_traits,
            "role_id": role_id,
        }

    def _get_question_repair_reason(
        self,
        *,
        question: str,
        tags: List[str],
        focus_area: str,
        conversation_history: List[Dict[str, Any]],
        decision_directive: Dict[str, Any],
    ) -> str:
        if len(question) < 12:
            return "问题为空或过短"
        if self._is_repeated_question(question, conversation_history):
            return "问题与历史提问重复"

        action = decision_directive.get("action")
        if action == "fill_gap":
            targets = self._as_list(decision_directive.get("target_skills", []))
            if targets and not self._contains_any(question + focus_area + " ".join(tags), targets):
                return "未覆盖待验证技能差距"
        elif action == "probe_deeper":
            probe_skill = str(decision_directive.get("probe_skill") or "").strip()
            if probe_skill and probe_skill not in question and probe_skill not in focus_area:
                return "未围绕指定技能追问"
        elif action == "switch_topic":
            topic = str(decision_directive.get("new_topic") or "").strip()
            if topic and topic not in question and topic not in focus_area and topic not in tags:
                return "未切换到指定话题"

        if not any(tag in BIG_FIVE_TRAITS for tag in tags + [focus_area]):
            return "缺少 Big Five 心理特质标签"
        return ""

    def _build_directive_question(
        self,
        *,
        role_id: str,
        role_meta: Dict[str, Any],
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        depth: int,
        decision_directive: Dict[str, Any],
        interview_state_context: Dict[str, Any],
        reason: str = "",
    ) -> Dict[str, Any]:
        """根据决策指令生成确定性修复问题。"""
        action = decision_directive.get("action", "continue")
        missing_traits = self._as_list(interview_state_context.get("missing_personality_traits", []))
        trait = self._pick_personality_trait(missing_traits, role_meta)
        job_anchor = self._pick_first(
            self._as_list(job_info.get("required_skills", job_info.get("skills", []))),
            str(job_info.get("title") or job_info.get("name") or "目标岗位"),
        )
        resume_anchor = self._pick_first(self._as_list(resume_info.get("skills", [])), "相关经历")

        if action == "fill_gap":
            targets = self._as_list(decision_directive.get("target_skills", []))
            target = self._pick_first(targets, job_anchor)
            question = f"围绕{target}，请结合一个具体项目说明你当时如何判断任务要求、推进实现并验证结果？"
            return {
                "question": question,
                "intent": "验证岗位技能差距并补充场景人格证据",
                "focus_area": target,
                "tags": ["技能匹配", "心理特质评估", target, trait],
            }

        if action == "probe_deeper":
            target = str(decision_directive.get("probe_skill") or "").strip() or resume_anchor
            question = f"刚才提到{target}，能进一步说明一个关键决策点吗？请讲清楚你的判断依据、权衡过程和最终结果。"
            return {
                "question": question,
                "intent": "深入追问候选人的问题解决过程",
                "focus_area": target,
                "tags": ["追问", target, trait],
            }

        if action == "switch_topic":
            topic = str(decision_directive.get("new_topic") or "").strip() or trait
            question = self._build_trait_question(topic, job_anchor, resume_anchor)
            return {
                "question": question,
                "intent": "切换话题以补充心理特质观察",
                "focus_area": topic,
                "tags": ["行为情境", "心理特质评估", topic],
            }

        if action == "switch_role":
            question = f"接下来从{role_meta['title']}视角看，请描述一次你在{job_anchor}相关任务中与他人协作并推动结果落地的经历。"
            return {
                "question": question,
                "intent": "多Agent面试视角下的综合评估",
                "focus_area": role_meta["focus_traits"][0],
                "tags": ["多Agent面试", "团队协作", trait],
            }

        focus_area = role_meta["focus_traits"][0]
        if reason == "缺少 Big Five 心理特质标签" or depth >= 2:
            question = self._build_trait_question(trait, job_anchor, resume_anchor)
            focus_area = trait
            tags = ["行为情境", "心理特质评估", trait]
            intent = "补充 Basic Personality 与 Scenario Personality 证据"
        else:
            question = f"请结合{resume_anchor}相关经历，说明你如何完成一个与{job_anchor}有关的任务，并复盘其中的关键收获。"
            tags = [focus_area, trait]
            intent = "结合简历与岗位要求进行综合考察"

        return {
            "question": question,
            "intent": intent,
            "focus_area": focus_area,
            "tags": tags,
        }

    def _build_non_repeated_directive_question(
        self,
        *,
        role_id: str,
        role_meta: Dict[str, Any],
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        depth: int,
        decision_directive: Dict[str, Any],
        interview_state_context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """在修复模板重复时，按同一目标生成不同角度的问题。"""
        action = decision_directive.get("action", "continue")
        missing_traits = self._as_list(interview_state_context.get("missing_personality_traits", []))
        trait = self._pick_personality_trait(missing_traits, role_meta)
        job_anchor = self._pick_first(
            self._as_list(job_info.get("required_skills", job_info.get("skills", []))),
            str(job_info.get("title") or job_info.get("name") or "目标岗位"),
        )
        resume_anchor = self._pick_first(self._as_list(resume_info.get("skills", [])), "相关经历")

        if action == "fill_gap":
            targets = self._as_list(decision_directive.get("target_skills", []))
            target = self._pick_first(targets, job_anchor)
            templates = [
                f"你刚才已经说明了{target}中的任务判断和推进过程。接下来请聚焦一次需求取舍：当业务目标、用户体验和实现成本不一致时，你如何排序并说服相关方？",
                f"换一个{target}相关场景来看，如果项目上线后的数据没有达到预期，你会先看哪些指标，如何判断问题来自需求、交互还是执行过程？",
                f"请从复盘角度补充一个{target}案例：如果现在重新做一次，你会保留什么、调整什么，依据是什么？",
            ]
            return self._select_question_variant(
                templates=templates,
                conversation_history=conversation_history,
                intent="验证岗位技能差距并补充场景人格证据",
                focus_area=target,
                tags=["技能匹配", "心理特质评估", target, trait],
            )

        if action == "probe_deeper":
            target = str(decision_directive.get("probe_skill") or "").strip() or resume_anchor
            templates = [
                f"关于{target}，请不要重复前面的整体流程，重点讲一个你当时最难判断的分歧点：有哪些备选方案，最后为什么选这一种？",
                f"继续看{target}这个方向，如果当时关键资源不足，你会怎样调整推进节奏并保证结果可验证？",
            ]
            return self._select_question_variant(
                templates=templates,
                conversation_history=conversation_history,
                intent="深入追问候选人的问题解决过程",
                focus_area=target,
                tags=["追问", target, trait],
            )

        topic = str(decision_directive.get("new_topic") or "").strip() or trait
        templates = [
            self._build_trait_question(topic, job_anchor, resume_anchor),
            f"请换一个不同于前面案例的经历，说明你在{job_anchor}相关情境下如何处理不确定性，并复盘你的判断是否有效。",
            f"从{role_meta['title']}视角看，请讲一次你在{job_anchor}相关任务中主动协调他人、推动结果落地的经历。",
        ]
        return self._select_question_variant(
            templates=templates,
            conversation_history=conversation_history,
            intent="补充岗位情境与心理特质观察",
            focus_area=topic,
            tags=["行为情境", "心理特质评估", topic],
        )

    def _select_question_variant(
        self,
        *,
        templates: List[str],
        conversation_history: List[Dict[str, Any]],
        intent: str,
        focus_area: str,
        tags: List[str],
    ) -> Dict[str, Any]:
        for question in templates:
            if question and not self._is_repeated_question(question, conversation_history):
                return {
                    "question": question,
                    "intent": intent,
                    "focus_area": focus_area,
                    "tags": tags,
                }
        return {
            "question": f"换一个新的角度来看{focus_area}：请结合一个尚未提到的具体情境，说明你的判断依据、行动步骤和复盘结论。",
            "intent": intent,
            "focus_area": focus_area,
            "tags": tags,
        }

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化最近 6 条对话"""
        if not history:
            return "(暂无历史记录)"

        recent = history[-6:]
        lines = []
        for msg in recent:
            role = msg.get("role", "unknown")
            label = "面试官" if role != "candidate" else "候选人"
            lines.append(f"{label}: {msg.get('content', '')}")
        return "\n".join(lines)

    def _format_experience(self, resume: Dict[str, Any]) -> str:
        """格式化工作经验描述"""
        years = resume.get("experience_years")
        desired = resume.get("desired_job", "")
        parts = []
        if years:
            parts.append(f"{years}年工作经验")
        if desired:
            parts.append(f"期望岗位: {desired}")
        return "；".join(parts) if parts else "未提供"

    def _as_list(self, value: Any) -> List[str]:
        """将外部输入规范为去空字符串列表。"""
        if value is None:
            return []
        if isinstance(value, list):
            raw_items = value
        elif isinstance(value, tuple) or isinstance(value, set):
            raw_items = list(value)
        else:
            raw_items = [value]

        items: List[str] = []
        for item in raw_items:
            if isinstance(item, dict):
                text = item.get("name") or item.get("skill_name") or item.get("trait") or item.get("title")
            else:
                text = item
            text = str(text or "").strip()
            if text and text not in items:
                items.append(text)
        return items

    def _pick_first(self, items: List[str], default: str) -> str:
        return items[0] if items else default

    def _contains_any(self, text: str, needles: List[str]) -> bool:
        return any(needle and needle in text for needle in needles)

    def _is_repeated_question(
        self,
        question: str,
        conversation_history: List[Dict[str, Any]],
    ) -> bool:
        normalized = self._normalize_text(question)
        if not normalized:
            return False
        for msg in conversation_history[-8:]:
            if msg.get("role") == "candidate":
                continue
            old = self._normalize_text(self._extract_history_question(msg))
            if old and (normalized == old or normalized in old or old in normalized):
                return True
            if self._text_similarity(normalized, old) >= 0.82:
                return True
        return False

    def _extract_history_question(self, msg: Dict[str, Any]) -> str:
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

    def _has_same_focus_and_tags(
        self,
        *,
        question: str,
        focus_area: str,
        tags: List[str],
        conversation_history: List[Dict[str, Any]],
    ) -> bool:
        current_tags = {str(tag).strip() for tag in (tags or []) if str(tag).strip()}
        for msg in conversation_history[-8:]:
            if msg.get("role") == "candidate":
                continue
            meta_tags = set(self._as_list(msg.get("tags", [])))
            if isinstance(msg.get("metadata"), dict):
                meta_tags.update(self._as_list(msg["metadata"].get("tags", [])))
            old_focus = str(msg.get("focus_area") or msg.get("focusArea") or "").strip()
            if isinstance(msg.get("metadata"), dict) and not old_focus:
                old_focus = str(msg["metadata"].get("focus_area") or "").strip()
            if old_focus and focus_area and old_focus == focus_area:
                old_text = self._extract_history_question(msg)
                if self._text_similarity(self._normalize_text(question), self._normalize_text(old_text)) >= 0.55:
                    return True
            if current_tags and meta_tags:
                overlap = len(current_tags & meta_tags) / max(len(current_tags), len(meta_tags))
                if overlap >= 0.7 and old_focus == focus_area:
                    return True
        return False

    def _recent_focus_areas(self, conversation_history: List[Dict[str, Any]]) -> set[str]:
        areas: set[str] = set()
        for msg in conversation_history[-8:]:
            if msg.get("role") == "candidate":
                continue
            focus = str(msg.get("focus_area") or msg.get("focusArea") or "").strip()
            if isinstance(msg.get("metadata"), dict) and not focus:
                focus = str(msg["metadata"].get("focus_area") or "").strip()
            if focus:
                areas.add(focus)
        return areas

    def _normalize_text(self, text: str) -> str:
        return "".join(str(text or "").split()).replace("？", "?")

    def _text_similarity(self, current: str, previous: str) -> float:
        if not current or not previous:
            return 0.0
        current_units = {current[i : i + 2] for i in range(max(1, len(current) - 1))}
        previous_units = {previous[i : i + 2] for i in range(max(1, len(previous) - 1))}
        if not current_units or not previous_units:
            return 0.0
        overlap = len(current_units & previous_units)
        return overlap / max(len(current_units), len(previous_units))

    def _ensure_big_five_tags(
        self,
        tags: List[str],
        focus_area: str,
        state_context: Dict[str, Any],
        role_meta: Dict[str, Any],
    ) -> List[str]:
        normalized = [tag for tag in tags if tag]
        if any(tag in BIG_FIVE_TRAITS for tag in normalized + [focus_area]):
            return list(dict.fromkeys(normalized))
        missing = self._as_list(state_context.get("missing_personality_traits", []))
        normalized.append(self._pick_personality_trait(missing, role_meta))
        return list(dict.fromkeys(normalized))

    def _pick_personality_trait(
        self,
        missing_traits: List[str],
        role_meta: Dict[str, Any],
    ) -> str:
        for trait in missing_traits:
            if trait in BIG_FIVE_TRAITS:
                return trait
        role_trait_map = {
            "沟通能力": "外向性",
            "团队协作": "宜人性",
            "文化契合": "宜人性",
            "技术深度": "开放性",
            "问题解决": "情绪稳定性",
            "系统思维": "开放性",
            "产品思维": "开放性",
            "用户洞察": "宜人性",
            "创新能力": "开放性",
            "战略思维": "开放性",
            "领导力": "外向性",
            "决策能力": "尽责性",
        }
        for focus in role_meta.get("focus_traits", []):
            trait = role_trait_map.get(focus)
            if trait:
                return trait
        return "尽责性"

    def _pick_focus_area(
        self,
        tags: List[str],
        role_meta: Dict[str, Any],
        state_context: Dict[str, Any],
    ) -> str:
        for tag in tags:
            if tag in BIG_FIVE_TRAITS:
                return tag
        missing = self._as_list(state_context.get("missing_personality_traits", []))
        return self._pick_personality_trait(missing, role_meta)

    def _resolve_expected_traits(
        self,
        tags: List[str],
        focus_area: str,
        role_meta: Dict[str, Any],
    ) -> List[str]:
        traits = [tag for tag in tags if tag in BIG_FIVE_TRAITS]
        if focus_area in BIG_FIVE_TRAITS:
            traits.insert(0, focus_area)
        if not traits:
            traits = [self._pick_personality_trait([], role_meta)]
        return list(dict.fromkeys(traits))

    def _normalize_difficulty(
        self,
        raw: Any,
        directive: Dict[str, Any],
        depth: int,
    ) -> str:
        difficulty = str(raw or "").strip().lower()
        if difficulty in {"easy", "medium", "hard"}:
            return difficulty
        level = directive.get("difficulty")
        try:
            level_int = int(level)
        except (TypeError, ValueError):
            level_int = 1 if depth <= 2 else 3 if depth <= 6 else 4
        if level_int <= 2:
            return "easy"
        if level_int >= 4:
            return "hard"
        return "medium"

    def _build_trait_question(self, trait: str, job_anchor: str, resume_anchor: str) -> str:
        questions = {
            "开放性": f"请描述一次你在{job_anchor}相关任务中需要快速学习或尝试新方法的经历，你如何判断学习重点并应用到结果中？",
            "尽责性": f"请描述一次你为了保证{job_anchor}相关交付质量而主动识别风险的经历，你采取了哪些具体措施？",
            "外向性": f"请描述一次你在{job_anchor}相关工作中需要主动沟通并影响他人的经历，你如何推动共识形成？",
            "宜人性": f"请描述一次你在{job_anchor}相关协作中遇到分歧的经历，你如何理解对方诉求并推进问题解决？",
            "情绪稳定性": f"请描述一次你在{job_anchor}相关任务中遇到压力或不确定性的经历，你如何调整节奏并保持判断稳定？",
        }
        if trait in questions:
            return questions[trait]
        return f"请结合{resume_anchor}相关经历，说明你在{job_anchor}情境下如何判断问题、采取行动并复盘结果。"

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """从 LLM 响应中提取 JSON"""
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass
        # 如果解析失败，把整个内容当作问题
        return {"question": content.strip()}

    def _format_directive(self, directive: Dict[str, Any]) -> str:
        """格式化 DecisionAgent 的指令为可读文本"""
        if not directive:
            return "无特殊指令，按正常流程提问"

        action = directive.get("action", "continue")
        hint = directive.get("hint", "")
        parts = [f"指令类型: {action}"]

        if action == "probe_deeper":
            skill = directive.get("probe_skill", "")
            reason = directive.get("probe_reason", "")
            if skill:
                parts.append(f"追问重点: {skill}")
            if reason:
                parts.append(f"追问原因: {reason}")
        elif action == "fill_gap":
            targets = self._as_list(directive.get("target_skills", []))
            if targets:
                parts.append(f"需验证的差距技能: {', '.join(targets)}")
        elif action == "switch_topic":
            new_topic = directive.get("new_topic", "")
            if new_topic:
                parts.append(f"切换到话题: {new_topic}")
        elif action == "switch_role":
            new_role = directive.get("new_role", "")
            if new_role:
                parts.append(f"切换面试官: {new_role}")

        difficulty = directive.get("difficulty", "")
        if difficulty:
            parts.append(f"建议难度: {difficulty}/5")

        if hint:
            parts.append(f"提示: {hint}")

        return "\n".join(parts)

    def _format_verified_skills(self, state_context: Dict[str, Any]) -> str:
        """格式化已验证技能摘要"""
        verified = state_context.get("verified_skills", {})
        if not verified:
            return "暂无"

        parts = []
        if not isinstance(verified, dict):
            return ", ".join(self._as_list(verified)) or "暂无"

        for name, info in verified.items():
            if isinstance(info, dict):
                try:
                    score = float(info.get("score", 0) or 0)
                except (TypeError, ValueError):
                    score = 0.0
                verified_flag = "✓" if info.get("verified") else "?"
                parts.append(f"{name}({score:.1f}分{verified_flag})")
            else:
                parts.append(str(name))
        return ", ".join(parts) if parts else "暂无"

    def _get_fallback(
        self,
        role_id: str,
        job_info: Dict[str, Any],
        resume_info: Dict[str, Any],
        depth: int,
        decision_directive: Optional[Dict[str, Any]] = None,
        interview_state_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """基于岗位、状态和决策指令生成备用问题。"""
        job_info = job_info if isinstance(job_info, dict) else {}
        resume_info = resume_info if isinstance(resume_info, dict) else {}
        decision_directive = decision_directive if isinstance(decision_directive, dict) else {}
        interview_state_context = interview_state_context if isinstance(interview_state_context, dict) else {}
        role_id, role_meta = self._resolve_role(role_id, decision_directive)
        draft = self._build_directive_question(
            role_id=role_id,
            role_meta=role_meta,
            job_info=job_info,
            resume_info=resume_info,
            depth=depth,
            decision_directive=decision_directive,
            interview_state_context=interview_state_context,
            reason="fallback",
        )
        tags = self._ensure_big_five_tags(draft["tags"], draft["focus_area"], interview_state_context, role_meta)
        expected_traits = self._resolve_expected_traits(tags, draft["focus_area"], role_meta)
        return {
            "question": draft["question"],
            "intent": draft["intent"],
            "difficulty": self._normalize_difficulty(None, decision_directive, depth),
            "resume_anchor": "",
            "tags": tags,
            "focus_area": draft["focus_area"],
            "context": draft["intent"],
            "expected_traits": expected_traits,
            "role_id": role_id,
        }
