# 🚀 OCR 功能激活 - 重启指南

## 为什么需要重启？

后端代码已更新添加了 OCR 功能，但 Python 进程需要重启才能加载新代码。

---

## 📝 重启步骤

### 方式 A: 手动重启 ✅ 快速

**步骤 1: 停止旧的后端进程**
```
在后端终端按: Ctrl + C
等待进程完全停止 (2-3秒)
```

**步骤 2: 验证依赖库**
```bash
cd D:\Desktop\graduation-project\backend
venv\Scripts\activate.ps1
pip list | findstr paddleocr
```
如果显示 `paddleocr` 版本号，说明已安装 ✅
如果没显示，请运行：
```bash
pip install paddleocr pillow -i https://pypi.org/simple/
```

**步骤 3: 重新启动后端**
```bash
# 仍在 backend 文件夹
python main.py
```

**预期输出:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🧪 验证重启成功

### 检查点 1: 后端日志
启动后看后端终端输出是否有：
```
✅ 正常
INFO:     Uvicorn running on http://0.0.0.0:8000

❌ 错误
ModuleNotFoundError: No module named 'paddleocr'
→ 需要重新安装依赖库
```

### 检查点 2: 再次上传扫描PDF

**上传新的扫描版PDF:**
- 打开 http://localhost:5173
- 进入"沉浸式面试" → Step 1  
- 上传你的扫描版 `简历 (1).pdf` (或其他扫描PDF)
- 观察前端控制台和后端日志

**预期看到 (后端日志):**
```
[INFO] 上传简历: candidate_id=..., filename=简历 (1).pdf, ext=.pdf
[INFO] 提取 PDF 格式文件
[WARNING] PDF 文档为空，尝试使用 OCR 识别
[INFO] 启用 OCR 识别，文件格式: .pdf
[INFO] PDF OCR: 转换为图片进行识别
[INFO] 正在OCR识别第 1/X 页...
[INFO] PDF OCR 识别成功，长度: XXXX
[INFO] 解析完成: {...}
```

**预期看到 (前端页面):**
- 识别方式: 🤖 `OCR识别(扫描版)` (橙色标签)
- 姓名: 自动填充
- 邮箱: 自动填充
- 学历: 自动填充
- 技能: 自动识别

---

## ⚠️ 常见问题

### 问题: "ModuleNotFoundError: No module named 'paddleocr'"

**原因**: 依赖库未安装或安装在了全局环境

**解决**:
```bash
# 确保激活虚拟环境
cd D:\Desktop\graduation-project\backend
venv\Scripts\activate.ps1

# 检查虚拟环境是否已激活
# 提示符应该显示 (venv) 前缀

# 重新安装
pip install paddleocr pillow --upgrade -i https://pypi.org/simple/

# 验证
python -c "import paddleocr; print('✅ PaddleOCR 已安装')"
```

### 问题: "错误: We need 'scipy' for this functionality"

**原因**: paddleocr 依赖 scipy 但未同时安装

**解决**:
```bash
pip install paddleocr scipy numpy pillow -i https://pypi.org/simple/
```

### 问题: "错误: torch/onnx runtime not found"

**原因**: paddleocr 需要深度学习框架

**解决**:
```bash
# 自动安装所有依赖
pip install paddleocr[gpu] -i https://pypi.org/simple/
# 或
pip install paddleocr[cpu] -i https://pypi.org/simple/  # 推荐，更轻量
```

### 问题: 重启后仍然显示 "native" (没有OCR标签)

**可能原因**:
1. 后端进程没有完全杀死，旧进程仍在运行
2. 前端缓存了旧的JavaScript代码
3. 网络请求被缓存

**解决**:

**办法1**: 完全杀死后端进程
```bash
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000

# 如果看到 python.exe，记下 PID (最后一列数字)
# 强制杀死
taskkill /PID <PID> /F

# 然后重新启动
python main.py
```

**办法2**: 清除前端缓存
```bash
# 在浏览器按 F12
# 进入 Application 标签
# 清除 Local Storage 和 Cookies
# 刷新页面 (F5)
```

**办法3**: 检查后端是否真的更新了
在后端终端运行：
```bash
python -c "import inspect; from routers.immersive_dialogue import _ocr_extract_text; print('✅ OCR 函数存在'); print(inspect.getsourcefile(_ocr_extract_text))"
```

### 问题: OCR 运行超时 (等待超过 5 分钟)

**可能原因**:
1. 首次运行在下载模型 (~50MB)
2. 文件太大或页数过多
3. 服务器资源不足

**解决**:
1. 首次运行耐心等待 2-5 分钟让模型下载完成
2. 模型缓存后速度会快很多
3. 尝试上传单页PDF测试

---

## 🎯 如果仍然不工作

### 完整故障排查流程

**Step 1: 检查虚拟环境**
```bash
cd D:\Desktop\graduation-project\backend
venv\Scripts\activate.ps1
python --version
which python  # 应该显示 venv 路径
```

**Step 2: 检查依赖**
```bash
pip list | grep -E "paddleocr|pillow|pdfplumber|python-docx"
# 所有都应该显示版本号
```

**Step 3: 测试导入**
```bash
python -c "
import paddleocr
import PIL
import pdfplumber
import docx
print('✅ 所有库都可用')
"
```

**Step 4: 查看后端日志**
- 启动后端: `python main.py`
- 上传文件，观察日志输出
- 复制任何错误信息

**Step 5: 查看前端日志**
- F12 打开控制台
- 上传文件
- 查看 Network 标签中 upload-resume 的响应
- 检查 Response 中是否包含 "extraction_method" 字段

---

## ✅ 重启完成检查清单

- [ ] Ctrl+C 停止了后端进程
- [ ] 虚拟环境已激活 (显示 (venv) 前缀)
- [ ] `pip list` 看到了 paddleocr
- [ ] 后端重新启动成功
- [ ] 后端日志显示 "Uvicorn running on..."
- [ ] 前端仍可访问 http://localhost:5173
- [ ] 可以上传文件到系统
- [ ] 后端日志有 "开始提取文本" 消息
- [ ] 对扫描PDF，后端日志有 "OCR" 相关消息
- [ ] 前端看到 "🤖 OCR识别(扫描版)" 标签

---

## 🚀 现在就试试

1. **停止后端**: Ctrl+C
2. **重启后端**: `python main.py`
3. **打开前端**: http://localhost:5173
4. **上传扫描PDF**: 简历 (1).pdf
5. **观察结果**: 应该看到 🤖 OCR识别标签!

---

## 📞 如果还是不行

请检查后端终端的完整错误信息，通常会显示：
```
ERROR: ...
```

常见的错误信息及解决方案已列在上面。

**祝你成功！** 🎉
