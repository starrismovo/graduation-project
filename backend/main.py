from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from database import Base, engine
from models.user import User
from models.job import Job
from models.interview import Interview
from models.candidate import Candidate
from models.hr_agent import Scenario, InterviewResponse, TraitScore, ScenarioSummary
from models.assessment import AssessmentRecord, CandidatePersonalityProfile, AssessmentMatchAnalysis, PersonalityTraitDescription
from routers.auth import router as auth_router
from routers.job import router as job_router
from routers.interview import router as interview_router
from routers.candidate import router as candidate_router
from routers.hr_agent import router as hr_agent_router
from routers.assessment import router as assessment_router
from routers.interviewer import router as interviewer_router

app = FastAPI(title="人岗匹配心理评估系统后端")

# CORS 配置 - 必须在路由之前添加
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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

# 引入路由
app.include_router(auth_router)
app.include_router(job_router)
app.include_router(interview_router)
app.include_router(candidate_router)
app.include_router(hr_agent_router)
app.include_router(assessment_router)
app.include_router(interviewer_router)

@app.get("/")
def read_root():
    return {"message": "人岗匹配心理评估系统后端已启动！", "docs": "/docs"}
