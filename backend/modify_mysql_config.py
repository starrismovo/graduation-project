#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL 数据迁移方案2 - 靠MySQL本身来迁移
策略: 修改MySQL配置，让它使用D盘的新数据目录
"""

import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def modify_mysql_config():
    """修改MySQL配置文件，改变datadir到D盘"""
    
    CONFIG_FILE = r"C:\ProgramData\MySQL\MySQL Server 5.7\my.ini"
    NEW_DATADIR = r"D:\MySQLData"
    
    print("\n" + "="*70)
    print("MySQL 配置修改 - 改变datadir到D盘")
    print("="*70)
    
    print(f"\n[INFO] 配置文件: {CONFIG_FILE}")
    print(f"[INFO] 新数据目录: {NEW_DATADIR}")
    
    # 检查文件
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"❌ 配置文件不存在: {CONFIG_FILE}")
        return False
    
    # 创建目标目录
    print(f"\n[STEP 1] 创建目标数据目录...")
    try:
        os.makedirs(NEW_DATADIR, exist_ok=True)
        logger.info(f"✓ 目录已创建/存在: {NEW_DATADIR}")
    except Exception as e:
        logger.error(f"❌ 无法创建目录: {e}")
        return False
    
    # 读取现有配置
    print(f"\n[STEP 2] 读取配置文件...")
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            config_lines = f.readlines()
        logger.info(f"✓ 共读取 {len(config_lines)} 行")
    except Exception as e:
        logger.error(f"❌ 无法读取配置: {e}")
        return False
    
    # 备份原配置
    print(f"\n[STEP 3] 备份原配置...")
    try:
        backup_file = CONFIG_FILE + '.backup_' + __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(config_lines)
        logger.info(f"✓ 备份文件: {backup_file}")
    except Exception as e:
        logger.error(f"⚠ 无法创建备份: {e}")
    
    # 修改配置
    print(f"\n[STEP 4] 修改datadir配置...")
    modified = False
    new_lines = []
    
    for line in config_lines:
        # 查找datadir配置行
        if re.match(r'^\s*datadir\s*=', line, re.IGNORECASE):
            logger.info(f"找到: {line.strip()}")
            new_line = f'datadir="{NEW_DATADIR}"\n'
            logger.info(f"改为: {new_line.strip()}")
            new_lines.append(new_line)
            modified = True
        else:
            new_lines.append(line)
    
    if not modified:
        logger.warning("⚠ 未找到现有的datadir配置")
        logger.info(f"将在[mysqld]后添加新配置...")
        
        # 在[mysqld]后添加
        for i, line in enumerate(new_lines):
            if re.match(r'^\[mysqld\]', line):
                new_lines.insert(i+1, f'datadir="{NEW_DATADIR}"\n')
                modified = True
                logger.info(f"在第{i+1}行后添加了datadir配置")
                break
    
    if not modified:
        logger.error("❌ 无法修改配置")
        return False
    
    # 写回配置
    print(f"\n[STEP 5] 保存配置文件...")
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        logger.info(f"✓ 配置已保存")
    except Exception as e:
        logger.error(f"❌ 无法保存配置: {e}")
        return False
    
    # 显示关键信息
    print(f"\n" + "="*70)
    print("✓ 配置已修改")
    print("="*70)
    print(f"""
【警告】为了完成迁移，你需要手动执行以下操作：

1. 停止MySQL服务（管理员权限）:
   net stop MySQL57

2. 将C盘旧数据复制到D盘新位置：
   xcopy "C:\\ProgramData\\MySQL\\MySQL Server 5.7\\Data\\*" "{NEW_DATADIR}" /E /I /Y

   或用PowerShell (管理员):
   Copy-Item -Path "C:\\ProgramData\\MySQL\\MySQL Server 5.7\\Data\\*" -Destination "{NEW_DATADIR}" -Recurse -Force

3. 启动MySQL服务：
   net start MySQL57

4. 验证MySQL是否正常启动：
   Get-Service MySQL57 | Select Status

5. 验证数据库连接：
   python check_disk.py

【配置修改说明】
✓ 配置文件已修改，datadir 指向 {NEW_DATADIR}
✓ 原配置备份已保存
✓ 请按照上述步骤手动完成迁移

如果遇到问题，可以恢复备份文件：
  {CONFIG_FILE}.backup_*
    """)
    
    return True

if __name__ == '__main__':
    success = modify_mysql_config()
    print()
    if not success:
        print("❌ 配置修改失败")
        import sys
        sys.exit(1)
