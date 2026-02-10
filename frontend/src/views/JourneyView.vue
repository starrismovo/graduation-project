<template>
  <div class="journey-page">
    <!-- 星空背景 -->
    <div class="stars-background">
      <div class="star" v-for="i in 30" :key="i" 
           :style="{
             left: Math.random() * 100 + '%',
             top: Math.random() * 100 + '%',
             animationDelay: Math.random() * 3 + 's'
           }"></div>
    </div>

    <!-- 顶部进度条 -->
    <div class="journey-header">
      <div class="header-content">
        <div class="journey-info">
          <h1 class="journey-title">{{ jobName || '星际探索' }}</h1>
          <div class="chapter-indicator">
            第 {{ activeChapter }}/{{ totalChapters }} 章
          </div>
        </div>
        
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        
        <div class="header-actions">
          <button class="btn-icon" @click="showPauseMenu = true" title="暂停">
            ⏸️
          </button>
          <button class="btn-icon" @click="showAbilityBag = true" title="能力背包">
            💎 {{ abilitiesCollected.length }}
          </button>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="journey-main">
      <!-- 左侧：虚拟形象 -->
      <div class="avatar-section">
        <div class="avatar-container">
          <div class="avatar-display" :class="avatarEmotion">
            <div class="avatar-image">
              {{ avatarEmoji }}
            </div>
            <div class="avatar-name">探险家</div>
          </div>
          
          <!-- 能力收集提示 -->
          <transition name="ability-collect">
            <div v-if="showAbilityCollect" class="ability-collect-popup">
              <div class="popup-icon">✨</div>
              <div class="popup-text">
                <div class="popup-title">能力发现！</div>
                <div class="popup-ability">{{ latestAbility }}</div>
              </div>
            </div>
          </transition>
        </div>
        
        <!-- 已收集能力列表 -->
        <div class="abilities-collected">
          <div class="abilities-header">
            <span>已发现能力</span>
            <el-tag size="small" type="success">{{ abilitiesCollected.length }}</el-tag>
          </div>
          <div class="abilities-list">
            <div 
              v-for="ability in abilitiesCollected" 
              :key="ability.id"
              class="ability-gem"
              :title="ability.description"
            >
              <span class="gem-icon">💎</span>
              <span class="gem-name">{{ ability.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：故事场景 -->
      <div class="story-section">
        <el-card class="story-card">
          <!-- 章节标题 -->
          <div class="chapter-header">
            <h2 class="chapter-title">{{ currentChapter.title }}</h2>
            <div class="chapter-subtitle">{{ currentChapter.subtitle }}</div>
          </div>

          <!-- 场景插图（可选） -->
          <div v-if="currentScene.illustration" class="scene-illustration">
            <div class="illustration-placeholder">
              {{ currentScene.illustration }}
            </div>
          </div>

          <!-- 故事内容区 -->
          <div class="story-content">
            <!-- 旁白/叙述 -->
            <div v-if="currentScene.type === 'narration'" class="narration">
              <div class="narration-icon">📖</div>
              <div class="narration-text" v-html="formatText(currentScene.content)"></div>
              <div class="narration-actions">
                <el-button type="primary" @click="nextScene">
                  继续 →
                </el-button>
              </div>
            </div>

            <!-- 对话场景 -->
            <div v-else-if="currentScene.type === 'dialogue'" class="dialogue">
              <div class="dialogue-messages">
                <div 
                  v-for="(msg, idx) in currentScene.messages" 
                  :key="idx"
                  class="message-bubble"
                  :class="msg.speaker === 'npc' ? 'npc-message' : 'player-message'"
                >
                  <div class="message-speaker">{{ msg.speakerName }}</div>
                  <div class="message-text">{{ msg.text }}</div>
                </div>
              </div>
              <div class="dialogue-actions">
                <el-button type="primary" @click="nextScene">
                  继续对话 →
                </el-button>
              </div>
            </div>

            <!-- 选择场景（核心评估） -->
            <div v-else-if="currentScene.type === 'choice'" class="choice-scene">
              <div class="choice-question">
                <div class="question-icon">🤔</div>
                <div class="question-text">{{ currentScene.question }}</div>
              </div>

              <div class="choice-options">
                <div 
                  v-for="option in currentScene.options" 
                  :key="option.id"
                  class="choice-option"
                  :class="{ selected: selectedOption === option.id, disabled: isProcessing }"
                  @click="selectOption(option)"
                >
                  <div class="option-icon">{{ option.icon || '●' }}</div>
                  <div class="option-content">
                    <div class="option-text">{{ option.text }}</div>
                    <div v-if="option.hint" class="option-hint">{{ option.hint }}</div>
                  </div>
                </div>
              </div>

              <div v-if="selectedOption" class="choice-actions">
                <el-button type="primary" @click="confirmChoice" :loading="isProcessing">
                  确认选择
                </el-button>
              </div>
            </div>

            <!-- 小游戏场景（认知任务） -->
            <div v-else-if="currentScene.type === 'game'" class="game-scene">
              <div class="game-header">
                <h3>{{ currentScene.gameTitle }}</h3>
                <p>{{ currentScene.gameDescription }}</p>
              </div>
              
              <div class="game-container">
                <!-- 根据游戏类型渲染不同组件 -->
                <component 
                  :is="getGameComponent(currentScene.gameType)" 
                  @complete="handleGameComplete"
                />
              </div>
            </div>

            <!-- 反馈场景 -->
            <div v-else-if="currentScene.type === 'feedback'" class="feedback-scene">
              <div class="feedback-icon">✨</div>
              <div class="feedback-content">
                <h3>{{ currentScene.feedbackTitle }}</h3>
                <div class="feedback-text" v-html="formatText(currentScene.feedbackText)"></div>
                
                <!-- 能力展示 -->
                <div v-if="currentScene.abilitiesRevealed" class="abilities-revealed">
                  <div class="revealed-title">你展现了以下能力：</div>
                  <div class="revealed-list">
                    <div 
                      v-for="ability in currentScene.abilitiesRevealed" 
                      :key="ability"
                      class="revealed-item"
                    >
                      <span class="revealed-icon">💎</span>
                      <span class="revealed-name">{{ ability }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="feedback-actions">
                <el-button type="primary" @click="nextScene">
                  继续探索 →
                </el-button>
              </div>
            </div>

            <!-- 章节完成 -->
            <div v-else-if="currentScene.type === 'chapter_end'" class="chapter-end">
              <div class="end-icon">🎉</div>
              <h2>章节完成！</h2>
              <div class="end-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ currentChapterAbilities.length }}</div>
                  <div class="stat-label">本章发现能力</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ abilitiesCollected.length }}</div>
                  <div class="stat-label">累计发现能力</div>
                </div>
              </div>
              <div class="end-actions">
                <el-button type="primary" size="large" @click="nextChapter">
                  {{ activeChapter < totalChapters ? '进入下一章 →' : '完成探索 🎊' }}
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 暂停菜单弹窗 -->
    <el-dialog v-model="showPauseMenu" title="暂停探索" width="400px">
      <div class="pause-menu">
        <p>你可以随时继续探索，进度已自动保存。</p>
        <div class="pause-actions">
          <el-button @click="showPauseMenu = false">继续探索</el-button>
          <el-button @click="saveAndExit">保存并退出</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 能力背包弹窗 -->
    <el-dialog v-model="showAbilityBag" title="能力背包" width="500px">
      <div class="ability-bag">
        <div v-if="abilitiesCollected.length === 0" class="empty-bag">
          <p>还没有发现任何能力，继续探索吧！</p>
        </div>
        <div v-else class="bag-grid">
          <div 
            v-for="ability in abilitiesCollected" 
            :key="ability.id"
            class="bag-item"
          >
            <div class="bag-icon">💎</div>
            <div class="bag-info">
              <div class="bag-name">{{ ability.name }}</div>
              <div class="bag-desc">{{ ability.description }}</div>
              <div class="bag-scene">发现于：{{ ability.scene }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 岗位信息
const jobId = computed(() => route.params.id)
const jobName = ref('前端工程师')

// 章节与场景管理
const activeChapter = ref(1)
const totalChapters = ref(5)
const activeScene = ref(0)

// 当前章节和场景数据
const currentChapter = ref({
  id: 'ch1',
  title: '第一章：初入团队',
  subtitle: '新的开始',
  scenes: []
})

const currentScene = ref({
  type: 'narration',
  content: '加载中...'
})

// 用户状态
const selectedOption = ref<string | null>(null)
const isProcessing = ref(false)
const abilitiesCollected = ref<any[]>([])
const currentChapterAbilities = ref<any[]>([])

// UI 状态
const showPauseMenu = ref(false)
const showAbilityBag = ref(false)
const showAbilityCollect = ref(false)
const latestAbility = ref('')

// 虚拟形象
const avatarEmoji = ref('👤')
const avatarEmotion = ref('neutral') // neutral, happy, thinking, surprised

// 进度计算
const progressPercentage = computed(() => {
  const totalScenes = currentChapter.value.scenes.length
  if (totalScenes === 0) return 0
  return Math.round((activeScene.value / totalScenes) * 100)
})

// 加载故事数据
const loadStoryData = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在进入星际航程...',
    background: 'rgba(0, 0, 0, 0.7)'
  })

  try {
    // 模拟从后端或本地加载故事数据
    // 实际应该调用 API: const response = await getStoryTemplate(jobId.value)
    
    // 这里使用硬编码的演示数据
    const storyData = getStoryTemplate(jobId.value as string)
    
    currentChapter.value = storyData.chapters[0]
    currentScene.value = currentChapter.value.scenes[0]
    
    // 根据岗位设置名称
    jobName.value = storyData.jobName
    
  } catch (error) {
    console.error('加载故事失败:', error)
    ElMessage.error('加载探索内容失败，请重试')
  } finally {
    loading.close()
  }
}

// 下一个场景
const nextScene = () => {
  const scenes = currentChapter.value.scenes
  
  if (activeScene.value < scenes.length - 1) {
    activeScene.value++
    currentScene.value = scenes[activeScene.value]
    
    // 更新虚拟形象表情
    updateAvatarEmotion()
  } else {
    // 章节结束
    currentScene.value = {
      type: 'chapter_end'
    }
  }
}

// 选择选项
const selectOption = (option: any) => {
  if (isProcessing.value) return
  selectedOption.value = option.id
}

// 确认选择
const confirmChoice = async () => {
  if (!selectedOption.value) return
  
  isProcessing.value = true
  
  const option = currentScene.value.options.find((opt: any) => opt.id === selectedOption.value)
  
  // 显示即时反馈
  if (option.feedback) {
    ElMessage.success(option.feedback)
  }
  
  // 收集能力
  if (option.abilitiesRevealed && option.abilitiesRevealed.length > 0) {
    option.abilitiesRevealed.forEach((abilityName: string) => {
      const ability = {
        id: Date.now() + Math.random(),
        name: abilityName,
        description: getAbilityDescription(abilityName),
        scene: currentChapter.value.title
      }
      
      abilitiesCollected.value.push(ability)
      currentChapterAbilities.value.push(ability)
      
      // 显示能力收集动画
      showAbilityCollectAnimation(abilityName)
    })
  }
  
  // 模拟AI分析延迟
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  // 跳转到反馈场景或下一场景
  if (option.feedbackScene) {
    currentScene.value = option.feedbackScene
  } else {
    nextScene()
  }
  
  selectedOption.value = null
  isProcessing.value = false
}

// 显示能力收集动画
const showAbilityCollectAnimation = (abilityName: string) => {
  latestAbility.value = abilityName
  showAbilityCollect.value = true
  
  setTimeout(() => {
    showAbilityCollect.value = false
  }, 3000)
}

// 更新虚拟形象表情
const updateAvatarEmotion = () => {
  if (currentScene.value.type === 'choice') {
    avatarEmotion.value = 'thinking'
  } else if (currentScene.value.type === 'feedback') {
    avatarEmotion.value = 'happy'
  } else {
    avatarEmotion.value = 'neutral'
  }
}

// 下一章节
const nextChapter = () => {
  if (activeChapter.value < totalChapters.value) {
    activeChapter.value++
    activeScene.value = 0
    currentChapterAbilities.value = []
    
    // 加载新章节数据
    const storyData = getStoryTemplate(jobId.value as string)
    currentChapter.value = storyData.chapters[activeChapter.value - 1]
    currentScene.value = currentChapter.value.scenes[0]
    
    ElMessage.success(`进入第 ${activeChapter.value} 章`)
  } else {
    // 完成所有章节，跳转到报告页
    completeJourney()
  }
}

// 完成探索
const completeJourney = () => {
  ElMessage.success('🎉 探索完成！正在生成你的星际航行日志...')
  
  setTimeout(() => {
    router.push({
      name: 'JourneyReport',
      params: { jobId: jobId.value },
      query: { abilities: JSON.stringify(abilitiesCollected.value) }
    })
  }, 2000)
}

// 保存并退出
const saveAndExit = () => {
  // 保存进度到本地或后端
  const progress = {
    jobId: jobId.value,
    activeChapter: activeChapter.value,
    activeScene: activeScene.value,
    abilities: abilitiesCollected.value
  }
  
  localStorage.setItem(`journey_${jobId.value}`, JSON.stringify(progress))
  
  ElMessage.success('进度已保存')
  router.push('/home')
}

// 小游戏完成
const handleGameComplete = (result: any) => {
  ElMessage.success('任务完成！')
  
  // 根据游戏结果收集能力
  if (result.abilities) {
    result.abilities.forEach((abilityName: string) => {
      const ability = {
        id: Date.now() + Math.random(),
        name: abilityName,
        description: getAbilityDescription(abilityName),
        scene: currentChapter.value.title
      }
      abilitiesCollected.value.push(ability)
    })
  }
  
  nextScene()
}

// 获取游戏组件
const getGameComponent = (gameType: string) => {
  // 根据游戏类型返回对应的组件
  // 这里简化处理，实际应该动态导入
  return 'div' // 占位
}

// 格式化文本（支持简单的 markdown）
const formatText = (text: string) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

// 获取能力描述
const getAbilityDescription = (abilityName: string): string => {
  const descriptions: Record<string, string> = {
    '沟通能力': '你善于表达想法，能够清晰地与他人交流',
    '主动性': '你主动承担责任，不等待别人的指示',
    '观察力': '你能够注意到细节，发现问题的关键',
    '逻辑思维': '你能够系统地分析问题，找到解决方案',
    '团队协作': '你善于与团队成员合作，共同达成目标',
    '问题解决': '你能够快速定位问题并提出有效的解决方案',
    '抗压能力': '你在压力下能够保持冷静，做出理性决策',
    '创新思维': '你能够提出新颖的想法和解决方案',
    '学习能力': '你善于快速学习新知识和技能',
    '同理心': '你能够理解他人的感受和立场'
  }
  
  return descriptions[abilityName] || '一项重要的职场能力'
}

// 获取故事模板（演示数据）
const getStoryTemplate = (jobId: string) => {
  // 这里返回硬编码的故事数据
  // 实际应该从后端获取或从 JSON 文件加载
  
  return {
    jobId: jobId,
    jobName: '前端工程师',
    chapters: [
      {
        id: 'ch1',
        title: '第一章：初入团队',
        subtitle: '新的开始',
        scenes: [
          {
            type: 'narration',
            content: '2156年，星际时代已经到来。\n\n你作为一名新加入的**前端工程师**，第一次登上了银河联盟的星际飞船"探索者号"。飞船的控制室里，全息屏幕显示着复杂的星图，团队成员们正专注于各自的工作站。\n\n这是你职业生涯的全新篇章。'
          },
          {
            type: 'dialogue',
            messages: [
              {
                speaker: 'npc',
                speakerName: '船长',
                text: '欢迎加入我们的团队！我是船长艾莉娜。你就是新来的前端工程师吧？'
              },
              {
                speaker: 'player',
                speakerName: '你',
                text: '是的，船长。很高兴能加入探索者号。'
              },
              {
                speaker: 'npc',
                speakerName: '船长',
                text: '很好。团队成员都在忙碌中，你可以先熟悉一下环境。'
              }
            ]
          },
          {
            type: 'choice',
            question: '控制室里有5位同事正专注于各自的屏幕。你会如何开始你的第一天？',
            options: [
              {
                id: 'opt1',
                icon: '👋',
                text: '主动向大家问好并介绍自己',
                hint: '展现你的社交能力',
                abilitiesRevealed: ['沟通能力', '主动性'],
                feedback: '你的主动让团队印象深刻！',
                feedbackScene: {
                  type: 'feedback',
                  feedbackTitle: '很好的开始！',
                  feedbackText: '你主动的问候打破了陌生感，团队成员们纷纷欢迎你的加入。船长微笑着点了点头。',
                  abilitiesRevealed: ['沟通能力', '主动性']
                }
              },
              {
                id: 'opt2',
                icon: '👀',
                text: '先观察一会儿，了解团队的工作节奏',
                hint: '细致的观察也很重要',
                abilitiesRevealed: ['观察力', '谨慎'],
                feedback: '你细致的观察展现了周全的考虑',
                feedbackScene: {
                  type: 'feedback',
                  feedbackTitle: '细心的开始',
                  feedbackText: '通过观察，你注意到团队的工作流程非常有序。每个人都有明确的分工，这让你对接下来的工作有了更清晰的认识。',
                  abilitiesRevealed: ['观察力']
                }
              },
              {
                id: 'opt3',
                icon: '💻',
                text: '直接走到工作台开始熟悉代码',
                hint: '行动派的选择',
                abilitiesRevealed: ['主动性', '学习能力'],
                feedback: '你的行动力令人印象深刻',
                feedbackScene: {
                  type: 'feedback',
                  feedbackTitle: '雷厉风行',
                  feedbackText: '你快速地打开代码仓库，开始浏览项目结构。技术主管注意到了你的主动，走过来表示可以随时提问。',
                  abilitiesRevealed: ['主动性', '学习能力']
                }
              }
            ]
          },
          {
            type: 'narration',
            content: '随着你融入团队，船长分配给你第一个任务：检查飞船控制台的前端界面，确保所有系统正常运行。\n\n这看似简单的任务，却是你展现专业能力的第一次机会。'
          }
        ]
      },
      {
        id: 'ch2',
        title: '第二章：技术挑战',
        subtitle: '突发危机',
        scenes: [
          {
            type: 'narration',
            content: '就在你熟悉控制台界面的时候，突然——\n\n**警报声响起！**\n\n主控制台的屏幕闪烁后黑屏了。整个控制室陷入了紧张的气氛。'
          },
          {
            type: 'dialogue',
            messages: [
              {
                speaker: 'npc',
                speakerName: '船长',
                text: '怎么回事？！控制台不能失灵！'
              },
              {
                speaker: 'npc',
                speakerName: '技术主管',
                text: '是前端界面出了问题。新来的工程师，你能处理吗？'
              }
            ]
          },
          {
            type: 'choice',
            question: '控制台突然黑屏，作为前端工程师，你的第一步会是什么？',
            options: [
              {
                id: 'opt1',
                icon: '🔍',
                text: '立即打开开发者工具查看控制台错误',
                hint: '技术导向的方法',
                abilitiesRevealed: ['逻辑思维', '问题解决'],
                feedback: '专业的诊断方式！'
              },
              {
                id: 'opt2',
                icon: '💬',
                text: '先询问其他人刚才做了什么操作',
                hint: '信息收集的方法',
                abilitiesRevealed: ['沟通能力', '系统思维'],
                feedback: '全面的信息收集很重要'
              },
              {
                id: 'opt3',
                icon: '⚡',
                text: '检查网络连接和服务器状态',
                hint: '排除硬件问题',
                abilitiesRevealed: ['系统思维', '问题解决'],
                feedback: '系统化的排查思路'
              }
            ]
          }
        ]
      }
    ]
  }
}

// 监听场景变化，更新表情
watch(currentScene, () => {
  updateAvatarEmotion()
})

onMounted(() => {
  loadStoryData()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Space+Mono:wght@400;700&display=swap');

* {
  box-sizing: border-box;
}

.journey-page {
  min-height: 100vh;
  background: #0a0e27;
  color: #e0e6ed;
  position: relative;
  overflow-x: hidden;
  font-family: 'Space Mono', monospace;
}

/* 星空背景 */
.stars-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* 顶部导航 */
.journey-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(167, 139, 250, 0.2);
  padding: 16px 24px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.journey-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.journey-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  margin: 0;
  color: #a78bfa;
}

.chapter-indicator {
  padding: 4px 12px;
  background: rgba(167, 139, 250, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #ec4899);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-icon {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Space Mono', monospace;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 主内容区 */
.journey-main {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

/* 左侧虚拟形象区 */
.avatar-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-container {
  position: relative;
}

.avatar-display {
  background: rgba(30, 41, 59, 0.6);
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
}

.avatar-display.happy {
  border-color: rgba(34, 197, 94, 0.5);
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.2);
}

.avatar-display.thinking {
  border-color: rgba(236, 72, 153, 0.5);
  box-shadow: 0 0 30px rgba(236, 72, 153, 0.2);
}

.avatar-image {
  font-size: 80px;
  margin-bottom: 12px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.avatar-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  color: #a78bfa;
}

/* 能力收集弹窗 */
.ability-collect-popup {
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  padding: 12px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 30px rgba(167, 139, 250, 0.5);
  animation: popup 0.5s ease;
}

@keyframes popup {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

.ability-collect-enter-active,
.ability-collect-leave-active {
  transition: all 0.5s ease;
}

.ability-collect-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.8);
}

.ability-collect-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px) scale(0.8);
}

.popup-icon {
  font-size: 24px;
}

.popup-title {
  font-weight: 700;
  font-size: 12px;
  margin-bottom: 2px;
}

.popup-ability {
  font-size: 14px;
  font-weight: 700;
}

/* 已收集能力 */
.abilities-collected {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  padding: 16px;
  backdrop-filter: blur(20px);
}

.abilities-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 700;
  font-size: 12px;
}

.abilities-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.ability-gem {
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.ability-gem:hover {
  background: rgba(167, 139, 250, 0.2);
  border-color: rgba(167, 139, 250, 0.5);
  transform: translateX(4px);
}

.gem-icon {
  font-size: 16px;
}

.gem-name {
  font-weight: 600;
}

/* 右侧故事区 */
.story-section {
  min-height: 600px;
}

.story-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 20px;
  backdrop-filter: blur(20px);
}

.story-card :deep(.el-card__body) {
  padding: 32px;
}

/* 章节标题 */
.chapter-header {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid rgba(167, 139, 250, 0.2);
}

.chapter-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 28px;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.chapter-subtitle {
  font-size: 14px;
  color: #94a3b8;
}

/* 场景插图 */
.scene-illustration {
  margin-bottom: 24px;
  text-align: center;
}

.illustration-placeholder {
  height: 200px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(236, 72, 153, 0.1));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
}

/* 故事内容 */
.story-content {
  min-height: 300px;
}

/* 旁白 */
.narration {
  padding: 24px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  border-left: 4px solid #a78bfa;
}

.narration-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.narration-text {
  font-size: 15px;
  line-height: 1.8;
  color: #cbd5e1;
  margin-bottom: 24px;
}

.narration-text :deep(strong) {
  color: #a78bfa;
  font-weight: 700;
}

.narration-actions {
  text-align: right;
}

/* 对话 */
.dialogue {
  padding: 24px;
}

.dialogue-messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.message-bubble {
  padding: 16px;
  border-radius: 12px;
  max-width: 80%;
}

.npc-message {
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  align-self: flex-start;
}

.player-message {
  background: rgba(236, 72, 153, 0.1);
  border: 1px solid rgba(236, 72, 153, 0.3);
  align-self: flex-end;
}

.message-speaker {
  font-size: 12px;
  font-weight: 700;
  color: #a78bfa;
  margin-bottom: 6px;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  color: #cbd5e1;
}

.dialogue-actions {
  text-align: right;
}

/* 选择场景 */
.choice-scene {
  padding: 24px;
}

.choice-question {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  padding: 20px;
  background: rgba(167, 139, 250, 0.05);
  border-radius: 12px;
  border-left: 4px solid #a78bfa;
}

.question-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  color: #e0e6ed;
  font-weight: 600;
}

.choice-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.choice-option {
  padding: 20px;
  background: rgba(30, 41, 59, 0.4);
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  display: flex;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.choice-option:hover:not(.disabled) {
  background: rgba(167, 139, 250, 0.1);
  border-color: rgba(167, 139, 250, 0.5);
  transform: translateX(8px);
}

.choice-option.selected {
  background: rgba(167, 139, 250, 0.2);
  border-color: #a78bfa;
  box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3);
}

.choice-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.option-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.option-content {
  flex: 1;
}

.option-text {
  font-size: 15px;
  line-height: 1.6;
  color: #e0e6ed;
  margin-bottom: 6px;
  font-weight: 600;
}

.option-hint {
  font-size: 12px;
  color: #94a3b8;
  font-style: italic;
}

.choice-actions {
  text-align: right;
}

/* 反馈场景 */
.feedback-scene {
  padding: 32px;
  text-align: center;
}

.feedback-icon {
  font-size: 64px;
  margin-bottom: 24px;
  animation: bounce 1s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.feedback-content h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  margin-bottom: 16px;
  color: #a78bfa;
}

.feedback-text {
  font-size: 15px;
  line-height: 1.8;
  color: #cbd5e1;
  margin-bottom: 24px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.abilities-revealed {
  margin: 24px 0;
  padding: 20px;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 12px;
}

.revealed-title {
  font-size: 14px;
  font-weight: 700;
  color: #a78bfa;
  margin-bottom: 12px;
}

.revealed-list {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.revealed-item {
  padding: 8px 16px;
  background: rgba(167, 139, 250, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.revealed-icon {
  font-size: 18px;
}

.feedback-actions {
  margin-top: 24px;
}

/* 章节完成 */
.chapter-end {
  padding: 48px 32px;
  text-align: center;
}

.end-icon {
  font-size: 80px;
  margin-bottom: 24px;
  animation: celebrate 1s ease;
}

@keyframes celebrate {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.2) rotate(-10deg); }
  75% { transform: scale(1.2) rotate(10deg); }
}

.chapter-end h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  margin-bottom: 32px;
  background: linear-gradient(135deg, #a78bfa, #ec4899, #f59e0b);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.end-stats {
  display: flex;
  gap: 48px;
  justify-content: center;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 48px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  color: #a78bfa;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8;
}

.end-actions {
  margin-top: 32px;
}

/* 弹窗 */
.pause-menu {
  text-align: center;
  padding: 20px;
}

.pause-menu p {
  margin-bottom: 24px;
  color: #666;
}

.pause-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.ability-bag {
  padding: 20px;
}

.empty-bag {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.bag-grid {
  display: grid;
  gap: 16px;
}

.bag-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(167, 139, 250, 0.05);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.bag-item:hover {
  background: rgba(167, 139, 250, 0.1);
  border-color: rgba(167, 139, 250, 0.4);
}

.bag-icon {
  font-size: 32px;
}

.bag-info {
  flex: 1;
}

.bag-name {
  font-weight: 700;
  font-size: 16px;
  color: #333;
  margin-bottom: 6px;
}

.bag-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  line-height: 1.5;
}

.bag-scene {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

/* 响应式 */
@media (max-width: 1024px) {
  .journey-main {
    grid-template-columns: 1fr;
  }
  
  .avatar-section {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
  }
  
  .progress-bar {
    width: 100%;
    order: 3;
  }
  
  .journey-main {
    padding: 16px;
  }
  
  .story-card :deep(.el-card__body) {
    padding: 20px;
  }
  
  .choice-option {
    flex-direction: column;
    text-align: center;
  }
}
</style>