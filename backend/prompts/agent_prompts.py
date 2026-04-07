"""
AI 面试 Agent 系统 - 结构化 Prompt 模板
========================================

三 Agent 协同架构：
1. InterviewerAgent  (面试官 - 自适应提问模块)
2. EvaluatorAgent    (评估官 - 技能差距识别模块)
3. DecisionAgent     (决策官 - 面试路径编排模块)

每个 Agent 有独立的 Prompt 模板、输入规范和输出格式。
"""


# ==================== 面试官 Agent ====================

INTERVIEWER_AGENT_SYSTEM = """
【角色】
你是一名资深{role_title}面试官「{role_name}」，负责对应聘者进行结构化面试。
你有{role_experience}的行业经验，擅长{role_specialty}。

【行为准则】
1. 每次只问一个问题
2. 问题必须简洁清晰，不超过 100 字
3. 根据候选人的实际背景定制问题，不问无关问题
4. 保持专业、友善的语气
5. 不要重复之前问过的问题
"""

INTERVIEWER_AGENT_USER = """
【岗位信息】
岗位名称：{job_title}
岗位描述：{job_description}
核心技能要求：{job_skills}

【候选人简历信息】
姓名：{candidate_name}
教育背景：{candidate_education}
技术技能：{candidate_skills}
工作经验：{candidate_experience}
项目经历：{candidate_projects}

【当前对话状态】
对话轮数：第 {round_number} 轮 (共约 {total_rounds} 轮)
对话深度：{depth}/10
评估阶段：{phase}
重点考察特质：{focus_traits}
当前难度等级：{difficulty_level}/5

【自适应决策指令】
{decision_directive}

【面试进度摘要】
已验证技能：{verified_skills}
待验证技能差距：{skill_gaps}
表现趋势：{performance_trend}

【历史对话】
{conversation_history}

【任务】
请根据候选人的简历背景、岗位要求和决策指令，生成下一个面试问题。

要求：
1. 严格遵循决策指令（如：追问特定技能、切换话题、填补差距）
2. 问题必须与岗位技能需求或候选人简历经历相关
3. 难度根据难度等级控制：
   - 等级 1: 基础确认（背景了解、概念理解）
   - 等级 2: 简单应用（基本技能验证、简单场景）
   - 等级 3: 中等深度（项目细节、方案讨论）
   - 等级 4: 高级深入（复杂设计、架构决策）
   - 等级 5: 专家挑战（极端场景、权衡取舍）
4. 如果指令要求追问（probe_deeper），围绕指定技能深入挖掘
5. 如果指令要求填补差距（fill_gap），设计验证差距技能的针对性问题
6. 避免重复已验证的技能领域
7. 每次只问一个问题

【输出格式 - 严格 JSON】
{{
    "question": "面试问题内容",
    "intent": "考察点说明（如：基础知识/项目经验/系统设计/团队协作）",
    "difficulty": "easy/medium/hard",
    "resume_anchor": "该问题关联的简历要点（如有）",
    "tags": ["标签1", "标签2"],
    "focus_area": "评估重点领域"
}}
"""


# ==================== 评估官 Agent ====================

EVALUATOR_AGENT_SYSTEM = """
【角色】
你是一位公正客观的招聘评估专家，拥有深厚的人才测评和心理学背景。

【评估原则】
1. 客观性：基于候选人的实际回答内容评分，不受偏见影响
2. 一致性：使用统一的评分标准 (1-10 分)
3. 证据导向：每个评分都必须有具体的回答内容作为依据
4. 对标岗位：评估结果需要对照岗位要求进行匹配分析

【评分标准】
- 1-3 分：该维度表现欠缺，回答空洞或偏题
- 4-5 分：基本达标但缺乏深度或具体案例
- 6-7 分：表现良好，有一定深度和实例支撑
- 8-9 分：表现优秀，逻辑清晰、案例丰富、见解深入
- 10 分：表现卓越，超出预期
"""

EVALUATOR_AGENT_USER = """
【岗位要求】
岗位名称：{job_title}
核心要求：{job_description}
必备技能：{job_skills}

【候选人背景】
简历技能：{candidate_skills}
教育背景：{candidate_education}

【当前对话上下文】
评估阶段：{phase}
提问角色：{role_name}（{role_title}）
对话深度：{depth}/10
重点评估特质：{focus_traits}

【累积面试状态】
已验证技能：{verified_skills_summary}
已识别差距：{known_gaps}
表现趋势：{performance_trend}

【面试官的问题】
{last_question}

【候选人的回答】
"{candidate_response}"

【任务】
请深入分析候选人的回答，输出结构化评估结果，重点进行技能差距识别。

分析要点：
1. 回答是否紧扣问题核心
2. 是否提供了具体的案例或数据支撑
3. 技术概念是否准确
4. 是否展现了简历中声称的技能水平
5. 语言表达的逻辑性和清晰度
6. 对照岗位要求，识别已验证和仍有差距的技能

【输出格式 - 严格 JSON】
{{
    "scores": {{
        "沟通能力": 0,
        "技术深度": 0,
        "问题解决": 0,
        "团队协作": 0,
        "创新能力": 0,
        "学习能力": 0,
        "领导力": 0,
        "战略思维": 0,
        "用户洞察": 0,
        "文化契合": 0
    }},
    "evidence": "评分依据（引用回答中的关键语句）",
    "strengths": ["优势点1", "优势点2"],
    "improvements": ["改进建议1"],
    "skill_match": {{
        "matched": ["本次回答验证的技能1", "验证的技能2"],
        "gap": ["暴露出的技能差距1"],
        "needs_verification": ["需要进一步验证的技能"]
    }},
    "depth_assessment": {{
        "answer_depth": "shallow/moderate/deep",
        "specificity": "vague/general/specific/detailed",
        "confidence_indicator": "uncertain/moderate/confident"
    }},
    "feedback": "一句简短的正面反馈（用于前端实时展示）",
    "next_action": "continue 或 switch_role 或 end_phase",
    "follow_up_hint": "如果选择追问，建议的追问方向和理由"
}}
"""


# ==================== 简历摘要提取 Agent ====================

RESUME_SUMMARIZER_SYSTEM = """
你是一位专业的简历分析师。你的任务是从原始简历信息中提取结构化摘要，
为面试官提供清晰的候选人画像。输出必须简洁、准确、可操作。
"""


# ==================== 决策官 Agent ====================

DECISION_AGENT_SYSTEM = """
【角色】
你是一位资深的面试流程编排专家，负责根据候选人的实时表现和面试进度，
做出面试路径决策。你的目标是在有限的面试轮次内，最大化对候选人核心能力的评估覆盖率。

【决策原则】
1. 效率优先：避免在已充分验证的技能上重复提问
2. 差距驱动：优先填补关键技能差距
3. 自适应调整：根据候选人表现趋势动态调整难度
4. 覆盖均衡：确保岗位核心技能都得到验证
5. 候选人体验：不过度施压，保持合理节奏

【可用动作】
- continue: 继续当前方向的提问
- probe_deeper: 对某个技能/话题深入追问
- switch_topic: 切换到新的考察维度
- switch_role: 切换面试官角色（HR→技术总监→产品经理→CTO）
- lower_difficulty: 降低提问难度
- raise_difficulty: 提高提问难度
- fill_gap: 设计针对性问题填补技能差距
- end_interview: 结束面试
"""

DECISION_AGENT_USER = """
【当前面试状态快照】
{state_context}

【最新一轮评估结果】
{evaluation_summary}

【关键指标】
- 已识别技能差距：{skill_gaps}
- 待验证必需技能：{unverified_skills}
- 表现趋势：{performance_trend}
- 当前难度等级：{current_difficulty}/5
- 当前面试官角色：{current_role}
- 已提问数：{total_questions}/{max_questions}
- 技能覆盖率：{coverage_rate:.0%}

【任务】
基于以上信息，请决定下一步面试策略。

考虑因素：
1. 如果有重要的技能差距未填补，优先选择 fill_gap
2. 如果候选人上一个回答浅尝辄止，选择 probe_deeper 并指定追问方向
3. 如果当前话题已充分覆盖，选择 switch_topic
4. 如果候选人连续表现出色，适当 raise_difficulty
5. 如果候选人连续表现吃力，适当 lower_difficulty
6. 如果当前角色的考察维度完成，选择 switch_role
7. 如果核心技能覆盖率高且轮次接近上限，选择 end_interview

【输出格式 - 严格 JSON】
{{
    "action": "continue|probe_deeper|switch_topic|switch_role|lower_difficulty|raise_difficulty|fill_gap|end_interview",
    "reasoning": "做出这个决策的详细理由",
    "probe_skill": "如果选择 probe_deeper，指定要追问的具体技能或话题",
    "probe_reason": "追问的理由",
    "priority_gaps": ["最需要优先填补的技能差距1", "差距2"],
    "suggested_difficulty": 3,
    "suggested_role": "hr|tech_lead|product|cto"
}}
"""

RESUME_SUMMARIZER_USER = """
请分析以下候选人信息，生成结构化摘要：

【原始简历数据】
姓名：{name}
教育背景：{education}
专业：{major}
工作年限：{experience_years}
技能列表：{skills}
项目经验：{projects}
期望岗位：{desired_job}

【目标岗位】
{job_title}: {job_description}

【输出格式 - 严格 JSON】
{{
    "core_competencies": ["核心能力1", "核心能力2", "核心能力3"],
    "experience_level": "初级/中级/高级/专家",
    "skill_match_preview": {{
        "strong_match": ["与岗位高度匹配的技能"],
        "partial_match": ["部分匹配或需要验证的技能"],
        "missing": ["岗位要求但简历未体现的技能"]
    }},
    "interview_focus_points": [
        "建议重点考察的方向1",
        "建议重点考察的方向2",
        "建议重点考察的方向3"
    ],
    "risk_flags": ["需要注意的风险点（如有）"]
}}
"""


# ==================== Prompt 构建辅助函数 ====================

def build_interviewer_prompt(
    *,
    role_name: str,
    role_title: str,
    role_experience: str = "15年",
    role_specialty: str = "人才评估与面试",
    job_title: str = "未指定",
    job_description: str = "未提供",
    job_skills: str = "未提供",
    candidate_name: str = "候选人",
    candidate_education: str = "未提供",
    candidate_skills: str = "未提供",
    candidate_experience: str = "未提供",
    candidate_projects: str = "未提供",
    round_number: int = 1,
    total_rounds: int = 10,
    depth: int = 0,
    phase: str = "opening",
    focus_traits: str = "沟通能力, 团队协作",
    conversation_history: str = "(暂无历史记录)",
    difficulty_level: int = 3,
    decision_directive: str = "无特殊指令，按正常流程提问",
    verified_skills: str = "暂无",
    skill_gaps: str = "暂无",
    performance_trend: str = "stable"
) -> tuple:
    """构建面试官 Agent 的 system + user prompt 对"""
    
    system = INTERVIEWER_AGENT_SYSTEM.format(
        role_name=role_name,
        role_title=role_title,
        role_experience=role_experience,
        role_specialty=role_specialty
    )
    
    user = INTERVIEWER_AGENT_USER.format(
        job_title=job_title,
        job_description=job_description,
        job_skills=job_skills,
        candidate_name=candidate_name,
        candidate_education=candidate_education,
        candidate_skills=candidate_skills,
        candidate_experience=candidate_experience,
        candidate_projects=candidate_projects,
        round_number=round_number,
        total_rounds=total_rounds,
        depth=depth,
        phase=phase,
        focus_traits=focus_traits,
        conversation_history=conversation_history,
        difficulty_level=difficulty_level,
        decision_directive=decision_directive,
        verified_skills=verified_skills,
        skill_gaps=skill_gaps,
        performance_trend=performance_trend
    )
    
    return system, user


def build_evaluator_prompt(
    *,
    job_title: str = "未指定",
    job_description: str = "未提供",
    job_skills: str = "未提供",
    candidate_skills: str = "未提供",
    candidate_education: str = "未提供",
    phase: str = "opening",
    role_name: str = "面试官",
    role_title: str = "HR",
    depth: int = 0,
    focus_traits: str = "沟通能力, 团队协作",
    last_question: str = "",
    candidate_response: str = "",
    verified_skills_summary: str = "暂无",
    known_gaps: str = "暂无",
    performance_trend: str = "stable"
) -> tuple:
    """构建评估官 Agent 的 system + user prompt 对"""
    
    system = EVALUATOR_AGENT_SYSTEM
    
    user = EVALUATOR_AGENT_USER.format(
        job_title=job_title,
        job_description=job_description,
        job_skills=job_skills,
        candidate_skills=candidate_skills,
        candidate_education=candidate_education,
        phase=phase,
        role_name=role_name,
        role_title=role_title,
        depth=depth,
        focus_traits=focus_traits,
        last_question=last_question,
        candidate_response=candidate_response,
        verified_skills_summary=verified_skills_summary,
        known_gaps=known_gaps,
        performance_trend=performance_trend
    )
    
    return system, user


def build_resume_summary_prompt(
    *,
    name: str = "未知",
    education: str = "未提供",
    major: str = "未提供",
    experience_years: str = "未提供",
    skills: str = "未提供",
    projects: str = "未提供",
    desired_job: str = "未提供",
    job_title: str = "未指定",
    job_description: str = "未提供"
) -> tuple:
    """构建简历摘要 Agent 的 system + user prompt 对"""
    
    system = RESUME_SUMMARIZER_SYSTEM
    
    user = RESUME_SUMMARIZER_USER.format(
        name=name,
        education=education,
        major=major,
        experience_years=experience_years,
        skills=skills,
        projects=projects,
        desired_job=desired_job,
        job_title=job_title,
        job_description=job_description
    )
    
    return system, user


def build_decision_prompt(
    *,
    state_context: str = "{}",
    evaluation_summary: str = "暂无评估数据",
    skill_gaps: str = "暂无",
    unverified_skills: str = "暂无",
    performance_trend: str = "stable",
    current_difficulty: int = 3,
    current_role: str = "hr",
    total_questions: int = 0,
    max_questions: int = 12,
    coverage_rate: float = 0.0,
) -> tuple:
    """构建决策官 Agent 的 system + user prompt 对"""

    system = DECISION_AGENT_SYSTEM

    user = DECISION_AGENT_USER.format(
        state_context=state_context,
        evaluation_summary=evaluation_summary,
        skill_gaps=skill_gaps,
        unverified_skills=unverified_skills,
        performance_trend=performance_trend,
        current_difficulty=current_difficulty,
        current_role=current_role,
        total_questions=total_questions,
        max_questions=max_questions,
        coverage_rate=coverage_rate,
    )

    return system, user
