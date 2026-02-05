# BasicInfo 模块前后端联调检查清单

## ✅ 文件结构统一

### 后端文件位置
```
backend/
├── models/
│   └── candidate.py          ✓ Candidate 模型
├── schemas/
│   └── candidate.py          ✓ BasicInfoSchema, BasicInfoResponseSchema
├── routers/
│   └── candidate.py          ✓ POST/GET /api/candidates/{id}/basic-info
├── main.py                   ✓ 已注册 candidate_router
└── database.py               ✓ 支持 SQLite 和 MySQL
```

### 前端文件位置
```
frontend/src/
├── api/
│   └── candidate.ts          ✓ saveBasicInfo, getBasicInfo API
└── views/assessment/
    ├── BasicInfo.vue         ✓ 基本信息表单组件
    └── AssessmentView.vue    ✓ 评估主容器（传递 candidateId）
```

---

## ✅ 数据流链路

### 1. 前端发起请求
```typescript
// frontend/src/views/assessment/BasicInfo.vue
const candidateId = computed(() => {
  return props.candidateId || props.candidate?.id || `temp-${Date.now()}`
})

await saveBasicInfo(candidateId.value, { ...form })
// ↓
// POST /api/candidates/{candidateId}/basic-info
// {
//   "name": "演示用户",
//   "age": 28,
//   "education": "本科",
//   "major": "计算机科学",
//   "desired_job": "前端工程师",
//   "experience_years": 3,
//   "skills": ["JavaScript", "Vue"]
// }
```

### 2. 后端验证请求
```python
# backend/routers/candidate.py
@router.post("/{candidate_id}/basic-info", response_model=BasicInfoResponseSchema)
async def save_basic_info(
    candidate_id: str,
    data: BasicInfoSchema,  # ← 验证数据
    db: Session = Depends(get_db)
):
```

### 3. 数据库操作
```python
# backend/models/candidate.py
class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)
    # ... 其他字段 ...
```

### 4. 返回响应
```python
# response_model=BasicInfoResponseSchema
# {
#   "id": "demo-001",
#   "name": "演示用户",
#   "age": 28,
#   ...
# }
```

---

## ✅ 关键配置检查

### 后端导入路径
- ✓ models 导入：`from models.candidate import Candidate`
- ✓ schemas 导入：`from schemas.candidate import BasicInfoSchema`
- ✓ database 导入：`from database import get_db, Base, engine`
- ✓ main.py 注册：`app.include_router(candidate_router)`

### 前端 Props 传递链
```
AssessmentView.vue
  ↓ :candidate-id="candidateId"
  ↓ :candidate="candidate"
BasicInfo.vue
  ↓ props.candidateId 和 props.candidate
  ↓ computed(candidateId)
  ↓ onSave() 调用 saveBasicInfo(candidateId.value, form)
```

### API 端点一致性
- ✓ 前端：`POST /api/candidates/{candidateId}/basic-info`
- ✓ 后端：`@router.post("/{candidate_id}/basic-info")`
- ✓ 前端：`GET /api/candidates/{candidateId}/basic-info`
- ✓ 后端：`@router.get("/{candidate_id}/basic-info")`

---

## ✅ 测试验证结果

### 后端集成测试 (`test_integration.py`)
```
[✓] 前端请求数据验证通过
[✓] 数据库表创建成功
[✓] 数据保存成功（INSERT）
[✓] 数据读取成功（SELECT）
[✓] 响应数据格式验证通过
```

### 示例数据库操作
```sql
INSERT INTO candidates (id, name, age, education, major, desired_job, experience_years, skills, created_at, updated_at)
VALUES ('demo-001', '演示用户', 28, '本科', '计算机科学', '前端工程师', 3.0, '["JavaScript", "Vue"]', ..., ...)
```

---

## 🔧 如何启动应用

### 1. 后端启动
```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 前端启动
```bash
cd frontend
npm run dev
```

### 3. 测试流程
1. 访问 http://localhost:5173
2. 进入评估流程
3. 在 BasicInfo 表单填写数据并点击"保存并下一步"
4. 应该看到成功提示，数据保存到 SQLite 数据库

---

## ⚠️ 常见问题排查

### 超时错误 (timeout of 15000ms)
原因：后端未启动或导入路径错误
解决：
- ✓ 已修复导入路径：`routers/candidate.py` 改为根目录下
- ✓ 已修复 `app/` 中的重复文件
- ✓ 确保 main.py 已注册 `candidate_router`

### 模块找不到 (ModuleNotFoundError)
原因：导入路径不对
解决：
- ✓ 所有文件都在根目录的 `routers/` 和 `schemas/` 下
- ✓ 导入统一使用相对路径：`from models.xxx`

### 数据库连接错误
原因：MySQL 连接失败或驱动缺失
解决：
- ✓ 自动降级到 SQLite（`database.py` 已改进）
- ✓ 支持 `.env` 配置或默认 SQLite

---

## 📝 总结

✅ **前端**：BasicInfo.vue 正确接收 candidateId，调用 saveBasicInfo API
✅ **后端**：routers/candidate.py 处理请求，验证数据，操作数据库
✅ **数据库**：SQLite 已配置，表结构完整
✅ **测试**：集成测试通过，数据流完整

**可以开始真实测试了！**
