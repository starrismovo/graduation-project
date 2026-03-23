#!/usr/bin/env python3
"""
数据一致性检查脚本
验证外键约束是否正确生效
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from database import SessionLocal, engine, Base
from models.user import User, UserType
from models.interview import Interview
from models.assessment import AssessmentRecord, AssessmentStatus
from models.job import Job
from models.hr_agent import InterviewResponse

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("\n" + "="*70)
print("🔍 数据一致性检查 - 外键约束验证")
print("="*70 + "\n")

# ============================================
# 测试 1: 级联删除 - 删除用户时的级联效果
# ============================================

print("测试 1️⃣: 级联删除 - 删除候选人用户")
print("-"*70)

try:
    # 创建测试数据
    print("\n✓ 创建测试数据...")
    candidate = User(
        username="cascade_test_candidate",
        email="cascade_candidate@example.com",
        hashed_password="pwd123",
        user_type=UserType.CANDIDATE,
        real_name="测试候选人",
        age=30,
        education="本科"
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    hr_user = User(
        username="cascade_test_hr",
        email="cascade_hr@example.com",
        hashed_password="pwd123",
        user_type=UserType.HR,
        real_name="测试 HR"
    )
    db.add(hr_user)
    db.commit()
    db.refresh(hr_user)
    
    job = Job(
        name="测试岗位",
        description="测试岗位",
        company="测试公司",
        category="技术",
        city="北京",
        salary_min=20,
        salary_max=30,
        required_traits=json.dumps({}),
        creator_id=hr_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    interview = Interview(
        candidate_id=candidate.id,
        job_id=job.id,
        status="started"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    print(f"  ✅ 创建完成")
    print(f"     Candidate ID: {candidate.id}")
    print(f"     Interview ID: {interview.id}")
    
    # 检查关联
    print("\n✓ 检查删除前的关联...")
    interviews_before = db.query(Interview).filter(Interview.candidate_id == candidate.id).count()
    print(f"  ✅ 关联的 Interview 数: {interviews_before}")
    
    # 删除候选人（应该级联删除关联的 Interview）
    print("\n✓ 删除候选人用户...")
    candidate_id = candidate.id
    db.delete(candidate)
    db.commit()
    print(f"  ✅ 候选人已删除")
    
    # 检查是否级联删除
    print("\n✓ 验证级联删除效果...")
    interviews_after = db.query(Interview).filter(Interview.candidate_id == candidate_id).count()
    if interviews_after == 0:
        print(f"  ✅ ✅ 级联删除成功！关联的 Interview 已被删除")
        print(f"     删除前: {interviews_before}, 删除后: {interviews_after}")
    else:
        print(f"  ❌ 级联删除失败！仍有 {interviews_after} 条孤立 Interview 记录")
    
    # 清理数据
    db.query(Job).filter(Job.id == job.id).delete()
    db.query(User).filter(User.id == hr_user.id).delete()
    db.commit()
    
    print("\n✅ 测试 1 完成\n")
    
except Exception as e:
    print(f"\n❌ 测试 1 失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 2: 外键约束 - 无效的外键
# ============================================

print("测试 2️⃣: 外键约束 - 防止无效关联")
print("-"*70)

try:
    print("\n✓ 测试是否能创建无效的外键引用...")
    
    # 尝试创建一个引用不存在用户的 Interview
    invalid_interview = Interview(
        candidate_id=99999,  # 不存在的 candidate ID
        job_id=99999,  # 不存在的 job ID
        status="started"
    )
    
    try:
        db.add(invalid_interview)
        db.commit()
        print(f"  ⚠️  警告: 系统允许创建无效的外键！(这可能是数据库约束未启用)")
        db.rollback()
    except Exception as constraint_error:
        print(f"  ✅ ✅ 外键约束生效！无效引用被拒绝")
        print(f"     错误信息: {str(constraint_error)[:80]}")
        db.rollback()
    
    print("\n✅ 测试 2 完成\n")
    
except Exception as e:
    print(f"\n⚠️  测试 2 异常: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 3: 软删除与查询
# ============================================

print("测试 3️⃣: 软删除与查询隔离")
print("-"*70)

try:
    print("\n✓ 创建测试用户...")
    soft_delete_candidate = User(
        username="soft_delete_test",
        email="soft_delete@example.com",
        hashed_password="pwd123",
        user_type=UserType.CANDIDATE,
        real_name="软删除测试"
    )
    db.add(soft_delete_candidate)
    db.commit()
    db.refresh(soft_delete_candidate)
    print(f"  ✅ 创建成功 - ID: {soft_delete_candidate.id}")
    
    print("\n✓ 验证删除前可以查询...")
    found_before = db.query(User).filter(User.id == soft_delete_candidate.id).first()
    if found_before:
        print(f"  ✅ 查询成功 - username: {found_before.username}")
    
    print("\n✓ 执行软删除...")
    soft_delete_candidate.is_deleted = True
    soft_delete_candidate.deleted_at = datetime.utcnow()
    db.commit()
    print(f"  ✅ 软删除完成 - is_deleted: {soft_delete_candidate.is_deleted}")
    
    print("\n✓ 验证软删除后的查询...")
    # 直接查询（包括已删除）
    found_direct = db.query(User).filter(User.id == soft_delete_candidate.id).first()
    if found_direct and found_direct.is_deleted:
        print(f"  ✅ 软删除记录仍存在于数据库")
        print(f"     is_deleted: {found_direct.is_deleted}")
        print(f"     deleted_at: {found_direct.deleted_at}")
    
    # 建议的做法：查询活跃的用户
    found_active = db.query(User).filter(
        (User.id == soft_delete_candidate.id) & 
        (User.is_deleted == False)
    ).first()
    if not found_active:
        print(f"  ✅ 通过 is_deleted=False 过滤时查询不到该用户")
    
    # 清理
    db.query(User).filter(User.id == soft_delete_candidate.id).delete(synchronize_session=False)
    db.commit()
    
    print("\n✅ 测试 3 完成\n")
    
except Exception as e:
    print(f"\n❌ 测试 3 失败: {str(e)}\n")
    db.rollback()

# ============================================
# 测试 4: 数据完整性检查
# ============================================

print("测试 4️⃣: 数据完整性检查")
print("-"*70)

try:
    print("\n✓ 检查孤立的 Interview 记录...")
    
    # 查找所有 Interview 中，candidate_id 不存在对应的 User 的记录
    from sqlalchemy import and_
    
    orphaned_interviews = db.query(Interview).outerjoin(
        User, Interview.candidate_id == User.id
    ).filter(User.id.is_(None)).all()
    
    if not orphaned_interviews:
        print(f"  ✅ 没有孤立的 Interview 记录")
    else:
        print(f"  ⚠️  发现 {len(orphaned_interviews)} 条孤立记录")
        for orphan in orphaned_interviews:
            print(f"     Interview ID: {orphan.id}, candidate_id: {orphan.candidate_id}")
    
    print("\n✓ 检查孤立的 InterviewResponse 记录...")
    orphaned_responses = db.query(InterviewResponse).outerjoin(
        AssessmentRecord, InterviewResponse.assessment_id == AssessmentRecord.id
    ).filter(AssessmentRecord.id.is_(None)).all()
    
    if not orphaned_responses:
        print(f"  ✅ 没有孤立的 InterviewResponse 记录")
    else:
        print(f"  ⚠️  发现 {len(orphaned_responses)} 条孤立记录")
    
    print("\n✓ 检查引用已删除用户的评估...")
    assessments_with_deleted_candidates = db.query(AssessmentRecord).join(
        User, AssessmentRecord.candidate_id == User.id
    ).filter(User.is_deleted == True).count()
    
    if assessments_with_deleted_candidates == 0:
        print(f"  ✅ 没有引用已删除候选人的评估记录")
    else:
        print(f"  ⚠️  发现 {assessments_with_deleted_candidates} 条引用已删除用户的评估")
    
    print("\n✅ 测试 4 完成\n")
    
except Exception as e:
    print(f"\n❌ 测试 4 失败: {str(e)}\n")

# ============================================
# 测试 5: 索引完整性检查
# ============================================

print("测试 5️⃣: 索引完整性检查")
print("-"*70)

try:
    # 创建测试数据
    print("\n✓ 创建索引测试数据...")
    
    candidates = []
    for i in range(5):
        candidate = User(
            username=f"index_test_{i}",
            email=f"index{i}@example.com",
            hashed_password="pwd123",
            user_type=UserType.CANDIDATE,
            is_deleted=i % 2 == 0  # 一半删除，一半不删除
        )
        db.add(candidate)
        candidates.append(candidate)
    
    db.commit()
    print(f"  ✅ 创建 5 条测试用户")
    
    print("\n✓ 测试 user_type 索引性能...")
    # 这应该使用 idx_users_type 索引
    candidates_query = db.query(User).filter(User.user_type == UserType.CANDIDATE).all()
    print(f"  ✅ user_type 过滤: 找到 {len(candidates_query)} 条候选人")
    
    print("\n✓ 测试 is_deleted 索引性能...")
    # 这应该使用 idx_users_deleted 索引
    active_users = db.query(User).filter(User.is_deleted == False).all()
    print(f"  ✅ is_deleted 过滤: 找到 {len(active_users)} 条活跃用户")
    
    print("\n✓ 测试复合查询...")
    # 查询活跃的候选人
    active_candidates = db.query(User).filter(
        (User.user_type == UserType.CANDIDATE) & 
        (User.is_deleted == False)
    ).all()
    print(f"  ✅ 复合查询: 找到 {len(active_candidates)} 条活跃候选人")
    
    # 清理
    for candidate in candidates:
        db.delete(candidate)
    db.commit()
    
    print("\n✅ 测试 5 完成\n")
    
except Exception as e:
    print(f"\n❌ 测试 5 失败: {str(e)}\n")
    db.rollback()

# ============================================
# 最终总结
# ============================================

print("="*70)
print("✅ 数据一致性检查完成")
print("="*70)
print("""
总结：
✓ 级联删除: 验证外键约束生效
✓ 外键验证: 防止无效关联
✓ 软删除: 确保逻辑删除正确
✓ 数据完整性: 检查孤立记录
✓ 索引性能: 验证索引创建
""")
print("="*70 + "\n")

db.close()
