"""POST /api/upload — accept a PDF, extract text, and persist to database."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import create_resume, get_or_create_user
from app.database import get_db
from app.schemas import ResumeSaveRequest, UploadResponse
from app.services.agents import extract_resume_skills
from app.services.pdf import extract_text_from_pdf

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(..., description="Resume or syllabus PDF"),
    name: str = Form("Demo User"),
    target_role: str = Form(""),
    user_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    """Store extracted PDF text on a new or existing user, create a Resume row, and return parsed skills."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid .pdf file.")

    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        max_mb = settings.max_upload_bytes // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"PDF is too large. Max size is {max_mb} MB.")

    try:
        extracted = extract_text_from_pdf(raw)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read or parse the provided PDF document.") from exc

    if not extracted:
        extracted = "(No extractable text found - the PDF may contain scanned images only.)"
    extracted = extracted[: settings.max_text_chars]

    user = get_or_create_user(db=db, user_id=user_id, name=name, target_role=target_role)
    resume = create_resume(db=db, user=user, raw_text=extracted)
    parsed_skills = extract_resume_skills(extracted)

    return UploadResponse(
        user_id=user.id,
        resume_id=resume.id,
        name=user.name,
        target_role=user.target_role,
        extracted_text=extracted,
        parsed_skills=parsed_skills,
    )


@router.post("/resume/save", response_model=UploadResponse)
def save_resume_text(
    payload: ResumeSaveRequest,
    db: Session = Depends(get_db),
):
    """Persist pasted/edited resume text directly into the database."""
    user = get_or_create_user(
        db=db,
        user_id=payload.user_id,
        name=payload.name,
        target_role=payload.target_role,
    )
    resume = create_resume(db=db, user=user, raw_text=payload.raw_text)
    parsed_skills = extract_resume_skills(payload.raw_text)

    return UploadResponse(
        user_id=user.id,
        resume_id=resume.id,
        name=user.name,
        target_role=user.target_role,
        extracted_text=payload.raw_text,
        parsed_skills=parsed_skills,
    )
