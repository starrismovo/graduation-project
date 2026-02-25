"""
虚拟面试官角色管理模块

支持多种面试官角色（HR、技术总监等），每个角色有独立的面试风格、问题库和评估标准。
支持动态 System Prompt 切换。
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


class InterviewerRole(str, Enum):
    """面试官角色枚举"""
    HR = "hr"  # 人力资源
    TECH_LEAD = "tech_lead"  # 技术总监
    PRODUCT_MANAGER = "product_manager"  # 产品经理
    CEO = "ceo"  # CEO/创始人


@dataclass
class RoleConfig:
    """面试官角色配置"""
    role_id: str  # 角色ID
    role_name: str  # 角色名称（如：HR 李明）
    role_type: InterviewerRole  # 角色类型
    
    # 面试风格特征
    tone: str  # 语气（正式、友好、严肃等）
    focus_areas: List[str]  # 关注领域
    
    # 系统提示词模板
    system_prompt_template: str  # 基础 System Prompt 模板
    role_description: str  # 角色描述
    
    # 问题库
    question_bank: Dict[str, List[str]] = field(default_factory=dict)
    
    # 评估重点
    evaluation_focus: Dict[str, float] = field(default_factory=dict)  # 评估维度及权重
    
    # 轮次特定的指导
    round_specific_prompts: Dict[int, str] = field(default_factory=dict)


class InterviewerState:
    """面试官当前状态"""
    
    def __init__(self, config: RoleConfig):
        self.config = config
        self.current_round = 0  # 当前轮次（从 0 开始）
        self.conversation_history: List[Dict[str, str]] = []  # 对话历史
        self.questions_asked: List[str] = []  # 已问过的问题
        self.candidate_responses: List[str] = []  # 候选人的回答
        self.scores: Dict[str, float] = {}  # 各维度评分
        self.state_created_at = datetime.now()
        
    def reset_for_new_round(self):
        """重置为下一轮"""
        self.current_round += 1
        self.conversation_history.clear()
        self.questions_asked.clear()
        
    def add_message(self, role: str, content: str):
        """添加对话消息"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_question(self, question: str):
        """记录提出的问题"""
        self.questions_asked.append(question)
        
    def add_candidate_response(self, response: str):
        """记录候选人回答"""
        self.candidate_responses.append(response)
        
    def update_score(self, dimension: str, score: float):
        """更新评估分数"""
        if 0 <= score <= 10:
            self.scores[dimension] = score
        else:
            raise ValueError(f"分数必须在 0-10 之间，收到 {score}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于存储或传输）"""
        return {
            "role_id": self.config.role_id,
            "role_name": self.config.role_name,
            "role_type": self.config.role_type.value,
            "current_round": self.current_round,
            "conversation_history": self.conversation_history,
            "questions_asked": self.questions_asked,
            "candidate_responses": self.candidate_responses,
            "scores": self.scores,
            "state_created_at": self.state_created_at.isoformat()
        }


class InterviewerRoleManager:
    """虚拟面试官角色管理器 - 核心类"""
    
    def __init__(self):
        """初始化角色管理器"""
        self._roles: Dict[str, RoleConfig] = {}
        self._current_state: Optional[InterviewerState] = None
        self._state_history: List[InterviewerState] = []
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """初始化默认的面试官角色"""
        
        # HR 李明 - 关注文化匹配和通用素质
        hr_config = RoleConfig(
            role_id="hr_liming",
            role_name="HR 李明",
            role_type=InterviewerRole.HR,
            tone="warm_and_professional",  # 温暖且专业
            focus_areas=["communication", "culture_fit", "work_experience"],
            system_prompt_template="""你是一位资深的人力资源招聘专家，名叫李明。
你的角色是在面试过程中评估候选人的综合素质，包括：
- 沟通能力和表达能力
- 与公司文化的匹配度
- 工作经验和职业发展
- 团队协作能力

你的面试风格：温暖、专业、鼓励性。
你会根据候选人的回答深入追问，了解他们的真实想法。

当前是第 {round} 轮面试。
{round_specific_guidance}

请记住：
- 用中文进行对话
- 每次只问一个问题
- 认真倾听候选人的回答
- 根据回答灵活调整后续问题""",
            role_description="资深HR，评估候选人的文化适配度和基础素质",
            evaluation_focus={
                "communication_skills": 0.25,
                "culture_fit": 0.25,
                "work_experience": 0.20,
                "teamwork": 0.20,
                "growth_potential": 0.10
            },
            round_specific_prompts={
                0: "这是第一轮面试。请从候选人的基本背景和职业目标开始提问。",
                1: "这是第二轮面试。请深入了解候选人在以往工作中的具体案例和成就。",
                2: "这是第三轮面试。请评估候选人与团队的协作能力和文化匹配度。"
            }
        )
        
        # 技术总监 张伟 - 关注技术能力和问题解决
        tech_config = RoleConfig(
            role_id="tech_lead_zhangwei",
            role_name="技术总监 张伟",
            role_type=InterviewerRole.TECH_LEAD,
            tone="rigorous_and_encouraging",  # 严谨且鼓励
            focus_areas=["technical_skills", "problem_solving", "system_design"],
            system_prompt_template="""你是一位技术总监，名叫张伟，有 15 年的技术经验。
你的角色是在面试过程中深入评估候选人的技术能力和解决问题的能力。
关注领域：
- 编程语言和框架掌握
- 系统设计和架构思维
- 问题解决的思路和方法
- 技术深度和学习能力

你的面试风格：严谨、有深度、但也很支持候选人。
你会通过设计一些场景题来理解候选人的思考过程。

当前是第 {round} 轮面试。
{round_specific_guidance}

请记住：
- 用中文进行对话
- 关注候选人的思考过程，而不仅仅是答案
- 每次只问一个问题
- 会根据回答逐步深入追问""",
            role_description="技术总监，深入评估候选人的技术深度和系统设计能力",
            evaluation_focus={
                "technical_depth": 0.35,
                "problem_solving": 0.25,
                "system_design": 0.20,
                "code_quality": 0.15,
                "learning_ability": 0.05
            },
            round_specific_prompts={
                0: "这是第一轮技术评估。请了解候选人的技术背景和擅长的领域。",
                1: "这是第二轮技术面试。请通过编程题或系统设计题深入了解候选人的技术思维。",
                2: "这是第三轮面试。请评估候选人的架构思维和大局观。"
            }
        )
        
        # 产品经理 王慧 - 关注产品思维和用户意识
        pm_config = RoleConfig(
            role_id="pm_wanghui",
            role_name="产品经理 王慧",
            role_type=InterviewerRole.PRODUCT_MANAGER,
            tone="creative_and_analytical",  # 创意且分析性
            focus_areas=["product_thinking", "user_awareness", "business_sense"],
            system_prompt_template="""你是一位资深产品经理，名叫王慧。
你的角色是在面试过程中评估候选人的产品思维和业务理解能力。
关注领域：
- 用户思维和同理心
- 产品创新意识
- 数据分析和决策能力
- 商业敏感度

你的面试风格：开放、激情、鼓励创新思维。
你会通过真实案例和假设场景来了解候选人的思考方式。

当前是第 {round} 轮面试。
{round_specific_guidance}

请记住：
- 用中文进行对话
- 关注候选人的用户意识和商业敏感度
- 鼓励候选人分享自己的观点
- 每次只问一个问题""",
            role_description="资深产品经理，评估候选人的产品思维和用户意识",
            evaluation_focus={
                "product_thinking": 0.30,
                "user_empathy": 0.25,
                "business_sense": 0.20,
                "analytical_thinking": 0.15,
                "innovation": 0.10
            },
            round_specific_prompts={
                0: "这是第一轮面试。请了解候选人对产品和用户的理解。",
                1: "这是第二轮面试。请通过案例分析评估候选人的产品思维。",
                2: "这是第三轮面试。请评估候选人的战略思维和大局观。"
            }
        )
        
        # 注册所有角色
        self.register_role(hr_config)
        self.register_role(tech_config)
        self.register_role(pm_config)
    
    def register_role(self, config: RoleConfig):
        """注册新的面试官角色"""
        self._roles[config.role_id] = config
    
    def get_role(self, role_id: str) -> Optional[RoleConfig]:
        """获取角色配置"""
        return self._roles.get(role_id)
    
    def get_all_roles(self) -> Dict[str, RoleConfig]:
        """获取所有角色"""
        return self._roles.copy()
    
    def switch_to_role(self, role_id: str) -> InterviewerState:
        """切换到指定角色，返回新的状态"""
        config = self.get_role(role_id)
        if not config:
            raise ValueError(f"角色不存在: {role_id}")
        
        # 保存当前状态到历史
        if self._current_state:
            self._state_history.append(self._current_state)
        
        # 创建新状态
        self._current_state = InterviewerState(config)
        return self._current_state
    
    def get_current_state(self) -> Optional[InterviewerState]:
        """获取当前角色状态"""
        return self._current_state
    
    def get_system_prompt(self, role_id: str, round_num: int) -> str:
        """
        获取特定轮次的 System Prompt
        
        参数:
            role_id: 角色ID
            round_num: 轮次（0 开始）
        
        返回:
            根据轮次定制的 System Prompt
        """
        config = self.get_role(role_id)
        if not config:
            raise ValueError(f"角色不存在: {role_id}")
        
        # 获取轮次特定的指导
        round_guidance = config.round_specific_prompts.get(
            round_num,
            f"这是第 {round_num + 1} 轮面试。请继续深入评估候选人。"
        )
        
        # 使用模板生成最终的 System Prompt
        system_prompt = config.system_prompt_template.format(
            round=round_num + 1,
            round_specific_guidance=round_guidance
        )
        
        return system_prompt
    
    def advance_round(self):
        """推进到下一轮"""
        if self._current_state:
            self._current_state.reset_for_new_round()
    
    def get_state_history(self) -> List[InterviewerState]:
        """获取状态历史"""
        return self._state_history.copy()
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """获取评估汇总"""
        if not self._current_state:
            return {}
        
        summary = {
            "role_name": self._current_state.config.role_name,
            "current_round": self._current_state.current_round,
            "messages_count": len(self._current_state.conversation_history),
            "questions_asked": len(self._current_state.questions_asked),
            "scores": self._current_state.scores,
            "evaluation_focus": self._current_state.config.evaluation_focus
        }
        
        return summary


# 全局单例 (可选，便于使用)
_global_role_manager: Optional[InterviewerRoleManager] = None


def get_role_manager() -> InterviewerRoleManager:
    """获取全局角色管理器单例"""
    global _global_role_manager
    if _global_role_manager is None:
        _global_role_manager = InterviewerRoleManager()
    return _global_role_manager
