import os
import sys

mysql_dir = r"C:\ProgramData\MySQL\MySQL Server 5.7\Data\hr_matching"

print(f"[INFO] 检查目录: {mysql_dir}")
print(f"[INFO] 目录存在: {os.path.exists(mysql_dir)}")

if os.path.exists(mysql_dir):
    try:
        files = os.listdir(mysql_dir)
        total_size = 0
        
        print(f"\n[INFO] 大于10MB的文件:")
        big_files = []
        for fname in files:
            fpath = os.path.join(mysql_dir, fname)
            try:
                fsize = os.path.getsize(fpath)
                total_size += fsize
                if fsize > 10 * 1024 * 1024:  # > 10MB
                    size_mb = fsize / 1024 / 1024
                    big_files.append((fname, size_mb))
            except Exception as e:
                pass
        
        # 按大小排序
        big_files.sort(key=lambda x: x[1], reverse=True)
        for fname, size_mb in big_files[:20]:
            print(f"  {fname}: {size_mb:.1f}MB")
        
        print(f"\n[INFO] MySQL hr_matching 数据库总占用: {total_size / 1024 / 1024 / 1024:.2f}GB")
        print(f"[INFO] 总文件数: {len(files)}")
                
    except PermissionError:
        print("[ERROR] 权限不足，无法访问这个目录")
    except Exception as e:
        print(f"[ERROR] {e}")
else:
    print("[ERROR] 目录不存在")
