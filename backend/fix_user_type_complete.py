#!/usr/bin/env python3
"""
最简单的方案：直接将 user_type_temp 转换为 ENUM
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

from database import engine
from sqlalchemy import text

db_connection = engine.connect()

print("\n=== 完成 user_type 列的修复 ===\n")

try:
    # 查看当前的列
    print("步骤 1: 检查当前表结构...")
    check_sql = "SHOW COLUMNS FROM users WHERE Field='user_type' OR Field='user_type_temp'"
    result = db_connection.execute(text(check_sql))
    cols = result.fetchall()
    print(f"  当前列: {cols}\n")
    
    # 直接将 user_type_temp 转换为 ENUM
    print("步骤 2: 将 user_type_temp 转换为 ENUM user_type...")
    modify_sql = """
    ALTER TABLE users 
    CHANGE COLUMN user_type_temp user_type 
    ENUM('HR', 'CANDIDATE') 
    DEFAULT 'CANDIDATE'
    """
    db_connection.execute(text(modify_sql))
    print("✅ 已转换为 ENUM\n")
    
    db_connection.commit()
    
  # 添加索引
    print("步骤 3: 添加索引...")
    try:
        index_sql = "ALTER TABLE users ADD INDEX idx_users_type (user_type)"
        db_connection.execute(text(index_sql))
        print("✅ 已添加索引\n")
    except:
        print("⚠️ 索引已存在\n")
    
    db_connection.commit()
    
    # 验证
    print("步骤 4: 验证结果...")
    verify_sql = """
    SELECT user_type, COUNT(*) as count 
    FROM users 
    GROUP BY user_type
    """
    result = db_connection.execute(text(verify_sql))
    types = result.fetchall()
    print(f"✅ user_type 值: {list(types)}\n")
    
    print("="*70)
    print("✅ user_type 列修复完成！")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {str(e)}\n")
    import traceback
    traceback.print_exc()
    db_connection.rollback()
finally:
    db_connection.close()
