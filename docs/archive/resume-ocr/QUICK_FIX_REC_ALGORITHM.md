# ⚡ 参数错误快速修复

**问题**: `ValueError: Unknown argument: rec_algorithm`  
**状态**: ✅ 已修复  
**行动**: 立即重启后端

---

## 🚀 3 步修复

### Step 1️⃣ 停止后端
```powershell
Ctrl + C
```

### Step 2️⃣ 重启后端
```powershell
python main.py
```

### Step 3️⃣ 重试上传
1. 访问 http://localhost:5173
2. 开始评估 → 基本信息
3. 上传 PDF/Word 文件

---

## 如果还是失败？

```powershell
# 安装 EasyOCR (更稳定的备选方案)
pip install easyocr

# 重启后端
python main.py

# 重试上传
```

---

## 新增的自动重试机制

修复添加了：
1. ✅ 参数兼容性检查
2. ✅ 最小化配置自动重试
3. ✅ EasyOCR 安装提示

现在即使参数不兼容，系统也会自动降级！

---

详见: `PADDLEOCR_REC_ALGORITHM_FIX.md`
