"""User & Candidate Management Router — RESTful CRUD, Resume Upload & AI Analysis."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Path, UploadFile
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
    AssessPositionRequest,
    CandidateAnalysisResponse,
    CandidateResumeResponse,
    OccupationalRiskResponse,
    UserCreateRequest,
    UserProfileDetail,
    UserSummaryItem,
    UserUpdateRequest,
)
from app.services.gemini import calculate_automation_risk_and_shielded_score

router = APIRouter(prefix="/api", tags=["users"])


@router.post("/users/assess-position", response_model=OccupationalRiskResponse)
def assess_position_risk(payload: AssessPositionRequest):
    """Assess dynamic Automation Risk and Shielded Score for a candidate's position."""
    result = calculate_automation_risk_and_shielded_score(
        position=payload.position,
        resume_text=payload.resume_text,
        country=payload.country,
    )
    return result


@router.get("/users", response_model=list[UserSummaryItem])
def list_candidates(db: Session = Depends(get_db)):
    """List all candidate profiles stored in the database."""
    return get_all_users_summary(db)


@router.post("/users", response_model=UserProfileDetail)
async def create_candidate_json(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new candidate from structured JSON data and persist to DB."""
    try:
        user = create_user_with_resume(
            db=db,
            name=payload.name,
            target_role=payload.target_role,
            position=payload.position or payload.target_role,
            country=payload.country,
            country_code=payload.country_code,
            currency=payload.currency,
            currency_code=payload.currency_code,
            currency_symbol=payload.currency_symbol,
            email=payload.email,
            current_role=payload.current_role,
            location=payload.location,
            avatar=payload.avatar,
            current_salary=payload.current_salary,
            target_salary=payload.target_salary,
            experience_years=payload.experience_years,
            automation_risk_score=payload.automation_risk_score,
            shielded_risk_score=payload.shielded_risk_score,
            automation_risk_explanation=payload.automation_risk_explanation,
            tasks_at_risk=payload.tasks_at_risk,
            skills_radar=payload.skills_radar,
            salary_growth=payload.salary_growth,
            translated_skills=payload.translated_skills,
            raw_text=payload.raw_text,
        )

    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create candidate: {exc}")

    profile = get_user_profile(db=db, user_id=user.id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Candidate profile could not be retrieved")
    return profile


@router.post("/users/upload", response_model=UserProfileDetail)
async def create_candidate_with_file(
    name: str = Form(..., description="Candidate Full Name (e.g. Rahul Sharma)"),
    target_role: str = Form("AI Operations & Support Systems Specialist", description="Target position / Job title"),
    position: str = Form("", description="Target Position"),
    country: str = Form("United States", description="Candidate Country"),
    country_code: str = Form("US", description="ISO Country Code"),
    currency: str = Form("US Dollar", description="Country Currency"),
    currency_code: str = Form("USD", description="Currency Code"),
    currency_symbol: str = Form("$", description="Currency Symbol"),
    email: str = Form("", description="Candidate email address"),
    current_role: str = Form("Customer Support Team Lead", description="Current job role"),
    location: str = Form("Austin, TX (or Remote)", description="Location"),
    current_salary: str = Form("$52,000", description="Current salary"),
    target_salary: str = Form("$89,000", description="Target salary"),
    file: UploadFile | None = File(None, description="Resume file (.pdf or .docx)"),
    db: Session = Depends(get_db),
):
    """Create a new candidate with optional uploaded resume file (.pdf or .docx) and country awareness."""
    file_bytes = None
    filename = ""

    if file and file.filename:
        filename = file.filename
        file_bytes = await file.read()

    chosen_role = position.strip() or target_role.strip() or "AI Systems Specialist"

    try:
        user = create_user_with_resume(
            db=db,
            name=name,
            target_role=chosen_role,
            position=chosen_role,
            country=country,
            country_code=country_code,
            currency=currency,
            currency_code=currency_code,
            currency_symbol=currency_symbol,
            email=email if email.strip() else None,
            current_role=current_role,
            location=location,
            current_salary=current_salary,
            target_salary=target_salary,
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
    """Update candidate profile details and persist to DB."""
    updated = update_user_details(
        db=db,
        user_id=user_id,
        name=payload.name,
        target_role=payload.target_role,
        position=payload.position,
        country=payload.country,
        country_code=payload.country_code,
        currency=payload.currency,
        currency_code=payload.currency_code,
        currency_symbol=payload.currency_symbol,
        email=payload.email,
        current_role=payload.current_role,
        location=payload.location,
        avatar=payload.avatar,
        current_salary=payload.current_salary,
        target_salary=payload.target_salary,
        experience_years=payload.experience_years,
        automation_risk_score=payload.automation_risk_score,
        shielded_risk_score=payload.shielded_risk_score,
        automation_risk_explanation=payload.automation_risk_explanation,
        tasks_at_risk=payload.tasks_at_risk,
        skills_radar=payload.skills_radar,
        salary_growth=payload.salary_growth,
        translated_skills=payload.translated_skills,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return get_user_profile(db=db, user_id=user_id)


@router.delete("/users/{user_id}")
def delete_candidate(
    user_id: int = Path(..., description="Unique user identifier"),
    db: Session = Depends(get_db),
):
    """Delete candidate and all associated resumes, attempts, and skill gaps from DB."""
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
            position=user.position,
            country=user.country,
            country_code=user.country_code,
            currency=user.currency,
            currency_code=user.currency_code,
            currency_symbol=user.currency_symbol,
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
