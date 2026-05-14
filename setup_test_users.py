#!/usr/bin/env python3
"""
创建测试用户和岗位的脚本
"""

import sys
sys.path.insert(0, 'd:\\Desktop\\graduation-project\\backend')

from database import SessionLocal
from models.user import User, UserType
from models.job import Job
from passlib.context import CryptContext
from datetime import datetime

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def main():
    db = SessionLocal()
    
    print("📝 创建测试用户和岗位...\n")
    
    # 1. 创建或更新 admin 用户
    print("1️⃣ 检查/创建 admin 用户...")
    admin = db.query(User).filter(User.username == "admin").first()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_hr=True,
            user_type=UserType.HR,
            nickname="管理员",
            real_name="系统管理员",
            created_at=datetime.utcnow()
        )
        db.add(admin)
        db.commit()
        print("   ✅ admin 用户已创建")
        print(f"   用户名: admin")
        print(f"   密码: admin123")
    else:
        print(f"   ✅ admin 用户已存在 (ID: {admin.id})")
    
    # 2. 创建测试候选人
    print("\n2️⃣ 创建测试候选人...")
    candidate_names = [
        ("candidate1", "张三", "张三"),
        ("candidate2", "李四", "李四"),
        ("candidate3", "王五", "王五"),
        ("candidate4", "赵六", "赵六"),
        ("candidate5", "刘七", "刘七"),
    ]
    
    for username, nickname, real_name in candidate_names:
        candidate = db.query(User).filter(User.username == username).first()
        if not candidate:
            candidate = User(
                username=username,
                email=f"{username}@example.com",
                hashed_password=get_password_hash("123456"),
                is_hr=False,
                user_type=UserType.CANDIDATE,
                nickname=nickname,
                real_name=real_name,
                age=28,
                education="本科",
                created_at=datetime.utcnow()
            )
            db.add(candidate)
            db.commit()
            print(f"   ✅ {username} 已创建 (ID: {candidate.id})")
        else:
            print(f"   ✅ {username} 已存在 (ID: {candidate.id})")
    
    # 3. 创建测试岗位（由 admin 创建）
    print("\n3️⃣ 创建测试岗位（由 admin 创建）...")
    
    jobs_data = [
        {
            "name": "Python 后端工程师",
            "description": "负责后端系统开发和维护，熟悉 FastAPI 框架",
            "company": "Tech Company",
            "category": "技术岗",
            "city": "北京",
            "salary_min": 25,
            "salary_max": 35,
        },
        {
            "name": "React 前端工程师",
            "description": "负责前端应用开发，使用 Vue 3 和 TypeScript",
            "company": "Tech Company",
            "category": "技术岗",
            "city": "北京",
            "salary_min": 20,
            "salary_max": 30,
        },
        {
            "name": "数据分析师",
            "description": "负责数据分析和可视化，使用 Python 和数据库",
            "company": "Tech Company",
            "category": "数据岗",
            "city": "上海",
            "salary_min": 18,
            "salary_max": 28,
        },
        {
            "name": "产品经理",
            "description": "负责产品规划和需求管理",
            "company": "Tech Company",
            "category": "产品岗",
            "city": "深圳",
            "salary_min": 22,
            "salary_max": 32,
        },
        {
            "name": "UI/UX 设计师",
            "description": "负责用户界面和用户体验设计",
            "company": "Tech Company",
            "category": "设计岗",
            "city": "北京",
            "salary_min": 18,
            "salary_max": 26,
        },
    ]
    
    for job_data in jobs_data:
        existing_job = db.query(Job).filter(Job.name == job_data["name"]).first()
        if not existing_job:
            job = Job(
                name=job_data["name"],
                description=job_data["description"],
                company=job_data["company"],
                category=job_data["category"],
                city=job_data["city"],
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                creator_id=admin.id,
                created_at=datetime.utcnow()
            )
            db.add(job)
            db.commit()
            print(f"   ✅ {job_data['name']} 已创建 (ID: {job.id})")
        else:
            print(f"   ✅ {job_data['name']} 已存在 (ID: {existing_job.id})")
    
    print("\n" + "="*60)
    print("✅ 测试数据创建完成！")
    print("\n可用的测试账户:")
    print("  • HR 账户:")
    print("    - 用户名: admin")
    print("    - 密码: admin123")
    print("  • 候选人账户:")
    for username, _, _ in candidate_names:
        print(f"    - 用户名: {username}, 密码: 123456")
    print("\n" + "="*60)
    
    db.close()

if __name__ == "__main__":
    main()
