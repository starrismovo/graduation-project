#!/usr/bin/env python3
"""
数据库迁移脚本 - 创建岗位需求相关的表
"""

import sys
sys.path.insert(0, '/d/Desktop/graduation-project/backend')

from database import engine, Base
from models import (
    JobRequirementTag,
    JobSkillRequirement,
    JobPersonalityFramework,
    CandidateJobApplication
)

def migrate():
    """执行迁移"""
    print("开始创建岗位需求相关的表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 应聘相关的表已创建:")
        print("   - job_requirement_tags (岗位需求标签)")
        print("   - job_skill_requirements (岗位技能需求)")
        print("   - job_personality_frameworks (岗位人格框架)")
        print("   - candidate_job_applications (候选人应聘记录)")
        
        print("\n✅ 数据库迁移完成！")
        return 0
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(migrate())
