"""Adzuna job search with role-aware local JSON fallback so market queries never fail."""

import json
import logging
from pathlib import Path

import httpx

from app.config import settings
from app.core.security import InputSanitizer
from app.schemas import JobPosting

logger = logging.getLogger("skillbridge.adzuna")

SAMPLE_JOBS_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_jobs.json"

# Role keyword groups for intelligent local filtering
ROLE_KEYWORDS: dict[str, list[str]] = {
    "iot":      ["iot", "embedded", "firmware", "sensor", "mqtt", "freertos", "esp32", "arm"],
    "devops":   ["devops", "sre", "site reliability", "platform", "kubernetes", "terraform", "ci/cd"],
    "frontend": ["frontend", "front end", "react", "ui", "ux", "angular", "vue", "typescript"],
    "ml":       ["ml", "machine learning", "data scientist", "pytorch", "tensorflow", "llm", "ai", "pandas"],
    "backend":  ["backend", "back end", "python", "fastapi", "django", "flask", "api engineer", "sql"],
    "cloud":    ["cloud", "aws", "azure", "gcp", "infrastructure"],
    "fullstack":["full stack", "fullstack"],
}


def _role_category(role: str) -> str:
    role_lower = (role or "").lower()
    for category, keywords in ROLE_KEYWORDS.items():
        if any(kw in role_lower for kw in keywords):
            return category
    return "backend"


def load_sample_jobs(role: str = "") -> list[JobPosting]:
    """Read data/sample_jobs.json and filter to the most relevant jobs for this role."""
    if not SAMPLE_JOBS_PATH.exists():
        return [
            JobPosting(
                title=f"{role or 'Software'} Engineer",
                company="Northstar Labs",
                description="FastAPI, Docker, SQL, and Git in a microservices environment.",
                source="sample",
            )
        ]

    try:
        with SAMPLE_JOBS_PATH.open(encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        raw = []

    category = _role_category(role)

    def score_job(item: dict) -> int:
        title = str(item.get("title", "")).lower()
        desc = str(item.get("description", "")).lower()
        kws = ROLE_KEYWORDS.get(category, [])
        return sum(2 for kw in kws if kw in title) + sum(1 for kw in kws if kw in desc)

    scored = sorted(raw, key=score_job, reverse=True)
    top = [JobPosting.model_validate({**item, "source": "sample"}) for item in scored[:6]]
    return top or [JobPosting.model_validate({**item, "source": "sample"}) for item in raw[:6]]


def search_jobs_for_role(role: str, location: str = "United States") -> list[JobPosting]:
    """Call Adzuna API for live jobs; on any failure return role-filtered sample jobs."""
    clean_role = InputSanitizer.sanitize_text(role, max_chars=100) or "Software Engineer"
    clean_location = InputSanitizer.sanitize_text(location, max_chars=100) or "United States"

    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        return load_sample_jobs(clean_role)

    country = (settings.adzuna_country or "us").strip().lower()
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "what": clean_role,
        "where": clean_location,
        "results_per_page": 8,
        "content-type": "application/json",
    }

    try:
        with httpx.Client(timeout=settings.external_request_timeout_seconds) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.debug("Adzuna query note: %s. Using role-filtered sample jobs.", exc)
        return load_sample_jobs(clean_role)

    results = payload.get("results") or []
    jobs: list[JobPosting] = []
    for item in results:
        company_name = (item.get("company") or {}).get("display_name") or "Leading Tech Company"
        jobs.append(
            JobPosting(
                title=(item.get("title") or f"{clean_role} Specialist")[:200],
                company=company_name[:200],
                description=(item.get("description") or "")[: settings.max_text_chars],
                location=clean_location,
                role=clean_role,
                source="adzuna",
            )
        )

    return jobs or load_sample_jobs(clean_role)


def search_jobs(role: str, location: str = "United States") -> list[JobPosting]:
    """Backward compatibility alias."""
    return search_jobs_for_role(role=role, location=location)
