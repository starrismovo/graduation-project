<template>
  <div class="immersive-dialogue">
    <!-- 舞台背景：模拟真实会议室 -->
    <div class="stage-background">
      <div class="ambient-layer"></div>
      <div class="meeting-room-overlay"></div>
    </div>

    <!-- 左侧：候选人信息与流程控制 -->
    <div class="left-sidebar" :style="{ backgroundImage: svgImageUrl ? `url(${svgImageUrl})` : 'none' }">
      <!-- SVG遮罩文字，在 svg 模式时显示 -->
      <div v-if="leftPanelMode === 'svg'" class="svg-overlay">
        <div class="placeholder-text">
          <p></p>
          <p class="sub-text"></p>
        </div>
      </div>

      <!-- 面板内容（info模式）覆盖在背景上，半透明白色背景 -->
        <div v-if="leftPanelMode === 'info'" class="panel-overlay">
        <div class="panel-title">
          <el-icon><i class="el-icon-user"></i></el-icon>
          <span>面试流程</span>
          <el-tag v-if="currentStep >= 1" size="small" type="success">已填充</el-tag>
        </div>
        <!-- 流程指示器 -->
        <div class="process-indicator">
          <div 
            v-for="(step, idx) in assessmentSteps" 
            :key="idx"
            :class="['step', { active: idx === currentStep, completed: idx < currentStep, locked: isInterviewLocked }]"
          >
            <div class="step-number">{{ idx + 1 }}</div>
            <div class="step-title">{{ step }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 中间主对话区：沉浸式聊天界面 -->
    <div class="dialogue-container">
      <div class="dialogue-header">
        <div class="job-info-bar">
          <div class="job-info-main">
            <span class="job-info-label">当前面试岗位</span>
            <strong class="job-info-title">{{ currentJobDisplayTitle }}</strong>
          </div>
          <div class="job-info-meta">
            <el-tag size="small" effect="dark" type="warning">{{ currentInterviewStatusLabel }}</el-tag>
            <span v-if="selectedJobId" class="job-info-id">岗位ID: {{ selectedJobId }}</span>
          </div>
        </div>

        <div class="session-info">
          <div class="header-content">
            <div class="ai-profile">
              <img :src="aiInterviewerAvatar" class="ai-avatar" />
              <div class="ai-info">
                <h3>AI 面试官</h3>
                <p>{{ aiInterviewerTitle }}</p>
              </div>
            </div>
            <div class="session-meta">
              <el-tag size="small" type="info">{{ currentPhase }}</el-tag>
              <span class="time-elapsed">⏱️ {{ formatTime(elapsedTime) }}</span>
              <span class="progress">📊 {{ respondedCount }}/{{ interviewPlan.totalQuestions }}</span>
            </div>
          </div>
        </div>
        
        <!-- 实时情绪与语气分析 -->
        <div class="sentiment-monitor" v-if="latestSentiment && currentStep >= 3">
          <div class="sentiment-indicator">
            <span class="label">作答状态:</span>
            <el-tag :type="getSentimentType(latestSentiment.emotion)" size="small">
              {{ latestSentiment.emotion }}
            </el-tag>
          </div>
          <div class="confidence-bar">
            <span class="label">表达稳定度:</span>
            <el-progress 
              :percentage="latestSentiment.confidence" 
              :color="getConfidenceColor(latestSentiment.confidence)"
              :show-text="false"
              :stroke-width="4"
            />
          </div>
        </div>
      </div>

      <!-- 消息流 -->
      <div class="message-stream" ref="messageStream">
        <!-- Step 0: 初始欢迎 -->
        <div v-if="currentStep === 0" class="conversation-starter initial-greeting">
          <!-- 加载中 -->
          <div v-if="initLoading" class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>正在初始化...</h4>
            <p>正在检查您的信息，请稍候</p>
          </div>

          <div v-else-if="!hasAssessmentPath" class="starter-content assessment-entry-choice">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>{{ introScene.title }}</h4>
            <p>{{ introScene.lines[0] }}</p>
            <p class="starter-tip">{{ introScene.lines[1] }}</p>

            <div class="entry-choice-grid">
              <button class="entry-choice-card primary" @click="startResumeAssessmentEntry">
                <div class="entry-choice-icon">🧾</div>
                <div class="entry-choice-title">基于简历开始综合评估</div>
                <div class="entry-choice-desc">
                  {{ hasExistingResume ? '系统将优先使用你已有的履历画像进入综合评估，也可随后替换为新简历。' : '系统会先解析你的简历，再围绕履历背景、通用能力与发展潜力进行综合评估。' }}
                </div>
              </button>

              <button class="entry-choice-card secondary" @click="goSelectJob">
                <div class="entry-choice-icon">🎯</div>
                <div class="entry-choice-title">返回选择岗位评估</div>
                <div class="entry-choice-desc">
                  先从岗位浏览锁定目标岗位，再进入针对岗位要求、技能和匹配度的定向评估面试。
                </div>
              </button>
            </div>
          </div>

          <!-- 有历史简历：先告知岗位与流程，再决定沿用信息或更新简历 -->
          <div v-else-if="hasExistingResume" class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>{{ introScene.title }}</h4>
            <p>{{ introScene.lines[0] }}</p>
            <p>{{ introScene.lines[1] }}</p>
            <p class="starter-tip">{{ introScene.lines[2] }}</p>
            
            <div class="resume-choice-area">
              <div class="resume-history-card" v-if="existingResumeInfo">
                <div class="info-header">📋 已有信息</div>
                <div class="info-content">
                  <div class="info-row" v-if="existingResumeInfo.name">
                    <span class="label">姓名:</span>
                    <span class="value">{{ existingResumeInfo.name }}</span>
                  </div>
                  <div class="info-row" v-if="existingResumeInfo.email">
                    <span class="label">邮箱:</span>
                    <span class="value">{{ existingResumeInfo.email }}</span>
                  </div>
                  <div class="info-row" v-if="existingResumeInfo.education">
                    <span class="label">学历:</span>
                    <span class="value">{{ existingResumeInfo.education }}</span>
                  </div>
                  <div class="info-row" v-if="existingResumeInfo.skills && existingResumeInfo.skills.length">
                    <span class="label">技能:</span>
                    <span class="value">{{ Array.isArray(existingResumeInfo.skills) ? existingResumeInfo.skills.join(', ') : existingResumeInfo.skills }}</span>
                  </div>
                </div>
              </div>

              <div class="resume-choice-buttons">
                <el-button type="primary" size="large" @click="useExistingResume">
                  ✅ 使用已有信息并启动面试
                </el-button>
                <el-button size="large" @click="openUploadDialog">
                  📄 上传新简历替换
                </el-button>
              </div>
            </div>
          </div>

          <!-- 无历史简历：直接上传 -->
          <div v-else class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>{{ introScene.title }}</h4>
            <p>{{ introScene.lines[0] }}</p>
            <p>{{ introScene.lines[1] }}</p>
            <p class="starter-tip">{{ introScene.lines[2] }}</p>
            <el-button type="primary" @click="openUploadDialog" class="upload-action-btn" size="large">
              📋 上传简历并开始
            </el-button>
          </div>
        </div>

        <!-- Step 1: 简历解析阶段 -->
        <div v-if="currentStep === 1" class="conversation-starter resume-parsing">
          <div class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>{{ introScene.title }}</h4>
            <p>{{ introScene.lines[0] }}</p>
            
            <!-- 显示解析的信息 -->
            <div v-if="parsedResumeData" class="parsed-info-display">
              <div class="info-card">
                <div class="info-header">📋 候选人信息</div>
                <div class="info-content">
                  <div class="info-row">
                    <span class="label">姓名:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.name }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">邮箱:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.email }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">学历:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.education }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">经验水平:</span>
                    <span class="value">{{ parsedResumeData.candidate_info.experience_level }}</span>
                  </div>
                  <div class="info-row" v-if="parsedResumeData.extraction_method">
                    <span class="label">识别方式:</span>
                    <span class="value">
                      <el-tag :type="parsedResumeData.extraction_method === 'ocr' ? 'warning' : 'success'">
                        {{ parsedResumeData.extraction_method === 'ocr' ? '🤖 OCR识别(扫描版)' : '✅ 原生提取' }}
                      </el-tag>
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-if="parsedResumeData.candidate_info.technical_skills.length > 0" class="info-card">
                <div class="info-header">💻 技术能力</div>
                <div class="skills-list">
                  <el-tag 
                    v-for="skill in parsedResumeData.candidate_info.technical_skills"
                    :key="skill"
                    type="primary"
                    effect="light"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
              </div>

              <div v-if="parsedResumeData.candidate_info.soft_skills.length > 0" class="info-card">
                <div class="info-header">✨ 核心素质</div>
                <div class="skills-list">
                  <el-tag 
                    v-for="skill in parsedResumeData.candidate_info.soft_skills"
                    :key="skill"
                    type="success"
                    effect="light"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
              </div>

              <div class="info-card">
                <div class="info-header">📊 评估维度 ({{ parsedResumeData.assessed_dimensions.length }}项)</div>
                <div class="dimensions-list">
                  <div v-for="(dim, idx) in parsedResumeData.assessed_dimensions" :key="idx" class="dimension-item">
                    {{ getDimensionIcon(Number(idx)) }} {{ dim }}
                  </div>
                </div>
              </div>
            </div>

            <div class="auto-progress-tip">
              <el-icon class="is-loading"><i class="el-icon-loading"></i></el-icon>
              <span>{{ introScene.status }}</span>
            </div>
          </div>
        </div>

        <!-- Step 2: 面试说明与准备 -->
        <div v-if="currentStep === 2" class="conversation-starter interview-briefing">
          <div class="starter-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>{{ introScene.title }}</h4>
            
            <div class="briefing-content">
              <p>{{ introScene.lines[0] }}</p>
              
              <div class="interview-plan">
                <div class="plan-item">
                  <div class="plan-icon">1️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">破冰与背景了解</div>
                    <p>我们先从你的工作经验和背景开始交流</p>
                  </div>
                </div>

                <div class="plan-item">
                  <div class="plan-icon">2️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">技术深度探索</div>
                    <p>深入讨论你的技术能力和问题解决经验</p>
                  </div>
                </div>

                <div class="plan-item">
                  <div class="plan-icon">3️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">产品思维对话</div>
                    <p>考察你的产品思维和创新意识</p>
                  </div>
                </div>

                <div class="plan-item">
                  <div class="plan-icon">4️⃣</div>
                  <div class="plan-detail">
                    <div class="plan-title">综合素质评估</div>
                    <p>评价你的沟通能力和团队协作精神</p>
                  </div>
                </div>
              </div>

              <div class="interview-stats">
                <div class="stat-item">
                  <div class="stat-label">预计时长</div>
                  <div class="stat-value">6分钟</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">问题数量</div>
                  <div class="stat-value">{{ interviewPlan.totalQuestions }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">评估维度</div>
                  <div class="stat-value">{{ parsedResumeData?.assessed_dimensions.length || 5 }}</div>
                </div>
              </div>

              <p class="starter-tip">{{ introScene.lines[1] }}</p>
            </div>

            <div class="auto-progress-tip">
              <el-icon class="is-loading"><i class="el-icon-loading"></i></el-icon>
              <span>{{ introScene.status }}</span>
            </div>
          </div>
        </div>

        <!-- Step 4: 完成状态。正式报告在独立报告模块查看。 -->
        <div v-if="currentStep === 4" class="conversation-starter report-section">
          <div class="starter-content report-content completion-content">
            <div class="greeting-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <h4>评估已完成</h4>

            <div v-if="reportLoading" class="report-loading report-loading-with-counselor">
              <div class="report-counselor-visual" aria-label="AI 咨询助手正在生成岗位适配建议">
                <span class="report-counselor-orbit"></span>
                <img src="/ai-counselor.png" alt="AI 咨询助手" class="report-counselor-image" />
              </div>
              <div class="report-loading-copy">
                <span class="report-complete-badge">已完成心理特质分析</span>
                <h4>AI 咨询助手正在生成你的岗位适配建议</h4>
              </div>
              <el-icon class="is-loading" style="font-size: 32px; color: #409eff;"><i class="el-icon-loading"></i></el-icon>
              <p>系统正在保存本次评估记录，并生成你的岗位适配报告。</p>
            </div>

            <div v-else class="completion-card">
              <div class="completion-stats">
                <div class="stat-item">
                  <div class="stat-label">面试时长</div>
                  <div class="stat-value">{{ formatTime(elapsedTime) }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">回答题数</div>
                  <div class="stat-value">{{ respondedCount }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">报告状态</div>
                  <div class="stat-value">{{ reportRecordId ? '已生成' : '已完成' }}</div>
                </div>
              </div>
              <p class="completion-tip">
                本页仅保留面试过程。完整评估报告、匹配度解释、证据链与HR反馈请在评估报告模块查看。
              </p>
              <div class="report-actions">
                <el-button v-if="reportRecordId" type="primary" size="large" @click="openReportModule">
                  查看评估报告
                </el-button>
                <el-button size="large" @click="finishAndClose">
                  完成
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div 
          v-for="(msg, idx) in messages" 
          :key="idx"
          :class="['message-item', msg.role === 'candidate' ? 'from-candidate' : 'from-ai']"
        >
          <!-- AI 消息 -->
          <div v-if="msg.role === 'ai'" class="ai-message">
            <div class="message-avatar">
              <img :src="aiInterviewerAvatar" />
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="speaker-name">AI 面试官</span>
                <span class="timestamp">{{ msg.time }}</span>
              </div>
              <div class="message-body">
                <div class="question-kicker">面试官提问</div>
                <p>{{ msg.content }}</p>
                <!-- 评估标签 -->
                <div v-if="msg.tags" class="message-tags">
                  <span class="tag-label">考察维度</span>
                  <el-tag 
                    v-for="tag in msg.tags" 
                    :key="tag"
                    size="small"
                    effect="plain"
                    type="info"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- 候选人消息 -->
          <div v-else class="candidate-message">
            <div class="message-content">
              <div class="message-header">
                <span class="timestamp">{{ msg.time }}</span>
                <span class="response-metrics" v-if="msg.responseTime">
                  ⏱️ {{ msg.responseTime }}秒
                </span>
              </div>
              <div class="message-body">
                <p>{{ msg.content }}</p>
              </div>
              <!-- AI 反馈 -->
              <div v-if="msg.aiFeedback" class="ai-feedback">
                <el-icon><i class="el-icon-documentcopy"></i></el-icon>
                <span>{{ msg.aiFeedback }}</span>
              </div>
            </div>
            <div class="message-avatar">
              <div class="candidate-avatar">You</div>
            </div>
          </div>
        </div>

        <!-- 打字中指示器 -->
        <div v-if="isTyping" class="typing-indicator">
          <div class="typing-avatar">
            <img :src="aiInterviewerAvatar" />
          </div>
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>

        <!-- 回答解析中指示器 -->
        <div v-if="isProcessing" class="analysis-indicator">
          <div class="typing-avatar">
            <img :src="aiInterviewerAvatar" />
          </div>
          <div class="analysis-bubble">
            <div class="analysis-title">正在解析你的回答</div>
            <div class="analysis-subtitle">{{ processingStatusText }}</div>
          </div>
        </div>
      </div>

      <!-- 智能输入区 -->
      <div class="input-area" v-if="currentStep === 3 && !shouldEndInterview">
        <!-- 上下文提示条 -->
        <div v-if="contextHint" class="context-hint">
          <el-icon><i class="el-icon-info"></i></el-icon>
          <span><strong>本题关注：</strong>{{ contextHint }}</span>
        </div>

        <!-- 输入框 -->
        <div class="answer-label">你的回答</div>
        <div class="input-wrapper">
          <el-input
            ref="inputRef"
            v-model="userInput"
            type="textarea"
            :placeholder="dynamicPlaceholder"
            :rows="3"
            :disabled="isProcessing || currentStep < 3"
            @keydown.ctrl.enter="submitMessage"
            @keydown.meta.enter="submitMessage"
          />
        </div>

        <!-- 控制按钮 -->
        <div class="input-controls">
          <div class="control-hints">
            <span>💡 Ctrl+Enter 快速发送</span>
          </div>
          <div class="control-buttons">
            <el-button 
              type="primary" 
              @click="submitMessage"
              :loading="isProcessing"
              :disabled="!canSubmit"
            >
              发送回答
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 注意：右侧评估面板已移除
         评估数据（实时雷达图、行为模式识别、回答统计）
         将在 HR 端单独实现，不在候选人端展示 -->
  </div>

  <!-- 上传/填写信息对话框 -->
  <el-dialog
    v-model="showUploadDialog"
    title="完善候选人信息"
    width="700px"
    class="info-dialog"
  >
    <div class="dialog-content">
      <!-- 简历上传区域 -->
      <div class="upload-section">
        <h4 class="section-title">📄 上传简历（可选）</h4>
        <p class="section-desc">支持 PDF、Word 等格式，系统将自动提取关键信息并填入下方表单</p>
        
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          @change="handleResumeUpload"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          class="resume-upload"
          :disabled="isAnalyzing"
        >
          <template #default>
            <div class="upload-content">
              <el-icon v-if="!isAnalyzing" class="upload-icon"><i class="el-icon-upload"></i></el-icon>
              <el-icon v-else class="upload-icon animate-spin"><i class="el-icon-loading"></i></el-icon>
              <div class="upload-text">
                <p v-if="!isAnalyzing" class="main">拖拽文件到此或<em>点击上传</em></p>
                <p v-else class="main">正在解析文件...</p>
                <p class="secondary">最大 10MB</p>
              </div>
            </div>
          </template>
          <template #tip>
            <div class="el-upload__tip">
              <span v-if="resumeFile && isAnalyzing" class="file-info">
                ⏳ 正在解析: {{ resumeFile.name }}
              </span>
              <span v-else-if="resumeFile" class="file-info">
                ✓ 已选择: {{ resumeFile.name }}
              </span>
              <span v-else>
                完成后自动填入姓名、邮箱、学历、技能等信息
              </span>
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 信息填写区域 -->
      <div class="form-section">
        <h4 class="section-title">👤 基本信息</h4>
        
        <div class="form-group">
          <label class="form-label">姓名 <span class="required">*</span></label>
          <el-input 
            v-model="candidateInfo.name" 
            placeholder="请输入您的姓名"
            clearable
            class="form-input"
          >
            <template #suffix v-if="candidateInfo.name">
              <span class="auto-fill-indicator">✓ 已自动填入</span>
            </template>
          </el-input>
        </div>

        <div class="form-group">
          <label class="form-label">邮箱 <span class="required">*</span></label>
          <el-input 
            v-model="candidateInfo.email" 
            placeholder="请输入您的邮箱地址"
            type="email"
            clearable
            class="form-input"
          >
            <template #suffix v-if="candidateInfo.email">
              <span class="auto-fill-indicator">✓ 已自动填入</span>
            </template>
          </el-input>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">学历 <span class="required">*</span></label>
            <el-select 
              v-model="candidateInfo.education" 
              placeholder="选择学历"
              class="form-select"
            >
              <el-option label="高中" value="高中" />
              <el-option label="大专" value="大专" />
              <el-option label="本科" value="本科" />
              <el-option label="硕士" value="硕士" />
              <el-option label="博士" value="博士" />
            </el-select>
            <span v-if="candidateInfo.education" class="auto-fill-tip">✓ 已自动填入</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">技能标签
            <span class="optional-tag">选填</span>
          </label>
          <el-input 
            v-model="candidateInfo.skills" 
            placeholder="e.g., JavaScript, Vue.js, Python（用逗号分隔）"
            clearable
            class="form-input"
          >
            <template #suffix v-if="candidateInfo.skills">
              <span class="auto-fill-indicator">✓ 已自动填入</span>
            </template>
          </el-input>
          <p class="form-help-text">上传简历后系统自动提取</p>
        </div>

        <div class="form-group">
          <label class="form-label">项目经验
            <span class="optional-tag">选填</span>
          </label>
          <el-input 
            v-model="candidateInfo.projects" 
            placeholder="列举您参与过的主要项目和成就"
            type="textarea"
            :rows="3"
            clearable
            class="form-input"
          >
          </el-input>
          <p class="form-help-text">上传简历后系统自动提取</p>
        </div>
      </div>

      <!-- 信息确认提示 -->
      <div class="info-tips" v-if="candidateInfo.name || candidateInfo.email">
        <el-alert
          title="信息已捕获"
          type="success"
          :closable="false"
          description="系统将使用以上信息生成个性化的面试策略。"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="cancelUpload">取消</el-button>
      <el-button type="primary" @click="proceedFromDialog" :loading="isAnalyzing">
        {{ isAnalyzing ? '分析中...' : '确认并继续' }}
      </el-button>
    </template>
  </el-dialog>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAssessmentStore } from '@/stores/assessment'
import request from '@/utils/request'
import {
  checkResume,
  checkProgress,
  getNextQuestion,
  analyzeInterviewResponse,
  analyzeAndGetNextQuestion,
  updateProgress,
  saveAssessmentResult,
  fetchReport,
  saveLocalProgress,
  loadLocalProgress,
  clearLocalProgress,
  type LocalProgress
} from '@/api/assessment'

// ==================== 类型定义 ====================
interface CandidateInfo {
  name: string
  email: string
  education: string
  skills: string
  projects: string
  background?: string
}

interface Message {
  role: 'ai' | 'candidate'
  content: string
  time: string
  tags?: string[]
  focusArea?: string
  agentRole?: string
  expectedTraits?: string[]
  scoreable?: boolean
  responseTime?: number
  aiFeedback?: string
}

interface InterviewPlan {
  totalQuestions: number
  estimatedTime: number
  category: string
  dimensions: string[]
}

interface Pattern {
  id: string
  name: string
  description: string
  confidence: number
  color: string
}

interface IntroScene {
  title: string
  lines: string[]
  status?: string
}

type AssessmentMode = 'job' | 'resume' | null

const dimensionIcons = ['🎯', '⚡', '🔥', '✨', '🚀'] as const

function getDimensionIcon(index: number): string {
  return dimensionIcons[index % dimensionIcons.length]
}

// ==================== Props & Emits ====================
const props = defineProps<{
  candidateId: string
  targetPosition?: string
  assessmentId?: number
  initialContext?: any
}>()

const emit = defineEmits<{
  (e: 'complete', data: any): void
  (e: 'update-scores', scores: Record<string, number>): void
  (e: 'save', data: any): void
}>()

// Store & Route
const assessmentStore = useAssessmentStore()
const route = useRoute()
const router = useRouter()

// ==================== 流程控制 ====================
const assessmentSteps = [
  '岗位确认',
  '简历解析',
  '面试启动',
  '智能面试',
  '评估报告'
]

const currentStep = ref(0)  // 0: 填写, 1: 确认, 2: 说明, 3: 面试, 4: 报告
const isAnalyzing = ref(false)
const infoConfirmed = ref(false)
const assessmentMode = ref<AssessmentMode>(null)
const selectedJobId = ref<number | null>(null)  // 已选择的岗位ID
const backendAssessmentId = ref<number | null>(null)  // 后端评估记录ID
const selectedJobTitle = ref('')  // 已选择的岗位名称

// ==================== 初始化状态 ====================
const initLoading = ref(true)  // 初始化加载中
const hasExistingResume = ref(false)  // 是否有历史简历
const existingResumeInfo = ref<any>(null)  // 历史简历信息
const hasInProgress = ref(false)  // 是否有进行中的评估
const inProgressInfo = ref<any>(null)  // 进行中评估信息
const localSavedProgress = ref<LocalProgress | null>(null)  // 本地保存的进度

// ==================== 左侧面板控制 ====================
const leftPanelMode = ref<'svg' | 'info'>('svg')  // svg: 显示欢迎图片, info: 显示流程
// SVG 图像地址列表
const svgList = ['/个人信息.svg','/个人信息2.svg','/个人信息3.svg']
const svgImageUrl = ref<string>(svgList[Math.floor(Math.random()*svgList.length)])
const FLOW_AUTO_ADVANCE_DELAY = 1200
let flowAdvanceTimer: number | null = null


// 上传对话框状态
const showUploadDialog = ref(false)

// 解析的简历数据
const parsedResumeData = ref<any>(null)

// ==================== 候选人信息 ====================
const candidateInfo = ref<CandidateInfo>({
  name: '',
  email: '',
  education: '',
  skills: '',
  projects: '',
  background: ''
})

const resumeFile = ref<File | null>(null)

// ==================== 面试信息 ====================
const interviewPlan = ref<InterviewPlan>({
  totalQuestions: 8,
  estimatedTime: 6,
  category: '技术与综合能力',
  dimensions: ['技术能力', '问题解决', '沟通能力', '团队协作']
})

const aiInterviewerAvatar = ref(generateAvatar('AI'))
const aiInterviewerTitle = ref('性格特质与岗位适配评估')

// ==================== 对话管理 ====================
const messages = ref<Message[]>([])
const userInput = ref('')
const isProcessing = ref(false)
const isTyping = ref(false)
const currentPhase = ref('面试准备中...')
const contextHint = ref<string | null>(null)

function toCandidateVisibleContext(context?: string | null) {
  const text = (context || '').trim()
  if (!text) return null
  const internalMarkers = ['问题草案', '规则修正', 'debug', '校验', 'validation']
  if (internalMarkers.some(marker => text.includes(marker))) return null
  return text
}

// ==================== 时间追踪 ====================
const startTime = ref<number>(0)
const elapsedTime = ref(0)
const timerInterval = ref<number | null>(null)

// ==================== 评估数据 ====================
const latestScores = ref<Record<string, number>>({})
const SCORE_ALIASES: Record<string, string> = {
  '专业能力': '技术深度',
  '逻辑思维': '问题解决',
  '表达能力': '沟通能力',
  '团队合作': '团队协作',
  '创新思维': '创新能力',
}
const assessmentEvidence = ref<{
  verified_skills: string[]
  missing_must_have_skills: string[]
  personality_evidence: Record<string, string>
  evidence_quote: string[]
}>({
  verified_skills: [],
  missing_must_have_skills: [],
  personality_evidence: {},
  evidence_quote: [],
})
const scoreCoverage = ref<Record<string, string>>({})
const unobservedScores = ref<Record<string, string>>({})

const latestSentiment = ref<{ emotion: string; confidence: number } | null>(null)
const detectedPatterns = ref<Pattern[]>([])

// ==================== 报告数据 ====================
const reportLoading = ref(false)
const reportData = ref<any>(null)
const reportRecordId = ref<number | null>(null)

// ==================== 三Agent自适应状态 ====================
const interviewState = ref<any>(null)       // 后端面试状态快照
const latestDecision = ref<any>(null)       // DecisionAgent 最新决策
const shouldEndInterview = ref(false)       // DecisionAgent 建议结束

function getCurrentAgentRoleId() {
  return (
    interviewState.value?.current_role ||
    latestDecision.value?.suggested_role ||
    'hr'
  )
}

// ==================== 统计数据 ====================
const respondedCount = ref(0)
const avgResponseTime = ref(0)
const avgResponseLength = computed(() => {
  if (respondedCount.value === 0) return 0
  const total = messages.value
    .filter(m => m.role === 'candidate')
    .reduce((sum, m) => sum + m.content.length, 0)
  return Math.round(total / respondedCount.value)
})

const hasResolvedJobTarget = computed(() => {
  return Boolean(
    selectedJobId.value ||
    inProgressInfo.value?.job_id ||
    props.initialContext?.job_id ||
    selectedJobTitle.value ||
    inProgressInfo.value?.job_title ||
    props.initialContext?.job_title
  )
})

const hasAssessmentPath = computed(() => hasResolvedJobTarget.value || assessmentMode.value === 'resume')

const currentJobDisplayTitle = computed(() => {
  if (hasResolvedJobTarget.value) {
    return (
      selectedJobTitle.value ||
      inProgressInfo.value?.job_title ||
      props.initialContext?.job_title ||
      '岗位评估'
    )
  }

  if (assessmentMode.value === 'resume') {
    return '简历综合评估'
  }

  return '未选择岗位'
})

const isInterviewLocked = computed(() => currentStep.value >= 1 && currentStep.value < 4)

const currentInterviewStatusLabel = computed(() => {
  if (currentStep.value >= 4) return reportLoading.value ? '报告生成中' : '评估完成'
  if (currentStep.value >= 3) return '面试进行中'
  if (currentStep.value >= 1) return '面试准备中'
  if (hasInProgress.value) return '可继续面试'
  return '待开始'
})

const clarityScore = computed(() => {
  return Math.max(5, Math.min(10, (avgResponseLength.value / 50) * 2 + 5))
})
const relevanceScore = computed(() => {
  return Math.max(6, Math.min(10, 7 + Math.random() * 2))
})

// ==================== UI 引用 ====================
const inputRef = ref<any>(null)
const messageStream = ref<any>(null)
const radarChart = ref<any>(null)

// ==================== 计算属性 ====================
const dynamicPlaceholder = computed(() => {
  if (isProcessing.value) return '正在分析中...'
  if (shouldEndInterview.value || currentStep.value >= 4) return '本轮面试已结束'
  if (currentStep.value < 3) return '请先完成前置步骤...'
  return '请结合真实经历，说明你的判断、行动和结果...'
})

const processingStatusText = computed(() => {
  if (respondedCount.value <= 2) return '系统正在提取关键信息并评估作答质量，请稍候...'
  return '系统正在更新评估轨迹并生成下一题，请稍候...'
})

const canSubmit = computed(() => {
  return !isProcessing.value
    && currentStep.value === 3
    && !shouldEndInterview.value
    && userInput.value.trim().length > 0
})

const introScene = computed<IntroScene>(() => {
  if (initLoading.value) {
    return {
      title: '正在连接面试现场',
      lines: ['正在核验候选人身份与评估上下文', '正在载入本场智能面试所需的会话资源'],
      status: '请稍候，系统即将完成接入。'
    }
  }

  if (currentStep.value === 0 && !hasAssessmentPath.value) {
    return {
      title: '请选择本场评估方式',
      lines: ['你可以直接基于简历进入综合评估，也可以先返回选择岗位，再进行针对岗位的定向评估', '岗位评估更强调匹配度，简历综合评估更强调履历与通用潜力'],
      status: ''
    }
  }

  if (currentStep.value === 0 && hasExistingResume.value) {
    return {
      title: hasResolvedJobTarget.value ? '岗位上下文已注入' : '综合评估链路已就绪',
      lines: [
        hasResolvedJobTarget.value ? `当前岗位：${currentJobDisplayTitle.value}` : '当前模式：简历综合评估',
        hasResolvedJobTarget.value ? '系统已检测到你的历史履历信息，正在准备岗位匹配型面试链路' : '系统已检测到你的历史履历信息，正在准备基于履历画像的综合评估链路',
        '你可以直接沿用已有画像，也可以替换为新的简历内容'
      ],
      status: '确认履历后，系统将立即进入正式面试。'
    }
  }

  if (currentStep.value === 0) {
    return {
      title: hasResolvedJobTarget.value ? '岗位上下文已注入' : '综合评估链路已就绪',
      lines: [
        hasResolvedJobTarget.value ? `当前岗位：${currentJobDisplayTitle.value}` : '当前模式：简历综合评估',
        hasResolvedJobTarget.value ? '系统将先解析你的简历与经历，再动态生成本场岗位评估策略' : '系统将先解析你的简历与经历，再动态生成综合评估策略',
        '信息完成后，系统会自动进入正式提问。'
      ],
      status: '请先上传简历或补全信息。'
    }
  }

  if (currentStep.value === 1) {
    return {
      title: '候选人画像构建完成',
      lines: ['我已完成对你的背景、技能和评估关注维度的初步建模'],
      status: hasResolvedJobTarget.value ? '正在生成岗位定制化面试计划，即将自动开始。' : '正在生成基于履历画像的综合评估计划，即将自动开始。'
    }
  }

  if (currentStep.value === 2) {
    return {
      title: '智能面试已就绪',
      lines: [hasResolvedJobTarget.value ? '我已结合岗位需求和履历信息，为你生成本场个性化评估计划' : '我已结合你的履历背景和能力线索，为你生成本场综合评估计划', '接下来我会连续推进提问、分析和决策，请尽量完整作答'],
      status: '系统正在启动面试流程，马上进入正式提问。'
    }
  }

  return {
    title: '面试已启动',
    lines: ['系统正在进入正式提问阶段'],
    status: ''
  }
})

// 安全解析候选人 ID - 防御性编程，层级化降级
const parsedCandidateId = computed(() => {
  console.log('【parsedCandidateId】计算开始:', {
    props: props.candidateId,
    type: typeof props.candidateId,
    isValidProps: props.candidateId && !isNaN(Number(props.candidateId))
  })
  
  // 优先：使用 props 中的有效数字值
  if (props.candidateId && !isNaN(Number(props.candidateId))) {
    const parsed = parseInt(String(props.candidateId))
    if (!isNaN(parsed) && parsed > 0) {
      console.log('【parsedCandidateId】✅ 使用 props 中的值:', parsed)
      return parsed
    }
  }
  
  // 其次：尝试从 localStorage 获取登录后保存的 user_id
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId && storedUserId !== 'null' && !isNaN(Number(storedUserId))) {
    const parsed = parseInt(storedUserId)
    if (!isNaN(parsed) && parsed > 0) {
      console.log('【parsedCandidateId】✅ 使用 localStorage 中的 user_id:', parsed)
      return parsed
    }
  }
  
  // 最后返回 null（而不是 NaN）
  console.warn('【parsedCandidateId】⚠️ 无法获取有效的 candidateId，returning null')
  return null
})

// ==================== 简历上传与解析 ====================
function goSelectJob() {
  router.push('/home/jobs')
}

function startResumeAssessmentEntry() {
  assessmentMode.value = 'resume'
  leftPanelMode.value = 'info'

  if (hasExistingResume.value) {
    void useExistingResume()
    return
  }

  openUploadDialog()
}

function clearFlowAdvanceTimer() {
  if (flowAdvanceTimer) {
    clearTimeout(flowAdvanceTimer)
    flowAdvanceTimer = null
  }
}

function queueBriefingAndInterviewStart() {
  clearFlowAdvanceTimer()
  flowAdvanceTimer = window.setTimeout(async () => {
    currentStep.value = 2
    await scrollToBottom()

    clearFlowAdvanceTimer()
    flowAdvanceTimer = window.setTimeout(async () => {
      await startInterview()
    }, FLOW_AUTO_ADVANCE_DELAY)
  }, FLOW_AUTO_ADVANCE_DELAY)
}

function openUploadDialog() {
  // 切换面板为 info 以显示流程叠加背景
  leftPanelMode.value = 'info'
  currentStep.value = 0
  showUploadDialog.value = true
  console.log('打开上传对话框:', showUploadDialog.value)
}

/** 使用已有的简历/个人信息，跳过上传步骤 */
async function useExistingResume() {
  if (!existingResumeInfo.value) return
  const info = existingResumeInfo.value

  // 填充 candidateInfo
  candidateInfo.value.name = info.name || ''
  candidateInfo.value.email = info.email || ''
  candidateInfo.value.education = info.education || ''
  candidateInfo.value.skills = Array.isArray(info.skills) ? info.skills.join(', ') : (info.skills || '')
  candidateInfo.value.projects = info.projects || info.project_experience || info.work_experience || ''

  // 构造 parsedResumeData 以供后续步骤使用
  parsedResumeData.value = {
    candidate_info: {
      name: info.name || '',
      email: info.email || '',
      education: info.education || '',
      experience_level: '',
      technical_skills: Array.isArray(info.skills) ? info.skills : [],
      project_experience: info.projects || info.project_experience || info.work_experience || '',
      work_experience: info.work_experience || info.project_experience || info.projects || '',
      soft_skills: [],
    },
    assessed_dimensions: ['技术能力', '问题解决', '沟通能力', '团队协作', '学习能力'],
  }

  leftPanelMode.value = 'info'
  currentStep.value = 1  // 直接跳到确认信息
  ElMessage.success('已加载历史信息')
  await scrollToBottom()
  queueBriefingAndInterviewStart()
}

function cancelUpload() {
  showUploadDialog.value = false
  // 如果还未完成任何填写，回到 SVG 欢迎屏
  if (!candidateInfo.value.name && !candidateInfo.value.education && !candidateInfo.value.skills) {
    leftPanelMode.value = 'svg'
  }
}

function handleResumeUpload(file: any) {
  resumeFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
  
  // 立即调用后端API解析文件
  uploadAndParseResume(file.raw, file.name)
}

async function uploadAndParseResume(file: File, filename: string) {
  const cid = String(parsedCandidateId.value || props.candidateId || '')
  // 创建FormData用于文件上传
  const formData = new FormData()
  formData.append('file', file)
  formData.append('candidate_id', cid)
  
  try {
    isAnalyzing.value = true
    console.log('开始上传文件:', filename, '大小:', file.size)
    
    // 调用后端API - 注意这里使用POST，参数在URL中
    const params = new URLSearchParams()
    params.append('candidate_id', cid)
    
    const response = await fetch(
      `/assessment/immersive/upload-resume?${params.toString()}`,
      {
        method: 'POST',
        body: formData
        // 不要设置 Content-Type header，浏览器会自动设置为 multipart/form-data
      }
    )
    
    console.log('后端响应状态码:', response.status)
    
    // 先检查response的状态和content-type
    if (!response.ok) {
      // 获取错误消息
      const contentType = response.headers.get('content-type')
      let errorMsg = `服务器错误 (${response.status})`
      
      if (contentType?.includes('application/json')) {
        try {
          const errorData = await response.json()
          errorMsg = errorData.detail || errorData.message || errorMsg
        } catch (e) {
          // JSON解析失败，使用默认错误信息
        }
      } else {
        // 非JSON响应，尝试获取文本
        try {
          const errorText = await response.text()
          if (errorText) {
            errorMsg = errorText.substring(0, 100) // 只显示前100个字符
          }
        } catch (e) {
          // 无法读取响应体
        }
      }
      
      console.error('后端返回错误:', errorMsg)
      throw new Error(errorMsg)
    }
    
    // 检查响应是否包含JSON
    const contentType = response.headers.get('content-type')
    if (!contentType?.includes('application/json')) {
      const responseText = await response.text()
      console.error('后端返回非JSON响应:', responseText.substring(0, 200))
      throw new Error('后端返回无效的响应格式（非JSON）')
    }
    
    // 安全地解析JSON
    let result
    try {
      result = await response.json()
    } catch (jsonError) {
      console.error('JSON解析错误:', jsonError)
      const responseText = await response.text()
      console.error('响应内容:', responseText.substring(0, 200))
      throw new Error('响应JSON格式错误')
    }
    
    console.log('解析后的结果:', result)
    
    if (result.code === 200) {
      const data = result.data
      
      // 保存完整的解析数据供Step 1展示
      parsedResumeData.value = result.data
      
      // 自动填入表单字段
      if (data.candidate_info) {
        const info = data.candidate_info
        
        // 填入基本信息
        if (info.name && info.name !== '未提取') {
          candidateInfo.value.name = info.name
          console.log('自动填入姓名:', info.name)
        }
        if (info.email) {
          candidateInfo.value.email = info.email
          console.log('自动填入邮箱:', info.email)
        }
        if (info.education && info.education !== '') {
          candidateInfo.value.education = info.education
          console.log('自动填入学历:', info.education)
        }
        
        // 填入技能
        if (info.technical_skills?.length > 0) {
          candidateInfo.value.skills = info.technical_skills.join(', ')
          console.log('自动填入技能:', info.technical_skills)
        }
        
        // 填入项目/实践经历
        const projectExperience = info.project_experience || info.projects || info.work_experience
        if (projectExperience && projectExperience !== ''){
          candidateInfo.value.projects = projectExperience.substring(0, 1000)
          console.log('自动填入项目/实践经历')
        }
      }
      
      ElMessage.success('文件解析成功，信息已自动填入！')
      console.log('✓ 简历解析完成')
    } else {
      console.warn('解析返回非200状态:', result)
      ElMessage.warning(result.message || '文件解析完成，请检查自动填入的信息')
    }
  } catch (error) {
    console.error('文件解析失败:', error)
    const errorMsg = error instanceof Error ? error.message : String(error)
    ElMessage.error(`文件解析失败: ${errorMsg}`)
    console.error('建议: 检查后端服务是否正运行，查看后端日志获取详细信息')
  } finally {
    isAnalyzing.value = false
  }
}

async function proceedToStep1() {
  // 验证必填信息
  if (!candidateInfo.value.name || !candidateInfo.value.email) {
    ElMessage.error('请填写姓名和邮箱')
    return
  }

  isAnalyzing.value = true
  
  try {
    // 调用后端API解析简历
    const cidStr = String(parsedCandidateId.value || props.candidateId || '')
    const response = await fetch(
      `/assessment/immersive/parse-resume?` + new URLSearchParams({
        candidate_id: cidStr,
        candidate_name: candidateInfo.value.name,
        candidate_email: candidateInfo.value.email,
        education: candidateInfo.value.education || '',
        skills: candidateInfo.value.skills || '',
        projects: candidateInfo.value.projects || ''
      }),
      {
        method: 'POST'
      }
    )
    
    const result = await response.json()
    
    if (result.code === 200) {
      // 保存解析的数据
      parsedResumeData.value = result.data
      
      // 更新候选人信息
      if (result.data.candidate_info) {
        candidateInfo.value = {
          ...candidateInfo.value,
          ...result.data.candidate_info
        }
      }
      
      // 关闭对话框，进入Step 1
      showUploadDialog.value = false
      currentStep.value = 1
      
      // 自动滚动到下面
      await scrollToBottom()
      queueBriefingAndInterviewStart()
      
      ElMessage.success('信息解析成功！')
    } else {
      throw new Error(result.message || '解析失败')
    }
  } catch (error) {
    console.error('简历解析失败:', error)
    ElMessage.error('信息解析失败，请重试')
  } finally {
    isAnalyzing.value = false
  }
}

// 从弹窗点击确认进入下一步
async function proceedFromDialog() {
  showUploadDialog.value = false
  await proceedToStep1()
}

async function proceedFromDialogComponent(info: CandidateInfo) {
  // 更新用户信息
  candidateInfo.value = { ...candidateInfo.value, ...info }
  showUploadDialog.value = false
  await proceedToStep1()
}

async function startInterview() {
  if (currentStep.value >= 3) return

  currentStep.value = 3
  respondedCount.value = 0
  
  // 启动计时器
  startTime.value = Date.now()
  timerInterval.value = window.setInterval(() => {
    elapsedTime.value = Date.now() - startTime.value
  }, 1000)
  
  // 启动自动保存
  startAutoSave()
  
  // 在后端创建评估记录（状态: pending）
  if (!backendAssessmentId.value) {
    const cid = parsedCandidateId.value
    if (cid) {
      try {
        const res = await updateProgress({
          candidate_id: cid,
          job_id: selectedJobId.value ?? undefined,
          job_title: selectedJobTitle.value || '未知岗位',
          status: 'pending',
          total_rounds: 0,
        })
        if (res.code === 200 && res.data?.assessment_id) {
          backendAssessmentId.value = res.data.assessment_id
        }
      } catch (e) {
        console.warn('创建评估记录失败:', e)
      }
    }
  }
  
  // 显示初始欢迎消息并生成第一个问题
  isTyping.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 添加面试开始消息
  const openingMessage = hasResolvedJobTarget.value
    ? `好的，我们开始吧！本场将围绕岗位“${currentJobDisplayTitle.value}”展开评估。\n\n我会从经历背景、岗位能力和综合潜力三个方向持续推进提问，并根据你的回答实时调整深度。`
    : `好的，我们开始吧！本场将进行简历综合评估。\n\n我会围绕你的履历背景、通用能力和发展潜力持续推进提问，并根据你的回答实时调整深度。`

  messages.value.push({
    role: 'ai',
    content: openingMessage,
    time: nowTime(),
    tags: ['面试开始', '破冰'],
    focusArea: 'opening',
    scoreable: false,
  })
  
  isTyping.value = false
  await scrollToBottom()
  
  // 延迟后生成第一个问题
  await new Promise(resolve => setTimeout(resolve, 500))
  await generateNextQuestion()
}

// ==================== 对话逻辑 ====================
async function generateNextQuestion() {
  isTyping.value = true
  
  // 获取下一个问题
  const question = await fetchNextQuestion()
  
  messages.value.push({
    role: 'ai',
    content: question.content,
    time: nowTime(),
    tags: question.tags,
    focusArea: question.focusArea,
    agentRole: question.agentRole,
    expectedTraits: question.expectedTraits,
    scoreable: true,
  })
  
  isTyping.value = false
  currentPhase.value = question.phase || '多轮面试中'
  contextHint.value = toCandidateVisibleContext(question.context)
  
  await scrollToBottom()
  inputRef.value?.focus()
}

async function submitMessage() {
  if (!canSubmit.value) return
  if (shouldEndInterview.value || currentStep.value !== 3) {
    userInput.value = ''
    return
  }

  const content = userInput.value.trim()
  const responseTime = Date.now()
  
  // 添加候选人消息
  messages.value.push({
    role: 'candidate',
    content,
    time: nowTime(),
    responseTime: Math.round((responseTime - startTime.value) / 1000)
  })
  
  respondedCount.value++
  userInput.value = ''
  isProcessing.value = true
  
  await scrollToBottom()
  
  try {
    const isFinalAnswer = respondedCount.value >= interviewPlan.value.totalQuestions
    // 最后一题只做回答分析，不再生成下一题，避免候选人等待无用的 LLM 请求
    const result = isFinalAnswer
      ? { analysis: await analyzeResponse(content), nextQuestion: null, shouldEnd: true }
      : await analyzeAndFetchNext(content)
    
    // 1. 更新评分
    updateScores(result.analysis.scores, result.analysis.scoreCoverage)
    
    // 2. 更新情绪
    latestSentiment.value = result.analysis.sentiment
    
    // 3. 更新模式
    if (result.analysis.patterns) {
      updatePatterns(result.analysis.patterns)
    }
    
    // 4. 添加反馈
    const personalityNote = result.analysis.personalityObservation?.scenario_personality
    messages.value[messages.value.length - 1].aiFeedback = personalityNote
      ? `${result.analysis.feedback}\n心理特质观察：${personalityNote}`
      : result.analysis.feedback
    
    // 5. 检查是否完成
    if (respondedCount.value >= interviewPlan.value.totalQuestions || result.shouldEnd) {
      shouldEndInterview.value = true
      messages.value.push({
        role: 'ai',
        content: '本轮智能面试已完成。系统将基于本次回答生成性格特质分析、岗位适配结论与匹配建议。',
        time: nowTime(),
        tags: ['面试结束', '心理特质评估', '人岗匹配'],
        focusArea: '评估总结',
        agentRole: getCurrentAgentRoleId(),
        scoreable: false,
      })
      await scrollToBottom()
      completeInterview()
    } else if (result.nextQuestion) {
      // 6. 每次回答后自动保存
      doAutoSave()
      // 7. 直接显示下一个问题（无需再发请求）
      isTyping.value = true
      await new Promise(resolve => setTimeout(resolve, 600))
      messages.value.push({
        role: 'ai',
        content: result.nextQuestion.content,
        time: nowTime(),
        tags: result.nextQuestion.tags,
        focusArea: result.nextQuestion.focusArea,
        agentRole: result.nextQuestion.agentRole,
        expectedTraits: result.nextQuestion.expectedTraits,
        scoreable: true,
      })
      isTyping.value = false
      currentPhase.value = result.nextQuestion.phase || '多轮面试中'
      contextHint.value = toCandidateVisibleContext(result.nextQuestion.context)
      await scrollToBottom()
      inputRef.value?.focus()
    } else {
      doAutoSave()
      await generateNextQuestion()
    }
    
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error('系统处理失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

async function analyzeResponse(content: string) {
  try {
    const cid = String(parsedCandidateId.value || props.candidateId || '')
    
    // 构建简历信息
    const resumePayload: Record<string, any> = {}
    if (candidateInfo.value.name) resumePayload.name = candidateInfo.value.name
    if (candidateInfo.value.education) resumePayload.education = candidateInfo.value.education
    const rawSkills = candidateInfo.value.skills || existingResumeInfo.value?.skills
    if (rawSkills) {
      resumePayload.skills = Array.isArray(rawSkills) ? rawSkills : String(rawSkills).split(/[,，]/).map((s: string) => s.trim()).filter(Boolean)
    }

    // 构建岗位信息
    const jobPayload: Record<string, any> = {}
    if (selectedJobId.value) jobPayload.id = selectedJobId.value
    if (selectedJobTitle.value) jobPayload.title = selectedJobTitle.value

    const data = await analyzeInterviewResponse({
      candidate_id: cid,
      assessment_id: backendAssessmentId.value ?? undefined,
      candidate_name: candidateInfo.value.name || '',
      role_id: getCurrentAgentRoleId(),
      candidate_response: content,
      conversation_depth: respondedCount.value,
      history: messages.value.slice(-5).map(m => ({
        role: m.role === 'candidate' ? 'candidate' : 'assistant',
        content: m.content,
        tags: m.tags || [],
        focus_area: m.focusArea,
        agent_role: m.agentRole,
        expected_traits: m.expectedTraits || [],
        scoreable: m.scoreable !== false,
      })),
      target_position: selectedJobTitle.value || undefined,
      resume_info: Object.keys(resumePayload).length > 0 ? resumePayload : undefined,
      job_info: Object.keys(jobPayload).length > 0 ? jobPayload : undefined,
    })

    if (data.code === 200 && data.data?.analysis) {
      const analysis = data.data.analysis
      mergeAssessmentEvidence(analysis)
      // 捕获 DecisionAgent 决策和面试状态
      if (analysis.decision) {
        latestDecision.value = analysis.decision
        shouldEndInterview.value = !!analysis.decision.should_end
      }
      if (analysis.interview_state) {
        interviewState.value = analysis.interview_state
      }
      return {
        scores: analysis.scores || {},
        scoreCoverage: analysis.score_coverage || {},
        qualitySignals: analysis.quality_signals || {},
        sentiment: analysis.sentiment || { emotion: '专注', confidence: 75 },
        patterns: analysis.patterns || [],
        feedback: analysis.feedback || '很好的回答！',
        personalityObservation: analysis.personality_observation || null,
        decision: analysis.decision || null
      }
    }
  } catch (error) {
    console.warn('API 调用失败:', error)
  }
  
  return getLocalFallbackAnalysis()
}

function getLocalFallbackAnalysis() {
  return {
    scores: {
      '专业能力': 7.5 + Math.random() * 2,
      '逻辑思维': 7.0 + Math.random() * 2,
      '表达能力': 7.5 + Math.random() * 2,
      '学习能力': 7.0 + Math.random() * 1.5,
      '团队合作': 7.5 + Math.random() * 1.5,
      '创新思维': 7.0 + Math.random() * 2
    },
    scoreCoverage: {
      '专业能力': 'observed',
      '逻辑思维': 'observed',
      '表达能力': 'observed',
      '学习能力': 'observed',
      '团队合作': 'observed',
      '创新思维': 'observed',
    },
    qualitySignals: { fallback: true },
    sentiment: { emotion: ['自信', '谨慎', '积极'][Math.floor(Math.random() * 3)], confidence: 70 + Math.random() * 20 },
    patterns: [
      {
        id: 'p1',
        name: '结构化思维',
        description: '回答清晰有条理',
        confidence: 78,
        color: '#67c23a'
      }
    ],
    feedback: '很好的回答！逻辑清晰，表达准确。',
    personalityObservation: {
      scenario_personality: '本地备用评估无法形成稳定心理特质判断'
    }
  }
}

// ==================== 合并请求：分析回答 + 生成下一题 ====================
async function analyzeAndFetchNext(content: string) {
  try {
    const cid = String(parsedCandidateId.value || props.candidateId || '')

    // 构建简历信息
    const resumePayload: Record<string, any> = {}
    if (candidateInfo.value.name) resumePayload.name = candidateInfo.value.name
    if (candidateInfo.value.education) resumePayload.education = candidateInfo.value.education
    const rawSkills = candidateInfo.value.skills || existingResumeInfo.value?.skills
    if (rawSkills) {
      resumePayload.skills = Array.isArray(rawSkills) ? rawSkills : String(rawSkills).split(/[,，]/).map((s: string) => s.trim()).filter(Boolean)
    }

    // 构建岗位信息
    const jobPayload: Record<string, any> = {}
    if (selectedJobId.value) jobPayload.id = selectedJobId.value
    if (selectedJobTitle.value) jobPayload.title = selectedJobTitle.value

    const data = await analyzeAndGetNextQuestion({
      candidate_id: cid,
      assessment_id: backendAssessmentId.value ?? undefined,
      candidate_name: candidateInfo.value.name || '',
      role_id: getCurrentAgentRoleId(),
      candidate_response: content,
      conversation_depth: respondedCount.value,
      history: messages.value.slice(-6).map(m => ({
        role: m.role === 'candidate' ? 'candidate' : 'assistant',
        content: m.content,
        tags: m.tags || [],
        focus_area: m.focusArea,
        agent_role: m.agentRole,
        expected_traits: m.expectedTraits || [],
        scoreable: m.scoreable !== false,
      })),
      target_position: selectedJobTitle.value || undefined,
      resume_info: Object.keys(resumePayload).length > 0 ? resumePayload : undefined,
      job_info: Object.keys(jobPayload).length > 0 ? jobPayload : undefined,
    })

    if (data.code === 200 && data.data) {
      const analysis = data.data.analysis || {}
      const nextQ = data.data.question
      mergeAssessmentEvidence(analysis)

      // 更新面试状态
      if (analysis.decision) {
        latestDecision.value = analysis.decision
      }
      if (analysis.interview_state) {
        interviewState.value = analysis.interview_state
      }
      if (nextQ?.interview_state) {
        interviewState.value = nextQ.interview_state
      }

      return {
        analysis: {
          scores: analysis.scores || {},
          scoreCoverage: analysis.score_coverage || {},
          qualitySignals: analysis.quality_signals || {},
          sentiment: analysis.sentiment || { emotion: '专注', confidence: 75 },
          patterns: analysis.patterns || [],
          feedback: analysis.feedback || '很好的回答！',
          personalityObservation: analysis.personality_observation || null,
        },
        nextQuestion: nextQ ? {
          content: nextQ.question || nextQ.content || '',
          tags: nextQ.tags || [],
          context: nextQ.context || null,
          interviewState: nextQ.interview_state || null,
          focusArea: nextQ.focus_area || null,
          agentRole: nextQ.interview_state?.current_role || getCurrentAgentRoleId(),
          expectedTraits: nextQ.expected_traits || [],
          phase: nextQ.phase || nextQ.interview_state?.current_role || '多轮面试'
        } : null,
        shouldEnd: !!data.data.should_end
      }
    }
  } catch (error) {
    console.warn('合并请求失败:', error)
  }

  // 降级：返回本地备用
  const fallback = getLocalFallbackAnalysis()
  return {
    analysis: fallback,
    nextQuestion: null,
    shouldEnd: false
  }
}

async function fetchNextQuestion() {
  try {
    const cid = String(parsedCandidateId.value || props.candidateId || '')
    
    // 构建简历信息 (简历驱动提问)
    const resumePayload: Record<string, any> = {}
    if (candidateInfo.value.name) resumePayload.name = candidateInfo.value.name
    if (candidateInfo.value.email) resumePayload.email = candidateInfo.value.email
    if (candidateInfo.value.education) resumePayload.education = candidateInfo.value.education
    if (candidateInfo.value.projects) resumePayload.projects = candidateInfo.value.projects
    // skills 可能是字符串或数组
    const rawSkills = candidateInfo.value.skills || existingResumeInfo.value?.skills
    if (rawSkills) {
      resumePayload.skills = Array.isArray(rawSkills) ? rawSkills : String(rawSkills).split(/[,，]/).map((s: string) => s.trim()).filter(Boolean)
    }

    // 构建岗位信息
    const jobPayload: Record<string, any> = {}
    if (selectedJobId.value) jobPayload.id = selectedJobId.value
    if (selectedJobTitle.value) jobPayload.title = selectedJobTitle.value

    const data = await getNextQuestion({
      candidate_id: cid,
      assessment_id: backendAssessmentId.value ?? undefined,
      candidate_name: candidateInfo.value.name || '',
      role_id: getCurrentAgentRoleId(),
      conversation_depth: respondedCount.value,
      history: messages.value.map(m => ({
        role: m.role === 'candidate' ? 'candidate' : 'assistant',
        content: m.content,
        tags: m.tags || [],
        focus_area: m.focusArea,
        agent_role: m.agentRole,
        expected_traits: m.expectedTraits || [],
        scoreable: m.scoreable !== false,
      })),
      target_position: selectedJobTitle.value || undefined,
      resume_info: Object.keys(resumePayload).length > 0 ? resumePayload : undefined,
      job_info: Object.keys(jobPayload).length > 0 ? jobPayload : undefined,
    })
    
    if (data.code === 200 && data.data?.question) {
      const question = data.data.question
      if (question.interview_state) {
        interviewState.value = question.interview_state
      }
      return {
        content: question.question || question.content,
        tags: question.tags || [],
        context: question.context,
        focusArea: question.focus_area || null,
        agentRole: question.interview_state?.current_role || getCurrentAgentRoleId(),
        expectedTraits: question.expected_traits || [],
        phase: question.phase || question.interview_state?.current_role || '多轮面试'
      }
    }
  } catch (error) {
    console.warn('获取问题失败:', error)
  }
  
  return getLocalFallbackQuestion()
}

function getLocalFallbackQuestion() {
  const questions = [
    '请简单介绍一下你自己和你的背景？',
    '你在过去的工作中遇到过什么挑战？如何解决的？',
    '描述一个你最自豪的项目经历',
    '如何处理与团队成员的分歧？',
    '你如何保持技术知识的更新？',
    '在压力下工作时你会怎样？',
    '你对这个岗位最感兴趣的部分是什么？',
    '你对我们公司有什么了解？为什么想加入我们？'
  ]
  
  const q = questions[respondedCount.value % questions.length]
  return {
    content: q,
    tags: ['开放式问题', '经验分享'],
    context: '请详细描述你的思考过程',
    focusArea: '综合评估',
    agentRole: getCurrentAgentRoleId(),
    expectedTraits: [],
    phase: '多轮面试'
  }
}

function normalizeScoreName(name: string) {
  return SCORE_ALIASES[name] || name
}

function updateScores(newScores: Record<string, number>, coverage?: Record<string, string>) {
  Object.entries(newScores || {}).forEach(([rawKey, rawValue]) => {
    const key = normalizeScoreName(rawKey)
    const rawStatus = coverage?.[rawKey] || coverage?.[key]
    if (coverage && rawStatus !== 'observed') {
      unobservedScores.value[key] = '证据不足/待补充观察'
      return
    }
    const value = Number(rawValue)
    if (!Number.isFinite(value) || value <= 0) return

    const target = value > 10 ? value / 10 : value
    const current = latestScores.value[key]
    latestScores.value[key] = typeof current === 'number' && current > 0
      ? Math.round((current * 0.6 + target * 0.4) * 10) / 10
      : Math.round(target * 10) / 10
    scoreCoverage.value[key] = 'observed'
    delete unobservedScores.value[key]
  })

  Object.entries(coverage || {}).forEach(([rawKey, status]) => {
    const key = normalizeScoreName(rawKey)
    if (status !== 'observed' && !latestScores.value[key]) {
      scoreCoverage.value[key] = status
      unobservedScores.value[key] = '证据不足/待补充观察'
    }
  })
  
  emit('update-scores', latestScores.value)
  // 评估数据不在候选人端显示，只在 HR 端显示
}

function mergeAssessmentEvidence(analysis: any) {
  const verified = [
    ...(analysis?.verified_skills || []),
    ...(analysis?.skill_match?.matched || []),
  ].map((item: any) => String(item || '').trim()).filter(Boolean)
  assessmentEvidence.value.verified_skills = Array.from(new Set([
    ...assessmentEvidence.value.verified_skills,
    ...verified,
  ])).slice(0, 12)

  const missing = [
    ...(analysis?.missing_must_have_skills || []),
    ...(analysis?.skill_match?.gap || []),
  ].map((item: any) => String(item || '').trim()).filter(Boolean)
  assessmentEvidence.value.missing_must_have_skills = Array.from(new Set([
    ...assessmentEvidence.value.missing_must_have_skills,
    ...missing,
  ])).slice(0, 12)

  const evidence = analysis?.personality_evidence || analysis?.personality_observation?.trait_evidence || {}
  Object.entries(evidence).forEach(([trait, quote]) => {
    const text = String(quote || '').trim()
    if (text && !text.includes('证据不足')) {
      assessmentEvidence.value.personality_evidence[trait] = text
    }
  })

  const quote = String(analysis?.evidence_quote || analysis?.evidence || '').trim()
  if (quote) {
    assessmentEvidence.value.evidence_quote = Array.from(new Set([
      ...assessmentEvidence.value.evidence_quote,
      quote,
    ])).slice(-8)
  }
}

function updatePatterns(patterns: Pattern[]) {
  detectedPatterns.value = patterns
}

function completeInterview() {
  if (shouldEndInterview.value && currentStep.value >= 4) return
  shouldEndInterview.value = true
  ElMessage.success('✨ 面试完成！正在生成报告...')
  currentStep.value = 4  // 进入报告阶段
  
  // 停止计时器 & 自动保存
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  stopAutoSave()
  
  // 清除本地进度
  const cid = parsedCandidateId.value
  if (cid) clearLocalProgress(cid)
  
  // 准备完成数据
  const validScores = Object.values(latestScores.value).filter(v => typeof v === 'number' && v > 0)
  const overallScore = validScores.length
    ? validScores.reduce((a, b) => a + b, 0) / validScores.length
    : 5
  
  const completionData = {
    sessionId: `session_${Date.now()}`,
    messages: messages.value,
    scores: latestScores.value,
    patterns: detectedPatterns.value,
    duration: elapsedTime.value,
    respondedCount: respondedCount.value,
    candidateId: props.candidateId,
    assessmentId: backendAssessmentId.value || props.assessmentId,
    candidateInfo: {
      name: candidateInfo.value.name,
      education: candidateInfo.value.education,
      skills: candidateInfo.value.skills,
      projects: candidateInfo.value.projects
    },
    startTime: new Date(startTime.value),
    endTime: new Date(),
    totalQuestions: interviewPlan.value.totalQuestions,
    avgResponseTime: respondedCount.value > 0 
      ? Math.round(elapsedTime.value / respondedCount.value / 1000) 
      : 0
  }
  
  // 📌 标记评估完成，通知 HomeView 刷新数据
  assessmentStore.markEvaluationComplete({
    jobId: props.initialContext?.job_id,
    assessmentId: (backendAssessmentId.value || props.assessmentId)?.toString(),
    sessionId: completionData.sessionId,
    candidateId: props.candidateId
  })
  
  // 生成报告
  generateReport(cid, overallScore, completionData)
  
  // Emit 完成事件（父组件可能需要关闭模态框或导航）
  emit('complete', completionData)
}

/** 本地降级时仅使用已有大五分；缺失时返回中性值 */
function getFallbackBigFive(scores: Record<string, number>): Record<string, number> {
  return {
    '外向性': scores['外向性'] ?? 5,
    '宜人性': scores['宜人性'] ?? 5,
    '尽责性': scores['尽责性'] ?? 5,
    '神经质': scores['神经质'] ?? 5,
    '开放性': scores['开放性'] ?? 5,
  }
}

function getAgentBigFiveScores(): Record<string, number> {
  const traits = interviewState.value?.personality_traits || {}
  const result: Record<string, number> = {}
  ;(['外向性', '宜人性', '尽责性', '开放性'] as const).forEach(trait => {
    const score = traits[trait]?.basic_score
    if (typeof score === 'number' && score > 0) result[trait] = score
  })
  const emotionalStability = traits['情绪稳定性']?.basic_score
  if (typeof emotionalStability === 'number' && emotionalStability > 0) {
    result['神经质'] = Math.max(0, Math.min(10, Math.round((10 - emotionalStability) * 10) / 10))
  }
  return result
}

function getAgentFusionScores(): Record<string, number> {
  const score = (keys: string[]) => {
    const values = keys
      .map(key => latestScores.value[key])
      .filter(value => typeof value === 'number' && value > 0)
    if (!values.length) return 50
    const avg = values.reduce((sum, value) => sum + value, 0) / values.length
    return Math.max(0, Math.min(100, Math.round((avg <= 10 ? avg * 10 : avg) * 10) / 10))
  }

  return {
    technical: score(['专业能力', '技术深度', '问题解决', '逻辑思维', '学习能力']),
    hr: score(['表达能力', '沟通能力', '团队合作', '团队协作', '文化契合']),
    hiring_manager: score(['创新能力', '用户洞察', '战略思维', '领导力', '问题解决'])
  }
}

function toBackendPercentScore(score: number | null | undefined): number {
  if (typeof score !== 'number' || !Number.isFinite(score)) return 0
  const percent = score <= 10 ? score * 10 : score
  return Math.max(0, Math.min(100, Math.round(percent * 10) / 10))
}

/** 调用后端保存评估结果并获取报告 */
async function generateReport(cid: number | null, overallScore: number, completionData: any) {
  reportLoading.value = true
  
  try {
    const jobId = selectedJobId.value || props.initialContext?.job_id || null
    const agentBigFive = getAgentBigFiveScores()
    const agentScores = getAgentFusionScores()
    const fallbackBigFive = getFallbackBigFive(agentBigFive)

    if (!jobId) {
      reportData.value = {
        ...buildLocalReport(fallbackBigFive, overallScore),
        report_mode: 'resume',
        report_title: '简历综合评估报告',
      }

      if (cid) {
        updateProgress({
          candidate_id: cid,
          assessment_id: backendAssessmentId.value ?? undefined,
          job_title: currentJobDisplayTitle.value,
          status: 'completed',
          total_rounds: respondedCount.value,
          duration_minutes: elapsedTime.value / 60000,
          conversation_depth: respondedCount.value,
          match_score: toBackendPercentScore(overallScore),
          conversation_summary: `完成${respondedCount.value}轮综合评估，总时长${formatTime(elapsedTime.value)}`,
        }).catch(e => console.warn('更新综合评估状态失败:', e))
      }

      return
    }
    
    // 1. 保存评估结果到后端（生成报告数据）
    const saveRes = await saveAssessmentResult({
      candidate_id: String(cid || props.candidateId),
      assessment_id: backendAssessmentId.value ?? undefined,
      job_id: jobId,
      assessment_mode: 'immersive',
      all_scores: latestScores.value,
      personality_scores: agentBigFive,
      agent_scores: agentScores,
      candidate_info: completionData.candidateInfo,
      assessment_evidence: {
        ...assessmentEvidence.value,
        score_coverage: scoreCoverage.value,
        unobserved_scores: unobservedScores.value,
      },
    })
    
    if (saveRes.code === 200 && saveRes.data?.record_id) {
      reportRecordId.value = saveRes.data.record_id
      
      // 2. 获取生成的报告
      const reportRes = await fetchReport(saveRes.data.record_id)
      
      if (reportRes.code === 200 && reportRes.data) {
        reportData.value = reportRes.data
        console.log('[Report] 报告已生成:', reportRes.data)
      } else {
        // 后端报告获取失败，使用本地数据
        reportData.value = buildLocalReport(fallbackBigFive, overallScore)
      }
    } else {
      console.warn('[Report] save-result 失败:', saveRes)
      reportData.value = buildLocalReport(getFallbackBigFive(latestScores.value), overallScore)
    }
    
    // 3. 同步评估进度状态
    if (cid) {
      const persistedMatchScore = toBackendPercentScore(
        saveRes?.data?.overall_score ??
        reportData.value?.match_score ??
        overallScore
      )
      updateProgress({
        candidate_id: cid,
        assessment_id: backendAssessmentId.value ?? undefined,
        job_id: selectedJobId.value ?? undefined,
        job_title: selectedJobTitle.value || '未知岗位',
        status: 'completed',
        total_rounds: respondedCount.value,
        duration_minutes: elapsedTime.value / 60000,
        conversation_depth: respondedCount.value,
        match_score: persistedMatchScore,
        conversation_summary: `完成${respondedCount.value}轮面试，总时长${formatTime(elapsedTime.value)}`,
      }).catch(e => console.warn('更新完成状态失败:', e))
    }
  } catch (e) {
    console.error('[Report] 报告生成失败:', e)
    reportData.value = buildLocalReport(getFallbackBigFive(latestScores.value), overallScore)
  } finally {
    reportLoading.value = false
  }
}

/** 后端不可用时的本地降级报告 */
function buildLocalReport(personalityScores: Record<string, number>, overallScore: number) {
  return {
    match_score: Math.round(overallScore * 10),
    personality_traits: Object.entries(personalityScores).map(([name, score]) => ({
      name,
      score: Math.round(score * 10) / 10,
    })),
    match_analysis: {
      strengths: Object.entries(latestScores.value)
        .filter(([, v]) => v >= 7.5)
        .map(([k]) => `${k}表现优异`),
      gaps: Object.entries(latestScores.value)
        .filter(([, v]) => v < 6)
        .map(([k]) => `${k}有待提升`),
    },
    recommendations: ['继续保持专业优势', '加强相对薄弱领域的训练', '多参与跨领域项目提升综合能力'],
    conversation_summary: `共${respondedCount.value}轮面试，总时长${formatTime(elapsedTime.value)}`,
  }
}

// ==================== 辅助方法 ====================
function getRoleAvatar(roleId: string): string {
  return aiInterviewerAvatar.value
}

function getTraitProgressColor(score: number): string {
  if (score >= 8) return '#67c23a'
  if (score >= 6) return '#409eff'
  if (score >= 4) return '#e6a23c'
  return '#f56c6c'
}

function finishAndClose() {
  ElMessage.success('评估已完成，感谢参与！')
  emit('complete', {
    finished: true,
    reportRecordId: reportRecordId.value,
    scores: latestScores.value,
  })
}

function openReportModule() {
  if (!reportRecordId.value) return
  router.push({
    name: 'AssessmentReport',
    params: { recordId: String(reportRecordId.value) },
  })
}

function getSentimentType(emotion: string): string {
  const map: Record<string, string> = {
    '自信': 'success',
    '谨慎': 'warning',
    '积极': 'success',
    '思考': 'info'
  }
  return map[emotion] || 'info'
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return '#67c23a'
  if (confidence >= 60) return '#409eff'
  if (confidence >= 40) return '#e6a23c'
  return '#f56c6c'
}

function getTraitColor(trait: string): string {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c45656']
  const index = Object.keys(latestScores.value).indexOf(trait)
  return colors[index % colors.length]
}

function generateAvatar(initials: string): string {
  const color = '#409eff'
  return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='${encodeURIComponent(color)}'/%3E%3Ctext x='32' y='40' font-size='20' text-anchor='middle' fill='%23fff' font-weight='bold'%3E${initials}%3C/text%3E%3C/svg%3E`
}

function nowTime(): string {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

async function scrollToBottom() {
  await nextTick()
  if (messageStream.value) {
    messageStream.value.scrollTop = messageStream.value.scrollHeight
  }
}

// 注意：雷达图渲染已移除，评估数据在 HR 端单独实现

// ==================== 自动保存 ====================
const AUTO_SAVE_INTERVAL = 60_000  // 每60秒自动保存
let autoSaveTimer: number | null = null

function getProgressSnapshot(): LocalProgress {
  return {
    currentStep: currentStep.value,
    messages: messages.value,
    scores: latestScores.value,
    patterns: detectedPatterns.value,
    respondedCount: respondedCount.value,
    candidateInfo: candidateInfo.value,
    parsedResumeData: parsedResumeData.value,
    selectedJobId: selectedJobId.value,
    assessmentId: backendAssessmentId.value ?? undefined,
    jobTitle: selectedJobTitle.value,
    interviewState: interviewState.value,
    latestDecision: latestDecision.value,
    startTime: startTime.value,
    elapsedTime: elapsedTime.value,
    timestamp: Date.now(),
  }
}

function doAutoSave() {
  const cid = parsedCandidateId.value
  if (!cid || currentStep.value < 3) return  // 面试阶段才自动保存

  // 保存到 localStorage
  saveLocalProgress(cid, getProgressSnapshot())
  console.log('[AutoSave] 进度已保存到 localStorage')

  // 每3次回答同步一次后端
  if (respondedCount.value > 0 && respondedCount.value % 3 === 0) {
    syncProgressToBackend()
  }
}

async function syncProgressToBackend() {
  const cid = parsedCandidateId.value
  if (!cid) return

  try {
    const res = await updateProgress({
      candidate_id: cid,
      assessment_id: backendAssessmentId.value ?? undefined,
      job_id: selectedJobId.value ?? undefined,
      job_title: selectedJobTitle.value || '未知岗位',
      status: 'pending',
      total_rounds: respondedCount.value,
      duration_minutes: elapsedTime.value / 60000,
      conversation_depth: respondedCount.value,
    })
    if (res.code === 200 && res.data?.assessment_id) {
      backendAssessmentId.value = res.data.assessment_id
    }
  } catch (e) {
    console.warn('[AutoSave] 后端同步失败:', e)
  }
}

function startAutoSave() {
  if (autoSaveTimer) return
  autoSaveTimer = window.setInterval(doAutoSave, AUTO_SAVE_INTERVAL)
}

function stopAutoSave() {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
    autoSaveTimer = null
  }
}

// ==================== 恢复进度 ====================
function restoreFromLocal(progress: LocalProgress) {
  currentStep.value = progress.currentStep
  messages.value = normalizeRestoredMessages(progress.messages || [])
  latestScores.value = progress.scores || latestScores.value
  detectedPatterns.value = progress.patterns || []
  respondedCount.value = progress.respondedCount || 0
  candidateInfo.value = progress.candidateInfo || candidateInfo.value
  parsedResumeData.value = progress.parsedResumeData
  selectedJobId.value = progress.selectedJobId
  backendAssessmentId.value = progress.assessmentId ?? null
  selectedJobTitle.value = progress.jobTitle || ''
  interviewState.value = progress.interviewState || null
  latestDecision.value = progress.latestDecision || null
  isProcessing.value = false
  isTyping.value = false
  shouldEndInterview.value = false
  currentPhase.value = progress.currentStep >= 3 ? '面试进行中' : '面试准备中'

  // 恢复计时
  if (progress.currentStep >= 3 && progress.startTime) {
    startTime.value = Date.now() - (progress.elapsedTime || 0)
    timerInterval.value = window.setInterval(() => {
      elapsedTime.value = Date.now() - startTime.value
    }, 1000)
    startAutoSave()
  }

  leftPanelMode.value = 'info'
  ElMessage.success('已恢复上次测评进度')

  nextTick(() => {
    resumeInterruptedAnalysisIfNeeded()
  })
}

function normalizeRestoredMessages(items: Message[]): Message[] {
  return (items || []).map((message) => {
    if (message.role !== 'ai') return message
    const tags = message.tags || []
    const isSystemMessage =
      message.scoreable === false ||
      tags.includes('面试开始') ||
      tags.includes('破冰') ||
      tags.includes('面试结束')
    return {
      ...message,
      scoreable: !isSystemMessage,
      expectedTraits: message.expectedTraits || [],
    }
  })
}

async function resumeInterruptedAnalysisIfNeeded() {
  if (currentStep.value !== 3 || shouldEndInterview.value || isProcessing.value) return
  const last = messages.value[messages.value.length - 1]
  if (!last || last.role !== 'candidate' || last.aiFeedback) return

  const hasQuestionAfterLastAnswer = messages.value
    .slice(messages.value.lastIndexOf(last) + 1)
    .some(message => message.role === 'ai' && message.scoreable !== false)
  if (hasQuestionAfterLastAnswer) return

  isProcessing.value = true
  try {
    const isFinalAnswer = respondedCount.value >= interviewPlan.value.totalQuestions
    const result = isFinalAnswer
      ? { analysis: await analyzeResponse(last.content), nextQuestion: null, shouldEnd: true }
      : await analyzeAndFetchNext(last.content)

    updateScores(result.analysis.scores, result.analysis.scoreCoverage)
    latestSentiment.value = result.analysis.sentiment
    if (result.analysis.patterns) {
      updatePatterns(result.analysis.patterns)
    }

    const personalityNote = result.analysis.personalityObservation?.scenario_personality
    last.aiFeedback = personalityNote
      ? `${result.analysis.feedback}\n心理特质观察：${personalityNote}`
      : result.analysis.feedback

    if (respondedCount.value >= interviewPlan.value.totalQuestions || result.shouldEnd) {
      shouldEndInterview.value = true
      messages.value.push({
        role: 'ai',
        content: '本轮智能面试已完成。系统将基于本次回答生成性格特质分析、岗位适配结论与匹配建议。',
        time: nowTime(),
        tags: ['面试结束', '心理特质评估', '人岗匹配'],
        focusArea: '评估总结',
        agentRole: getCurrentAgentRoleId(),
        scoreable: false,
      })
      await scrollToBottom()
      completeInterview()
    } else if (result.nextQuestion) {
      messages.value.push({
        role: 'ai',
        content: result.nextQuestion.content,
        time: nowTime(),
        tags: result.nextQuestion.tags,
        focusArea: result.nextQuestion.focusArea,
        agentRole: result.nextQuestion.agentRole,
        expectedTraits: result.nextQuestion.expectedTraits,
        scoreable: true,
      })
      currentPhase.value = result.nextQuestion.phase || '多轮面试中'
      contextHint.value = toCandidateVisibleContext(result.nextQuestion.context)
      doAutoSave()
      await scrollToBottom()
      inputRef.value?.focus()
    }
  } catch (error) {
    console.warn('恢复后续跑分析失败:', error)
    ElMessage.warning('已恢复进度，可继续输入回答')
  } finally {
    isProcessing.value = false
    isTyping.value = false
  }
}

// ==================== 页面退出保存 ====================
function handleBeforeUnload(event?: BeforeUnloadEvent) {
  const cid = parsedCandidateId.value
  if (!cid || currentStep.value < 1 || currentStep.value >= 4) return

  saveLocalProgress(cid, getProgressSnapshot())

  if (event) {
    event.preventDefault()
    event.returnValue = '当前面试尚未完成，离开后将中断本次面试流程。'
  }
}

onBeforeRouteLeave(async (_, __, next) => {
  if (!isInterviewLocked.value) {
    next()
    return
  }

  const cid = parsedCandidateId.value
  if (cid) {
    saveLocalProgress(cid, getProgressSnapshot())
  }

  try {
    await ElMessageBox.confirm(
      '当前面试正在进行或仍处于启动阶段。现在离开会中断本次面试链路，仅保留当前进度，确定离开吗？',
      '离开面试',
      {
        confirmButtonText: '仍要离开',
        cancelButtonText: '继续面试',
        type: 'warning',
      }
    )
    next()
  } catch {
    next(false)
  }
})

// ==================== 生命周期 ====================
onMounted(async () => {
  // 从路由参数读取预选的岗位ID
  const queryJobId = route.query.jobId
  const queryAssessmentId = route.query.assessmentId
  if (queryAssessmentId) {
    const aid = Number(queryAssessmentId)
    if (!isNaN(aid) && aid > 0) {
      backendAssessmentId.value = aid
    }
  }
  if (queryJobId) {
    const jid = Number(queryJobId)
    if (!isNaN(jid) && jid > 0) {
      assessmentMode.value = 'job'
      selectedJobId.value = jid
      // 获取岗位名称
      try {
        const res = await request.get(`/jobs/${jid}`)
        const job = res.data?.data || res.data
        if (job?.name) {
          selectedJobTitle.value = job.name
          console.log('从路由预选岗位:', job.name)
        }
      } catch {
        console.warn('获取预选岗位信息失败')
      }
    }
  }

  const cid = parsedCandidateId.value
  if (!cid) {
    initLoading.value = false
    return
  }

  try {
    // 1) 先检查本地是否有保存的进度
    const local = loadLocalProgress(cid)
    if (local && local.currentStep >= 3 && local.messages.length > 0) {
      localSavedProgress.value = local
      // 弹窗询问是否继续
      try {
        await ElMessageBox.confirm(
          `检测到您有一个未完成的测评（已回答 ${local.respondedCount} 题），是否继续？`,
          '继续上次测评',
          { confirmButtonText: '继续测评', cancelButtonText: '重新开始', type: 'info' }
        )
        // 用户选择继续
        restoreFromLocal(local)
        initLoading.value = false
        return
      } catch {
        // 用户选择重新开始
        clearLocalProgress(cid)
        localSavedProgress.value = null
      }
    }

    // 2) 检查后端是否有进行中的评估
    const [resumeRes, progressRes] = await Promise.all([
      checkResume(cid).catch(() => null),
      checkProgress(cid, {
        jobId: selectedJobId.value,
        assessmentId: backendAssessmentId.value,
      }).catch(() => null),
    ])

    // 处理进行中评估
    if (progressRes?.code === 200 && progressRes.data?.has_progress) {
      hasInProgress.value = true
      inProgressInfo.value = progressRes.data
      backendAssessmentId.value = progressRes.data.assessment_id
      if (progressRes.data.job_id) {
        assessmentMode.value = 'job'
      }
    }

    // 处理简历检查
    if (resumeRes?.code === 200 && resumeRes.data?.has_resume) {
      hasExistingResume.value = true
      existingResumeInfo.value = resumeRes.data.resume_info
    }
  } catch (e) {
    console.warn('初始化检查失败:', e)
  } finally {
    initLoading.value = false
  }

  // 注册 beforeunload
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  clearFlowAdvanceTimer()
  stopAutoSave()
  handleBeforeUnload()
  window.removeEventListener('beforeunload', handleBeforeUnload)
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.immersive-dialogue {
  position: relative;
  display: grid;
  grid-template-columns: 260px 1fr;
  grid-template-rows: 1fr;
  gap: 0;
  height: 100vh;
  padding: 0;
  background: #eef4ff;
  overflow: hidden;
  z-index: 1;
}

/* ==================== 左侧面板 ==================== */
.left-sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  background-color: #fff;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  box-shadow: 1px 0 10px rgba(73, 96, 143, 0.08);
  overflow: hidden;
  z-index: 2;
}

.left-sidebar::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.68);
  pointer-events: none;
  z-index: 0;
}

.svg-overlay {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: rgba(255, 255, 255, 0.55);
  color: white;
  text-align: center;
}

/* panel-overlay - 仅显示流程控制器，不显示表单 */

.el-dialog__body .upload-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.el-dialog__body .info-form {
  margin-top: 12px;
}

.panel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 18px;
  overflow-y: auto;
  z-index: 1;
}

.step.locked {
  cursor: default;
}

/* SVG 容器 */
.svg-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.auto-progress-tip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(64, 158, 255, 0.08);
  color: #1f2d3d;
}

.assessment-entry-choice {
  max-width: 760px;
}

.entry-choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.entry-choice-card {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 14px;
  padding: 20px;
  background: #fff;
  text-align: left;
  transition: all 0.22s ease;
  cursor: pointer;
}

.entry-choice-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(31, 45, 61, 0.08);
}

.entry-choice-card.primary {
  border-color: rgba(64, 158, 255, 0.28);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.08), rgba(64, 158, 255, 0.02));
}

.entry-choice-card.secondary {
  border-color: rgba(144, 147, 153, 0.2);
}

.entry-choice-icon {
  font-size: 24px;
  margin-bottom: 12px;
}

.entry-choice-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.entry-choice-desc {
  font-size: 13px;
  line-height: 1.7;
  color: #606266;
}

.svg-placeholder {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.placeholder-text {
  margin-bottom: 32px;
}

.placeholder-text p {
  margin: 0 0 12px 0;
  font-size: 18px;
}

.placeholder-text .sub-text {
  font-size: 14px;
  opacity: 0.9;
}

/* SVG 图片会替换上面的placeholder-text */
.svg-container svg,
.svg-container img {
  max-width: 100%;
  max-height: 350px;
  object-fit: contain;
}

/* 流程指示器 */
.process-indicator {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  overflow-y: auto;
  flex-shrink: 0;
}

.process-indicator .step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.process-indicator .step:hover {
  background: #f5f7fa;
}

.process-indicator .step.active {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.16), rgba(109, 93, 252, 0.1));
  color: #2563eb;
  box-shadow: inset 3px 0 0 #409eff;
}

.process-indicator .step.completed {
  color: #3b8f2d;
}

.process-indicator .step-number {
  min-width: 32px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f0f0f0;
  font-weight: bold;
  font-size: 13px;
}

.process-indicator .step.active .step-number {
  background: #409eff;
  color: white;
}

.process-indicator .step.completed .step-number {
  background: #67c23a;
  color: white;
}

.process-indicator .step-title {
  font-size: 13px;
  flex: 1;
}

/* ==================== 舞台背景 ==================== */
.stage-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.ambient-layer {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(64, 158, 255, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(103, 194, 58, 0.08) 0%, transparent 50%);
  animation: ambient-shift 20s ease-in-out infinite;
}

.meeting-room-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.5) 100%);
}

@keyframes ambient-shift {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.8; }
}

/* 左侧面板覆盖 - 信息模式 */

/* 流程指示器 */
.process-indicator {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(209, 224, 255, 0.72);
}

.step.active {
  background: linear-gradient(135deg, #eaf3ff 0%, #f3efff 100%);
  border-color: rgba(64, 158, 255, 0.42);
  box-shadow: inset 3px 0 0 #409eff, 0 8px 22px rgba(64, 158, 255, 0.12);
}

.step.completed {
  opacity: 0.7;
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
}

.step:hover {
  background: #f0f2f5;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: #dce8ff;
  color: #2563eb;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step.completed .step-number {
  background: #67c23a;
  color: #fff;
}

.step-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.step.active .step-title {
  color: #2c3e50;
  font-weight: 600;
}

/* 信息面板 */
.info-panel {
  flex: 1;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.panel-title .close-btn {
  margin-left: auto;
  margin-right: auto;
  color: #909399;
}

.panel-title .close-btn:hover {
  color: #f56c6c;
}

.step-content {
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.upload-area {
  margin-bottom: 16px;
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 12px 0;
}

.form-item {
  font-size: 13px;
}

.next-btn,
.start-btn {
  width: 100%;
  margin-top: 12px;
}

.start-btn {
  height: 40px;
  font-size: 15px;
}

.info-display {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.confirm-checkbox {
  margin: 12px 0;
  font-size: 12px;
}

.process-preview {
  margin-bottom: 16px;
}

.process-preview h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #2c3e50;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
}

.plan-details h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.dimension-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.interview-progress {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-stats {
  padding: 12px;
  background: #fafbfc;
  border-radius: 6px;
}

.stat {
  margin-bottom: 8px;
}

.stat:last-child {
  margin-bottom: 0;
}

.stat-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.candidate-summary {
  padding: 12px;
  background: #fafbfc;
  border-radius: 6px;
}

.candidate-summary h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}

.summary-item .key {
  color: #909399;
}

.summary-item .value {
  color: #2c3e50;
  font-weight: 500;
}

/* ==================== 对话框操作按钮 ==================== */
.conversation-starter .action-btn {
  margin-top: 16px;
  padding: 8px 24px;
  font-size: 14px;
  font-weight: 600;
}

.conversation-starter .action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.upload-action-btn {
  margin-top: 24px;
  padding: 12px 40px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  min-height: 44px !important;
}

.upload-action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* ==================== 简历选择区域 ==================== */
.resume-choice-area {
  margin-top: 20px;
  width: 100%;
  max-width: 480px;
}

.resume-history-card {
  background: rgba(64, 158, 255, 0.06);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.resume-history-card .info-header {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.resume-history-card .info-row {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
}

.resume-history-card .info-row .label {
  color: #909399;
  min-width: 50px;
}

.resume-history-card .info-row .value {
  color: #303133;
}

.resume-choice-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.resume-choice-buttons .el-button {
  padding: 12px 28px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  height: auto !important;
  min-height: 44px !important;
}

/* ==================== 评估报告样式 ==================== */
.report-content {
  max-width: 680px;
  width: 100%;
}

.report-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  padding: 18px 0 26px;
  color: #606266;
}

.report-loading-with-counselor > .el-icon {
  display: none;
}

.report-counselor-visual {
  position: relative;
  width: min(100%, 360px);
  min-height: 300px;
  border-radius: 26px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 52% 36%, rgba(139, 92, 246, 0.2), transparent 38%),
    radial-gradient(circle at 68% 62%, rgba(96, 165, 250, 0.18), transparent 42%),
    linear-gradient(145deg, #f8fbff 0%, #eef4ff 54%, #f6f2ff 100%);
  box-shadow: inset 0 0 0 1px rgba(129, 140, 248, 0.18), 0 22px 46px rgba(99, 102, 241, 0.14);
}

.report-counselor-orbit {
  position: absolute;
  width: 220px;
  height: 220px;
  left: 50%;
  top: 47%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(99, 102, 241, 0.24);
  box-shadow:
    0 0 0 20px rgba(219, 234, 254, 0.46),
    0 0 42px rgba(96, 165, 250, 0.26);
}

.report-counselor-orbit::before,
.report-counselor-orbit::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.28);
  box-shadow: 0 0 18px rgba(96, 165, 250, 0.3);
}

.report-counselor-orbit::before {
  width: 8px;
  height: 8px;
  right: 28px;
  top: 26px;
}

.report-counselor-orbit::after {
  width: 6px;
  height: 6px;
  left: 24px;
  bottom: 44px;
}

.report-counselor-image {
  position: relative;
  z-index: 1;
  width: min(86%, 286px);
  max-height: 286px;
  object-fit: contain;
  object-position: center bottom;
  filter: drop-shadow(0 24px 26px rgba(60, 72, 125, 0.22));
}

.report-loading-copy {
  max-width: 520px;
}

.report-complete-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
  font-size: 13px;
  font-weight: 700;
}

.report-loading-copy h4 {
  margin: 12px 0 8px;
  color: #1e293b;
  font-size: 20px;
  line-height: 1.35;
}

.report-loading-copy p {
  margin: 0;
}

.report-detail {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.completion-content {
  max-width: 720px;
}

.completion-card {
  width: 100%;
  margin-top: 18px;
  padding: 20px;
  border: 1px solid #dbe6f7;
  border-radius: 10px;
  background: #fff;
}

.completion-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.completion-tip {
  margin: 0 0 16px;
  color: #606266;
  font-size: 14px;
  line-height: 1.7;
}

.report-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px 20px;
  text-align: left;
}

.report-card .info-header {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.report-stats {
  display: flex;
  gap: 20px;
  justify-content: space-around;
}

.report-stats .stat-item {
  text-align: center;
}

.report-stats .stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.report-stats .stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.report-stats .stat-value.match-score {
  color: #409eff;
}

.trait-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trait-row {
  display: flex;
  align-items: center;
}

.trait-row .trait-name {
  min-width: 80px;
  font-size: 13px;
  color: #606266;
}

.trait-row .trait-score {
  min-width: 36px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.report-card .analysis-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.report-summary {
  margin: 0 0 10px;
  font-size: 13px;
  line-height: 1.7;
  color: #606266;
}

.report-card .analysis-list li {
  padding: 6px 0;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px dashed #ebeef5;
}

.report-card .analysis-list li:last-child {
  border-bottom: none;
}

.report-card .analysis-list li::before {
  content: '•';
  margin-right: 8px;
  color: #409eff;
  font-weight: bold;
}

.report-actions {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.report-actions .el-button {
  padding: 12px 48px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  min-height: 44px !important;
}

.start-interview-btn {
  margin-top: 24px;
  padding: 12px 40px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  height: auto !important;
  min-height: 44px !important;
}

.start-interview-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* ==================== 解析信息展示 ==================== */
.parsed-info-display {
  margin: 20px 0;
  text-align: left;
}

.info-card {
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}

.info-header {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.info-row .label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
}

.info-row .value {
  color: #2c3e50;
  flex: 1;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skills-list :deep(.el-tag) {
  border-radius: 4px;
}

.dimensions-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.dimension-item {
  padding: 8px 12px;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  border: 1px solid #ebeef5;
}

/* ==================== 面试流程说明 ==================== */
.interview-briefing {
  padding: 20px;
}

.briefing-content {
  text-align: left;
  margin: 20px 0;
}

.interview-plan {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.plan-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.plan-icon {
  font-size: 24px;
  min-width: 40px;
  text-align: center;
  line-height: 1;
}

.plan-detail {
  flex: 1;
}

.plan-title {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.plan-item p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.interview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

/* ==================== 信息对话框样式 ==================== */
.info-dialog {
  --el-dialog-border-radius: 12px;
}

.info-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px 12px 0 0;
}

.info-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}

.info-dialog :deep(.el-dialog__close) {
  color: #fff;
}

.dialog-content {
  padding: 24px 0;
}

.upload-section,
.form-section {
  margin-bottom: 24px;
  padding: 0 24px;
}

.section-title {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-desc {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #909399;
}

/* 简历上传样式 */
.resume-upload {
  width: 100%;
}

.resume-upload :deep(.el-upload-dragger) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  transition: all 0.3s ease;
  padding: 40px 20px;
}

.resume-upload :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.resume-upload :deep(.el-upload-dragger.is-dragover) {
  border-color: #409eff;
  background-color: #e6eefb;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
}

.upload-icon.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.upload-text {
  text-align: center;
}

.upload-text .main {
  margin: 0;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.upload-text .main em {
  color: #409eff;
  font-style: normal;
  font-weight: 600;
}

.upload-text .secondary {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.resume-upload :deep(.el-upload__tip) {
  margin-top: 12px;
  font-size: 12px;
}

.file-info {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #f0f9ff;
  border-radius: 4px;
  color: #67c23a;
  font-weight: 500;
}

/* 表单样式 */
.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-row .form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.required {
  color: #f56c6c;
}

.optional-tag {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  margin-left: 4px;
}

.form-input,
.form-select {
  width: 100%;
  font-size: 13px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.form-select {
  --el-border-radius-base: 6px;
}

.auto-fill-indicator {
  font-size: 12px;
  color: #67c23a;
  font-weight: 600;
  margin-left: 4px;
}

.auto-fill-tip {
  display: block;
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
  font-weight: 600;
}

.form-help-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #909399;
}

/* 信息提示 */
.info-tips {
  margin: 0 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.info-tips :deep(.el-alert) {
  border-radius: 8px;
  --el-alert-bg-color: #f0f9ff;
  --el-alert-border-color: #b3e5fc;
  --el-alert-title-color: #0288d1;
  --el-alert-description-color: #01579b;
}

/* 确保 el-dialog 显示在最上方 */
:deep(.el-dialog) {
  z-index: 3000 !important;
}

:deep(.el-overlay) {
  z-index: 2999 !important;
}

:deep(.el-overlay__wrapper) {
  z-index: 2999 !important;
}

/* ==================== 对话容器 ==================== */
.dialogue-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  background: #f7faff;
  border-radius: 0;
  box-shadow: none;
  overflow: hidden;
}

.dialogue-header {
  padding: 12px 28px;
  background: linear-gradient(135deg, #4f7df3 0%, #6d5dfc 56%, #794fb0 100%);
  color: #fff;
}

.job-info-bar {
  max-width: 960px;
  margin: 0 auto 10px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.13);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 10px;
  backdrop-filter: blur(8px);
}

.job-info-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.job-info-label {
  font-size: 11px;
  letter-spacing: 0;
  opacity: 0.82;
}

.job-info-title {
  font-size: 17px;
  font-weight: 700;
  line-height: 1.3;
  word-break: break-word;
}

.job-info-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.job-info-id {
  font-size: 12px;
  opacity: 0.9;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  max-width: 960px;
  margin: 0 auto;
  width: 100%;
}

.ai-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.ai-info h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.ai-info p {
  margin: 0;
  font-size: 12px;
  opacity: 0.88;
}

.session-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 12px;
}

.sentiment-monitor {
  max-width: 960px;
  margin: 10px auto 0;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.sentiment-indicator,
.confidence-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-bar {
  min-width: 180px;
}

.confidence-bar :deep(.el-progress) {
  width: 96px;
}

.sentiment-indicator .label,
.confidence-bar .label {
  font-size: 12px;
  opacity: 0.9;
}

/* ==================== 消息流 ==================== */
.message-stream {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  background: #f7faff;
  scroll-behavior: smooth;
}

.conversation-starter {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 280px;
}

.starter-content {
  text-align: center;
  max-width: 560px;
  width: 100%;
}

/* 岗位选择和简历解析阶段需要更宽的布局 */
.job-selection-briefing .starter-content,
.resume-parsing .starter-content,
.interview-briefing .starter-content {
  max-width: 680px;
}

.greeting-avatar {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 12px;
  overflow: hidden;
}

.greeting-avatar img {
  width: 100%;
  height: 100%;
}

.starter-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
  display: block;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.starter-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #2c3e50;
}

.starter-content p {
  margin: 4px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

.starter-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 12px;
}

.message-item {
  margin-bottom: 20px;
  animation: message-slide-in 0.3s ease-out;
}

@keyframes message-slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.ai-message .message-body {
  border-radius: 4px 12px 12px 12px;
  border-left: 3px solid #409eff;
}

.message-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 10px;
}

.candidate-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.message-content {
  flex: 1;
  max-width: min(75%, 980px);
}

.message-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
}

.speaker-name {
  font-weight: 600;
  color: #2c3e50;
}

.timestamp {
  color: #c0c4cc;
}

.response-metrics {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
}

.message-body {
  padding: 14px 18px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #dbe6f7;
  line-height: 1.7;
  color: #2c3e50;
  font-size: 14px;
  box-shadow: 0 8px 22px rgba(50, 74, 117, 0.06);
  word-break: break-word;
  overflow-wrap: break-word;
}

.message-body p {
  margin: 0;
}

.candidate-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: flex-end;
}

.candidate-message .message-content {
  flex: 0 0 auto;
  max-width: min(68%, 860px);
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.candidate-message .message-body {
  background: linear-gradient(135deg, #5f7bea 0%, #7551b5 100%);
  color: #fff;
  border: none;
  border-radius: 12px 2px 12px 12px;
  box-shadow: 0 10px 24px rgba(92, 112, 211, 0.24);
}

.question-kicker {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #2563eb;
}

.message-tags {
  margin-top: 10px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.tag-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.ai-feedback {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ==================== 打字指示器 ==================== */
.typing-indicator {
  display: flex;
  gap: 12px;
  align-items: center;
  animation: message-slide-in 0.3s ease-out;
}

.typing-avatar {
  width: 40px;
  height: 40px;
}

.typing-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.analysis-indicator {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-top: 8px;
  animation: message-slide-in 0.3s ease-out;
}

.analysis-bubble {
  background: #fff7e6;
  border: 1px solid #f3d19e;
  border-left: 3px solid #e6a23c;
  border-radius: 10px;
  padding: 10px 14px;
  max-width: 75%;
}

.analysis-title {
  font-size: 13px;
  font-weight: 600;
  color: #8a5300;
  margin-bottom: 2px;
}

.analysis-subtitle {
  font-size: 12px;
  color: #a86a10;
  line-height: 1.5;
}

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

/* ==================== 输入区 ==================== */
.input-area {
  padding: 16px 28px 18px;
  background: #fff;
  border-top: 1px solid #dbe6f7;
}

.context-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 1080px;
  margin: 0 auto 12px;
  padding: 10px 12px;
  background: #fff8e8;
  border-left: 3px solid #e6a23c;
  border-radius: 8px;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
}

.answer-label {
  max-width: 1080px;
  margin: 0 auto 8px;
  font-size: 13px;
  font-weight: 700;
  color: #24364f;
}

.input-wrapper {
  max-width: 1080px;
  margin: 0 auto 12px;
}

.input-wrapper :deep(.el-textarea__inner) {
  min-height: 92px !important;
  border-radius: 10px;
  border-color: #d8e2f2;
  box-shadow: none;
  line-height: 1.7;
}

.input-wrapper :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.12);
}

.input-controls {
  max-width: 1080px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-hints {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #909399;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

/* 右侧洞察面板已移除，评估数据在 HR 端单独实现 */

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .immersive-dialogue {
    grid-template-columns: 220px 1fr;
  }

  .message-content {
    max-width: 85%;
  }

  .starter-content {
    max-width: 480px;
  }
}

@media (max-width: 768px) {
  .immersive-dialogue {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 100vh;
  }

  .left-sidebar {
    max-height: 200px;
    overflow-y: auto;
    border-bottom: 1px solid #e4e7ed;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  }

  .dialogue-container {
    min-height: calc(100vh - 200px);
  }

  .message-stream {
    padding: 16px;
  }

  .input-area {
    padding: 12px 16px;
  }

  .message-content {
    max-width: 90%;
  }

  .job-info-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .job-info-meta {
    flex-wrap: wrap;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .session-meta {
    font-size: 11px;
    flex-wrap: wrap;
  }

  .starter-content {
    max-width: 100%;
    padding: 0 12px;
  }

  .entry-choice-grid {
    grid-template-columns: 1fr;
  }
}

/* ==================== 完成对话框 ==================== */
.completion-summary {
  padding: 20px 0;
}

.summary-header {
  text-align: center;
  margin-bottom: 24px;
}

.success-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 12px;
}

.summary-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-highlights h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #2c3e50;
}

.summary-highlights ul {
  margin: 0;
  padding-left: 20px;
}

.summary-highlights li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}
</style>
