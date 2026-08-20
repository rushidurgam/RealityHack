"""Session restore, history, and resume queries for SkillBridge AI."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import build_session, gap_dicts, get_gaps_for_resume, get_or_create_user, history_for_user
from app.database import get_db
from app.models import Resume, User
from app.schemas import HistoryResponse, MissingSkill, SessionResponse

router = APIRouter(prefix="/api", tags=["session"])


@router.get("/session/latest", response_model=SessionResponse)
def get_latest_session(
    user_id: int | None = Query(None, description="User ID to restore (or most recently active user)"),
    db: Session = Depends(get_db),
):
    """Restore complete application state across page reloads."""
    user = None
    if user_id is not None:
        user = db.get(User, user_id)

    if user is None:
        # Pick the most recently active user
        user = db.query(User).order_by(User.created_at.desc(), User.id.desc()).first()

    if user is None:
        user = get_or_create_user(db=db, user_id=None, name="Demo User")

    session_data = build_session(db=db, user=user)
    return session_data


@router.get("/history", response_model=HistoryResponse)
def get_user_history(
    user_id: int | None = Query(None, description="User ID for historical analysis (or latest active user)"),
    db: Session = Depends(get_db),
):
    """Retrieve timeline of analyzed resumes, gap trends over time, and practice stats."""
    user = None
    if user_id is not None:
        user = db.get(User, user_id)

    if user is None:
        user = db.query(User).order_by(User.created_at.desc(), User.id.desc()).first()

    if user is None:
        return HistoryResponse(
            user_id=None,
            resumes=[],
            gap_trends={},
            average_practice_score=0,
            total_attempts=0,
        )

    return history_for_user(db=db, user_id=user.id)


@router.get("/resumes/{resume_id}/gaps", response_model=list[MissingSkill])
def get_resume_gaps(resume_id: int, db: Session = Depends(get_db)):
    """Retrieve ranked skill gaps associated with a specific resume analysis."""
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    gaps = get_gaps_for_resume(db=db, resume_id=resume_id)
    return gap_dicts(gaps)
