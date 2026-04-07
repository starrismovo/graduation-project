#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL 数据迁移脚本 - C盘 → D盘
"""

import os
import sys
import shutil
import time
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    SOURCE_DATA = r"C:\ProgramData\MySQL\MySQL Server 5.7\Data"
    TARGET_DATA = r"D:\MySQLData"
    CONFIG_FILE = r"C:\ProgramData\MySQL\MySQL Server 5.7\my.ini"
    
    print("\n" + "="*70)
    print("MySQL 数据迁移工具 (C盘 → D盘)")
    print("="*70)
    
    # 步骤1: 检查源路径
    print("\n[STEP 1] 检查源路径...")
    if not os.path.exists(SOURCE_DATA):
        logger.error(f"❌ 源路径不存在: {SOURCE_DATA}")
        return False
    logger.info(f"✓ 源路径存在: {SOURCE_DATA}")
    
    # 检查源大小
    source_size = 0
    try:
        for root, dirs, files in os.walk(SOURCE_DATA):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    source_size += os.path.getsize(filepath)
                except:
                    pass
        logger.info(f"✓ 源数据大小: {source_size / 1024 / 1024 / 1024:.2f}GB")
    except Exception as e:
        logger.warning(f"⚠ 无法计算源数据大小: {e}")
    
    # 步骤2: 检查目标空间
    print("\n[STEP 2] 检查目标磁盘空间...")
    try:
        stat = shutil.disk_usage("D:\\")
        free_space = stat.free / 1024 / 1024 / 1024
        required_space = source_size / 1024 / 1024 / 1024 * 1.2  # 留20%余量
        
        logger.info(f"✓ D盘可用空间: {free_space:.2f}GB")
        logger.info(f"✓ 迁移所需空间: {required_space:.2f}GB")
        
        if free_space < required_space:
            logger.error(f"❌ D盘空间不足! 需要{required_space:.2f}GB，实际{free_space:.2f}GB")
            return False
        logger.info(f"✓ 空间检查通过")
    except Exception as e:
        logger.error(f"❌ 无法查询磁盘空间: {e}")
        return False
    
    # 步骤3: 创建备份（以防万一）
    print("\n[STEP 3] 创建原数据备份...")
    backup_path = r"C:\ProgramData\MySQL\MySQL Server 5.7\Data_backup"
    if os.path.exists(backup_path):
        logger.info(f"⚠ 备份目录已存在，跳过备份")
    else:
        try:
            logger.info(f"正在备份到: {backup_path}")
            logger.info("这可能需要几分钟...")
            shutil.copytree(SOURCE_DATA, backup_path)
            logger.info(f"✓ 备份完成")
        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            logger.error("⚠ 继续可能有风险，建议停止")
            response = input("是否继续? (y/n): ").strip().lower()
            if response != 'y':
                return False
    
    # 步骤4: 复制数据到D盘
    print("\n[STEP 4] 复制数据到D盘...")
    try:
        # 创建目标目录
        if os.path.exists(TARGET_DATA):
            logger.info(f"⚠ 目标目录已存在: {TARGET_DATA}")
            response = input("是否覆盖? (y/n): ").strip().lower()
            if response == 'y':
                logger.info("正在删除旧数据...")
                shutil.rmtree(TARGET_DATA)
            else:
                return False
        
        logger.info(f"正在复制数据到: {TARGET_DATA}")
        logger.info("这可能需要 5-20 分钟（取决于数据大小）...")
        
        shutil.copytree(SOURCE_DATA, TARGET_DATA)
        logger.info(f"✓ 数据复制完成")
        
        # 验证复制
        logger.info("正在验证数据完整性...")
        target_size = 0
        for root, dirs, files in os.walk(TARGET_DATA):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    target_size += os.path.getsize(filepath)
                except:
                    pass
        
        if abs(source_size - target_size) > 1024 * 1024:  # 允许1MB差异
            logger.error(f"❌ 数据验证失败!")
            logger.error(f"源: {source_size / 1024 / 1024 / 1024:.2f}GB, 目标: {target_size / 1024 / 1024 / 1024:.2f}GB")
            return False
        logger.info(f"✓ 数据验证通过")
        
    except Exception as e:
        logger.error(f"❌ 复制失败: {e}")
        return False
    
    # 步骤5: 修改MySQL配置
    print("\n[STEP 5] 修改MySQL配置...")
    try:
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"❌ 配置文件不存在: {CONFIG_FILE}")
            return False
        
        # 读取配置
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 备份原配置
        backup_config = CONFIG_FILE + '.backup'
        with open(backup_config, 'w', encoding='utf-8') as f:
            f.write(config_content)
        logger.info(f"✓ 配置文件备份: {backup_config}")
        
        # 替换datadir
        lines = config_content.split('\n')
        new_lines = []
        found_datadir = False
        
        for line in lines:
            if line.strip().startswith('datadir'):
                logger.info(f"找到 datadir 配置: {line.strip()}")
                new_lines.append(f'datadir="{TARGET_DATA}"')
                found_datadir = True
                logger.info(f"修改为: datadir=\"{TARGET_DATA}\"")
            else:
                new_lines.append(line)
        
        if not found_datadir:
            logger.warning("⚠ 未找到 datadir 配置，添加新行...")
            # 在[mysqld]后添加
            for i, line in enumerate(new_lines):
                if line.strip() == '[mysqld]':
                    new_lines.insert(i+1, f'datadir="{TARGET_DATA}"')
                    found_datadir = True
                    break
        
        if not found_datadir:
            logger.error("❌ 无法修改datadir配置")
            return False
        
        # 写回配置
        new_config = '\n'.join(new_lines)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(new_config)
        logger.info(f"✓ 配置文件已更新")
        
    except Exception as e:
        logger.error(f"❌ 修改配置失败: {e}")
        return False
    
    # 步骤6: 重启MySQL服务
    print("\n[STEP 6] 重启MySQL服务...")
    try:
        import subprocess
        
        # 停止服务
        logger.info("正在停止MySQL服务...")
        subprocess.run(['net', 'stop', 'MySQL57'], capture_output=True)
        time.sleep(2)
        
        # 启动服务
        logger.info("正在启动MySQL服务...")
        result = subprocess.run(['net', 'start', 'MySQL57'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ MySQL服务已重启")
        else:
            logger.warning(f"⚠ 启动可能需要管理员权限: {result.stderr}")
            logger.info("请手动重启: net start MySQL57")
        
    except Exception as e:
        logger.error(f"⚠ 无法自动重启服务: {e}")
        logger.info("请手动执行: net start MySQL57")
    
    # 步骤7: 验证
    print("\n[STEP 7] 验证迁移...")
    time.sleep(3)
    
    try:
        from database import SessionLocal
        db = SessionLocal()
        
        # 测试连接
        from sqlalchemy import text
        result = db.execute(text("SELECT DATABASE()")).fetchall()
        db.close()
        
        logger.info("✓ MySQL连接成功")
        logger.info("✓ 迁移完成！")
        
        return True
    except Exception as e:
        logger.warning(f"⚠ 连接测试失败: {e}")
        logger.info("请确保MySQL服务已重启，并检查配置文件")
        return False

if __name__ == '__main__':
    success = main()
    
    if success:
        print("\n" + "="*70)
        print("✓ 迁移成功！")
        print("="*70)
        print("\n下一步：运行导入脚本继续导入数据")
        print("  python 招聘数据/import_zhilian.py 2")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ 迁移失败")
        print("="*70)
        sys.exit(1)
