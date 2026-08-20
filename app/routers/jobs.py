"""GET /api/jobs — search live jobs (Adzuna) with role-aware sample fallback, persisted to DB."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import get_or_create_user, job_dicts, persist_jobs
from app.database import get_db
from app.schemas import JobPosting
from app.services.adzuna import search_jobs_for_role

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs", response_model=list[JobPosting])
def get_jobs(
    role: str = Query(..., min_length=2, max_length=100, description="Target job title"),
    location: str = Query("United States", min_length=2, max_length=100),
    user_id: int | None = Query(None),
    resume_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """Search and cache job postings. Returns a flat list of postings directly usable by frontend."""
    raw_jobs = search_jobs_for_role(role=role, location=location)

    user = get_or_create_user(db=db, user_id=user_id, target_role=role)
    persisted = persist_jobs(
        db=db,
        user=user,
        resume_id=resume_id,
        role=role,
        location=location,
        jobs=raw_jobs,
        source="adzuna" if raw_jobs and raw_jobs[0].source == "adzuna" else "sample",
    )

    return job_dicts(persisted)
