"""GET /api/proof/{user_identifier} — Verified proof-of-work public telemetry profile."""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.crud import get_proof_profile
from app.database import get_db
from app.schemas import ProofProfileResponse

router = APIRouter(prefix="/api", tags=["proof"])


@router.get("/proof/{user_identifier}", response_model=ProofProfileResponse)
def get_verified_proof(
    user_identifier: str = Path(..., description="User ID or persona slug (e.g. jordan-chen-2 or 2)"),
    db: Session = Depends(get_db),
):
    """Deliver verified telemetry proof-of-work report with SHA-256 integrity hash."""
    profile = get_proof_profile(db=db, identifier=user_identifier)
    if profile is None:
        raise HTTPException(status_code=404, detail="Proof-of-work profile not found")
    return profile
