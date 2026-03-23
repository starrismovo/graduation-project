#!/usr/bin/env python3
"""
检查数据库中的 user_type 值和 enum 定义
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models.user import User, UserType

db = SessionLocal()

print("\n=== User Type Enum 定义 ===")
print(f"UserType.HR = {repr(UserType.HR)}, value={UserType.HR.value}")
print(f"UserType.CANDIDATE = {repr(UserType.CANDIDATE)}, value={UserType.CANDIDATE.value}")

print("\n=== 数据库中的用户 ===")
users = db.query(User).limit(5).all()
for user in users:
    print(f"ID: {user.id}, username: {user.username}, user_type: {repr(user.user_type)}, is_hr: {user.is_hr}")

print("\n=== 检查是否有非法 enum 值 ===")
try:
    # 尝试查询所有用户
    all_users = db.query(User).all()
    print(f"✅ 成功查询所有 {len(all_users)} 个用户")
except Exception as e:
    print(f"❌ 查询失败: {type(e).__name__}: {str(e)}")
    
    # 使用原始SQL查询
    print("\n使用原始 SQL 查询:")
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT id, username, user_type, is_hr FROM users LIMIT 5"))
        rows = result.fetchall()
        print("Raw SQL 结果:")
        for row in rows:
            print(f"  ID: {row[0]}, username: {row[1]}, user_type: {repr(row[2])}, is_hr: {row[3]}")
    except Exception as e2:
        print(f"Raw SQL 也失败了: {type(e2).__name__}: {str(e2)}")

db.close()
