"""Pydantic request/response schemas for the SkillBridge AI API."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings
from app.core.security import InputSanitizer


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ============================================================================
# Job Intelligence Schemas
# ============================================================================
class JobPosting(BaseSchema):
    id: int | None = None
    title: str = Field(min_length=1, max_length=200, examples=["Senior Backend Engineer"])
    company: str = Field(min_length=1, max_length=200, examples=["Northstar Labs"])
    description: str = Field(max_length=settings.max_text_chars, examples=["FastAPI, Docker, SQL, and Git."])
    role: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=200)
    source: str = Field(default="adzuna", max_length=50)
    created_at: str | None = None

    @field_validator("title", "company", "description", mode="before")
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))


class JobsFetchResponse(BaseSchema):
    jobs: list[JobPosting]
    saved_count: int
    batch_id: str | None = None
    user_id: int | None = None


# ============================================================================
# Auth & User Profile Schemas
# ============================================================================
class LoginRequest(BaseSchema):
    email: str | None = Field(default=None, max_length=255, examples=["jordan@example.com"])
    user_id: int | None = Field(default=None, examples=[1])
    name: str | None = Field(default=None, max_length=200, examples=["Jordan Chen"])

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        return InputSanitizer.sanitize_text(v) if v else None


class RegisterRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=200, examples=["Jordan Chen"])
    email: str | None = Field(default=None, max_length=255, examples=["jordan.chen@example.com"])
    target_role: str = Field(default="", max_length=200, examples=["Junior Backend Engineer"])

    @field_validator("name", "target_role", mode="before")
    @classmethod
    def sanitize_inputs(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))


class UserListItem(BaseSchema):
    id: int
    name: str
    email: str | None = None
    target_role: str = ""
    initials: str = "SB"
    is_sample: bool = False
    resume_id: int | None = None
    file_name: str = ""
    candidate_score: float = 0.0
    resume_score: float = 0.0
    skills_count: int = 0
    created_at: str | None = None


UserSummaryItem = UserListItem


class CandidateAIAnalysis(BaseSchema):
    summary: str = ""
    current_position: str = ""
    skills: list[str] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommended_skills: list[str] = Field(default_factory=list)
    recommended_roles: list[str] = Field(default_factory=list)
    resume_score: int = 0
    candidate_score: int = 0
    interview_questions: list[str] = Field(default_factory=list)
    key_observations: list[str] = Field(default_factory=list)


class CandidateResumeResponse(BaseSchema):
    user_id: int
    resume_id: int | None = None
    file_name: str = ""
    file_type: str = "pdf"
    raw_text: str = ""
    parsed_skills: list[str] = Field(default_factory=list)
    resume_score: float = 0.0
    candidate_score: float = 0.0
    created_at: str | None = None


class CandidateAnalysisResponse(BaseSchema):
    user_id: int
    resume_id: int | None = None
    analysis: CandidateAIAnalysis | dict = Field(default_factory=dict)
    candidate_score: float = 0.0
    resume_score: float = 0.0


class UserCreateRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=200, examples=["Rahul Sharma"])
    target_role: str = Field(default="", max_length=200, examples=["Backend Developer"])
    email: str | None = Field(default=None, max_length=255, examples=["rahul@example.com"])

    @field_validator("name", "target_role", mode="before")
    @classmethod
    def sanitize_inputs(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))


class UserUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, max_length=200)
    target_role: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=255)

    @field_validator("name", "target_role", mode="before")
    @classmethod
    def sanitize_inputs(cls, v: str | None) -> str | None:
        return InputSanitizer.sanitize_text(v) if v else None


class UserProfileDetail(BaseSchema):
    id: int
    name: str
    email: str | None = None
    target_role: str = ""
    initials: str = "SB"
    is_sample: bool = False
    resume_id: int | None = None
    file_name: str = ""
    file_type: str = "pdf"
    raw_text: str = ""
    parsed_skills: list[str] = Field(default_factory=list)
    ai_analysis: CandidateAIAnalysis | dict = Field(default_factory=dict)
    resume_score: float = 0.0
    candidate_score: float = 0.0
    experience_years: float = 0.0
    gaps: list[MissingSkill] = Field(default_factory=list)
    learning_path: list[LearningPathItem] = Field(default_factory=list)
    badges: list[dict] = Field(default_factory=list)
    created_at: str | None = None



# ============================================================================
# Skill Delta & Gap Analysis Schemas
# ============================================================================
class AnalyzeRequest(BaseSchema):
    resume_text: str = Field(min_length=1, max_length=settings.max_text_chars)
    job_descriptions: list[str] = Field(
        default_factory=list,
        max_length=settings.max_job_descriptions,
    )
    user_id: int | None = None
    resume_id: int | None = None
    name: str = "Demo User"
    target_role: str = ""

    @field_validator("resume_text", "name", "target_role", mode="before")
    @classmethod
    def sanitize_texts(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))

    @field_validator("job_descriptions")
    @classmethod
    def limit_job_description_size(cls, value: list[str]) -> list[str]:
        return [InputSanitizer.sanitize_text(item)[: settings.max_text_chars] for item in value]


class MissingSkill(BaseSchema):
    id: int | None = None
    skill: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=500)
    priority_rank: int = 1
    demand_count: int = 1
    status: str = "open"
    created_at: str | None = None


class LearningPathItem(BaseSchema):
    order: int
    skill: str
    minutes: int
    why: str = ""


class AnalyzeResponse(BaseSchema):
    user_id: int
    resume_id: int
    parsed_skills: list[str]
    coverage_percent: int
    gaps: list[MissingSkill]
    learning_path: list[LearningPathItem]


# ============================================================================
# Lesson & Sprints Schemas
# ============================================================================
class LessonRequest(BaseSchema):
    skill: str = Field(min_length=1, max_length=100)
    skill_gap_id: int | None = None

    @field_validator("skill", mode="before")
    @classmethod
    def sanitize_skill(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))


class LessonResponse(BaseSchema):
    id: int | None = None
    skill_gap_id: int | None = None
    skill_name: str = ""
    theory_markdown: str = Field(max_length=settings.max_text_chars)
    starter_code: str = Field(max_length=settings.max_code_chars)
    solution_code: str = Field(max_length=settings.max_code_chars)


# ============================================================================
# Code Evaluation & Rubric Schemas
# ============================================================================
class RubricScores(BaseSchema):
    correctness: int = 0
    code_quality: int = 0
    concept_match: int = 0


class CheckCodeRequest(BaseSchema):
    submitted_code: str = Field(min_length=1, max_length=settings.max_code_chars)
    solution_code: str = Field(min_length=1, max_length=settings.max_code_chars)
    lesson_id: int | None = None
    concept: str = ""

    @field_validator("submitted_code", "solution_code", "concept", mode="before")
    @classmethod
    def sanitize_code_inputs(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""), strip_html=False)


class CheckCodeResponse(BaseSchema):
    id: int | None = None
    passed: bool
    hint: str = Field(max_length=500)
    score: float = 0
    rubric: RubricScores = Field(default_factory=RubricScores)
    evaluation: dict | None = None


# ============================================================================
# Upload & Resume Persistence
# ============================================================================
class UploadResponse(BaseSchema):
    user_id: int
    resume_id: int | None = None
    name: str = Field(max_length=200)
    target_role: str = Field(max_length=200)
    extracted_text: str = Field(max_length=settings.max_text_chars)
    parsed_skills: list[str] = Field(default_factory=list)


class ResumeSaveRequest(BaseSchema):
    raw_text: str = Field(min_length=1, max_length=settings.max_text_chars)
    user_id: int | None = None
    name: str = "Demo User"
    target_role: str = ""

    @field_validator("raw_text", "name", "target_role", mode="before")
    @classmethod
    def sanitize_resume_inputs(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))


# ============================================================================
# Grounded Q&A Chat Schemas
# ============================================================================
class ChatRequest(BaseSchema):
    skill_gap_id: int
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message", mode="before")
    @classmethod
    def sanitize_chat_message(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(str(v or ""))


class ChatResponse(BaseSchema):
    id: int | None = None
    role: str
    content: str
    created_at: str | None = None


# ============================================================================
# Session & History Schemas
# ============================================================================
class AttemptHistoryItem(BaseSchema):
    id: int
    lesson_id: int
    passed: bool
    score: float
    hint: str
    rubric: RubricScores
    created_at: str | None = None


class ResumeHistoryItem(BaseSchema):
    resume_id: int
    created_at: str | None
    raw_text: str = ""
    parsed_skills: list[str] = Field(default_factory=list)
    coverage_percent: int = 0
    gaps: list[MissingSkill] = Field(default_factory=list)
    learning_path: list[LearningPathItem] = Field(default_factory=list)


class HistoryResponse(BaseSchema):
    user_id: int | None
    resumes: list[ResumeHistoryItem]
    gap_trends: dict[str, list[dict]]
    average_practice_score: float = 0
    total_attempts: int = 0


class SessionResponse(BaseSchema):
    user_id: int | None
    name: str = "Demo User"
    email: str | None = None
    target_role: str = ""
    resume_id: int | None = None
    resume_text: str = ""
    parsed_skills: list[str] = Field(default_factory=list)
    coverage_percent: int = 0
    jobs: list[JobPosting] = Field(default_factory=list)
    gaps: list[MissingSkill] = Field(default_factory=list)
    learning_path: list[LearningPathItem] = Field(default_factory=list)
    selected_gap: MissingSkill | None = None
    lesson: LessonResponse | None = None
    chat: list[ChatResponse] = Field(default_factory=list)
    last_attempt: CheckCodeResponse | None = None


# ============================================================================
# Proof-of-Work & Platform Analytics Schemas
# ============================================================================
class VerifiedBadge(BaseSchema):
    key: str
    name: str
    earned_at: str | None = None
    attempts: int = 1
    score: float = 95.0


class ProofProfileResponse(BaseSchema):
    user_id: int
    name: str
    initials: str
    target_role: str
    verified_hash: str
    verified_url: str
    completion_rate: int
    average_score: float
    total_attempts: int
    badges_count: int
    badges: list[VerifiedBadge]
    skills_radar: list[dict[str, Any]]
    created_at: str | None = None


class PlatformStatsResponse(BaseSchema):
    total_learners: int
    total_scanned_jobs: int
    total_attempts: int
    average_score: float
    top_demanded_skills: list[dict[str, Any]]
    system_status: str = "operational"


class HealthDiagnosticsResponse(BaseSchema):
    status: str
    version: str
    environment: str
    uptime_seconds: float
    database: dict[str, Any]
    ai_engine: dict[str, Any]
    jobs_service: dict[str, Any]
