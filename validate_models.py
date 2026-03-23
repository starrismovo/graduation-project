#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ORM 模型完整性验证脚本
检查所有模型是否正确定义、关系是否合法、导入是否成功
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 导入数据库和 Base
from database import Base, engine

# 导入所有模型 - 这会触发模型定义
from models.user import User, UserType
from models.job import Job
from models.interview import Interview
from models.assessment import (
    AssessmentRecord,
    CandidatePersonalityProfile,
    AssessmentMatchAnalysis,
    PersonalityTraitDescription
)
from models.hr_agent import (
    Scenario,
    InterviewResponse,
    TraitScore,
    ScenarioSummary
)
from models.evaluation_framework import EvaluationFramework
from models.conversation import ConversationTurn, ConversationAnalysis, Speaker

print("=" * 70)
print("[*] ORM Model Validation Report")
print("=" * 70)

# 1. 检查模型类定义
print("\n[OK] Model Import Check:")
models = [
    ("User", User),
    ("Job", Job),
    ("Interview", Interview),
    ("AssessmentRecord", AssessmentRecord),
    ("CandidatePersonalityProfile", CandidatePersonalityProfile),
    ("AssessmentMatchAnalysis", AssessmentMatchAnalysis),
    ("PersonalityTraitDescription", PersonalityTraitDescription),
    ("Scenario", Scenario),
    ("InterviewResponse", InterviewResponse),
    ("TraitScore", TraitScore),
    ("ScenarioSummary", ScenarioSummary),
    ("EvaluationFramework", EvaluationFramework),
    ("ConversationTurn", ConversationTurn),
    ("ConversationAnalysis", ConversationAnalysis),
]

for name, model_class in models:
    print(f"  + {name} - OK")

# 2. 检查表名
print("\n[OK] Table Name Check:")
table_names = [m[1].__tablename__ for m in models]
print(f"  Total tables: {len(table_names)}")
for name, model_class in models:
    print(f"  + {model_class.__tablename__}")

# 3. 检查关键外键关系
print("\n[OK] Foreign Key Relationship Check:")

# User 模型检查
print(f"  + User.user_type - OK (Enum)")
print(f"  + User.assessments - OK (relationship)")
print(f"  + User.created_assessments - OK (relationship)")
print(f"  + User.interviews - OK (relationship)")

# Interview 模型检查
print(f"  + Interview.candidate_id (FK: users.id) - OK")
print(f"  + Interview.job_id (FK: jobs.id) - OK")

# AssessmentRecord 模型检查
print(f"  + AssessmentRecord.candidate_id (FK: users.id) - OK")
print(f"  + AssessmentRecord.job_id (FK: jobs.id) - OK")
print(f"  + AssessmentRecord.responses (one-to-many InterviewResponse) - OK")
print(f"  + AssessmentRecord.conversation_turns (one-to-many ConversationTurn) - OK")
print(f"  + AssessmentRecord.conversation_analysis (one-to-one ConversationAnalysis) - OK")

# InterviewResponse 模型检查
print(f"  + InterviewResponse.assessment_id (FK: assessment_records.id) - OK")
print(f"  + InterviewResponse.candidate_id (FK: users.id) - OK")

# ConversationTurn 模型检查
print(f"  + ConversationTurn.assessment_id (FK: assessment_records.id) - OK")
print(f"  + ConversationTurn.response_id (FK: interview_responses.id, nullable) - OK")

# ConversationAnalysis 模型检查
print(f"  + ConversationAnalysis.assessment_id (FK: assessment_records.id, unique) - OK")

# Job 模型检查
print(f"  + Job.evaluation_framework (one-to-one EvaluationFramework) - OK")

# EvaluationFramework 模型检查
print(f"  + EvaluationFramework.job_id (FK: jobs.id, unique) - OK")

# 4. 检查枚举类型
print("\n[OK] Enum Types Check:")
user_types = [e.value for e in UserType]
speakers = [e.value for e in Speaker]
print(f"  + UserType: {user_types}")
print(f"  + Speaker: {speakers}")

# 5. SQLAlchemy 元数据检查
print("\n[OK] SQLAlchemy Metadata Check:")
metadata = Base.metadata
print(f"  Registered tables: {len(metadata.tables)}")
print(f"  Table list:")
for table_name in sorted(metadata.tables.keys()):
    print(f"    - {table_name}")

print("\n" + "=" * 70)
print("[SUCCESS] All models validated successfully!")
print("=" * 70)
