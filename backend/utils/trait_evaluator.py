"""
特质评估器 - 从对话中提取候选人特质和评分
"""

import re
import json
from typing import Dict, List, Any
from collections import Counter


class TraitEvaluator:
    """特质评估引擎"""
    
    # 定义所有可评估的特质维度
    TRAIT_DIMENSIONS = {
        "沟通能力": {
            "keywords": ["清晰", "表达", "沟通", "说明", "描述", "阐述", "讲述"],
            "indicators": ["语句通顺", "逻辑清晰", "用词恰当", "举例生动"]
        },
        "问题解决": {
            "keywords": ["解决", "方案", "思路", "分析", "处理", "应对", "克服"],
            "indicators": ["分步骤", "考虑周全", "创意解法", "可行性强"]
        },
        "技术深度": {
            "keywords": ["算法", "架构", "系统", "设计", "优化", "性能", "框架"],
            "indicators": ["概念准确", "细节清晰", "权衡分析", "技术前沿"]
        },
        "团队协作": {
            "keywords": ["团队", "合作", "沟通", "反馈", "配合", "支持", "共同"],
            "indicators": ["他人视角", "主动沟通", "冲突处理", "互补协作"]
        },
        "创新能力": {
            "keywords": ["创新", "想法", "尝试", "突破", "新的", "改进", "优化"],
            "indicators": ["思维新颖", "敢于尝试", "敢于挑战", "提出新解"]
        },
        "学习能力": {
            "keywords": ["学习", "提升", "成长", "改进", "进步", "新知", "反思"],
            "indicators": ["乐于学习", "举一反三", "快速掌握", "自我认知"]
        },
        "领导力": {
            "keywords": ["领导", "管理", "决策", "影响", "指导", "引导", "推动"],
            "indicators": ["主动担当", "目标清晰", "执行力强", "他人信任"]
        },
        "战略思维": {
            "keywords": ["战略", "规划", "目标", "方向", "长期", "全局", "前景"],
            "indicators": ["眼光长远", "统筹全局", "目标导向", "价值判断"]
        },
        "用户洞察": {
            "keywords": ["用户", "客户", "需求", "体验", "痛点", "场景", "行为"],
            "indicators": ["需求精准", "深度理解", "同理心强", "用户为中心"]
        },
        "文化契合": {
            "keywords": ["价值观", "文化", "理念", "原则", "信念", "追求"],
            "indicators": ["价值观一致", "使命认同", "长期承诺"]
        }
    }
    
    # 评估特质与特质关键词的映射
    EVALUATION_TRAIT_MAPPING = {
        "沟通能力": ["communication", "expression", "clarity"],
        "问题解决": ["problem_solving", "solution_design"],
        "技术深度": ["technical_depth", "expertise"],
        "团队协作": ["teamwork", "collaboration"],
        "创新能力": ["innovation", "creativity"],
        "学习能力": ["learning", "growth"],
        "领导力": ["leadership", "management"],
        "战略思维": ["strategic_thinking", "vision"],
        "用户洞察": ["user_insight", "customer_focus"],
        "文化契合": ["culture_fit", "values"]
    }
    
    def extract_scores(self, evaluation: Dict[str, Any]) -> Dict[str, float]:
        """
        从 LLM 评估结果中提取特质评分
        
        Args:
            evaluation: LLM 返回的评估结果
        
        Returns:
            {"特质名": 分数, ...}
        """
        
        scores = {}
        
        # 优先取 LLM 直接返回的评分
        if "scores" in evaluation and isinstance(evaluation["scores"], dict):
            scores = evaluation["scores"]
        
        # 如果没有评分，尝试从其他字段推导
        if not scores:
            scores = self._infer_scores_from_evaluation(evaluation)
        
        # 确保所有默认特质都有分数
        for trait in self.TRAIT_DIMENSIONS.keys():
            if trait not in scores:
                scores[trait] = 5.0  # 默认中等分数
        
        # 限制分数在 1-10 之间
        for trait in scores:
            scores[trait] = max(1.0, min(10.0, scores[trait]))
        
        return scores
    
    def _infer_scores_from_evaluation(self, evaluation: Dict[str, Any]) -> Dict[str, float]:
        """从评估文本推导分数"""
        
        scores = {}
        
        # 构建评估文本
        eval_text = ""
        if "strengths" in evaluation:
            eval_text += " ".join(evaluation["strengths"]) + " "
        if "analysis" in evaluation:
            eval_text += evaluation["analysis"] + " "
        
        eval_text = eval_text.lower()
        
        # 针对每个特质的关键词进行评分
        for trait, dimension in self.TRAIT_DIMENSIONS.items():
            # 计算关键词出现频率
            keyword_count = sum(
                eval_text.count(keyword)
                for keyword in dimension["keywords"]
            )
            
            # 计算指标词出现频率
            indicator_count = sum(
                eval_text.count(indicator)
                for indicator in dimension["indicators"]
            )
            
            # 推导分数 (基础 5.0 + 关键词和指标词的贡献)
            score = 5.0 + keyword_count * 0.5 + indicator_count * 1.0
            scores[trait] = min(10.0, score)
        
        return scores
    
    def detect_patterns(
        self,
        response: str,
        evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        识别候选人的行为模式
        
        Args:
            response: 候选人的回答文本
            evaluation: LLM 的评估结果
        
        Returns:
            [
                {
                    "id": "pattern_1",
                    "name": "模式名称",
                    "description": "模式描述",
                    "confidence": 78,
                    "color": "#67c23a"
                },
                ...
            ]
        """
        
        patterns = []
        colors = ["#67c23a", "#409eff", "#e6a23c", "#f56c6c", "#909399"]
        color_idx = 0
        
        # 从评估中获取优势
        if "strengths" in evaluation and isinstance(evaluation["strengths"], list):
            for strength in evaluation["strengths"][:3]:  # 最多3个模式
                # 计算置信度
                confidence = self._calculate_confidence(strength, response)
                
                patterns.append({
                    "id": f"pattern_{len(patterns) + 1}",
                    "name": strength,
                    "description": self._get_pattern_description(strength),
                    "confidence": confidence,
                    "color": colors[color_idx % len(colors)]
                })
                color_idx += 1
        
        # 自动检测其他模式
        detected = self._auto_detect_patterns(response)
        for pattern in detected[:2]:  # 最多再加 2 个
            if len(patterns) < 5:  # 总共不超过 5 个
                patterns.append({
                    "id": f"pattern_{len(patterns) + 1}",
                    "name": pattern["name"],
                    "description": pattern["description"],
                    "confidence": pattern["confidence"],
                    "color": colors[color_idx % len(colors)]
                })
                color_idx += 1
        
        return patterns
    
    def _calculate_confidence(self, pattern_name: str, response: str) -> int:
        """计算模式的置信度"""
        
        # 简单的启发式方法
        response_lower = response.lower()
        pattern_lower = pattern_name.lower()
        
        # 如果模式关键词在回答中出现
        keyword_matches = sum(
            1 for word in pattern_lower.split()
            if word in response_lower and len(word) > 2
        )
        
        # 基础置信度 60 + 关键词匹配加分
        confidence = 60 + min(keyword_matches * 5, 30)
        
        return min(confidence, 100)
    
    def _get_pattern_description(self, pattern_name: str) -> str:
        """获取模式描述"""
        
        descriptions = {
            "结构化思维": "回答展现出清晰的逻辑结构，思路井然有序",
            "实例驱动": "善于用具体案例和细节支撑观点，论证有力",
            "系统思维": "能够从全局和联系角度分析问题，考虑周全",
            "用户导向": "始终以用户需求和体验为中心，视角独特",
            "创新思维": "提出了新颖独特的想法和解决方案",
            "团队意识": "强调团队协作和沟通的重要性，有大局观",
            "自我反思": "能够客观认识自己的不足和改进方向",
            "持续学习": "表现出对学习和进步的主动追求和热情",
            "问题导向": "能够迅速定位问题的核心，抓住要点",
            "数据驱动": "决策和判断建立在数据和事实基础之上"
        }
        
        return descriptions.get(
            pattern_name,
            f"{pattern_name}的表现突出，在这个方面展现了优势"
        )
    
    def _auto_detect_patterns(self, response: str) -> List[Dict[str, Any]]:
        """自动检测回答中的模式"""
        
        detected = []
        response_lower = response.lower()
        
        # 检测模式的规则
        pattern_rules = {
            "第一": ("结构化思维", ["首先", "其次", "最后", "第一", "第二"]),
            "具体例子": ("实例驱动", ["例如", "比如", "具体来说", "我之前", "一个真实的例子"]),
            "全局": ("系统思维", ["整体", "全局", "系统", "链路", "环节", "步骤"]),
            "用户": ("用户导向", ["用户", "客户", "需求", "体验", "场景"]),
            "新": ("创新思维", ["创新", "新的", "尝试", "突破", "改进"]),
            "团队": ("团队意识", ["团队", "协作", "合作", "沟通", "配合"]),
            "不足": ("自我反思", ["不足", "缺点", "改进", "学习", "进步"]),
            "学习": ("持续学习", ["学习", "提升", "掌握", "深入", "钻研"])
        }
        
        for key, (pattern_name, keywords) in pattern_rules.items():
            # 检查关键词是否在回答中出现
            keyword_count = sum(
                response_lower.count(kw)
                for kw in keywords
            )
            
            if keyword_count > 0:
                confidence = min(70 + keyword_count * 5, 95)
                detected.append({
                    "name": pattern_name,
                    "description": self._get_pattern_description(pattern_name),
                    "confidence": confidence
                })
        
        # 按置信度排序
        detected.sort(key=lambda x: x["confidence"], reverse=True)
        
        return detected
    
    def calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """计算总体评分"""
        
        if not scores:
            return 0.0
        
        # 按重要性加权
        weights = {
            "沟通能力": 1.1,
            "问题解决": 1.2,
            "技术深度": 1.1,
            "团队协作": 1.0,
            "创新能力": 1.0,
            "学习能力": 0.9,
            "领导力": 1.2,
            "战略思维": 1.1,
            "用户洞察": 1.0,
            "文化契合": 0.8
        }
        
        total_weight = sum(
            weights.get(trait, 1.0)
            for trait in scores.keys()
        )
        
        weighted_sum = sum(
            score * weights.get(trait, 1.0)
            for trait, score in scores.items()
        )
        
        overall = weighted_sum / total_weight if total_weight > 0 else 0
        
        return round(overall, 1)
    
    @staticmethod
    def match_job_score(
        candidate_scores: Dict[str, float],
        job_required_traits: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        计算候选人与岗位的匹配度
        
        Args:
            candidate_scores: 候选人的特质评分
            job_required_traits: 岗位需求的特质（重要度权重）
        
        Returns:
            {
                "match_score": 0-100,
                "matched_traits": [...],
                "gap_traits": [...]
            }
        """
        
        matched = []
        gaps = []
        
        for trait, required_level in job_required_traits.items():
            candidate_level = candidate_scores.get(trait, 5.0)
            
            if candidate_level >= required_level:
                matched.append({
                    "trait": trait,
                    "candidate_score": candidate_level,
                    "required_score": required_level,
                    "gap": candidate_level - required_level
                })
            else:
                gaps.append({
                    "trait": trait,
                    "candidate_score": candidate_level,
                    "required_score": required_level,
                    "gap": required_level - candidate_level
                })
        
        # 计算匹配度
        if not job_required_traits:
            match_score = 50
        else:
            match_rate = len(matched) / len(job_required_traits) * 100
            score_gap = sum(t["gap"] for t in gaps) / len(gaps) if gaps else 0
            match_score = match_rate - (score_gap * 5)
            match_score = max(0, min(100, match_score))
        
        return {
            "match_score": round(match_score, 1),
            "matched_traits": matched,
            "gap_traits": gaps,
            "match_count": len(matched),
            "total_traits": len(job_required_traits)
        }


if __name__ == "__main__":
    evaluator = TraitEvaluator()
    
    # 示例评估结果
    sample_evaluation = {
        "scores": {
            "沟通能力": 8,
            "问题解决": 7.5,
            "技术深度": 8.5
        },
        "strengths": ["结构化思维", "实例驱动", "系统思维"],
        "analysis": "候选人的回答清晰有条理，能够准确把握问题的要点..."
    }
    
    sample_response = "首先，我需要理解这个问题的背景。其次，我会分析可能的解决方案。例如，在我之前的项目中..."
    
    # 测试
    scores = evaluator.extract_scores(sample_evaluation)
    patterns = evaluator.detect_patterns(sample_response, sample_evaluation)
    
    print("分数:", scores)
    print("模式:", patterns)
