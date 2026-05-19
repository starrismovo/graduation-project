"""
Report Agent service.

Encapsulates report-oriented analysis generation so router code only orchestrates
pipeline steps and persistence.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from models.assessment import CandidatePersonalityProfile
from models.job import Job
from services.personality_scoring import normalize_big_five_scores


class ReportAgent:
    """Builds strengths, gaps, and recommendations for assessment reports."""

    TRAIT_CONFIG = [
        {
            "field": "trait_extroversion",
            "key": "extraversion",
            "label": "外向性",
            "description": "反映候选人在沟通表达、社交互动与主动协同中的倾向。",
            "high_summary": "在需要访谈、表达和跨团队沟通的场景中更容易建立互动。",
            "low_summary": "在独立思考和深度分析任务中可能更稳定，但高频外部沟通场景需要额外适应。",
            "advice": "可通过结构化表达训练和情境模拟提升面试与跨部门沟通表现。",
        },
        {
            "field": "trait_agreeableness",
            "key": "agreeableness",
            "label": "宜人性",
            "description": "反映候选人在合作意愿、同理心与关系协调方面的稳定倾向。",
            "high_summary": "在用户洞察、团队协作和需求对齐场景中更容易建立信任。",
            "low_summary": "更容易保持独立判断，但在协商和冲突协调场景中需要加强柔性沟通。",
            "advice": "可通过复盘协作场景，训练需求澄清和冲突协调能力。",
        },
        {
            "field": "trait_conscientiousness",
            "key": "conscientiousness",
            "label": "尽责性",
            "description": "反映候选人在任务执行、计划管理与结果交付方面的稳定程度。",
            "high_summary": "更适合承担执行链条长、交付要求明确的岗位任务。",
            "low_summary": "在灵活探索场景中可能更有弹性，但需要补足计划性与落地性。",
            "advice": "建议通过周计划、里程碑拆解和复盘机制提升稳定交付能力。",
        },
        {
            "field": "trait_neuroticism",
            "key": "neuroticism",
            "label": "神经质",
            "description": "反映候选人在压力、变化与不确定情境下的情绪波动程度。",
            "high_summary": "面对高压反馈或频繁变化场景时，可能更容易出现紧张和波动。",
            "low_summary": "在复杂和高压环境中通常更稳定，更有利于持续判断与沟通。",
            "advice": "建议通过压力情境演练、情绪记录和节奏管理提升稳定性。",
        },
        {
            "field": "trait_openness",
            "key": "openness",
            "label": "开放性",
            "description": "反映候选人在新信息吸收、抽象思考与创新尝试方面的倾向。",
            "high_summary": "在用户研究、产品创新和跨学科协同场景中更容易形成新思路。",
            "low_summary": "在标准化执行场景中可能更稳健，但面对探索型任务时需要主动拓展视角。",
            "advice": "建议通过案例拆解、跨领域阅读和需求分析训练提升探索深度。",
        },
    ]

    ROLE_CATEGORIES = {
        "research": ("用户研究与洞察类岗位", ["研究", "用户", "内容", "策划", "产品"]),
        "delivery": ("执行与项目推进类岗位", ["运营", "项目", "交付", "实施", "管理"]),
        "creative": ("创意与体验设计类岗位", ["设计", "体验", "产品", "策划", "内容"]),
    }

    @staticmethod
    def _coerce_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _coerce_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    @classmethod
    def _trait_requirement_map(cls, job: Optional[Job]) -> Dict[str, float]:
        if not job:
            return {}

        raw = cls._coerce_dict(getattr(job, "required_traits", None))
        if not raw:
            raw = cls._coerce_dict(getattr(job, "personality_requirements", None))
            raw = cls._coerce_dict(raw.get("generated_big_five")) or raw

        aliases = {
            "外向性": "extraversion",
            "extroversion": "extraversion",
            "extraversion": "extraversion",
            "宜人性": "agreeableness",
            "agreeableness": "agreeableness",
            "尽责性": "conscientiousness",
            "conscientiousness": "conscientiousness",
            "神经质": "neuroticism",
            "neuroticism": "neuroticism",
            "情绪稳定性": "neuroticism",
            "emotional_stability": "neuroticism",
            "开放性": "openness",
            "openness": "openness",
        }

        requirements: Dict[str, float] = {}
        for raw_key, raw_value in normalize_big_five_scores(raw).items():
            key = aliases.get(str(raw_key).strip())
            if not key:
                continue
            requirements[key] = max(0.0, min(10.0, cls._coerce_float(raw_value, 0.0)))
        return requirements

    @classmethod
    def _build_trait_insights(
        cls,
        profile: CandidatePersonalityProfile,
        job: Optional[Job],
    ) -> List[Dict[str, Any]]:
        requirements = cls._trait_requirement_map(job)
        insights: List[Dict[str, Any]] = []

        for config in cls.TRAIT_CONFIG:
            score = getattr(profile, config["field"], None)
            if score is None:
                continue

            score = round(float(score), 1)
            requirement = requirements.get(config["key"])

            if config["key"] == "neuroticism":
                if requirement is None:
                    match_status = "balanced" if score <= 5.5 else "watch"
                elif score <= requirement + 0.6:
                    match_status = "aligned"
                elif score <= requirement + 1.5:
                    match_status = "watch"
                else:
                    match_status = "gap"
            else:
                if requirement is None:
                    match_status = "balanced" if 4.5 <= score <= 7.5 else "watch"
                elif score >= requirement - 0.6:
                    match_status = "aligned"
                elif score >= requirement - 1.5:
                    match_status = "watch"
                else:
                    match_status = "gap"

            if match_status == "aligned":
                summary = f"{config['label']}表现与当前岗位要求较为一致。{config['high_summary'] if score >= 6 else config['low_summary']}"
            elif match_status == "watch":
                summary = f"{config['label']}基本能够支撑当前岗位，但在高强度场景下仍存在一定波动空间。"
            elif match_status == "gap":
                summary = f"{config['label']}与当前岗位的人格期望存在差距，可能影响关键情境下的稳定表现。"
            else:
                summary = f"{config['label']}整体处于相对均衡区间，可结合具体岗位情境进一步观察。"

            insights.append({
                "name": config["label"],
                "score": score,
                "description": config["description"],
                "job_requirement": round(requirement, 1) if requirement is not None else None,
                "match_status": match_status,
                "summary": summary,
                "advice": config["advice"],
            })

        return insights

    @classmethod
    def _build_career_recommendations(
        cls,
        profile: CandidatePersonalityProfile,
        job: Optional[Job],
        trait_insights: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, str]]]:
        job_name = getattr(job, "name", "当前岗位")
        job_text = f"{getattr(job, 'name', '')} {getattr(job, 'category', '')} {getattr(job, 'description', '')}".lower()
        extraversion = getattr(profile, "trait_extroversion", None)
        agreeableness = getattr(profile, "trait_agreeableness", None)
        conscientiousness = getattr(profile, "trait_conscientiousness", None)
        openness = getattr(profile, "trait_openness", None)
        neuroticism = getattr(profile, "trait_neuroticism", None)

        current_fit = "建议优先尝试"
        aligned_count = sum(1 for item in trait_insights if item["match_status"] == "aligned")
        gap_count = sum(1 for item in trait_insights if item["match_status"] == "gap")
        if any(item["match_status"] == "gap" for item in trait_insights):
            current_fit = "可作为发展方向"
        if aligned_count >= 4:
            current_fit = "高度建议优先"

        recommendations = [
            {
                "title": f"{job_name}岗位方向",
                "fit_level": current_fit,
                "reason": "当前评估显示，你的人格结构与该岗位的核心情境存在较明确的对应关系，适合继续围绕该方向积累面试与项目证据。",
                "action": "建议优先补足报告中提示的薄弱维度，再进行下一轮针对性岗位投递。",
            }
        ]

        if openness is not None and agreeableness is not None and openness >= 7 and agreeableness >= 6.5:
            recommendations.append({
                "title": "研究与洞察类岗位",
                "fit_level": "较为适合",
                "reason": "开放性与宜人性较高，通常更适合需要用户理解、信息整合与跨角色协同的岗位情境。",
                "action": "可优先关注用户研究、产品研究、内容策划等强调洞察与沟通的岗位模板。",
            })
        elif conscientiousness is not None and neuroticism is not None and conscientiousness >= 7 and neuroticism <= 5.5:
            recommendations.append({
                "title": "执行与交付类岗位",
                "fit_level": "较为适合",
                "reason": "尽责性较高且情绪稳定性较好，更容易在目标明确、交付要求清晰的岗位中保持稳定表现。",
                "action": "可关注项目推进、运营实施、流程管理等强调执行闭环的岗位方向。",
            })
        else:
            recommendations.append({
                "title": "复合能力培养方向",
                "fit_level": "建议逐步探索",
                "reason": "当前人格表现较为均衡，但尚未在单一岗位方向上形成非常突出的稳定优势。",
                "action": "建议先围绕一个核心岗位方向补足案例，再逐步拓展到相邻岗位实例。",
            })

        if "研究" in job_text or "用户" in job_text or "产品" in job_text:
            recommendations.append({
                "title": "当前岗位的成长重点",
                "fit_level": "针对性建议",
                "reason": "该岗位更重视洞察、协同与表达链路，因此人格优势需要通过真实案例和结构化表达转化为岗位胜任力。",
                "action": "准备2到3个完整案例，重点说明问题定义、证据收集、结论形成和跨团队沟通过程。",
            })
        else:
            recommendations.append({
                "title": "岗位适配拓展建议",
                "fit_level": "针对性建议",
                "reason": "除人格匹配外，当前岗位适配度还取决于你能否把已有特质转化为岗位语言和场景化成果。",
                "action": "建议围绕目标岗位补充作品、项目或STAR案例，增强评估中的情境说服力。",
            })

        cautious_recommendations: List[Dict[str, str]] = []
        if extraversion is not None and agreeableness is not None and extraversion <= 5 and agreeableness <= 5.5:
            cautious_recommendations.append({
                "title": "高频外联与强销售导向岗位",
                "fit_level": "不建议优先投递",
                "reason": "当前人格结构在持续陌生沟通、强说服和高频关系推进场景中可能适应成本较高。",
                "action": "如果确需尝试，建议先通过模拟沟通、案例表达训练与真实外联实践补足证据。",
            })
        if openness is not None and openness <= 5.5 and "创新" in job_text:
            cautious_recommendations.append({
                "title": "高探索与强创新要求岗位",
                "fit_level": "不建议优先投递",
                "reason": "当前开放性表现偏稳健，面对高度模糊和持续探索的岗位情境时，可能需要更长适应周期。",
                "action": "建议先积累跨领域分析、需求拆解和创新案例，再逐步尝试相关岗位实例。",
            })
        if conscientiousness is not None and conscientiousness <= 5.5 and ("项目" in job_text or "交付" in job_text or "运营" in job_text):
            cautious_recommendations.append({
                "title": "强节奏交付与流程推进岗位",
                "fit_level": "不建议优先投递",
                "reason": "当前尽责性表现尚未形成稳定优势，面对多任务并行和严格节点要求时可能压力较大。",
                "action": "建议先通过项目管理、小型交付任务和周期复盘提升稳定执行能力。",
            })
        if neuroticism is not None and neuroticism >= 6.5:
            cautious_recommendations.append({
                "title": "高压与高不确定性岗位",
                "fit_level": "不建议优先投递",
                "reason": "当前在压力和变化情境下的情绪稳定性仍需加强，过早进入高压岗位可能影响发挥。",
                "action": "建议先在相对可控的岗位情境中积累节奏管理经验，再考虑高压岗位方向。",
            })
        if gap_count >= 3:
            cautious_recommendations.append({
                "title": "与当前人格画像偏差较大的岗位方向",
                "fit_level": "不建议优先投递",
                "reason": "当前多个人格维度与岗位情境要求存在明显差距，短期内直接投递成功率可能有限。",
                "action": "建议优先选择相邻岗位模板，在提升关键维度后再回到目标方向。",
            })

        if not cautious_recommendations:
            cautious_recommendations.append({
                "title": "暂不设明确回避方向",
                "fit_level": "可谨慎拓展",
                "reason": "当前人格结构整体较均衡，暂未出现需要明确回避的岗位方向，但仍需结合真实技能与履历判断。",
                "action": "建议优先投递与本次报告推荐方向一致的岗位实例，并逐步拓展相邻方向。",
            })

        return {
            "recommended": recommendations,
            "cautious": cautious_recommendations,
        }

    @classmethod
    def _build_development_actions(cls, trait_insights: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        if not trait_insights:
            return []

        priority = sorted(
            trait_insights,
            key=lambda item: (
                0 if item["match_status"] == "gap" else 1 if item["match_status"] == "watch" else 2,
                item["score"],
            ),
        )[:3]

        phase_labels = ["近期", "中期", "持续"]
        actions: List[Dict[str, str]] = []
        for idx, insight in enumerate(priority):
            actions.append({
                "phase": phase_labels[idx] if idx < len(phase_labels) else "持续",
                "title": f"围绕{insight['name']}制定提升动作",
                "description": insight.get("advice") or "建议通过复盘、训练和情境模拟逐步提升该维度在岗位场景中的表现。",
            })
        return actions

    @staticmethod
    def generate_analysis(analysis_type: str, profile: CandidatePersonalityProfile) -> List[str]:
        if analysis_type == "strengths":
            analysis: List[str] = []
            if profile.trait_conscientiousness and profile.trait_conscientiousness >= 7:
                analysis.append("责任心强，执行力强")
            if profile.trait_openness and profile.trait_openness >= 7:
                analysis.append("思维开放，学习能力强")
            if profile.trait_extroversion and profile.trait_extroversion >= 7:
                analysis.append("沟通能力强，团队协作意识强")
            if profile.trait_agreeableness and profile.trait_agreeableness >= 7:
                analysis.append("同理心强，合作意识强")
            if not analysis:
                analysis.append("表现均衡，基础素质扎实")
            return analysis

        analysis = []
        if not profile.trait_conscientiousness or profile.trait_conscientiousness < 6:
            analysis.append("需要提升执行力和自律性")
        if not profile.trait_openness or profile.trait_openness < 6:
            analysis.append("建议加强学习心态和创新意识")
        if not profile.trait_extroversion or profile.trait_extroversion < 6:
            analysis.append("可以加强沟通和表达能力")
        if not profile.trait_neuroticism or profile.trait_neuroticism < 5:
            analysis.append("需要加强压力管理和情绪控制")
        if not analysis:
            analysis.append("继续保持和完善各项能力")
        return analysis

    @staticmethod
    def generate_recommendations(profile: CandidatePersonalityProfile, job: Job) -> List[str]:
        recommendations = [
            "根据评估结果，建议职业发展方向明确",
            "持续提升专业技能，增强岗位胜任力",
        ]

        if job.category and "engineer" in job.category.lower():
            recommendations.append("建议参加技术领导力或架构设计培训")
        elif job.category and "product" in job.category.lower():
            recommendations.append("建议加强用户研究和数据分析能力")
        elif job.category and "manager" in job.category.lower():
            recommendations.append("建议参加团队领导力或项目管理培训")
        else:
            recommendations.append("建议参加相关领域的专业培训课程")

        recommendations.append("定期反思和改进，制定个人发展计划")
        return recommendations

    def build_report_sections(
        self,
        *,
        profile: CandidatePersonalityProfile,
        job: Optional[Job],
        match_breakdown: Dict[str, float],
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        evidence = evidence or {}
        trait_insights = self._build_trait_insights(profile, job)
        career_advice = self._build_career_recommendations(profile, job, trait_insights)
        career_recommendations = career_advice["recommended"]
        cautious_career_recommendations = career_advice["cautious"]
        development_actions = self._build_development_actions(trait_insights)
        weights = match_breakdown.get("weights") or {}
        hard_skill_gate = match_breakdown.get("hard_skill_gate") or {}
        gate_reason = str(hard_skill_gate.get("reason") or "").strip()

        overview_summary = (
            f"本次评估显示，你与“{getattr(job, 'name', '目标岗位')}”的整体匹配度为"
            f"{round(self._coerce_float(match_breakdown.get('overall_score', 50.0)), 1)}%，"
            "该结果由技能匹配、人格匹配与多Agent评估证据综合形成。"
        )
        if hard_skill_gate.get("applied") and gate_reason:
            overview_summary += f"由于{gate_reason}，系统触发了硬技能封顶机制。"
        personality_summary = "报告从大五人格视角解释你在当前岗位情境中的稳定优势、潜在风险与发展方向。"

        match_dimensions = [
            {
                "label": "岗位人格适配",
                "score": round(self._coerce_float(match_breakdown.get("personality_match", 50.0)), 1),
                "description": f"依据候选人大五人格与岗位心理要求区间的适配程度计算，并非人格雷达图的平均分，当前权重约 {round(self._coerce_float(weights.get('personality', 0.35)) * 100)}%。",
            },
            {
                "label": "技能匹配",
                "score": round(self._coerce_float(match_breakdown.get("skill_match", 50.0)), 1),
                "description": f"依据岗位技能证据与评估过程中的能力表现综合判断，当前权重约 {round(self._coerce_float(weights.get('skill', 0.5)) * 100)}%。",
            },
            {
                "label": "综合匹配",
                "score": round(self._coerce_float(match_breakdown.get("overall_score", 50.0)), 1),
                "description": gate_reason if hard_skill_gate.get("applied") else "综合人格、技能与岗位情境得到的整体 Person-Job Matching 结果。",
            },
        ]

        return {
            "overview_summary": overview_summary,
            "personality_summary": personality_summary,
            "match_dimensions": match_dimensions,
            "evidence_summary": {
                "verified_skills": evidence.get("verified_skills", []),
                "missing_must_have_skills": evidence.get("missing_must_have_skills", []),
                "personality_evidence": evidence.get("personality_evidence", {}),
                "evidence_quote": evidence.get("evidence_quote", []),
                "hard_skill_gate": hard_skill_gate,
            },
            "trait_insights": trait_insights,
            "career_recommendations": career_recommendations,
            "cautious_career_recommendations": cautious_career_recommendations,
            "development_actions": development_actions,
        }

    def build_match_analysis(
        self,
        *,
        profile: CandidatePersonalityProfile,
        job: Job,
        scoring_meta: Dict[str, Any],
        match_breakdown: Dict[str, float],
        matched_skills: List[str],
        missing_skills: List[str],
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        evidence = evidence or {}
        strengths = self.generate_analysis("strengths", profile)
        gaps = self.generate_analysis("gaps", profile)
        recommendations = self.generate_recommendations(profile, job)
        verified_from_evidence = [
            str(item).strip()
            for item in (evidence.get("verified_skills") or [])
            if str(item).strip()
        ]
        missing_from_evidence = [
            str(item).strip()
            for item in (evidence.get("missing_must_have_skills") or [])
            if str(item).strip()
        ]
        personality_evidence = {
            str(key): str(value)
            for key, value in (evidence.get("personality_evidence") or {}).items()
            if str(value).strip()
        }
        evidence_quotes = [
            str(item).strip()
            for item in (evidence.get("evidence_quote") or [])
            if str(item).strip()
        ]
        hard_skill_gate = match_breakdown.get("hard_skill_gate") or {}
        weights = match_breakdown.get("weights") or {}

        all_matched = list(dict.fromkeys([*matched_skills, *verified_from_evidence]))
        all_missing = list(dict.fromkeys([*missing_skills, *missing_from_evidence]))
        if all_matched:
            strengths.insert(0, f"已形成岗位能力证据：{', '.join(all_matched[:5])}")
        if personality_evidence:
            trait_names = "、".join(list(personality_evidence.keys())[:4])
            strengths.append(f"已获得心理特质证据：{trait_names}")
        if all_missing:
            gaps.insert(0, f"岗位必备能力仍需补证或存在缺口：{', '.join(all_missing[:5])}")
        if hard_skill_gate.get("applied"):
            cap = hard_skill_gate.get("cap")
            reason = hard_skill_gate.get("reason") or "硬技能证据不足"
            gaps.insert(0, f"综合匹配度受到硬技能封顶影响：{reason}，当前上限为 {cap}%")
            recommendations.insert(0, "优先补齐岗位必备技能证据，再综合参考人格匹配结果。")
        if all_missing:
            recommendations.insert(0, f"围绕 {', '.join(all_missing[:3])} 补充项目案例、工具使用过程和可量化结果。")
        report_sections = self.build_report_sections(
            profile=profile,
            job=job,
            match_breakdown=match_breakdown,
            evidence={
                "verified_skills": all_matched,
                "missing_must_have_skills": all_missing,
                "personality_evidence": personality_evidence,
                "evidence_quote": evidence_quotes,
            },
        )

        detailed_analysis = {
            "model_version": scoring_meta.get("model_version"),
            "scoring_source": scoring_meta.get("source"),
            "input_dimensions": scoring_meta.get("input_dimensions", []),
            "match_breakdown": {
                "skill_match": round(float(match_breakdown.get("skill_match", 50.0)), 1),
                "personality_match": round(float(match_breakdown.get("personality_match", 50.0)), 1),
                "overall_score": round(float(match_breakdown.get("overall_score", 50.0)), 1),
                "weights": weights,
                "hard_skill_gate": hard_skill_gate,
            },
            "skill_evidence": {
                "matched_skills": all_matched,
                "missing_skills": all_missing,
            },
            "personality_evidence": personality_evidence,
            "evidence_quote": evidence_quotes,
            "score_explanation": {
                "summary": report_sections.get("overview_summary"),
                "weights": weights,
                "hard_skill_gate": hard_skill_gate,
            },
            "structured_report": report_sections,
        }

        return {
            "strengths": strengths,
            "gaps": gaps,
            "recommendations": recommendations,
            "report_sections": report_sections,
            "detailed_analysis": detailed_analysis,
        }


report_agent = ReportAgent()
