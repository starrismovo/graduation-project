<template>
  <div class="login-page">
    <section class="brand-section" aria-label="AI 人岗评估系统介绍">
      <div class="brand-shell">
        <header class="brand-header">
          <div class="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 48 48">
              <rect width="48" height="48" rx="12" fill="url(#markGradient)" />
              <path d="M17 22.5c0-4.1 3.1-7.5 7-7.5s7 3.4 7 7.5v5c0 4.1-3.1 7.5-7 7.5s-7-3.4-7-7.5v-5Z" fill="none" stroke="white" stroke-width="2.2" />
              <path d="M24 15v-4" stroke="white" stroke-width="2.2" stroke-linecap="round" />
              <circle cx="24" cy="9" r="2.2" fill="white" />
              <circle cx="21" cy="25" r="1.8" fill="white" />
              <circle cx="27" cy="25" r="1.8" fill="white" />
              <path d="M12 25h-2.5M38.5 25H36" stroke="white" stroke-width="2.2" stroke-linecap="round" />
              <defs>
                <linearGradient id="markGradient" x1="6" x2="42" y1="5" y2="43">
                  <stop stop-color="#5c72ff" />
                  <stop offset="1" stop-color="#8d52ff" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <h1>AI 人岗评估系统</h1>
            <p>基于 AI 智能体的科学评估与精准匹配平台</p>
          </div>
        </header>

        <div class="hero-copy">
          <h2>
            让人才与岗位
            <span>更智能地相遇</span>
          </h2>
          <div class="hero-rule" aria-hidden="true"></div>
          <p>AI 驱动的人岗评估，助力组织高效决策与人才发展</p>
        </div>

        <div class="ai-stage" aria-hidden="true">
          <div class="stage-halo"></div>
          <svg class="ai-illustration" viewBox="0 0 620 440" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="glassFill" x1="0" x2="1" y1="0" y2="1">
                <stop stop-color="#ffffff" stop-opacity=".92" />
                <stop offset=".48" stop-color="#f6f3ff" stop-opacity=".64" />
                <stop offset="1" stop-color="#e9e4ff" stop-opacity=".24" />
              </linearGradient>
              <linearGradient id="purpleStroke" x1="67" x2="541" y1="85" y2="386">
                <stop stop-color="#f6f4ff" />
                <stop offset=".48" stop-color="#a59bff" />
                <stop offset="1" stop-color="#6d60f5" />
              </linearGradient>
              <linearGradient id="robotBody" x1="252" x2="388" y1="200" y2="362">
                <stop stop-color="#ffffff" />
                <stop offset=".55" stop-color="#eceeff" />
                <stop offset="1" stop-color="#cbcfff" />
              </linearGradient>
              <linearGradient id="helmetGloss" x1="278" x2="372" y1="165" y2="234">
                <stop stop-color="#ffffff" />
                <stop offset=".64" stop-color="#f0f2ff" />
                <stop offset="1" stop-color="#d5d9ff" />
              </linearGradient>
              <linearGradient id="visorFill" x1="272" x2="368" y1="184" y2="229">
                <stop stop-color="#17246b" />
                <stop offset=".6" stop-color="#111b58" />
                <stop offset="1" stop-color="#29368a" />
              </linearGradient>
              <linearGradient id="eyeGlow" x1="0" x2="1" y1="0" y2="1">
                <stop stop-color="#8af6ff" />
                <stop offset=".58" stop-color="#45dfff" />
                <stop offset="1" stop-color="#5d8cff" />
              </linearGradient>
              <linearGradient id="baseTop" x1="187" x2="444" y1="337" y2="406">
                <stop stop-color="#fdfdff" />
                <stop offset=".53" stop-color="#dddfff" />
                <stop offset="1" stop-color="#776bf4" />
              </linearGradient>
              <linearGradient id="baseRim" x1="204" x2="436" y1="344" y2="385">
                <stop stop-color="#bbb6ff" />
                <stop offset=".4" stop-color="#7e72f6" />
                <stop offset="1" stop-color="#5649db" />
              </linearGradient>
              <linearGradient id="tabletFill" x1="279" x2="361" y1="278" y2="334">
                <stop stop-color="#8c83ff" />
                <stop offset=".58" stop-color="#776bf4" />
                <stop offset="1" stop-color="#5d52dd" />
              </linearGradient>
              <filter id="softShadow" x="-30%" y="-40%" width="160%" height="180%">
                <feDropShadow dx="0" dy="24" stdDeviation="20" flood-color="#685cf0" flood-opacity=".26" />
              </filter>
              <filter id="glassShadow" x="-30%" y="-30%" width="160%" height="170%">
                <feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#7770ff" flood-opacity=".16" />
              </filter>
              <filter id="cardBlur" x="-18%" y="-18%" width="136%" height="136%">
                <feGaussianBlur stdDeviation=".35" />
                <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#7568f2" flood-opacity=".12" />
              </filter>
              <filter id="eyeSoftGlow" x="-90%" y="-120%" width="280%" height="340%">
                <feGaussianBlur stdDeviation="2.4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <radialGradient id="screenGlow" cx=".5" cy=".55" r=".65">
                <stop stop-color="#4fdcff" stop-opacity=".8" />
                <stop offset="1" stop-color="#4f46e5" stop-opacity="0" />
              </radialGradient>
              <radialGradient id="baseGlow" cx=".5" cy=".45" r=".7">
                <stop stop-color="#ffffff" stop-opacity=".95" />
                <stop offset=".46" stop-color="#e6e4ff" stop-opacity=".86" />
                <stop offset="1" stop-color="#7368f4" stop-opacity=".22" />
              </radialGradient>
            </defs>

            <ellipse class="orbit-ring outer-ring" cx="319" cy="382" rx="305" ry="53" stroke="url(#purpleStroke)" stroke-opacity=".34" stroke-width="1.6" />
            <ellipse class="orbit-ring inner-ring" cx="318" cy="370" rx="198" ry="40" fill="#e9e8ff" opacity=".5" />
            <ellipse cx="320" cy="375" rx="132" ry="29" fill="#b2aaff" opacity=".14" />

            <g class="panel-main" filter="url(#cardBlur)" opacity=".9">
              <path d="M145 82c0-18.8 15.8-33.3 34.6-31.7l179.8 15.8c17 1.5 30.1 15.7 30.1 32.8v88.2c0 18.8-15.8 33.3-34.6 31.7L175.1 203c-17-1.5-30.1-15.7-30.1-32.8V82Z" fill="url(#glassFill)" stroke="white" stroke-width="2.4" />
              <path d="M153 84c0-13.7 11.5-24.3 25.1-23.1l179.8 15.8c12.4 1.1 22.1 11.5 22.1 24v82.6" stroke="#ffffff" stroke-opacity=".42" stroke-width="2" />
              <rect x="171" y="98" width="148" height="66" rx="16" fill="white" fill-opacity=".76" stroke="#ddd9ff" />
              <circle cx="199" cy="127" r="9" fill="#7566f6" />
              <path d="M180 151c2.5-12 11.8-18.8 22-18.8 10.1 0 19.5 6.8 22 18.8H180Z" fill="#7566f6" opacity=".9" />
              <rect x="236" y="115" width="42" height="6" rx="3" fill="#c9c5fb" />
              <rect x="236" y="132" width="75" height="6" rx="3" fill="#d9d6ff" />
              <rect x="236" y="148" width="54" height="6" rx="3" fill="#d9d6ff" />
              <path d="M342 154c10-18 17-38 23-62 6 28 13 45 23 63" stroke="#edeaff" stroke-width="9" stroke-linecap="round" />
              <path d="M365 93v64" stroke="#c6bfff" stroke-width="7" stroke-linecap="round" />
            </g>

            <g class="panel-chart" filter="url(#glassShadow)" opacity=".9">
              <rect x="438" y="103" width="100" height="126" rx="18" fill="url(#glassFill)" stroke="#ddd9ff" stroke-width="1.4" />
              <rect x="447" y="114" width="82" height="103" rx="12" fill="#ffffff" fill-opacity=".18" />
              <path d="M462 157h46" stroke="#beb8ff" stroke-width="5" stroke-linecap="round" />
              <path d="M462 139h36" stroke="#d8d4ff" stroke-width="5" stroke-linecap="round" />
              <path d="M462 194l21-24 17 15 23-35" stroke="#b6adff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
              <rect class="bar bar-1" x="463" y="190" width="8" height="28" rx="3" fill="#8a7cff" />
              <rect class="bar bar-2" x="480" y="177" width="9" height="41" rx="3" fill="#7b6cf7" />
              <rect class="bar bar-3" x="498" y="163" width="9" height="55" rx="3" fill="#6a5df3" />
              <rect class="bar bar-4" x="516" y="146" width="9" height="72" rx="3" fill="#897bf7" />
            </g>

            <g class="panel-cube" filter="url(#glassShadow)" opacity=".78">
              <rect x="111" y="220" width="67" height="76" rx="16" fill="url(#glassFill)" stroke="#dedaff" />
              <path d="M123 241h42l-12 14h-42l12-14Z" fill="#ffffff" fill-opacity=".32" />
              <circle class="mini-orbit" cx="145" cy="258" r="18" fill="#f5f3ff" />
              <circle class="mini-core" cx="145" cy="258" r="9" stroke="#8072f5" stroke-width="6" />
              <rect x="126" y="280" width="37" height="5" rx="2.5" fill="#d5d1ff" />
            </g>

            <g class="robot-core" filter="url(#softShadow)">
              <ellipse cx="320" cy="365" rx="130" ry="38" fill="#6f63ea" opacity=".28" />
              <ellipse class="base-shadow" cx="320" cy="357" rx="132" ry="40" fill="#8579f6" opacity=".5" />
              <ellipse cx="320" cy="348" rx="130" ry="43" fill="url(#baseTop)" stroke="#f7f6ff" stroke-width="2" />
              <ellipse cx="320" cy="344" rx="114" ry="34" fill="url(#baseRim)" opacity=".9" />
              <ellipse cx="320" cy="336" rx="92" ry="28" fill="url(#baseGlow)" stroke="#d7d3ff" />
              <ellipse class="base-light" cx="320" cy="333" rx="62" ry="17" fill="#f5f4ff" stroke="#ffffff" stroke-opacity=".8" />
              <ellipse cx="320" cy="333" rx="42" ry="11" fill="#dedbff" opacity=".7" />

              <path d="M265 253c-8 27-10 62-4 80 15 20 102 20 118 0 6-18 4-53-4-80H265Z" fill="url(#robotBody)" stroke="#d5d8ff" stroke-width="1.5" />
              <path d="M265 332c20 13 94 13 114 0" stroke="#c7ccff" stroke-width="2" opacity=".58" />
              <path d="M278 258c11 11 74 11 86 0" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity=".48" />
              <path d="M267 255c5-29 28-48 53-48s48 19 53 48c-17 14-89 14-106 0Z" fill="#fafbff" stroke="#dfe2ff" stroke-width="1.5" />
              <path d="M283 258c14 7 60 7 74 0" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity=".58" />

              <path d="M268 268c-24 9-43 31-49 56-1.2 5.4 4.8 9.6 9.4 6.6l45.4-29.5 5.7-25.6-11.5-7.5Z" fill="#e8eaff" stroke="#c9cdff" stroke-width="1.4" />
              <path d="M372 268c24 9 43 31 49 56 1.2 5.4-4.8 9.6-9.4 6.6l-45.4-29.5-5.7-25.6 11.5-7.5Z" fill="#e8eaff" stroke="#c9cdff" stroke-width="1.4" />
              <path d="M234 318c11-15 25-26 41-32" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity=".45" />
              <path d="M406 318c-11-15-25-26-41-32" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity=".45" />

              <g class="letter-card">
                <path d="M284 274c1-7.4 7-12.6 14.2-11.6l68.2 9.4c6.5.9 11.2 6.7 10.3 13.2l-7 51c-1 7.3-7.6 12.4-14.8 11.2l-68-11c-6.4-1-10.8-7-9.9-13.4l7-48.8Z" fill="url(#tabletFill)" stroke="#6b60e8" stroke-width="1.6" />
                <path d="M288 279l37.6 30.8c3.7 3 8.9 3.5 13 1.1l35.2-20.2" stroke="#bcb7ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity=".48" />
                <path d="M293 294c19 7 42 10 65 9" stroke="#dad8ff" stroke-width="3" stroke-linecap="round" opacity=".36" />
                <path d="M293 308c17 5 37 7 56 5" stroke="#dad8ff" stroke-width="2.6" stroke-linecap="round" opacity=".3" />
                <path d="M286 330c19-10 36-18 50-20 12 7 22 16 31 28" stroke="#5f54dc" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity=".28" />
              </g>

              <g class="robot-hands">
                <path d="M269 305c7-5 18-3 23 4 4.8 7 2.7 17-4.5 21.8-7.4 4.9-18 2.9-23-4.2-5-7.2-2.8-16.8 4.5-21.6Z" fill="#f4f5ff" stroke="#d3d7ff" stroke-width="1.5" />
                <path d="M279 306c4.8.8 9 3.8 11.4 8" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity=".7" />
                <path d="M288 318c-6-5-12-6-20-3" stroke="#cfd3ff" stroke-width="2.4" stroke-linecap="round" />
                <path d="M352 315c6.2-6.6 17.5-6.6 23.8 0 6.1 6.4 5.5 16.4-1.3 22-6.9 5.7-17.6 5-23.4-1.6-5.6-6.4-5.1-14.6.9-20.4Z" fill="#f4f5ff" stroke="#d3d7ff" stroke-width="1.5" />
                <path d="M362 313c5-.8 10 1 13.2 4.8" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity=".7" />
                <path d="M352 326c6-5 13-6 21-2" stroke="#cfd3ff" stroke-width="2.4" stroke-linecap="round" />
              </g>

              <rect x="252" y="163" width="136" height="86" rx="42" fill="url(#helmetGloss)" stroke="#dde0ff" stroke-width="1.6" />
              <path d="M272 175c20-17 78-19 98-1" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity=".48" />
              <path d="M287 166c18-6 50-6 68 0" stroke="#eef0ff" stroke-width="2" stroke-linecap="round" opacity=".55" />
              <rect class="visor" x="268" y="187" width="104" height="45" rx="19" fill="url(#visorFill)" />
              <path d="M275 195c17-5 67-5 90 0" stroke="#5062b9" stroke-width="2" stroke-linecap="round" opacity=".22" />
              <path class="visor-scan" d="M282 222h76" stroke="#7ff0ff" stroke-width="1.4" stroke-linecap="round" opacity=".14" />
              <g class="eye-pair" filter="url(#eyeSoftGlow)">
                <rect class="eye left-eye" x="291" y="201" width="12" height="23" rx="6" fill="url(#eyeGlow)" />
                <rect class="eye right-eye" x="337" y="201" width="12" height="23" rx="6" fill="url(#eyeGlow)" />
              </g>
              <path class="mouth-light" d="M309 224c5 2 12 2 17 0" stroke="#78efff" stroke-width="2.2" stroke-linecap="round" opacity=".28" />
              <ellipse cx="320" cy="214" rx="51" ry="24" fill="url(#screenGlow)" opacity=".24" />
              <path d="M384 196c15 4 25 17 24 33-1.5 15-14 28-29 29l-.9-20c5.5-.5 10-5 10.5-11 .5-5.8-3-10-8.4-11l3.8-20Z" fill="#dfe3ff" stroke="#b8c0ff" />
              <path d="M256 196c-15 4-25 17-24 33 1.5 15 14 28 29 29l.9-20c-5.5-.5-10-5-10.5-11-.5-5.8 3-10 8.4-11l-3.8-20Z" fill="#dfe3ff" stroke="#b8c0ff" />
              <circle cx="400" cy="220" r="15" fill="#7a6df4" />
              <circle cx="400" cy="220" r="10" fill="#b2abff" />
              <circle cx="400" cy="220" r="5" fill="#6658e8" opacity=".74" />
              <circle cx="240" cy="220" r="15" fill="#7a6df4" />
              <circle cx="240" cy="220" r="10" fill="#b2abff" />
              <circle cx="240" cy="220" r="5" fill="#6658e8" opacity=".74" />
            </g>

            <g class="sparkles">
              <path d="M443 54c9 3 15 10 17 19" stroke="#f3f0ff" stroke-width="5" stroke-linecap="round" opacity=".75" />
              <path d="M470 71l9-8" stroke="#7ee3ef" stroke-width="5" stroke-linecap="round" opacity=".48" />
              <circle cx="491" cy="70" r="5" fill="#7ee3ef" opacity=".48" />
              <circle cx="116" cy="172" r="3.5" fill="#bdb7ff" opacity=".32" />
              <circle cx="416" cy="251" r="3" fill="#ffffff" opacity=".72" />
              <circle cx="526" cy="259" r="4.2" fill="#b4adff" opacity=".28" />
            </g>
          </svg>
        </div>

        <div class="feature-row">
          <div class="feature-item" v-for="feature in features" :key="feature.title">
            <div class="feature-icon">
              <component :is="feature.icon" />
            </div>
            <div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.desc }}</p>
            </div>
          </div>
        </div>

        <p class="copyright">© 2026 AI 人岗评估系统 · 让每一次选择更有依据</p>
      </div>
    </section>

    <section class="form-section" aria-label="登录注册">
      <div class="login-card">
        <div class="card-header">
          <p class="card-kicker">企业管理入口</p>
          <h2>{{ activeTab === 'login' ? '欢迎回来' : '创建账户' }}</h2>
          <p>登录后进入 AI 人岗匹配与评估工作台</p>
        </div>

        <div class="segmented-control">
          <button :class="['segment-btn', { active: activeTab === 'login' }]" type="button" @click="activeTab = 'login'">
            登录
          </button>
          <button :class="['segment-btn', { active: activeTab === 'register' }]" type="button" @click="activeTab = 'register'">
            注册
          </button>
        </div>

        <div v-show="activeTab === 'login'" class="form-area">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef" @submit.prevent="handleLogin">
            <el-form-item prop="username">
              <label class="form-label">用户名</label>
              <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" class="custom-input">
                <template #prefix>
                  <User class="input-icon" />
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <label class="form-label">密码</label>
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" show-password class="custom-input">
                <template #prefix>
                  <Lock class="input-icon" />
                </template>
              </el-input>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe" class="remember-checkbox">记住我</el-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>

            <el-form-item class="submit-area">
              <button type="button" class="submit-button" :disabled="loading" @click="handleLogin">
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </el-form-item>
          </el-form>
        </div>

        <div v-show="activeTab === 'register'" class="form-area">
          <el-form :model="registerForm" :rules="rules" ref="registerFormRef" @submit.prevent="handleRegister">
            <div class="user-type-selector">
              <label :class="['type-label', { active: registerForm.userType === 'candidate' }]">
                <input v-model="registerForm.userType" value="candidate" type="radio" />
                <UserFilled class="type-icon" />
                <span>
                  <strong>普通用户</strong>
                  <small>应聘者和求职者</small>
                </span>
              </label>
              <label :class="['type-label', { active: registerForm.userType === 'hr' }]">
                <input v-model="registerForm.userType" value="hr" type="radio" />
                <Suitcase class="type-icon" />
                <span>
                  <strong>HR 管理员</strong>
                  <small>{{ registerForm.userType === 'hr' ? '需要邀请码' : '企业邀请码认证' }}</small>
                </span>
              </label>
            </div>

            <el-form-item prop="username">
              <label class="form-label">用户名</label>
              <el-input v-model="registerForm.username" placeholder="至少 3 个字符" size="large" class="custom-input">
                <template #prefix>
                  <User class="input-icon" />
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="email">
              <label class="form-label">邮箱地址</label>
              <el-input v-model="registerForm.email" placeholder="example@company.com" size="large" class="custom-input">
                <template #prefix>
                  <Message class="input-icon" />
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <label class="form-label">密码</label>
              <el-input v-model="registerForm.password" type="password" placeholder="至少 6 个字符" size="large" show-password class="custom-input">
                <template #prefix>
                  <Lock class="input-icon" />
                </template>
              </el-input>
            </el-form-item>

            <div v-if="registerForm.userType === 'hr'" class="hr-invite-section">
              <el-form-item prop="inviteCode">
                <label class="form-label">HR 邀请码 <span class="required">*</span></label>
                <el-input v-model="registerForm.inviteCode" placeholder="请输入企业邀请码" size="large" maxlength="20" class="custom-input">
                  <template #prefix>
                    <Key class="input-icon" />
                  </template>
                </el-input>
              </el-form-item>
              <div class="invite-tip">
                <InfoFilled class="tip-icon" />
                <span>请输入有效的企业邀请码才能注册为 HR 管理员</span>
              </div>
            </div>

            <div class="register-notice">
              <InfoFilled class="notice-icon" />
              <div>
                <strong>注册须知</strong>
                <p>请使用有效邮箱。HR 账号需要通过企业邀请码认证。</p>
              </div>
            </div>

            <el-form-item class="submit-area">
              <button type="button" class="submit-button" :disabled="loading" @click="handleRegister">
                {{ loading ? '注册中...' : '立即注册' }}
              </button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { h, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Key, Lock, Message, Suitcase, User, UserFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const activeTab = ref('login')
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  userType: 'candidate',
  inviteCode: '',
  is_hr: false
})

const VALID_HR_INVITE_CODES = [
  'HR2026@STAR',
  'ADMIN@RECRUIT',
  'TALENT@MATCH',
  'HIRING@PRO',
  'RECRUIT@2026'
]

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }]
}

const featureSvgAttrs = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  'stroke-width': '2.2',
  'stroke-linecap': 'round',
  'stroke-linejoin': 'round'
}

const features = [
  {
    icon: () => h('svg', featureSvgAttrs, [
      h('path', { d: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2' }),
      h('circle', { cx: '9', cy: '7', r: '4' }),
      h('path', { d: 'M22 21v-2a4 4 0 0 0-3-3.87' }),
      h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
    ]),
    title: '智能评估',
    desc: '多维度能力与特质分析'
  },
  {
    icon: () => h('svg', featureSvgAttrs, [
      h('circle', { cx: '12', cy: '12', r: '8' }),
      h('circle', { cx: '12', cy: '12', r: '3' }),
      h('path', { d: 'M12 2v3M12 19v3M2 12h3M19 12h3' })
    ]),
    title: '精准匹配',
    desc: 'AI 推荐最优人岗匹配方案'
  },
  {
    icon: () => h('svg', featureSvgAttrs, [
      h('path', { d: 'M4 19V9' }),
      h('path', { d: 'M10 19V5' }),
      h('path', { d: 'M16 19v-8' }),
      h('path', { d: 'M22 19V3' })
    ]),
    title: '数据洞察',
    desc: '可视化分析与决策支持'
  }
]

const API_BASE = 'http://127.0.0.1:8000'
const router = useRouter()
const userStore = useUserStore()

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await axios.post(`${API_BASE}/auth/login`, {
      username: loginForm.username,
      password: loginForm.password
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      transformRequest: [data => new URLSearchParams(data).toString()]
    })

    userStore.login({
      access_token: res.data.access_token,
      is_hr: res.data.is_hr,
      username: res.data.username,
      user_id: res.data.user_id,
      email: res.data.email
    })

    ElMessage.success('登录成功')
    router.push('/home')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  try {
    if (!registerForm.username || registerForm.username.length < 3) {
      ElMessage.warning('用户名至少 3 个字符')
      loading.value = false
      return
    }
    if (!registerForm.email || !registerForm.email.includes('@')) {
      ElMessage.warning('邮箱格式不正确')
      loading.value = false
      return
    }
    if (!registerForm.password || registerForm.password.length < 6) {
      ElMessage.warning('密码至少 6 个字符')
      loading.value = false
      return
    }

    if (registerForm.userType === 'hr') {
      if (!registerForm.inviteCode) {
        ElMessage.warning('请输入 HR 邀请码')
        loading.value = false
        return
      }
      if (!VALID_HR_INVITE_CODES.includes(registerForm.inviteCode.trim())) {
        ElMessage.error('邀请码无效，请确认输入正确')
        loading.value = false
        return
      }
    }

    const formData = new FormData()
    formData.append('username', registerForm.username)
    formData.append('email', registerForm.email)
    formData.append('password', registerForm.password)
    formData.append('is_hr', (registerForm.userType === 'hr').toString())

    await axios.post(`${API_BASE}/auth/register`, formData, {
      withCredentials: false
    })

    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
    registerForm.inviteCode = ''
    registerForm.userType = 'candidate'
    registerForm.is_hr = false
  } catch (err: any) {
    console.error('注册错误:', err)
    const detail = err.response?.data?.detail
    let errorMessage = '注册失败，请重试'

    if (typeof detail === 'string') {
      errorMessage = detail
    } else if (err.response?.status === 500) {
      errorMessage = '服务器错误，请检查后端是否运行正常'
    } else if (err.message === 'Network Error') {
      errorMessage = '网络错误，无法连接到服务器，请检查后端是否启动'
    }

    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.login-page {
  display: grid;
  grid-template-columns: minmax(720px, 1fr) 520px;
  min-height: 100vh;
  background: #f8f9ff;
  color: #151d3d;
}

.brand-section {
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  background:
    radial-gradient(circle at 72% 47%, rgba(142, 118, 255, .28), transparent 23%),
    radial-gradient(circle at 52% 65%, rgba(111, 92, 248, .12), transparent 32%),
    linear-gradient(135deg, #fbfcff 0%, #f4f5ff 48%, #eef0ff 100%);
}

.brand-section::before,
.brand-section::after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.brand-section::before {
  inset: 0;
  background:
    linear-gradient(90deg, rgba(255,255,255,.78), rgba(255,255,255,0) 54%),
    radial-gradient(circle at 88% 4%, rgba(255,255,255,.95), transparent 28%);
}

.brand-section::after {
  right: -150px;
  top: -150px;
  width: 470px;
  height: 470px;
  border-radius: 50%;
  background: rgba(124, 104, 255, .08);
  filter: blur(8px);
}

.brand-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-rows: auto 1fr auto auto;
  min-height: 100vh;
  padding: 52px 54px 24px;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-mark {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  box-shadow: 0 18px 34px rgba(104, 86, 242, .24);
}

.brand-mark svg {
  display: block;
  width: 100%;
  height: 100%;
}

.brand-header h1 {
  margin: 0 0 5px;
  font-size: 27px;
  line-height: 1;
  font-weight: 900;
  color: #111a3c;
  letter-spacing: 0;
}

.brand-header p {
  margin: 0;
  color: #7c859c;
  font-size: 14px;
  font-weight: 600;
}

.hero-copy {
  align-self: center;
  width: 47%;
  min-width: 390px;
  padding-bottom: 72px;
}

.hero-copy h2 {
  margin: 0;
  color: #111a3c;
  font-size: 42px;
  line-height: 1.25;
  font-weight: 900;
  letter-spacing: 0;
}

.hero-copy h2 span {
  display: block;
  color: #665cf6;
  text-shadow: 0 10px 24px rgba(102, 92, 246, .18);
}

.hero-rule {
  width: 43px;
  height: 5px;
  margin: 24px 0 18px;
  border-radius: 999px;
  background: #665cf6;
  box-shadow: 28px 0 0 -1px rgba(102, 92, 246, .42);
}

.hero-copy p {
  margin: 0;
  color: #5d6880;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.8;
}

.ai-stage {
  position: absolute;
  right: -22px;
  top: 166px;
  width: min(61vw, 660px);
  height: 468px;
  isolation: isolate;
  filter: saturate(1.04);
}

.stage-halo {
  position: absolute;
  inset: 56px 12px 8px 0;
  border-radius: 50%;
  background:
    radial-gradient(circle at 54% 48%, rgba(255,255,255,.72), transparent 17%),
    radial-gradient(circle at 54% 50%, rgba(130, 109, 255, .32), rgba(130, 109, 255, .11) 40%, transparent 72%);
  filter: blur(24px);
  animation: haloBreath 5.8s ease-in-out infinite;
}

.ai-stage::before,
.ai-stage::after {
  content: "";
  position: absolute;
  pointer-events: none;
  z-index: 1;
}

.ai-stage::before {
  left: 80px;
  right: 20px;
  bottom: 42px;
  height: 110px;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(124, 112, 248, .16), transparent 68%);
  filter: blur(20px);
}

.ai-stage::after {
  inset: 0;
  background: linear-gradient(90deg, rgba(248,249,255,.18), transparent 23%, transparent 78%, rgba(248,249,255,.2));
  mix-blend-mode: screen;
}

.ai-illustration {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.panel-main,
.panel-chart,
.panel-cube,
.robot-core,
.sparkles {
  transform-box: fill-box;
  transform-origin: center;
  will-change: transform, opacity;
}

.panel-main {
  animation: floatPanelMain 5.8s ease-in-out infinite;
}

.panel-chart {
  animation: floatPanelChart 6.4s ease-in-out infinite;
}

.panel-cube {
  animation: floatPanelCube 5.4s ease-in-out infinite;
}

.robot-core {
  animation: robotHover 4.8s ease-in-out infinite;
}

.sparkles {
  animation: sparkleDrift 4.8s ease-in-out infinite;
}

.orbit-ring {
  transform-box: fill-box;
  transform-origin: center;
}

.outer-ring {
  animation: orbitPulse 5.2s ease-in-out infinite;
}

.inner-ring {
  animation: innerPulse 4.2s ease-in-out infinite;
}

.base-light,
.visor,
.visor-scan,
.eye-pair,
.mouth-light,
.mini-core {
  transform-box: fill-box;
  transform-origin: center;
}

.base-light {
  animation: baseLight 3.8s ease-in-out infinite;
}

.visor {
  animation: visorGlow 3.4s ease-in-out infinite;
}

.visor-scan {
  animation: visorScan 4.2s ease-in-out infinite;
}

.eye-pair {
  animation: eyeBreathe 3.6s ease-in-out infinite;
}

.eye {
  transform-box: fill-box;
  transform-origin: center;
  animation: eyeBlink 5.4s ease-in-out infinite;
}

.right-eye {
  animation-delay: .08s;
}

.mouth-light {
  animation: mouthGlow 3.6s ease-in-out infinite;
}

.mini-core {
  animation: miniSpin 3.2s linear infinite;
}

.bar {
  transform-box: fill-box;
  transform-origin: bottom;
  animation: barPulse 2.6s ease-in-out infinite;
}

.bar-2 { animation-delay: .18s; }
.bar-3 { animation-delay: .34s; }
.bar-4 { animation-delay: .5s; }

@keyframes haloBreath {
  0%, 100% { opacity: .76; transform: scale(.98); }
  50% { opacity: 1; transform: scale(1.03); }
}

@keyframes floatPanelMain {
  0%, 100% { transform: translate3d(0, 0, 0) rotate(-.4deg); opacity: .88; }
  50% { transform: translate3d(0, -10px, 0) rotate(.5deg); opacity: .98; }
}

@keyframes floatPanelChart {
  0%, 100% { transform: translate3d(0, 0, 0) rotate(.7deg); }
  50% { transform: translate3d(8px, -13px, 0) rotate(-.6deg); }
}

@keyframes floatPanelCube {
  0%, 100% { transform: translate3d(0, 0, 0) rotate(-.7deg); }
  50% { transform: translate3d(-9px, -8px, 0) rotate(.8deg); }
}

@keyframes robotHover {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-7px) scale(1.012); }
}

@keyframes orbitPulse {
  0%, 100% { opacity: .68; transform: scaleX(1); }
  50% { opacity: .95; transform: scaleX(1.025); }
}

@keyframes innerPulse {
  0%, 100% { opacity: .42; transform: scale(.98); }
  50% { opacity: .64; transform: scale(1.02); }
}

@keyframes baseLight {
  0%, 100% { opacity: .82; transform: scaleX(.98); }
  50% { opacity: 1; transform: scaleX(1.05); }
}

@keyframes visorGlow {
  0%, 100% { filter: drop-shadow(0 0 0 rgba(79, 224, 255, 0)); }
  50% { filter: drop-shadow(0 0 7px rgba(79, 224, 255, .24)); }
}

@keyframes visorScan {
  0%, 100% { opacity: .1; transform: translateY(-8px); }
  45%, 55% { opacity: .34; transform: translateY(3px); }
}

@keyframes eyeBreathe {
  0%, 100% { opacity: .9; filter: drop-shadow(0 0 2px rgba(79, 224, 255, .28)); }
  50% { opacity: 1; filter: drop-shadow(0 0 6px rgba(79, 224, 255, .48)); }
}

@keyframes eyeBlink {
  0%, 88%, 100% { opacity: .96; transform: scaleY(1); }
  91% { opacity: .58; transform: scaleY(.24); }
  94% { opacity: .98; transform: scaleY(1); }
}

@keyframes mouthGlow {
  0%, 100% { opacity: .34; }
  50% { opacity: .56; }
}

@keyframes miniSpin {
  from { transform: rotate(0); }
  to { transform: rotate(360deg); }
}

@keyframes barPulse {
  0%, 100% { transform: scaleY(.86); opacity: .76; }
  50% { transform: scaleY(1.08); opacity: 1; }
}

@keyframes sparkleDrift {
  0%, 100% { transform: translateY(0); opacity: .76; }
  50% { transform: translateY(-8px); opacity: 1; }
}

.feature-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 34px;
  margin: 0 0 42px;
}

.feature-item {
  display: grid;
  grid-template-columns: 50px 1fr;
  align-items: center;
  gap: 13px;
  min-width: 0;
}

.feature-icon {
  display: grid;
  place-items: center;
  width: 50px;
  height: 50px;
  border: 1px solid rgba(218, 221, 255, .88);
  border-radius: 10px;
  color: #665cf6;
  background: rgba(255, 255, 255, .68);
  box-shadow: 0 15px 30px rgba(103, 92, 246, .1), inset 0 1px 0 rgba(255,255,255,.9);
  backdrop-filter: blur(12px);
}

.feature-icon svg {
  width: 28px;
  height: 28px;
}

.feature-item h3 {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 900;
  color: #172042;
}

.feature-item p {
  margin: 0;
  color: #7a849a;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
}

.copyright {
  margin: 0;
  color: #8a93a8;
  font-size: 12px;
  font-weight: 600;
}

.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background:
    radial-gradient(circle at 50% 14%, rgba(115, 101, 246, .11), transparent 28%),
    #f7f8ff;
}

.login-card {
  width: 100%;
  max-width: 430px;
  padding: 38px;
  border: 1px solid rgba(221, 224, 255, .78);
  border-radius: 22px;
  background: rgba(255, 255, 255, .9);
  box-shadow: 0 28px 80px rgba(31, 38, 96, .13);
  backdrop-filter: blur(18px);
}

.card-header {
  margin-bottom: 26px;
}

.card-kicker {
  margin: 0 0 10px;
  color: #665cf6;
  font-size: 13px;
  font-weight: 800;
}

.card-header h2 {
  margin: 0 0 9px;
  color: #121a38;
  font-size: 30px;
  line-height: 1.18;
  font-weight: 900;
}

.card-header p:last-child {
  margin: 0;
  color: #7b8498;
  font-size: 14px;
  line-height: 1.6;
}

.segmented-control {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 6px;
  margin-bottom: 24px;
  border-radius: 12px;
  background: #eef0fb;
}

.segment-btn {
  height: 42px;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: #6d758b;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: .18s ease;
}

.segment-btn.active {
  color: #151d3d;
  background: white;
  box-shadow: 0 9px 18px rgba(100, 92, 246, .12);
}

.form-area {
  animation: fadeUp .22s ease;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-label {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  color: #384158;
  font-size: 14px;
  font-weight: 800;
}

:deep(.custom-input .el-input__wrapper) {
  min-height: 48px;
  padding: 0 15px;
  border: 1px solid #dde1ee;
  border-radius: 10px;
  background: #fbfcff;
  box-shadow: none;
  transition: .18s ease;
}

:deep(.custom-input .el-input__wrapper:hover) {
  border-color: #cbd1e3;
  background: #ffffff;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  border-color: #7064f4;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(112, 100, 244, .12);
}

:deep(.custom-input .el-input__inner) {
  color: #161d34;
  font-size: 14px;
  font-weight: 600;
}

:deep(.custom-input .el-input__inner::placeholder) {
  color: #a3abbc;
}

.input-icon {
  width: 18px;
  height: 18px;
  color: #9ba4b8;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 18px 0 24px;
}

:deep(.remember-checkbox .el-checkbox__label) {
  color: #697286;
  font-size: 14px;
  font-weight: 700;
}

:deep(.remember-checkbox .el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #665cf6;
  border-color: #665cf6;
}

.forgot-link {
  color: #665cf6;
  font-size: 14px;
  font-weight: 800;
  text-decoration: none;
}

.user-type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.type-label {
  display: grid;
  grid-template-columns: 26px 1fr;
  align-items: center;
  gap: 10px;
  min-width: 0;
  padding: 14px;
  border: 1px solid #dde1ee;
  border-radius: 10px;
  background: #fbfcff;
  cursor: pointer;
  transition: .18s ease;
}

.type-label input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.type-label.active {
  border-color: #7367f4;
  background: #f4f3ff;
  box-shadow: 0 0 0 4px rgba(115, 103, 244, .1);
}

.type-icon {
  width: 24px;
  height: 24px;
  color: #665cf6;
}

.type-label strong,
.type-label small {
  display: block;
}

.type-label strong {
  color: #1b2440;
  font-size: 13px;
  font-weight: 900;
}

.type-label small {
  margin-top: 3px;
  color: #7d879a;
  font-size: 11px;
  font-weight: 700;
}

.hr-invite-section {
  margin-bottom: 18px;
  animation: fadeUp .22s ease;
}

.required {
  color: #ef4444;
}

.invite-tip,
.register-notice {
  display: flex;
  gap: 9px;
  align-items: flex-start;
  border-radius: 10px;
}

.invite-tip {
  margin-top: -6px;
  padding: 11px 12px;
  border: 1px solid #ead8a6;
  background: #fff8e6;
  color: #8a6014;
  font-size: 12px;
  font-weight: 700;
}

.tip-icon,
.notice-icon {
  flex: 0 0 auto;
  width: 17px;
  height: 17px;
}

.register-notice {
  margin: 18px 0 22px;
  padding: 13px 14px;
  border: 1px solid #dde1ee;
  background: #fbfcff;
}

.register-notice strong {
  display: block;
  margin-bottom: 4px;
  color: #384158;
  font-size: 13px;
  font-weight: 900;
}

.register-notice p {
  margin: 0;
  color: #737d91;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.5;
}

.submit-area {
  margin-bottom: 0;
}

.submit-button {
  width: 100%;
  height: 50px;
  border: 0;
  border-radius: 10px;
  color: white;
  background: linear-gradient(135deg, #635cf6 0%, #8b5cf6 100%);
  box-shadow: 0 16px 30px rgba(102, 92, 246, .24);
  font-size: 15px;
  font-weight: 900;
  cursor: pointer;
  transition: .18s ease;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 20px 34px rgba(102, 92, 246, .3);
}

.submit-button:disabled {
  opacity: .62;
  cursor: not-allowed;
}

@media (max-width: 1180px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .brand-section {
    min-height: 720px;
  }

  .form-section {
    min-height: 100vh;
  }

  .ai-stage {
    right: -12px;
    width: 620px;
  }
}

@media (max-width: 760px) {
  .brand-section {
    min-height: 660px;
  }

  .brand-shell {
    padding: 34px 24px 22px;
  }

  .brand-header h1 {
    font-size: 22px;
  }

  .brand-header p {
    font-size: 12px;
  }

  .hero-copy {
    align-self: start;
    width: 100%;
    min-width: 0;
    padding-top: 66px;
  }

  .hero-copy h2 {
    font-size: 34px;
  }

  .ai-stage {
    top: 258px;
    right: -150px;
    width: 590px;
    opacity: .9;
  }

  .feature-row {
    grid-template-columns: 1fr;
    gap: 14px;
    margin-bottom: 22px;
  }

  .feature-item {
    grid-template-columns: 44px 1fr;
  }

  .feature-icon {
    width: 44px;
    height: 44px;
  }

  .form-section {
    padding: 24px;
  }

  .login-card {
    padding: 28px 22px;
  }

  .user-type-selector {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .stage-halo,
  .panel-main,
  .panel-chart,
  .panel-cube,
  .robot-core,
  .sparkles,
  .outer-ring,
  .inner-ring,
  .base-light,
  .visor,
  .eye,
  .mini-core,
  .bar {
    animation: none;
  }
}
</style>
