from database import engine
import os
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # 查看MySQL数据目录
        result = conn.execute(text("SHOW VARIABLES LIKE 'datadir'")).fetchall()
        if result:
            datadir = result[0][1]
            print(f"[INFO] MySQL datadir: {datadir}")
            
            # 查看hr_matching数据库的大小
            if os.path.exists(datadir):
                total_size = 0
                db_dir = os.path.join(datadir, "hr_matching")
                if os.path.exists(db_dir):
                    for file in os.listdir(db_dir):
                        fpath = os.path.join(db_dir, file)
                        if os.path.isfile(fpath):
                            fsize = os.path.getsize(fpath)
                            total_size += fsize
                            if fsize > 100 * 1024 * 1024:  # 超过100MB的文件
                                print(f"  {file}: {fsize / 1024**3:.2f}GB")
                    print(f"[INFO] hr_matching 数据库总占用: {total_size / 1024**3:.2f}GB")
        
        # 检查boss_raw_data表的大小
        result = conn.execute(text("SELECT COUNT(*) as cnt FROM boss_raw_data")).fetchall()
        if result:
            cnt = result[0][0]
            print(f"\n[INFO] boss_raw_data 表: {cnt:,} 条记录")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
