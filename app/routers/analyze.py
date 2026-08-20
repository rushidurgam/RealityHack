"""POST /api/analyze — AI agent matches resume vs target jobs, computes gaps & learning path, and persists to DB."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import (
    coverage_percent,
    create_resume,
    gap_dicts,
    get_or_create_user,
    persist_gaps,
    upsert_learning_path,
)
from app.database import get_db
from app.models import Resume
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.agents import (
    analyze_skill_gaps_agent,
    extract_resume_skills,
    generate_learning_path_agent,
)

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze skill gaps between resume and jobs, generate learning path, and persist to database."""
    user = get_or_create_user(
        db=db,
        user_id=payload.user_id,
        name=payload.name,
        target_role=payload.target_role,
    )

    resume = None
    if payload.resume_id:
        resume = db.get(Resume, payload.resume_id)

    if resume is None or resume.raw_text != payload.resume_text:
        resume = create_resume(db=db, user=user, raw_text=payload.resume_text)

    # Invoke agent orchestration
    gaps_raw = analyze_skill_gaps_agent(
        payload.resume_text,
        payload.job_descriptions,
        target_role=payload.target_role,
    )
    parsed_skills = extract_resume_skills(payload.resume_text)

    # Persist gaps in DB
    persisted_gaps = persist_gaps(db=db, user=user, resume=resume, gaps=gaps_raw)

    # Generate and persist structured learning path
    learning_path_raw = generate_learning_path_agent(gaps_raw)
    upsert_learning_path(db=db, resume_id=resume.id, items=learning_path_raw)

    coverage = coverage_percent(parsed_skills, len(persisted_gaps))

    return AnalyzeResponse(
        user_id=user.id,
        resume_id=resume.id,
        parsed_skills=parsed_skills,
        coverage_percent=coverage,
        gaps=gap_dicts(persisted_gaps),  # type: ignore
        learning_path=learning_path_raw,  # type: ignore
    )
