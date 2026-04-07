from database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # 查询所有表的大小
        query = """
        SELECT 
            TABLE_NAME,
            ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = 'hr_matching'
        ORDER BY (data_length + index_length) DESC
        """
        result = conn.execute(text(query)).fetchall()
        
        print("[INFO] hr_matching 数据库各表大小:\n")
        total_size = 0
        for row in result:
            table_name = row[0]
            size_mb = row[1] or 0
            total_size += size_mb
            print(f"  {table_name}: {size_mb:.1f}MB")
        
        print(f"\n[INFO] 总占用: {total_size:.1f}MB ({total_size/1024:.2f}GB)")
        
        # 预估导入后的大小（599885条已导入，还需要导入12550000-599885=11950115条）
        print(f"\n[INFO] 预估:")
        print(f"  已导入: 599,885 条")
        print(f"  还需导入: 11,950,115 条")
        print(f"  预估增长倍数: {11950115/599885:.1f}x")
        print(f"  预估最终大小: {total_size * 11950115 / 599885 / 1024:.2f}GB")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
