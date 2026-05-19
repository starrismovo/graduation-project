from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv
import os
from database import Base, engine
from models.user import User
from models.job import Job
from models.interview import Interview
from models.candidate import Candidate
from models.hr_agent import Scenario, InterviewResponse, TraitScore, ScenarioSummary
from models.assessment import AssessmentRecord, CandidatePersonalityProfile, AssessmentMatchAnalysis, PersonalityTraitDescription
from models.job_requirement import JobRequirementTag, JobSkillRequirement, JobPersonalityFramework, CandidateJobApplication
from models.saved_job import SavedJob
from models.hr_invitation import HRInvitation
from routers.auth import router as auth_router
from routers.job import router as job_router
from routers.interview import router as interview_router
from routers.candidate import router as candidate_router
from routers.assessment import router as assessment_router
from routers.user import router as user_router
from routers.immersive_dialogue import router as immersive_dialogue_router
from routers.job_requirements import router as job_requirements_router
from routers.saved_job import router as saved_job_router
from routers.hr_invitation import router as hr_invitation_router
from services.user_settings_service import ensure_notification_columns

# 加载环境变量
load_dotenv()

app = FastAPI(title="人岗匹配心理评估系统后端")

# CORS 配置 - 必须在路由之前添加
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 创建所有表
Base.metadata.create_all(bind=engine)
ensure_notification_columns(engine)

# 引入路由
app.include_router(auth_router)
app.include_router(job_router)
app.include_router(interview_router)
app.include_router(candidate_router)
app.include_router(assessment_router)
app.include_router(user_router)
app.include_router(immersive_dialogue_router)
app.include_router(job_requirements_router)
app.include_router(saved_job_router)
app.include_router(hr_invitation_router)

@app.on_event("startup")
async def preload_ocr_models():
    if os.getenv("OCR_PRELOAD", "1").lower() not in {"0", "false", "no"}:
        from paddleocr_local import preload_paddleocr_async
        preload_paddleocr_async()

@app.get("/")
def read_root():
    return {"message": "人岗匹配心理评估系统后端已启动！", "docs": "/docs"}
