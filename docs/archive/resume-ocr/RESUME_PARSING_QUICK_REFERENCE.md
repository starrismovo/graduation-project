# 🎯 简历解析模块快速参考卡

## 📍 核心位置

```
后端路由      backend/routers/immersive_dialogue.py
服务层        backend/services/resume_parsing_v2.py
配置          backend/paddleocr_local.py
数据库        backend/models/candidate.py
测试文件      backend/test_*.py
```

## 🔄 处理流程一览

```
POST /upload-resume 
    ↓
validate_file()          // 验证格式与大小
    ↓
_extract_resume_text()   // 提取文本（7种处理方式）
    ├─ .txt       → decode
    ├─ .docx      → python-docx
    ├─ .pdf       → pdfplumber (→ OCR if empty)
    ├─ .jpg/.png  → OCR
    ├─ .doc       → fallback
    └─ other      → message
    ↓
_parse_resume_info()     // 解析关键信息（正则+库匹配）
    ├─ name       (regex)
    ├─ email      (regex)
    ├─ phone      (regex)
    ├─ education  (keyword)
    ├─ skills     (library match)
    ├─ soft_skills (semantic)
    └─ experience (text extraction)
    ↓
compute_metadata()       // 计算完整性、维度、关键词
    ↓
return_response()        // JSON 响应
```

## 🛠️ 三层 OCR 降级策略

```
┌─────────────────────────────┐
│ 1️⃣ PaddleOCR (主)           │
│ from paddleocr_local import create_paddleocr
│ ocr = create_paddleocr()
│ result = ocr.ocr(image)     │
└────────────────┬────────────┘
                 │ ❌ fail
                 ▼
┌─────────────────────────────┐
│ 2️⃣ EasyOCR (备选)           │
│ import easyocr
│ reader = easyocr.Reader(['ch'])
│ result = reader.readtext(img) │
└────────────────┬────────────┘
                 │ ❌ fail
                 ▼
┌─────────────────────────────┐
│ 3️⃣ 用户提示 (降级)          │
│ "【⚠️ OCR功能暂不可用】"    │
│ • 手动填写                   │
│ • 尝试其他格式               │
│ • 修复建议                   │
└─────────────────────────────┘
```

## 📊 支持的文件格式

| 格式 | 库 | 说明 | 备注 |
|------|-----|------|------|
| `.txt` | native | 最快 | UTF-8, 120ms |
| `.docx` | python-docx | 可靠 | 需要库, 200ms |
| `.pdf` | pdfplumber | 通用 | 无文本→OCR, 300ms+OCR |
| `.jpg` | PaddleOCR | 自动 | 需要OCR, 1000ms+ |
| `.png` | EasyOCR | 自动 | 需要OCR, 1000ms+ |
| `.doc` | native | 降级 | 提示升级 |

## 🔍 信息提取规则

### 姓名提取
```regex
姓名[:\s：]+([^\n,]+)  // "姓名: 张三"
名字[:\s：]+([^\n,]+)  // "名字: 张三"
Name[:\s]+([^\n,]+)    // "Name: Zhang San"
```

### 邮箱提取
```regex
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
// "zhangsan@example.com"
```

### 电话提取
```regex
1[3-9]\d{9}           // "13800138000"
0\d{2,3}-?\d{7,8}     // "010-12345678" or "01012345678"
```

### 学历识别
```keywords
本科, 硕士, 博士, 大专, 高中
Bachelor, Master, PhD, Associate
```

### 技能识别
```库match
TECH_SKILLS_LIBRARY = [
  "JavaScript", "Python", "Vue", "React",
  "Java", "Docker", "MySQL", ...
]
```

## 🎯 完整性评分

```python
profile_completeness = completed_fields / 5.0

高度完整  0.8 - 1.0  ✅ 优秀
中等完整  0.5 - 0.8  🟡 良好
低度完整  0.0 - 0.5  ⚠️  需补充

评分字段:
1. 姓名
2. 邮箱
3. 学历
4. 技能
5. 工作经历
```

## 📈 评估维度生成

```logic
⟹ 基础: ["技术能力"]

If 技能数 > 0:
  ⟹ 添加 "技术深度"

If 软技能 not empty:
  ⟹ 添加所有软技能 ["沟通能力", "团队合作", ...]

If 级别 in ["高级", "专家级"]:
  ⟹ 添加 ["领导力", "战略思维"]

去重后返回 assessed_dimensions
```

## 🚨 常见错误码

| 代码 | 含义 | 原因 | 解决 |
|------|------|------|------|
| 200 OK | 成功 | 解析完成 | ✅ 正常 |
| 400 INVALID_FORMAT | 格式错误 | 不支持的扩展名 | 检查文件 |
| 413 FILE_TOO_LARGE | 过大 | > 10MB | 压缩文件 |
| 422 EXTRACTION_FAILED | 提取失败 | 库或格式问题 | 安装依赖 |
| 503 OCR_FAILED | OCR 失败 | 模型不可用 | 重启后端 |

## 💾 API 响应结构

```json
{
  "code": 200,
  "message": "简历解析成功",
  "data": {
    "filename": "resume.pdf",
    "file_size": 102400,
    "extracted_text": "前500字...",
    "extraction_method": "native|ocr",
    "candidate_info": {
      "name": "张三",
      "email": "zhang@example.com",
      "phone": "13800138000",
      "education": "本科",
      "experience_level": "中级",
      "technical_skills": ["Python", "Vue"],
      "soft_skills": ["沟通能力"],
      "work_experience": "..."
    },
    "extracted_keywords": [...],
    "profile_completeness": 0.8,
    "assessed_dimensions": [...]
  }
}
```

## 🔧 关键配置

### 环境变量 (已在 paddleocr_local.py 设置)
```bash
PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=1    # 离线模式
PADDLE_PDX_OFFLINE_MODE=True
PADDLE_FLAGS=FLAGS_runtime_eager_delete=0   # 禁用优化
FLAGS_use_cinn=0                            # 禁用 CINN
```

### 文件限制
```python
MAX_FILE_SIZE = 10 * 1024 * 1024   # 10MB
CHUNK_SIZE = 8192                   # 读取块大小
```

### 数据库表
```
candidates          // candidate_id, name, email
candidate_resumes   // 简历存储（如需）
assessment_records  // 评估结果关联
```

## 🐛 快速故障排除

### 症状：OCR 返回【】开头消息
```
原因：文本提取失败或依赖缺失
解决：
  1. pip install python-docx pdfplumber
  2. 检查日志：grep -i "ERROR\|WARN" backend.log
  3. 重启后端
```

### 症状：set_optimization_level 错误 ✅ 已修复
```
原因：Paddle 版本不兼容
解决：
  • 已应用 PaddleX 补丁
  • 已实现延迟加载
  • 重启后端生效
```

### 症状：邮箱/电话提取错误
```
原因：非标准格式
解决：
  1. 检查正则表达式精度
  2. 在 immersive_dialogue.py 中调整 pattern
  3. 测试：python -c "import re; re.search(pattern, text)"
```

### 症状：PDF 识别结果为空
```
原因：PDF 无文本层，需要 OCR
解决：
  1. 检查 PaddleOCR 是否可用：python test_paddleocr.bat
  2. 安装 EasyOCR 作为备选：pip install easyocr
  3. 重启后端
```

## ✅ 检查清单

上传文件前：
- [ ] 后端运行中: `python main.py`
- [ ] 前端运行中: `npm run dev`
- [ ] 文件 ≤ 10MB
- [ ] 扩展名小写: .pdf .docx .txt .jpg
- [ ] 文件非空

上传后：
- [ ] 返回 code=200（成功）或 code=2xx（部分成功）
- [ ] candidate_info 包含至少：name, email
- [ ] profile_completeness > 0
- [ ] assessed_dimensions not empty

## 📚 详细文档

- 完整分析: [RESUME_PARSING_COMPLETE_ANALYSIS.md](RESUME_PARSING_COMPLETE_ANALYSIS.md)
- 诊断工具: [RESUME_PARSING_DIAGNOSTICS.md](RESUME_PARSING_DIAGNOSTICS.md)
- OCR修复: [PADDLEOCR_SETOPTIMIZATION_FIX.md](PADDLEOCR_SETOPTIMIZATION_FIX.md)
- 源代码: 
  - [immersive_dialogue.py](../backend/routers/immersive_dialogue.py)
  - [resume_parsing_v2.py](../backend/services/resume_parsing_v2.py)

## 🔗 相关命令

```bash
# 启动后端
cd backend && python main.py

# 启动前端
cd frontend && npm run dev

# 查看日志
tail -f backend.log | grep "resume\|简历\|OCR"

# 测试 OCR
python test_paddleocr.bat

# 测试 API
curl -X POST http://localhost:8000/assessment/immersive/upload-resume \
  -F "file=@resume.pdf" \
  -F "candidate_id=test_123"

# 查询当前值
grep -n "ALLOWED_EXTENSIONS\|MAX_FILE_SIZE" backend/routers/immersive_dialogue.py
```

## 📞 支持

- **日志位置**: backend.log
- **测试文件**: backend/test_*.py
- **问题追踪**: 查看 [QUICK_FIX_*.md](.) 文件
- **最后更新**: 2026-03-28

---

**💡 提示**: 使用 Ctrl+F 在此文档中快速查找，或访问详细分析文档了解更多。
