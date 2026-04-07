"""
AdaptiveInterviewState - 自适应面试状态机
==========================================

职责：
  在整个面试过程中追踪候选人表现、技能验证进度和面试路径，
  为 DecisionAgent 提供决策依据。

状态维度：
  - verified_skills: 已验证的技能列表（含分数）
  - skill_gaps: 已识别的技能差距
  - performance_trend: 表现趋势（上升/稳定/下降）
  - difficulty_level: 当前难度等级 (1-5)
  - coverage_map: 已覆盖的考察维度
  - interview_path: 面试路径轨迹
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class DifficultyLevel(int, Enum):
    """难度等级"""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


class PerformanceTrend(str, Enum):
    """表现趋势"""
    RISING = "rising"          # 上升趋势
    STABLE = "stable"          # 稳定表现
    DECLINING = "declining"    # 下降趋势
    FLUCTUATING = "fluctuating"  # 波动


class InterviewAction(str, Enum):
    """决策动作类型"""
    CONTINUE = "continue"               # 继续当前方向
    PROBE_DEEPER = "probe_deeper"       # 深入追问
    SWITCH_TOPIC = "switch_topic"       # 切换话题
    SWITCH_ROLE = "switch_role"         # 切换面试官角色
    LOWER_DIFFICULTY = "lower_difficulty"  # 降低难度
    RAISE_DIFFICULTY = "raise_difficulty"  # 提高难度
    FILL_GAP = "fill_gap"              # 填补技能差距
    END_INTERVIEW = "end_interview"     # 结束面试


@dataclass
class SkillRecord:
    """技能验证记录"""
    skill_name: str
    score: float = 0.0          # 0-10
    evidence: str = ""           # 评分依据
    verified: bool = False       # 是否已充分验证
    question_count: int = 0      # 针对该技能的提问次数
    is_required: bool = False    # 是否为岗位必需技能


@dataclass
class TopicRecord:
    """话题覆盖记录"""
    topic: str
    questions_asked: int = 0
    avg_score: float = 0.0
    total_score: float = 0.0


@dataclass
class AdaptiveInterviewState:
    """自适应面试状态"""

    # ===== 技能追踪 =====
    verified_skills: Dict[str, SkillRecord] = field(default_factory=dict)
    skill_gaps: List[str] = field(default_factory=list)

    # ===== 表现追踪 =====
    score_history: List[float] = field(default_factory=list)
    performance_trend: PerformanceTrend = PerformanceTrend.STABLE
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    consecutive_high: int = 0   # 连续高分次数
    consecutive_low: int = 0    # 连续低分次数

    # ===== 覆盖追踪 =====
    coverage_map: Dict[str, TopicRecord] = field(default_factory=dict)
    topics_explored: List[str] = field(default_factory=list)

    # ===== 面试路径 =====
    interview_path: List[Dict[str, Any]] = field(default_factory=list)
    current_focus_skill: Optional[str] = None
    last_action: InterviewAction = InterviewAction.CONTINUE
    total_questions: int = 0
    current_role: str = "hr"

    def update_after_evaluation(
        self,
        evaluation_result: Dict[str, Any],
        question_info: Dict[str, Any],
    ) -> None:
        """根据评估结果更新状态"""

        self.total_questions += 1

        # 1. 更新分数历史与趋势
        scores = evaluation_result.get("scores", {})
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            self.score_history.append(avg_score)
            self._update_performance_trend(avg_score)
            self._update_difficulty(avg_score)

        # 2. 更新技能验证
        skill_match = evaluation_result.get("skill_match", {})
        matched = skill_match.get("matched", [])
        gaps = skill_match.get("gap", [])

        for skill in matched:
            if skill in self.verified_skills:
                record = self.verified_skills[skill]
                record.question_count += 1
                # 用最新评分加权更新
                skill_score = scores.get("技术深度", scores.get("问题解决", avg_score if scores else 6.0))
                record.total_score = (record.score * (record.question_count - 1) + skill_score) / record.question_count
                record.score = record.total_score
                if record.question_count >= 2 and record.score >= 6.0:
                    record.verified = True
            else:
                skill_score = scores.get("技术深度", avg_score if scores else 6.0)
                self.verified_skills[skill] = SkillRecord(
                    skill_name=skill,
                    score=skill_score,
                    question_count=1,
                    verified=skill_score >= 7.5,  # 高分直接验证
                )

        # 更新技能差距
        for gap_skill in gaps:
            if gap_skill not in self.skill_gaps:
                self.skill_gaps.append(gap_skill)
        # 如果之前的差距已被验证，移除
        self.skill_gaps = [
            g for g in self.skill_gaps
            if g not in self.verified_skills or not self.verified_skills[g].verified
        ]

        # 3. 更新话题覆盖
        focus_area = question_info.get("focus_area", "综合")
        if focus_area in self.coverage_map:
            topic = self.coverage_map[focus_area]
            topic.questions_asked += 1
            topic.total_score += avg_score if scores else 6.0
            topic.avg_score = topic.total_score / topic.questions_asked
        else:
            self.coverage_map[focus_area] = TopicRecord(
                topic=focus_area,
                questions_asked=1,
                total_score=avg_score if scores else 6.0,
                avg_score=avg_score if scores else 6.0,
            )

        if focus_area not in self.topics_explored:
            self.topics_explored.append(focus_area)

        # 4. 记录面试路径
        self.interview_path.append({
            "question_num": self.total_questions,
            "role": self.current_role,
            "focus_area": focus_area,
            "avg_score": avg_score if scores else 6.0,
            "difficulty": self.difficulty_level.value,
            "action": self.last_action.value,
        })

    def init_required_skills(self, job_skills: List[str]) -> None:
        """初始化岗位需求技能列表"""
        for skill in job_skills:
            if skill not in self.verified_skills:
                self.verified_skills[skill] = SkillRecord(
                    skill_name=skill,
                    is_required=True,
                )
            else:
                self.verified_skills[skill].is_required = True

    def get_unverified_required_skills(self) -> List[str]:
        """获取尚未验证的必需技能"""
        return [
            name for name, record in self.verified_skills.items()
            if record.is_required and not record.verified
        ]

    def get_weak_areas(self) -> List[str]:
        """获取薄弱领域（考察过但得分低）"""
        return [
            name for name, record in self.verified_skills.items()
            if record.question_count > 0 and record.score < 5.0
        ]

    def get_coverage_summary(self) -> Dict[str, Any]:
        """获取覆盖度摘要"""
        total_required = sum(1 for r in self.verified_skills.values() if r.is_required)
        verified_required = sum(
            1 for r in self.verified_skills.values()
            if r.is_required and r.verified
        )
        return {
            "total_required_skills": total_required,
            "verified_required_skills": verified_required,
            "coverage_rate": verified_required / total_required if total_required > 0 else 0.0,
            "topics_explored": len(self.topics_explored),
            "total_questions": self.total_questions,
            "skill_gaps": self.skill_gaps[:],
            "unverified": self.get_unverified_required_skills(),
        }

    def to_context_dict(self) -> Dict[str, Any]:
        """转换为可传递给 Prompt / 前端的字典"""
        return {
            "verified_skills": {
                name: {"score": r.score, "verified": r.verified, "count": r.question_count}
                for name, r in self.verified_skills.items()
            },
            "skill_gaps": self.skill_gaps[:],
            "performance_trend": self.performance_trend.value,
            "difficulty_level": self.difficulty_level.value,
            "score_history": self.score_history[-10:],  # 最近 10 轮
            "topics_explored": self.topics_explored[:],
            "total_questions": self.total_questions,
            "current_role": self.current_role,
            "current_focus_skill": self.current_focus_skill,
            "last_action": self.last_action.value,
            "coverage": self.get_coverage_summary(),
        }

    # ==================== 内部方法 ====================

    def _update_performance_trend(self, latest_score: float) -> None:
        """更新表现趋势"""
        if latest_score >= 7.0:
            self.consecutive_high += 1
            self.consecutive_low = 0
        elif latest_score < 5.0:
            self.consecutive_low += 1
            self.consecutive_high = 0
        else:
            self.consecutive_high = 0
            self.consecutive_low = 0

        if len(self.score_history) < 3:
            self.performance_trend = PerformanceTrend.STABLE
            return

        recent_3 = self.score_history[-3:]
        trend_diff = recent_3[-1] - recent_3[0]

        if trend_diff > 1.0:
            self.performance_trend = PerformanceTrend.RISING
        elif trend_diff < -1.0:
            self.performance_trend = PerformanceTrend.DECLINING
        elif max(recent_3) - min(recent_3) > 2.0:
            self.performance_trend = PerformanceTrend.FLUCTUATING
        else:
            self.performance_trend = PerformanceTrend.STABLE

    def _update_difficulty(self, latest_score: float) -> None:
        """自动调整难度"""
        if self.consecutive_high >= 2 and self.difficulty_level.value < 5:
            self.difficulty_level = DifficultyLevel(self.difficulty_level.value + 1)
            self.consecutive_high = 0
        elif self.consecutive_low >= 2 and self.difficulty_level.value > 1:
            self.difficulty_level = DifficultyLevel(self.difficulty_level.value - 1)
            self.consecutive_low = 0
