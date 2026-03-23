#!/usr/bin/env python3
"""
修复数据库中的 user_type enum 值 - 改进版本
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

print("\n=== 修复 user_type enum 值 ===\n")

try:
    # 首先查看现有的值
    print("步骤 1: 检查现有的 user_type 值...")
    verify_sql = "SELECT DISTINCT user_type, COUNT(*) as count FROM users GROUP BY user_type"
    result = db_connection.execute(text(verify_sql))
    types = result.fetchall()
    print(f"  现有值: {list(types)}\n")
    
    # 使用临时列来更新值
    print("步骤 2: 使用临时列更新值...")
    
    # 添加一个临时列
    add_temp_col = "ALTER TABLE users ADD COLUMN user_type_temp VARCHAR(50)"
    try:
        db_connection.execute(text(add_temp_col))
        print("  ✓ 添加临时列")
    except:
        print("  ⚠️ 临时列已存在")
    
    # 更新临时列为大写值
    update_temp = """
    UPDATE users 
    SET user_type_temp = CASE 
        WHEN user_type = 'candidate' THEN 'CANDIDATE'
        WHEN user_type = 'hr' THEN 'HR'
        ELSE user_type
    END
    """
    result = db_connection.execute(text(update_temp))
    print(f"  ✓ 更新值: {result.rowcount} 条记录")
    
    db_connection.commit()
    
    # 删除原始列
    print("\n步骤 3: 重新创建 user_type 列...")
    
    drop_old = "ALTER TABLE users DROP COLUMN user_type"
    db_connection.execute(text(drop_old))
    print("  ✓ 删除原始列")
    
    # 重命名临时列
    rename_col = "ALTER TABLE users RENAME COLUMN user_type_temp TO user_type"
    db_connection.execute(text(rename_col))
    print("  ✓ 重命名临时列")
    
    db_connection.commit()
    
    # 转换为 ENUM，并添加约束和索引
    print("\n步骤 4: 添加 ENUM 约束...")
    modify_col = """
    ALTER TABLE users 
    MODIFY COLUMN user_type ENUM('HR', 'CANDIDATE') 
    DEFAULT 'CANDIDATE'
    COMMENT '用户类型: HR 或 CANDIDATE'
    """
    db_connection.execute(text(modify_col))
    print("  ✓ 添加 ENUM 约束")
    
    # 添加索引
    add_index = "ALTER TABLE users ADD INDEX idx_users_type (user_type)"
    try:
        db_connection.execute(text(add_index))
        print("  ✓ 添加索引")
    except:
        print("  ⚠️ 索引已存在")
    
    db_connection.commit()
    
    # 验证
    print("\n步骤 5: 验证修改...")
    verify_sql = """
    SELECT user_type, COUNT(*) as count 
    FROM users 
    WHERE user_type IS NOT NULL
    GROUP BY user_type
    """
    result = db_connection.execute(text(verify_sql))
    types = result.fetchall()
    print(f"  最终值: {list(types)}\n")
    
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
