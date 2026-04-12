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
from typing import Optional, Dict, List, Any

from utils.llm_client import LLMClient
from utils.trait_evaluator import TraitEvaluator
from prompts.agent_prompts import build_evaluator_prompt

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
        if not last_question and conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("role") != "candidate":
                    last_question = msg.get("content", "")
                    break

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
                max_tokens=600
            )

            evaluation = self._parse_json(response.content)

            # 提取标准化评分
            scores = self.trait_evaluator.extract_scores(evaluation)

            # 检测行为模式
            patterns = self.trait_evaluator.detect_patterns(
                response=candidate_response,
                evaluation=evaluation
            )

            # 决定下一步行动
            next_action = evaluation.get("next_action", self._decide_next_action(depth, scores))

            return {
                "scores": scores,
                "sentiment": {
                    "emotion": self._infer_emotion(evaluation),
                    "confidence": self._infer_confidence(evaluation, scores)
                },
                "patterns": patterns,
                "feedback": evaluation.get("feedback", "回答不错，继续保持"),
                "next_action": next_action,
                "skill_match": {
                    "matched": evaluation.get("skill_match", {}).get("matched", []),
                    "gap": evaluation.get("skill_match", {}).get("gap", []),
                    "needs_verification": evaluation.get("skill_match", {}).get("needs_verification", []),
                },
                "depth_assessment": evaluation.get("depth_assessment", {
                    "answer_depth": "moderate",
                    "specificity": "general",
                    "confidence_indicator": "moderate",
                }),
                "follow_up_hint": evaluation.get("follow_up_hint", ""),
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
            return 60
        avg = sum(scores.values()) / len(scores) if scores else 5
        return min(100, int(avg * 12))

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
        return {
            "scores": {trait: 6.5 for trait in role_meta["focus_traits"]},
            "sentiment": {"emotion": "平稳", "confidence": 65},
            "patterns": [],
            "feedback": "回答有一定参考价值，继续保持",
            "next_action": "continue",
            "skill_match": {"matched": [], "gap": []},
            "follow_up_hint": "",
            "evidence": "",
            "strengths": [],
            "improvements": [],
            "raw_evaluation": {}
        }
