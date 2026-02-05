#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化脚本 - 向数据库插入示例情景
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, Base, engine
from models.hr_agent import Scenario

def init_scenarios():
    """初始化示例情景"""
    
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 清空现有数据
        db.query(Scenario).delete()
        db.commit()
        
        # 插入示例情景
        scenarios = [
            Scenario(
                id="scenario_001",
                title="项目延期应对",
                description="""
                假设你负责一个重要项目，原定交付期限是两周后。
                
                最近，你的团队发现一个关键的技术障碍，可能需要额外的两周时间来解决。
                同时，客户已经在期待这个功能的上线，他们对延期非常敏感。
                
                作为项目负责人，你需要立即采取行动。你的任务是：
                1. 立即向相关方（包括客户和内部管理层）沟通
                2. 制定一个可行的解决方案
                3. 保持团队的士气和信心
                
                请告诉我：在这种情况下，你会如何处理？
                """,
                target_traits=["责任心", "宜人性"],
                max_rounds=3,
                instructions="""
                你是一位资深的人力资源评估专家。
                
                正在评估候选人的应对能力，重点关注：
                1. 责任心 - 候选人是否主动承担责任，提出切实可行的方案
                2. 宜人性 - 候选人是否重视沟通，考虑他人的感受
                
                请根据候选人的回答，生成有针对性的追问，逐步深入了解他们的特质。
                """
            ),
            Scenario(
                id="scenario_002",
                title="团队冲突处理",
                description="""
                你的团队中两位核心成员因为技术选型方案产生了严重分歧。
                
                - 一位主张采用已经成熟的技术栈，以确保项目按时完成
                - 另一位则坚持采用新兴技术，认为这样能提高系统的长期竞争力
                
                双方都有各自的合理性，但现在陷入了僵持。
                你已经感觉到团队的协作气氛在恶化，其他成员也开始站队。
                这种状况继续下去，可能会影响项目进度。
                
                作为项目经理，你将如何处理这个冲突？
                """,
                target_traits=["情绪稳定性", "宜人性"],
                max_rounds=3,
                instructions="""
                评估候选人在处理团队冲突时的表现。
                
                重点关注：
                1. 情绪稳定性 - 在压力下是否保持冷静理性
                2. 宜人性 - 是否尊重不同观点，能否找到共识
                """
            ),
            Scenario(
                id="scenario_003",
                title="工作量突增应对",
                description="""
                在一个看似平静的周一早上，你突然收到来自CEO的消息：
                
                "一个重要客户要求在本周五之前演示一个新的功能模块。
                这个需求很急迫，直接关系到一个100万的合同。"
                
                但事实是：
                - 你的团队目前还在处理两个项目的关键阶段
                - 这个新功能的需求还不清楚，需要与客户多次沟通
                - 加班文化在你的团队中并不流行，大家都已经很疲惫
                
                你需要在短时间内做出决策。你的计划是什么？
                """,
                target_traits=["责任心", "情绪稳定性"],
                max_rounds=3
            )
        ]
        
        for scenario in scenarios:
            # 检查是否已存在
            existing = db.query(Scenario).filter(Scenario.id == scenario.id).first()
            if not existing:
                db.add(scenario)
        
        db.commit()
        print("✓ 示例情景已插入数据库")
        
        # 显示插入的情景
        all_scenarios = db.query(Scenario).all()
        print(f"\n当前数据库中有 {len(all_scenarios)} 个情景：")
        for s in all_scenarios:
            print(f"  - {s.id}: {s.title}")
            print(f"    目标特质: {s.target_traits}")
            print()
        
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("初始化 HR-Agent 示例情景")
    print("=" * 60)
    init_scenarios()
    print("\n初始化完成！")
