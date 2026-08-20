"""User authentication and profile management router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import build_session, get_or_create_user
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, SessionResponse, UserListItem

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/users", response_model=list[UserListItem])
def list_users(db: Session = Depends(get_db)):
    """List all registered and demo users for 1-click account switching."""
    users = db.query(User).order_by(User.created_at.desc(), User.id.desc()).all()
    return [
        UserListItem(
            id=u.id,
            name=u.name,
            email=u.email,
            target_role=u.target_role,
            is_sample=u.is_sample,
            created_at=u.created_at.isoformat() if u.created_at else None,
        )
        for u in users
    ]


@router.post("/register", response_model=SessionResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new learner account."""
    if payload.email:
        existing = db.query(User).filter(User.email == payload.email.strip().lower()).first()
        if existing:
            return build_session(db=db, user=existing)

    user = User(
        name=payload.name.strip()[:200],
        email=payload.email.strip().lower()[:255] if payload.email else None,
        target_role=payload.target_role.strip()[:200],
        is_sample=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_session(db=db, user=user)


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Log in by user ID, email, or name."""
    user = None
    if payload.user_id:
        user = db.get(User, payload.user_id)
    elif payload.email:
        user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    elif payload.name:
        user = db.query(User).filter(User.name.ilike(f"%{payload.name.strip()}%")).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User account not found")

    return build_session(db=db, user=user)
