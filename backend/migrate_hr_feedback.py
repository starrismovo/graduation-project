"""
Add HR feedback columns to assessment_records.

This migration is intentionally idempotent for late-stage project demos:
it checks the current MySQL schema first and only adds missing columns.
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured in backend/.env")


def column_exists(conn, column_name: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'assessment_records'
              AND COLUMN_NAME = :column_name
            """
        ),
        {"column_name": column_name},
    )
    return result.scalar() > 0


def index_exists(conn, index_name: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'assessment_records'
              AND INDEX_NAME = :index_name
            """
        ),
        {"index_name": index_name},
    )
    return result.scalar() > 0


def constraint_exists(conn, constraint_name: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'assessment_records'
              AND CONSTRAINT_NAME = :constraint_name
            """
        ),
        {"constraint_name": constraint_name},
    )
    return result.scalar() > 0


def main() -> None:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    columns = {
        "feedback_status": "ALTER TABLE assessment_records ADD COLUMN feedback_status VARCHAR(30) NOT NULL DEFAULT 'pending'",
        "feedback_result": "ALTER TABLE assessment_records ADD COLUMN feedback_result VARCHAR(30) NULL",
        "hr_feedback": "ALTER TABLE assessment_records ADD COLUMN hr_feedback TEXT NULL",
        "feedback_visible_to_candidate": "ALTER TABLE assessment_records ADD COLUMN feedback_visible_to_candidate BOOLEAN NOT NULL DEFAULT TRUE",
        "feedback_by": "ALTER TABLE assessment_records ADD COLUMN feedback_by INT NULL",
        "feedback_at": "ALTER TABLE assessment_records ADD COLUMN feedback_at DATETIME NULL",
    }

    with engine.begin() as conn:
        for column_name, ddl in columns.items():
            if column_exists(conn, column_name):
                print(f"skip column: {column_name}")
                continue
            conn.execute(text(ddl))
            print(f"added column: {column_name}")

        index_name = "idx_assessment_records_feedback_status"
        if not index_exists(conn, index_name):
            conn.execute(text(f"CREATE INDEX {index_name} ON assessment_records (feedback_status)"))
            print(f"added index: {index_name}")
        else:
            print(f"skip index: {index_name}")

        constraint_name = "fk_assessment_records_feedback_by"
        if not constraint_exists(conn, constraint_name):
            conn.execute(
                text(
                    """
                    ALTER TABLE assessment_records
                    ADD CONSTRAINT fk_assessment_records_feedback_by
                    FOREIGN KEY (feedback_by) REFERENCES users(id)
                    ON DELETE SET NULL
                    """
                )
            )
            print(f"added constraint: {constraint_name}")
        else:
            print(f"skip constraint: {constraint_name}")

    print("HR feedback migration completed.")


if __name__ == "__main__":
    main()
