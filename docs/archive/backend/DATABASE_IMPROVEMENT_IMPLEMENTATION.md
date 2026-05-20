# 数据库结构改进 - 代码实现参考

## 📝 改进方案详细实现

### 方案 1: 合并 users 和 candidates 表

#### 步骤 1: 更新 User 模型

```python
# models/user.py
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, Float
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class UserType(str, Enum):
    """用户类型枚举"""
    HR = "hr"
    CANDIDATE = "candidate"


class User(Base):
    __tablename__ = "users"

    # 主键和认证
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False, index=True)  # 'hr' 或 'candidate'
    
    # 通用个人信息
    real_name = Column(String(100), nullable=True)
    nickname = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True, index=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)  # LONGTEXT 支持 Base64
    delivery_privacy = Column(Integer, default=2)  # 1=实名, 2=昵称, 3=匿名
    
    # ===== 候选人专有字段（HR 用户时为 NULL） =====
    age = Column(Integer, nullable=True)
    education = Column(String(50), nullable=True)  # 大专、本科、硕士、博士
    major = Column(String(100), nullable=True)
    desired_job = Column(String(100), nullable=True)
    experience_years = Column(Float, nullable=True)
    skills = Column(JSON, nullable=True)  # 存储技能列表
    resume_url = Column(Text, nullable=True)  # 简历文件路径
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)  # 软删除
    deleted_at = Column(DateTime, nullable=True)
    
    # ===== 关系 =====
    # HR 创建的岗位
    jobs = relationship("Job", back_populates="creator", 
                       foreign_keys="Job.creator_id",
                       cascade="all, delete-orphan")
    
    # 候选人的面试记录
    interviews = relationship("Interview", back_populates="candidate",
                             foreign_keys="Interview.candidate_id",
                             cascade="all, delete-orphan")
    
    # 候选人的评估记录
    assessments = relationship("AssessmentRecord", back_populates="candidate",
                              foreign_keys="AssessmentRecord.candidate_id",
                              cascade="all, delete-orphan")
    
    # 候选人的心理特质档案
    personality_profile = relationship("CandidatePersonalityProfile", 
                                      back_populates="candidate",
                                      uselist=False,
                                      cascade="all, delete-orphan")
    
    # 候选人的面试回答
    interview_responses = relationship("InterviewResponse", back_populates="candidate",
                                      foreign_keys="InterviewResponse.candidate_id",
                                      cascade="all, delete-orphan")
    
    # HR 的创建操作（审计）
    created_items = relationship("AssessmentRecord", back_populates="created_by_user",
                                foreign_keys="AssessmentRecord.created_by",
                                cascade="all, delete-orphan")
    
    @property
    def is_hr(self):
        """便利属性，检查是否为 HR"""
        return self.user_type == UserType.HR
    
    @property
    def is_candidate(self):
        """便利属性，检查是否为候选人"""
        return self.user_type == UserType.CANDIDATE
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "nickname": self.nickname,
            "user_type": self.user_type.value,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        # 候选人信息
        if self.is_candidate:
            data.update({
                "age": self.age,
                "education": self.education,
                "major": self.major,
                "experience_years": self.experience_years,
                "skills": self.skills,
                "desired_job": self.desired_job,
            })
        
        # 敏感信息
        if include_sensitive:
            data.update({
                "email": self.email,
                "phone": self.phone,
            })
        
        return data
```

---

#### 步骤 2: 删除 Candidate 模型

```python
# models/candidate.py 可以删除或标记为废弃
# 如果迁移期间需要保留，可以：
# class Candidate(Base):
#     __tablename__ = "candidates_deprecated"  # 标记为废弃
#     # 保持原有结构以便数据迁移
```

---

### 方案 2: 修复 Interview 表关系

#### 更新后的 Interview 模型

```python
# models/interview.py
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 外键 - 确保 candidate_id 指向 User 表中的候选人 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), 
                         nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), 
                   nullable=False, index=True)
    
    # ===== 关系 =====
    # 关联到候选人用户
    candidate = relationship("User", 
                            back_populates="interviews",
                            foreign_keys=[candidate_id])
    
    # 关联到岗位
    job = relationship("Job", back_populates="interviews")
    
    # ===== 面试状态和结果 =====
    status = Column(String(20), default="started", index=True)  
    # 状态值: started/in_progress/completed/passed/failed/withdrawn
    
    # Big Five 人格特质评分（来自评估）
    personality_traits = Column(JSON, nullable=True)  
    # 格式: {"openness": 7.5, "conscientiousness": 8.0, ...}
    
    # 总体匹配度评分 (0-100)
    match_score = Column(Float, nullable=True)
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # ===== 其他信息 =====
    notes = Column(String(500), nullable=True)
    
    def get_duration_minutes(self):
        """计算面试耗时（分钟）"""
        if self.completed_at and self.created_at:
            duration = (self.completed_at - self.created_at).total_seconds() / 60
            return round(duration, 2)
        return None
```

---

### 方案 3: 统一主键类型

#### 更新 AssessmentRecord

```python
# models/assessment.py (修改部分)

class AssessmentRecord(Base):
    """评估记录表 - 存储候选人对岗位的一次完整评估"""
    __tablename__ = "assessment_records"

    # ✅ 统一使用自增 INT
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 外键 - 统一使用 INT 类型 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), 
                         nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), 
                   nullable=False, index=True)
    
    # ===== 哪个 HR 创建了这个评估（审计追踪） =====
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    job_title = Column(String(255), nullable=False)
    
    # ===== 评估状态 =====
    assessment_status = Column(SQLEnum(AssessmentStatus), 
                              default=AssessmentStatus.PENDING,
                              index=True)
    assessment_mode = Column(String(50), default="immersive", index=True)
    
    # ===== 评估结果 =====
    match_score = Column(Float, nullable=True)  # 0-100
    conversation_summary = Column(Text, nullable=True)
    
    # ===== 评估统计 =====
    total_rounds = Column(Integer, default=0)
    duration_minutes = Column(Float, nullable=True)
    conversation_depth = Column(Float, nullable=True)  # 0-10
    roles_participated = Column(JSON, nullable=True)  # ["hr", "tech_lead"]
    overall_impression = Column(Text, nullable=True)
    
    # ===== 关联的场景 =====
    scenario_ids = Column(JSON, nullable=True)  # [1, 2, 3] 或 ["scenario_1", "scenario_2"]
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, 
                       nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow)
    
    # ===== 关系 =====
    candidate = relationship("User", back_populates="assessments",
                            foreign_keys=[candidate_id])
    job = relationship("Job")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    # 关联的回答记录
    responses = relationship("InterviewResponse", back_populates="assessment",
                            cascade="all, delete-orphan")
    
    # 关联的匹配分析
    match_analysis = relationship("AssessmentMatchAnalysis", 
                                 back_populates="assessment",
                                 uselist=False,
                                 cascade="all, delete-orphan")
    
    # 关联的特质描述
    trait_descriptions = relationship("PersonalityTraitDescription",
                                     back_populates="assessment",
                                     cascade="all, delete-orphan")
```

---

### 方案 4: 添加 assessment_id 到 InterviewResponse

#### 更新 InterviewResponse 模型

```python
# models/hr_agent.py (修改部分)

class InterviewResponse(Base):
    """面试回答记录表 - 存储每一轮的回答"""
    __tablename__ = "interview_responses"
    
    # ✅ 统一使用自增 INT
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ===== 核心外键 - 关联到评估记录 =====
    assessment_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    
    # ===== 用户关系 =====
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False, index=True)
    
    # ===== 场景关系 =====
    scenario_id = Column(String(50), ForeignKey("scenarios.id"), 
                        nullable=False, index=True)
    
    # ===== 回答内容 =====
    round_num = Column(Integer, nullable=False)  # 第几轮（1, 2, 3...）
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # ===== 行为分析 =====
    answer_latency = Column(Float, nullable=True)     # 回答耗时（秒）
    emotion = Column(String(50), nullable=True)       # 检测到的情感
    answer_length = Column(Integer, nullable=True)    # 回答长度
    is_paste = Column(Boolean, default=False)         # 是否粘贴回答
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord", back_populates="responses")
    candidate = relationship("User", back_populates="interview_responses")
    scenario = relationship("Scenario")
    
    # 关联的特质评分
    trait_scores = relationship("TraitScore", back_populates="response",
                               cascade="all, delete-orphan")
```

---

### 方案 5: 新增 EvaluationFramework 表

#### 新增评估框架表

```python
# models/evaluation_framework.py (新增)

from sqlalchemy import Column, Integer, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class EvaluationFramework(Base):
    """评估框架表 - 为每个岗位定义评估标准"""
    __tablename__ = "evaluation_frameworks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联到岗位（一个岗位对应一个评估框架）
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"),
                   nullable=False, unique=True, index=True)
    
    # ===== Big Five 目标值 =====
    target_openness = Column(Float, default=5.0, nullable=False)           # 开放性
    target_conscientiousness = Column(Float, default=5.0, nullable=False)  # 尽责性
    target_extroversion = Column(Float, default=5.0, nullable=False)       # 外向性
    target_agreeableness = Column(Float, default=5.0, nullable=False)      # 宜人性
    target_neuroticism = Column(Float, default=5.0, nullable=False)        # 神经质
    
    # ===== 权重配置 =====
    weights = Column(JSON, nullable=False)
    # 示例: {
    #   "openness": 0.15,
    #   "conscientiousness": 0.25,
    #   "extroversion": 0.20,
    #   "agreeableness": 0.20,
    #   "neuroticism": 0.20
    # }
    
    # ===== 其他评估维度 =====
    custom_dimensions = Column(JSON, nullable=True)
    # 示例: {
    #   "leadership": {"weight": 0.15, "target": 8.0},
    #   "technical_skills": {"weight": 0.25, "target": 8.5}
    # }
    
    # ===== 通过标准 =====
    min_match_score = Column(Float, default=70.0, nullable=False)
    
    # ===== 描述 =====
    description = Column(Text, nullable=True)
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== 关系 =====
    job = relationship("Job", back_populates="evaluation_framework")


# Job 模型中需要添加：
# evaluation_framework = relationship("EvaluationFramework", back_populates="job",
#                                    uselist=False, cascade="all, delete-orphan")
```

---

### 方案 6: 新增对话历史表

#### 完整的对话历史追踪

```python
# models/conversation.py (新增)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum


class Speaker(str, Enum):
    """发言者类型"""
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    SYSTEM = "system"


class ConversationTurn(Base):
    """对话记录表 - 记录评估过程中的每一条消息"""
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联到评估记录
    assessment_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    
    # 关联到具体的回答（可选，某些消息可能不是回答）
    response_id = Column(Integer, ForeignKey("interview_responses.id", ondelete="SET NULL"),
                        nullable=True, index=True)
    
    # ===== 对话内容 =====
    round_num = Column(Integer, nullable=False)  # 第几轮
    turn_num = Column(Integer, nullable=False)  # 轮内第几条（1, 2, 3...）
    
    speaker = Column(SQLEnum(Speaker), nullable=False)  # 谁说的
    speaker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 具体是哪个用户/面试官
    
    message = Column(Text, nullable=False)  # 原始消息
    
    # ===== 行为数据 =====
    emotion = Column(String(50), nullable=True)  # 候选人的情感
    sentiment = Column(String(20), nullable=True)  # 情感倾向：positive/neutral/negative
    confidence_score = Column(Float, nullable=True)  # 置信度
    
    # ===== 技术信息 =====
    response_time_ms = Column(Integer, nullable=True)  # 响应时间（毫秒）
    message_length = Column(Integer, nullable=True)  # 消息长度
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord")
    response = relationship("InterviewResponse")
    speaker_user = relationship("User", foreign_keys=[speaker_id])
    
    @property
    def is_candidate_message(self):
        return self.speaker == Speaker.CANDIDATE
    
    @property
    def is_interviewer_message(self):
        return self.speaker == Speaker.INTERVIEWER


class ConversationAnalysis(Base):
    """对话分析表 - 存储 AI 对对话的总体分析"""
    __tablename__ = "conversation_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联到评估
    assessment_id = Column(Integer, ForeignKey("assessment_records.id", ondelete="CASCADE"),
                          nullable=False, unique=True, index=True)
    
    # ===== 对话分析结果 =====
    average_response_time = Column(Float, nullable=True)  # 平均回答时间（秒）
    total_turns = Column(Integer, default=0)  # 总对话轮数
    candidate_emotion_trend = Column(Text, nullable=True)  # 情感变化趋势描述
    
    # ===== 整体评价 =====
    communication_clarity = Column(Float, nullable=True)  # 表达清晰度 (0-10)
    engagement_level = Column(Float, nullable=True)  # 参与度 (0-10)
    coherence = Column(Float, nullable=True)  # 逻辑连贯性 (0-10)
    
    # ===== AI 生成的总结 =====
    summary = Column(Text, nullable=True)
    
    # ===== 时间戳 =====
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== 关系 =====
    assessment = relationship("AssessmentRecord")
```

---

## 📊 数据迁移脚本

#### MySQL 迁移脚本

```sql
-- ============================================
-- 数据库迁移脚本
-- ============================================

-- Step 1: 备份原始数据
CREATE TABLE candidates_backup AS SELECT * FROM candidates;
CREATE TABLE users_backup AS SELECT * FROM users;

-- Step 2: 添加候选人字段到 users 表（如果还没有）
ALTER TABLE users ADD COLUMN IF NOT EXISTS age INT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS education VARCHAR(50) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS major VARCHAR(100) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS desired_job VARCHAR(100) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_years FLOAT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS skills JSON NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS resume_url TEXT NULL;

-- Step 3: 添加 user_type 列（如果还没有）
ALTER TABLE users ADD COLUMN IF NOT EXISTS user_type ENUM('hr', 'candidate') NOT NULL DEFAULT 'candidate';

-- Step 4: 添加审计字段（如果还没有）
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL;
ALTER TABLE users ADD INDEX idx_deleted (is_deleted);

-- Step 5: 迁移候选人数据
UPDATE users u
JOIN candidates c ON u.id = c.id
SET 
    u.age = c.age,
    u.education = c.education,
    u.major = c.major,
    u.desired_job = c.desired_job,
    u.experience_years = c.experience_years,
    u.skills = c.skills
WHERE u.is_hr = FALSE;

-- Step 6: 更新 Interview 表的外键约束
-- 先删除旧约束
ALTER TABLE interviews DROP CONSTRAINT IF EXISTS interviews_ibfk_1;

-- 重新定义外键（确保指向候选人）
ALTER TABLE interviews
MODIFY COLUMN candidate_id INT NOT NULL,
ADD CONSTRAINT interviews_fk_candidate 
FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE;

-- Step 7: 添加 assessment_id 到 interview_responses
ALTER TABLE interview_responses 
ADD COLUMN IF NOT EXISTS assessment_id INT NOT NULL,
ADD CONSTRAINT interview_responses_fk_assessment 
FOREIGN KEY (assessment_id) REFERENCES assessment_records(id) ON DELETE CASCADE;

-- Step 8: 创建 evaluation_frameworks 表
CREATE TABLE IF NOT EXISTS evaluation_frameworks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT UNIQUE NOT NULL,
    
    target_openness FLOAT DEFAULT 5.0 NOT NULL,
    target_conscientiousness FLOAT DEFAULT 5.0 NOT NULL,
    target_extroversion FLOAT DEFAULT 5.0 NOT NULL,
    target_agreeableness FLOAT DEFAULT 5.0 NOT NULL,
    target_neuroticism FLOAT DEFAULT 5.0 NOT NULL,
    
    weights JSON NOT NULL,
    custom_dimensions JSON NULL,
    min_match_score FLOAT DEFAULT 70.0 NOT NULL,
    description TEXT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_job (job_id)
);

-- Step 9: 创建 conversation_turns 表
CREATE TABLE IF NOT EXISTS conversation_turns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    assessment_id INT NOT NULL,
    response_id INT NULL,
    round_num INT NOT NULL,
    turn_num INT NOT NULL,
    
    speaker ENUM('candidate', 'interviewer', 'system') NOT NULL,
    speaker_id INT NULL,
    message LONGTEXT NOT NULL,
    
    emotion VARCHAR(50) NULL,
    sentiment VARCHAR(20) NULL,
    confidence_score FLOAT NULL,
    
    response_time_ms INT NULL,
    message_length INT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (assessment_id) REFERENCES assessment_records(id) ON DELETE CASCADE,
    FOREIGN KEY (response_id) REFERENCES interview_responses(id) ON DELETE SET NULL,
    FOREIGN KEY (speaker_id) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_assessment (assessment_id),
    INDEX idx_response (response_id),
    INDEX idx_round (assessment_id, round_num)
);

-- Step 10: 创建 conversation_analyses 表
CREATE TABLE IF NOT EXISTS conversation_analyses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    assessment_id INT UNIQUE NOT NULL,
    
    average_response_time FLOAT NULL,
    total_turns INT DEFAULT 0,
    candidate_emotion_trend TEXT NULL,
    
    communication_clarity FLOAT NULL,
    engagement_level FLOAT NULL,
    coherence FLOAT NULL,
    
    summary LONGTEXT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (assessment_id) REFERENCES assessment_records(id) ON DELETE CASCADE,
    INDEX idx_assessment (assessment_id)
);

-- Step 11: 添加审计字段到核心表
ALTER TABLE assessment_records ADD COLUMN IF NOT EXISTS created_by INT NULL;
ALTER TABLE assessment_records ADD CONSTRAINT assessment_records_fk_created_by 
FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- Step 12: 添加索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_deleted ON users(is_deleted);
CREATE INDEX IF NOT EXISTS idx_assessment_records_candidate ON assessment_records(candidate_id);
CREATE INDEX IF NOT EXISTS idx_assessment_records_job ON assessment_records(job_id);
CREATE INDEX IF NOT EXISTS idx_assessment_records_status ON assessment_records(assessment_status);
CREATE INDEX IF NOT EXISTS idx_assessment_records_created ON assessment_records(created_at);
CREATE INDEX IF NOT EXISTS idx_interview_responses_assessment ON interview_responses(assessment_id);

-- Step 13: 验证迁移
-- 检查 Interview 表的数据完整性
SELECT COUNT(*) as interview_count FROM interviews i
WHERE EXISTS (SELECT 1 FROM users u WHERE u.id = i.candidate_id AND u.user_type = 'candidate');

-- 检查 InterviewResponse 表
SELECT COUNT(*) as response_without_assessment FROM interview_responses WHERE assessment_id IS NULL;

-- Step 14: 备份完整后，删除旧表（谨慎操作）
-- DROP TABLE candidates;  -- 仅在确认数据迁移完毕后执行
```

---

## ✅ 验证检查表

迁移后应检查以下项目：

```sql
-- 1. 验证外键完整性
SELECT CONSTRAINT_NAME, TABLE_NAME, REFERENCED_TABLE_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;

-- 2. 验证数据一致性
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION
SELECT 'jobs', COUNT(*) FROM jobs
UNION
SELECT 'interviews', COUNT(*) FROM interviews
UNION
SELECT 'assessment_records', COUNT(*) FROM assessment_records
UNION
SELECT 'interview_responses', COUNT(*) FROM interview_responses;

-- 3. 检查孤立记录
SELECT * FROM interview_responses ir
WHERE NOT EXISTS (SELECT 1 FROM assessment_records ar WHERE ar.id = ir.assessment_id);

-- 4. 检查类型一致性
SELECT DISTINCT user_type, COUNT(*) FROM users GROUP BY user_type;

-- 5. 性能检查
EXPLAIN SELECT * FROM assessment_records WHERE candidate_id = 1 ORDER BY created_at DESC;
```

---

## 📋 实施时间表

| 阶段 | 任务 | 所需时间 |
|-----|------|--------|
| 1 | 创建备份、测试环境 | 0.5 天 |
| 2 | 运行迁移脚本 | 0.5 天 |
| 3 | 更新 SQLAlchemy 模型 | 1 天 |
| 4 | 更新相关 API 端点 | 1.5 天 |
| 5 | 数据验证和修复 | 1 天 |
| 6 | 回归测试 | 1 天 |
| 7 | 性能优化 | 0.5 天 |
| **总计** | | **6 天** |

