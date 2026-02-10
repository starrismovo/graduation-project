<template>
  <el-card class="page-card">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>AI 智能评估配置</h2>
      <p class="sub">
        通过参数化配置，控制 AI 在多轮对话中的评估重点与追问策略
      </p>
    </div>

    <!-- 1. 岗位评估目标 -->
    <el-divider>岗位评估目标</el-divider>
    <el-form label-width="140px">
      <el-form-item
        v-for="item in config.dimensions"
        :key="item.key"
        :label="item.label"
      >
        <el-slider
          v-model="item.weight"
          :min="0"
          :max="100"
          show-input
        />
      </el-form-item>
    </el-form>

    <!-- 2. AI 对话风格 -->
    <el-divider>AI 对话风格</el-divider>
    <el-form label-width="140px">
      <el-form-item label="整体风格">
        <el-radio-group v-model="config.style">
          <el-radio label="professional">理性 · 专业</el-radio>
          <el-radio label="gentle">温和 · 引导式</el-radio>
          <el-radio label="challenging">高压 · 挑战式</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="追问强度">
        <el-select v-model="config.followUpLevel">
          <el-option label="低" value="low" />
          <el-option label="中" value="medium" />
          <el-option label="高" value="high" />
        </el-select>
      </el-form-item>

      <el-form-item label="允许质疑回答">
        <el-switch v-model="config.allowChallenge" />
      </el-form-item>
    </el-form>

    <!-- 3. 问题类型 -->
    <el-divider>问题类型配置</el-divider>
    <el-checkbox-group v-model="config.questionTypes">
      <el-checkbox label="behavior">行为回溯类</el-checkbox>
      <el-checkbox label="scenario">情境假设类</el-checkbox>
      <el-checkbox label="decision">决策分析类</el-checkbox>
    </el-checkbox-group>

    <!-- 4. 追问与反作弊 -->
    <el-divider>追问逻辑与真实性判断</el-divider>
    <el-form label-width="140px">
      <el-form-item label="最少追问次数">
        <el-input-number v-model="config.minFollowUps" :min="0" :max="10" />
      </el-form-item>

      <el-form-item label="反作弊策略">
        <el-checkbox-group v-model="config.antiCheat">
          <el-checkbox label="template">模板化回答检测</el-checkbox>
          <el-checkbox label="cross">交叉验证提问</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </el-form>

    <!-- 5. 风险偏好 -->
    <el-divider>风险偏好设置</el-divider>
    <el-form label-width="180px">
      <el-form-item label="真实性 vs 表达能力">
        <el-slider
          v-model="config.truthPriority"
          :min="0"
          :max="100"
          show-input
        />
      </el-form-item>

      <el-form-item label="可疑回答处理方式">
        <el-select v-model="config.riskStrategy">
          <el-option label="仅记录风险" value="record" />
          <el-option label="降低评分权重" value="penalize" />
          <el-option label="终止评估" value="terminate" />
        </el-select>
      </el-form-item>
    </el-form>

    <!-- 底部操作 -->
    <div class="actions">
      <el-button>预览 AI 提问示例</el-button>
      <el-button type="primary" @click="onSave">
        保存并启用
      </el-button>
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const config = reactive({
  dimensions: [
    { key: 'skill', label: '专业能力', weight: 40 },
    { key: 'communication', label: '沟通能力', weight: 30 },
    { key: 'pressure', label: '抗压能力', weight: 30 }
  ],

  style: 'professional',
  followUpLevel: 'medium',
  allowChallenge: true,

  questionTypes: ['behavior', 'scenario'],
  minFollowUps: 2,
  antiCheat: ['template'],

  truthPriority: 70,
  riskStrategy: 'record'
})

function onSave() {
  console.log('评估配置：', config)

  // 👉 这里未来可以做两件事：
  // 1. 发送给后端保存
  // 2. 转换成 Prompt 传给 LLM

  ElMessage.success('评估配置已保存并启用')
}
</script>
<style scoped>
.page-card {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}

.sub {
  font-size: 13px;
  color: #666;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
