"""
DecisionAgent - 面试决策引擎 Agent
===================================

职责：
  根据 EvaluatorAgent 的评估结果和 AdaptiveInterviewState 的累积状态，
  做出面试流程决策：
  - 决定下一步动作（追问/切换话题/切换角色/调整难度/结束）
  - 识别技能差距并生成追问指令
  - 动态调整面试路径
  - 生成面试终结建议

输入：
  - evaluation_result: EvaluatorAgent 的评估输出
  - interview_state: AdaptiveInterviewState 当前状态快照
  - job_info, resume_info

输出：
  {
    "action": "probe_deeper | switch_topic | switch_role | ...",
    "directive": { ... },   # 给 InterviewerAgent 的指令
    "reasoning": "决策理由",
    "priority_gaps": [...],  # 优先填补的技能差距
    "suggested_difficulty": 1-5,
    "suggested_role": "hr | tech_lead | product | cto",
    "should_end": false
  }
"""

import json
import logging
from typing import Optional, Dict, List, Any

from utils.llm_client import LLMClient
from prompts.agent_prompts import build_decision_prompt
from services.agents.interview_state import (
    AdaptiveInterviewState,
    InterviewAction,
    DifficultyLevel,
    PerformanceTrend,
)

logger = logging.getLogger(__name__)

# 角色转换规则
ROLE_TRANSITION = {
    "hr": "tech_lead",
    "tech_lead": "product",
    "product": "cto",
    "cto": "cto",  # CTO 是最终角色
}

# 每个角色的建议提问轮数
ROLE_QUESTION_BUDGET = {
    "hr": 3,
    "tech_lead": 4,
    "product": 3,
    "cto": 2,
}


class DecisionAgent:
    """面试决策 Agent"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def decide(
        self,
        *,
        evaluation_result: Dict[str, Any],
        interview_state: AdaptiveInterviewState,
        job_info: Optional[Dict[str, Any]] = None,
        resume_info: Optional[Dict[str, Any]] = None,
        max_questions: int = 12,
    ) -> Dict[str, Any]:
        """
        根据评估结果和面试状态做出决策

        Returns:
            {
                "action": str,          # InterviewAction 值
                "directive": dict,      # 给 InterviewerAgent 的指令
                "reasoning": str,       # 决策理由
                "priority_gaps": list,  # 优先技能差距
                "suggested_difficulty": int,
                "suggested_role": str,
                "should_end": bool
            }
        """
        job_info = job_info or {}
        resume_info = resume_info or {}

        state_context = interview_state.to_context_dict()

        # ===== 规则优先：硬性条件直接判断 =====
        rule_decision = self._apply_rules(interview_state, evaluation_result, max_questions)
        if rule_decision:
            logger.info(f"[DecisionAgent] 规则决策: {rule_decision['action']}")
            return rule_decision

        # ===== LLM 辅助决策 =====
        try:
            system_prompt, user_prompt = build_decision_prompt(
                state_context=json.dumps(state_context, ensure_ascii=False, indent=2),
                evaluation_summary=self._format_evaluation_summary(evaluation_result),
                skill_gaps=", ".join(interview_state.skill_gaps) or "暂无",
                unverified_skills=", ".join(interview_state.get_unverified_required_skills()) or "暂无",
                performance_trend=interview_state.performance_trend.value,
                current_difficulty=interview_state.difficulty_level.value,
                current_role=interview_state.current_role,
                total_questions=interview_state.total_questions,
                max_questions=max_questions,
                coverage_rate=state_context["coverage"]["coverage_rate"],
            )

            response = await self.llm.call_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,   # 低温度确保决策稳定
                max_tokens=300,
            )

            decision = self._parse_json(response.content)

            # 规范化 action
            action = self._normalize_action(decision.get("action", "continue"))

            # 构建指令
            directive = self._build_directive(
                action=action,
                decision=decision,
                interview_state=interview_state,
                evaluation_result=evaluation_result,
            )

            result = {
                "action": action.value,
                "directive": directive,
                "reasoning": decision.get("reasoning", "基于综合分析"),
                "priority_gaps": decision.get("priority_gaps", interview_state.skill_gaps[:3]),
                "suggested_difficulty": min(5, max(1, decision.get("suggested_difficulty", interview_state.difficulty_level.value))),
                "suggested_role": decision.get("suggested_role", interview_state.current_role),
                "should_end": action == InterviewAction.END_INTERVIEW,
            }

            # 更新状态
            interview_state.last_action = action
            if result["suggested_role"] != interview_state.current_role:
                interview_state.current_role = result["suggested_role"]

            logger.info(f"[DecisionAgent] LLM决策: action={action.value}, role={result['suggested_role']}")
            return result

        except Exception as e:
            logger.warning(
                "[DecisionAgent] LLM 调用失败: type=%s repr=%r str=%s, 使用规则决策",
                type(e).__name__,
                e,
                str(e),
                exc_info=True,
            )
            return self._get_fallback_decision(interview_state, evaluation_result)

    # ==================== 规则引擎 ====================

    def _apply_rules(
        self,
        state: AdaptiveInterviewState,
        evaluation: Dict[str, Any],
        max_questions: int,
    ) -> Optional[Dict[str, Any]]:
        """硬性规则判断（优先级高于 LLM）"""

        # 规则1：达到最大提问数 → 结束
        if state.total_questions >= max_questions:
            return {
                "action": InterviewAction.END_INTERVIEW.value,
                "directive": {"reason": "已达到最大提问数"},
                "reasoning": f"已完成 {state.total_questions} 个问题，达到上限",
                "priority_gaps": state.skill_gaps[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": True,
            }

        # 规则2：所有必需技能已验证 + 已问足够多 → 结束
        coverage = state.get_coverage_summary()
        if (
            coverage["coverage_rate"] >= 0.9
            and state.total_questions >= max_questions * 0.7
        ):
            return {
                "action": InterviewAction.END_INTERVIEW.value,
                "directive": {"reason": "核心技能覆盖率已达标"},
                "reasoning": f"技能覆盖率 {coverage['coverage_rate']:.0%}，已充分验证",
                "priority_gaps": [],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": True,
            }

        # 规则3：当前角色提问轮数耗尽 → 切换角色
        current_role = state.current_role
        budget = ROLE_QUESTION_BUDGET.get(current_role, 3)
        role_questions = sum(
            1 for step in state.interview_path if step.get("role") == current_role
        )
        if role_questions >= budget and current_role != "cto":
            next_role = ROLE_TRANSITION.get(current_role, "cto")
            return {
                "action": InterviewAction.SWITCH_ROLE.value,
                "directive": {
                    "new_role": next_role,
                    "reason": f"{current_role} 阶段已完成 {role_questions} 轮提问",
                },
                "reasoning": f"当前角色 {current_role} 已完成预算轮数，切换至 {next_role}",
                "priority_gaps": state.skill_gaps[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": next_role,
                "should_end": False,
            }

        return None  # 无硬性规则匹配，交给 LLM

    # ==================== 指令构建 ====================

    def _build_directive(
        self,
        action: InterviewAction,
        decision: Dict[str, Any],
        interview_state: AdaptiveInterviewState,
        evaluation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """构建给 InterviewerAgent 的执行指令"""

        base_directive = {
            "action": action.value,
            "difficulty": interview_state.difficulty_level.value,
        }

        if action == InterviewAction.PROBE_DEEPER:
            # 追问指令：指定追问方向
            probe_skill = decision.get("probe_skill", interview_state.current_focus_skill or "")
            base_directive["probe_skill"] = probe_skill
            base_directive["probe_reason"] = decision.get("probe_reason", "回答缺乏深度，需要进一步验证")
            base_directive["hint"] = f"请围绕「{probe_skill}」进行深入追问"

        elif action == InterviewAction.FILL_GAP:
            # 填补差距指令：指定目标技能
            gaps = interview_state.skill_gaps[:2]
            base_directive["target_skills"] = gaps
            base_directive["hint"] = f"候选人在以下技能存在差距: {', '.join(gaps)}，请设计验证问题"

        elif action == InterviewAction.SWITCH_TOPIC:
            # 切换话题指令
            explored = set(interview_state.topics_explored)
            all_topics = {"技术深度", "问题解决", "团队协作", "产品思维", "系统设计", "领导力"}
            unexplored = list(all_topics - explored)
            base_directive["new_topic"] = unexplored[0] if unexplored else "综合评估"
            base_directive["hint"] = f"切换到新话题: {base_directive['new_topic']}"

        elif action == InterviewAction.SWITCH_ROLE:
            new_role = decision.get("suggested_role", ROLE_TRANSITION.get(interview_state.current_role, "cto"))
            base_directive["new_role"] = new_role
            base_directive["hint"] = f"切换面试官至 {new_role}"

        elif action in (InterviewAction.RAISE_DIFFICULTY, InterviewAction.LOWER_DIFFICULTY):
            base_directive["hint"] = f"调整难度至 {interview_state.difficulty_level.value}"

        return base_directive

    # ==================== 辅助方法 ====================

    def _format_evaluation_summary(self, evaluation: Dict[str, Any]) -> str:
        """格式化评估摘要供 LLM 参考"""
        scores = evaluation.get("scores", {})
        skill_match = evaluation.get("skill_match", {})
        feedback = evaluation.get("feedback", "")
        strengths = evaluation.get("strengths", [])
        improvements = evaluation.get("improvements", [])

        parts = []
        if scores:
            score_text = ", ".join(f"{k}: {v}" for k, v in scores.items())
            parts.append(f"评分: {score_text}")
        if skill_match.get("matched"):
            parts.append(f"匹配技能: {', '.join(skill_match['matched'])}")
        if skill_match.get("gap"):
            parts.append(f"差距技能: {', '.join(skill_match['gap'])}")
        if strengths:
            parts.append(f"优势: {', '.join(strengths[:3])}")
        if improvements:
            parts.append(f"改进: {', '.join(improvements[:2])}")
        if feedback:
            parts.append(f"反馈: {feedback}")
        return "\n".join(parts) if parts else "暂无评估数据"

    def _normalize_action(self, action_str: str) -> InterviewAction:
        """将 LLM 返回的 action 字符串规范化"""
        mapping = {
            "continue": InterviewAction.CONTINUE,
            "probe_deeper": InterviewAction.PROBE_DEEPER,
            "probe": InterviewAction.PROBE_DEEPER,
            "switch_topic": InterviewAction.SWITCH_TOPIC,
            "switch_role": InterviewAction.SWITCH_ROLE,
            "lower_difficulty": InterviewAction.LOWER_DIFFICULTY,
            "raise_difficulty": InterviewAction.RAISE_DIFFICULTY,
            "fill_gap": InterviewAction.FILL_GAP,
            "end_interview": InterviewAction.END_INTERVIEW,
            "end": InterviewAction.END_INTERVIEW,
        }
        return mapping.get(action_str.lower().strip(), InterviewAction.CONTINUE)

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

    def _get_fallback_decision(
        self,
        state: AdaptiveInterviewState,
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """LLM 失败时的备用决策"""

        # 有未验证的技能差距 → 填补
        if state.skill_gaps:
            action = InterviewAction.FILL_GAP
            directive = {
                "action": action.value,
                "target_skills": state.skill_gaps[:2],
                "difficulty": state.difficulty_level.value,
                "hint": f"请围绕 {', '.join(state.skill_gaps[:2])} 设计问题",
            }
        # 连续高分 → 提高难度
        elif state.consecutive_high >= 2:
            action = InterviewAction.RAISE_DIFFICULTY
            directive = {
                "action": action.value,
                "difficulty": min(5, state.difficulty_level.value + 1),
                "hint": "候选人表现优秀，提升难度",
            }
        # 连续低分 → 降低难度
        elif state.consecutive_low >= 2:
            action = InterviewAction.LOWER_DIFFICULTY
            directive = {
                "action": action.value,
                "difficulty": max(1, state.difficulty_level.value - 1),
                "hint": "候选人表现吃力，降低难度",
            }
        else:
            action = InterviewAction.CONTINUE
            directive = {
                "action": action.value,
                "difficulty": state.difficulty_level.value,
                "hint": "继续当前方向的提问",
            }

        state.last_action = action
        return {
            "action": action.value,
            "directive": directive,
            "reasoning": "基于规则的备用决策",
            "priority_gaps": state.skill_gaps[:3],
            "suggested_difficulty": directive.get("difficulty", state.difficulty_level.value),
            "suggested_role": state.current_role,
            "should_end": False,
        }
