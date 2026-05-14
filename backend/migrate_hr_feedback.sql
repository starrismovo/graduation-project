ALTER TABLE assessment_records
  ADD COLUMN feedback_status VARCHAR(30) NOT NULL DEFAULT 'pending',
  ADD COLUMN feedback_result VARCHAR(30) NULL,
  ADD COLUMN hr_feedback TEXT NULL,
  ADD COLUMN feedback_visible_to_candidate BOOLEAN NOT NULL DEFAULT TRUE,
  ADD COLUMN feedback_by INT NULL,
  ADD COLUMN feedback_at DATETIME NULL;

CREATE INDEX idx_assessment_records_feedback_status
  ON assessment_records (feedback_status);

ALTER TABLE assessment_records
  ADD CONSTRAINT fk_assessment_records_feedback_by
  FOREIGN KEY (feedback_by) REFERENCES users(id)
  ON DELETE SET NULL;
