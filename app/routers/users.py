"""User & Candidate Management Router — RESTful CRUD, Resume Upload & AI Analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from sqlalchemy.orm import Session

from app.crud import (
    create_user_with_resume,
    delete_user_by_id,
    get_all_users_summary,
    get_candidate_analysis_data,
    get_candidate_resume_data,
    get_user_profile,
    reanalyze_user_resume,
    update_user_details,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    CandidateAnalysisResponse,
    CandidateResumeResponse,
    UserProfileDetail,
    UserSummaryItem,
    UserUpdateRequest,
)

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/users", response_model=list[UserSummaryItem])
def list_candidates(db: Session = Depends(get_db)):
    """List all candidate profiles stored in the database."""
    return get_all_users_summary(db)


@router.post("/users", response_model=UserProfileDetail)
async def create_candidate(
    name: str = Form(..., description="Candidate Full Name (e.g. Rahul Sharma)"),
    target_role: str = Form("Software Engineer", description="Target position / Job title"),
    email: str = Form("", description="Candidate email address"),
    file: UploadFile | None = File(None, description="Resume file (.pdf or .docx)"),
    db: Session = Depends(get_db),
):
    """Create a new candidate, extract resume text (PDF or DOCX), generate structured AI insights, and persist."""
    file_bytes = None
    filename = ""

    if file and file.filename:
        filename = file.filename
        file_bytes = await file.read()

    try:
        user = create_user_with_resume(
            db=db,
            name=name,
            target_role=target_role,
            email=email if email.strip() else None,
            file_bytes=file_bytes,
            filename=filename,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process candidate resume: {exc}")

    profile = get_user_profile(db=db, user_id=user.id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Candidate profile could not be retrieved")
    return profile


@router.get("/users/{user_id}", response_model=UserProfileDetail)
def get_candidate(
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Retrieve full candidate profile, extracted resume, structured AI insights, and interview questions."""
    profile = get_user_profile(db=db, user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return profile


@router.put("/users/{user_id}", response_model=UserProfileDetail)
def update_candidate(
    payload: UserUpdateRequest,
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Update candidate name, position, or email."""
    updated = update_user_details(
        db=db,
        user_id=user_id,
        name=payload.name,
        target_role=payload.target_role,
        email=payload.email,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return get_user_profile(db=db, user_id=user_id)


@router.delete("/users/{user_id}")
def delete_candidate(
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Delete candidate and all associated resumes, attempts, and skill gaps."""
    success = delete_user_by_id(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"status": "deleted", "id": user_id, "message": "Candidate successfully deleted"}


@router.post("/users/{user_id}/resume", response_model=UserProfileDetail)
async def upload_candidate_resume(
    user_id: int = Path(..., description="Unique user identifier"),
    file: UploadFile = File(..., description="Updated resume (.pdf or .docx)"),
    db: Session = Depends(get_db),
):
    """Replace/update candidate's resume, extract new text, and re-run Gemini AI analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No resume file provided.")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    file_bytes = await file.read()
    try:
        create_user_with_resume(
            db=db,
            name=user.name,
            target_role=user.target_role,
            email=user.email,
            file_bytes=file_bytes,
            filename=file.filename,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume update failed: {exc}")

    return get_user_profile(db=db, user_id=user_id)


@router.get("/users/{user_id}/resume", response_model=CandidateResumeResponse)
def get_candidate_resume(
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Retrieve raw extracted resume document data and skills for a candidate."""
    resume_data = get_candidate_resume_data(db=db, user_id=user_id)
    if resume_data is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return resume_data


@router.get("/users/{user_id}/analysis", response_model=CandidateAnalysisResponse)
def get_candidate_analysis(
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Retrieve stored Gemini AI structured insights for a candidate."""
    analysis_data = get_candidate_analysis_data(db=db, user_id=user_id)
    if analysis_data is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return analysis_data


@router.post("/users/{user_id}/reanalyze", response_model=UserProfileDetail)
@router.post("/users/{user_id}/analyze", response_model=UserProfileDetail)
def reanalyze_candidate(
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Re-run Gemini AI analysis on the candidate's latest resume."""
    profile = reanalyze_user_resume(db=db, user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Candidate not found or has no resume")
    return profile
