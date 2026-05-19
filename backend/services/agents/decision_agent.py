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
import re
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

TOPIC_SWITCH_ORDER = ["产品思维", "用户研究", "沟通能力", "团队协作", "情绪稳定性", "尽责性", "开放性", "领导力"]

# 角色转换规则
ROLE_TRANSITION = {
    "hr": "tech_lead",
    "tech_lead": "product",
    "product": "cto",
    "cto": "cto",  # CTO 是最终角色
}

# 每个角色的建议提问轮数
ROLE_QUESTION_BUDGET = {
    "hr": 2,
    "tech_lead": 2,
    "product": 2,
    "cto": 1,
}

PSYCHOLOGICAL_TOPICS = {"尽责性", "开放性", "团队协作", "压力应对", "情绪稳定性", "职业动机"}


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
        allow_llm: bool = False,
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

        if not allow_llm:
            decision = self._get_fast_rule_decision(interview_state, evaluation_result)
            logger.info(f"[DecisionAgent] 快速规则决策: {decision['action']}")
            return decision

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

        depth_assessment = evaluation.get("depth_assessment", {}) or {}
        answer_depth = depth_assessment.get("answer_depth")
        specificity = depth_assessment.get("specificity")
        missing_personality_traits = state.get_missing_personality_traits()
        coverage = state.get_coverage_summary()
        missing_must_have = [
            str(skill).strip()
            for skill in (evaluation.get("missing_must_have_skills") or [])
            if str(skill).strip()
        ]
        skill_match = evaluation.get("skill_match", {}) or {}
        needs_verification = [
            str(skill).strip()
            for skill in (skill_match.get("needs_verification") or [])
            if str(skill).strip()
        ]
        recent_topics = [
            step.get("focus_area")
            for step in state.interview_path[-2:]
            if step.get("focus_area")
        ]
        if self._recent_focus_or_tags_repeated(state) and state.total_questions < max_questions - 1:
            topic = self._next_uncovered_topic(state)
            return {
                "action": InterviewAction.SWITCH_TOPIC.value,
                "directive": {
                    "new_topic": topic,
                    "reason": "最近两轮 focus_area 或核心 tags 重复",
                    "hint": f"请强制切换到{topic}，不要继续围绕上一题的同一能力点或同一项目追问",
                },
                "reasoning": "最近两轮考察维度高度相似，为避免重复提问，优先切换到未覆盖维度",
                "priority_gaps": state.skill_gaps[:2],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则1.1：岗位必备技能缺失优先补齐，避免只围绕心理特质追问
        if missing_must_have:
            return {
                "action": InterviewAction.FILL_GAP.value,
                "directive": {
                    "target_skills": missing_must_have[:2],
                    "reason": "岗位必备技能证据不足",
                    "hint": f"请围绕岗位必备技能 {', '.join(missing_must_have[:2])} 设计一个真实工作情境问题，并要求候选人说明具体做法和结果",
                },
                "reasoning": "本轮回答未能证明岗位必备技能，下一轮优先验证硬性岗位要求",
                "priority_gaps": missing_must_have[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则1.2：岗位必需技能覆盖率不足时优先验证未覆盖技能
        unverified_required = coverage.get("unverified", [])
        if (
            coverage.get("total_required_skills", 0) > 0
            and coverage.get("coverage_rate", 0.0) < 0.6
            and unverified_required
            and state.total_questions < max_questions - 1
        ):
            targets = unverified_required[:2]
            return {
                "action": InterviewAction.FILL_GAP.value,
                "directive": {
                    "target_skills": targets,
                    "reason": "岗位核心技能覆盖率不足",
                    "hint": f"请优先验证 {', '.join(targets)}，问题要贴合岗位真实任务，不要泛泛询问掌握程度",
                },
                "reasoning": f"当前必需技能覆盖率仅 {coverage.get('coverage_rate', 0.0):.0%}，需要先补齐岗位硬性能力证据",
                "priority_gaps": targets,
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则1.3：Evaluator 明确标记待验证技能时，优先形成证据链
        if needs_verification and state.total_questions < max_questions - 1:
            return {
                "action": InterviewAction.FILL_GAP.value,
                "directive": {
                    "target_skills": needs_verification[:2],
                    "reason": "存在待验证岗位技能",
                    "hint": f"请围绕 {', '.join(needs_verification[:2])} 追问候选人的真实项目行为、工具使用和结果指标",
                },
                "reasoning": "EvaluatorAgent 标记了待验证技能，下一题用于补充技能证据链",
                "priority_gaps": needs_verification[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则1.35：同一案例最多连续追问 2 轮，第三轮强制切换考察维度
        if self._same_case_depth(state) >= 3 and state.total_questions < max_questions - 1:
            topic = self._next_switch_topic(state)
            return {
                "action": InterviewAction.SWITCH_TOPIC.value,
                "directive": {
                    "new_topic": topic,
                    "reason": "同一项目或业务案例已连续追问超过2轮",
                    "hint": f"请切换到{topic}，围绕新的岗位任务或新的心理特质情境提问，避免继续追问上一案例",
                },
                "reasoning": "为保证 8 轮面试覆盖更多岗位能力与 Scenario Personality 证据，当前需要跳出上一案例",
                "priority_gaps": state.skill_gaps[:2],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则1.4：连续低信息回答 → 结束，避免重复追问
        if state.low_info_streak >= 2 and state.total_questions >= 4:
            return {
                "action": InterviewAction.END_INTERVIEW.value,
                "directive": {"reason": "候选人连续低信息回答，继续追问收益较低"},
                "reasoning": "已获得部分评估样本，候选人连续简短回答，结束面试并基于既有证据生成结果",
                "priority_gaps": state.skill_gaps[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": True,
            }

        # 规则1.45：单次低信息回答 → 降低难度，换成更贴近岗位的简单情境题
        if state.low_info_streak >= 1:
            return {
                "action": InterviewAction.SWITCH_TOPIC.value,
                "directive": {
                    "new_topic": "销售场景适应性",
                    "reason": "候选人回答信息量较低，降低难度并改用具体销售情境",
                    "hint": "请用更简单的互联网销售情境提问，允许候选人从校园推广、兼职、社团拉新等经历回答",
                },
                "reasoning": "候选人近期回答较短，先降低问题抽象度，观察基础沟通意愿和销售场景适应性",
                "priority_gaps": state.skill_gaps[:2],
                "suggested_difficulty": 1,
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则1.5：低信息回答且已覆盖一定轮次 → 结束，避免反复追问造成体验下降
        if (
            state.total_questions >= 6
            and (answer_depth == "shallow" or specificity in {"vague", "general"})
            and state.get_personality_coverage_rate() >= 0.6
        ):
            return {
                "action": InterviewAction.END_INTERVIEW.value,
                "directive": {"reason": "已获得足够样本，候选人近期回答信息量较低"},
                "reasoning": "已完成多轮技能与行为样本采集，继续追问收益较低，结束面试并生成评估结果",
                "priority_gaps": state.skill_gaps[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": True,
            }

        # 规则1.6：至少完成 7 轮后结束，保证前端不会长时间等待下一题
        if state.total_questions >= 7 and state.get_personality_coverage_rate() >= 0.6:
            return {
                "action": InterviewAction.END_INTERVIEW.value,
                "directive": {"reason": "已达到建议评估轮次"},
                "reasoning": "已完成建议评估轮次，进入报告生成阶段",
                "priority_gaps": state.skill_gaps[:3],
                "suggested_difficulty": state.difficulty_level.value,
                "suggested_role": state.current_role,
                "should_end": True,
            }

        # 规则2：心理特质覆盖不足时，只在必要时补问；避免把面试变成大五维度清单
        missing_personality_traits = [
            trait for trait in missing_personality_traits
            if trait not in recent_topics
        ]
        if (
            state.total_questions >= 3
            and missing_personality_traits
            and answer_depth != "deep"
        ):
            topic = missing_personality_traits[0]
            return {
                "action": InterviewAction.SWITCH_TOPIC.value,
                "directive": {
                    "new_topic": topic,
                    "reason": "大五人格维度证据不足，补充心理特质评估",
                    "hint": f"请基于候选人上一回答继续追问，并在问题中观察{topic}；不要脱离上下文另起一个泛化题",
                },
                "reasoning": f"当前缺少{topic}的人格证据，需要补齐 Scenario Personality 评估链路",
                "priority_gaps": state.skill_gaps[:2],
                "suggested_difficulty": max(1, state.difficulty_level.value - 1),
                "suggested_role": state.current_role,
                "should_end": False,
            }

        # 规则3：所有必需技能已验证 + 已问足够多 → 结束
        if (
            coverage["coverage_rate"] >= 0.9
            and coverage["personality_coverage_rate"] >= 0.6
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

        # 规则4：当前角色提问轮数耗尽 → 切换角色
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

        # 规则5：连续围绕同一主题时，切换到心理特质/行为情境，避免单点纠缠
        if len(recent_topics) >= 2 and len(set(recent_topics)) == 1:
            topic = self._next_psychological_topic(state)
            return {
                "action": InterviewAction.SWITCH_TOPIC.value,
                "directive": {
                    "new_topic": topic,
                    "reason": "连续追问同一主题，切换到心理特质观察",
                    "hint": f"请转向{topic}相关的行为情境问题，不再继续追问同一技术细节",
                },
                "reasoning": "为体现心理特质评估，避免连续围绕单一技能点追问",
                "priority_gaps": state.skill_gaps[:2],
                "suggested_difficulty": max(1, state.difficulty_level.value - 1),
                "suggested_role": state.current_role,
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
            missing_must_have = evaluation_result.get("missing_must_have_skills") or []
            needs_verification = (evaluation_result.get("skill_match") or {}).get("needs_verification") or []
            gaps = list(dict.fromkeys(
                [str(s) for s in missing_must_have if str(s).strip()]
                + [str(s) for s in interview_state.skill_gaps[:2] if str(s).strip()]
                + [str(s) for s in needs_verification if str(s).strip()]
            ))[:2]
            base_directive["target_skills"] = gaps
            base_directive["hint"] = f"候选人在以下技能存在差距: {', '.join(gaps)}，请设计验证问题"

        elif action == InterviewAction.SWITCH_TOPIC:
            # 切换话题指令
            explored = set(interview_state.topics_explored)
            all_topics = {"技术深度", "问题解决", "团队协作", "产品思维", "系统设计", "领导力", "尽责性", "开放性", "压力应对", "情绪稳定性", "职业动机"}
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

    def _next_psychological_topic(self, state: AdaptiveInterviewState) -> str:
        explored = set(state.topics_explored)
        for topic in ["尽责性", "开放性", "团队协作", "压力应对", "情绪稳定性", "职业动机"]:
            if topic not in explored:
                return topic
        return "综合心理特质"

    def _recent_focus_or_tags_repeated(self, state: AdaptiveInterviewState) -> bool:
        recent = state.interview_path[-2:]
        if len(recent) < 2:
            return False
        focus = [str(step.get("focus_area") or "").strip() for step in recent]
        if focus[0] and focus[0] == focus[1]:
            return True
        tag_sets = []
        for step in recent:
            tags = {
                str(tag).strip()
                for tag in (step.get("tags") or [])
                if str(tag).strip()
            }
            tag_sets.append(tags)
        if not tag_sets[0] or not tag_sets[1]:
            return False
        overlap = len(tag_sets[0] & tag_sets[1]) / max(len(tag_sets[0]), len(tag_sets[1]))
        return overlap >= 0.6

    def _next_uncovered_topic(self, state: AdaptiveInterviewState) -> str:
        recent_topics = {
            str(step.get("focus_area") or "").strip()
            for step in state.interview_path[-3:]
            if str(step.get("focus_area") or "").strip()
        }
        for trait in state.get_missing_personality_traits():
            if trait not in recent_topics:
                return trait
        explored = set(state.topics_explored)
        for topic in TOPIC_SWITCH_ORDER:
            if topic not in explored and topic not in recent_topics:
                return topic
        for skill in state.get_unverified_required_skills():
            if skill not in recent_topics:
                return skill
        return "综合行为情境"

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
        if evaluation.get("verified_skills"):
            parts.append(f"已验证技能证据: {', '.join(evaluation['verified_skills'])}")
        if evaluation.get("missing_must_have_skills"):
            parts.append(f"缺失必备技能: {', '.join(evaluation['missing_must_have_skills'])}")
        if evaluation.get("evidence_quote"):
            parts.append(f"关键原话: {evaluation['evidence_quote']}")
        if strengths:
            parts.append(f"优势: {', '.join(strengths[:3])}")
        if improvements:
            parts.append(f"改进: {', '.join(improvements[:2])}")
        if feedback:
            parts.append(f"反馈: {feedback}")
        personality = evaluation.get("personality_observation")
        if personality:
            parts.append(f"心理特质观察: {json.dumps(personality, ensure_ascii=False)}")
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

    def _same_case_depth(self, state: AdaptiveInterviewState) -> int:
        """估算是否连续围绕同一案例追问，避免 8 题都陷在一个项目里。"""
        recent = state.interview_path[-3:]
        if len(recent) < 3:
            return 0

        focus_areas = [str(step.get("focus_area") or "").strip() for step in recent]
        if focus_areas and max(focus_areas.count(item) for item in set(focus_areas)) >= 3:
            return 3

        questions = [str(step.get("question") or "") for step in recent]
        quote_anchors: List[str] = []
        for question in questions:
            quote_anchors.extend([
                item.strip()
                for item in re.findall(r"[“\"']([^”\"']{4,30})[”\"']", question)
                if item.strip()
            ])
        for anchor in quote_anchors:
            if sum(1 for question in questions if anchor in question) >= 2:
                return 3

        shared_case_words = [
            "刚才", "提到", "这个案例", "上述案例", "回到", "在这个基础上",
            "协作启动", "空白页面", "留存率", "漏斗分析",
        ]
        if sum(1 for question in questions if any(word in question for word in shared_case_words)) >= 3:
            return 3

        return 0

    def _next_switch_topic(self, state: AdaptiveInterviewState) -> str:
        explored = set(state.topics_explored[-5:])
        for topic in TOPIC_SWITCH_ORDER:
            if topic not in explored:
                return topic
        return "岗位必备能力验证"

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

    def _get_fast_rule_decision(
        self,
        state: AdaptiveInterviewState,
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """One-call interview mode: no LLM, only route by state and evaluation."""
        next_action = str(evaluation.get("next_action") or "continue").strip()
        missing_must_have = [
            str(skill).strip()
            for skill in (evaluation.get("missing_must_have_skills") or [])
            if str(skill).strip()
        ]
        skill_match = evaluation.get("skill_match", {}) or {}
        needs_verification = [
            str(skill).strip()
            for skill in (skill_match.get("needs_verification") or [])
            if str(skill).strip()
        ]
        coverage = state.get_coverage_summary()

        if missing_must_have:
            action = InterviewAction.FILL_GAP
            directive = {
                "action": action.value,
                "target_skills": missing_must_have[:2],
                "difficulty": state.difficulty_level.value,
                "hint": f"请优先验证岗位必备技能: {', '.join(missing_must_have[:2])}",
                "reason": "岗位必备技能证据不足",
            }
        elif coverage.get("total_required_skills", 0) > 0 and coverage.get("coverage_rate", 0.0) < 0.6 and coverage.get("unverified"):
            action = InterviewAction.FILL_GAP
            targets = coverage.get("unverified", [])[:2]
            directive = {
                "action": action.value,
                "target_skills": targets,
                "difficulty": state.difficulty_level.value,
                "hint": f"请优先验证尚未覆盖的岗位技能: {', '.join(targets)}",
                "reason": "岗位技能覆盖率不足",
            }
        elif needs_verification:
            action = InterviewAction.FILL_GAP
            directive = {
                "action": action.value,
                "target_skills": needs_verification[:2],
                "difficulty": state.difficulty_level.value,
                "hint": f"请补充验证技能证据: {', '.join(needs_verification[:2])}",
                "reason": "EvaluatorAgent 标记存在待验证技能",
            }
        elif self._same_case_depth(state) >= 3:
            action = InterviewAction.SWITCH_TOPIC
            topic = self._next_switch_topic(state)
            directive = {
                "action": action.value,
                "new_topic": topic,
                "difficulty": state.difficulty_level.value,
                "hint": f"请切换到{topic}，不要继续追问上一项目或业务案例",
                "reason": "同一案例连续追问超过2轮",
            }
        elif next_action == "switch_role" and state.current_role != "cto":
            next_role = ROLE_TRANSITION.get(state.current_role, "cto")
            state.current_role = next_role
            action = InterviewAction.SWITCH_ROLE
            directive = {
                "action": action.value,
                "new_role": next_role,
                "difficulty": state.difficulty_level.value,
                "hint": f"切换面试官至 {next_role}",
            }
        elif state.skill_gaps:
            action = InterviewAction.FILL_GAP
            directive = {
                "action": action.value,
                "target_skills": state.skill_gaps[:2],
                "difficulty": state.difficulty_level.value,
                "hint": f"请围绕 {', '.join(state.skill_gaps[:2])} 设计问题",
            }
        else:
            action = InterviewAction.CONTINUE
            directive = {
                "action": action.value,
                "difficulty": state.difficulty_level.value,
                "hint": evaluation.get("follow_up_hint", "继续补充评估证据"),
            }
        state.last_action = action
        return {
            "action": action.value,
            "directive": directive,
            "reasoning": "基于技能覆盖率、必备技能缺口与心理特质证据覆盖度进行路径控制",
            "priority_gaps": state.skill_gaps[:3],
            "suggested_difficulty": state.difficulty_level.value,
            "suggested_role": state.current_role,
            "should_end": False,
        }
