"""
初始化 MySQL 数据库中的测试情景数据
不依赖 FastAPI，仅通过 SQLAlchemy 直接操作
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# 加载 .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not configured in .env")

print(f"Using DATABASE_URL: {DATABASE_URL}")

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)

# 定义场景数据
scenarios_data = [
    {
        "id": "scenario_001",
        "title": "项目紧急应对",
        "description": "你正在负责一个关键项目，突然发现上游部门提供的核心数据有严重错误，导致已经开发了一周的功能需要重新设计。时间紧张，你需要在三天内重新交付。你会如何应对这个挑战？",
        "target_traits": '["责任心", "压力应对", "解决问题能力"]',
        "max_rounds": 3
    },
    {
        "id": "scenario_002",
        "title": "团队冲突处理",
        "description": "你所在的团队中，两位重要成员因为技术方案选择产生了严重分歧，影响了工作效率。一方坚持使用已有的技术栈，另一方认为需要引入新技术以提高效率。作为项目负责人，你需要在这次冲突中找到解决方案。",
        "target_traits": '["沟通能力", "决策力", "团队协作"]',
        "max_rounds": 3
    },
    {
        "id": "scenario_003",
        "title": "创意方案评估",
        "description": "团队成员提出了一个创新的功能方案，可以大幅提升产品竞争力，但实现成本很高且风险不确定。你需要评估这个方案是否值得投入，并考虑如何向上级说服或者如何向提案者解释不通过的原因。",
        "target_traits": '["创新思维", "战略思维", "风险评估"]',
        "max_rounds": 3
    }
]

try:
    with engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='hr_matching' AND TABLE_NAME='scenarios'"
        ))
        table_exists = result.scalar() > 0
        
        if not table_exists:
            print("[INFO] scenarios table does not exist, skipping insert")
            print("[INFO] Please run: python -m uvicorn main:app to create tables")
        else:
            # 清空现有数据（可选）
            # conn.execute(text("DELETE FROM scenarios"))
            
            # 插入场景数据
            for scenario in scenarios_data:
                try:
                    conn.execute(text(
                        """INSERT IGNORE INTO scenarios (id, title, description, target_traits, max_rounds, created_at, updated_at)
                           VALUES (:id, :title, :description, :target_traits, :max_rounds, NOW(), NOW())"""
                    ), {
                        "id": scenario["id"],
                        "title": scenario["title"],
                        "description": scenario["description"],
                        "target_traits": scenario["target_traits"],
                        "max_rounds": scenario["max_rounds"]
                    })
                    print(f"[OK] Inserted scenario: {scenario['id']} - {scenario['title']}")
                except Exception as e:
                    print(f"[ERROR] Failed to insert {scenario['id']}: {e}")
            
            print("\n[SUCCESS] All scenarios initialized")
            
            # 验证
            result = conn.execute(text("SELECT id, title FROM scenarios"))
            rows = result.fetchall()
            print(f"\n--- Scenarios in Database ({len(rows)} total) ---")
            for row in rows:
                print(f"  {row[0]}\t{row[1]}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
