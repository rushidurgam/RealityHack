"""SQLAlchemy engine and session management. Supports Postgres/Supabase and SQLite fallback."""

import logging
import time
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

logger = logging.getLogger("skillbridge.database")

# Normalize DATABASE_URL (Supabase and Heroku often provide postgres:// instead of postgresql://)
db_url = settings.database_url or "sqlite:///./skillbridge.db"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # Postgres / Supabase pool configuration
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 300

try:
    engine = create_engine(db_url, **engine_kwargs)
except Exception as e:
    logger.warning(f"Could not connect to configured DATABASE_URL ({e}). Falling back to local SQLite.")
    db_url = "sqlite:///./skillbridge.db"
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
    if not db_url.startswith("sqlite"):
        return
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
    except Exception:
        pass


class Base(DeclarativeBase):
    """Base class all ORM models inherit from."""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_health() -> dict:
    """Test database connectivity, measure latency, and count active tables."""
    start = time.monotonic()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "dialect": engine.dialect.name,
            "tables_count": len(tables),
            "tables": tables,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
            "latency_ms": round((time.monotonic() - start) * 1000, 2),
            "dialect": engine.dialect.name,
        }


def _table_columns(table: str) -> set[str]:
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return set()
    return {col["name"] for col in inspector.get_columns(table)}


def _add_column(table: str, ddl: str) -> None:
    with engine.begin() as connection:
        try:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
        except SQLAlchemyError:
            pass


def _migrate_legacy_columns() -> None:
    """Safely ensure all expected columns and indexes exist in the schema."""
    try:
        user_cols = _table_columns("users")
        if user_cols:
            if "email" not in user_cols:
                _add_column("users", "email VARCHAR(255)")
            if "current_role" not in user_cols:
                _add_column("users", "current_role VARCHAR(200) DEFAULT 'Customer Support Team Lead'")
            if "location" not in user_cols:
                _add_column("users", "location VARCHAR(200) DEFAULT 'Austin, TX (or Remote)'")
            if "avatar" not in user_cols:
                _add_column("users", "avatar VARCHAR(500) DEFAULT ''")
            if "current_salary" not in user_cols:
                _add_column("users", "current_salary VARCHAR(50) DEFAULT '$52,000'")
            if "target_salary" not in user_cols:
                _add_column("users", "target_salary VARCHAR(50) DEFAULT '$89,000'")
            if "experience_years" not in user_cols:
                _add_column("users", "experience_years FLOAT DEFAULT 4.0")
            if "automation_risk_score" not in user_cols:
                _add_column("users", "automation_risk_score INTEGER DEFAULT 78")
            if "shielded_risk_score" not in user_cols:
                _add_column("users", "shielded_risk_score INTEGER DEFAULT 14")
            if "automation_risk_explanation" not in user_cols:
                _add_column("users", "automation_risk_explanation TEXT DEFAULT ''")
            if "position" not in user_cols:
                _add_column("users", "position VARCHAR(200) DEFAULT 'AI Operations & Support Systems Specialist'")
            if "country" not in user_cols:
                _add_column("users", "country VARCHAR(100) DEFAULT 'United States'")
            if "country_code" not in user_cols:
                _add_column("users", "country_code VARCHAR(10) DEFAULT 'US'")
            if "currency" not in user_cols:
                _add_column("users", "currency VARCHAR(50) DEFAULT 'US Dollar'")
            if "currency_code" not in user_cols:
                _add_column("users", "currency_code VARCHAR(10) DEFAULT 'USD'")
            if "currency_symbol" not in user_cols:
                _add_column("users", "currency_symbol VARCHAR(10) DEFAULT '$'")
            if "tasks_at_risk" not in user_cols:
                _add_column("users", "tasks_at_risk JSON DEFAULT '[]'")
            if "skills_radar" not in user_cols:
                _add_column("users", "skills_radar JSON DEFAULT '[]'")
            if "salary_growth" not in user_cols:
                _add_column("users", "salary_growth JSON DEFAULT '[]'")
            if "translated_skills" not in user_cols:
                _add_column("users", "translated_skills JSON DEFAULT '[]'")
            if "is_sample" not in user_cols:
                _add_column("users", "is_sample BOOLEAN DEFAULT 0")
            if "created_at" not in user_cols:
                _add_column("users", "created_at TIMESTAMP")

        gap_cols = _table_columns("skill_gaps")
        if gap_cols:
            if "resume_id" not in gap_cols:
                _add_column("skill_gaps", "resume_id INTEGER")
            if "demand_count" not in gap_cols:
                _add_column("skill_gaps", "demand_count INTEGER DEFAULT 1")
            if "reason" not in gap_cols:
                _add_column("skill_gaps", "reason TEXT DEFAULT ''")
            if "priority_rank" not in gap_cols:
                _add_column("skill_gaps", "priority_rank INTEGER DEFAULT 1")
            if "created_at" not in gap_cols:
                _add_column("skill_gaps", "created_at TIMESTAMP")

        job_cols = _table_columns("job_postings")
        if job_cols:
            if "role" not in job_cols:
                _add_column("job_postings", "role VARCHAR(200) DEFAULT ''")

        resume_cols = _table_columns("resumes")
        if resume_cols:
            if "file_name" not in resume_cols:
                _add_column("resumes", "file_name VARCHAR(255) DEFAULT ''")
            if "file_type" not in resume_cols:
                _add_column("resumes", "file_type VARCHAR(50) DEFAULT 'pdf'")
            if "ai_analysis" not in resume_cols:
                _add_column("resumes", "ai_analysis JSON DEFAULT '{}'")
            if "resume_score" not in resume_cols:
                _add_column("resumes", "resume_score FLOAT DEFAULT 0")
            if "candidate_score" not in resume_cols:
                _add_column("resumes", "candidate_score FLOAT DEFAULT 0")
            if "experience_years" not in resume_cols:
                _add_column("resumes", "experience_years FLOAT DEFAULT 0")

        lesson_cols = _table_columns("lessons")
        if lesson_cols:
            if "skill_name" not in lesson_cols:
                _add_column("lessons", "skill_name VARCHAR(200) DEFAULT ''")

        attempt_cols = _table_columns("practice_attempts")
        if attempt_cols:
            if "score" not in attempt_cols:
                _add_column("practice_attempts", "score FLOAT DEFAULT 0")
            if "evaluation_json" not in attempt_cols:
                _add_column("practice_attempts", "evaluation_json JSON DEFAULT '{}'")
    except Exception as exc:
        logger.warning(f"Column migration check note: {exc}")


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_legacy_columns()
    from app.seed import seed_if_empty

    seed_if_empty()
