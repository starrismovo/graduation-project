"""
Report Agent service.

Encapsulates report-oriented analysis generation so router code only orchestrates
pipeline steps and persistence.
"""

from __future__ import annotations

from typing import Dict, Any, List

from models.assessment import CandidatePersonalityProfile
from models.job import Job


class ReportAgent:
    """Builds strengths, gaps, and recommendations for assessment reports."""

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

    def build_match_analysis(
        self,
        *,
        profile: CandidatePersonalityProfile,
        job: Job,
        scoring_meta: Dict[str, Any],
        match_breakdown: Dict[str, float],
        matched_skills: List[str],
        missing_skills: List[str],
    ) -> Dict[str, Any]:
        strengths = self.generate_analysis("strengths", profile)
        gaps = self.generate_analysis("gaps", profile)
        recommendations = self.generate_recommendations(profile, job)

        detailed_analysis = {
            "model_version": scoring_meta.get("model_version"),
            "scoring_source": scoring_meta.get("source"),
            "input_dimensions": scoring_meta.get("input_dimensions", []),
            "match_breakdown": {
                "skill_match": round(float(match_breakdown.get("skill_match", 50.0)), 1),
                "personality_match": round(float(match_breakdown.get("personality_match", 50.0)), 1),
                "overall_score": round(float(match_breakdown.get("overall_score", 50.0)), 1),
            },
            "skill_evidence": {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
            },
        }

        return {
            "strengths": strengths,
            "gaps": gaps,
            "recommendations": recommendations,
            "detailed_analysis": detailed_analysis,
        }


report_agent = ReportAgent()
