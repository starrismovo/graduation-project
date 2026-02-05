"""
测试数据库连接脚本
运行: python test_db.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"数据库连接字符串: {DATABASE_URL}")

try:
    from database import engine
    print("✓ 成功导入 database 模块")
    
    # 测试连接
    with engine.connect() as conn:
        print("✓ 成功连接到数据库")
        result = conn.execute("SELECT 1")
        print(f"✓ 数据库查询正常: {result.fetchone()}")
        
except ImportError as e:
    print(f"✗ 导入错误: {e}")
    print("  请确保已安装: pip install sqlalchemy pymysql")
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    print("  请检查:")
    print("  1. MySQL 服务是否运行")
    print("  2. 数据库地址、用户名、密码是否正确")
    print("  3. .env 文件中的 DATABASE_URL 配置是否正确")
