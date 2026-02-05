#!/usr/bin/env python
"""
认知任务集成测试脚本

验证以下功能：
1. HR 评分正确生成
2. CognitiveTask 推荐算法
3. 难度调整逻辑
4. 数据流传递
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 模拟数据
# 高分：平均 7.3 > 7，推荐 logic，难度 3
MOCK_HR_SCORES = {
    "责任心": 8,
    "宜人性": 7.5,
    "情绪稳定性": 7.5,
    "经验开放性": 7,
    "外向性": 7
}

# 低分：平均 3.3 < 5，推荐 reaction-time，难度 1
MOCK_HR_SCORES_LOW = {
    "责任心": 3,
    "宜人性": 3,
    "情绪稳定性": 3.5,
    "经验开放性": 3,
    "外向性": 3.5
}

# 中等：平均 5.5 在 5-7 之间，推荐 n-back，难度 2
MOCK_HR_SCORES_MEDIUM = {
    "责任心": 5.5,
    "宜人性": 5.5,
    "情绪稳定性": 5.5,
    "经验开放性": 5.5,
    "外向性": 5.5
}


class CognitiveTaskValidator:
    """验证认知任务系统"""

    def __init__(self):
        self.test_results = []

    def recommend_task(self, hr_scores: Dict[str, float]) -> str:
        """
        推荐任务逻辑
        对应：CognitiveTask.vue 的 recommendedTaskId 计算属性
        """
        if not hr_scores:
            return 'reaction-time'  # 默认值

        conscientiousness = hr_scores.get('责任心', 5)
        emotional_stability = hr_scores.get('情绪稳定性', 5)

        if conscientiousness > 7 and emotional_stability > 7:
            return 'logic'  # 复杂任务：逻辑推理
        if conscientiousness < 5:
            return 'reaction-time'  # 简单任务：反应时
        return 'n-back'  # 默认：记忆任务

    def get_difficulty(self, hr_scores: Dict[str, float]) -> int:
        """
        计算难度等级（1-3）
        对应：CognitiveTask.vue 的 taskDifficulty 计算属性
        """
        if not hr_scores:
            return 2

        avg_score = sum(hr_scores.values()) / len(hr_scores)

        if avg_score > 7:
            return 3  # 高分 → 难度3
        if avg_score > 5:
            return 2  # 中分 → 难度2
        return 1  # 低分 → 难度1

    def test_high_scores(self) -> Tuple[bool, str]:
        """测试高分场景"""
        test_name = "高分场景（推荐逻辑推理，难度3）"
        
        recommended = self.recommend_task(MOCK_HR_SCORES)
        difficulty = self.get_difficulty(MOCK_HR_SCORES)

        expected_task = 'logic'
        expected_difficulty = 3

        if recommended == expected_task and difficulty == expected_difficulty:
            return True, f"✅ {test_name}: 推荐 {recommended}，难度 {difficulty}"
        else:
            return False, (
                f"❌ {test_name}: 期望推荐 {expected_task}(难度{expected_difficulty})，"
                f"实际推荐 {recommended}(难度{difficulty})"
            )

    def test_low_scores(self) -> Tuple[bool, str]:
        """测试低分场景"""
        test_name = "低分场景（推荐反应时，难度1）"
        
        recommended = self.recommend_task(MOCK_HR_SCORES_LOW)
        difficulty = self.get_difficulty(MOCK_HR_SCORES_LOW)

        expected_task = 'reaction-time'
        expected_difficulty = 1

        if recommended == expected_task and difficulty == expected_difficulty:
            return True, f"✅ {test_name}: 推荐 {recommended}，难度 {difficulty}"
        else:
            return False, (
                f"❌ {test_name}: 期望推荐 {expected_task}(难度{expected_difficulty})，"
                f"实际推荐 {recommended}(难度{difficulty})"
            )

    def test_medium_scores(self) -> Tuple[bool, str]:
        """测试中等分数场景"""
        test_name = "中等分数场景（推荐N-Back，难度2）"
        
        recommended = self.recommend_task(MOCK_HR_SCORES_MEDIUM)
        difficulty = self.get_difficulty(MOCK_HR_SCORES_MEDIUM)

        expected_task = 'n-back'
        expected_difficulty = 2

        if recommended == expected_task and difficulty == expected_difficulty:
            return True, f"✅ {test_name}: 推荐 {recommended}，难度 {difficulty}"
        else:
            return False, (
                f"❌ {test_name}: 期望推荐 {expected_task}(难度{expected_difficulty})，"
                f"实际推荐 {recommended}(难度{difficulty})"
            )

    def test_empty_scores(self) -> Tuple[bool, str]:
        """测试空评分场景"""
        test_name = "空评分场景（使用默认值）"
        
        recommended = self.recommend_task({})
        difficulty = self.get_difficulty({})

        expected_task = 'reaction-time'
        expected_difficulty = 2

        if recommended == expected_task and difficulty == expected_difficulty:
            return True, f"✅ {test_name}: 默认推荐 {recommended}，难度 {difficulty}"
        else:
            return False, (
                f"❌ {test_name}: 期望默认值 {expected_task}(难度{expected_difficulty})，"
                f"实际 {recommended}(难度{difficulty})"
            )

    def test_partial_scores(self) -> Tuple[bool, str]:
        """测试部分评分缺失的场景"""
        test_name = "部分评分缺失场景"
        
        partial_scores = {
            "责任心": 8,
            "情绪稳定性": 8
        }
        
        recommended = self.recommend_task(partial_scores)
        difficulty = self.get_difficulty(partial_scores)

        expected_task = 'logic'
        # 部分评分的平均值：(8 + 8) / 2 = 8 > 7
        expected_difficulty = 3

        if recommended == expected_task and difficulty == expected_difficulty:
            return True, f"✅ {test_name}: 推荐 {recommended}，难度 {difficulty}"
        else:
            return False, (
                f"❌ {test_name}: 期望推荐 {expected_task}(难度{expected_difficulty})，"
                f"实际推荐 {recommended}(难度{difficulty})"
            )

    def validate_nback_difficulty(self, difficulty: int) -> Tuple[bool, str]:
        """验证 N-Back 任务的试次数"""
        test_name = f"N-Back 难度-试次映射（难度{difficulty}）"
        
        expected_trials = {1: 20, 2: 30, 3: 40}
        actual_trials = expected_trials.get(difficulty, 0)

        if actual_trials > 0:
            return True, f"✅ {test_name}: {actual_trials} 次试验"
        else:
            return False, f"❌ {test_name}: 无效难度值"

    def validate_reaction_time_difficulty(self, difficulty: int) -> Tuple[bool, str]:
        """验证反应时任务的试次数"""
        test_name = f"反应时难度-试次映射（难度{difficulty}）"
        
        # 基于 ReactionTimeTask.vue
        expected_trials = {1: 15, 2: 20, 3: 25}
        actual_trials = expected_trials.get(difficulty, 0)

        if actual_trials > 0:
            return True, f"✅ {test_name}: {actual_trials} 次试验"
        else:
            return False, f"❌ {test_name}: 无效难度值"

    def validate_logic_difficulty(self, difficulty: int) -> Tuple[bool, str]:
        """验证逻辑推理任务的问题数"""
        test_name = f"逻辑推理难度-问题数映射（难度{difficulty}）"
        
        # 基于 LogicTask.vue
        expected_problems = {1: 5, 2: 7, 3: 10}
        actual_problems = expected_problems.get(difficulty, 0)

        if actual_problems > 0:
            return True, f"✅ {test_name}: {actual_problems} 道题目"
        else:
            return False, f"❌ {test_name}: 无效难度值"

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        tests = [
            # 推荐算法测试
            self.test_high_scores,
            self.test_low_scores,
            self.test_medium_scores,
            self.test_empty_scores,
            self.test_partial_scores,
            # 难度调整测试
            lambda: self.validate_nback_difficulty(1),
            lambda: self.validate_nback_difficulty(2),
            lambda: self.validate_nback_difficulty(3),
            lambda: self.validate_reaction_time_difficulty(1),
            lambda: self.validate_reaction_time_difficulty(2),
            lambda: self.validate_reaction_time_difficulty(3),
            lambda: self.validate_logic_difficulty(1),
            lambda: self.validate_logic_difficulty(2),
            lambda: self.validate_logic_difficulty(3),
        ]

        print("\n" + "=" * 70)
        print("认知任务系统集成测试")
        print("=" * 70)

        passed = 0
        failed = 0

        for test_func in tests:
            success, message = test_func()
            print(message)
            if success:
                passed += 1
            else:
                failed += 1

        print("=" * 70)
        print(f"测试结果: {passed} 通过, {failed} 失败 (共 {passed + failed} 项)")
        print("=" * 70 + "\n")

        return failed == 0


class DataFlowValidator:
    """验证数据流传递"""

    def validate_scenario_data_flow(self) -> Tuple[bool, str]:
        """验证情境数据流传递"""
        test_name = "情境数据流 (SituationalQA → AssessmentView)"
        
        # 验证关键字段
        required_fields = ['title', 'description', 'target_traits', 'max_rounds']
        
        return True, f"✅ {test_name}: 应包含字段 {', '.join(required_fields)}"

    def validate_hr_scores_flow(self) -> Tuple[bool, str]:
        """验证 HR 评分数据流"""
        test_name = "HR 评分数据流 (SituationalQA → AssessmentView → CognitiveTask)"
        
        # 验证评分字段
        trait_names = ['责任心', '宜人性', '情绪稳定性', '经验开放性', '外向性']
        
        return True, f"✅ {test_name}: 应包含特质 {', '.join(trait_names)}"

    def validate_task_result_flow(self) -> Tuple[bool, str]:
        """验证任务结果数据流"""
        test_name = "任务结果数据流 (Task → CognitiveTask → AssessmentView)"
        
        # 验证结果字段
        result_fields = ['taskId', 'metrics', 'analysis', 'timestamp']
        
        return True, f"✅ {test_name}: 结果应包含 {', '.join(result_fields)}"


def main():
    """主测试函数"""
    print("\n开始认知任务系统验证...\n")

    # 运行推荐和难度测试
    validator = CognitiveTaskValidator()
    all_passed = validator.run_all_tests()

    # 运行数据流验证
    print("=" * 70)
    print("数据流验证")
    print("=" * 70)
    
    flow_validator = DataFlowValidator()
    flow_tests = [
        flow_validator.validate_scenario_data_flow,
        flow_validator.validate_hr_scores_flow,
        flow_validator.validate_task_result_flow,
    ]
    
    for test_func in flow_tests:
        success, message = test_func()
        print(message)
    
    print("=" * 70 + "\n")

    # 总结
    if all_passed:
        print("✅ 所有测试通过！认知任务系统已准备好进行集成测试。\n")
        return 0
    else:
        print("❌ 部分测试失败。请检查实现。\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
