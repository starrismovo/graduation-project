"""Models package"""
# Direct imports for main models
from .user import User, UserType
from .job import Job
from .interview import Interview
from .assessment import (
    AssessmentRecord,
    CandidatePersonalityProfile,
    AssessmentMatchAnalysis,
    PersonalityTraitDescription
)
from .hr_agent import (
    Scenario,
    InterviewResponse,
    TraitScore,
    ScenarioSummary
)
from .evaluation_framework import EvaluationFramework
from .conversation import ConversationTurn, ConversationAnalysis

__all__ = [
    "User", "UserType",
    "Job",
    "Interview",
    "AssessmentRecord",
    "CandidatePersonalityProfile",
    "AssessmentMatchAnalysis",
    "PersonalityTraitDescription",
    "Scenario",
    "InterviewResponse",
    "TraitScore",
    "ScenarioSummary",
    "EvaluationFramework",
    "ConversationTurn",
    "ConversationAnalysis"
]

