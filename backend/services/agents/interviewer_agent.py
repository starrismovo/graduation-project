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
        job_info = job_info or {}
        resume_info = resume_info or {}
        decision_directive = decision_directive or {}
        interview_state_context = interview_state_context or {}
        role_meta = ROLE_META.get(role_id, ROLE_META["hr"])

        # 格式化对话历史
        history_text = self._format_history(conversation_history)

        # 格式化简历技能
        skills_raw = resume_info.get("skills", [])
        if isinstance(skills_raw, list):
            candidate_skills = ", ".join(skills_raw) if skills_raw else "未提供"
        else:
            candidate_skills = str(skills_raw) or "未提供"

        # 格式化岗位技能要求
        job_skills_raw = job_info.get("required_skills", job_info.get("skills", []))
        if isinstance(job_skills_raw, list):
            job_skills = ", ".join(job_skills_raw) if job_skills_raw else "未提供"
        else:
            job_skills = str(job_skills_raw) or "未提供"

        # 格式化决策指令
        directive_text = self._format_directive(decision_directive)

        # 格式化面试状态摘要
        verified_skills_text = self._format_verified_skills(interview_state_context)
        skill_gaps_text = ", ".join(interview_state_context.get("skill_gaps", [])) or "暂无"
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

            # 确保必要字段
            return {
                "question": result.get("question", ""),
                "intent": result.get("intent", "综合考察"),
                "difficulty": result.get("difficulty", "medium"),
                "resume_anchor": result.get("resume_anchor", ""),
                "tags": result.get("tags", []),
                "focus_area": result.get("focus_area", role_meta["focus_traits"][0]),
                "context": result.get("intent", ""),
                "expected_traits": role_meta["focus_traits"]
            }
        except Exception as e:
            logger.warning(
                "[InterviewerAgent] LLM 调用失败: type=%s repr=%r str=%s, 使用备用问题",
                type(e).__name__,
                e,
                str(e),
                exc_info=True,
            )
            return self._get_fallback(role_id, resume_info, depth)

    # ==================== 内部方法 ====================

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
            targets = directive.get("target_skills", [])
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
        for name, info in verified.items():
            if isinstance(info, dict):
                score = info.get("score", 0)
                verified_flag = "✓" if info.get("verified") else "?"
                parts.append(f"{name}({score:.1f}分{verified_flag})")
            else:
                parts.append(str(name))
        return ", ".join(parts) if parts else "暂无"

    def _get_fallback(
        self, role_id: str, resume_info: Dict[str, Any], depth: int
    ) -> Dict[str, Any]:
        """基于简历生成备用问题"""
        skills = resume_info.get("skills", [])
        name = resume_info.get("name", "你")

        if depth <= 2 and skills:
            skill = skills[0] if isinstance(skills, list) else str(skills).split(",")[0]
            question = f"我注意到你的简历中提到了 {skill}，能具体谈谈你在实际项目中是如何使用它的吗？"
            intent = "技能验证"
        elif depth <= 5:
            question = "能描述一个你在工作中遇到的最有挑战性的技术问题，以及你是如何解决的吗？"
            intent = "问题解决能力"
        else:
            question = "如果让你重新设计你参与过的最重要的项目，你会做出什么改变？为什么？"
            intent = "系统设计和反思能力"

        role_meta = ROLE_META.get(role_id, ROLE_META["hr"])
        return {
            "question": question,
            "intent": intent,
            "difficulty": "easy" if depth <= 2 else ("medium" if depth <= 6 else "hard"),
            "resume_anchor": "",
            "tags": [intent],
            "focus_area": role_meta["focus_traits"][0],
            "context": intent,
            "expected_traits": role_meta["focus_traits"],
        }
