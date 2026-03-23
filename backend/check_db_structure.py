#!/usr/bin/env python3
"""
数据库结构和数据预检查脚本
在执行迁移前验证当前状态
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)
connection = engine.connect()

print("\n" + "="*70)
print("📊 当前数据库结构检查")
print("="*70 + "\n")

# 检查表是否存在
inspector = inspect(engine)
tables = inspector.get_table_names()

print("✓ 存在的表:")
for table in tables:
    print(f"  - {table}")

print("\n" + "-"*70)
print("📋 核心表的列信息:")
print("-"*70 + "\n")

# 检查 users 表
print("users 表列:")
users_cols = inspector.get_columns('users')
for col in users_cols:
    print(f"  - {col['name']}: {col['type']}")

print("\ncancel dates 表列:")
candidates_cols = inspector.get_columns('candidates')
for col in candidates_cols:
    print(f"  - {col['name']}: {col['type']}")

print("\ninterviews 表信息:")
interviews_cols = inspector.get_columns('interviews')
for col in interviews_cols:
    print(f"  - {col['name']}: {col['type']}")

interviews_fks = inspector.get_foreign_keys('interviews')
print("\n  外键关系:")
for fk in interviews_fks:
    print(f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

# 检查数据量
print("\n" + "-"*70)
print("📊 数据量统计:")
print("-"*70 + "\n")

queries = [
    ("users 表", "SELECT COUNT(*) as count FROM users"),
    ("candidates 表", "SELECT COUNT(*) as count FROM candidates"),
    ("interviews 表", "SELECT COUNT(*) as count FROM interviews"),
    ("assessment_records 表", "SELECT COUNT(*) as count FROM assessment_records"),
    ("interview_responses 表", "SELECT COUNT(*) as count FROM interview_responses"),
]

for name, query in queries:
    try:
        result = connection.execute(text(query))
        count = result.fetchone()[0]
        print(f"✓ {name}: {count} 行")
    except Exception as e:
        print(f"❌ {name}: 查询失败 - {str(e)[:50]}")

# 检查潜在问题
print("\n" + "-"*70)
print("🔍 潜在问题检查:")
print("-"*70 + "\n")

# 检查是否有 user_type 列
try:
    result = connection.execute(text("SELECT user_type FROM users LIMIT 1"))
    print("✓ users 表已有 user_type 列")
except:
    print("⚠️  users 表缺少 user_type 列 (需要添加)")

# 检查 candidates.id 类型
try:
    result = connection.execute(text("SELECT id FROM candidates LIMIT 1"))
    print("✓ candidates 表存在")
except:
    print("⚠️  candidates 表不存在")

# 检查是否可以关联 candidates 到 users
try:
    result = connection.execute(text("""
        SELECT u.id, u.username, u.real_name, c.id as c_id, c.name 
        FROM users u 
        LEFT JOIN candidates c ON u.real_name = c.name OR u.username = c.id
        LIMIT 5
    """))
    print("\n候选人关联示例:")
    for row in result:
        print(f"  user(id={row[0]}, name={row[1]}, real_name={row[2]}) → candidate(id={row[3]:.50 if row[3] else 'NULL'}, name={row[4]})")
except Exception as e:
    print(f"⚠️  无法关联候选人: {str(e)[:100]}")

# 检查 interview 的外键是否正确
print("\n" + "-"*70)
print("🔗 Interview 表外键完整性:")
print("-"*70 + "\n")

try:
    result = connection.execute(text("""
        SELECT COUNT(*) as orphaned_count
        FROM interviews i
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = i.candidate_id)
    """))
    orphaned = result.fetchone()[0]
    if orphaned > 0:
        print(f"⚠️  发现 {orphaned} 条孤立的 interview 记录")
    else:
        print("✓ 所有 interview 记录的 candidate_id 都有效")
except Exception as e:
    print(f"❌ 检查失败: {str(e)[:100]}")

connection.close()

print("\n" + "="*70)
print("✅ 预检查完成")
print("="*70 + "\n")
