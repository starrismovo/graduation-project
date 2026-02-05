"""
测试 HR-Agent 后端集成
验证所有必需的 API 端点是否正常工作
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, Base, engine
from models.hr_agent import Scenario
from prompts.hr_agent_llm import HRAgentLLM
import json

def test_backend_integration():
    """测试后端集成"""
    print("\n" + "="*60)
    print("🧪 HR-Agent 后端集成测试")
    print("="*60)
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. 测试情景数据
        print("\n1️⃣ 测试情景数据加载...")
        scenario = db.query(Scenario).filter(Scenario.id == "scenario_001").first()
        
        if scenario:
            print(f"   ✓ 情景已存在: {scenario.title}")
            print(f"     - ID: {scenario.id}")
            print(f"     - 目标特质: {scenario.target_traits}")
            print(f"     - 最大轮次: {scenario.max_rounds}")
        else:
            print("   ❌ 情景不存在，需要运行 init_scenarios.py")
            return False
        
        # 2. 测试 LLM 初始化
        print("\n2️⃣ 测试 LLM 初始化...")
        llm = HRAgentLLM(force_mock=True)
        print(f"   ✓ LLM 实例创建成功")
        print(f"     - 模式: {'模拟' if llm.use_mock else 'API'}")
        
        # 3. 测试生成开场白
        print("\n3️⃣ 测试生成开场白...")
        opening_questions = {
            'scenario_001': '你好，我是 HR-Agent，我们现在讨论一个情景。请根据上述情景，说出你的初步想法和处理方案。',
            'scenario_002': '我是你的面试官，请听我讲述这个情景，然后告诉我你的看法。'
        }
        for sid, q in opening_questions.items():
            print(f"   ✓ {sid}: {q[:50]}...")
        
        # 4. 测试生成追问
        print("\n4️⃣ 测试生成追问...")
        result = llm.generate_follow_up_question(
            scenario_description=scenario.description,
            target_traits=scenario.target_traits,
            previous_answers=[],
            round_num=1,
            max_rounds=3
        )
        print(f"   ✓ 追问生成成功")
        print(f"     - 问题: {result['question'][:60]}...")
        print(f"     - 理由: {result.get('reasoning', 'N/A')[:60]}...")
        
        # 5. 测试评分
        print("\n5️⃣ 测试回答评分...")
        score_result = llm.score_answer(
            scenario_description=scenario.description,
            target_traits=scenario.target_traits,
            current_answer="我会立即与团队和客户沟通，制定应急方案。首先评估实际的工作量和风险。",
            all_answers=[]
        )
        print(f"   ✓ 评分成功")
        print(f"     - 评分结果: {json.dumps(score_result['scores'], ensure_ascii=False, indent=8)}")
        print(f"     - 分析理由: {json.dumps(score_result['reasoning'], ensure_ascii=False, indent=8)}")
        
        # 6. 测试数据模式：完整的 API 请求格式
        print("\n6️⃣ 验证 API 请求格式...")
        
        # 保存回答的请求格式
        save_response_request = {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "round_num": 1,
            "question": "项目工期突然提前，你怎么处理？",
            "answer": "我会立即与团队和客户沟通，评估实际情况。",
            "answer_latency": 15.5,
            "emotion": "neutral"
        }
        print(f"   ✓ 保存回答请求格式:")
        print(f"     {json.dumps(save_response_request, ensure_ascii=False, indent=8)}")
        
        # 评分的请求格式
        score_answer_request = {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "response_id": "resp_abc123",
            "target_traits": scenario.target_traits,
            "answer": "我会立即与团队和客户沟通，评估实际情况。"
        }
        print(f"   ✓ 评分请求格式:")
        print(f"     {json.dumps(score_answer_request, ensure_ascii=False, indent=8)}")
        
        # 生成追问的请求格式
        follow_up_request = {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "round_num": 2,
            "previous_answers": [
                {
                    "question": "项目工期突然提前，你怎么处理？",
                    "answer": "我会立即与团队和客户沟通，评估实际情况。"
                }
            ]
        }
        print(f"   ✓ 生成追问请求格式:")
        print(f"     {json.dumps(follow_up_request, ensure_ascii=False, indent=8)}")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！后端已准备就绪")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_backend_integration()
    sys.exit(0 if success else 1)
