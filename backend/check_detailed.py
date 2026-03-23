#!/usr/bin/env python3
"""直接检查数据库表结构"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)
connection = engine.connect()

print("\n" + "="*70)
print("📊 详细的数据库列检查")
print("="*70 + "\n")

# 检查 users 表的所有列
print("users 表的所有列:")
print("-"*70)
result = connection.execute(text("DESC users;"))
for row in result:
    column_name, col_type, null, key, default, extra = row
    print(f"  {column_name:25} {str(col_type):30} NULL:{null} DEFAULT:{default}")

print("\n" + "-"*70)
print("新建的重要表检查:")
print("-"*70)

tables_to_check = ['evaluation_frameworks', 'conversation_turns', 'conversation_analyses']
for table in tables_to_check:
    try:
        result = connection.execute(text(f"DESC {table};"))
        rows = result.fetchall()
        if rows:
            print(f"\n✓ {table} 已创建 ({len(rows)} 列)")
            for row in rows:
                column_name = row[0]
                col_type = row[1]
                print(f"    - {column_name}: {col_type}")
        else:
            print(f"\n❌ {table} 表为空")
    except Exception as e:
        print(f"\n❌ {table} 表不存在: {str(e)[:50]}")

print("\n" + "-"*70)
print("interview_responses 表检查:")
print("-"*70)
result = connection.execute(text("DESC interview_responses;"))
for row in result:
    column_name, col_type, null, key, default, extra = row
    print(f"  {column_name:25} {str(col_type):30}")

print("\n" + "-"*70)
print("assessment_records 表检查:")
print("-"*70)
result = connection.execute(text("DESC assessment_records;"))
for row in result:
    column_name, col_type, null, key, default, extra = row
    print(f"  {column_name:25} {str(col_type):30}")

connection.close()

print("\n" + "="*70)
print("✅ 详细检查完成")
print("="*70 + "\n")
