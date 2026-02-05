from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.hr_agent import Scenario, InterviewResponse, TraitScore, ScenarioSummary
from schemas import hr_agent as schemas_hr_agent
from schemas.hr_agent import (
    ScenarioSchema, FollowUpQuestionRequest, FollowUpQuestionResponse,
    ScoreAnswerRequest, ScoreAnswerResponse, TraitScoreSchema,
    InterviewResponseCreateSchema
)
from prompts.hr_agent_llm import hr_agent_llm
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/interview", tags=["HR-Agent"])


@router.get("/scenarios/{scenario_id}", response_model=ScenarioSchema)
async def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """获取情景描述"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="情景不存在")
    return scenario


@router.get("/scenarios", response_model=list[ScenarioSchema])
async def list_scenarios(db: Session = Depends(get_db)):
    """获取所有情景"""
    scenarios = db.query(Scenario).all()
    return scenarios


@router.post("/follow-up-question", response_model=FollowUpQuestionResponse)
async def generate_follow_up_question(
    request: FollowUpQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    生成追问问题
    
    Args:
        candidate_id: 候选人ID
        scenario_id: 情景ID
        round_num: 当前轮次
        previous_answers: 历史回答列表
    
    Returns:
        question: 追问问题
        reasoning: 追问理由
    """
    
    # 获取情景
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="情景不存在")
    
    # 检查轮次是否超过限制
    if request.round_num > scenario.max_rounds:
        raise HTTPException(status_code=400, detail="已达到最大轮次")
    
    # 调用 LLM 生成追问
    result = hr_agent_llm.generate_follow_up_question(
        scenario_description=scenario.description,
        target_traits=scenario.target_traits,
        previous_answers=request.previous_answers,
        round_num=request.round_num,
        max_rounds=scenario.max_rounds
    )
    
    return FollowUpQuestionResponse(
        question=result["question"],
        reasoning=result.get("reasoning")
    )


@router.post("/score-answer", response_model=ScoreAnswerResponse)
async def score_answer(
    request: ScoreAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    对回答进行评分
    
    Args:
        candidate_id: 候选人ID
        scenario_id: 情景ID
        response_id: 回答ID
        target_traits: 要评分的特质列表
        answer: 候选人的回答
    
    Returns:
        scores: 各特质评分
        reasoning: 评分理由
    """
    
    # 获取情景
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="情景不存在")
    
    # 获取所有历史回答
    all_responses = db.query(InterviewResponse).filter(
        InterviewResponse.candidate_id == request.candidate_id,
        InterviewResponse.scenario_id == request.scenario_id
    ).all()
    
    previous_answers = [
        {"question": r.question, "answer": r.answer}
        for r in all_responses
    ]
    
    # 调用 LLM 评分
    result = hr_agent_llm.score_answer(
        scenario_description=scenario.description,
        target_traits=request.target_traits,
        current_answer=request.answer,
        all_answers=previous_answers
    )
    
    # 保存评分到数据库
    for trait_name, score in result["scores"].items():
        trait_score = TraitScore(
            id=f"score_{uuid.uuid4().hex[:12]}",
            response_id=request.response_id,
            candidate_id=request.candidate_id,
            scenario_id=request.scenario_id,
            trait_name=trait_name,
            score=score,
            reasoning=result["reasoning"].get(trait_name, "")
        )
        db.add(trait_score)
    
    db.commit()
    
    return ScoreAnswerResponse(
        scores=result["scores"],
        reasoning=result["reasoning"]
    )


@router.post("/save-response")
async def save_response(
    request: schemas_hr_agent.InterviewResponseCreateSchema,
    db: Session = Depends(get_db)
):
    """
    保存一轮的回答记录
    
    Args:
        candidate_id: 候选人ID
        scenario_id: 情景ID
        round_num: 轮次号
        question: 问题内容
        answer: 回答内容
        answer_latency: 回答耗时（秒）
        emotion: 情感分析结果
    
    Returns:
        id: 回答记录ID
        message: 保存成功消息
    """
    
    # 验证情景是否存在
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="情景不存在")
    
    response = InterviewResponse(
        id=f"resp_{uuid.uuid4().hex[:12]}",
        candidate_id=request.candidate_id,
        scenario_id=request.scenario_id,
        round_num=request.round_num,
        question=request.question,
        answer=request.answer,
        answer_latency=request.answer_latency,
        emotion=request.emotion
    )
    
    db.add(response)
    db.commit()
    db.refresh(response)
    
    return {
        "id": response.id,
        "message": "回答已保存"
    }


@router.get("/scenario-summary/{candidate_id}/{scenario_id}")
async def get_scenario_summary(
    candidate_id: str,
    scenario_id: str,
    db: Session = Depends(get_db)
):
    """
    获取情景评估总结（所有特质的平均分）
    """
    
    # 获取所有评分
    scores = db.query(TraitScore).filter(
        TraitScore.candidate_id == candidate_id,
        TraitScore.scenario_id == scenario_id
    ).all()
    
    if not scores:
        raise HTTPException(status_code=404, detail="未找到评分记录")
    
    # 按特质分组计算平均分
    trait_averages = {}
    trait_reasonings = {}
    
    from collections import defaultdict
    trait_scores = defaultdict(list)
    trait_reasons = defaultdict(list)
    
    for score in scores:
        trait_scores[score.trait_name].append(score.score)
        trait_reasons[score.trait_name].append(score.reasoning or "")
    
    for trait, score_list in trait_scores.items():
        trait_averages[trait] = sum(score_list) / len(score_list)
        # 使用最后一条理由或汇总
        trait_reasonings[trait] = trait_reasons[trait][-1] if trait_reasons[trait] else ""
    
    return {
        "candidate_id": candidate_id,
        "scenario_id": scenario_id,
        "trait_averages": trait_averages,
        "trait_reasonings": trait_reasonings,
        "summary": f"候选人在该情景中表现综合评分为 {sum(trait_averages.values()) / len(trait_averages):.1f} 分"
    }
