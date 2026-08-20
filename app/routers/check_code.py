"""POST /api/check-code — AI agent evaluates student code with 0-100 rubric score and persists attempt."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import persist_attempt
from app.database import get_db
from app.schemas import CheckCodeRequest, CheckCodeResponse
from app.services.agents import evaluate_practice_attempt_agent

router = APIRouter(prefix="/api", tags=["check-code"])


@router.post("/check-code", response_model=CheckCodeResponse)
def grade_code(payload: CheckCodeRequest, db: Session = Depends(get_db)):
    """Evaluate submitted code safely via AI agent, compute 0-100 score + rubric, and persist attempt."""
    result = evaluate_practice_attempt_agent(
        submitted_code=payload.submitted_code,
        solution_code=payload.solution_code,
        concept=payload.concept,
    )

    attempt_id = None
    if payload.lesson_id:
        persisted = persist_attempt(
            db=db,
            lesson_id=payload.lesson_id,
            submitted=payload.submitted_code,
            result=result,
        )
        attempt_id = persisted.id

    rubric = result.get("rubric") or {}

    return CheckCodeResponse(
        id=attempt_id,
        passed=bool(result.get("passed")),
        hint=str(result.get("hint") or ""),
        score=float(result.get("score") or 0),
        rubric={
            "correctness": int(rubric.get("correctness") or 0),
            "code_quality": int(rubric.get("code_quality") or 0),
            "concept_match": int(rubric.get("concept_match") or 0),
        },
        evaluation=result,
    )
