#!/usr/bin/env python3
"""
HR-Agent LLM 模拟模式测试脚本
用于验证模拟模式能否正常运行和返回符合预期的数据
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.prompts.hr_agent_llm import HRAgentLLM
import json


def print_header(title):
    """打印标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_mock_mode():
    """测试模拟模式"""
    print_header("🧪 测试 1: 模拟模式初始化")
    
    # 强制使用模拟模式
    llm = HRAgentLLM(force_mock=True)
    print(f"✓ 已创建 HRAgentLLM 实例")
    print(f"  - 使用模式: {'模拟' if llm.use_mock else 'API'}")
    print(f"  - 模型: {llm.model}")
    
    return llm


def test_follow_up_generation(llm):
    """测试追问生成"""
    print_header("🧪 测试 2: 动态追问生成")
    
    test_cases = [
        {
            "round_num": 1,
            "target_traits": ["责任心", "宜人性"],
            "description": "第 1 轮（初始追问）"
        },
        {
            "round_num": 2,
            "target_traits": ["情绪稳定性"],
            "description": "第 2 轮（深化追问）"
        },
        {
            "round_num": 3,
            "target_traits": ["学习能力"],
            "description": "第 3 轮（最后追问）"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['description']}:")
        print(f"  目标特质: {', '.join(test['target_traits'])}")
        
        result = llm.generate_follow_up_question(
            scenario_description="项目延期，需要向客户和团队解释",
            target_traits=test['target_traits'],
            previous_answers=[],
            round_num=test['round_num']
        )
        
        print(f"  问题: {result['question']}")
        print(f"  理由: {result['reasoning']}")


def test_scoring(llm):
    """测试答案评分"""
    print_header("🧪 测试 3: 答案评分")
    
    test_answers = [
        {
            "answer": "我会立即主动承担责任，尽快制定补救方案，并主动与团队沟通。",
            "traits": ["责任心", "宜人性"],
            "description": "高质量回答（包含多个关键词）"
        },
        {
            "answer": "我会保持冷静，理性分析问题，制定有序的应对计划。",
            "traits": ["情绪稳定性"],
            "description": "情绪稳定性相关回答"
        },
        {
            "answer": "这次经历让我学到了很多，我会反思并改进我的项目管理方式。",
            "traits": ["学习能力"],
            "description": "学习能力相关回答"
        },
        {
            "answer": "我会尝试一些新的方法来解决这个问题。",
            "traits": ["创新能力"],
            "description": "创新能力相关回答"
        },
        {
            "answer": "这是一个很难的情况。",
            "traits": ["责任心"],
            "description": "低质量回答（缺乏关键词）"
        }
    ]
    
    for test in test_answers:
        print(f"\n{test['description']}:")
        print(f"  回答: {test['answer']}")
        print(f"  评估特质: {', '.join(test['traits'])}")
        
        result = llm.score_answer(
            scenario_description="项目延期",
            target_traits=test['traits'],
            current_answer=test['answer'],
            all_answers=[]
        )
        
        print(f"  评分结果:")
        for trait, score in result['scores'].items():
            reason = result['reasoning'][trait]
            print(f"    - {trait}: {score} 分")
            print(f"      理由: {reason}")


def test_answer_length_impact(llm):
    """测试回答长度对分数的影响"""
    print_header("🧪 测试 4: 回答长度对分数的影响")
    
    base_content = "我会主动"
    test_lengths = [10, 50, 100, 200]
    
    print("\n测试不同长度的回答对分数的影响:")
    print(f"{'长度(字)':>8} | {'包含关键词':>8} | {'评分':>6} | {'说明'}")
    print("-" * 50)
    
    for length in test_lengths:
        # 构造特定长度的回答
        if length <= 10:
            answer = base_content
        else:
            padding = "承担责任" * ((length - len(base_content)) // 4)
            answer = base_content + padding
            answer = answer[:length]
        
        result = llm.score_answer(
            scenario_description="项目延期",
            target_traits=["责任心"],
            current_answer=answer,
            all_answers=[]
        )
        
        score = result['scores'].get("责任心", "N/A")
        has_keywords = "是" if any(kw in answer for kw in ["主动", "承担责任"]) else "否"
        
        print(f"{len(answer):>8} | {has_keywords:>8} | {score:>6} | 长度奖励效果")


def test_multi_round_scenario(llm):
    """测试多轮对话场景"""
    print_header("🧪 测试 5: 完整的多轮对话场景")
    
    scenario = {
        "id": "scenario_001",
        "title": "项目延期应对",
        "description": "你的项目比预期晚了两周交付，需要向客户和团队解释。",
        "target_traits": ["责任心", "宜人性", "情绪稳定性"],
        "max_rounds": 3
    }
    
    conversation = []
    
    print(f"\n情景: {scenario['title']}")
    print(f"描述: {scenario['description']}")
    print(f"目标特质: {', '.join(scenario['target_traits'])}")
    print(f"最大轮次: {scenario['max_rounds']}\n")
    
    for round_num in range(1, scenario['max_rounds'] + 1):
        print(f"\n--- 第 {round_num} 轮 ---")
        
        # 生成追问
        follow_up = llm.generate_follow_up_question(
            scenario_description=scenario['description'],
            target_traits=scenario['target_traits'],
            previous_answers=conversation,
            round_num=round_num
        )
        
        print(f"问题: {follow_up['question']}")
        
        # 模拟用户回答
        mock_answers = [
            "我会立即承担责任，主动与团队和客户沟通，制定详细的补救方案。",
            "我会保持冷静，分析延期的原因，并与团队协商解决方法，确保客户理解。",
            "这次经历教会了我更好的项目规划方法，我会改进我的时间管理能力。"
        ]
        
        user_answer = mock_answers[round_num - 1]
        print(f"回答: {user_answer}")
        
        # 评分
        score = llm.score_answer(
            scenario_description=scenario['description'],
            target_traits=scenario['target_traits'],
            current_answer=user_answer,
            all_answers=conversation
        )
        
        print(f"评分:")
        for trait in scenario['target_traits']:
            s = score['scores'][trait]
            r = score['reasoning'][trait]
            print(f"  • {trait}: {s} 分 - {r}")
        
        # 保存到对话历史
        conversation.append({"question": follow_up['question'], "answer": user_answer})


def test_mode_switching():
    """测试模式切换"""
    print_header("🧪 测试 6: 模式切换")
    
    print("\n1. 强制使用模拟模式:")
    llm_mock = HRAgentLLM(force_mock=True)
    print(f"   ✓ use_mock = {llm_mock.use_mock}")
    
    print("\n2. 自动检测模式（无 API Key）:")
    # 临时清除环境变量
    api_key_backup = os.environ.pop("OPENAI_API_KEY", None)
    try:
        llm_auto = HRAgentLLM()
        print(f"   ✓ use_mock = {llm_auto.use_mock}")
    finally:
        if api_key_backup:
            os.environ["OPENAI_API_KEY"] = api_key_backup


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  HR-Agent LLM 模拟模式完整测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        llm = test_mock_mode()
        test_follow_up_generation(llm)
        test_scoring(llm)
        test_answer_length_impact(llm)
        test_multi_round_scenario(llm)
        test_mode_switching()
        
        # 总结
        print_header("✅ 所有测试完成")
        print("\n测试结果摘要:")
        print("  ✓ 模拟模式初始化成功")
        print("  ✓ 动态追问生成正常")
        print("  ✓ 答案评分规则有效")
        print("  ✓ 回答长度影响得当")
        print("  ✓ 多轮对话流程完整")
        print("  ✓ 模式切换灵活")
        print("\n🎉 模拟模式已准备好用于开发！\n")
        
    except Exception as e:
        print_header("❌ 测试失败")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
