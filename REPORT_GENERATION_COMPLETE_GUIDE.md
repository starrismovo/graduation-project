# 🎓 报告生成功能完整实现指南

## 目标
完成面试流程后，生成包含5维人格画像的候选人评估报告，包括：
- 五大人格维度评分（外向性、宜人性、尽责性、神经质、开放性）
- 岗位匹配度分析
- 强弱项评估
- 改进建议

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Assessment Flow (5步)                    │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│ Step 1: BasicInfo        → candidate info                    │
│ Step 2: SituationalQA    → scenario scores (5 traits)        │
│ Step 3: ImmersiveRoleDialogue → immersive scores            │
│ Step 4: CognitiveTask    → cognitive metrics                │
│ Step 5: PersonalityScale → personality scores               │
│ Step 6: ReportGenerate   → FINAL REPORT                     │
│                                                                │
│ allScores = {...latestScores, ...immersiveScores,           │
│             ...personalityScores}                            │
│             (合并所有来源的评分)                             │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 数据收集规范

### 各步骤的数据输出

| 步骤 | 组件 | 输出 | 数据结构 |
|------|------|------|---------|
| 1 | BasicInfo | 候选人信息 | `{name, age, education, desired_job, ...}` |
| 2 | SituationalQA | HR评分 | `{责任心: 8.5, 沟通能力: 7.8, ...}` |
| 3 | ImmersiveRoleDialogue | 多角色评分 | `{领导力: 8, 团队合作: 7.5, ...}` |
| 4 | CognitiveTask | 认知指标 | `{记忆: 85%, 反应时: 220ms, ...}` |
| 5 | PersonalityScale | 特质评分 | `{外向性: 7, 宜人性: 6.5, ...}` |

### allScores 的最终形态

```typescript
allScores = {
  // 来自 SituationalQA
  "责任心": 8.5,
  "沟通能力": 7.8,
  
  // 来自 ImmersiveRoleDialogue
  "领导力": 8,
  "团队合作": 7.5,
  
  // 来自 PersonalityScale（核心的5维）
  "外向性": 7,
  "宜人性": 6.5,
  "尽责性": 8,
  "神经质": 4,
  "开放性": 7.5
}
```

---

## 🎯 五大人格维度映射

系统需要将各个评分源的数据映射到标准的五大人格维度：

```typescript
const BIG_FIVE_MAPPING = {
  "外向性": ["沟通能力", "领导力", "团队合作"],
  "宜人性": ["合作意识", "同理心", "谦虚度"],
  "尽责性": ["责任心", "执行力", "自律性"],
  "神经质": ["压力管理", "情绪稳定", "抗挫能力"],
  "开放性": ["创新思维", "学习能力", "独立思考"]
}
```

**计算方法**：对每个维度下的多个指标取加权平均

---

## 💾 后端实现

### 1. 新增 API 端点（assessment.py）

```python
@router.post("/save-result", response_model=StandardResponse)
async def save_assessment_result(
    request: SaveAssessmentResultRequest,
    db: Session = Depends(get_db)
):
    """
    保存评估结果并生成报告
    
    请求体:
    {
      candidate_id: str,
      job_id: int,
      assessment_mode: "immersive" | "standard",
      all_scores: {维度: 分数},
      situational_scores: {...},
      personality_scores: {...},
      candidate_info: {...}
    }
    """
    try:
        # 1. 创建评估记录
        record = AssessmentRecord(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            assessment_mode=request.assessment_mode,
            assessment_status=AssessmentStatus.COMPLETED
        )
        db.add(record)
        db.flush()
        
        # 2. 计算并保存五大人格评分
        personality_profile = CandidatePersonalityProfile(
            candidate_id=request.candidate_id,
            trait_extroversion=request.personality_scores.get("外向性", 0),
            trait_agreeableness=request.personality_scores.get("宜人性", 0),
            trait_conscientiousness=request.personality_scores.get("尽责性", 0),
            trait_neuroticism=request.personality_scores.get("神经质", 0),
            trait_openness=request.personality_scores.get("开放性", 0),
            latest_assessment_id=record.id
        )
        db.add(personality_profile)
        
        # 3. 计算岗位匹配度
        job = db.query(Job).filter_by(id=request.job_id).first()
        if job:
            match_score = calculate_job_match_score(personality_profile, job)
            record.match_score = match_score
        
        # 4. 保存特质描述
        for trait_name, score in request.personality_scores.items():
            trait_desc = PersonalityTraitDescription(
                assessment_record_id=record.id,
                trait_name=trait_name,
                score=score,
                description=get_trait_description(trait_name)
            )
            db.add(trait_desc)
        
        # 5. 生成分析（调用 LLM）
        analysis = generate_assessment_analysis(
            personality_profile,
            request.all_scores,
            job
        )
        
        match_analysis = AssessmentMatchAnalysis(
            assessment_record_id=record.id,
            strengths=analysis.strengths,
            gaps=analysis.gaps,
            recommendations=analysis.recommendations
        )
        db.add(match_analysis)
        
        db.commit()
        
        return StandardResponse(
            code=200,
            message="评估结果已保存",
            data={"record_id": record.id}
        )
    except Exception as e:
        db.rollback()
        logger.error(f"保存评估结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎨 前端实现

### 1. 改进 ReportGenerate 组件

```typescript
// ReportGenerate.vue - Script部分
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps<{
  candidate?: Record<string, any>
  personalityScores?: Record<string, number>
  allScores?: Record<string, number>
  jobId?: number
  assessmentMode?: string
}>()

const emit = defineEmits<{
  (e: 'finish'): void
}>()

// 状态
const loading = ref(false)
const reportData = ref<any>(null)
const matchScore = ref(0)
const strengths = ref<string[]>([])
const gaps = ref<string[]>([])
const recommendations = ref<string[]>([])

// 五维数据（标准化）
const bigFiveScores = computed(() => ({
  extraversion: props.personalityScores?.['外向性'] ?? 
                 props.personalityScores?.['外向'] ?? 0,
  agreeableness: props.personalityScores?.['宜人性'] ?? 
                 props.personalityScores?.['宜人'] ?? 0,
  conscientiousness: props.personalityScores?.['尽责性'] ?? 
                     props.personalityScores?.['责任心'] ?? 0,
  neuroticism: props.personalityScores?.['神经质'] ?? 
               props.personalityScores?.['情绪'] ?? 0,
  openness: props.personalityScores?.['开放性'] ?? 
            props.personalityScores?.['开放'] ?? 0
}))

// 计算报告时间
const reportTime = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('zh-CN') + ' ' + 
         d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

// 初始化报告
onMounted(async () => {
  await generateReport()
})

// 生成报告
async function generateReport() {
  try {
    loading.value = true
    
    // 调用后端保存评估结果
    const response = await axios.post('/assessment/save-result', {
      candidate_id: props.candidate?.id,
      job_id: props.jobId,
      assessment_mode: props.assessmentMode || 'immersive',
      all_scores: props.allScores || {},
      personality_scores: bigFiveScores.value,
      situational_scores: props.personalityScores || {},
      candidate_info: props.candidate
    })
    
    if (response.data.code === 200) {
      const recordId = response.data.data.record_id
      
      // 获取生成的报告
      const reportResponse = await axios.get(`/assessment/report/${recordId}`)
      
      if (reportResponse.data.code === 200) {
        const report = reportResponse.data.data
        reportData.value = report
        matchScore.value = report.match_score || 75
        strengths.value = report.match_analysis?.strengths || []
        gaps.value = report.match_analysis?.gaps || []
        recommendations.value = report.recommendations || []
      }
    }
  } catch (err: any) {
    console.error('生成报告失败:', err)
    ElMessage.error('报告生成失败：' + (err.response?.data?.message || err.message))
  } finally {
    loading.value = false
  }
}

// 下载 PDF
async function downloadPDF() {
  ElMessage.info('PDF 导出功能开发中...')
}

// 完成评估
function finishAssessment() {
  ElMessage.success('评估已完成，感谢参与！')
  emit('finish')
}
</script>
```

### 2. 改进 AssessmentView 的报告传值

```typescript
// AssessmentView.vue
<ReportGenerate
  v-else-if="activeStep === stepCount"
  :candidate="candidate"
  :personality-scores="personalityScores"
  :all-scores="allScores"
  :job-id="selectedJobId"
  :assessment-mode="showImmersiveMode ? 'immersive' : 'standard'"
  @finish="handleReportFinish"
/>

// 处理报告完成
function handleReportFinish() {
  router.push('/home')  // 返回首页或报告列表
}
```

---

## 🔄 完整数据流

```
1️⃣ BasicInfo (Step 1)
   → 保存: candidate.value = {...user info...}

2️⃣ SituationalQA (Step 2)
   → 保存: latestScores.value = {...situational scores...}

3️⃣ ImmersiveRoleDialogue (Step 3)
   → completionEvent emits scores
   → handleImmersiveScores() 更新 immersiveScores.value

4️⃣ CognitiveTask (Step 4)
   → 认知指标收集（可选）

5️⃣ PersonalityScale (Step 5)
   → 保存: personalityScores.value = {...big five...}
   → 计算: allScores = {...latestScores, ...immersiveScores, ...personalityScores}

6️⃣ ReportGenerate (Step 6)
   ├─ 接收 allScores, personalityScores
   ├─ 调用 POST /assessment/save-result
   ├─ 后端生成报告并保存
   ├─ 调用 GET /assessment/report/{recordId}
   └─ 显示完整报告
```

---

## ✅ 实现清单

### 前端任务
- [ ] 改进 ReportGenerate.vue 显示真实数据
- [ ] 实现五维数据标准化 (bigFiveScores computed)
- [ ] 添加后端 API 调用逻辑
- [ ] 实现数据保存和报告获取
- [ ] 处理加载和错误状态
- [ ] 改进样式和UI展示

### 后端任务
- [ ] 创建 SaveAssessmentResultRequest schema
- [ ] 实现 POST /assessment/save-result 端点
- [ ] 实现 calculate_job_match_score 函数
- [ ] 实现 generate_assessment_analysis 函数（基于规则或LLM）
- [ ] 完善 GET /assessment/report/{recordId} 端点

### 数据模型任务
- [ ] 确保 PersonalityTraitDescription 表结构完整
- [ ] 确保 AssessmentMatchAnalysis 表结构完整
- [ ] 确保与已有的 AssessmentRecord 兼容

---

## 🧪 测试用例

### 完整流程测试

```
1. 登录: candidate1 / 123456
2. 进入评估: /assessment
3. 填写基本信息 → 下一步
4. 完成情境问答 → 收集评分
5. 完成多角色对话 → 收集评分
6. 跳过认知任务 → 下一步
7. 完成特质量表 → 收集五维评分
8. 生成报告
   ✅ 应该看到五维评分进度条
   ✅ 应该看到岗位匹配度 (70-85%)
   ✅ 应该看到强项和改进空间
   ✅ 应该看到具体建议
9. 点击"完成评估"返回首页
```

### 单元测试

```python
# 后端测试
def test_save_assessment_result():
    payload = {
        "candidate_id": "user_2",
        "job_id": 1,
        "assessment_mode": "immersive",
        "personality_scores": {
            "外向性": 7,
            "宜人性": 6.5,
            "尽责性": 8,
            "神经质": 4,
            "开放性": 7.5
        }
    }
    response = client.post("/assessment/save-result", json=payload)
    assert response.status_code == 200
    assert "record_id" in response.json()["data"]
```

---

## 🎯 性能优化

1. **缓存报告**: 30分钟内相同 record_id 的查询返回缓存
2. **异步生成**: 报告生成可异步处理，立即返回 record_id，后续poll获取
3. **批量操作**: 评分保存使用批量插入

---

## 📝 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 评分数据不完整 | 使用默认值 0，显示警告 |
| 岗位不存在 | 返回通用匹配度 50 |
| LLM 分析失败 | 使用模板建议 |
| 数据库连接失败 | 重试 3 次，然后返回 500 错误 |

---

## 📚 相关文件

- [ReportGenerate.vue](frontend/src/views/assessment/components/ReportGenerate.vue)
- [AssessmentView.vue](frontend/src/views/AssessmentView.vue)
- [assessment.py](backend/routers/assessment.py)
- [Assessment Model](backend/models/assessment.py)
