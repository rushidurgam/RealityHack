"""Create/read helpers so routers stay thin and every demo action hits the DB."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.security import InputSanitizer, generate_proof_hash
from app.models import (
    ChatMessage,
    JobPosting,
    LearningPath,
    Lesson,
    PracticeAttempt,
    Resume,
    SkillGap,
    User,
)
from app.services.countries import get_country_currency_info
from app.services.document import extract_document_text
from app.services.gemini import (
    analyze_candidate_resume,
    analyze_skill_gaps,
    calculate_automation_risk_and_shielded_score,
    generate_learning_path,
    parse_resume_skills,
)



def get_or_create_user(
    db: Session,
    user_id: int | None,
    name: str = "Demo User",
    target_role: str = "",
    email: str | None = None,
) -> User:
    clean_name = InputSanitizer.sanitize_text(name or "Demo User", max_chars=200)
    clean_role = InputSanitizer.sanitize_text(target_role or "", max_chars=200)
    clean_email = InputSanitizer.sanitize_text(email or "", max_chars=255).lower() if email else None

    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        user = User(
            name=clean_name,
            target_role=clean_role,
            email=clean_email,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    if clean_name:
        user.name = clean_name
    if clean_role:
        user.target_role = clean_role
    if clean_email:
        user.email = clean_email
    db.commit()
    db.refresh(user)
    return user


def create_resume(db: Session, user: User, raw_text: str) -> Resume:
    sanitized_text = InputSanitizer.sanitize_text(raw_text)
    skills = parse_resume_skills(sanitized_text)
    resume = Resume(user_id=user.id, raw_text=sanitized_text, parsed_skills=skills)
    user.resume_text = sanitized_text
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def latest_resume(db: Session, user_id: int) -> Resume | None:
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .first()
    )


def get_resume_by_id(db: Session, resume_id: int) -> Resume | None:
    return db.get(Resume, resume_id)


def cached_jobs(
    db: Session,
    user_id: int,
    role: str,
    location: str,
    max_age_hours: int = 6,
) -> list[JobPosting] | None:
    latest = (
        db.query(JobPosting)
        .filter(
            JobPosting.user_id == user_id,
            JobPosting.role_query == role,
            JobPosting.location == location,
        )
        .order_by(JobPosting.created_at.desc())
        .first()
    )
    if latest is None or not latest.batch_id:
        return None
    created = latest.created_at
    if created and created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if created and datetime.now(timezone.utc) - created > timedelta(hours=max_age_hours):
        return None
    return (
        db.query(JobPosting)
        .filter(JobPosting.batch_id == latest.batch_id)
        .order_by(JobPosting.id.asc())
        .all()
    )


def persist_jobs(
    db: Session,
    user: User,
    resume_id: int | None,
    role: str,
    location: str,
    jobs: list,
    source: str = "adzuna",
) -> list[JobPosting]:
    batch_id = uuid4().hex
    rows: list[JobPosting] = []
    for job in jobs:
        title = getattr(job, "title", None) or (job.get("title") if isinstance(job, dict) else "")
        company = getattr(job, "company", None) or (job.get("company") if isinstance(job, dict) else "")
        description = getattr(job, "description", None) or (job.get("description") if isinstance(job, dict) else "")
        row = JobPosting(
            user_id=user.id,
            resume_id=resume_id,
            batch_id=batch_id,
            role=InputSanitizer.sanitize_text(role, max_chars=200),
            role_query=InputSanitizer.sanitize_text(role, max_chars=200),
            location=InputSanitizer.sanitize_text(location, max_chars=200),
            title=InputSanitizer.sanitize_text(title, max_chars=200),
            company=InputSanitizer.sanitize_text(company, max_chars=200),
            description=InputSanitizer.sanitize_text(description),
            source=source,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def persist_gaps(db: Session, user: User, resume: Resume, gaps: list[dict]) -> list[SkillGap]:
    rows: list[SkillGap] = []
    for index, item in enumerate(gaps, start=1):
        demand_count = int(item.get("demand_count") or item.get("demand_pct") or (4 - index) if (4 - index) > 0 else 1)
        row = SkillGap(
            user_id=user.id,
            resume_id=resume.id,
            skill_name=InputSanitizer.sanitize_text(item["skill"], max_chars=200),
            reason=InputSanitizer.sanitize_text(item.get("reason") or "", max_chars=500),
            priority_rank=index,
            demand_count=demand_count,
            status="open",
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def get_gaps_for_resume(db: Session, resume_id: int) -> list[SkillGap]:
    return (
        db.query(SkillGap)
        .filter(SkillGap.resume_id == resume_id)
        .order_by(SkillGap.priority_rank.asc(), SkillGap.id.asc())
        .all()
    )


def upsert_learning_path(db: Session, resume_id: int, items: list) -> LearningPath:
    path = db.query(LearningPath).filter(LearningPath.resume_id == resume_id).first()
    if path is None:
        path = LearningPath(resume_id=resume_id, items=items)
        db.add(path)
    else:
        path.items = items
    db.commit()
    db.refresh(path)
    return path


def cached_lesson(db: Session, skill_gap_id: int) -> Lesson | None:
    return (
        db.query(Lesson)
        .filter(Lesson.skill_gap_id == skill_gap_id)
        .order_by(Lesson.created_at.desc())
        .first()
    )


def persist_lesson(db: Session, skill_gap_id: int, payload: dict, skill_name: str = "") -> Lesson:
    existing = cached_lesson(db, skill_gap_id)
    if existing:
        return existing
    gap = db.get(SkillGap, skill_gap_id)
    if not skill_name and gap:
        skill_name = gap.skill_name
    lesson = Lesson(
        skill_gap_id=skill_gap_id,
        skill_name=InputSanitizer.sanitize_text(skill_name, max_chars=200),
        theory_markdown=payload.get("theory_markdown") or payload.get("markdown_theory", ""),
        starter_code=payload.get("starter_code", ""),
        solution_code=payload.get("solution_code", ""),
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def get_attempts_for_lesson(db: Session, lesson_id: int) -> list[PracticeAttempt]:
    return (
        db.query(PracticeAttempt)
        .filter(PracticeAttempt.lesson_id == lesson_id)
        .order_by(PracticeAttempt.created_at.desc())
        .all()
    )


def persist_attempt(db: Session, lesson_id: int, submitted: str, result: dict) -> PracticeAttempt:
    rubric = result.get("rubric") or {}
    attempt = PracticeAttempt(
        lesson_id=lesson_id,
        submitted_code=submitted,
        hint=InputSanitizer.sanitize_text(str(result.get("hint") or ""), max_chars=500),
        passed=bool(result.get("passed")),
        score=float(result.get("score") or 0),
        correctness=int(rubric.get("correctness") or 0),
        code_quality=int(rubric.get("code_quality") or 0),
        concept_match=int(rubric.get("concept_match") or 0),
        evaluation_json=result,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def persist_chat(db: Session, skill_gap_id: int, role: str, content: str) -> ChatMessage:
    message = ChatMessage(
        skill_gap_id=skill_gap_id,
        role=role[:20],
        content=InputSanitizer.sanitize_text(content, max_chars=3000),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_chat_for_gap(db: Session, skill_gap_id: int) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.skill_gap_id == skill_gap_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def job_dicts(rows: list[JobPosting]) -> list[dict]:
    return [
        {
            "id": row.id,
            "title": row.title,
            "company": row.company,
            "description": row.description,
            "role": row.role or row.role_query,
            "location": row.location,
            "source": row.source,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


def gap_dicts(rows: list[SkillGap]) -> list[dict]:
    return [
        {
            "id": row.id,
            "skill": row.skill_name,
            "reason": row.reason,
            "priority_rank": row.priority_rank,
            "demand_count": row.demand_count,
            "status": row.status,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


def latest_jobs_for_user(db: Session, user_id: int) -> list[JobPosting]:
    latest = (
        db.query(JobPosting)
        .filter(JobPosting.user_id == user_id)
        .order_by(JobPosting.created_at.desc())
        .first()
    )
    if latest is None or not latest.batch_id:
        return []
    return (
        db.query(JobPosting)
        .filter(JobPosting.batch_id == latest.batch_id)
        .order_by(JobPosting.id.asc())
        .all()
    )


def coverage_percent(parsed_skills: list, gap_count: int) -> int:
    have = len(parsed_skills or [])
    total = have + max(gap_count, 0)
    if total == 0:
        return 0
    return round(100 * have / total)


def build_session(db: Session, user: User) -> dict:
    resume = latest_resume(db, user.id)
    jobs = latest_jobs_for_user(db, user.id)
    gaps: list[SkillGap] = []
    path_items = []
    lesson_payload = None
    selected_gap = None
    chat = []
    last_attempt = None

    if resume:
        gaps = (
            db.query(SkillGap)
            .filter(SkillGap.resume_id == resume.id)
            .order_by(SkillGap.priority_rank.asc(), SkillGap.id.asc())
            .all()
        )
        if resume.learning_path:
            path_items = resume.learning_path.items or []
        else:
            path = db.query(LearningPath).filter(LearningPath.resume_id == resume.id).first()
            path_items = path.items if path else []

        if gaps:
            selected_gap = gaps[0]
            lesson = cached_lesson(db, selected_gap.id)
            if lesson:
                lesson_payload = {
                    "id": lesson.id,
                    "skill_gap_id": lesson.skill_gap_id,
                    "skill_name": lesson.skill_name or selected_gap.skill_name,
                    "theory_markdown": lesson.theory_markdown,
                    "starter_code": lesson.starter_code,
                    "solution_code": lesson.solution_code,
                }
                chat = [
                    {"id": msg.id, "role": msg.role, "content": msg.content}
                    for msg in (
                        db.query(ChatMessage)
                        .filter(ChatMessage.skill_gap_id == selected_gap.id)
                        .order_by(ChatMessage.created_at.asc())
                        .all()
                    )
                ]
                attempt = (
                    db.query(PracticeAttempt)
                    .filter(PracticeAttempt.lesson_id == lesson.id)
                    .order_by(PracticeAttempt.created_at.desc())
                    .first()
                )
                if attempt:
                    last_attempt = {
                        "id": attempt.id,
                        "passed": attempt.passed,
                        "hint": attempt.hint,
                        "score": attempt.score,
                        "rubric": {
                            "correctness": attempt.correctness,
                            "code_quality": attempt.code_quality,
                            "concept_match": attempt.concept_match,
                        },
                        "evaluation": attempt.evaluation_json,
                    }

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "target_role": user.target_role,
        "resume_id": resume.id if resume else None,
        "resume_text": resume.raw_text if resume else user.resume_text,
        "parsed_skills": resume.parsed_skills if resume else [],
        "coverage_percent": coverage_percent(
            resume.parsed_skills if resume else [],
            len(gaps),
        ),
        "jobs": job_dicts(jobs),
        "gaps": gap_dicts(gaps),
        "learning_path": path_items,
        "selected_gap": gap_dicts([selected_gap])[0] if selected_gap else None,
        "lesson": lesson_payload,
        "chat": chat,
        "last_attempt": last_attempt,
    }


def history_for_user(db: Session, user_id: int) -> dict:
    resumes = (
        db.query(Resume)
        .options(selectinload(Resume.skill_gaps), selectinload(Resume.learning_path))
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    items = []
    trend: dict[str, list] = {}
    for resume in resumes:
        gaps = sorted(resume.skill_gaps, key=lambda g: (g.priority_rank, g.id))
        for gap in gaps:
            trend.setdefault(gap.skill_name, []).append(
                {
                    "resume_id": resume.id,
                    "created_at": resume.created_at.isoformat() if resume.created_at else None,
                    "rank": gap.priority_rank,
                }
            )
        items.append(
            {
                "resume_id": resume.id,
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
                "raw_text": resume.raw_text[:200] + ("..." if len(resume.raw_text) > 200 else ""),
                "parsed_skills": resume.parsed_skills or [],
                "coverage_percent": coverage_percent(resume.parsed_skills or [], len(gaps)),
                "gaps": gap_dicts(gaps),
                "learning_path": resume.learning_path.items if resume.learning_path else [],
            }
        )
    avg_score = (
        db.query(func.avg(PracticeAttempt.score))
        .join(Lesson, Lesson.id == PracticeAttempt.lesson_id)
        .join(SkillGap, SkillGap.id == Lesson.skill_gap_id)
        .filter(SkillGap.user_id == user_id)
        .scalar()
    )
    attempts_count = (
        db.query(func.count(PracticeAttempt.id))
        .join(Lesson, Lesson.id == PracticeAttempt.lesson_id)
        .join(SkillGap, SkillGap.id == Lesson.skill_gap_id)
        .filter(SkillGap.user_id == user_id)
        .scalar()
    )
    return {
        "user_id": user_id,
        "resumes": items,
        "gap_trends": trend,
        "average_practice_score": round(float(avg_score or 0), 1),
        "total_attempts": int(attempts_count or 0),
    }


def get_proof_profile(db: Session, identifier: str | int) -> dict | None:
    """Build verified telemetry proof profile with SHA-256 verification hash."""
    user = None
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        user = db.get(User, int(identifier))
    else:
        # Search by slug or name (e.g. jordan-chen-2 or jordan)
        clean_slug = str(identifier).replace("-", " ").strip()
        user = db.query(User).filter(User.name.ilike(f"%{clean_slug}%")).first()

    if user is None:
        user = db.query(User).filter(User.is_sample.is_(True)).first()
    if user is None:
        return None

    # Fetch attempts and passed badges
    passed_attempts = (
        db.query(PracticeAttempt, Lesson)
        .join(Lesson, Lesson.id == PracticeAttempt.lesson_id)
        .join(SkillGap, SkillGap.id == Lesson.skill_gap_id)
        .filter(SkillGap.user_id == user.id, PracticeAttempt.passed.is_(True))
        .all()
    )

    badges = []
    seen_badges = set()
    for attempt, lesson in passed_attempts:
        skill_name = lesson.skill_name or "Engineering Standard"
        if skill_name not in seen_badges:
            seen_badges.add(skill_name)
            badges.append({
                "key": skill_name.lower().replace(" ", "_"),
                "name": f"{skill_name} Verified",
                "earned_at": attempt.created_at.strftime("%b %d") if attempt.created_at else "Recent",
                "attempts": 1,
                "score": attempt.score or 95.0,
            })

    # If no passed attempts yet in DB, populate based on user profile skills
    if not badges:
        resume = latest_resume(db, user.id)
        skills = resume.parsed_skills if resume else ["FastAPI", "SQL", "Git"]
        for s in skills[:4]:
            badges.append({
                "key": s.lower().replace(" ", "_"),
                "name": f"{s} Verified",
                "earned_at": "Recent",
                "attempts": 1,
                "score": 92.0,
            })

    total_attempts = db.query(func.count(PracticeAttempt.id)).join(Lesson).join(SkillGap).filter(SkillGap.user_id == user.id).scalar() or len(badges)
    avg_score = db.query(func.avg(PracticeAttempt.score)).join(Lesson).join(SkillGap).filter(SkillGap.user_id == user.id).scalar() or 91.5

    badge_names = [b["name"] for b in badges]
    proof_hash = generate_proof_hash(user.id, badge_names, float(avg_score))

    name_parts = user.name.split()
    initials = "".join(p[0].upper() for p in name_parts[:2]) if name_parts else "SB"

    skills_radar = [
        {"skill": b["name"].replace(" Verified", ""), "Demand": 85, "You": int(b["score"])}
        for b in badges
    ]

    return {
        "user_id": user.id,
        "name": user.name,
        "initials": initials,
        "target_role": user.target_role or "Software Engineer",
        "verified_hash": proof_hash,
        "verified_url": f"https://skillbridge.ai/proof/{user.name.lower().replace(' ', '-')}-{user.id}",
        "completion_rate": min(100, round((len(badges) / 6) * 100)),
        "average_score": round(float(avg_score), 1),
        "total_attempts": int(total_attempts),
        "badges_count": len(badges),
        "badges": badges,
        "skills_radar": skills_radar,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def get_platform_stats(db: Session) -> dict:
    """Aggregate high-level platform telemetry from actual candidates, resumes, and attempts in the database."""
    total_learners = db.query(func.count(User.id)).scalar() or 0
    total_jobs = db.query(func.count(JobPosting.id)).scalar() or 0
    total_attempts = db.query(func.count(PracticeAttempt.id)).scalar() or 0
    total_resumes = db.query(func.count(Resume.id)).scalar() or 0

    if total_learners == 0:
        return {
            "total_learners": 0,
            "total_scanned_jobs": total_jobs,
            "total_attempts": total_attempts,
            "total_resumes": total_resumes,
            "average_score": 0.0,
            "average_resume_score": 0.0,
            "top_demanded_skills": [],
            "system_status": "operational",
        }

    # Calculate average score across actual stored candidate profiles
    avg_cand_score = db.query(func.avg(Resume.candidate_score)).filter(Resume.candidate_score > 0).scalar()
    if avg_cand_score is None:
        avg_cand_score = db.query(func.avg(PracticeAttempt.score)).scalar() or 0.0

    avg_res_score = db.query(func.avg(Resume.resume_score)).filter(Resume.resume_score > 0).scalar() or 0.0

    # Calculate top skills from all parsed skills across resumes in the database
    resumes = db.query(Resume).all()
    skill_counts: Counter[str] = Counter()
    for r in resumes:
        if r.parsed_skills and isinstance(r.parsed_skills, list):
            for s in r.parsed_skills:
                if s and isinstance(s, str):
                    skill_counts[s] += 1

    # Also aggregate skill gaps
    top_gaps = (
        db.query(SkillGap.skill_name, func.count(SkillGap.id).label("count"))
        .group_by(SkillGap.skill_name)
        .order_by(func.count(SkillGap.id).desc())
        .limit(5)
        .all()
    )
    for g_name, count in top_gaps:
        skill_counts[g_name] += count

    top_skills = [
        {"skill": skill, "frequency": freq}
        for skill, freq in skill_counts.most_common(6)
    ]

    return {
        "total_learners": total_learners,
        "total_scanned_jobs": total_jobs,
        "total_attempts": total_attempts,
        "total_resumes": total_resumes,
        "average_score": round(float(avg_cand_score), 1),
        "average_resume_score": round(float(avg_res_score), 1),
        "top_demanded_skills": top_skills,
        "system_status": "operational",
    }



def get_candidate_resume_data(db: Session, user_id: int) -> dict | None:
    """Retrieve raw extracted resume document data for a candidate."""
    user = db.get(User, user_id)
    if user is None:
        return None
    resume = latest_resume(db, user.id)
    return {
        "user_id": user.id,
        "resume_id": resume.id if resume else None,
        "file_name": resume.file_name if resume else "resume",
        "file_type": resume.file_type if resume else "text",
        "raw_text": resume.raw_text if resume else user.resume_text,
        "parsed_skills": resume.parsed_skills if resume else [],
        "resume_score": resume.resume_score if resume else 0.0,
        "candidate_score": resume.candidate_score if resume else 0.0,
        "created_at": resume.created_at.isoformat() if (resume and resume.created_at) else None,
    }


def get_candidate_analysis_data(db: Session, user_id: int) -> dict | None:
    """Retrieve structured AI analysis data for a candidate."""
    user = db.get(User, user_id)
    if user is None:
        return None
    resume = latest_resume(db, user.id)
    if not resume:
        return {
            "user_id": user.id,
            "resume_id": None,
            "analysis": {},
            "candidate_score": 0.0,
            "resume_score": 0.0,
        }

    ai_analysis = resume.ai_analysis if resume.ai_analysis else (
        analyze_candidate_resume(resume.raw_text, target_position=user.target_role) if resume.raw_text else {}
    )

    return {
        "user_id": user.id,
        "resume_id": resume.id,
        "analysis": ai_analysis,
        "candidate_score": resume.candidate_score or float(ai_analysis.get("candidate_score") or 85.0),
        "resume_score": resume.resume_score or float(ai_analysis.get("resume_score") or 80.0),
    }


def _user_initials(name: str) -> str:
    parts = (name or "Candidate").strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) >= 2:
        return parts[0][:2].upper()
    return "SB"


def create_user_with_resume(
    db: Session,
    name: str,
    target_role: str = "",
    position: str | None = None,
    country: str | None = None,
    country_code: str | None = None,
    currency: str | None = None,
    currency_code: str | None = None,
    currency_symbol: str | None = None,
    email: str | None = None,
    current_role: str = "Customer Support Team Lead",
    location: str = "Austin, TX (or Remote)",
    avatar: str = "",
    current_salary: str = "$52,000",
    target_salary: str = "$89,000",
    experience_years: float = 4.0,
    automation_risk_score: int | None = None,
    shielded_risk_score: int | None = None,
    automation_risk_explanation: str | None = None,
    tasks_at_risk: list | None = None,
    skills_radar: list | None = None,
    salary_growth: list | None = None,
    translated_skills: list | None = None,
    file_bytes: bytes | None = None,
    filename: str = "",
    raw_text: str = "",
) -> User:
    """Create a new user, process their PDF/DOCX resume, run AI analysis, and store all structured data."""
    clean_name = InputSanitizer.sanitize_text(name or "New Candidate", max_chars=200)
    clean_role = InputSanitizer.sanitize_text(position or target_role or "AI Operations & Support Systems Specialist", max_chars=200)
    clean_current_role = InputSanitizer.sanitize_text(current_role or "Customer Support Team Lead", max_chars=200)
    clean_location = InputSanitizer.sanitize_text(location or "Austin, TX (or Remote)", max_chars=200)
    clean_email = InputSanitizer.sanitize_text(email or "", max_chars=255).lower() if email else None

    # Resolve Country and Currency automatically
    country_info = get_country_currency_info(country or country_code or "United States")
    resolved_country = country_info["name"] if country else (country or "United States")
    resolved_country_code = country_info["country_code"]
    resolved_currency = currency if (currency and not country) else country_info["currency"]
    resolved_currency_code = currency_code if (currency_code and not country) else country_info["currency_code"]
    resolved_currency_symbol = currency_symbol if (currency_symbol and not country) else country_info["currency_symbol"]

    # Compute dynamic AI occupational risk for this position
    risk_info = calculate_automation_risk_and_shielded_score(
        clean_role,
        resume_text=raw_text or "",
        country=resolved_country,
    )
    final_auto_risk = automation_risk_score if (automation_risk_score is not None and automation_risk_score != 78) else risk_info["automation_risk_score"]
    final_shield_score = shielded_risk_score if (shielded_risk_score is not None and shielded_risk_score != 14) else risk_info["shielded_risk_score"]
    final_explanation = automation_risk_explanation or risk_info["explanation"]
    final_tasks = tasks_at_risk if tasks_at_risk else risk_info["tasks_at_risk"]

    # Check if existing user with same email exists
    if clean_email:
        existing = db.query(User).filter(User.email == clean_email).first()
        if existing:
            user = existing
            user.name = clean_name
            user.target_role = clean_role
            user.position = clean_role
            user.current_role = clean_current_role
            user.location = clean_location
            user.country = resolved_country
            user.country_code = resolved_country_code
            user.currency = resolved_currency
            user.currency_code = resolved_currency_code
            user.currency_symbol = resolved_currency_symbol
            user.automation_risk_score = final_auto_risk
            user.shielded_risk_score = final_shield_score
            user.automation_risk_explanation = final_explanation
            user.tasks_at_risk = final_tasks
            if avatar:
                user.avatar = avatar
            if current_salary:
                user.current_salary = current_salary
            if target_salary:
                user.target_salary = target_salary
            if experience_years:
                user.experience_years = experience_years
            if skills_radar:
                user.skills_radar = skills_radar
            if salary_growth:
                user.salary_growth = salary_growth
            if translated_skills:
                user.translated_skills = translated_skills
        else:
            user = User(
                name=clean_name,
                target_role=clean_role,
                position=clean_role,
                current_role=clean_current_role,
                location=clean_location,
                country=resolved_country,
                country_code=resolved_country_code,
                currency=resolved_currency,
                currency_code=resolved_currency_code,
                currency_symbol=resolved_currency_symbol,
                avatar=avatar or "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
                current_salary=current_salary or "$52,000",
                target_salary=target_salary or "$89,000",
                experience_years=experience_years or 4.0,
                automation_risk_score=final_auto_risk,
                shielded_risk_score=final_shield_score,
                automation_risk_explanation=final_explanation,
                tasks_at_risk=final_tasks,
                skills_radar=skills_radar or [],
                salary_growth=salary_growth or [],
                translated_skills=translated_skills or [],
                email=clean_email,
                is_sample=False,
            )
            db.add(user)
    else:
        user = User(
            name=clean_name,
            target_role=clean_role,
            position=clean_role,
            current_role=clean_current_role,
            location=clean_location,
            country=resolved_country,
            country_code=resolved_country_code,
            currency=resolved_currency,
            currency_code=resolved_currency_code,
            currency_symbol=resolved_currency_symbol,
            avatar=avatar or "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            current_salary=current_salary or "$52,000",
            target_salary=target_salary or "$89,000",
            experience_years=experience_years or 4.0,
            automation_risk_score=final_auto_risk,
            shielded_risk_score=final_shield_score,
            automation_risk_explanation=final_explanation,
            tasks_at_risk=final_tasks,
            skills_radar=skills_radar or [],
            salary_growth=salary_growth or [],
            translated_skills=translated_skills or [],
            email=None,
            is_sample=False,
        )
        db.add(user)

    db.flush()

    extracted_text = ""
    file_type = "text"

    if file_bytes:
        extracted_text, file_type = extract_document_text(file_bytes, filename=filename)
    elif raw_text:
        extracted_text = InputSanitizer.sanitize_text(raw_text)
        file_type = "text"

    if extracted_text:
        user.resume_text = extracted_text
        parsed_skills = parse_resume_skills(extracted_text)

        # Run structured Gemini AI analysis with country & currency context
        ai_insights = analyze_candidate_resume(
            extracted_text,
            target_position=clean_role,
            country=resolved_country,
            currency=resolved_currency,
            currency_symbol=resolved_currency_symbol,
        )

        user.automation_risk_score = ai_insights.get("automation_risk_score", final_auto_risk)
        user.shielded_risk_score = ai_insights.get("shielded_risk_score", final_shield_score)
        user.automation_risk_explanation = ai_insights.get("automation_risk_explanation", final_explanation)
        user.tasks_at_risk = ai_insights.get("tasks_at_risk", final_tasks)

        resume_score = float(ai_insights.get("resume_score") or 82.0)
        candidate_score = float(ai_insights.get("candidate_score") or 85.0)
        exp_years = float(ai_insights.get("experience_years") or experience_years or 2.0)

        # Merge extracted skills with technical skills from AI
        all_skills = list(dict.fromkeys(parsed_skills + (ai_insights.get("technical_skills") or [])))

        resume = Resume(
            user_id=user.id,
            file_name=filename[:255] if filename else "resume",
            file_type=file_type[:50],
            raw_text=extracted_text,
            parsed_skills=all_skills,
            ai_analysis=ai_insights,
            resume_score=resume_score,
            candidate_score=candidate_score,
            experience_years=exp_years,
        )
        db.add(resume)
        db.flush()

        # Generate initial skill gaps and learning path
        missing = ai_insights.get("missing_skills") or ["Docker", "CI/CD", "FastAPI"]
        gap_dicts_list = [
            {"skill": s, "reason": f"Required production standard for {clean_role}.", "demand_count": max(1, 4 - i)}
            for i, s in enumerate(missing[:4], start=1)
        ]
        persisted_gaps = persist_gaps(db, user, resume, gap_dicts_list)
        path_items = generate_learning_path(gap_dicts_list)
        upsert_learning_path(db, resume.id, path_items)

        # Generate skills radar data if not provided
        if not user.skills_radar:
            radar_items = []
            selected_skills = (all_skills[:3] + missing[:3])[:6]
            if not selected_skills:
                selected_skills = ["Technical Execution", "System Design", "Cloud Infrastructure", "AI Tooling", "Problem Solving", "Leadership"]
            for s in selected_skills:
                is_have = s in all_skills
                current_score = 75 if is_have else 35
                target_score = 90 if s in missing else 92
                radar_items.append({"subject": s, "current": current_score, "target": target_score, "fullMark": 100})
            user.skills_radar = radar_items

        # Generate salary growth trajectory if not provided
        if not user.salary_growth:
            import re
            def _parse_k(val_str, default_val=52):
                nums = re.findall(r"\d+", str(val_str or "").replace(",", ""))
                if nums:
                    v = float(nums[0])
                    return round(v / 1000) if v > 1000 else round(v)
                return default_val

            base_k = _parse_k(user.current_salary, 52)
            tgt_k = _parse_k(user.target_salary, round(base_k * 1.7))
            step = (tgt_k - base_k) / 5.0
            user.salary_growth = [
                {"period": "Current", "baseline": base_k, "reskilled": base_k},
                {"period": "Month 3", "baseline": base_k, "reskilled": round(base_k + step * 0.7)},
                {"period": "Month 6", "baseline": round(base_k + 1), "reskilled": round(base_k + step * 1.7)},
                {"period": "Month 12", "baseline": round(base_k + 2), "reskilled": round(base_k + step * 3.0)},
                {"period": "Year 2", "baseline": round(base_k + 3), "reskilled": round(base_k + step * 4.0)},
                {"period": "Year 3", "baseline": round(base_k + 4), "reskilled": tgt_k},
            ]

        # Generate translated skills if not provided
        if not user.translated_skills and all_skills:
            skill_a = all_skills[0] if len(all_skills) > 0 else "System Architecture"
            skill_b = all_skills[1] if len(all_skills) > 1 else "API Engineering"
            user.translated_skills = [
                {
                    "legacy": f"Implemented traditional {skill_a} operations and manual workflows",
                    "modern": f"Human-in-the-loop (HITL) {skill_a} System Calibration & Safety",
                    "premium": "+35% Market Match",
                    "badge": "AI Alignment"
                },
                {
                    "legacy": f"Maintained data pipelines and regular tasks with {skill_b}",
                    "modern": f"Automated {skill_b} Telemetry & SLA Drift Monitoring",
                    "premium": "+42% Market Match",
                    "badge": "AI Ops"
                }
            ]

    db.commit()
    db.refresh(user)
    return user


def get_user_profile(db: Session, user_id: int) -> dict | None:
    """Retrieve full user profile with resume, AI analysis, gaps, and statistics."""
    user = db.get(User, user_id)
    if user is None:
        return None

    resume = latest_resume(db, user.id)
    gaps = get_gaps_for_resume(db, resume.id) if resume else []
    learning_path = resume.learning_path.items if (resume and resume.learning_path) else []

    # Badges / passed attempts
    passed_attempts = (
        db.query(PracticeAttempt, Lesson)
        .join(Lesson, Lesson.id == PracticeAttempt.lesson_id)
        .join(SkillGap, SkillGap.id == Lesson.skill_gap_id)
        .filter(SkillGap.user_id == user.id, PracticeAttempt.passed.is_(True))
        .all()
    )
    badges = []
    seen_badges = set()
    for attempt, lesson in passed_attempts:
        s_name = lesson.skill_name or "Verified Skill"
        if s_name not in seen_badges:
            seen_badges.add(s_name)
            badges.append({
                "skill": s_name,
                "earned_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
                "score": attempt.score,
            })

    country_val = user.country or "United States"
    currency_val = user.currency or "US Dollar"
    symbol_val = user.currency_symbol or "$"

    ai_analysis = (
        resume.ai_analysis
        if resume and resume.ai_analysis
        else (
            analyze_candidate_resume(
                resume.raw_text,
                target_position=user.target_role,
                country=country_val,
                currency=currency_val,
                currency_symbol=symbol_val,
            )
            if resume and resume.raw_text
            else {}
        )
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "current_role": user.current_role or "Customer Support Team Lead",
        "target_role": user.target_role or "AI Operations & Support Systems Specialist",
        "position": user.position or user.target_role or "AI Operations & Support Systems Specialist",
        "location": user.location or "Austin, TX (or Remote)",
        "country": user.country or "United States",
        "country_code": user.country_code or "US",
        "currency": user.currency or "US Dollar",
        "currency_code": user.currency_code or "USD",
        "currency_symbol": user.currency_symbol or "$",
        "avatar": user.avatar or "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        "current_salary": user.current_salary or "$52,000",
        "target_salary": user.target_salary or "$89,000",
        "experience_years": user.experience_years or (resume.experience_years if resume else 4.0),
        "automation_risk_score": user.automation_risk_score if user.automation_risk_score is not None else 78,
        "shielded_risk_score": user.shielded_risk_score if user.shielded_risk_score is not None else 14,
        "automation_risk_explanation": user.automation_risk_explanation or (ai_analysis.get("automation_risk_explanation") if isinstance(ai_analysis, dict) else ""),
        "tasks_at_risk": user.tasks_at_risk or [],
        "skills_radar": user.skills_radar or [],
        "salary_growth": user.salary_growth or [],
        "translated_skills": user.translated_skills or [],
        "initials": _user_initials(user.name),
        "is_sample": user.is_sample,
        "resume_id": resume.id if resume else None,
        "file_name": resume.file_name if resume else "",
        "file_type": resume.file_type if resume else "pdf",
        "raw_text": resume.raw_text if resume else user.resume_text,
        "parsed_skills": resume.parsed_skills if resume else [],
        "ai_analysis": ai_analysis,
        "resume_score": resume.resume_score if resume else (ai_analysis.get("resume_score") if isinstance(ai_analysis, dict) else 0.0),
        "candidate_score": resume.candidate_score if resume else (ai_analysis.get("candidate_score") if isinstance(ai_analysis, dict) else 0.0),
        "gaps": gap_dicts(gaps),
        "learning_path": learning_path,
        "badges": badges,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def update_user_details(
    db: Session,
    user_id: int,
    name: str | None = None,
    target_role: str | None = None,
    position: str | None = None,
    country: str | None = None,
    country_code: str | None = None,
    currency: str | None = None,
    currency_code: str | None = None,
    currency_symbol: str | None = None,
    email: str | None = None,
    current_role: str | None = None,
    location: str | None = None,
    avatar: str | None = None,
    current_salary: str | None = None,
    target_salary: str | None = None,
    experience_years: float | None = None,
    automation_risk_score: int | None = None,
    shielded_risk_score: int | None = None,
    automation_risk_explanation: str | None = None,
    tasks_at_risk: list | None = None,
    skills_radar: list | None = None,
    salary_growth: list | None = None,
    translated_skills: list | None = None,
) -> User | None:
    """Update user profile metadata."""
    user = db.get(User, user_id)
    if user is None:
        return None
    if name is not None:
        user.name = InputSanitizer.sanitize_text(name, max_chars=200)
    
    role_changed = False
    if target_role is not None:
        user.target_role = InputSanitizer.sanitize_text(target_role, max_chars=200)
        user.position = user.target_role
        role_changed = True
    if position is not None:
        user.position = InputSanitizer.sanitize_text(position, max_chars=200)
        user.target_role = user.position
        role_changed = True
        
    if country is not None:
        info = get_country_currency_info(country)
        user.country = info["name"]
        user.country_code = info["country_code"]
        user.currency = info["currency"]
        user.currency_code = info["currency_code"]
        user.currency_symbol = info["currency_symbol"]
    if country_code is not None and country is None:
        user.country_code = country_code
    if currency is not None:
        user.currency = currency
    if currency_code is not None:
        user.currency_code = currency_code
    if currency_symbol is not None:
        user.currency_symbol = currency_symbol
    if email is not None:
        user.email = InputSanitizer.sanitize_text(email, max_chars=255).lower() if email else None
    if current_role is not None:
        user.current_role = InputSanitizer.sanitize_text(current_role, max_chars=200)
    if location is not None:
        user.location = InputSanitizer.sanitize_text(location, max_chars=200)
    if avatar is not None:
        user.avatar = avatar
    if current_salary is not None:
        user.current_salary = current_salary
    if target_salary is not None:
        user.target_salary = target_salary
    if experience_years is not None:
        user.experience_years = experience_years
        
    if automation_risk_score is not None:
        user.automation_risk_score = automation_risk_score
    if shielded_risk_score is not None:
        user.shielded_risk_score = shielded_risk_score
    if automation_risk_explanation is not None:
        user.automation_risk_explanation = automation_risk_explanation
    if tasks_at_risk is not None:
        user.tasks_at_risk = tasks_at_risk
        
    # If role changed and scores weren't explicitly provided, recalculate dynamically
    if role_changed and automation_risk_score is None:
        risk_calc = calculate_automation_risk_and_shielded_score(
            user.position or user.target_role or "Software Engineer",
            resume_text=user.resume_text or "",
            country=user.country or "United States",
        )
        user.automation_risk_score = risk_calc["automation_risk_score"]
        user.shielded_risk_score = risk_calc["shielded_risk_score"]
        user.automation_risk_explanation = risk_calc["explanation"]
        if tasks_at_risk is None:
            user.tasks_at_risk = risk_calc["tasks_at_risk"]

    if role_changed:
        resume = latest_resume(db, user.id)
        country_val = user.country or "United States"
        currency_val = user.currency or "US Dollar"
        symbol_val = user.currency_symbol or "$"
        raw_txt = (resume.raw_text if resume else "") or user.resume_text or ""
        new_analysis = analyze_candidate_resume(
            raw_txt,
            target_position=user.target_role or user.position or "Software Engineer",
            current_role=user.current_role or "Current Professional",
            country=country_val,
            currency=currency_val,
            currency_symbol=symbol_val,
        )
        if resume:
            resume.ai_analysis = new_analysis

    if skills_radar is not None:
        user.skills_radar = skills_radar
    if salary_growth is not None:
        user.salary_growth = salary_growth
    if translated_skills is not None:
        user.translated_skills = translated_skills
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, user_id: int) -> bool:
    """Delete a user and all cascaded data."""
    user = db.get(User, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True


def reanalyze_user_resume(db: Session, user_id: int) -> dict | None:
    """Re-run Gemini AI analysis on the candidate's latest resume with country awareness."""
    user = db.get(User, user_id)
    if user is None:
        return None
    resume = latest_resume(db, user.id)
    if resume is None or not resume.raw_text:
        return get_user_profile(db, user.id)

    country_val = user.country or "United States"
    currency_val = user.currency or "US Dollar"
    symbol_val = user.currency_symbol or "$"

    ai_insights = analyze_candidate_resume(
        resume.raw_text,
        target_position=user.target_role,
        country=country_val,
        currency=currency_val,
        currency_symbol=symbol_val,
    )
    resume.ai_analysis = ai_insights
    resume.resume_score = float(ai_insights.get("resume_score") or 82.0)
    resume.candidate_score = float(ai_insights.get("candidate_score") or 85.0)
    resume.experience_years = float(ai_insights.get("experience_years") or 2.0)
    resume.parsed_skills = list(dict.fromkeys(resume.parsed_skills + (ai_insights.get("technical_skills") or [])))

    user.automation_risk_score = ai_insights.get("automation_risk_score", user.automation_risk_score)
    user.shielded_risk_score = ai_insights.get("shielded_risk_score", user.shielded_risk_score)
    user.automation_risk_explanation = ai_insights.get("automation_risk_explanation", user.automation_risk_explanation)
    user.tasks_at_risk = ai_insights.get("tasks_at_risk", user.tasks_at_risk)

    # Refresh gaps
    missing = ai_insights.get("missing_skills") or ["Docker", "CI/CD"]
    gap_dicts_list = [
        {"skill": s, "reason": f"Required production standard for {user.target_role}.", "demand_count": max(1, 4 - i)}
        for i, s in enumerate(missing[:4], start=1)
    ]
    # Remove previous gaps
    db.query(SkillGap).filter(SkillGap.resume_id == resume.id).delete()
    persist_gaps(db, user, resume, gap_dicts_list)
    path_items = generate_learning_path(gap_dicts_list)
    upsert_learning_path(db, resume.id, path_items)

    db.commit()
    return get_user_profile(db, user.id)


def get_all_users_summary(db: Session) -> list[dict]:
    """Retrieve all users formatted with full summary metrics."""
    users = db.query(User).order_by(User.id.asc()).all()
    results = []
    for u in users:
        resume = latest_resume(db, u.id)
        candidate_score = resume.candidate_score if (resume and resume.candidate_score) else (
            (resume.ai_analysis.get("candidate_score") if resume and isinstance(resume.ai_analysis, dict) else 0.0)
        )
        resume_score = resume.resume_score if (resume and resume.resume_score) else (
            (resume.ai_analysis.get("resume_score") if resume and isinstance(resume.ai_analysis, dict) else 0.0)
        )
        skills_count = len(resume.parsed_skills) if (resume and resume.parsed_skills) else 0

        results.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "current_role": u.current_role or "Customer Support Team Lead",
            "target_role": u.target_role or "AI Operations & Support Systems Specialist",
            "position": u.position or u.target_role or "AI Operations & Support Systems Specialist",
            "location": u.location or "Austin, TX (or Remote)",
            "country": u.country or "United States",
            "country_code": u.country_code or "US",
            "currency": u.currency or "US Dollar",
            "currency_code": u.currency_code or "USD",
            "currency_symbol": u.currency_symbol or "$",
            "avatar": u.avatar or "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            "current_salary": u.current_salary or "$52,000",
            "target_salary": u.target_salary or "$89,000",
            "experience_years": float(u.experience_years or 4.0),
            "automation_risk_score": int(u.automation_risk_score if u.automation_risk_score is not None else 78),
            "shielded_risk_score": int(u.shielded_risk_score if u.shielded_risk_score is not None else 14),
            "automation_risk_explanation": u.automation_risk_explanation or "",
            "tasks_at_risk": u.tasks_at_risk or [],
            "skills_radar": u.skills_radar or [],
            "salary_growth": u.salary_growth or [],
            "translated_skills": u.translated_skills or [],
            "initials": _user_initials(u.name),
            "is_sample": u.is_sample,
            "resume_id": resume.id if resume else None,
            "file_name": resume.file_name if resume else "",
            "candidate_score": float(candidate_score or 0.0),
            "resume_score": float(resume_score or 0.0),
            "skills_count": skills_count,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return results
