"""
评估系统初始化脚本
创建示例数据，用于测试和演示
"""

from database import SessionLocal, engine, Base
from models.assessment import AssessmentRecord, CandidatePersonalityProfile, AssessmentMatchAnalysis, AssessmentStatus
from models.job import Job
from models.candidate import Candidate
from models.user import User

import json
from datetime import datetime, timedelta


def init_jobs(db):
    """初始化示例岗位"""
    
    # Big Five 特质期望值示例
    # 范围：1-10，数值越高表示期望该特质评分越高
    
    jobs_data = [
        {
            "name": "高级前端工程师",
            "description": "领导前端技术团队，负责核心基础设施建设，参与架构决策",
            "company": "科技公司A",
            "category": "技术部",
            "city": "北京",
            "salary_min": 25,
            "salary_max": 35,
            "required_traits": {
                "外向性": 7,      # 需要较强的沟通和表达
                "宜人性": 6,      # 需要一定的团队合作
                "尽责性": 9,      # 需要高度责任心（高）
                "神经质": 3,      # 需要情绪稳定（低分更好）
                "开放性": 8       # 需要创新思维和学习能力
            }
        },
        {
            "name": "产品经理",
            "description": "负责C端产品规划与迭代，与设计、技术团队协作",
            "company": "互联网公司B",
            "category": "产品部",
            "city": "杭州",
            "salary_min": 20,
            "salary_max": 30,
            "required_traits": {
                "外向性": 8,      # 需要强沟通能力（高）
                "宜人性": 7,      # 需要较强团队合作
                "尽责性": 7,      # 需要计划性和执行力
                "神经质": 4,      # 需要一定的抗压能力
                "开放性": 8       # 需要创新思维
            }
        },
        {
            "name": "技术总监",
            "description": "领导技术部门战略规划，管理技术团队，推动技术创新",
            "company": "大型互联网公司",
            "category": "技术部",
            "city": "深圳",
            "salary_min": 35,
            "salary_max": 50,
            "required_traits": {
                "外向性": 7,      # 需要领导力和表达
                "宜人性": 6,      # 需要管理能力
                "尽责性": 9,      # 需要高度责任心（高）
                "神经质": 2,      # 需要成熟稳定
                "开放性": 9       # 需要战略眼光和创新
            }
        },
        {
            "name": "用户研究员",
            "description": "进行用户研究和数据分析，支持产品决策",
            "company": "设计咨询公司C",
            "category": "产品部",
            "city": "北京",
            "salary_min": 15,
            "salary_max": 25,
            "required_traits": {
                "外向性": 7,      # 需要用户访谈能力
                "宜人性": 8,      # 需要同理心（高）
                "尽责性": 8,      # 需要严谨性
                "神经质": 5,      # 有一定敏感度
                "开放性": 8       # 需要学习能力
            }
        },
        {
            "name": "后端工程师",
            "description": "开发和维护后端系统，编写高质量代码，参与系统设计",
            "company": "技术公司D",
            "category": "技术部",
            "city": "上海",
            "salary_min": 18,
            "salary_max": 28,
            "required_traits": {
                "外向性": 5,      # 不需要过度社交
                "宜人性": 6,      # 需要基本合作能力
                "尽责性": 9,      # 需要高度责任心（高）
                "神经质": 3,      # 需要稳定心态
                "开放性": 7       # 需要学习新技术
            }
        },
    ]
    
    existing_jobs = db.query(Job).count()
    if existing_jobs > 0:
        print(f"数据库中已有 {existing_jobs} 个岗位，跳过初始化")
        return
    
    for job_data in jobs_data:
        job = Job(
            name=job_data["name"],
            description=job_data["description"],
            company=job_data["company"],
            category=job_data["category"],
            city=job_data["city"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            required_traits=job_data["required_traits"],
            creator_id=1  # 假设管理员用户ID为1
        )
        db.add(job)
    
    db.commit()
    print(f"✅ 成功创建 {len(jobs_data)} 个岗位")


def init_candidate_profiles(db):
    """初始化示例候选人心理特质"""
    
    profiles_data = [
        {
            "candidate_id": "cand_001",
            "trait_extroversion": 7.5,
            "trait_agreeableness": 6.8,
            "trait_conscientiousness": 8.9,
            "trait_neuroticism": 3.2,
            "trait_openness": 8.1,
            "assessment_count": 2
        },
        {
            "candidate_id": "cand_002",
            "trait_extroversion": 8.2,
            "trait_agreeableness": 7.5,
            "trait_conscientiousness": 7.6,
            "trait_neuroticism": 4.1,
            "trait_openness": 7.9,
            "assessment_count": 3
        },
        {
            "candidate_id": "cand_003",
            "trait_extroversion": 5.5,
            "trait_agreeableness": 6.2,
            "trait_conscientiousness": 9.2,
            "trait_neuroticism": 2.8,
            "trait_openness": 7.3,
            "assessment_count": 1
        },
    ]
    
    existing_profiles = db.query(CandidatePersonalityProfile).count()
    if existing_profiles > 0:
        print(f"数据库中已有 {existing_profiles} 个候选人心理特质记录，跳过初始化")
        return
    
    for profile_data in profiles_data:
        profile = CandidatePersonalityProfile(**profile_data)
        db.add(profile)
    
    db.commit()
    print(f"✅ 成功创建 {len(profiles_data)} 个候选人心理特质记录")


def init_assessment_records(db):
    """初始化示例评估记录"""
    
    existing_records = db.query(AssessmentRecord).count()
    if existing_records > 0:
        print(f"数据库中已有 {existing_records} 个评估记录，跳过初始化")
        return
    
    # 为示例候选人创建评估记录
    records_data = [
        {
            "candidate_id": "cand_001",
            "job_id": 1,
            "job_title": "高级前端工程师",
            "assessment_status": AssessmentStatus.COMPLETED,
            "assessment_mode": "immersive",
            "match_score": 87.5,
            "conversation_summary": "候选人在对话中展现了出色的问题分析能力和技术深度。能够清晰地解释复杂的技术概念，并且对新技术充满热情。团队合作意识较强。",
            "total_rounds": 28,
            "duration_minutes": 17.5,
            "conversation_depth": 8.7,
            "roles_participated": ["hr", "tech_lead", "product"],
            "overall_impression": "强烈推荐进一步沟通，候选人各项指标均符合岗位要求"
        },
        {
            "candidate_id": "cand_001",
            "job_id": 3,
            "job_title": "技术总监",
            "assessment_status": AssessmentStatus.COMPLETED,
            "assessment_mode": "immersive",
            "match_score": 79.2,
            "conversation_summary": "候选人展现了良好的战略视野和领导潜力。在与CTO的对话中，能够从多个维度思考技术方向。但在人员管理经验上有所欠缺。",
            "total_rounds": 32,
            "duration_minutes": 19.2,
            "conversation_depth": 8.3,
            "roles_participated": ["hr", "tech_lead", "cto"],
            "overall_impression": "推荐考虑，但需要在管理经验上有所补强"
        },
        {
            "candidate_id": "cand_002",
            "job_id": 2,
            "job_title": "产品经理",
            "assessment_status": AssessmentStatus.COMPLETED,
            "assessment_mode": "immersive",
            "match_score": 84.3,
            "conversation_summary": "候选人具有出色的沟通能力和产品思维。能够从用户角度思考问题，并能够与技术团队有效沟通。创新思维突出。",
            "total_rounds": 30,
            "duration_minutes": 18.5,
            "conversation_depth": 8.5,
            "roles_participated": ["hr", "product", "tech_lead"],
            "overall_impression": "非常推荐，各方面能力与岗位匹配度很高"
        },
    ]
    
    for record_data in records_data:
        record = AssessmentRecord(**record_data)
        db.add(record)
    
    db.commit()
    print(f"✅ 成功创建 {len(records_data)} 个评估记录")
    
    # 创建匹配分析
    db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id.in_(["cand_001", "cand_002", "cand_003"])
    ).all()
    
    analysis_data = [
        {
            "assessment_record_id": 1,
            "strengths": ["技术深度扎实 - 能独立解决复杂技术问题", "沟通能力强 - 能清晰表达和倾听", "学习能力强 - 对新技术充满热情", "责任意识高 - 对工作质量有严格要求"],
            "gaps": ["项目管理经验不足", "大团队协作经验相对较少", "需要进一步提升系统架构思维"],
            "recommendations": ["建议参与更多大型项目的团队合作，积累项目管理经验", "推荐学习系统架构和服务设计相关知识", "可考虑参与开源项目，扩展技术视野", "建议定期参加技术分享和交流活动"]
        },
        {
            "assessment_record_id": 2,
            "strengths": ["战略视野较好 - 能从全局思考技术方向", "领导潜力 - 能够激发团队创新"],
            "gaps": ["人员管理经验不足", "大规模团队管理经验缺乏"],
            "recommendations": ["建议参与更多管理相关的培训和实践", "可考虑在现有项目中担当小组组长角色"]
        },
        {
            "assessment_record_id": 3,
            "strengths": ["沟通能力优秀 - 内外部沟通能力都很强", "产品思维清晰 - 能从用户角度思考问题", "创新思维突出 - 能够提出新颖的解决方案"],
            "gaps": ["数据分析能力需提升", "部分技术细节理解可更深入"],
            "recommendations": ["建议强化数据分析和用户研究能力", "可考虑与设计和技术团队进行定期协作学习"]
        }
    ]
    
    for analysis in analysis_data:
        match_analysis = AssessmentMatchAnalysis(**analysis)
        db.add(match_analysis)
    
    db.commit()
    print(f"✅ 成功创建 {len(analysis_data)} 个匹配分析记录")


def init_database():
    """初始化数据库"""
    print("🚀 正在初始化评估系统数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    db = SessionLocal()
    try:
        init_jobs(db)
        init_candidate_profiles(db)
        init_assessment_records(db)
        print("\n✨ 评估系统初始化完成！")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
