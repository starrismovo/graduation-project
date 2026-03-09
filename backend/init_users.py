#!/usr/bin/env python
"""初始化测试用户"""
from database import SessionLocal, engine, Base
# 导入所有models以初始化relationships
from models.user import User
from models.job import Job
from models.interview import Interview
from models.assessment import AssessmentRecord
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建表
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 检查并创建测试用户
users = [
    {"username": "candidate1", "email": "candidate1@test.com", "password": "123456", "is_hr": False},
    {"username": "hr1", "email": "hr1@test.com", "password": "123456", "is_hr": True},
]

for user_data in users:
    existing = db.query(User).filter(User.username == user_data["username"]).first()
    if not existing:
        hashed_pwd = pwd_context.hash(user_data["password"])
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_pwd,
            is_hr=user_data["is_hr"],
        )
        db.add(user)
        print(f"✅ 创建用户: {user_data['username']}")
    else:
        print(f"⏭️ 用户已存在: {user_data['username']}")

db.commit()
db.close()
print("\n✅ 初始化完成")
