# candidate_id 参数问题 - 快速修复指南

## 🔴 问题诊断

### 当前状态分析

**前端侧** (`ImmersiveRoleDialogue.vue`)：
```typescript
// 前端发送 candidate_id 为字符串
const params = new URLSearchParams()
params.append('candidate_id', props.candidateId)  // ✅ 字符串

const response = await fetch(
  `/assessment/immersive/upload-resume?${params.toString()}`,
  { method: 'POST', body: formData }
)
```

**后端侧** (`immersive_dialogue.py`)：
```python
@router.post("/upload-resume")
async def upload_resume(
    candidate_id: str = Query(...),  # ✅ 期望字符串
    db: Session = Depends(get_db)
):
    # 但在某些地方...
    AssessmentRecord.candidate_id == int(candidate_id)  # ❌ 类型转换！
```

**问题来源**：
- 前端传：`"123"` (字符串)
- 后端期望：字符串 ✅
- 但数据库查询时：`int("123")` ✅ (如果是纯数字OK)
- **风险**：如果是 UUID(`"cand_abc123"`)，`int()` 会抛异常 ❌

---

## ✅ 快速修复（5 分钟）

### 首先：理解你的 candidate_id 格式

**检查数据库**：

```python
# 在后端运行
from models.candidate import Candidate
from database import SessionLocal

db = SessionLocal()
candidates = db.query(Candidate).limit(5).all()

for c in candidates:
    print(f"ID: {c.id} | Type: {type(c.id).__name__}")
    
# 输出示例：
# ID: 1 | Type: int
# ID: cand_123 | Type: str
```

### 修复方案（选择一个）

#### 🔧 方案 A：候选人 ID 为纯数字（最常见）

**支持**：`1`, `123`, `999`

```python
# routers/immersive_dialogue.py

def _parse_candidate_id(candidate_id: str) -> int | str:
    """解析 candidate_id，支持整数或字符串"""
    try:
        # 尝试转换为整数
        return int(candidate_id)
    except ValueError:
        # 不是整数，保持为字符串
        return candidate_id

# 在所有接口中使用
@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: str = Query(...),
    db: Session = Depends(get_db)
):
    # ✅ 新增：统一处理 candidate_id
    candidate_id_normalized = _parse_candidate_id(candidate_id)
    
    # 使用规范化后的 ID
    record = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate_id_normalized
    ).first()
    
    # ... rest of code
```

#### 🔧 方案 B：候选人 ID 为字符串（UUID 格式）

**支持**：`"cand_123"`, `"user_abc123"`, 或 UUID

```python
# routers/immersive_dialogue.py

def _validate_candidate_id(candidate_id: str) -> str:
    """验证并规范化 candidate_id（字符串格式）"""
    if not candidate_id or not candidate_id.strip():
        raise ValueError("候选人ID不能为空")
    
    normalized = candidate_id.strip()
    
    if len(normalized) > 100:
        raise ValueError("候选人ID长度不能超过100")
    
    return normalized

# 在所有接口中使用
@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: str = Query(...),
    db: Session = Depends(get_db)
):
    # ✅ 新增：验证并规范化 candidate_id
    try:
        candidate_id = _validate_candidate_id(candidate_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 使用规范化后的 ID
    record = db.query(AssessmentRecord).filter(
        AssessmentRecord.candidate_id == candidate_id
    ).first()
    
    # ... rest of code
```

---

## 🔍 具体修复步骤

### 第1步：检查当前 candidate_id 的格式

```bash
# 在项目根目录运行
cd backend
python

# 在 Python 中运行
from models.candidate import Candidate
from database import SessionLocal

db = SessionLocal()

# 查看真实的 candidate_id 类型和值
candidates = db.query(Candidate).limit(10).all()
print("Current candidate_id samples:")
for c in candidates:
    print(f"  - {repr(c.id)} (type: {type(c.id).__name__})")
```

**可能的输出**：
```
# 情况 1：纯数字（整数）
Current candidate_id samples:
  - 1 (type: int)
  - 2 (type: int)

# 情况 2：字符串（UUID）
Current candidate_id samples:
  - 'cand_001' (type: str)
  - 'user_002' (type: str)

# 情况 3：混合（危险！）
Current candidate_id samples:
  - 1 (type: int)
  - 'cand_abc' (type: str)
```

### 第2步：根据结果选择修复方案

| 情况 | 修复方案 | 复杂度 |
|------|---------|--------|
| 全是整数 | 方案 A | ⭐ 低 |
| 全是字符串 | 方案 B | ⭐ 低 |
| 混合类型 | 方案 C | ⭐⭐⭐ 高 |

#### 🔧 方案 C：混合类型处理（如果需要）

```python
def _normalize_candidate_id(candidate_id: str) -> int | str:
    """处理混合类型的 candidate_id"""
    if not candidate_id:
        raise ValueError("candidate_id 不能为空")
    
    # 第1优先级：尝试转整数
    try:
        return int(candidate_id)
    except ValueError:
        pass
    
    # 第2优先级：验证字符串格式
    normalized = candidate_id.strip()
    if len(normalized) > 100:
        raise ValueError("candidate_id 过长")
    
    if not normalized:
        raise ValueError("candidate_id 不能为空")
    
    return normalized
```

### 第3步：在所有使用 candidate_id 的地方应用修复

在 `immersive_dialogue.py` 中找到所有接口：

```python
# 🔴 需要修复的接口列表：

1. @router.post("/next-question")
   async def get_next_question(
       candidate_id: str = Query(...),
       ...
   )

2. @router.post("/analyze-response")
   async def analyze_candidate_response(
       candidate_id: str = Query(...),
       ...
   )

3. @router.post("/save-session")
   async def save_assessment_session(
       request_data: Dict[str, Any],  # 包含 candidate_id
       ...
   )

4. @router.post("/parse-resume")
   async def parse_resume(
       candidate_id: str = Query(...),
       ...
   )

5. @router.post("/upload-resume")
   async def upload_resume(
       candidate_id: str = Query(...),
       ...
   )

6. @router.get("/candidate/{candidate_id}/sessions")
   async def get_candidate_sessions(
       candidate_id: str,
       ...
   )
```

为每个接口添加验证：

```python
# 模板代码
@router.post("/endpoint-name")
async def endpoint_function(
    candidate_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """接口描述"""
    try:
        # ✅ 新增：验证 candidate_id
        candidate_id = _normalize_candidate_id(candidate_id)
        
        # 原有业务逻辑
        # db.query(...).filter(Model.candidate_id == candidate_id)
        
        return { "code": 200, "data": {...} }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
```

### 第4步：测试修复

**本地测试脚本**：

```bash
# 在后端目录运行
python

# 测试脚本
import requests
import json

BASE_URL = "http://localhost:8000"

# 测试 1：有效的 candidate_id（整数）
response = requests.post(
    f"{BASE_URL}/assessment/immersive/parse-resume",
    params={
        "candidate_id": "123",
        "candidate_name": "测试用户",
        "candidate_email": "test@example.com"
    }
)
print(f"Test 1 (整数ID): {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 测试 2：有效的 candidate_id（字符串）
response = requests.post(
    f"{BASE_URL}/assessment/immersive/parse-resume",
    params={
        "candidate_id": "cand_abc123",
        "candidate_name": "测试用户",
        "candidate_email": "test@example.com"
    }
)
print(f"Test 2 (字符串ID): {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 测试 3：无效的 candidate_id（空）
response = requests.post(
    f"{BASE_URL}/assessment/immersive/parse-resume",
    params={
        "candidate_id": "",
        "candidate_name": "测试用户",
        "candidate_email": "test@example.com"
    }
)
print(f"Test 3 (空ID): {response.status_code}")
print(json.dumps(response.json(), indent=2))
```

---

## 📋 修复检查清单

- [ ] 检查数据库中 candidate_id 的类型（整数/字符串/混合）
- [ ] 选择合适的修复方案（A/B/C）
- [ ] 添加验证/规范化函数
- [ ] 在所有 6 个接口中应用修复
- [ ] 本地测试（整数、字符串、空值、超长值）
- [ ] 检查日志输出（无 type error）
- [ ] 测试与前端的集成
- [ ] 提交代码变更
- [ ] 更新文档

---

## 🔗 相关文件

| 文件 | 用途 |
|------|------|
| `backend/routers/immersive_dialogue.py` | 需要修复的主文件 |
| `backend/models/candidate.py` | 检查 ID 字段类型 |
| `backend/models/assessment.py` | 检查外键类型 |
| `services/resume_parsing_v2.py` | 新增优化模块（可选） |

---

## 🚨 可能的错误信息及解决

### 错误 1：`ValueError: invalid literal for int()`
```
❌ 原因：candidate_id 是字符串但不是纯数字
✅ 解决：使用方案 B 或 C，保持字符串格式
```

### 错误 2：`sqlalchemy.exc.StatementError`
```
❌ 原因：查询条件类型不匹配
✅ 解决：确保 candidate_id 与数据库字段类型一致
```

### 错误 3：`TypeError: unsupported operand type(s)`
```
❌ 原因：混合了不同类型
✅ 解决：使用方案 C 统一处理
```

---

## 💡 最佳实践

1. **统一验证层**
   ```python
   # ✅ 好
   candidate_id = validate_and_normalize(candidate_id)
   
   # ❌ 差
   candidate_id = candidate_id  # 直接使用
   ```

2. **审计日志**
   ```python
   logger.info(f"候选人ID验证: {repr(input_id)} -> {repr(normalized_id)}")
   ```

3. **类型提示**
   ```python
   def process(candidate_id: int | str) -> int | str:
       """明确支持的类型"""
       pass
   ```

4. **单元测试**
   ```python
   def test_normalize_candidate_id():
       assert normalize("123") == 123
       assert normalize("cand_abc") == "cand_abc"
       with pytest.raises(ValueError):
           normalize("")
   ```

---

## 📞 如需帮助

如果在修复过程中遇到问题：

1. 检查日志：`tail -f backend.log | grep candidate_id`
2. 运行诊断脚本（第2步）
3. 查看相关数据库表的 Schema
4. 参考 `resume_parsing_v2.py` 中的 `CandidateIDValidator` 类
