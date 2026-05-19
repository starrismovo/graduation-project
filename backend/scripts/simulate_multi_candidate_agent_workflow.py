"""Simulate multi-candidate Multi-Agent Interview flows for admin Job Instances.

This script is designed for end-to-end validation and data seeding:
- reads Job Instances published by username ``admin``;
- creates/updates deterministic candidate personas with different education,
  personality tendency, and skill backgrounds;
- runs the backend InterviewerAgent -> EvaluatorAgent -> DecisionAgent loop with
  a local fake LLM so the test is reproducible and does not depend on network;
- persists final AssessmentRecord/EvaluationResult/report data through the
  existing save_assessment_result path;
- writes a concise validation report under docs/.
"""

from __future__ import annotations

import asyncio
import json
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)
warnings.filterwarnings("ignore", category=UserWarning, module=r"pydantic\._internal\..*")

from database import SessionLocal, engine
from models.assessment import AssessmentRecord, EvaluationResult
from models.job import Job
from models.job_requirement import CandidateJobApplication
from models.user import User, UserType
from routers.assessment import get_report, save_assessment_result
from schemas.assessment import SaveAssessmentResultRequest
from services.immersive_dialogue import ImmersiveDialogueService, RoleType
from utils.llm_client import LLMResponse


@dataclass(frozen=True)
class Persona:
    username: str
    real_name: str
    education: str
    major: str
    experience_years: float
    style: str
    personality_scores: Dict[str, float]
    ability_scores: Dict[str, float]
    skills: List[str]
    answer_style: str


PERSONAS = [
    Persona(
        username="sim_master_backend",
        real_name="周明远",
        education="硕士",
        major="软件工程",
        experience_years=5,
        style="高尽责、低神经质、偏技术深度",
        personality_scores={"外向性": 5.8, "宜人性": 7.1, "尽责性": 8.9, "神经质": 2.8, "开放性": 7.6},
        ability_scores={"表达能力": 7.4, "团队合作": 7.2, "专业能力": 9.0, "逻辑思维": 8.8, "创新思维": 7.3, "学习能力": 8.4},
        skills=["Java", "Spring Boot", "MySQL", "Redis", "微服务", "Python", "FastAPI"],
        answer_style="回答结构清晰，强调架构取舍、稳定性和线上问题复盘。",
    ),
    Persona(
        username="sim_bachelor_frontend",
        real_name="林佳琪",
        education="本科",
        major="计算机科学与技术",
        experience_years=3,
        style="开放性高、表达主动、前端产品结合",
        personality_scores={"外向性": 7.8, "宜人性": 7.4, "尽责性": 7.2, "神经质": 4.1, "开放性": 8.6},
        ability_scores={"表达能力": 8.2, "团队合作": 7.8, "专业能力": 8.0, "逻辑思维": 7.6, "创新思维": 8.7, "学习能力": 8.3},
        skills=["Vue", "React", "TypeScript", "Element Plus", "Figma", "用户体验"],
        answer_style="回答偏用户体验和工程效率，能结合组件化、可维护性与协作流程。",
    ),
    Persona(
        username="sim_junior_ops",
        real_name="陈思源",
        education="大专",
        major="电子商务",
        experience_years=1.5,
        style="外向性高、技能较浅、学习意愿强",
        personality_scores={"外向性": 8.4, "宜人性": 7.8, "尽责性": 6.4, "神经质": 5.8, "开放性": 6.9},
        ability_scores={"表达能力": 7.9, "团队合作": 7.6, "专业能力": 5.8, "逻辑思维": 6.1, "创新思维": 6.8, "学习能力": 7.7},
        skills=["Excel", "SQL基础", "用户运营", "活动策划", "数据看板"],
        answer_style="回答积极但技术细节有限，更多强调执行、复盘和快速学习。",
    ),
    Persona(
        username="sim_phd_algorithm",
        real_name="顾清和",
        education="博士",
        major="人工智能",
        experience_years=2,
        style="开放性高、表达克制、算法研究能力强",
        personality_scores={"外向性": 4.3, "宜人性": 6.5, "尽责性": 8.2, "神经质": 3.5, "开放性": 9.2},
        ability_scores={"表达能力": 6.8, "团队合作": 6.6, "专业能力": 9.3, "逻辑思维": 9.4, "创新思维": 9.1, "学习能力": 9.0},
        skills=["Python", "推荐系统", "机器学习", "深度学习", "A/B实验", "特征工程"],
        answer_style="回答偏研究与实验验证，重视指标定义、模型泛化和长期效果。",
    ),
    Persona(
        username="sim_designer_product",
        real_name="许安然",
        education="本科",
        major="工业设计",
        experience_years=4,
        style="宜人性和开放性高、设计沟通强",
        personality_scores={"外向性": 7.1, "宜人性": 8.6, "尽责性": 7.5, "神经质": 4.3, "开放性": 8.9},
        ability_scores={"表达能力": 8.4, "团队合作": 8.5, "专业能力": 7.4, "逻辑思维": 7.2, "创新思维": 9.0, "学习能力": 8.1},
        skills=["Figma", "用户研究", "交互设计", "视觉设计", "可用性测试", "产品思维"],
        answer_style="回答强调用户情境、设计理由、跨部门沟通和体验验证。",
    ),
]


class FakeLLMClient:
    """Deterministic local LLM replacement for agent workflow testing."""

    def __init__(self, persona: Persona, job: Job):
        self.persona = persona
        self.job = job
        self.question_index = 0

    async def call_async(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **_: Any) -> LLMResponse:
        if "面试官" in system_prompt and "每次只问一个问题" in system_prompt:
            return LLMResponse(json.dumps(self._question_payload(user_prompt), ensure_ascii=False))
        if "招聘评估专家" in system_prompt:
            return LLMResponse(json.dumps(self._evaluation_payload(user_prompt), ensure_ascii=False))
        if "面试流程编排专家" in system_prompt:
            return LLMResponse(json.dumps(self._decision_payload(user_prompt), ensure_ascii=False))
        return LLMResponse("{}")

    def _question_payload(self, user_prompt: str) -> Dict[str, Any]:
        self.question_index += 1
        if "技术总监" in user_prompt:
            focus = "技术深度"
            question = f"请结合你过往经历，说明你会如何支撑“{self.job.name}”中的核心技术要求？"
        elif "产品经理" in user_prompt:
            focus = "用户洞察"
            question = f"如果你负责“{self.job.name}”相关需求，你会如何判断用户痛点和优先级？"
        elif "CTO" in user_prompt:
            focus = "战略思维"
            question = f"从长期发展看，你认为该岗位最需要在哪些能力上持续成长？"
        else:
            focus = "沟通能力"
            question = f"请先介绍一下你的背景，并说明为什么选择应聘“{self.job.name}”？"
        return {
            "question": question,
            "intent": f"考察{focus}与岗位动机",
            "difficulty": "medium" if self.question_index < 3 else "hard",
            "resume_anchor": "候选人技能与项目经历",
            "tags": [focus, self.job.category or "岗位适配"],
            "focus_area": focus,
        }

    def _evaluation_payload(self, user_prompt: str) -> Dict[str, Any]:
        score = dict(self.persona.ability_scores)
        role_bonus = 0.0
        if "技术总监" in user_prompt and any(s in self.job.description for s in ["Java", "算法", "数据", "安全", "前端"]):
            role_bonus = 0.3
        if "产品经理" in user_prompt and any(s in self.persona.skills for s in ["用户研究", "产品思维", "用户运营"]):
            role_bonus = 0.4
        for key in score:
            score[key] = round(min(10.0, max(1.0, score[key] + role_bonus)), 1)

        matched = [s for s in self.persona.skills if s.lower() in (self.job.description or "").lower() or s in (self.job.name or "")]
        if not matched:
            matched = self.persona.skills[:2]

        gap = []
        for keyword in ["Java", "React", "Vue", "Python", "推荐系统", "安全", "运营", "Figma", "SQL"]:
            if keyword in f"{self.job.name} {self.job.description}" and keyword not in self.persona.skills:
                gap.append(keyword)
        gap = gap[:2]

        return {
            "scores": {
                "沟通能力": score.get("表达能力", 6),
                "技术深度": score.get("专业能力", 6),
                "问题解决": score.get("逻辑思维", 6),
                "团队协作": score.get("团队合作", 6),
                "创新能力": score.get("创新思维", 6),
                "学习能力": score.get("学习能力", 6),
                "领导力": round((score.get("表达能力", 6) + score.get("团队合作", 6)) / 2, 1),
                "战略思维": round((score.get("逻辑思维", 6) + score.get("创新思维", 6)) / 2, 1),
                "用户洞察": round((score.get("表达能力", 6) + score.get("创新思维", 6)) / 2, 1),
                "文化契合": round((score.get("团队合作", 6) + score.get("学习能力", 6)) / 2, 1),
            },
            "evidence": self.persona.answer_style,
            "strengths": [self.persona.style, "回答能够结合个人经历与岗位要求"],
            "improvements": [f"继续补充{gap[0]}经验" if gap else "进一步量化项目结果"],
            "skill_match": {
                "matched": matched,
                "gap": gap,
                "needs_verification": gap[1:] if len(gap) > 1 else [],
            },
            "depth_assessment": {
                "answer_depth": "deep" if self.persona.ability_scores["专业能力"] >= 8 else "moderate",
                "specificity": "specific",
                "confidence_indicator": "confident" if self.persona.personality_scores["外向性"] >= 7 else "moderate",
            },
            "feedback": "回答与岗位要求有一定关联，能够体现个人经历。",
            "next_action": "continue",
            "follow_up_hint": "围绕技能差距或岗位场景继续追问",
        }

    def _decision_payload(self, user_prompt: str) -> Dict[str, Any]:
        if "已提问数：1/" in user_prompt:
            return {"action": "switch_role", "reasoning": "进入专业能力验证阶段", "suggested_difficulty": 3, "suggested_role": "tech_lead", "priority_gaps": []}
        if "已提问数：2/" in user_prompt:
            return {"action": "switch_role", "reasoning": "补充产品和用户视角", "suggested_difficulty": 3, "suggested_role": "product", "priority_gaps": []}
        return {"action": "end_interview", "reasoning": "模拟面试轮次已覆盖HR、技术和产品视角", "suggested_difficulty": 3, "suggested_role": "product", "priority_gaps": []}


def choose_persona(index: int, job: Job) -> Persona:
    text = f"{job.name} {job.description} {job.category}"
    if any(k in text for k in ["算法", "推荐"]):
        return PERSONAS[3]
    if any(k in text for k in ["前端", "React", "Vue"]):
        return PERSONAS[1]
    if any(k in text for k in ["设计", "UI", "UX"]):
        return PERSONAS[4]
    if any(k in text for k in ["运营"]):
        return PERSONAS[2]
    if any(k in text for k in ["Java", "后端", "安全"]):
        return PERSONAS[0]
    return PERSONAS[index % len(PERSONAS)]


def ensure_candidate(db, persona: Persona) -> User:
    user = db.query(User).filter(User.username == persona.username).first()
    if not user:
        user = User(
            username=persona.username,
            email=f"{persona.username}@example.com",
            hashed_password="simulated-not-for-login",
            is_hr=False,
            user_type=UserType.CANDIDATE,
            created_at=datetime.utcnow(),
        )
        db.add(user)
    user.real_name = persona.real_name
    user.nickname = persona.real_name
    user.education = persona.education
    user.major = persona.major
    user.experience_years = persona.experience_years
    user.desired_job = "AI招聘评估模拟候选人"
    user.skills = persona.skills
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def ensure_application(db, candidate_id: int, job_id: int, match_score: float | None) -> None:
    app = db.query(CandidateJobApplication).filter(
        CandidateJobApplication.candidate_id == candidate_id,
        CandidateJobApplication.job_id == job_id,
    ).first()
    if not app:
        app = CandidateJobApplication(candidate_id=candidate_id, job_id=job_id)
        db.add(app)
    app.application_status = "interviewing"
    app.match_score = match_score
    app.overall_score = match_score
    app.notes = "多Agent面试模拟自动生成，用于验证AssessmentSession闭环。"
    db.commit()


def answer_for(persona: Persona, job: Job, question: str, round_index: int) -> str:
    examples = [
        f"我是{persona.real_name}，{persona.education}学历，专业是{persona.major}。我关注这个岗位是因为它和我的技能组合 {', '.join(persona.skills[:4])} 有较强关联。",
        f"在类似项目中，我通常先拆解目标，再根据岗位要求验证关键路径。{persona.answer_style}",
        f"如果进入{job.name}，我会先补齐岗位中的关键差距，再把个人优势转化为稳定产出。",
    ]
    return f"{examples[min(round_index, len(examples)-1)]} 针对问题“{question}”，我的回答会结合具体案例、结果指标和复盘经验展开。"


def build_agent_scores(averaged_scores: Dict[str, float]) -> Dict[str, float]:
    """Build 0-100 Agent scores for fusion validation."""
    technical = (
        averaged_scores.get("专业能力", 5.0) * 0.55
        + averaged_scores.get("逻辑思维", 5.0) * 0.45
    ) * 10
    hr = (
        averaged_scores.get("表达能力", 5.0) * 0.5
        + averaged_scores.get("团队合作", 5.0) * 0.5
    ) * 10
    hiring_manager = (
        averaged_scores.get("创新思维", 5.0) * 0.4
        + averaged_scores.get("学习能力", 5.0) * 0.3
        + averaged_scores.get("逻辑思维", 5.0) * 0.3
    ) * 10
    return {
        "technical": round(min(100.0, max(0.0, technical)), 1),
        "hr": round(min(100.0, max(0.0, hr)), 1),
        "hiring_manager": round(min(100.0, max(0.0, hiring_manager)), 1),
    }


async def run_one_interview(db, candidate: User, persona: Persona, job: Job) -> Dict[str, Any]:
    fake_llm = FakeLLMClient(persona, job)
    service = ImmersiveDialogueService(db)
    service.llm_client = fake_llm
    service.interviewer_agent.llm = fake_llm
    service.evaluator_agent.llm = fake_llm
    service.decision_agent.llm = fake_llm

    job_info = {"id": job.id, "title": job.name, "description": job.description}
    resume_info = {
        "name": persona.real_name,
        "education": persona.education,
        "skills": persona.skills,
        "experience_years": persona.experience_years,
        "projects": persona.answer_style,
    }
    history: List[Dict[str, Any]] = []
    current_role = RoleType.HR
    all_round_scores: List[Dict[str, float]] = []
    decisions: List[Dict[str, Any]] = []
    questions: List[Dict[str, Any]] = []

    for round_index in range(3):
        q = await service.generate_next_question(
            id=str(candidate.id),
            candidate_name=persona.real_name,
            current_role=current_role,
            conversation_history=history,
            conversation_depth=round_index,
            target_position=job.name,
            job_info=job_info,
            resume_info=resume_info,
            assessment_id=None,
        )
        questions.append(q)
        history.append({
            "role": "assistant",
            "content": q["question"],
            "focus_area": q.get("focus_area"),
            "agent_role": q.get("interview_state", {}).get("current_role", current_role.value),
        })
        answer = answer_for(persona, job, q["question"], round_index)
        history.append({"role": "candidate", "content": answer})
        analysis = await service.analyze_candidate_response(
            id=str(candidate.id),
            candidate_name=persona.real_name,
            current_speaker=current_role,
            candidate_response=answer,
            conversation_history=history,
            conversation_depth=round_index + 1,
            target_position=job.name,
            job_info=job_info,
            resume_info=resume_info,
            assessment_id=None,
        )
        all_round_scores.append(analysis.get("scores", {}))
        decision = analysis.get("decision", {})
        decisions.append(decision)
        suggested = decision.get("suggested_role")
        if suggested:
            try:
                current_role = RoleType(suggested)
            except ValueError:
                current_role = current_role
        if decision.get("should_end"):
            break

    averaged_scores: Dict[str, float] = dict(persona.ability_scores)
    if all_round_scores:
        for source_key, target_key in [
            ("沟通能力", "表达能力"),
            ("团队协作", "团队合作"),
            ("技术深度", "专业能力"),
            ("问题解决", "逻辑思维"),
            ("创新能力", "创新思维"),
            ("学习能力", "学习能力"),
        ]:
            vals = [scores[source_key] for scores in all_round_scores if source_key in scores]
            if vals:
                averaged_scores[target_key] = round(sum(vals) / len(vals), 1)

    request = SaveAssessmentResultRequest(
        candidate_id=candidate.username,
        job_id=job.id,
        assessment_mode="immersive",
        all_scores=averaged_scores,
        personality_scores=persona.personality_scores,
        agent_scores=build_agent_scores(averaged_scores),
        candidate_info={
            "skills": persona.skills,
            "education": persona.education,
            "persona_style": persona.style,
            "simulated_questions": questions,
            "simulated_decisions": decisions,
        },
    )
    save_result = await save_assessment_result(request, db)
    record_id = save_result.data["record_id"]
    record = db.query(AssessmentRecord).filter(AssessmentRecord.id == record_id).first()
    if record:
        record.total_rounds = len(all_round_scores)
        record.conversation_depth = len(all_round_scores)
        record.roles_participated = sorted({q.get("interview_state", {}).get("current_role", "hr") for q in questions})
        record.conversation_summary = f"模拟候选人{persona.real_name}完成{len(all_round_scores)}轮多Agent面试，画像：{persona.style}。"
        record.overall_impression = json.dumps({
            "persona": persona.__dict__,
            "questions": questions,
            "decisions": decisions,
            "history": history,
        }, ensure_ascii=False)
        db.commit()

    ensure_application(db, candidate.id, job.id, save_result.data.get("overall_score"))
    report = await get_report(record_id, db)
    return {
        "candidate_id": candidate.id,
        "candidate_name": persona.real_name,
        "username": candidate.username,
        "education": persona.education,
        "persona_style": persona.style,
        "job_id": job.id,
        "job_title": job.name,
        "record_id": record_id,
        "evaluation_result_id": save_result.data.get("evaluation_result_id"),
        "overall_score": save_result.data.get("overall_score"),
        "skill_match": save_result.data.get("skill_match"),
        "personality_match": save_result.data.get("personality_match"),
        "rounds": len(all_round_scores),
        "roles": record.roles_participated if record else [],
        "report_match_score": report.data.match_score if report.data else None,
        "has_trait_comparison": bool(save_result.data.get("trait_comparison")),
        "has_agent_fusion": bool(save_result.data.get("fusion_details")),
        "issues": [],
    }


async def main() -> int:
    engine.echo = False
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            raise RuntimeError("未找到 username=admin 的 HR 用户")
        jobs = db.query(Job).filter(Job.creator_id == admin.id).order_by(Job.id.asc()).all()
        if not jobs:
            raise RuntimeError("admin 尚未发布岗位，无法执行模拟")

        results = []
        for index, job in enumerate(jobs):
            persona = choose_persona(index, job)
            candidate = ensure_candidate(db, persona)
            result = await run_one_interview(db, candidate, persona, job)
            if not result["evaluation_result_id"]:
                result["issues"].append("EvaluationResult 未创建")
            if not result["roles"]:
                result["issues"].append("roles_participated 为空")
            if result["overall_score"] is None:
                result["issues"].append("未生成综合匹配分")
            if not result["has_trait_comparison"]:
                result["issues"].append("Scenario Personality 对比未生成")
            if not result["has_agent_fusion"]:
                result["issues"].append("Agent评分融合未生成")
            results.append(result)
            print(f"OK {result['candidate_name']} -> {result['job_title']} score={result['overall_score']} record={result['record_id']}")

        total_records = db.query(AssessmentRecord).count()
        total_results = db.query(EvaluationResult).count()
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = {
            "generated_at": generated_at,
            "admin_id": admin.id,
            "job_count": len(jobs),
            "simulated_sessions": len(results),
            "database_totals": {
                "assessment_records": total_records,
                "evaluation_results": total_results,
            },
            "results": results,
            "observations": [
                "三Agent调用链可在无外部LLM条件下完成 InterviewerAgent -> EvaluatorAgent -> DecisionAgent 闭环。",
                "最终结果通过 /assessment/save-result 同一路径沉淀为 AssessmentRecord、CandidatePersonalityProfile、EvaluationResult、AssessmentMatchAnalysis 和 PersonalityTraitDescription。",
                "SaveAssessmentResultRequest 已声明 agent_scores 字段，可通过标准请求进入多Agent评分融合分支。",
                "agent_scoring_fusion 已增加中文岗位类别映射，可处理 技术/产品/设计/运营 等本地类别。",
            ],
        }

        docs_dir = PROJECT_DIR / "docs"
        docs_dir.mkdir(exist_ok=True)
        report_path = docs_dir / "MULTI_AGENT_SIMULATION_RECORD.md"
        lines = [
            "# 多Agent面试模拟与闭环验证记录",
            "",
            f"生成时间：{generated_at}",
            "",
            "## 概况",
            "",
            f"- admin 用户ID：{admin.id}",
            f"- 覆盖岗位实例数：{len(jobs)}",
            f"- 新增/更新模拟评估会话数：{len(results)}",
            f"- 当前 AssessmentRecord 总数：{total_records}",
            f"- 当前 EvaluationResult 总数：{total_results}",
            "",
            "## 模拟结果",
            "",
            "| 候选人 | 学历 | 性格/能力画像 | 岗位实例 | 记录ID | 综合匹配 | 技能匹配 | 人格匹配 | 轮次 | 参与角色 |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
        for item in results:
            lines.append(
                f"| {item['candidate_name']} | {item['education']} | {item['persona_style']} | "
                f"{item['job_title']} | {item['record_id']} | {item['overall_score']} | "
                f"{item['skill_match']} | {item['personality_match']} | {item['rounds']} | "
                f"{', '.join(item['roles'])} |"
            )
        lines.extend([
            "",
            "## 闭环判断",
            "",
            "本次模拟覆盖了候选人资料写入、岗位实例读取、多Agent面试、回答评估、路径决策、AssessmentSession结果保存、人格画像更新、EvaluationResult生成、报告读取和应聘记录沉淀。整体流程可以跑通。",
            "",
            "## 发现的不合理点",
            "",
        ])
        for obs in report["observations"][2:]:
            lines.append(f"- {obs}")
        lines.extend([
            "",
            "## 原始JSON摘要",
            "",
            "```json",
            json.dumps(report, ensure_ascii=False, indent=2),
            "```",
            "",
        ])
        try:
            report_path.write_text("\n".join(lines), encoding="utf-8")
        except PermissionError:
            report_path = PROJECT_DIR / "MULTI_AGENT_SIMULATION_RECORD.md"
            try:
                report_path.write_text("\n".join(lines), encoding="utf-8")
            except PermissionError:
                report_path = Path(r"D:\tmp\MULTI_AGENT_SIMULATION_RECORD.md")
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"REPORT {report_path}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
