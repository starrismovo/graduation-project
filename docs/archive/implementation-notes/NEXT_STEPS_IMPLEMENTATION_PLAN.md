# 🛠️ 下一步实施计划 - 详细技术方案

**计划周期**: 本周 + 下周  
**目标状态**: 系统可部署上线  
**风险等级**: 低（所有核心功能已实现）

---

## 📋 优先级 1：立即启动（本周内）

### Task 1.1: 简历上传 UI 完善 🔴

**当前状态**: 
- ✅ 后端 API 完全就绪（`POST /candidates/upload_resume`）
- ❌ 前端 UI 组件需完善（80% 完成）

**执行步骤**:

#### 步骤 1: 分析现有代码
```bash
# 查看现有上传组件
cat frontend/src/components/UploadInfoDialog.vue
```

**期望内容**:
- 文件选择器（accept=".pdf,.doc,.docx,.txt")
- 拖拽上传区域
- 上传进度条
- 错误提示

#### 步骤 2: 完创建增强版本（预计 4 小时）

```typescript
// frontend/src/components/ResearchResumeUpload.vue
<template>
  <div class="upload-container">
    <!-- 1. 拖拽区域 -->
    <div 
      class="drag-drop-zone"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"  
      @drop.prevent="handleFileDrop"
      :class="{ active: isDragging }"
    >
      <p>拖拽简历到此，或点击选择</p>
      <input 
        type="file"
        @change="handleFileSelect"
        accept=".pdf,.doc,.docx,.txt,.jpg,.png"
        hidden
        ref="fileInput"
      />
    </div>

    <!-- 2. 上传进度 -->
    <div v-if="uploading" class="progress">
      <el-progress :percentage="uploadProgress" />
      <p>{{ uploadProgress }}%</p>
    </div>

    <!-- 3. 解析结果展示 -->
    <div v-if="parseResult" class="parse-result">
      <el-form :model="parseResult" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="parseResult.name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="parseResult.email" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="parseResult.phone" />
        </el-form-item>
        <el-form-item label="技能">
          <el-tag-input v-model="parseResult.skills" />
        </el-form-item>
        <el-form-item label="工作经验">
          <el-input v-model="parseResult.experience_years" type="number" />
        </el-form-item>
      </el-form>
    </div>

    <!-- 4. 状态提示 -->
    <el-alert 
      v-if="uploadError"
      :title="uploadError"
      type="error"
      closable
    />
    <el-alert 
      v-if="uploadSuccess"
      title="简历上传成功"
      type="success"
      closable
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { uploadResume } from '@/api/candidate'

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadError = ref('')
const uploadSuccess = ref(false)
const isDragging = ref(false)
const parseResult = ref(null)

const handleFileDrop = async (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (files) {
    await uploadFile(files[0])
  }
}

const handleFileSelect = async (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files) {
    await uploadFile(files[0])
  }
}

const uploadFile = async (file: File) => {
  // 验证
  if (!['application/pdf', 'application/msword'].includes(file.type)) {
    uploadError.value = '仅支持 PDF、DOC、DOCX 格式'
    return
  }

  if (file.size > 10 * 1024 * 1024) { // 10MB
    uploadError.value = '文件大小不能超过 10MB'
    return
  }

  // 上传
  uploading.value = true
  uploadProgress.value = 0
  uploadError.value = ''
  uploadSuccess.value = false

  do {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await uploadResume(formData)
      parseResult.value = response.data
      uploadSuccess.value = true
    } catch (error) {
      uploadError.value = '上传失败，请重试'
    } finally {
      uploading.value = false
    }
  } while (false)
}
</script>

<style scoped>
.upload-container {
  padding: 20px;
}

.drag-drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.drag-drop-zone.active {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.parse-result {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.progress {
  margin-top: 20px;
  text-align: center;
}
</style>
```

#### 步骤 3: 集成到评估流程（预计 2 小时）
```typescript
// frontend/src/views/assessment/BasicInfo.vue

// 在第一步"基本信息"中添加简历上传功能
<template>
  <div class="basic-info-step">
    <!-- 现有: 手工填写表单 -->
    <el-form :model="formData">
      <!-- 已有字段 -->
    </el-form>

    <!-- 新增: 简历上传 -->
    <div class="resume-upload-section">
      <h3>或上传简历自动填充</h3>
      <ResearchResumeUpload @success="handleResumeUpload" />
    </div>
  </div>
</template>

<script setup lang="ts">
const handleResumeUpload = (parseResult: any) => {
  // 将解析结果填充到表单
  formData.value = {
    ...formData.value,
    ...parseResult,
    resume_url: parseResult.resume_url
  }
  console.log('简历数据已填充', formData.value)
}
</script>
```

#### 步骤 4: 测试（预计 1 小时）
```bash
# 测试场景 1: 上传有效 PDF
# 预期: 显示进度，自动识别字段

# 测试场景 2: 上传无效格式
# 预期: 错误提示"仅支持 PDF、DOC、DOCX 格式"

# 测试场景 3: 文件过大（>10MB）
# 预期: 错误提示"文件大小不能超过 10MB"

# 测试场景 4: 网络异常
# 预期: 显示重试按钮，数据保留

# 测试场景 5: 多次上传
# 预期: 新解析结果覆盖旧数据
```

**完成标志**:
- ✅ 可上传文件并显示进度
- ✅ 自动识别的数据可编辑
- ✅ 解析失败有错误提示
- ✅ 集成到评估流程中

**验证 API**:
```bash
# 确认后端 API 正确返回
curl -X POST http://localhost:8000/api/candidates/upload_resume \
  -F "file=@resume.pdf"

# 期望返回:
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "education": "本科",
  "major": "计算机科学",
  "skills": ["Python", "Java", "SQL"],
  "experience_years": 3,
  "resume_url": "/uploads/resume_xxxxx.pdf"
}
```

---

### Task 1.2: Mock 数据替换 - LLM 集成 🔴

**当前问题**:
```python
# backend/services/immersive_dialogue.py 第 ~180 行
def generate_next_question(assessment_id: str, context: dict):
    # ❌ 当前: 返回硬编码对话
    return {
        "question": "请介绍一下你自己",  # 硬编码
        "role": "interviewer"
    }
```

**解决方案**:

#### 步骤 1: 配置 LLM 环境变量（预计 0.5 小时）

```bash
# 编辑 backend/.env

# 选项 A: OpenAI (推荐)
OPENAI_API_KEY=sk-xxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# 选项 B: Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-xxx
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-haiku

# 选项 C: 本地模型 (如无 API Key 使用)
LLM_PROVIDER=local
LOCAL_MODEL_PATH=/path/to/model
```

#### 步骤 2: 实现 LLM 包装函数（预计 3 小时）

```python
# backend/services/llm_client.py (新建)

import os
import json
from abc import ABC, abstractmethod
from typing import Optional

class LLMClient(ABC):
    """LLM 客户端基类"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIClient(LLMClient):
    """OpenAI API 实现"""
    
    def __init__(self):
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        import openai
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一名专业的人力资源面试官"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content

class AnthropicClient(LLMClient):
    """Claude/Anthropic 实现"""
    
    def __init__(self):
        import anthropic
        self.client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    
    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system="你是一名专业的人力资源面试官",
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

class LocalClient(LLMClient):
    """本地模型实现 (如果有 GPU)"""
    
    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        model_path = os.getenv("LOCAL_MODEL_PATH")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
    
    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=max_tokens)
        return self.tokenizer.decode(outputs[0])

# Factory
def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    elif provider == "local":
        return LocalClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

#### 步骤 3: 修改 ImmersiveDialogue 服务（预计 2 小时）

```python
# backend/services/immersive_dialogue.py (修改)

from services.llm_client import get_llm_client

class ImmersiveDialogueService:
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def generate_next_question(
        self, 
        assessment_id: str, 
        conversation_history: list,
        context: dict
    ) -> dict:
        """生成下一个面试问题 - 使用真实 LLM"""
        
        # 构建 prompt
        prompt = self._build_question_prompt(
            assessment_id=assessment_id,
            conversation_history=conversation_history,
            context=context
        )
        
        try:
            # 调用 LLM
            question_text = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=200
            )
            
            # 解析响应
            question_data = self._parse_question(question_text)
            
            # 记录 API 调用
            self._log_llm_usage(
                assessment_id=assessment_id,
                tokens_used=len(question_text.split()),
                cost=self._estimate_cost(question_text)
            )
            
            return {
                "question": question_data["content"],
                "role": question_data["role"],
                "timestamp": datetime.now(),
                "source": "llm"
            }
        
        except Exception as e:
            logger.error(f"LLM API 错误: {e}")
            # 降级到预设问题
            return self._get_fallback_question(context)
    
    async def analyze_answer(
        self,
        assessment_id: str,
        candidate_answer: str,
        question: str
    ) -> dict:
        """分析候选人回答 - 使用真实 LLM"""
        
        prompt = f"""
        面试问题: {question}
        候选人回答: {candidate_answer}
        
        请分析并评分 (1-10):
        1. 表达清晰度
        2. 相关性
        3. 完整性
        4. 来源: 原创/背诵
        5. 整体评价
        
        返回 JSON 格式:
        {{
            "clarity": 8,
            "relevance": 9,
            "completeness": 7,
            "is_original": true,
            "emotional_tone": "confident",
            "summary": "回答xxxx"
        }}
        """
        
        try:
            analysis_text = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=300
            )
            return json.loads(analysis_text)
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return self._get_fallback_analysis()
    
    def _build_question_prompt(self, assessment_id, conversation_history, context):
        """构建问题生成 prompt"""
        
        history_text = "\n".join([
            f"{turn['role']}: {turn['content']}"
            for turn in conversation_history[-5:]  # 最近 5 轮
        ])
        
        prompt = f"""
        你是一名资深人力资源面试官。根据以下信息生成下一个面试问题:
        
        候选人信息:
        - 职位: {context.get('target_job')}
        - 经验年限: {context.get('experience_years')}
        - 教育背景: {context.get('education')}
        
        对话历史:
        {history_text}
        
        要求:
        1. 问题应该深入挖掘候选人的：能力、经验、性格特征
        2. 考虑前面问题，设计递进式问题
        3. 避免重复已问问题
        4. 语言专业、清晰、恰当
        
        直接返回面试问题，不需要额外说明:
        """
        
        return prompt
    
    def _parse_question(self, question_text):
        """解析 LLM 返回的问题"""
        # 简单实现：直接返回
        return {
            "content": question_text.strip(),
            "role": "interviewer"
        }
```

#### 步骤 4: 安装依赖（预计 0.5 小时）

```bash
# 进入后端目录
cd backend

# 安装 OpenAI 或 Anthropic 库
pip install openai>=1.0.0  # OpenAI
# 或
pip install anthropic>=0.7.0  # Claude

# 验证安装
python -c "import openai; print(openai.__version__)"
```

#### 步骤 5: 测试 LLM 集成（预计 1 小时）

```python
# backend/tests/test_llm_integration.py (新建)

import pytest
from services.llm_client import get_llm_client

@pytest.mark.asyncio
async def test_generate_question():
    """测试问题生成"""
    service = get_llm_client()
    
    prompt = "生成一个HR面试问题关于候选人的工作经验"
    response = await service.generate(prompt)
    
    assert response is not None
    assert len(response) > 10
    print(f"生成的问题: {response}")

@pytest.mark.asyncio
async def test_analyze_answer():
    """测试回答分析"""
    from services.immersive_dialogue import ImmersiveDialogueService
    
    service = ImmersiveDialogueService()
    analysis = await service.analyze_answer(
        assessment_id="test_123",
        question="你的优缺点是什么？",
        candidate_answer="我优点是执行力强，缺点是有时太追求完美。"
    )
    
    assert analysis.get("clarity") is not None
    assert analysis.get("relevance") is not None
    print(f"分析结果: {analysis}")

# 运行测试
# pytest backend/tests/test_llm_integration.py -v
```

#### 步骤 6: 验证数据流（预计 1 小时）

```bash
# 启动后端
cd backend
python main.py

# 在浏览器测试完整流程
# 1. 登录
# 2. 开始评估
# 3. 进入 AI 对话步骤
# 4. 观察是否收到 LLM 生成的问题（而不是硬编码的）
# 5. 回答问题
# 6. 检查数据库是否正确记录 (conversation_turns 表)
```

**完成标志**:
- ✅ API 环境变量正确配置
- ✅ LLM 调用成功（无 timeout）
- ✅ 生成的问题符合质量标准
- ✅ 数据正确存储到数据库
- ✅ 错误情况有降级方案

**成本估算** (如使用 OpenAI GPT-3.5):
```
每个问题: ~0.001-0.002 USD
每次评估 (10-15 个问题): ~0.015-0.03 USD
1000 次评估: ~15-30 USD

预算建议: 设置 API 调用限额和监控
```

**故障排除**:
```python
# 如果 LLM API 超时
# 1. 增加 timeout 参数
# 2. 使用重试机制
# 3. 降级到预设问题

# 如果 API 配额用尽
# 1. 检查 API Key 有效期
# 2. 检查账户余额
# 3. 切换到 Claude/本地模型

# 如果生成质量差
# 1. 调整 prompt 提示词
# 2. 提高 temperature 参数
# 3. 增加 few-shot examples
```

---

### Task 1.3: 表单验证完善 🔴 (1 天)

**位置**: `frontend/src/views/assessment/`

```typescript
// 为每个步骤添加完整验证

// BasicInfo.vue
const validateBasicInfo = () => {
  const errors: string[] = []
  
  if (!formData.value.real_name?.trim()) {
    errors.push('姓名不能为空')
  }
  if (!formData.value.email || !isValidEmail(formData.value.email)) {
    errors.push('邮箱格式不正确')
  }
  if (!formData.value.phone || !isValidPhone(formData.value.phone)) {
    errors.push('电话格式不正确')
  }
  if (!formData.value.desired_job) {
    errors.push('期望岗位不能为空')
  }
  
  return errors.length === 0 ? true : errors
}

// 在提交前检查
const handleNext = async () => {
  const validation = validateBasicInfo()
  if (validation !== true) {
    ElMessage.error(validation.join('；'))
    return
  }
  // 继续下一步
}
```

---

## 📋 优先级 2：本周末完成

### Task 2.1: 完整流程集成测试 🟠 (2-3 天)

**测试清单**:

```bash
# 场景 1: 新用户注册 → 完整评估
1. 访问注册页面
2. 填写基本信息（或上传简历自动填充）
3. 提交注册
4. 登录
5. 进入评估流程
6. 完成 6 个评估步骤
7. 查看报告
8. 验证数据库数据完整性

# 场景 2: 简历上传数据完整性
1. 上传含有所有信息的简历
2. 验证自动提取的字段
3. 确认手工编辑后保存成功
4. 检查 User 表是否更新

# 场景 3: 多轮对话记录
1. 进入 AI 对话步骤
2. 进行 5+ 轮对话
3. 检查 conversation_turns 表
4. 验证每条记录都有: speaker, message, emotion, confidence_score

# 场景 4: 评估报告生成
1. 完成评估
2. 点击"生成报告"
3. 验证报告包含：
   - 心理画像
   - 各维度评分
   - 岗位推荐
4. 导出 PDF (后续功能)
```

**自动化测试** (可选):

```bash
# 使用 Playwright 或 Cypress
# frontend/e2e/full-flow.spec.ts

test('完整评估流程', async ({ page }) => {
  // 导航到注册
  await page.goto('http://localhost:5173/register')
  
  // 填写信息
  await page.fill('input[name="username"]', 'testuser')
  await page.fill('input[name="password"]', 'Password123!')
  await page.click('button:has-text("注册")')
  
  // 等待重定向
  await page.waitForURL('**/login')
  
  // 登录
  await page.fill('input[name="username"]', 'testuser')
  await page.fill('input[name="password"]', 'Password123!')
  await page.click('button:has-text("登录")')
  
  // 进入评估
  await page.click('button:has-text("开始评估")')
  
  // 完成 6 步评估...
  
  // 验证报告
  await expect(page.locator('.report-card')).toBeVisible()
})
```

### Task 2.2: 数据库性能优化 🟠 (1-2 天)

```sql
-- 添加关键索引
ALTER TABLE conversation_turns ADD INDEX idx_assessment_id (assessment_id);
ALTER TABLE conversation_turns ADD INDEX idx_created_at (created_at);

ALTER TABLE interview_responses ADD INDEX idx_candidate_id (candidate_id);
ALTER TABLE interview_responses ADD INDEX idx_assessment_id (assessment_id);

ALTER TABLE assessment_records ADD INDEX idx_candidate_id (candidate_id);
ALTER TABLE assessment_records ADD INDEX idx_created_at (created_at);

-- 验证索引
SHOW INDEX FROM conversation_turns;
```

### Task 2.3: 前端性能优化 🟠 (1-2 天)

```typescript
// 组件懒加载
const ReportGenerate = defineAsyncComponent(() =>
  import('./ReportGenerate.vue')
)

// 虚拟滚动 (评估历史)
<el-virtual-list
  :items="assessmentHistory"
  :item-size="100"
  height="600"
>
  <template #default="{ item }">
    <AssessmentHistoryItem :item="item" />
  </template>
</el-virtual-list>

// 查询去重
const cachedAssessments = new Map()
const getAssessments = async (candidateId: string) => {
  if (cachedAssessments.has(candidateId)) {
    return cachedAssessments.get(candidateId)
  }
  const data = await api.getAssessments(candidateId)
  cachedAssessments.set(candidateId, data)
  return data
}
```

---

## 📋 优先级 3: 下周完成

### Task 3.1: 部署准备 🟡 (1-2 天)

```bash
# 1. 环境配置
cp backend/.env.example backend/.env.production
# 编辑 .env.production，设置生产环境变量

# 2. 数据库初始化
python backend/scripts/init_db.py --env=production

# 3. 编译前端
cd frontend
npm run build
# 输出: dist/

# 4. Docker 部署 (可选)
docker-compose -f docker-compose.prod.yml up -d
```

### Task 3.2: 安全加固 🟡 (1 天)

```python
# backend/middleware/security.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import re

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 1. 输入验证
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            # SQL injection check
            if self._has_sql_injection(body.decode()):
                raise HTTPException(status_code=400, detail="Invalid input")
        
        # 2. 上传文件检查
        if "upload" in request.url.path:
            # 验证文件类型
            # 检查文件大小
            # 扫描病毒 (可选)
            pass
        
        # 3. 速率限制
        # 限制 API 调用频率
        
        response = await call_next(request)
        
        # 4. 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
    
    @staticmethod
    def _has_sql_injection(text: str) -> bool:
        """检查 SQL 注入"""
        patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b.*=.*)",
            r"(;.*\bdrop\b)",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

# main.py 中注册
app.add_middleware(SecurityMiddleware)
```

---

## ⏰ 工作日程表

```
本周 (第 1-5 天):
  周一-周二: Task 1.1 (简历上传 UI)
  周二-周三: Task 1.2 (LLM 集成)
  周四: Task 1.3 (表单验证)
  周五上午: Task 2.1 (集成测试)

周末:
  周五下午-周日: Task 2.2/2.3 (性能优化)

下周:
  周一-周二: Task 3.1 (部署准备)
  周三: Task 3.2 (安全加固)
  周四-周五: 最终测试 & 上线
```

---

## ✅ 验收条件

**本周检查清单**:
- [ ] 简历上传功能可完全使用
- [ ] LLM API 正确集成，无 Mock 数据
- [ ] 完整评估流程可跑通
- [ ] 数据完整性验证通过
- [ ] 性能基准测试完成

**部署检查清单**:
- [ ] 生产环境配置完成
- [ ] 数据备份管理就位
- [ ] 监控告警配置完成
- [ ] API 文档最新
- [ ] 用户文档完备

---

## 📞 支持联系

**后端问题**: 查看 `/backend/QUICK_START_BACKEND.md`  
**前端问题**: 查看 `/frontend/README.md`  
**数据库问题**: 查看数据库初始化脚本 `/backend/scripts/`

---

*最后更新: 2026-03-28*  
*计划有效期: 至完成或重新评估*
