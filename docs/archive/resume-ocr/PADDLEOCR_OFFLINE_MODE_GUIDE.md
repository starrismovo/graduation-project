# 🔧 PaddleOCR 模型加载问题 - 解决方案

## 📍 问题诊断

你遇到的错误：
```
No available model hosting platforms detected. 
Please check your network connection to one of the following model hoster: 
HuggingFace, ModelScope, AIStudio, or BOS
```

**原因**: PaddleOCR 尝试从网上下载3个模型文件，但无法连接到任何源。

---

## 🚀 快速解决方案 (选择一个)

### ✅ 方案 A: 使用离线模式 (最简单)

代码已更新，现在会**禁用网络检查**并使用离线模式。

**只需要重启后端**:
```bash
# 停止后端 (Ctrl+C)
# 然后重新启动
cd D:\Desktop\graduation-project\backend
python main.py
```

**预期输出**:
```
[INFO] 启用 OCR 识别
[INFO] PDF OCR: 转换为图片进行识别  
[INFO] 初始化 PaddleOCR 模型...
# (可能会显示一些 PaddleOCR 的初始化日志)
[INFO] PDF OCR 识别成功
```

**如果仍然失败** → 继续下面的方案 B

---

### ✅ 方案 B: 预先下载模型 (推荐用于生产环境)

PaddleOCR 需要3个模型：
- `ch_PP-OCRv4_det_infer` (检测模型)
- `ch_PP-OCRv4_rec_infer` (识别模型)  
- `ch_ppocr_mobile_cls` (分类模型)

**步骤 1: 创建模型缓存目录**
```powershell
# Windows
$env:PADDLE_OCR_DIR = "$env:USERPROFILE\.paddleocr"
mkdir $env:PADDLE_OCR_DIR
```

**步骤 2: 下载模型** (选择其中一种方法)

**方法 B1: 使用 Python 脚本自动下载**
```python
import os
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

# 创建一个临时脚本来预加载模型
# 保存为: download_paddle_models.py

from paddleocr import PaddleOCR

print("正在初始化 PaddleOCR (会自动下载模型)...")
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=True)
print("✅ 模型下载完成！")
print(f"模型位置: {os.path.expanduser('~/.paddleocr')}")

# 运行这个脚本
# python download_paddle_models.py
```

**方法 B2: 手动从官方源下载**

如果自动下载失败，从这里下载模型文件：
- https://github.com/PaddlePaddle/PaddleOCR/releases

下载后解压到:
```
Windows: %USERPROFILE%\.paddleocr\
Linux/Mac: ~/.paddleocr/
```

**步骤 3: 验证模型已下载**
```powershell
# Windows
ls $env:USERPROFILE\.paddleocr
# 应该看到三个文件夹:
# - ch_PP-OCRv4_det_infer
# - ch_PP-OCRv4_rec_infer  
# - ch_ppocr_mobile_cls
```

---

### ✅ 方案 C: 更换为更轻量级的 OCR 库 (备选)

如果 PaddleOCR 持续无法工作，可以使用 **EasyOCR** (更简单):

```bash
# 安装
pip install easyocr -i https://pypi.org/simple/

# 这需要修改后端代码，但更容易部署
```

---

## 🛠️ 代码改动说明

已更新 `_ocr_extract_text()` 函数：

**新增**:
```python
import os
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
```

**效果**:
- ✅ 禁用模型源连接性检查
- ✅ 允许使用本地缓存模型
- ✅ 如果本地模型不存在，会提示错误而不是卡住

**其他改进**:
- ✅ 详细的错误日志 (`exc_info=True`)
- ✅ 降低日志输出噪音 (`show_log=False`)
- ✅ 单页失败不影响整个PDF处理
- ✅ 更友好的错误信息

---

## 📋 操作清单

### 立即尝试 (5分钟)
- [ ] 停止后端 (Ctrl+C)
- [ ] 重新启动后端
- [ ] 再次上传扫描PDF
- [ ] **检查后端日志**是否显示模型初始化成功

### 如果还是失败 (10-15分钟)
- [ ] 打开命令行
- [ ] 运行 `python -c "from paddleocr import PaddleOCR; print('✅')"` 
- [ ] 观察是否有错误信息
- [ ] 如有错误，运行 `pip install --upgrade paddleocr`

### 手动下载模型 (30分钟)
- [ ] 创建 `download_paddle_models.py` 脚本
- [ ] 运行脚本下载模型
- [ ] 确认模型文件在 `~/.paddleocr` 目录
- [ ] 重启后端
- [ ] 再次上传文件

---

## 🔍 诊断步骤

### Step 1: 检查 PaddleOCR 是否可导入
```bash
python -c "from paddleocr import PaddleOCR; print('✅ PaddleOCR 可用')"
```

**如果出现错误** → 重新安装:
```bash
pip uninstall paddleocr -y
pip install paddleocr -i https://pypi.org/simple/
```

### Step 2: 查看后端日志
启动后端，观察是否有这些关键日志：
```
✅ [INFO] 启用 OCR 识别，文件格式: .pdf
✅ [INFO] PDF OCR: 转换为图片进行识别
✅ [INFO] 正在OCR识别第 1/X 页...
✅ [INFO] 初始化 PaddleOCR 模型...
✅ [INFO] 执行 OCR 识别...
✅ [INFO] PDF OCR 识别成功，总长度: XXXX

❌ [ERROR] PDF OCR 识别失败: ... → 看具体是什么错误
```

### Step 3: 查看错误详情
从日志中找关键错误信息：
- `No available model hosting platforms` → 需要离线模型
- `ModuleNotFoundError` → PaddleOCR 未安装
- `CUDA out of memory` → GPU 内存不足
- `Timeout` → 网络太慢

---

## ⚠️ 常见错误及解决方案

### 错误 1: "No available model hosting platforms"
**症状**: 跟上次一样的错误  
**原因**: 环境变量没有生效或模型初始化仍需网络  
**解决**:
```bash
# 强制使用离线模式
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = 'True'
$env:PADDLE_INFERENCE_MODEL_DIR = "$env:USERPROFILE\.paddleocr"
python main.py
```

### 错误 2: "Creating model: ('PP-LCNet_x1_0_doc_ori', None) failed"
**症状**: 模型初始化失败  
**原因**: 本地模型不存在或损坏  
**解决**:
```bash
# 删除所有本地模型，重新下载
rmdir $env:USERPROFILE\.paddleocr /s /q
# 然后运行下载脚本
```

### 错误 3: "CUDA out of memory" 或类似 GPU 错误
**症状**: 显存不足  
**原因**: GPU 被占用或模型太大  
**解决**:
```python
# 改为 CPU 模式（在代码中）
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
```

### 错误 4: 卡住/超时
**症状**: 后端没有响应，持续显示 "正在初始化 PaddleOCR 模型..."  
**原因**: 
- 网络卡顿下载模型
- 系统资源不足
- 模型太大

**解决**:
```bash
# 方案 A: 加大超时时间
# 在后端 main.py 中：
# uvicorn.run(..., timeout_keep_alive=300)

# 方案 B: 减少日志输出
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

# 方案 C: 增加系统资源
# 关闭其他应用，释放内存
```

---

## 📊 预期输出

### ✅ 成功情况
```
[2026-03-10 11:50:00,123] [INFO] 启用 OCR 识别，文件格式: .pdf
[2026-03-10 11:50:01,234] [ INFO] PDF OCR: 转换为图片进行识别
[2026-03-10 11:50:02,345] [INFO] 正在OCR识别第 1/1 页...
[2026-03-10 11:50:03,456] [INFO]   初始化 PaddleOCR 模型...
[2026-03-10 11:50:10,567] [INFO]   执行 OCR 识别...
[2026-03-10 11:50:15,678] [INFO]   第 1 页识别完成，提取文本长度: 856
[2026-03-10 11:50:15,789] [INFO] PDF OCR 识别成功，总长度: 856

前端显示: 🤖 OCR识别(扫描版)  ← 成功！
```

### ❌ 失败情况（需要调试）
```
[ERROR] PDF OCR 识别失败: No available model hosting platforms detected
```
→ 需要运行方案 A 或 B

---

## 🎯 最终建议

### 对于开发环境 (你现在的情况)
1. **先尝试半分钟**: 重启后端，看是否自动工作
2. **如不行**: 运行离线模式设置
3. **还不行**: 手动下载模型

### 对于生产环境 (部署到服务器)
1. 提前下载模型到服务器
2. 设置环境变量使用本地模型
3. 测试确认无网络时仍能工作
4. 配置监控告警

---

## 📞 需要帮助？

如果问题仍未解决，请提供：
1. 后端启动时的完整日志
2. 上传文件时的完整错误日志
3. 你的网络情况描述
4. 你使用的操作系统和Python版本

---

**现在就试试方案 A 吧！应该能解决问题 🚀**
