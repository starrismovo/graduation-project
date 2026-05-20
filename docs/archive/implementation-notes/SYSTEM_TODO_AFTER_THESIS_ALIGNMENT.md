# 系统与论文一致性待改清单

本文档用于记录本次论文自动校对后发现的系统实现差距。清单按优先级排列，便于后续逐项修正。

## 一、必须优先修正

### 1. 独立实现 Role Template（岗位模板）模型

当前情况：
- 代码中已有 `Job`、`JobRequirementTag`、`JobSkillRequirement`、`JobPersonalityFramework` 等结构。
- 这些结构能够表达岗位实例和岗位需求，但尚未形成独立的 `RoleTemplate` 数据模型。

影响：
- 与 AGENTS.md 中“Keep Role Template and Job Instance as separate concepts and models”的架构规则不完全一致。
- 论文第三章、第四章中的岗位双层建模在数据库层尚未完全落地。

建议改动：
- 新增 `backend/models/role_template.py`。
- 新增 `RoleTemplate` 表，字段包括模板名称、岗位类别、通用技能、人格需求、工作环境特征、职责描述等。
- 在 `Job` 中新增 `role_template_id` 外键。
- 前端岗位管理页增加“从岗位模板创建岗位实例”的入口。

### 2. 统一 AssessmentSession 术语映射

当前情况：
- 论文术语使用 `AssessmentSession / 评估会话`。
- 代码实体使用 `AssessmentRecord`。

影响：
- 论文与代码命名存在解释成本。

建议改动：
- 短期：在论文中继续说明 `AssessmentRecord` 是 AssessmentSession 的工程实现名。
- 中期：可考虑新增别名层、schema 注释或文档注释，明确 `AssessmentRecord == AssessmentSession`。

### 3. 强化 EvaluationResult 与报告证据链

当前情况：
- `EvaluationResult` 已实现，能够保存能力评分、人格对比、Agent评分、优势、不足和建议。
- 但报告解释仍偏模板化，缺少“某条回答 -> 某个维度 -> 匹配分数”的细粒度证据链。

建议改动：
- 在 `EvaluationResult.report_content` 中增加 evidence 数组。
- 每条 evidence 记录 `conversation_turn_id`、trait、score_delta、reasoning、confidence。
- 报告页展示“证据解释”区域。

## 二、建议完善

### 4. 场景人格长期画像

当前情况：
- `calculate_scenario_traits()` 已支持规则化场景人格计算。
- 场景人格主要写入单次 `EvaluationResult.trait_comparison`，尚未形成可跨岗位对比的历史结构。

建议改动：
- 新增 `ScenarioPersonalitySnapshot` 表。
- 字段包含 `assessment_record_id`、`job_id`、`basic_traits`、`scenario_traits`、`adjustments`、`job_requirements`。
- 支持候选人在不同 Job Instance 下的 Scenario Personality 对比。

### 5. 前端报告页补齐 explainability 结构

当前情况：
- 报告页已有评分、人格、匹配分析和建议。
- 证据解释和匹配分解还可以更明确。

建议改动：
- 增加 score overview、personality radar、match breakdown、evidence explanation、recommendations 五块结构。
- 与 AGENTS.md 中报告页面可解释性要求保持一致。

### 6. 权重配置可视化与可维护化

当前情况：
- 多Agent融合权重集中在 `agent_scoring_fusion.py`。
- 前端和HR端尚未提供权重查看或管理入口。

建议改动：
- 在HR岗位管理中显示当前岗位类别对应的Agent权重。
- 后端增加权重配置读取接口。
- 后续可将权重迁移到数据库配置表。

## 三、论文实验后续可补充

### 7. 补充真实样本验证

当前情况：
- 第六章已调整为工程验证，不再虚构大规模专家实验。

建议改动：
- 若后续有真实数据，可增加小规模候选人样本。
- 保留样本来源、评估流程和专家标注说明。
- 不写无法证明的长期预测能力或长期绩效结论。

### 8. 标准化人格量表融合

当前情况：
- 当前人格评分主要来自面试能力维度和行为线索映射。

建议改动：
- 可新增简短大五人格问卷模块。
- 报告中区分“标准量表结果”和“面试行为推断结果”。
- 避免将面试推断直接表述为严格心理测量结论。

## 四、已在论文中修正的内容

- 第一章已修正：章节结构说明与第六章标题、验证口径保持一致，避免写成未实施的大规模实验。
- 第二章已修正：多Agent任务分解与当前代码中的 `interviewer_agent`、`evaluator_agent`、`decision_agent` 对齐。
- 第三章已修正：用户角色、功能模块、图号、评估流程和 Role Template 当前实现状态已统一说明。
- 第四章已修正：Agent 角色、岗位双层建模实现状态、图号占位和公式异常字符已修正。
- 第五章已修正：`EvaluationResult` 已实现，不再写成仅由 `AssessmentMatchAnalysis` 替代。
- 第五章已修正：Scenario Personality 已具备后端规则化计算，不再写成完全未实现。
- 第五章已修正：多Agent权重不是固定 1/3，而是由岗位类别动态配置。
- 第五章已修正：前端关键组件名称改为当前代码中真实存在的页面和组件。
- 第六章已重写：从计划式专家实验改为工程验证与结果分析。
- 第七章已修正：总结中明确 Role Template 仍需独立建模，避免夸大当前实现。
