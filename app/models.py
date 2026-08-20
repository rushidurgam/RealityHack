"""Persisted product schema: users, resumes, jobs, gaps, lessons, attempts, chat, learning paths."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """A learner. All profile metrics, salary simulations, and skill radars are persisted."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), default="Demo User", index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    current_role: Mapped[str] = mapped_column(String(200), default="Customer Support Team Lead")
    target_role: Mapped[str] = mapped_column(String(200), default="AI Operations & Support Systems Specialist")
    position: Mapped[str | None] = mapped_column(String(200), nullable=True, default="AI Operations & Support Systems Specialist")
    location: Mapped[str] = mapped_column(String(200), default="Austin, TX (or Remote)")
    country: Mapped[str | None] = mapped_column(String(100), default="United States")
    country_code: Mapped[str | None] = mapped_column(String(10), default="US")
    currency: Mapped[str | None] = mapped_column(String(50), default="US Dollar")
    currency_code: Mapped[str | None] = mapped_column(String(10), default="USD")
    currency_symbol: Mapped[str | None] = mapped_column(String(10), default="$")
    avatar: Mapped[str] = mapped_column(String(500), default="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80")
    current_salary: Mapped[str] = mapped_column(String(50), default="$52,000")
    target_salary: Mapped[str] = mapped_column(String(50), default="$89,000")
    experience_years: Mapped[float] = mapped_column(Float, default=4.0)
    automation_risk_score: Mapped[int] = mapped_column(Integer, default=78)
    shielded_risk_score: Mapped[int] = mapped_column(Integer, default=14)
    automation_risk_explanation: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    tasks_at_risk: Mapped[list] = mapped_column(JSON, default=list)
    skills_radar: Mapped[list] = mapped_column(JSON, default=list)
    salary_growth: Mapped[list] = mapped_column(JSON, default=list)
    translated_skills: Mapped[list] = mapped_column(JSON, default=list)
    resume_text: Mapped[str] = mapped_column(Text, default="")
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    resumes: Mapped[list["Resume"]] = relationship(back_populates="user", cascade="all, delete-orphan", order_by="desc(Resume.created_at)")
    job_postings: Mapped[list["JobPosting"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    skill_gaps: Mapped[list["SkillGap"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    """One uploaded/pasted resume or syllabus, with parsed skills JSON."""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    file_name: Mapped[str] = mapped_column(String(255), default="")
    file_type: Mapped[str] = mapped_column(String(50), default="pdf")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    parsed_skills: Mapped[list] = mapped_column(JSON, default=list)
    ai_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    resume_score: Mapped[float] = mapped_column(Float, default=0.0)
    candidate_score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_years: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped["User"] = relationship(back_populates="resumes")
    skill_gaps: Mapped[list["SkillGap"]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    job_postings: Mapped[list["JobPosting"]] = relationship(back_populates="resume")
    learning_path: Mapped["LearningPath | None"] = relationship(
        back_populates="resume", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_resumes_user_created", "user_id", "created_at"),
    )


class JobPosting(Base):
    """Cached job ads so a demo does not re-hit Adzuna on every click."""

    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id", ondelete="SET NULL"), index=True, nullable=True)
    batch_id: Mapped[str] = mapped_column(String(64), index=True, default="")
    role: Mapped[str] = mapped_column(String(200), default="")
    role_query: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(50), default="adzuna")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped["User | None"] = relationship(back_populates="job_postings")
    resume: Mapped["Resume | None"] = relationship(back_populates="job_postings")

    __table_args__ = (
        Index("ix_jobs_batch_id", "batch_id"),
        Index("ix_jobs_user_role", "user_id", "role_query"),
    )


class SkillGap(Base):
    """A ranked missing skill tied to a specific resume analysis."""

    __tablename__ = "skill_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=True)
    skill_name: Mapped[str] = mapped_column(String(200), index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    priority_rank: Mapped[int] = mapped_column(Integer, default=1)
    demand_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="open")  # 'open', 'practiced', 'mastered'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped["User | None"] = relationship(back_populates="skill_gaps")
    resume: Mapped["Resume | None"] = relationship(back_populates="skill_gaps")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="skill_gap", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="skill_gap", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_gaps_resume_priority", "resume_id", "priority_rank"),
    )


class Lesson(Base):
    """Cached micro-lesson for one skill gap (avoid regenerating during a demo)."""

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_gap_id: Mapped[int] = mapped_column(ForeignKey("skill_gaps.id", ondelete="CASCADE"), index=True)
    skill_name: Mapped[str] = mapped_column(String(200), default="", index=True)
    theory_markdown: Mapped[str] = mapped_column(Text, default="")
    starter_code: Mapped[str] = mapped_column(Text, default="")
    solution_code: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    skill_gap: Mapped["SkillGap"] = relationship(back_populates="lessons")
    attempts: Mapped[list["PracticeAttempt"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan", order_by="desc(PracticeAttempt.created_at)"
    )


class PracticeAttempt(Base):
    """One submitted answer plus AI rubric scores (never executed on the server)."""

    __tablename__ = "practice_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    submitted_code: Mapped[str] = mapped_column(Text, default="")
    hint: Mapped[str] = mapped_column(Text, default="")
    passed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    score: Mapped[float] = mapped_column(Float, default=0)
    correctness: Mapped[int] = mapped_column(Integer, default=0)
    code_quality: Mapped[int] = mapped_column(Integer, default=0)
    concept_match: Mapped[int] = mapped_column(Integer, default=0)
    evaluation: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    @property
    def evaluation_json(self) -> dict:
        return self.evaluation

    @evaluation_json.setter
    def evaluation_json(self, value: dict) -> None:
        self.evaluation = value

    lesson: Mapped["Lesson"] = relationship(back_populates="attempts")

    __table_args__ = (
        Index("ix_attempts_lesson_created", "lesson_id", "created_at"),
    )


class ChatMessage(Base):
    """Follow-up Q&A grounded in the gap, lesson, and job postings."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_gap_id: Mapped[int] = mapped_column(ForeignKey("skill_gaps.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    skill_gap: Mapped["SkillGap"] = relationship(back_populates="chat_messages")


class LearningPath(Base):
    """Ordered study plan for a resume's ranked gaps, with time estimates."""

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, index=True)
    items: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    resume: Mapped["Resume"] = relationship(back_populates="learning_path")
