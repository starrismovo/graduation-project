"""
EvaluatorAgent - 回答评估 Agent（技能差距识别版）
===================================================

职责：
  分析候选人的回答，输出结构化评估结果。
  对标岗位需求 + 简历声称技能，给出匹配度分析。
  输出结构化技能差距识别结果，驱动 DecisionAgent 追问策略。

输入：
  - candidate_response: 候选人回答文本
  - last_question: 面试官提出的问题
  - job_info: 岗位信息
  - resume_info: 候选人简历信息
  - role_id, depth, conversation_history
  - interview_state_context: 面试状态上下文（已验证技能、已知差距等）

输出：
  {
    "scores": { "沟通能力": 8, ... },
    "evidence": "评分依据",
    "strengths": [...],
    "improvements": [...],
    "skill_match": { "matched": [...], "gap": [...], "needs_verification": [...] },
    "depth_assessment": { "answer_depth": ..., "specificity": ..., "confidence_indicator": ... },
    "feedback": "简短反馈",
    "next_action": "continue / switch_role / end_phase",
    "follow_up_hint": "追问建议"
  }
"""

import json
import logging
import re
from typing import Optional, Dict, List, Any

from utils.llm_client import LLMClient
from utils.trait_evaluator import TraitEvaluator
from prompts.agent_prompts import build_evaluator_prompt
from services.big_five_rubric import build_personality_observation

logger = logging.getLogger(__name__)

# 角色元信息（与 InterviewerAgent 保持一致）
ROLE_META = {
    "hr": {"name": "李明", "title": "HR 经理", "focus_traits": ["沟通能力", "团队协作", "文化契合"]},
    "tech_lead": {"name": "张伟", "title": "技术总监", "focus_traits": ["技术深度", "问题解决", "系统思维"]},
    "product": {"name": "王芳", "title": "产品经理", "focus_traits": ["产品思维", "用户洞察", "创新能力"]},
    "cto": {"name": "刘强", "title": "CTO", "focus_traits": ["战略思维", "领导力", "决策能力"]},
}


class EvaluatorAgent:
    """回答评估 Agent"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.trait_evaluator = TraitEvaluator()

    async def evaluate(
        self,
        *,
        candidate_response: str,
        last_question: str = "",
        role_id: str = "hr",
        job_info: Optional[Dict[str, Any]] = None,
        resume_info: Optional[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, str]] = None,
        depth: int = 0,
        interview_state_context: Optional[Dict[str, Any]] = None,
        question_tags: Optional[List[str]] = None,
        expected_traits: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        评估候选人回答（含技能差距识别）

        Args:
            interview_state_context: 面试状态上下文（已验证技能、已知差距等）

        Returns:
            {
                "scores": dict,
                "sentiment": dict,
                "patterns": list,
                "feedback": str,
                "next_action": str,
                "skill_match": dict,     # 含 needs_verification 字段
                "depth_assessment": dict, # 回答深度评估
                "follow_up_hint": str,
                "raw_evaluation": dict
            }
        """
        job_info = job_info or {}
        resume_info = resume_info or {}
        conversation_history = conversation_history or []
        interview_state_context = interview_state_context or {}
        role_meta = ROLE_META.get(role_id, ROLE_META["hr"])

        # 格式化简历技能
        skills_raw = resume_info.get("skills", [])
        if isinstance(skills_raw, list):
            candidate_skills = ", ".join(skills_raw) if skills_raw else "未提供"
        else:
            candidate_skills = str(skills_raw) or "未提供"

        # 格式化岗位技能
        job_skills_raw = job_info.get("required_skills", job_info.get("skills", []))
        if isinstance(job_skills_raw, list):
            job_skills = ", ".join(job_skills_raw) if job_skills_raw else "未提供"
        else:
            job_skills = str(job_skills_raw) or "未提供"

        # 如果没有明确的上一个问题，从历史中提取
        question_tags = self._normalize_tags(question_tags)
        expected_traits = self._normalize_tags(expected_traits)
        answer_repeats_question = self._answer_repeats_question(candidate_response, last_question)
        if not last_question and conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("role") != "candidate" and msg.get("scoreable", True) is not False:
                    last_question = self._extract_question_text(msg)
                    question_tags = self._merge_tags(question_tags, self._extract_tags_from_message(msg))
                    expected_traits = self._merge_tags(expected_traits, self._extract_expected_traits_from_message(msg))
                    break
        elif conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("role") != "candidate" and self._extract_question_text(msg) == last_question:
                    question_tags = self._merge_tags(question_tags, self._extract_tags_from_message(msg))
                    expected_traits = self._merge_tags(expected_traits, self._extract_expected_traits_from_message(msg))
                    break
        answer_repeats_question = self._answer_repeats_question(candidate_response, last_question)

        # 构建面试状态摘要
        verified_skills_summary = self._format_verified_skills(interview_state_context)
        known_gaps = ", ".join(interview_state_context.get("skill_gaps", [])) or "暂无"
        performance_trend = interview_state_context.get("performance_trend", "stable")

        # 构建 prompt
        system_prompt, user_prompt = build_evaluator_prompt(
            job_title=job_info.get("title", job_info.get("name", "未指定")),
            job_description=job_info.get("description", "未提供"),
            job_skills=job_skills,
            candidate_skills=candidate_skills,
            candidate_education=resume_info.get("education", "未提供"),
            phase=role_meta.get("phase", "opening") if "phase" in role_meta else self._infer_phase(depth),
            role_name=role_meta["name"],
            role_title=role_meta["title"],
            depth=depth,
            focus_traits=", ".join(role_meta["focus_traits"]),
            last_question=last_question,
            candidate_response=candidate_response,
            verified_skills_summary=verified_skills_summary,
            known_gaps=known_gaps,
            performance_trend=performance_trend
        )

        logger.info(f"[EvaluatorAgent] role={role_id}, depth={depth}")

        try:
            response = await self.llm.call_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.4,   # 低温度保证评估一致性
                max_tokens=900
            )

            evaluation = self._parse_json(response.content)

            depth_assessment = evaluation.get("depth_assessment", {
                "answer_depth": "moderate",
                "specificity": "general",
                "confidence_indicator": "moderate",
            })
            question_tags = self._extract_question_tags(
                last_question,
                evaluation,
                self._merge_tags(question_tags, expected_traits),
            )

            # 提取并校准评分：不对未观察维度补默认 5 分
            raw_scores = self.trait_evaluator.extract_scores(evaluation)
            calibration = self.trait_evaluator.calibrate_scores_from_response(
                candidate_response=candidate_response,
                question_tags=question_tags,
                raw_scores=raw_scores,
                last_question=last_question,
            )
            if answer_repeats_question:
                calibration["quality_signals"]["answer_repeats_question"] = True
                calibration["quality_signals"]["low_evidence"] = True
                calibration["scores"] = {}
                calibration["score_coverage"] = self.trait_evaluator.build_score_coverage({})
            observed_dimensions = [
                key for key, status in calibration["score_coverage"].items()
                if status == "observed"
            ]
            evidence_text = str(evaluation.get("evidence") or evaluation.get("evidence_quote") or "").strip()
            if self.trait_evaluator.is_score_anomalous(
                raw_scores,
                target_dimensions=observed_dimensions,
                quality_signals=calibration["quality_signals"],
                evidence_text=evidence_text,
            ):
                scores = calibration["scores"]
                score_coverage = calibration["score_coverage"]
            else:
                blended = self._blend_scores(raw_scores, calibration["scores"], calibration["score_coverage"])
                scores = blended["scores"]
                score_coverage = blended["score_coverage"]
            quality_signals = calibration["quality_signals"]

            skill_match = evaluation.get("skill_match", {}) if isinstance(evaluation.get("skill_match"), dict) else {}
            verified_skills = evaluation.get("verified_skills")
            if not isinstance(verified_skills, list):
                verified_skills = skill_match.get("matched", [])
            missing_must_have_skills = evaluation.get("missing_must_have_skills")
            if not isinstance(missing_must_have_skills, list):
                missing_must_have_skills = []

            personality_observation = build_personality_observation(
                evaluation.get("personality_observation", {}),
                candidate_response=candidate_response,
                depth_assessment=depth_assessment,
                ability_scores=scores,
                question_tags=question_tags,
                expected_traits=expected_traits,
            )
            personality_evidence = evaluation.get("personality_evidence")
            if not isinstance(personality_evidence, dict):
                personality_evidence = personality_observation.get("trait_evidence", {}) or {}
            evidence_quote = str(evaluation.get("evidence_quote") or evaluation.get("evidence") or "").strip()
            if len(evidence_quote) > 80:
                evidence_quote = evidence_quote[:80]

            # 检测行为模式
            patterns = self.trait_evaluator.detect_patterns(
                response=candidate_response,
                evaluation=evaluation
            )

            # 决定下一步行动
            next_action = evaluation.get("next_action", self._decide_next_action(depth, scores))

            feedback = self._build_feedback(
                evaluation.get("feedback", ""),
                quality_signals,
                personality_observation,
            )

            return {
                "scores": scores,
                "score_coverage": score_coverage,
                "quality_signals": quality_signals,
                "sentiment": {
                    "emotion": self._infer_emotion(evaluation),
                    "confidence": self._infer_confidence(evaluation, scores)
                },
                "patterns": patterns,
                "feedback": feedback,
                "next_action": next_action,
                "skill_match": {
                    "matched": skill_match.get("matched", []),
                    "gap": skill_match.get("gap", []),
                    "needs_verification": skill_match.get("needs_verification", []),
                },
                "verified_skills": verified_skills,
                "missing_must_have_skills": missing_must_have_skills,
                "depth_assessment": depth_assessment,
                "follow_up_hint": evaluation.get("follow_up_hint", ""),
                "personality_observation": personality_observation,
                "personality_evidence": personality_evidence,
                "evidence_quote": evidence_quote,
                "suggested_next_question": self._normalize_next_question(
                    evaluation.get("suggested_next_question"),
                    role_meta,
                ),
                "evidence": evaluation.get("evidence", ""),
                "strengths": evaluation.get("strengths", []),
                "improvements": evaluation.get("improvements", []),
                "raw_evaluation": evaluation
            }

        except Exception as e:
            logger.warning(
                "[EvaluatorAgent] LLM 调用失败: type=%s repr=%r str=%s, 使用备用评估",
                type(e).__name__,
                e,
                str(e),
                exc_info=True,
            )
            return self._get_fallback(role_id, depth)

    # ==================== 内部方法 ====================

    def _infer_phase(self, depth: int) -> str:
        if depth <= 2:
            return "opening"
        elif depth <= 5:
            return "technical"
        elif depth <= 7:
            return "product_thinking"
        elif depth <= 9:
            return "multi_perspective"
        else:
            return "strategic"

    def _infer_emotion(self, evaluation: Dict) -> str:
        """从评估结果推断候选人情绪"""
        feedback = evaluation.get("feedback", "")
        if any(w in feedback for w in ["优秀", "出色", "深入", "清晰"]):
            return "自信"
        elif any(w in feedback for w in ["不错", "良好", "继续"]):
            return "平稳"
        elif any(w in feedback for w in ["模糊", "偏题", "欠缺"]):
            return "紧张"
        return "思考中"

    def _infer_confidence(self, evaluation: Dict, scores: Dict) -> int:
        """推断回答自信度"""
        if not scores:
            return 0
        avg = sum(scores.values()) / len(scores) if scores else 5
        return min(100, int(avg * 12))

    def _extract_tags_from_message(self, msg: Dict[str, Any]) -> List[str]:
        tags: List[str] = []
        containers = [msg]
        if isinstance(msg.get("metadata"), dict):
            containers.append(msg["metadata"])
        if isinstance(msg.get("data"), dict):
            containers.append(msg["data"])
        for source in containers:
            raw_tags = source.get("tags")
            if isinstance(raw_tags, list):
                tags.extend(str(item) for item in raw_tags)
            if source.get("focus_area"):
                tags.append(str(source.get("focus_area")))
        return list(dict.fromkeys([tag.strip() for tag in tags if tag and tag.strip()]))

    def _extract_question_text(self, msg: Dict[str, Any]) -> str:
        for key in ("question", "content", "message"):
            raw = msg.get(key)
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
            if isinstance(raw, dict):
                return str(raw.get("question") or raw.get("content") or "").strip()
        for wrapper in ("metadata", "data"):
            payload = msg.get(wrapper)
            if isinstance(payload, dict):
                text = str(payload.get("question") or payload.get("content") or "").strip()
                if text:
                    return text
        return ""

    def _extract_expected_traits_from_message(self, msg: Dict[str, Any]) -> List[str]:
        traits = msg.get("expected_traits")
        if traits is None and isinstance(msg.get("metadata"), dict):
            traits = msg["metadata"].get("expected_traits")
        if traits is None and isinstance(msg.get("data"), dict):
            traits = msg["data"].get("expected_traits")
        return self._normalize_tags(traits)

    def _normalize_tags(self, value: Optional[List[str]]) -> List[str]:
        if not value:
            return []
        if not isinstance(value, list):
            value = [value]
        return list(dict.fromkeys([
            str(item).strip()
            for item in value
            if str(item or "").strip()
        ]))

    def _merge_tags(self, *groups: List[str]) -> List[str]:
        merged: List[str] = []
        for group in groups:
            for tag in self._normalize_tags(group):
                if tag not in merged:
                    merged.append(tag)
        return merged

    def _extract_question_tags(
        self,
        last_question: str,
        evaluation: Dict[str, Any],
        existing_tags: Optional[List[str]] = None,
    ) -> List[str]:
        tags: List[str] = list(existing_tags or [])
        question = last_question or ""
        for tag in [
            "沟通能力", "问题解决", "技术深度", "团队协作", "创新能力", "学习能力",
            "领导力", "战略思维", "用户洞察", "文化契合", "产品思维", "需求分析",
            "用户研究", "外向性", "宜人性", "尽责性", "开放性", "情绪稳定性",
        ]:
            if tag in question:
                tags.append(tag)
        return list(dict.fromkeys(tags))

    def _answer_repeats_question(self, answer: str, question: str) -> bool:
        answer_norm = self._normalize_text(answer)
        question_norm = self._normalize_text(question)
        if not answer_norm or not question_norm:
            return False
        if answer_norm == question_norm:
            return True
        length_ratio = len(answer_norm) / max(len(question_norm), 1)
        if len(answer_norm) >= 12 and answer_norm in question_norm:
            return True
        if len(answer_norm) >= 12 and question_norm in answer_norm and length_ratio <= 1.35:
            return True
        if length_ratio < 0.55 or length_ratio > 1.45:
            return False
        answer_units = {answer_norm[i : i + 2] for i in range(max(1, len(answer_norm) - 1))}
        question_units = {question_norm[i : i + 2] for i in range(max(1, len(question_norm) - 1))}
        if not answer_units or not question_units:
            return False
        return len(answer_units & question_units) / max(len(answer_units), len(question_units)) >= 0.78

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", "", str(text or "")).replace("？", "?")

    def _build_feedback(
        self,
        llm_feedback: str,
        quality_signals: Dict[str, Any],
        personality_observation: Dict[str, Any],
    ) -> str:
        if quality_signals.get("answer_repeats_question"):
            return "你这轮主要复述了问题本身，还缺少自己的经历、行动和结果。下一题我会换一个更具体的场景，帮助你展开。"
        if quality_signals.get("low_evidence"):
            return "这轮回答信息量偏少，暂时不足以形成稳定的心理特质证据。建议结合具体场景、行动步骤和结果补充说明。"
        observed = personality_observation.get("observed_traits") or []
        if observed:
            return f"这轮回答提供了较具体的行为证据，已观察到{ '、'.join(observed[:3]) }相关线索。接下来会补充其他未覆盖维度。"
        if llm_feedback and "回答不错，继续保持" not in llm_feedback:
            return llm_feedback
        return "这轮回答具备一定岗位相关性，但心理特质证据还需要结合后续情境继续验证。"

    def _blend_scores(
        self,
        raw_scores: Dict[str, float],
        calibrated_scores: Dict[str, float],
        calibration_coverage: Dict[str, str],
    ) -> Dict[str, Any]:
        blended: Dict[str, float] = {}
        for key, calibrated in calibrated_scores.items():
            if calibration_coverage.get(key) != "observed":
                continue
            if key in raw_scores:
                blended[key] = round(float(raw_scores[key]) * 0.55 + float(calibrated) * 0.45, 1)
            else:
                blended[key] = round(float(calibrated), 1)
        return {
            "scores": blended,
            "score_coverage": self.trait_evaluator.build_score_coverage(blended, list(blended.keys())),
        }

    def _decide_next_action(self, depth: int, scores: Dict) -> str:
        if depth >= 10:
            return "end_phase"
        elif depth > 0 and depth % 3 == 0:
            return "switch_role"
        return "continue"

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """从 LLM 响应中提取 JSON"""
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass
        return {}

    def _format_verified_skills(self, state_context: Dict[str, Any]) -> str:
        """格式化已验证技能摘要"""
        verified = state_context.get("verified_skills", {})
        if not verified:
            return "暂无"
        parts = []
        for name, info in verified.items():
            if isinstance(info, dict):
                score = info.get("score", 0)
                verified_flag = "✓" if info.get("verified") else "?"
                parts.append(f"{name}({score:.1f}分{verified_flag})")
            else:
                parts.append(str(name))
        return ", ".join(parts) if parts else "暂无"

    def _get_fallback(self, role_id: str, depth: int) -> Dict[str, Any]:
        """备用评估结果"""
        role_meta = ROLE_META.get(role_id, ROLE_META["hr"])
        personality_observation = build_personality_observation(
            {},
            candidate_response="",
            depth_assessment={"answer_depth": "shallow", "specificity": "vague"},
            ability_scores={},
        )
        return {
            "scores": {},
            "score_coverage": self.trait_evaluator.build_score_coverage({}),
            "quality_signals": {"fallback": True, "reason": "llm_evaluation_failed"},
            "sentiment": {"emotion": "无法判断", "confidence": 0},
            "patterns": [],
            "feedback": "回答有一定参考价值，继续保持",
            "next_action": "continue",
            "skill_match": {"matched": [], "gap": [], "needs_verification": []},
            "verified_skills": [],
            "missing_must_have_skills": [],
            "follow_up_hint": "",
            "personality_observation": personality_observation,
            "personality_evidence": personality_observation.get("trait_evidence", {}) or {},
            "evidence_quote": "",
            "suggested_next_question": self._normalize_next_question(None, role_meta),
            "evidence": "",
            "strengths": [],
            "improvements": [],
            "raw_evaluation": {}
        }

    def _normalize_next_question(
        self,
        raw: Optional[Dict[str, Any]],
        role_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Normalize EvaluatorAgent's one-call next-question draft."""
        raw = raw if isinstance(raw, dict) else {}
        question = str(raw.get("question") or "").strip()
        focus_area = str(raw.get("focus_area") or role_meta["focus_traits"][0]).strip()
        tags = raw.get("tags")
        if not isinstance(tags, list):
            tags = [focus_area]
        if not question:
            question = "请结合一个具体经历，说明你在压力或协作情境下如何做出判断并推进结果。"
            focus_area = "情绪稳定性"
            tags = ["心理特质评估", "情绪稳定性", "行为情境"]
        return {
            "question": question,
            "intent": raw.get("intent", "补充评估证据"),
            "difficulty": raw.get("difficulty", "medium"),
            "focus_area": focus_area,
            "tags": tags,
            "context": raw.get("context", raw.get("intent", "")),
            "expected_traits": [focus_area],
        }
