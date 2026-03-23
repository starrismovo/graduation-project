#!/usr/bin/env python3
"""
ORM 模型增删改查测试脚本
验证数据库字段映射是否正确
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import datetime
import json
import time

# 添加 backend 路径
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from database import SessionLocal, engine, Base
from models.user import User, UserType
from models.interview import Interview
from models.assessment import AssessmentRecord, AssessmentStatus
from models.job import Job
from models.hr_agent import InterviewResponse

# 初始化数据库（创建表）
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 生成唯一的时间戳
timestamp = int(time.time() * 1000) % 10000

print("\n" + "="*70)
print("🧪 ORM 模型增删改查测试")
print("="*70 + "\n")

# ============================================
# 测试 1: User 表 CRUD
# ============================================

print("测试 1️⃣: User 表 CRUD 操作")
print("-"*70)

try:
    # CREATE: 创建候选人用户
    print("\n✓ 创建候选人用户...")
    candidate = User(
        username=f"test_candidate_{timestamp}",
        email=f"candidate_{timestamp}@example.com",
        hashed_password="hashed_pwd_123",
        user_type=UserType.CANDIDATE,
        real_name="张三",
        nickname="小张",
        age=28,
        education="本科",
        major="计算机科学",
        desired_job="后端工程师",
        experience_years=3.5,
        skills=json.dumps(["Python", "Java", "Docker"]),
        phone="13800138000",
        bio="热爱编程和开源贡献"
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    print(f"  ✅ 候选人创建成功 - ID: {candidate.id}")
    print(f"     user_type: {candidate.user_type}")
    print(f"     age: {candidate.age}, education: {candidate.education}")
    print(f"     skills: {candidate.skills}")
    
    # CREATE: 创建 HR 用户
    print("\n✓ 创建 HR 用户...")
    hr_user = User(
        username=f"test_hr_{timestamp}",
        email=f"hr_{timestamp}@example.com",
        hashed_password="hashed_pwd_456",
        user_type=UserType.HR,
        real_name="李四",
        nickname="HR李"
    )
    db.add(hr_user)
    db.commit()
    db.refresh(hr_user)
    print(f"  ✅ HR 用户创建成功 - ID: {hr_user.id}")
    print(f"     user_type: {hr_user.user_type}")
    
    # READ: 读取用户
    print("\n✓ 读取用户...")
    candidate_from_db = db.query(User).filter(User.id == candidate.id).first()
    print(f"  ✅ 读取成功")
    print(f"     username: {candidate_from_db.username}")
    print(f"     user_type: {candidate_from_db.user_type}")
    print(f"     age: {candidate_from_db.age}")
    print(f"     is_deleted: {candidate_from_db.is_deleted}")
    
    # UPDATE: 更新用户
    print("\n✓ 更新用户信息...")
    candidate_from_db.age = 29
    candidate_from_db.experience_years = 4.0
    db.commit()
    print(f"  ✅ 更新成功 - age: {candidate_from_db.age}")
    
    # DELETE: 软删除
    print("\n✓ 软删除用户...")
    candidate_from_db.is_deleted = True
    candidate_from_db.deleted_at = datetime.utcnow()
    db.commit()
    print(f"  ✅ 软删除成功 - is_deleted: {candidate_from_db.is_deleted}")
    
    print("\n✅ User 表 CRUD 测试通过\n")
    
except Exception as e:
    print(f"\n❌ User 表 CRUD 测试失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 2: Job 表 CRUD
# ============================================

print("测试 2️⃣: Job 表 CRUD 操作")
print("-"*70)

try:
    # CREATE: 创建岗位
    print("\n✓ 创建岗位...")
    job = Job(
        name="后端工程师",
        description="负责后端服务开发和维护",
        company="科技公司 ABC",
        category="技术岗",
        city="北京",
        salary_min=20,
        salary_max=35,
        required_traits=json.dumps({
            "openness": 7.0,
            "conscientiousness": 8.0,
            "extroversion": 5.0,
            "agreeableness": 6.5,
            "neuroticism": 4.0
        }),
        creator_id=hr_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    print(f"  ✅ 岗位创建成功 - ID: {job.id}")
    print(f"     name: {job.name}")
    print(f"     creator_id: {job.creator_id}")
    
    # READ: 读取岗位
    print("\n✓ 读取岗位...")
    job_from_db = db.query(Job).filter(Job.id == job.id).first()
    print(f"  ✅ 读取成功")
    print(f"     name: {job_from_db.name}")
    print(f"     creator.username: {job_from_db.creator.username}")
    
    # UPDATE: 更新岗位
    print("\n✓ 更新岗位...")
    job_from_db.salary_max = 40
    db.commit()
    print(f"  ✅ 更新成功 - salary_max: {job_from_db.salary_max}")
    
    print("\n✅ Job 表 CRUD 测试通过\n")
    
except Exception as e:
    print(f"\n❌ Job 表 CRUD 测试失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 3: Interview 表 CRUD
# ============================================

print("测试 3️⃣: Interview 表 CRUD 操作")
print("-"*70)

try:
    # CREATE: 创建面试记录
    print("\n✓ 创建面试记录...")
    interview = Interview(
        candidate_id=candidate.id,
        job_id=job.id,
        status="started",
        personality_traits=json.dumps({
            "openness": 7.2,
            "conscientiousness": 8.1,
            "extroversion": 5.3,
            "agreeableness": 6.8,
            "neuroticism": 4.2
        }),
        match_score=82.5
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    print(f"  ✅ 面试记录创建成功 - ID: {interview.id}")
    print(f"     candidate_id: {interview.candidate_id}")
    print(f"     job_id: {interview.job_id}")
    print(f"     status: {interview.status}")
    print(f"     match_score: {interview.match_score}")
    
    # READ: 读取面试记录
    print("\n✓ 读取面试记录...")
    interview_from_db = db.query(Interview).filter(Interview.id == interview.id).first()
    print(f"  ✅ 读取成功")
    print(f"     candidate.username: {interview_from_db.candidate.username}")
    print(f"     job.name: {interview_from_db.job.name}")
    
    # UPDATE: 更新面试状态
    print("\n✓ 更新面试状态...")
    interview_from_db.status = "completed"
    interview_from_db.match_score = 85.0
    db.commit()
    print(f"  ✅ 更新成功 - status: {interview_from_db.status}, match_score: {interview_from_db.match_score}")
    
    # DELETE: 软删除
    print("\n✓ 软删除面试记录...")
    interview_from_db.is_deleted = True
    interview_from_db.deleted_at = datetime.utcnow()
    db.commit()
    print(f"  ✅ 软删除成功 - is_deleted: {interview_from_db.is_deleted}")
    
    print("\n✅ Interview 表 CRUD 测试通过\n")
    
except Exception as e:
    print(f"\n❌ Interview 表 CRUD 测试失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 4: AssessmentRecord 表 CRUD
# ============================================

print("测试 4️⃣: AssessmentRecord 表 CRUD 操作")
print("-"*70)

try:
    # CREATE: 创建评估记录
    print("\n✓ 创建评估记录...")
    assessment = AssessmentRecord(
        candidate_id=candidate.id,
        job_id=job.id,
        job_title=job.name,
        assessment_status=AssessmentStatus.COMPLETED,
        assessment_mode="immersive",
        match_score=82.5,
        conversation_summary="考生表现良好，技能深度符合岗位要求",
        total_rounds=3,
        duration_minutes=45.5,
        conversation_depth=8.5,
        roles_participated=json.dumps(["hr", "tech_lead"]),
        overall_impression="技术能力强，沟通能力有待提升",
        created_by=hr_user.id
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    print(f"  ✅ 评估记录创建成功 - ID: {assessment.id}")
    print(f"     candidate_id: {assessment.candidate_id}")
    print(f"     assessment_status: {assessment.assessment_status}")
    print(f"     created_by: {assessment.created_by}")
    print(f"     is_deleted: {assessment.is_deleted}")
    
    # READ: 读取评估记录
    print("\n✓ 读取评估记录...")
    assessment_from_db = db.query(AssessmentRecord).filter(AssessmentRecord.id == assessment.id).first()
    print(f"  ✅ 读取成功")
    print(f"     candidate.username: {assessment_from_db.candidate.username}")
    print(f"     created_by_user.username: {assessment_from_db.created_by_user.username}")
    
    # UPDATE: 更新评估记录
    print("\n✓ 更新评估记录...")
    assessment_from_db.match_score = 85.0
    db.commit()
    print(f"  ✅ 更新成功 - match_score: {assessment_from_db.match_score}")
    
    # DELETE: 软删除
    print("\n✓ 软删除评估记录...")
    assessment_from_db.is_deleted = True
    assessment_from_db.deleted_at = datetime.utcnow()
    db.commit()
    print(f"  ✅ 软删除成功 - is_deleted: {assessment_from_db.is_deleted}")
    
    print("\n✅ AssessmentRecord 表 CRUD 测试通过\n")
    
except Exception as e:
    print(f"\n❌ AssessmentRecord 表 CRUD 测试失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 5: InterviewResponse 表 CRUD
# ============================================

print("测试 5️⃣: InterviewResponse 表 CRUD 操作")
print("-"*70)

try:
    # CREATE: 创建面试回答
    print("\n✓ 创建面试回答...")
    response = InterviewResponse(
        assessment_id=assessment.id,
        candidate_id=candidate.id,
        scenario_id="scenario_001",
        round_num=1,
        question="请介绍一下你的项目经验",
        answer="我参与了多个后端项目，使用 Python 和 Java",
        answer_latency=5.2,
        emotion="confident",
        answer_length=45,
        is_paste=False
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    print(f"  ✅ 面试回答创建成功 - ID: {response.id}")
    print(f"     assessment_id: {response.assessment_id}")
    print(f"     candidate_id: {response.candidate_id}")
    print(f"     emotion: {response.emotion}")
    
    # READ: 读取面试回答
    print("\n✓ 读取面试回答...")
    response_from_db = db.query(InterviewResponse).filter(InterviewResponse.id == response.id).first()
    print(f"  ✅ 读取成功")
    print(f"     question: {response_from_db.question}")
    print(f"     assessment_id: {response_from_db.assessment_id}")
    
    # UPDATE: 更新面试回答
    print("\n✓ 更新面试回答...")
    response_from_db.emotion = "neutral"
    db.commit()
    print(f"  ✅ 更新成功 - emotion: {response_from_db.emotion}")
    
    print("\n✅ InterviewResponse 表 CRUD 测试通过\n")
    
except Exception as e:
    print(f"\n❌ InterviewResponse 表 CRUD 测试失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 6: 关系验证
# ============================================

print("测试 6️⃣: 模型关系验证")
print("-"*70)

try:
    print("\n✓ 验证用户与面试的关系...")
    user_interviews = db.query(Interview).filter(
        Interview.candidate_id == candidate.id
    ).all()
    print(f"  ✅ 找到 {len(user_interviews)} 条面试记录")
    
    print("\n✓ 验证用户与评估的关系...")
    user_assessments = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate.id
    ).all()
    print(f"  ✅ 找到 {len(user_assessments)} 条评估记录")
    
    print("\n✓ 验证岗位与面试的关系...")
    job_interviews = db.query(Interview).filter(
        Interview.job_id == job.id
    ).all()
    print(f"  ✅ 找到 {len(job_interviews)} 条关联面试")
    
    print("\n✅ 模型关系验证通过\n")
    
except Exception as e:
    print(f"\n❌ 模型关系验证失败: {str(e)}\n")

# ============================================
# 测试总结
# ============================================

print("="*70)
print("✅ 所有 ORM CRUD 测试完成")
print("="*70 + "\n")

# 清理数据库
print("清理测试数据...")
try:
    # 删除创建的数据
    if 'candidate' in locals():
        db.query(InterviewResponse).filter(InterviewResponse.candidate_id == candidate.id).delete()
        db.query(Interview).filter(Interview.candidate_id == candidate.id).delete()
        db.query(AssessmentRecord).filter(AssessmentRecord.candidate_id == candidate.id).delete()
        db.query(User).filter(User.id.in_([candidate.id])).delete()
    
    if 'hr_user' in locals():
        db.query(User).filter(User.id == hr_user.id).delete()
    
    if 'job' in locals():
        db.query(Job).filter(Job.id == job.id).delete()
    
    db.commit()
    print("✅ 测试数据已清理\n")
except Exception as e:
    print(f"⚠️  清理数据时出错: {str(e)}\n")
    db.rollback()

db.close()
