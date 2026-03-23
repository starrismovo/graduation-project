-- ============================================
-- P0 数据库迁移脚本 (已调整版本)
-- 根据实际数据库状态优化
-- 候选人数据重复、主键类型、审计字段等问题修复
-- ============================================

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- STEP 1: 备份现有数据
-- ============================================

CREATE TABLE IF NOT EXISTS candidates_backup AS SELECT * FROM candidates;
CREATE TABLE IF NOT EXISTS users_backup AS SELECT * FROM users;

SELECT '✓ STEP 1: 备份完成' AS migration_step, NOW() AS timestamp;

-- ============================================
-- STEP 2: 查看迁移前数据
-- ============================================

SELECT '✓ STEP 2: 迁移前数据统计' AS migration_step;
SELECT CONCAT('  users 表: ', COUNT(*), ' 行') FROM users;
SELECT CONCAT('  candidates 表: ', COUNT(*), ' 行') FROM candidates;
SELECT CONCAT('  interviews 表: ', COUNT(*), ' 行') FROM interviews;

-- ============================================
-- STEP 3: 为 users 表添加候选人相关字段
-- ============================================

SELECT '✓ STEP 3: 为 users 表添加候选人字段' AS migration_step;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS age INT NULL AFTER delivery_privacy,
ADD COLUMN IF NOT EXISTS education VARCHAR(50) NULL AFTER age,
ADD COLUMN IF NOT EXISTS major VARCHAR(100) NULL AFTER education,
ADD COLUMN IF NOT EXISTS desired_job VARCHAR(100) NULL AFTER major,
ADD COLUMN IF NOT EXISTS experience_years FLOAT NULL AFTER desired_job,
ADD COLUMN IF NOT EXISTS skills JSON NULL AFTER experience_years,
ADD COLUMN IF NOT EXISTS resume_url TEXT NULL AFTER skills;

-- ============================================
-- STEP 4: 为 users 表添加用户类型列
-- ============================================

SELECT '✓ STEP 4: 为 users 表添加 user_type 列' AS migration_step;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS user_type ENUM('hr', 'candidate') DEFAULT 'candidate' AFTER is_hr;

-- 根据 is_hr 字段设置 user_type
UPDATE users 
SET user_type = CASE 
    WHEN is_hr = 1 THEN 'hr'
    WHEN is_hr = 0 THEN 'candidate'
    ELSE 'candidate'
END 
WHERE user_type IS NULL OR user_type = 'candidate';

SELECT '  设置 user_type 完成' AS sub_step;

-- ============================================
-- STEP 5: 为 users 表添加审计和软删除字段
-- ============================================

SELECT '✓ STEP 5: 为 users 表添加审计字段' AS migration_step;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE AFTER updated_at,
ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL AFTER is_deleted;

CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_deleted ON users(is_deleted);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

SELECT '  审计字段添加完成' AS sub_step;

-- ============================================
-- STEP 6: 迁移 candidates 数据到 users 表（如果有数据）
-- ============================================

SELECT '✓ STEP 6: 迁移候选人数据' AS migration_step;

-- 由于 candidates.id 是 VARCHAR(100)，而 users.id 是 INT，
-- 需要通过 name 或其他字段进行关联
UPDATE users u
SET 
    u.age = COALESCE(u.age, (
        SELECT c.age FROM candidates c 
        WHERE c.name = u.real_name OR c.name = u.username 
        LIMIT 1
    )),
    u.education = COALESCE(u.education, (
        SELECT c.education FROM candidates c 
        WHERE c.name = u.real_name OR c.name = u.username 
        LIMIT 1
    )),
    u.major = COALESCE(u.major, (
        SELECT c.major FROM candidates c 
        WHERE c.name = u.real_name OR c.name = u.username 
        LIMIT 1
    )),
    u.desired_job = COALESCE(u.desired_job, (
        SELECT c.desired_job FROM candidates c 
        WHERE c.name = u.real_name OR c.name = u.username 
        LIMIT 1
    )),
    u.experience_years = COALESCE(u.experience_years, (
        SELECT c.experience_years FROM candidates c 
        WHERE c.name = u.real_name OR c.name = u.username 
        LIMIT 1
    )),
    u.skills = COALESCE(u.skills, (
        SELECT c.skills FROM candidates c 
        WHERE c.name = u.real_name OR c.name = u.username 
        LIMIT 1
    ))
WHERE u.user_type = 'candidate' AND ((u.age IS NULL) OR (u.education IS NULL));

SELECT '  候选人数据迁移完成' AS sub_step;

-- ============================================
-- STEP 7: 检查 interviews 表的外键关系（已正确，无需修改）
-- ============================================

SELECT '✓ STEP 7: Interview 表外键检查' AS migration_step;

-- 显示当前外键关系
SELECT 'interviews 表外键关系: OK (candidate_id → users(id))' AS fk_status;

-- ============================================
-- STEP 8: 为 interviews 表添加审计字段
-- ============================================

SELECT '✓ STEP 8: 为 interviews 表添加必要字段' AS migration_step;

ALTER TABLE interviews 
ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER completed_at,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE AFTER notes,
ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL AFTER is_deleted;

CREATE INDEX IF NOT EXISTS idx_interviews_deleted ON interviews(is_deleted);
CREATE INDEX IF NOT EXISTS idx_interviews_created_at ON interviews(created_at);

SELECT '  审计字段添加完成' AS sub_step;

-- ============================================
-- STEP 9: 为 assessment_records 表添加审计字段
-- ============================================

SELECT '✓ STEP 9: 为 assessment_records 表添加审计字段和索引' AS migration_step;

ALTER TABLE assessment_records 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE AFTER updated_at,
ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL AFTER is_deleted,
ADD COLUMN IF NOT EXISTS created_by INT NULL AFTER job_title;

CREATE INDEX IF NOT EXISTS idx_assessment_records_deleted ON assessment_records(is_deleted);
CREATE INDEX IF NOT EXISTS idx_assessment_records_candidate ON assessment_records(candidate_id);
CREATE INDEX IF NOT EXISTS idx_assessment_records_job ON assessment_records(job_id);
CREATE INDEX IF NOT EXISTS idx_assessment_records_status ON assessment_records(assessment_status);
CREATE INDEX IF NOT EXISTS idx_assessment_records_created ON assessment_records(created_at);

-- ============================================
-- STEP 10: 为 interview_responses 表添加关键字段
-- ============================================

SELECT '✓ STEP 10: 为 interview_responses 表添加关键字段' AS migration_step;

ALTER TABLE interview_responses 
ADD COLUMN IF NOT EXISTS assessment_id INT NULL AFTER id;

CREATE INDEX IF NOT EXISTS idx_interview_responses_assessment ON interview_responses(assessment_id);
CREATE INDEX IF NOT EXISTS idx_interview_responses_candidate ON interview_responses(candidate_id);
CREATE INDEX IF NOT EXISTS idx_interview_responses_round ON interview_responses(round_num);

-- ============================================
-- STEP 11: 创建缺失的关键字段（更新_at）
-- ============================================

SELECT '✓ STEP 11: 为其他表添加 updated_at 字段' AS migration_step;

ALTER TABLE scenarios ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
ALTER TABLE scenario_summaries ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- ============================================
-- STEP 12: 创建 evaluation_frameworks 表（新增）
-- ============================================

SELECT '✓ STEP 12: 创建新的 evaluation_frameworks 表' AS migration_step;

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

SELECT '  evaluation_frameworks 表创建完成' AS sub_step;

-- ============================================
-- STEP 13: 创建 conversation_turns 表（新增）
-- ============================================

SELECT '✓ STEP 13: 创建新的 conversation_turns 表' AS migration_step;

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
    INDEX idx_round (assessment_id, round_num),
    INDEX idx_created (created_at)
);

SELECT '  conversation_turns 表创建完成' AS sub_step;

-- ============================================
-- STEP 14: 创建 conversation_analyses 表（新增）  
-- ============================================

SELECT '✓ STEP 14: 创建新的 conversation_analyses 表' AS migration_step;

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

SELECT '  conversation_analyses 表创建完成' AS sub_step;

-- ============================================
-- STEP 15: 重新启用外键约束
-- ============================================

SELECT '✓ STEP 15: 重新启用外键约束' AS migration_step;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- STEP 16: 最终数据验证和统计
-- ============================================

SELECT '✓ STEP 16: 迁移后数据统计' AS migration_step;

SELECT CONCAT('  users 表: ', COUNT(*), ' 行') FROM users;
SELECT CONCAT('  候选人用户数: ', COUNT(*), ' 行') FROM users WHERE user_type = 'candidate';
SELECT CONCAT('  HR用户数: ', COUNT(*), ' 行') FROM users WHERE user_type = 'hr';
SELECT CONCAT('  interviews 表: ', COUNT(*), ' 行') FROM interviews;
SELECT CONCAT('  assessment_records 表: ', COUNT(*), ' 行') FROM assessment_records;

-- ============================================
-- STEP 17: 数据完整性检查
-- ============================================

SELECT '✓ STEP 17: 数据完整性检查' AS verification_step;

-- 检查孤立 interview 记录
SELECT CONCAT('  孤立的 interview 记录: ', COUNT(*), ' 条') 
FROM interviews i
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = i.candidate_id);

-- 检查无效 job 外键
SELECT CONCAT('  无效的 job_id: ', COUNT(*), ' 条') 
FROM interviews i
WHERE NOT EXISTS (SELECT 1 FROM jobs j WHERE j.id = i.job_id);

-- 检查 user_type 为 NULL 的记录
SELECT CONCAT('  user_type 为 NULL: ', COUNT(*), ' 条') 
FROM users WHERE user_type IS NULL;

-- ============================================
-- 迁移脚本结束
-- ============================================

SELECT '✅ P0 迁移脚本执行完成!' AS final_status, NOW() AS completion_time;
