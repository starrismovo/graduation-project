#!/usr/bin/env python3
"""
数据库迁移验证脚本

验证以下内容：
1. EvaluationResult 表是否存在
2. trait_scores 表是否有新字段
3. jobs 表是否有新字段
"""

import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载 .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("❌ DATABASE_URL 未配置")
    sys.exit(1)

try:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    inspector = inspect(engine)
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 数据库结构验证")
    logger.info("=" * 60)
    
    # 1. 验证 EvaluationResult 表
    logger.info("\n✅ 1. EvaluationResult 表")
    tables = inspector.get_table_names()
    if "evaluation_results" in tables:
        columns = [col['name'] for col in inspector.get_columns("evaluation_results")]
        logger.info(f"   表存在 ✅")
        logger.info(f"   字段数: {len(columns)}")
        logger.info(f"   字段列表: {', '.join(columns[:5])}...")
    else:
        logger.error("   表不存在 ❌")
    
    # 2. 验证 trait_scores 表新字段
    logger.info("\n✅ 2. trait_scores 表新字段")
    if "trait_scores" in tables:
        columns = {col['name']: col['type'] for col in inspector.get_columns("trait_scores")}
        logger.info(f"   表存在 ✅")
        
        if "basic_traits" in columns:
            logger.info(f"   • basic_traits: {columns['basic_traits']} ✅")
        else:
            logger.error(f"   • basic_traits: 不存在 ❌")
        
        if "scenario_traits" in columns:
            logger.info(f"   • scenario_traits: {columns['scenario_traits']} ✅")
        else:
            logger.error(f"   • scenario_traits: 不存在 ❌")
    else:
        logger.error("   表不存在 ❌")
    
    # 3. 验证 jobs 表新字段
    logger.info("\n✅ 3. jobs 表新字段")
    if "jobs" in tables:
        columns = {col['name']: col['type'] for col in inspector.get_columns("jobs")}
        logger.info(f"   表存在 ✅")
        
        if "personality_requirements" in columns:
            logger.info(f"   • personality_requirements: {columns['personality_requirements']} ✅")
        else:
            logger.error(f"   • personality_requirements: 不存在 ❌")
        
        if "work_environment" in columns:
            logger.info(f"   • work_environment: {columns['work_environment']} ✅")
        else:
            logger.error(f"   • work_environment: 不存在 ❌")
    else:
        logger.error("   表不存在 ❌")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ 数据库迁移验证完成！")
    logger.info("=" * 60)
    logger.info("\n📝 后续步骤：")
    logger.info("   1. 重启应用服务")
    logger.info("   2. 查看 FINAL_DELIVERY_SUMMARY.md 了解新功能")
    logger.info("   3. 参考 QUICK_REFERENCE_GUIDE.md 使用新API")
    
except Exception as e:
    logger.error(f"❌ 验证失败: {str(e)}")
    sys.exit(1)
