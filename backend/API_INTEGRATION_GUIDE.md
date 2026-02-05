"""
后端 API 文档和集成指南
本文件详细说明前端与后端的 API 交互规范
"""

# ============================================
# API 端点总览
# ============================================

API_ENDPOINTS = {
    # 情景管理
    "GET /api/interview/scenarios": {
        "description": "获取所有可用的情景列表",
        "response": [
            {
                "id": "scenario_001",
                "title": "项目延期应对",
                "description": "情景描述文本",
                "target_traits": ["责任心", "宜人性"],
                "max_rounds": 3,
                "instructions": "HR-Agent的指导说明"
            }
        ]
    },
    
    "GET /api/interview/scenarios/{scenario_id}": {
        "description": "获取特定情景的详细信息",
        "params": {
            "scenario_id": "情景ID (例如: scenario_001)"
        },
        "response": {
            "id": "scenario_001",
            "title": "项目延期应对",
            "description": "详细的情景描述...",
            "target_traits": ["责任心", "宜人性"],
            "max_rounds": 3,
            "instructions": "HR-Agent指导说明"
        }
    },
    
    # 回答管理
    "POST /api/interview/save-response": {
        "description": "保存一轮的回答记录",
        "request": {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "round_num": 1,
            "question": "HR-Agent发出的问题",
            "answer": "候选人的回答",
            "answer_latency": 15.5,  # 秒数，可选
            "emotion": "neutral"      # 可选
        },
        "response": {
            "id": "resp_abc123",
            "message": "回答已保存"
        }
    },
    
    # 评分
    "POST /api/interview/score-answer": {
        "description": "对回答进行AI评分",
        "request": {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "response_id": "resp_abc123",
            "target_traits": ["责任心", "宜人性"],
            "answer": "候选人的回答内容"
        },
        "response": {
            "scores": {
                "责任心": 8.7,
                "宜人性": 8.5
            },
            "reasoning": {
                "责任心": "候选人表现出了主动承担责任的态度...",
                "宜人性": "强调了与他人的沟通和协作..."
            }
        }
    },
    
    # 追问
    "POST /api/interview/follow-up-question": {
        "description": "生成下一轮的追问问题",
        "request": {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "round_num": 2,
            "previous_answers": [
                {
                    "question": "第一轮的问题",
                    "answer": "第一轮的回答"
                }
            ]
        },
        "response": {
            "question": "根据你的回答，我想深入了解...",
            "reasoning": "追问的理由说明"
        }
    },
    
    # 评估总结
    "GET /api/interview/scenario-summary/{candidate_id}/{scenario_id}": {
        "description": "获取一个情景的最终评估总结",
        "params": {
            "candidate_id": "候选人ID",
            "scenario_id": "情景ID"
        },
        "response": {
            "candidate_id": "test_001",
            "scenario_id": "scenario_001",
            "trait_averages": {
                "责任心": 8.5,
                "宜人性": 8.3
            },
            "trait_reasonings": {
                "责任心": "总体评价：该候选人表现出了...",
                "宜人性": "总体评价：该候选人在团队..."
            },
            "summary": "候选人在该情景中表现综合评分为 8.4 分"
        }
    }
}

# ============================================
# 前端调用流程
# ============================================

INTERVIEW_FLOW = """
1. 加载情景 (onMounted)
   GET /api/interview/scenarios/{scenario_id}
   
2. 显示情景描述
   (显示 500ms，然后自动开始对话)
   
3. 自动发送开场白
   (不需要调用 API，直接显示预定义的开场白)
   
4. 对话循环 (对于每一轮，最多 3 轮):
   
   a) 用户输入回答
      - 测量耗时 (latency)
      - 收集情感状态 (emotion)
   
   b) 保存回答
      POST /api/interview/save-response
      ├─ candidate_id: 候选人ID
      ├─ scenario_id: 情景ID
      ├─ round_num: 轮次号
      ├─ question: 当前问题
      ├─ answer: 用户回答
      ├─ answer_latency: 回答耗时
      └─ emotion: 情感分析
      
      返回: { id: "resp_xxx", message: "..." }
   
   c) 评分
      POST /api/interview/score-answer
      ├─ candidate_id: 候选人ID
      ├─ scenario_id: 情景ID
      ├─ response_id: 来自上一步
      ├─ target_traits: 评分特质
      └─ answer: 用户回答
      
      返回: { scores: {...}, reasoning: {...} }
      
      注意：将 scores 和 reasoning 保存到答案对象中！
      这样 AI 分析面板就可以显示这些数据。
   
   d) 如果 round < max_rounds:
      生成追问
      POST /api/interview/follow-up-question
      ├─ candidate_id: 候选人ID
      ├─ scenario_id: 情景ID
      ├─ round_num: 下一轮号
      └─ previous_answers: 历史Q&A
      
      返回: { question: "...", reasoning: "..." }
      
      显示追问问题，继续对话 (go to 4a)
   
   e) 如果 round == max_rounds:
      显示完成提示，等待用户点击"完成情景"
5. 用户点击"完成情景"
   获取总结
   GET /api/interview/scenario-summary/{candidate_id}/{scenario_id}
   
   显示最终评估结果
   emit('next') 切换到下一步
"""

# ============================================
# 关键注意事项
# ============================================

KEY_POINTS = """
1. 数据结构：
   - 每个回答对象需要包含:
     * text: 回答文本
     * time: 回答时间
     * latency: 回答耗时
     * emotion: 情感分析（可选）
     * scores: AI 评分结果（来自 score-answer 端点）
     * reasoning: AI 分析理由（来自 score-answer 端点）

2. 时序要求：
   - 保存 (save-response) 必须先于评分 (score-answer)
   - 评分必须先于生成追问 (follow-up-question)
   - 所有 API 请求都是异步的，需要处理加载状态

3. 错误处理：
   - 情景不存在 (404): 显示错误提示，重新加载
   - API 失败: 显示"操作失败，请重试"并保持现有状态
   - 网络超时: 添加重试机制

4. 性能优化：
   - 使用 debounce 防止连续提交
   - 在 isLoading 期间禁用提交按钮
   - 使用 setTimeout 实现延迟，改善用户体验

5. 左侧面板（AI 分析面板）：
   - 从 answers.value 中提取最新的 scores 和 reasoning
   - 在每个 emit('update-answers') 时更新面板
   - 显示已分析的轮次、得分和理由
"""

# ============================================
# 数据库自动创建说明
# ============================================

DATABASE_NOTE = """
初始化步骤：

1. 首次运行时，SQLAlchemy 会自动创建所有必需的表：
   - scenarios: 情景模板
   - interview_responses: 回答记录
   - trait_scores: 评分记录
   - scenario_summaries: 情景总结

2. 初始化情景数据：
   运行: python init_scenarios.py
   
   这会插入 5 个预定义的情景：
   - scenario_001: 项目延期应对
   - scenario_002: 团队冲突解决
   - scenario_003: 技术决策与风险平衡
   - scenario_004: 个人职业发展与团队需要
   - scenario_005: 用户反馈与功能设计冲突

3. 验证后端准备：
   运行: python test_hr_agent_integration.py
   
   这会测试：
   - 情景数据是否存在
   - LLM 初始化是否成功
   - 生成追问是否工作
   - 评分是否工作
   - API 请求格式是否正确
"""

if __name__ == "__main__":
    import json
    
    print("="*80)
    print("🌐 后端 API 文档")
    print("="*80)
    
    print("\n📋 API 端点总览:")
    print("-"*80)
    for endpoint, info in API_ENDPOINTS.items():
        print(f"\n{endpoint}")
        print(f"  描述: {info['description']}")
        if 'params' in info:
            print(f"  参数: {json.dumps(info['params'], ensure_ascii=False, indent=12)}")
        if 'request' in info:
            print(f"  请求: {json.dumps(info['request'], ensure_ascii=False, indent=12)}")
        if 'response' in info:
            print(f"  响应: {json.dumps(info['response'], ensure_ascii=False, indent=12)}")
    
    print("\n\n🔄 前端调用流程:")
    print("-"*80)
    print(INTERVIEW_FLOW)
    
    print("\n\n⚠️ 关键注意事项:")
    print("-"*80)
    print(KEY_POINTS)
    
    print("\n\n📚 数据库初始化:")
    print("-"*80)
    print(DATABASE_NOTE)
    
    print("\n" + "="*80)
