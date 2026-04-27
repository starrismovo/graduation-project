#!/usr/bin/env python3
"""
毕业设计系统改进 - 数据库迁移脚本

执行内容：
1. 创建 EvaluationResult 表（评估结果集中存储）
2. 为 trait_scores 表添加 scenario_traits 字段
3. 为 jobs 表添加 personality_requirements 和 work_environment 字段

使用方法：
    python migrate_improvements.py

或在Windows PowerShell中：
    python .\migrate_improvements.py
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载 .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("❌ DATABASE_URL 未配置，请在 .env 中设置")
    sys.exit(1)

logger.info(f"📊 数据库连接: {DATABASE_URL.split('@')[-1].split('/')[0]}")


# ============ 迁移SQL语句 ============

# 1. 创建 EvaluationResult 表
CREATE_EVALUATION_RESULT_TABLE = """
CREATE TABLE IF NOT EXISTS evaluation_results (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    result_id VARCHAR(50) UNIQUE NOT NULL,
    assessment_record_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score FLOAT NOT NULL,
    ability_scores JSON,
    trait_comparison JSON,
    agent_scores JSON,
    strengths TEXT,
    gaps TEXT,
    recommendations TEXT,
    report_content JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_record_id) REFERENCES assessment_records(id) ON DELETE CASCADE,
    FOREIGN KEY(candidate_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_result_id (result_id),
    INDEX idx_assessment_record (assessment_record_id),
    INDEX idx_candidate (candidate_id),
    INDEX idx_job (job_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# 2. 为 trait_scores 表添加字段
ADD_TRAIT_SCORES_BASIC_TRAITS = """
ALTER TABLE trait_scores ADD COLUMN basic_traits JSON COMMENT '基础人格评分（Big Five）' AFTER reasoning;
"""

ADD_TRAIT_SCORES_SCENARIO_TRAITS = """
ALTER TABLE trait_scores ADD COLUMN scenario_traits JSON COMMENT '场景人格评分（针对特定岗位）' AFTER basic_traits;
"""

# 3. 为 jobs 表添加字段
ADD_JOBS_PERSONALITY_REQUIREMENTS = """
ALTER TABLE jobs ADD COLUMN personality_requirements JSON COMMENT '岗位人格需求' AFTER salary_max;
"""

ADD_JOBS_WORK_ENVIRONMENT = """
ALTER TABLE jobs ADD COLUMN work_environment JSON COMMENT '工作环境特征' AFTER personality_requirements;
"""


def check_table_exists(engine, table_name):
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def execute_sql(engine, sql_statement, statement_name):
    """执行单个SQL语句"""
    try:
        with engine.connect() as connection:
            connection.execute(text(sql_statement))
            connection.commit()
        logger.info(f"✅ {statement_name} - 成功")
        return True
    except SQLAlchemyError as e:
        error_msg = str(e)
        # 处理"列已存在"的错误（MySQL: Duplicate column name）
        if "Duplicate column name" in error_msg or "already exists" in error_msg:
            logger.info(f"⏭️  {statement_name} - 列已存在（不需要添加）")
            return True  # 视为成功
        else:
            logger.warning(f"⚠️  {statement_name} - {error_msg[:100]}")
            return False
    except Exception as e:
        error_msg = str(e)
        if "Duplicate column name" in error_msg or "already exists" in error_msg:
            logger.info(f"⏭️  {statement_name} - 列已存在（不需要添加）")
            return True  # 视为成功
        else:
            logger.error(f"❌ {statement_name} - {error_msg[:100]}")
            return False


def main():
    """主迁移函数"""
    logger.info("=" * 60)
    logger.info("🚀 毕业设计系统改进 - 数据库迁移开始")
    logger.info("=" * 60)
    
    try:
        # 创建数据库引擎
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ 数据库连接成功")
        
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {str(e)}")
        sys.exit(1)
    
    # ===== 执行迁移 =====
    
    migration_results = {
        "成功": [],
        "失败": [],
        "跳过": []
    }
    
    # 1. 创建 EvaluationResult 表
    logger.info("\n📋 步骤1: 创建 EvaluationResult 表...")
    if not check_table_exists(engine, "evaluation_results"):
        if execute_sql(engine, CREATE_EVALUATION_RESULT_TABLE, "CREATE TABLE evaluation_results"):
            migration_results["成功"].append("创建 evaluation_results 表")
        else:
            migration_results["失败"].append("创建 evaluation_results 表")
    else:
        logger.info("⏭️  evaluation_results 表已存在，跳过")
        migration_results["跳过"].append("evaluation_results 表已存在")
    
    # 2. 为 trait_scores 表添加 basic_traits 字段
    logger.info("\n📋 步骤2: 为 trait_scores 表添加 basic_traits 字段...")
    if check_table_exists(engine, "trait_scores"):
        if execute_sql(engine, ADD_TRAIT_SCORES_BASIC_TRAITS, "ADD COLUMN basic_traits"):
            migration_results["成功"].append("为 trait_scores 表添加 basic_traits 字段")
        else:
            migration_results["失败"].append("为 trait_scores 表添加 basic_traits 字段")
    else:
        logger.warning("⚠️  trait_scores 表不存在")
        migration_results["失败"].append("trait_scores 表不存在")
    
    # 3. 为 trait_scores 表添加 scenario_traits 字段
    logger.info("\n📋 步骤3: 为 trait_scores 表添加 scenario_traits 字段...")
    if check_table_exists(engine, "trait_scores"):
        if execute_sql(engine, ADD_TRAIT_SCORES_SCENARIO_TRAITS, "ADD COLUMN scenario_traits"):
            migration_results["成功"].append("为 trait_scores 表添加 scenario_traits 字段")
        else:
            migration_results["失败"].append("为 trait_scores 表添加 scenario_traits 字段")
    else:
        logger.warning("⚠️  trait_scores 表不存在")
        migration_results["失败"].append("trait_scores 表不存在")
    
    # 4. 为 jobs 表添加 personality_requirements 字段
    logger.info("\n📋 步骤4: 为 jobs 表添加 personality_requirements 字段...")
    if check_table_exists(engine, "jobs"):
        if execute_sql(engine, ADD_JOBS_PERSONALITY_REQUIREMENTS, "ADD COLUMN personality_requirements"):
            migration_results["成功"].append("为 jobs 表添加 personality_requirements 字段")
        else:
            migration_results["失败"].append("为 jobs 表添加 personality_requirements 字段")
    else:
        logger.warning("⚠️  jobs 表不存在")
        migration_results["失败"].append("jobs 表不存在")
    
    # 5. 为 jobs 表添加 work_environment 字段
    logger.info("\n📋 步骤5: 为 jobs 表添加 work_environment 字段...")
    if check_table_exists(engine, "jobs"):
        if execute_sql(engine, ADD_JOBS_WORK_ENVIRONMENT, "ADD COLUMN work_environment"):
            migration_results["成功"].append("为 jobs 表添加 work_environment 字段")
        else:
            migration_results["失败"].append("为 jobs 表添加 work_environment 字段")
    else:
        logger.warning("⚠️  jobs 表不存在")
        migration_results["失败"].append("jobs 表不存在")
    
    # ===== 输出汇总 =====
    logger.info("\n" + "=" * 60)
    logger.info("📊 迁移结果汇总")
    logger.info("=" * 60)
    
    logger.info(f"\n✅ 成功 ({len(migration_results['成功'])} 项):")
    for item in migration_results["成功"]:
        logger.info(f"   • {item}")
    
    if migration_results["失败"]:
        logger.info(f"\n❌ 失败 ({len(migration_results['失败'])} 项):")
        for item in migration_results["失败"]:
            logger.error(f"   • {item}")
    
    if migration_results["跳过"]:
        logger.info(f"\n⏭️  跳过 ({len(migration_results['跳过'])} 项):")
        for item in migration_results["跳过"]:
            logger.info(f"   • {item}")
    
    logger.info("\n" + "=" * 60)
    
    # 验证迁移结果
    if migration_results["失败"]:
        logger.error("❌ 迁移未完全成功，请检查错误信息")
        sys.exit(1)
    else:
        logger.info("✅ 数据库迁移完成！")
        logger.info("\n📝 下一步:")
        logger.info("   1. 重启应用服务")
        logger.info("   2. 查看 FINAL_DELIVERY_SUMMARY.md 了解新功能")
        logger.info("   3. 参考 QUICK_REFERENCE_GUIDE.md 使用新API")
        sys.exit(0)


if __name__ == "__main__":
    main()
