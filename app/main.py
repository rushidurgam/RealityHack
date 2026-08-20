"""SkillBridge AI — FastAPI Backend Application.

Entrypoint with enterprise security, OWASP headers, rate limiting,
custom Swagger UI styling, and full database persistence.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.docs import custom_swagger_ui_html
from app.core.logging import RequestLoggingMiddleware, setup_logging
from app.core.security import RateLimitMiddleware, SecurityHeadersMiddleware
from app.database import check_database_health, init_db
from app.routers import (
    analytics,
    analyze,
    auth,
    chat,
    check_code,
    demo,
    jobs,
    lesson,
    proof,
    session,
    upload,
    users,
)
from app.schemas import HealthDiagnosticsResponse

# Setup beautiful structured logging
logger = setup_logging()
SERVER_START_TIME = time.time()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Bootstrap database tables, seed demo data, and initialize service pool."""
    logger.info("Initializing SkillBridge AI backend (v%s)...", settings.app_version)
    init_db()
    logger.info("Database schema initialized and verified.")
    yield
    logger.info("SkillBridge AI backend shutting down.")


app = FastAPI(
    title="SkillBridge AI API",
    description=(
        "Enterprise AI backend connecting candidate resumes to live market job demand. "
        "Extracts technical skills, identifies concrete gaps, generates focused micro-sprints, "
        "and evaluates coding answers using multi-dimensional rubric scoring with complete database persistence."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=None,  # We serve custom-themed Swagger UI below
    redoc_url="/redoc",
)

# 1. Security Headers Middleware (OWASP)
if settings.enable_security_headers:
    app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate Limiting Middleware (Token bucket)
if settings.enable_rate_limiting:
    app.add_middleware(RateLimitMiddleware, enabled=True)

# 3. Structured Request Logging
if settings.enable_request_logging:
    app.add_middleware(RequestLoggingMiddleware)

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global Exception Handlers (Standardized & Safe Error Envelope)
# ============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """Handle explicit HTTP exceptions cleanly without leaking internals."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Format Pydantic schema validation errors into human-readable details."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "Invalid request body")
    detail = f"Validation error at '{field}': {msg}"

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": 422,
            "detail": detail,
            "errors": [
                {
                    "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
                    "message": err.get("msg"),
                    "type": err.get("type"),
                }
                for err in errors
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    """Catch-all to log unexpected exceptions and prevent stack trace leaks to clients."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": 500,
            "detail": "An internal server error occurred. Our engineers have been notified.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ============================================================================
# Custom Themed Documentation
# ============================================================================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_docs():
    """Deliver customized dark-themed Swagger UI."""
    return custom_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SkillBridge AI — Interactive API Documentation",
    )


# ============================================================================
# Core Routers Registration
# ============================================================================
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(lesson.router)
app.include_router(check_code.router)
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(proof.router)
app.include_router(analytics.router)
app.include_router(demo.router)


# ============================================================================
# Health & Diagnostics Endpoints
# ============================================================================
@app.get("/health", response_model=HealthDiagnosticsResponse, tags=["system"])
def health():
    """Liveness & full system diagnostics check."""
    uptime = round(time.time() - SERVER_START_TIME, 2)
    db_health = check_database_health()
    has_gemini = bool(settings.gemini_api_key)
    has_adzuna = bool(settings.adzuna_app_id and settings.adzuna_app_key)

    return HealthDiagnosticsResponse(
        status="ok" if db_health.get("status") == "healthy" else "degraded",
        version=settings.app_version,
        environment=settings.environment,
        uptime_seconds=uptime,
        database=db_health,
        ai_engine={
            "configured": has_gemini,
            "primary_model": settings.gemini_model,
            "fallback_models": settings.fallback_model_list,
            "heuristic_engine": "active",
        },
        jobs_service={
            "configured": has_adzuna,
            "provider": "Adzuna + Role-aware cache",
            "country": settings.adzuna_country,
        },
    )
