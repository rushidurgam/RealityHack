"""POST /api/demo/load-sample — load pre-seeded multi-resume demo session."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import build_session
from app.database import get_db
from app.schemas import SessionResponse
from app.seed import get_or_seed_sample_user

router = APIRouter(prefix="/api", tags=["demo"])


@router.post("/demo/load-sample", response_model=SessionResponse)
def load_sample_demo(db: Session = Depends(get_db)):
    """Seed / reset rich sample demo user with 3 historical resume versions and active sprint."""
    user = get_or_seed_sample_user(db=db)
    session_data = build_session(db=db, user=user)
    return session_data
