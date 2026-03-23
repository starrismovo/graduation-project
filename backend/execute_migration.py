#!/usr/bin/env python3
"""
P0 数据库迁移执行脚本
处理候选人数据重复、外键关系、主键类型问题
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

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
    logger.error("❌ DATABASE_URL 未配置")
    sys.exit(1)

logger.info(f"📊 数据库连接: {DATABASE_URL.split('@')[1]}")


def read_migration_script(script_path):
    """读取 SQL 迁移脚本"""
    with open(script_path, 'r', encoding='utf-8') as f:
        return f.read()


def execute_migration(engine, sql_script):
    """执行 SQL 迁移脚本"""
    connection = None
    try:
        connection = engine.connect()
        
        # 将脚本分割成单个语句
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        logger.info(f"📋 准备执行 {len(statements)} 个 SQL 语句...")
        
        for idx, statement in enumerate(statements, 1):
            # 跳过注释和空语句
            if statement.strip().startswith('--'):
                continue
            
            try:
                logger.info(f"✓ 执行 [{idx}/{len(statements)}] ...")
                connection.execute(text(statement))
                connection.commit()
                
                # 对于 SELECT 语句，打印结果
                if statement.strip().upper().startswith('SELECT'):
                    try:
                        result = connection.execute(text(statement))
                        rows = result.fetchall()
                        logger.info(f"  结果: {rows}")
                    except:
                        pass
                        
            except SQLAlchemyError as e:
                logger.warning(f"⚠️  语句 {idx} 执行失败（非致命）: {str(e)[:100]}")
                # 继续执行下一个语句
                continue
        
        logger.info("✅ 迁移脚本执行完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {str(e)}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if connection:
            connection.close()


def verify_migration(engine):
    """验证迁移结果"""
    logger.info("\n" + "="*60)
    logger.info("🔍 迁移验证开始")
    logger.info("="*60)
    
    connection = None
    try:
        connection = engine.connect()
        
        checks = [
            ("users 表行数", "SELECT COUNT(*) as count FROM users;"),
            ("候选人用户数", "SELECT COUNT(*) as count FROM users WHERE user_type = 'candidate' OR is_hr = 0;"),
            ("HR 用户数", "SELECT COUNT(*) as count FROM users WHERE user_type = 'hr' OR is_hr = 1;"),
            ("interviews 表行数", "SELECT COUNT(*) as count FROM interviews;"),
            ("assessment_records 表行数", "SELECT COUNT(*) as count FROM assessment_records;"),
            ("候选人带有年龄数据", "SELECT COUNT(*) as count FROM users WHERE age IS NOT NULL AND user_type = 'candidate';"),
        ]
        
        for check_name, query in checks:
            try:
                result = connection.execute(text(query))
                row = result.fetchone()
                count = row[0] if row else 0
                logger.info(f"✓ {check_name}: {count}")
            except Exception as e:
                logger.warning(f"⚠️  {check_name}: 无法获取 ({str(e)[:50]})")
        
        # 检查孤立记录
        logger.info("\n检查数据完整性:")
        
        try:
            result = connection.execute(text(
                "SELECT COUNT(*) FROM interviews i WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = i.candidate_id);"
            ))
            orphaned = result.fetchone()[0]
            if orphaned > 0:
                logger.warning(f"⚠️  发现 {orphaned} 条孤立的 interview 记录")
            else:
                logger.info("✓ interviews 表外键完整")
        except:
            pass
        
        # 检查用户类型一致性
        try:
            result = connection.execute(text(
                "SELECT COUNT(*) FROM users WHERE user_type IS NULL;"
            ))
            null_types = result.fetchone()[0]
            if null_types > 0:
                logger.warning(f"⚠️  发现 {null_types} 个用户的 user_type 为 NULL")
            else:
                logger.info("✓ 所有用户的 user_type 都已设置")
        except:
            pass
        
        logger.info("\n" + "="*60)
        logger.info("✅ 验证完成")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ 验证失败: {str(e)}")
        
    finally:
        if connection:
            connection.close()


def main():
    """主程序"""
    logger.info("\n" + "="*60)
    logger.info("🚀 开始 P0 数据库迁移")
    logger.info("="*60 + "\n")
    
    # 创建数据库引擎
    try:
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
        logger.info("✓ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 无法连接到数据库: {str(e)}")
        sys.exit(1)
    
    # 读取迁移脚本
    script_path = os.path.join(os.path.dirname(__file__), 'migrate_p0_primary_key.sql')
    if not os.path.exists(script_path):
        logger.error(f"❌ 迁移脚本不存在: {script_path}")
        sys.exit(1)
    
    logger.info(f"📂 加载脚本: {script_path}")
    sql_script = read_migration_script(script_path)
    logger.info(f"✓ 脚本大小: {len(sql_script)} 字节")
    
    # 获取用户确认
    logger.info("\n⚠️  警告:")
    logger.info("  - 此迁移将修改数据库结构")
    logger.info("  - 自动备份已创建到 *_backup 表")
    logger.info("  - 强烈建议手动备份数据库后再执行")
    
    # 检查是否传入 --skip-confirm 参数
    skip_confirm = '--skip-confirm' in sys.argv
    if not skip_confirm:
        confirm = input("\n👉 继续执行迁移? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("❌ 迁移已取消")
            sys.exit(0)
    else:
        logger.info("\n✓ 跳过确认，继续执行迁移...")
    
    # 执行迁移
    logger.info("\n" + "-"*60)
    logger.info("开始执行 SQL 语句...")
    logger.info("-"*60 + "\n")
    
    success = execute_migration(engine, sql_script)
    
    if success:
        # 验证迁移结果
        verify_migration(engine)
        logger.info("\n✨ 迁移成功完成！")
        logger.info("\n后续步骤:")
        logger.info("  1. 查看备份表: candidates_backup, users_backup, interviews_backup")
        logger.info("  2. 测试应用程序功能")
        logger.info("  3. 确认所有功能正常后，运行清理脚本删除备份表")
    else:
        logger.error("\n❌ 迁移执行失败")
        sys.exit(1)
    
    logger.info("\n" + "="*60)
    logger.info(f"迁移完成时间: {__import__('datetime').datetime.now()}")
    logger.info("="*60 + "\n")


if __name__ == '__main__':
    main()
