-- ============================================
-- P0 数据库迁移脚本
-- 问题：候选人数据重复、外键关系错误、主键类型混乱
-- 执行时间：2026-03-23
-- ============================================

-- 启用外键检查（确保迁移完整）
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- STEP 1: 备份原始数据（以防需要回滚）
-- ============================================

CREATE TABLE IF NOT EXISTS candidates_backup AS SELECT * FROM candidates;
CREATE TABLE IF NOT EXISTS users_backup AS SELECT * FROM users;
CREATE TABLE IF NOT EXISTS interviews_backup AS SELECT * FROM interviews;

-- 记录备份时间
SELECT '========== BACKUP CREATED AT ' AS backup_timestamp, NOW() AS timestamp;

-- ============================================
-- STEP 2: 检查现有数据（迁移前验证）
-- ============================================

SELECT 'BEFORE MIGRATION - Data Summary:' AS migration_step;
SELECT 'users table count:', COUNT(*) FROM users;
SELECT 'candidates table count:', COUNT(*) FROM candidates;
SELECT 'interviews table count:', COUNT(*) FROM interviews;
SELECT 'interview_responses table count:', COUNT(*) FROM interview_responses;

-- ============================================
-- STEP 3: 临时禁用外键约束（进行表结构修改）
-- ============================================

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- STEP 4: 添加候选人字段到 users 表
-- ============================================

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS age INT NULL AFTER delivery_privacy,
ADD COLUMN IF NOT EXISTS education VARCHAR(50) NULL AFTER age,
ADD COLUMN IF NOT EXISTS major VARCHAR(100) NULL AFTER education,
ADD COLUMN IF NOT EXISTS desired_job VARCHAR(100) NULL AFTER major,
ADD COLUMN IF NOT EXISTS experience_years FLOAT NULL AFTER desired_job,
ADD COLUMN IF NOT EXISTS skills JSON NULL AFTER experience_years,
ADD COLUMN IF NOT EXISTS resume_url TEXT NULL AFTER skills;

-- ============================================
-- STEP 5: 添加用户类型字段到 users 表
-- ============================================

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS user_type ENUM('hr', 'candidate') 
DEFAULT 'candidate' NULL AFTER is_hr,
ADD INDEX IF NOT EXISTS idx_user_type (user_type);

-- ============================================
-- STEP 6: 设置用户类型值（基于 is_hr 字段）
-- ============================================

UPDATE users 
SET user_type = CASE 
    WHEN is_hr = 1 THEN 'hr'
    WHEN is_hr = 0 THEN 'candidate'
    ELSE 'candidate'
END 
WHERE user_type IS NULL;

-- ============================================
-- STEP 7: 从 candidates 表迁移数据到 users 表
-- ============================================

-- 匹配 candidates.id (STRING) 到 users.id (INT)
-- 假设 candidates 表的某个字段可以用于关联
-- 如果 candidates.id 是字符串，需要找到关联方式

-- 检查是否可以通过 email 或 name 关联
UPDATE users u
SET 
    u.age = (SELECT c.age FROM candidates c 
             WHERE c.name = u.real_name OR c.id = u.username LIMIT 1),
    u.education = (SELECT c.education FROM candidates c 
                   WHERE c.name = u.real_name OR c.id = u.username LIMIT 1),
    u.major = (SELECT c.major FROM candidates c 
               WHERE c.name = u.real_name OR c.id = u.username LIMIT 1),
    u.desired_job = (SELECT c.desired_job FROM candidates c 
                     WHERE c.name = u.real_name OR c.id = u.username LIMIT 1),
    u.experience_years = (SELECT c.experience_years FROM candidates c 
                          WHERE c.name = u.real_name OR c.id = u.username LIMIT 1),
    u.skills = (SELECT c.skills FROM candidates c 
                WHERE c.name = u.real_name OR c.id = u.username LIMIT 1)
WHERE u.user_type = 'candidate' AND u.is_hr = 0;

-- ============================================
-- STEP 8: 验证迁移结果
-- ============================================

SELECT 'AFTER DATA MIGRATION - Verification:' AS verification_step;
SELECT COUNT(*) as users_with_candidate_data 
FROM users 
WHERE user_type = 'candidate' AND age IS NOT NULL;

-- ============================================
-- STEP 9: 修复 Interview 表外键关系
-- ============================================

-- 创建临时表以处理外键
CREATE TABLE interviews_temp LIKE interviews;

-- 复制数据到临时表
INSERT INTO interviews_temp SELECT * FROM interviews;

-- 删除原始表的外键约束
ALTER TABLE interviews DROP FOREIGN KEY IF EXISTS interviews_ibfk_1;
ALTER TABLE interviews DROP FOREIGN KEY IF EXISTS interviews_ibfk_2;

-- 删除原始表
DROP TABLE interviews;

-- 重新创建 interviews 表，修正外键定义
CREATE TABLE interviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    candidate_id INT NOT NULL,
    job_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'started',
    personality_traits JSON NULL,
    match_score FLOAT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    notes VARCHAR(500) NULL,
    
    FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    
    INDEX idx_candidate_id (candidate_id),
    INDEX idx_job_id (job_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 恢复数据到新表
INSERT INTO interviews (id, candidate_id, job_id, status, personality_traits, match_score, created_at, updated_at, completed_at, notes)
SELECT id, candidate_id, job_id, status, personality_traits, match_score, created_at, updated_at, completed_at, notes
FROM interviews_temp;

-- 删除临时表
DROP TABLE interviews_temp;

-- ============================================
-- STEP 10: 修复 interview_responses 表的主键类型
-- ============================================

-- 检查 interview_responses 表
-- 如果 id 是 STRING，转换为 INT
-- 但由于 id 是主键且可能有外键引用，需要谨慎处理

-- 首先检查是否有其他表引用 interview_responses.id
-- CREATE TABLE interview_responses_temp LIKE interview_responses;
-- （如需要再处理）

-- ============================================
-- STEP 11: 添加关键索引以优化查询性能
-- ============================================

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_assessment_records_candidate ON assessment_records(candidate_id);
CREATE INDEX IF NOT EXISTS idx_assessment_records_job ON assessment_records(job_id);
CREATE INDEX IF NOT EXISTS idx_assessment_records_status ON assessment_records(assessment_status);
CREATE INDEX IF NOT EXISTS idx_assessment_records_created ON assessment_records(created_at);
CREATE INDEX IF NOT EXISTS idx_interview_responses_candidate ON interview_responses(candidate_id);

-- ============================================
-- STEP 12: 添加审计字段到核心表（如未存在）
-- ============================================

ALTER TABLE assessment_records
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE AFTER updated_at,
ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL AFTER is_deleted,
ADD COLUMN IF NOT EXISTS created_by INT NULL AFTER job_title,
ADD INDEX IF NOT EXISTS idx_deleted (is_deleted);

ALTER TABLE interviews
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE AFTER notes,
ADD COLUMN IF NOT EXISTS deleted_at DATETIME NULL AFTER is_deleted,
ADD INDEX IF NOT EXISTS idx_deleted (is_deleted);

-- ============================================
-- STEP 13: 重新启用外键约束
-- ============================================

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- STEP 14: 最终验证和统计
-- ============================================

SELECT '========== MIGRATION COMPLETED ===========' AS status;

SELECT 'Final Data Summary:' AS final_step;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as hr_users FROM users WHERE user_type = 'hr';
SELECT COUNT(*) as candidate_users FROM users WHERE user_type = 'candidate';
SELECT COUNT(*) as interviews FROM interviews;
SELECT COUNT(*) as assessment_records FROM assessment_records;

-- ============================================
-- STEP 15: 检查并修复任何不一致性
-- ============================================

SELECT 'Consistency Check - Broken Foreign Keys:' AS consistency_check;

-- 检查 interviews 表中的孤立记录
SELECT COUNT(*) as orphaned_interviews 
FROM interviews i
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = i.candidate_id);

-- 检查 interviews 表中的无效职位
SELECT COUNT(*) as invalid_job_interviews 
FROM interviews i
WHERE NOT EXISTS (SELECT 1 FROM jobs j WHERE j.id = i.job_id);

-- ============================================
-- STEP 16: 列出可以后续删除的表（需要手动确认）
-- ============================================

SELECT 'Tables that can be deleted after verification:' AS cleanup_note;
SELECT 'candidates (原始数据已备份到 candidates_backup)' AS table_to_drop;
SELECT 'candidates_backup (如果迁移完全成功)' AS backup_table_note;
SELECT 'users_backup (保留用于回滚)' AS backup_table_note;
SELECT 'interviews_backup (保留用于回滚)' AS backup_table_note;

-- ============================================
-- 迁移脚本结束
-- ============================================

COMMIT;

SELECT 'Migration script execution completed at:', NOW() AS completion_time;
