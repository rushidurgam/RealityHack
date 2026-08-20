"""GET /api/stats and GET /api/roles — real-time platform metrics and role taxonomies."""

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import get_platform_stats
from app.database import get_db
from app.schemas import PlatformStatsResponse

router = APIRouter(prefix="/api", tags=["analytics"])

ROLE_TAXONOMIES = [
    {
        "key": "backend",
        "label": "Junior Backend Engineer",
        "location": "New York, NY",
        "sample_postings": 1248,
        "demand_weights": {"docker": 88, "cicd": 78, "fastapi": 74, "cloud": 66, "git": 58, "sql": 60, "algo": 45, "ds": 42},
    },
    {
        "key": "iot",
        "label": "IoT & Embedded Systems Engineer",
        "location": "Austin, TX (Hybrid)",
        "sample_postings": 842,
        "demand_weights": {"mqtt": 92, "freertos": 85, "embedded_c": 90, "edge": 76, "git": 60, "cicd": 50, "algo": 55, "ds": 48},
    },
    {
        "key": "frontend",
        "label": "Frontend Engineer",
        "location": "San Francisco, CA",
        "sample_postings": 932,
        "demand_weights": {"docker": 35, "cicd": 55, "fastapi": 20, "cloud": 40, "git": 70, "sql": 30, "algo": 50, "ds": 55},
    },
    {
        "key": "devops",
        "label": "DevOps Engineer",
        "location": "Remote (US)",
        "sample_postings": 617,
        "demand_weights": {"docker": 95, "cicd": 92, "fastapi": 30, "cloud": 90, "git": 65, "sql": 45, "algo": 35, "ds": 30},
    },
]


@router.get("/stats", response_model=PlatformStatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Retrieve live aggregate platform metrics and skill telemetry."""
    return get_platform_stats(db)


@router.get("/roles")
def get_supported_roles() -> list[dict[str, Any]]:
    """Retrieve supported engineering roles with baseline market weights and sample sizes."""
    return ROLE_TAXONOMIES
