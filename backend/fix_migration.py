#!/usr/bin/env python3
"""
直接执行关键 SQL 修复脚本
处理 users 表字段添加失败的问题
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)
connection = engine.connect()

print("\n" + "="*70)
print("🔧 执行关键 SQL 修复")
print("="*70 + "\n")

# 关键的 SQL 语句
sql_statements = [
    # 1. 添加 user_type 列到 users 表
    ("添加 user_type 列", """
        ALTER TABLE users 
        ADD COLUMN user_type ENUM('hr', 'candidate') DEFAULT 'candidate' AFTER is_hr
    """),
    
    # 2. 设置 user_type 值
    ("设置 user_type 值", """
        UPDATE users 
        SET user_type = CASE 
            WHEN is_hr = 1 THEN 'hr'
            ELSE 'candidate'
        END 
        WHERE user_type = 'candidate'
    """),
    
    # 3. 为 users 表添加候选人字段
    ("添加 age 列", "ALTER TABLE users ADD COLUMN age INT NULL AFTER delivery_privacy"),
    ("添加 education 列", "ALTER TABLE users ADD COLUMN education VARCHAR(50) NULL AFTER age"),
    ("添加 major 列", "ALTER TABLE users ADD COLUMN major VARCHAR(100) NULL AFTER education"),
    ("添加 desired_job 列", "ALTER TABLE users ADD COLUMN desired_job VARCHAR(100) NULL AFTER major"),
    ("添加 experience_years 列", "ALTER TABLE users ADD COLUMN experience_years FLOAT NULL AFTER desired_job"),
    ("添加 skills 列", "ALTER TABLE users ADD COLUMN skills JSON NULL AFTER experience_years"),
    ("添加 resume_url 列", "ALTER TABLE users ADD COLUMN resume_url TEXT NULL AFTER skills"),
    
    # 4. 添加审计字段
    ("添加 is_deleted 列", "ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE AFTER updated_at"),
    ("添加 deleted_at 列", "ALTER TABLE users ADD COLUMN deleted_at DATETIME NULL AFTER is_deleted"),
    
    # 5. 创建索引
    ("创建 user_type 索引", "CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type)"),
    ("创建 email 索引", "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"),
    ("创建 deleted 索引", "CREATE INDEX IF NOT EXISTS idx_users_deleted ON users(is_deleted)"),
    
    # 6. 为 interview_responses 添加 assessment_id
    ("添加 assessment_id 列到 interview_responses", 
     "ALTER TABLE interview_responses ADD COLUMN assessment_id INT NULL AFTER id"),
    
    # 7. 为 assessment_records 添加审计字段
    ("为 assessment_records 添加 is_deleted", 
     "ALTER TABLE assessment_records ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE AFTER updated_at"),
    ("为 assessment_records 添加 deleted_at", 
     "ALTER TABLE assessment_records ADD COLUMN deleted_at DATETIME NULL AFTER is_deleted"),
    ("为 assessment_records 添加 created_by", 
     "ALTER TABLE assessment_records ADD COLUMN created_by INT NULL AFTER job_title"),
    
    # 8. 为 interviews 添加审计字段
    ("为 interviews 添加 updated_at", 
     "ALTER TABLE interviews ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER completed_at"),
    ("为 interviews 添加 is_deleted", 
     "ALTER TABLE interviews ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE AFTER notes"),
    ("为 interviews 添加 deleted_at", 
     "ALTER TABLE interviews ADD COLUMN deleted_at DATETIME NULL AFTER is_deleted"),
    
    # 9. 创建 conversation_turns 表（修复外键问题）
    ("创建 conversation_turns 表", """
        CREATE TABLE IF NOT EXISTS conversation_turns (
            id INT PRIMARY KEY AUTO_INCREMENT,
            assessment_id INT NOT NULL,
            response_id INT NULL,
            round_num INT NOT NULL,
            turn_num INT NOT NULL,
            speaker ENUM('candidate', 'interviewer', 'system') NOT NULL,
            speaker_id INT NULL,
            message LONGTEXT NOT NULL,
            emotion VARCHAR(50) NULL,
            sentiment VARCHAR(20) NULL,
            confidence_score FLOAT NULL,
            response_time_ms INT NULL,
            message_length INT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_assessment (assessment_id),
            INDEX idx_response (response_id),
            INDEX idx_round (assessment_id, round_num),
            INDEX idx_created (created_at)
        )
    """),
]

# 执行所有 SQL 语句
success_count = 0
fail_count = 0

for step_name, sql_statement in sql_statements:
    try:
        logger.info(f"执行: {step_name}")
        connection.execute(text(sql_statement))
        connection.commit()
        logger.info(f"✓ {step_name} 成功\n")
        success_count += 1
    except Exception as e:
        error_msg = str(e)
        # 检查是否是已存在的列或外键错误
        if "already exists" in error_msg or "Duplicate" in error_msg or "already" in error_msg:
            logger.info(f"ⓘ {step_name} - 已存在，跳过\n")
            success_count += 1
        else:
            logger.warning(f"❌ {step_name} 失败: {error_msg[:100]}\n")
            fail_count += 1

connection.close()

print("="*70)
print(f"✅ 修复完成 - 成功: {success_count}, 失败: {fail_count}")
print("="*70 + "\n")

# 再次验证
print("\n验证修复结果...\n")
engine2 = create_engine(DATABASE_URL, echo=False)
connection2 = engine2.connect()

result = connection2.execute(text("DESC users;"))
columns = [row[0] for row in result]

print("users 表现在包含的关键列:")
key_columns = ['user_type', 'age', 'education', 'major', 'experience_years', 'skills', 'is_deleted', 'deleted_at']
for col in key_columns:
    if col in columns:
        print(f"  ✓ {col}")
    else:
        print(f"  ❌ {col} (缺失)")

connection2.close()
print("\n" + "="*70)
