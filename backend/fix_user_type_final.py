#!/usr/bin/env python3
"""
简化版：直接修改 user_type 为 ENUM
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

print("\n=== 修复 user_type 列 ===\n")

try:
    print("步骤 1: 将小写值更新为大写...")
    update_sql = """
    UPDATE users 
    SET user_type_temp = CASE 
        WHEN user_type_temp IS NOT NULL THEN UPPER(user_type_temp)
        ELSE 'CANDIDATE'
    END
    WHERE user_type_temp IS NOT NULL
    """
    result = db_connection.execute(text(update_sql))
    print(f"✅ 已更新 {result.rowcount} 条记录")
    
    db_connection.commit()
    
    print("\n步骤 2: 删除旧的 user_type 列...")
    drop_sql = "ALTER TABLE users DROP COLUMN user_type"
    db_connection.execute(text(drop_sql))
    print("✅ 已删除旧列")
    
    db_connection.commit()
    
    print("\n步骤 3: 将 user_type_temp 列转换为 ENUM...")
    modify_sql = """
    ALTER TABLE users 
    CHANGE COLUMN user_type_temp user_type 
    ENUM('HR', 'CANDIDATE') 
    DEFAULT 'CANDIDATE'
    COMMENT '用户类型: HR 或 CANDIDATE'
    """
    db_connection.execute(text(modify_sql))
    print("✅ 已添加 ENUM 约束")
    
    db_connection.commit()
    
    print("\n步骤 4: 添加索引...")
    index_sql = "ALTER TABLE users ADD INDEX idx_users_type (user_type)"
    try:
        db_connection.execute(text(index_sql))
        print("✅ 已添加索引")
    except:
        print("⚠️ 索引已存在")
    
    db_connection.commit()
    
    print("\n步骤 5: 验证结果...")
    verify_sql = """
    SELECT user_type, COUNT(*) as count 
    FROM users 
    GROUP BY user_type
    """
    result = db_connection.execute(text(verify_sql))
    types = result.fetchall()
    print(f"✅ 最终值: {list(types)}\n")
    
    print("="*70)
    print("✅ 修复完成！")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {str(e)}\n")
    import traceback
    traceback.print_exc()
    db_connection.rollback()
finally:
    db_connection.close()
