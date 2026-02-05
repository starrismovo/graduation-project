"""
HR-Agent 大模型集成工具
用于与 OpenAI / Claude 等大模型交互

配置说明：
1. 模拟模式（开发/测试）：
   - 自动启用（当 OPENAI_API_KEY 环境变量不存在时）
   - 手动启用：force_mock=True
   - 优点：快速、无需 API 调用、完全可控

2. 真实 API 模式（生产）：
   - 设置 OPENAI_API_KEY 环境变量
   - 或传递 api_key 参数
   - force_mock=False 禁用模拟模式

使用示例：
    # 开发模式（自动使用模拟）
    llm = HRAgentLLM()  # 不存在 API Key 时自动启用模拟
    
    # 手动启用模拟模式
    llm = HRAgentLLM(force_mock=True)
    
    # 真实 API 模式
    llm = HRAgentLLM(api_key="sk-xxx", force_mock=False)
"""

import os
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class HRAgentLLM:
    """HR-Agent 大模型接口
    
    支持两种模式：
    1. 模拟模式（Mock）：本地规则引擎，用于开发和测试
    2. 真实 API 模式：调用实际的 LLM API（OpenAI、Claude 等）
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4", force_mock: bool = None):
        """初始化 HR-Agent LLM
        
        Args:
            api_key: OpenAI API 密钥，也可通过环境变量 OPENAI_API_KEY 传递
            model: 模型名称（gpt-4、gpt-3.5-turbo 等）
            force_mock: 强制使用模拟模式
                - None（默认）：自动判断（有 API Key 则使用真实API，无则使用模拟）
                - True：强制使用模拟模式
                - False：强制使用真实 API（需提供 api_key）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        
        # 确定是否使用模拟模式
        if force_mock is True:
            # 显式要求使用模拟模式
            self.use_mock = True
            logger.info("✓ HR-Agent 已启用模拟模式（手动设置）")
        elif force_mock is False:
            # 显式要求使用真实 API
            if not self.api_key:
                logger.warning("⚠ 要求使用真实 API 但未提供 API Key，自动回退到模拟模式")
                self.use_mock = True
            else:
                self.use_mock = False
                logger.info(f"✓ HR-Agent 已启用真实 API 模式（模型：{self.model}）")
        else:
            # 自动判断
            self.use_mock = not self.api_key
            if self.use_mock:
                logger.info("✓ HR-Agent 已启用模拟模式（自动检测）")
            else:
                logger.info(f"✓ HR-Agent 已启用真实 API 模式（模型：{self.model}）")
    
    def generate_follow_up_question(
        self,
        scenario_description: str,
        target_traits: List[str],
        previous_answers: List[Dict[str, str]],
        round_num: int,
        max_rounds: int = 3
    ) -> Dict[str, Any]:
        """
        生成追问问题
        
        Args:
            scenario_description: 情景描述
            target_traits: 目标特质列表
            previous_answers: 历史回答
            round_num: 当前轮次
            max_rounds: 最大轮次
            
        Returns:
            {
                "question": "追问问题",
                "reasoning": "为什么这样问"
            }
        """
        
        if self.use_mock:
            return self._mock_follow_up_question(round_num, target_traits)
        
        # 实际调用 OpenAI API
        conversation = self._build_conversation(
            scenario_description,
            target_traits,
            previous_answers
        )
        
        return self._call_openai(conversation)
    
    def score_answer(
        self,
        scenario_description: str,
        target_traits: List[str],
        current_answer: str,
        all_answers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        对回答进行特质评分
        
        Args:
            scenario_description: 情景描述
            target_traits: 要评分的特质列表
            current_answer: 当前回答
            all_answers: 所有历史回答
            
        Returns:
            {
                "scores": {"特质1": 7.5, "特质2": 8.0},
                "reasoning": {"特质1": "理由...", "特质2": "理由..."}
            }
        """
        
        if self.use_mock:
            return self._mock_score_answer(target_traits, current_answer)
        
        # 实际调用 OpenAI API
        prompt = self._build_scoring_prompt(
            scenario_description,
            target_traits,
            current_answer,
            all_answers
        )
        
        return self._call_openai_scoring(prompt)
    
    def _mock_follow_up_question(self, round_num: int, target_traits: List[str]) -> Dict[str, str]:
        """模拟生成追问问题（本地规则）
        
        设计策略：
        - 第 1 轮：了解候选人的整体应对思路
        - 第 2 轮：深化探讨，考察特定特质
        - 第 3 轮：最后的强化追问，评估学习和反思
        """
        
        # 根据目标特质定制追问
        trait_based_questions = {
            "责任心": [
                "你会采取什么行动来尽快弥补延期带来的影响？",
                "这次延期后，你会如何制定新的计划来避免再次延期？",
                "你认为自己在这个项目中应该承担什么责任？"
            ],
            "宜人性": [
                "请具体说明你会如何与团队成员沟通这个坏消息？",
                "假设团队成员有异议，你会如何处理冲突并维持团队凝聚力？",
                "你会如何获得团队的支持和理解？"
            ],
            "情绪稳定性": [
                "当听到项目延期这个坏消息时，你的第一反应是什么？",
                "在压力下，你通常采取什么方式来保持冷静？",
                "这个经历给你什么启发或教训？"
            ]
        }
        
        # 通用的递进式追问
        default_follow_ups = {
            1: {
                "question": "请详细描述你的应对方案，包括具体的步骤和时间安排。",
                "reasoning": "了解候选人的系统性思维和计划能力"
            },
            2: {
                "question": "在执行这个方案时，你预期会遇到什么挑战？你会如何应对？",
                "reasoning": "评估风险认知和应变能力"
            },
            3: {
                "question": "如果这个方案还是没有完全解决问题，你会怎么办？",
                "reasoning": "考察坚持性和备选方案"
            }
        }
        
        # 如果有特定的目标特质，使用特质定制的问题
        if target_traits and round_num <= 3:
            for trait in target_traits:
                if trait in trait_based_questions:
                    questions = trait_based_questions[trait]
                    if round_num <= len(questions):
                        return {
                            "question": questions[round_num - 1],
                            "reasoning": f"针对 '{trait}' 特质的深层考察"
                        }
        
        # 回退到默认问题
        return default_follow_ups.get(round_num, {
            "question": "你还想补充什么关于你的处理方案吗？",
            "reasoning": "收集补充信息和最终思考"
        })
    
    def _mock_score_answer(self, target_traits: List[str], answer: str) -> Dict[str, Any]:
        """模拟评分（本地规则 + 关键词匹配 + 文本长度启发式）
        
        评分规则设计：
        - 基础分：5.0（中等水平）
        - 关键词匹配：+3.0（高分）
        - 多个关键词：+0.5 ~ 1.0（额外奖励）
        - 回答长度和详细度：+0.5 ~ 1.0（鼓励详细回答）
        
        使用本地规则的优点：
        1. 快速响应（毫秒级）
        2. 完全可控和可解释
        3. 无需 API 调用，节省成本
        4. 便于调试和优化评分逻辑
        """
        
        scores = {}
        reasoning = {}
        
        # 特质评分规则库
        trait_rules = {
            "责任心": {
                "high_keywords": ["主动", "承担责任", "尽快", "立即", "优先", "确保", "保证", "必须"],
                "medium_keywords": ["会", "应该", "可以"],
                "base_score": 5.0,
                "high_score": 8.5,
                "reason_high": "表现出了主动承担责任的态度，展现了高度的责任心",
                "reason_low": "对责任的承诺不够明确，需要更主动的态度"
            },
            "宜人性": {
                "high_keywords": ["沟通", "协商", "合作", "倾听", "理解", "支持", "帮助", "配合"],
                "medium_keywords": ["一起", "团队", "共同"],
                "base_score": 5.0,
                "high_score": 8.5,
                "reason_high": "强调了与他人的沟通和协作，展现了良好的团队意识",
                "reason_low": "缺乏对团队协作和人际沟通的强调"
            },
            "情绪稳定性": {
                "high_keywords": ["冷静", "分析", "有序", "计划", "理性", "客观", "系统", "逻辑"],
                "medium_keywords": ["思考", "想法", "方案"],
                "base_score": 5.0,
                "high_score": 8.5,
                "reason_high": "表现出了冷静理性的分析能力，在压力下保持了稳定",
                "reason_low": "可能在压力下反应仓促，需要更理性的思考"
            },
            "学习能力": {
                "high_keywords": ["学到", "教训", "改进", "优化", "反思", "总结", "升级", "演进"],
                "medium_keywords": ["知道", "了解", "意识"],
                "base_score": 5.0,
                "high_score": 8.5,
                "reason_high": "展现了从经历中吸取教训的能力，具有持续改进的意识",
                "reason_low": "缺乏对经历的反思和改进动力"
            },
            "创新能力": {
                "high_keywords": ["尝试", "创新", "新方法", "突破", "改变", "创意", "不同"],
                "medium_keywords": ["可以", "也许", "想到"],
                "base_score": 5.0,
                "high_score": 8.5,
                "reason_high": "展现了创新思维和敢于尝试新方法的态度",
                "reason_low": "更多遵循传统方法，缺乏创新意识"
            }
        }
        
        # 计算回答长度分数（鼓励详细回答）
        answer_length = len(answer)
        length_bonus = min(1.0, answer_length / 100)  # 100 字以上得满分
        
        # 对每个特质进行评分
        for trait in target_traits:
            if trait in trait_rules:
                rule = trait_rules[trait]
                score = rule["base_score"]
                
                # 检查高优先级关键词
                high_matches = sum(1 for kw in rule["high_keywords"] if kw in answer)
                if high_matches > 0:
                    score = rule["high_score"]
                    reason = rule["reason_high"]
                    
                    # 多个高优先级关键词的奖励
                    if high_matches > 1:
                        score = min(9.5, score + (high_matches - 1) * 0.3)
                else:
                    # 检查中等优先级关键词
                    medium_matches = sum(1 for kw in rule["medium_keywords"] if kw in answer)
                    if medium_matches > 0:
                        score = 6.5 + (medium_matches - 1) * 0.5
                        reason = "有一定的倾向，但不够明显"
                    else:
                        reason = rule["reason_low"]
                
                # 添加长度奖励
                score = min(10.0, score + length_bonus * 0.5)
                scores[trait] = round(score, 1)
                reasoning[trait] = reason
            else:
                # 未知特质
                scores[trait] = 5.0
                reasoning[trait] = "特质类型未在规则库中定义"
        
        return {
            "scores": scores,
            "reasoning": reasoning
        }
    
    def _build_conversation(
        self,
        scenario: str,
        target_traits: List[str],
        previous_answers: List[Dict]
    ) -> List[Dict]:
        """构建与 LLM 的对话历史"""
        
        system_message = f"""你是一位资深的人力资源评估专家和面试官。
        
当前正在评估候选人对以下情景的应对能力，重点关注以下特质：
{', '.join(target_traits)}

情景描述：
{scenario}

你的职责是：
1. 根据候选人的回答，问出有针对性的追问，深入了解他们的特质
2. 每个追问都应该帮助我们更好地评估目标特质
3. 追问应该自然、专业，且循序渐进

请根据候选人之前的回答生成下一个追问问题。"""
        
        conversation = [
            {"role": "system", "content": system_message}
        ]
        
        # 添加历史回答
        for i, item in enumerate(previous_answers):
            if "question" in item:
                conversation.append({
                    "role": "assistant",
                    "content": item["question"]
                })
            if "answer" in item:
                conversation.append({
                    "role": "user",
                    "content": item["answer"]
                })
        
        return conversation
    
    def _build_scoring_prompt(
        self,
        scenario: str,
        target_traits: List[str],
        current_answer: str,
        all_answers: List[Dict]
    ) -> str:
        """构建评分提示词"""
        
        prompt = f"""
请根据以下信息，对候选人在每个特质上的表现进行评分。

【情景描述】
{scenario}

【目标特质】
{', '.join(target_traits)}

【候选人的所有回答】
"""
        
        for i, answer in enumerate(all_answers, 1):
            prompt += f"\n第{i}轮回答：{answer.get('answer', '')}"
        
        prompt += f"""

请为每个特质评分（1-10分），其中：
- 1-3分：表现不符合特质要求
- 4-6分：表现一般，符合基本要求
- 7-8分：表现较好，展现了该特质
- 9-10分：表现优秀，充分展现了该特质

请用以下 JSON 格式返回评分和理由：
{{
    "scores": {{"特质1": 7.5, "特质2": 8.0}},
    "reasoning": {{"特质1": "详细理由...", "特质2": "详细理由..."}}
}}
"""
        
        return prompt
    
    def _call_openai(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用 OpenAI API（需要实现）"""
        # 这里需要实际调用 OpenAI API
        # 目前返回模拟数据
        return {
            "question": "请具体说明你会如何与客户沟通项目延期的影响？",
            "reasoning": "深入了解候选人的沟通技巧和客户服务意识"
        }
    
    def _call_openai_scoring(self, prompt: str) -> Dict[str, Any]:
        """调用 OpenAI API 进行评分（需要实现）"""
        # 这里需要实际调用 OpenAI API
        # 目前返回模拟数据
        return {
            "scores": {"责任心": 7.5, "宜人性": 8.0},
            "reasoning": {
                "责任心": "候选人主动承担责任，提出了具体的解决方案",
                "宜人性": "候选人强调了与团队的沟通和协作"
            }
        }


# 创建全局实例
# 支持以下配置方式：
# 1. 默认（自动）：检测 OPENAI_API_KEY 环境变量
# 2. 强制模拟：设置环境变量 LLM_FORCE_MOCK=true
# 3. 代码配置：HRAgentLLM(force_mock=True)

force_mock_env = os.getenv("LLM_FORCE_MOCK", "").lower() in ("true", "1", "yes")
hr_agent_llm = HRAgentLLM(force_mock=force_mock_env if force_mock_env else None)
