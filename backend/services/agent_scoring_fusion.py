"""
多Agent评分融合服务

论文第4.1节"多Agent协同面试机制"的核心实现
公式：综合评分 = w₁×s_技术 + w₂×s_HR + w₃×s_用人主管
"""

from typing import Dict, List, Tuple, Any, Optional
from enum import Enum


class AgentType(str, Enum):
    """Agent类型定义"""
    TECHNICAL = "technical"      # 技术评估Agent
    HR = "hr"                    # HR评估Agent
    HIRING_MANAGER = "hiring_manager"  # 用人主管Agent
    CTO = "cto"                  # CTO战略评估Agent


class JobCategory(str, Enum):
    """岗位类别"""
    TECHNICAL = "technical"      # 技术岗（如算法、后端、前端工程师）
    PRODUCT = "product"          # 产品岗
    DESIGN = "design"            # 设计岗
    MANAGEMENT = "management"    # 管理岗
    BUSINESS = "business"        # 业务岗


# 按岗位类别定义的权重配置
# 论文示例：技术岗 w₁=0.5, w₂=0.3, w₃=0.2
AGENT_WEIGHTS_BY_CATEGORY = {
    JobCategory.TECHNICAL: {
        AgentType.TECHNICAL: 0.5,        # 技术深度最重要
        AgentType.HR: 0.3,               # 团队协作次要
        AgentType.HIRING_MANAGER: 0.2,   # 岗位适配最后
    },
    JobCategory.PRODUCT: {
        AgentType.TECHNICAL: 0.3,        # 技术理解但不是主要
        AgentType.HR: 0.4,               # 沟通能力最重要
        AgentType.HIRING_MANAGER: 0.3,   # 岗位适配次要
    },
    JobCategory.MANAGEMENT: {
        AgentType.TECHNICAL: 0.2,        # 技术背景参考
        AgentType.HR: 0.4,               # 人员管理能力
        AgentType.HIRING_MANAGER: 0.4,   # 岗位领导力适配
    },
    JobCategory.DESIGN: {
        AgentType.TECHNICAL: 0.2,        # 技术理解
        AgentType.HR: 0.3,               # 沟通协作
        AgentType.HIRING_MANAGER: 0.5,   # 设计思维与岗位适配
    },
    JobCategory.BUSINESS: {
        AgentType.TECHNICAL: 0.1,        # 最少权重
        AgentType.HR: 0.5,               # 沟通和协商能力最重要
        AgentType.HIRING_MANAGER: 0.4,   # 业务目标理解
    },
}

# 默认权重配置（当岗位类别未明确时）
DEFAULT_WEIGHTS = {
    AgentType.TECHNICAL: 0.4,
    AgentType.HR: 0.3,
    AgentType.HIRING_MANAGER: 0.3,
}


def _clamp_score(score: float, low: float = 0.0, high: float = 100.0) -> float:
    """确保评分在有效范围内"""
    return max(low, min(high, float(score)))


def get_agent_weights(job_category: Optional[str] = None) -> Dict[str, float]:
    """
    根据岗位类别获取Agent权重配置
    
    Args:
        job_category: 岗位类别（如"技术岗"、"产品岗"等）
    
    Returns:
        权重配置字典，格式为 {"technical": 0.5, "hr": 0.3, "hiring_manager": 0.2}
    """
    try:
        category = JobCategory(job_category) if job_category else JobCategory.TECHNICAL
        weights = AGENT_WEIGHTS_BY_CATEGORY.get(category, DEFAULT_WEIGHTS)
    except ValueError:
        # 如果岗位类别无法识别，使用默认权重
        weights = DEFAULT_WEIGHTS
    
    return {
        AgentType.TECHNICAL.value: weights.get(AgentType.TECHNICAL, 0.4),
        AgentType.HR.value: weights.get(AgentType.HR, 0.3),
        AgentType.HIRING_MANAGER.value: weights.get(AgentType.HIRING_MANAGER, 0.3),
    }


def fuse_agent_scores(
    agent_scores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
    job_category: Optional[str] = None,
) -> Tuple[float, Dict[str, Any]]:
    """
    融合多个Agent的评分，生成综合评分
    
    论文公式：综合评分 = w₁×s_技术 + w₂×s_HR + w₃×s_用人主管
    
    Args:
        agent_scores: Agent评分字典，格式为 {
            "technical": 7.5,
            "hr": 8.0,
            "hiring_manager": 7.0
        }
        weights: 权重字典（可选），如果提供则使用；否则根据job_category推导
        job_category: 岗位类别，用于推导权重（当weights为None时）
    
    Returns:
        (综合评分, 融合详情)：
        - 综合评分：0-100的加权平均值
        - 融合详情：包含各Agent贡献、权重配置、融合过程说明
    """
    # 确保权重总和为1.0
    if weights is None:
        weights = get_agent_weights(job_category)
    
    # 归一化权重（确保总和为1.0）
    total_weight = sum(weights.values())
    if total_weight <= 0:
        weights = DEFAULT_WEIGHTS
        total_weight = sum(weights.values())
    
    normalized_weights = {k: v / total_weight for k, v in weights.items()}
    
    # 计算加权评分
    fused_score = 0.0
    agent_contributions = {}
    
    for agent_name, weight in normalized_weights.items():
        score = agent_scores.get(agent_name, 5.0)  # 默认5分
        score = _clamp_score(score)
        contribution = weight * score
        
        fused_score += contribution
        agent_contributions[agent_name] = {
            "score": score,
            "weight": weight,
            "contribution": contribution,
        }
    
    fused_score = _clamp_score(fused_score, 0, 100)
    
    # 构建详情信息
    fusion_details = {
        "fused_score": fused_score,
        "weights_used": normalized_weights,
        "agent_contributions": agent_contributions,
        "job_category": job_category,
        "fusion_method": "weighted_average",
        "formula": "综合评分 = w₁×s_技术 + w₂×s_HR + w₃×s_用人主管",
        "timestamp": None,  # 由调用者填充
    }
    
    return fused_score, fusion_details


def validate_agent_scores(agent_scores: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    验证Agent评分是否合理
    
    检查：
    1. 必须有技术Agent评分
    2. 所有评分在0-100范围内
    3. 检测异常离群值
    
    Args:
        agent_scores: Agent评分字典
    
    Returns:
        (是否有效, 警告列表)
    """
    warnings = []
    
    # 检查必要Agent
    if "technical" not in agent_scores or agent_scores["technical"] is None:
        warnings.append("缺少技术Agent评分")
    
    # 检查评分范围
    for agent_name, score in agent_scores.items():
        if score is None:
            warnings.append(f"{agent_name}评分为空")
            continue
        
        try:
            score_float = float(score)
            if score_float < 0 or score_float > 100:
                warnings.append(f"{agent_name}评分{score_float}超出范围[0-100]")
        except (TypeError, ValueError):
            warnings.append(f"{agent_name}评分{score}无法转换为数字")
    
    # 检查离群值（某个Agent评分与其他差异过大）
    valid_scores = [
        float(s) for s in agent_scores.values()
        if s is not None and isinstance(s, (int, float))
    ]
    
    if len(valid_scores) >= 2:
        avg_score = sum(valid_scores) / len(valid_scores)
        for agent_name, score in agent_scores.items():
            if score is not None:
                try:
                    score_float = float(score)
                    if abs(score_float - avg_score) > 25:  # 超过平均分25分
                        warnings.append(
                            f"{agent_name}评分{score_float}与平均分差异过大"
                            f"（平均{avg_score:.1f}），可能需要复核"
                        )
                except (TypeError, ValueError):
                    pass
    
    is_valid = len(warnings) == 0
    return is_valid, warnings


def resolve_weight_conflicts(
    primary_weights: Dict[str, float],
    secondary_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    当多个权重源冲突时，合并权重配置
    
    优先级：
    1. primary_weights（主权重，通常来自岗位JD）
    2. secondary_weights（次权重，通常来自部门经理建议）
    
    Args:
        primary_weights: 主权重配置
        secondary_weights: 次权重配置（可选）
    
    Returns:
        合并后的权重配置
    """
    merged = dict(primary_weights)
    
    if secondary_weights:
        # 按70:30的比例混合两个权重源
        for agent_name, primary_weight in primary_weights.items():
            secondary_weight = secondary_weights.get(agent_name, primary_weight)
            merged[agent_name] = primary_weight * 0.7 + secondary_weight * 0.3
    
    # 归一化确保总和为1.0
    total = sum(merged.values())
    if total > 0:
        merged = {k: v / total for k, v in merged.items()}
    
    return merged


def generate_fusion_report(
    agent_scores: Dict[str, float],
    fused_score: float,
    weights: Dict[str, float],
    job_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    生成融合评分报告（用于可解释性）
    
    Args:
        agent_scores: 各Agent原始评分
        fused_score: 融合后的综合评分
        weights: 使用的权重配置
        job_context: 岗位上下文信息
    
    Returns:
        自然语言报告
    """
    report_lines = [
        "=== 多Agent评分融合报告 ===",
        "",
        f"综合评分：{fused_score:.1f}分",
        "",
        "各Agent评分及权重：",
    ]
    
    for agent_name in ["technical", "hr", "hiring_manager"]:
        score = agent_scores.get(agent_name)
        weight = weights.get(agent_name, 0)
        if score is not None:
            contribution = score * weight
            report_lines.append(
                f"  • {agent_name:20s}：{score:5.1f}分 × {weight:.1%} = {contribution:.2f}分"
            )
    
    report_lines.append("")
    
    # 添加岗位上下文
    if job_context:
        job_category = job_context.get("category", "未知")
        report_lines.append(f"岗位类别：{job_category}")
        report_lines.append("权重配置说明：")
        
        if job_context.get("category") == "technical":
            report_lines.append("  技术岗：技术能力权重最高（50%），强调专业基础和深度")
        elif job_context.get("category") == "product":
            report_lines.append("  产品岗：沟通能力权重最高（40%），强调跨部门协作")
        elif job_context.get("category") == "management":
            report_lines.append("  管理岗：HR和主管权重均衡（各40%），强调人员管理和战略对齐")
    
    report_lines.append("")
    report_lines.append("融合方法：加权平均")
    report_lines.append("公式：综合评分 = Σ(Agent评分 × 权重)")
    
    return "\n".join(report_lines)
