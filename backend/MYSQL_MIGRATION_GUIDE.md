# MySQL 数据迁移指南 (C盘 → D盘)

## 📋 背景
- **问题**: MySQL数据目录在C盘（C:\ProgramData\MySQL\MySQL Server 5.7\Data），空间不足
- **解决**: 将MySQL数据迁移到D盘（D:\MySQLData），D盘有足够空间
- **当前进度**: 配置文件已修改，准备移动数据

## 🔧 迁移步骤

### ✅ 已完成
- [x] 分析磁盘空间
- [x] 修改MySQL配置文件（my.ini）
- [x] 创建D盘目标目录

### ⏳ 需要手动执行（以管理员身份）
需要在**管理员PowerShell或CMD**中执行以下步骤：

#### 方式1: 使用准备好的批处理文件（推荐）

**在Windows Explorer中:**
1. 找到文件: `D:\Desktop\graduation-project\backend\migrate_mysql.bat`
2. 右键点击
3. 选择 "以管理员身份运行"
4. 等待完成

**或在PowerShell (管理员模式):**
```powershell
cd D:\Desktop\graduation-project\backend
.\migrate_mysql.bat
```

#### 方式2: 手动执行命令

**在管理员PowerShell中逐条运行:**

```powershell
# 1. 停止 MySQL 服务
net stop MySQL57

# 等待2秒
Start-Sleep -Seconds 2

# 2. 复制数据到D盘
Copy-Item -Path "C:\ProgramData\MySQL\MySQL Server 5.7\Data\*" -Destination "D:\MySQLData" -Recurse -Force

# 3. 启动 MySQL 服务
net start MySQL57

# 4. 等待启动完成
Start-Sleep -Seconds 3

# 5. 验证服务状态
Get-Service MySQL57 | Select-Object Name, Status
```

## ✔️ 验证迁移成功

迁移完成后，运行验证脚本：

```bash
python check_disk.py
```

**预期输出:**
```
[INFO] MySQL datadir: D:\MySQLData
[INFO] hr_matching 数据库占用: 0.97GB
[INFO] boss_raw_data 表: 599,885 条记录
```

## ⚠️ 故障排除

### 如果MySQL无法启动

**症状:** `net start MySQL57` 返回错误

**解决方案:**

1. 检查事件查看器：
   ```powershell
   Get-EventLog -LogName Application -Source MySQL57 -Newest 10
   ```

2. 使用还原脚本恢复配置：
   ```powershell
   .\restore_mysql_config.bat
   ```

3. 手动检查权限：
   ```powershell
   Get-Acl D:\MySQLData
   ```

### 如果数据复制失败

**症状:** 复制时报告"访问被拒绝"

**解决方案:**
1. 确保以管理员身份运行
2. 检查D盘是否有足够空间（需要~30GB）
3. 确保D:\MySQLData目录可写

## 🔄 恢复原配置

如果需要恢复到C盘配置：

```powershell
.\restore_mysql_config.bat
```

或手动执行：
```powershell
$backupFile = "C:\ProgramData\MySQL\MySQL Server 5.7\my.ini.backup_*" | Get-ChildItem | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item -Path $backupFile.FullName -Destination "C:\ProgramData\MySQL\MySQL Server 5.7\my.ini" -Force
net start MySQL57
```

## 📊 迁移后续步骤

迁移成功并验证后，继续导入数据：

```bash
# 从现有599,885条记录后续断导入
python 招聘数据/import_zhilian.py 2
```

## 📝 技术细节

**配置修改:**
```ini
# 之前:
datadir=C:/ProgramData/MySQL/MySQL Server 5.7/Data

# 之后:
datadir="D:\MySQLData"
```

**磁盘空间统计:**
| 项目 | 大小 |
|-----|------|
| C盘可用 | 19.5 GB |
| boss_raw_data表 | 984.9 MB |
| 预估最终大小 | ~19.24 GB |
| D盘可用 | 33.46 GB ✓充足 |

## ❓ 常见问题

**Q: 迁移需要多久?**  
A: 数据复制通常需要 5-15 分钟（取决于磁盘速度和文件系统）

**Q: 可以中途停止吗?**  
A: 不建议。如果中途停止，请运行恢复脚本恢复原配置

**Q: 迁移后原C盘数据怎么办?**  
A: 可以在验证D盘数据完整后，手动删除C:\ProgramData\MySQL\MySQL Server 5.7\Data目录以释放空间

**Q: 是否影响现有的导入进度?**  
A: 不影响。迁移完成后，数据和进度都在D盘，可以直接继续导入
