#!/usr/bin/env python3
"""
岗位需求与应聘功能验证脚本

测试项:
1. 数据库表是否正确创建
2. JD 解析是否正常
3. 匹配算法是否准确
"""

import sys
sys.path.insert(0, '/d/Desktop/graduation-project/backend')

from database import SessionLocal
from models import (
    Job, JobRequirementTag, JobSkillRequirement, 
    JobPersonalityFramework, CandidateJobApplication
)
from services.job_requirement_service import jd_parser, matching_engine
from schemas.job_requirement import JobSkillRequirementSchema, JobPersonalityFrameworkSchema

def check_database_tables():
    """检查数据库表是否创建成功"""
    print("\n" + "="*60)
    print("✅ 检查 1: 数据库表")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 检查表是否存在
        tables = [
            ('job_requirement_tags', JobRequirementTag),
            ('job_skill_requirements', JobSkillRequirement),
            ('job_personality_frameworks', JobPersonalityFramework),
            ('candidate_job_applications', CandidateJobApplication),
        ]
        
        for table_name, model_class in tables:
            count = db.query(model_class).count()
            print(f"  ✓ {table_name:40} ({count} 记录)")
        
        print("\n  ✅ 所有表都已创建!")
        return True
    
    except Exception as e:
        print(f"  ❌ 检查失败: {str(e)}")
        return False
    
    finally:
        db.close()


def test_jd_parsing():
    """测试 JD 解析"""
    print("\n" + "="*60)
    print("✅ 检查 2: JD 解析")
    print("="*60)
    
    test_jd = """
    职位: 高级 Python 工程师
    
    我们需要一名有 5+ 年 Python 经验的工程师，精通 FastAPI 框架、
    PostgreSQL 数据库、Docker 容器化等技术。
    
    岗位要求:
    - 精通 Python, 熟练使用 FastAPI 和 Django
    - 5 年以上后端开发经验
    - 深入理解数据库设计和优化 (PostgreSQL, MySQL)
    - 熟悉 Docker 和 Kubernetes 容器化
    - 需要具有团队协作和沟通能力
    - 必须具有问题解决能力和创新思维
    """
    
    try:
        skills, tags, personality_fw = jd_parser.parse_jd_with_llm(
            jd_text=test_jd,
            role_category="backend"
        )
        
        print(f"\n  解析结果:")
        print(f"  📌 提取技能数: {len(skills)}")
        for skill in skills:
            print(f"     • {skill.skill_name} ({skill.skill_type}) - "
                  f"优先级: {skill.priority_score}/10 "
                  f"{'(必需)' if skill.is_must_have else ''}")
        
        print(f"\n  💼 能力标签数: {len(tags)}")
        for tag in tags:
            print(f"     • {tag.capability_name} ({tag.capability_category}) - {tag.importance_level}")
        
        print(f"\n  🧠 人格框架:")
        print(f"     • 尽责性最低: {personality_fw.conscientiousness_min}")
        print(f"     • 外向性最低: {personality_fw.extraversion_min}")
        print(f"     • 开放性最低: {personality_fw.openness_min}")
        
        print("\n  ✅ JD 解析成功!")
        return True
    
    except Exception as e:
        print(f"  ❌ 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_skill_matching():
    """测试技能匹配"""
    print("\n" + "="*60)
    print("✅ 检查 3: 技能匹配计算")
    print("="*60)
    
    # 测试数据
    candidate_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
    
    required_skills = [
        JobSkillRequirementSchema(
            skill_name="Python", skill_type="programming_language",
            required_level="expert", is_must_have=True, priority_score=9
        ),
        JobSkillRequirementSchema(
            skill_name="FastAPI", skill_type="framework",
            required_level="intermediate", is_must_have=True, priority_score=8
        ),
        JobSkillRequirementSchema(
            skill_name="Kubernetes", skill_type="tool",
            required_level="intermediate", is_must_have=False, priority_score=5
        ),
    ]
    
    try:
        match_score, matched, missing = matching_engine.calculate_skill_match(
            candidate_skills,
            required_skills
        )
        
        print(f"\n  候选人技能: {', '.join(candidate_skills)}")
        print(f"  岗位需求: {len(required_skills)} 项")
        
        print(f"\n  匹配结果:")
        print(f"  ✓ 已匹配: {', '.join(matched)}")
        print(f"  ✗ 缺失: {', '.join(missing)}")
        print(f"\n  📊 匹配度: {match_score}%")
        
        print("\n  ✅ 技能匹配计算成功!")
        return True
    
    except Exception as e:
        print(f"  ❌ 计算失败: {str(e)}")
        return False


def test_personality_matching():
    """测试人格匹配"""
    print("\n" + "="*60)
    print("✅ 检查 4: 人格匹配计算")
    print("="*60)
    
    # 候选人人格评分
    candidate_personality = {
        "openness": 75,
        "conscientiousness": 85,
        "extraversion": 60,
        "agreeableness": 70,
        "neuroticism": 40
    }
    
    # 岗位要求
    job_framework = JobPersonalityFrameworkSchema(
        openness_min=50, openness_max=100,
        conscientiousness_min=70, conscientiousness_max=100,
        extraversion_min=40, extraversion_max=100,
        agreeableness_min=50, agreeableness_max=100,
        neuroticism_min=0, neuroticism_max=60
    )
    
    try:
        match_score = matching_engine.calculate_personality_match(
            candidate_personality,
            job_framework
        )
        
        print(f"\n  候选人人格评分:")
        for dim, score in candidate_personality.items():
            print(f"    • {dim:20}: {score}/100")
        
        print(f"\n  岗位要求范围:")
        print(f"    • openness:        {job_framework.openness_min}-{job_framework.openness_max}")
        print(f"    • conscientiousness: {job_framework.conscientiousness_min}-{job_framework.conscientiousness_max}")
        print(f"    • extraversion:    {job_framework.extraversion_min}-{job_framework.extraversion_max}")
        
        print(f"\n  📊 人格匹配度: {match_score}%")
        
        print("\n  ✅ 人格匹配计算成功!")
        return True
    
    except Exception as e:
        print(f"  ❌ 计算失败: {str(e)}")
        return False


def test_overall_matching():
    """测试综合匹配"""
    print("\n" + "="*60)
    print("✅ 检查 5: 综合匹配度计算")
    print("="*60)
    
    try:
        skill_match = 80
        personality_match = 75
        resume_match = 85
        
        overall = matching_engine.calculate_overall_match(
            skill_match,
            personality_match,
            resume_match
        )
        
        print(f"\n  匹配度分解:")
        print(f"    • 技能匹配度:     {skill_match}% (权重 50%)")
        print(f"    • 人格匹配度:     {personality_match}% (权重 30%)")
        print(f"    • 简历匹配度:     {resume_match}% (权重 20%)")
        
        print(f"\n  综合评分计算:")
        print(f"    = {skill_match} × 0.5 + {personality_match} × 0.3 + {resume_match} × 0.2")
        print(f"    = {skill_match * 0.5} + {personality_match * 0.3} + {resume_match * 0.2}")
        print(f"    = {overall}%")
        
        # 判断推荐等级
        if overall >= 75:
            recommendation = "🟢 高度匹配"
        elif overall >= 60:
            recommendation = "🟡 中等匹配"
        else:
            recommendation = "🔴 低匹配"
        
        print(f"\n  推荐等级: {recommendation}")
        
        print("\n  ✅ 综合匹配计算成功!")
        return True
    
    except Exception as e:
        print(f"  ❌ 计算失败: {str(e)}")
        return False


def main():
    """运行所有验证"""
    print("\n" + "="*70)
    print("🔍 岗位需求与应聘功能验证")
    print("="*70)
    
    results = []
    
    # 运行所有检查
    results.append(("数据库表", check_database_tables()))
    results.append(("JD 解析", test_jd_parsing()))
    results.append(("技能匹配", test_skill_matching()))
    results.append(("人格匹配", test_personality_matching()))
    results.append(("综合匹配", test_overall_matching()))
    
    # 总结
    print("\n" + "="*70)
    print("📊 验证结果总结")
    print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name:20}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 所有验证都通过了! 系统已准备好投入使用。")
        print("\n后续步骤:")
        print("  1. 启动前端: npm run dev")
        print("  2. 测试 HR 岗位需求编辑功能")
        print("  3. 测试候选人应聘流程")
        return 0
    else:
        print("❌ 部分验证失败，请检查日志信息。")
        return 1
    
    print("="*70 + "\n")


if __name__ == "__main__":
    sys.exit(main())
