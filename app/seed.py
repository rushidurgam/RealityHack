"""Seed 3 historical resume analyses so the demo still looks full if APIs fail."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ChatMessage, JobPosting, LearningPath, Lesson, PracticeAttempt, Resume, SkillGap, User
from app.services.gemini import LESSON_LIBRARY, parse_resume_skills

SAMPLE_JOBS = [
    {
        "title": "Junior Backend Engineer",
        "company": "Northstar Labs",
        "description": "Python FastAPI REST APIs, Docker, SQL, pytest, and Git. Kubernetes is a plus.",
    },
    {
        "title": "Platform Engineer Intern",
        "company": "Harbor Cloud",
        "description": "Containerize services with Docker, deploy with Kubernetes, write Terraform, and monitor Linux hosts.",
    },
    {
        "title": "AI Application Engineer",
        "company": "LumenForge",
        "description": "Ship LLM features behind FastAPI, parse PDFs, return structured JSON, and add input validation.",
    },
]


def seed_if_empty() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.is_sample.is_(True)).first():
            return
        _seed_sample_user(db)
        db.commit()
    finally:
        db.close()


def get_or_seed_sample_user(db: Session) -> User:
    user = db.query(User).filter(User.is_sample.is_(True)).first()
    if user:
        return user
    user = _seed_sample_user(db)
    db.commit()
    db.refresh(user)
    return user


def _seed_sample_user(db: Session) -> User:
    now = datetime.now(timezone.utc)
    user = User(
        name="Jordan Chen",
        email="jordan.chen@example.com",
        target_role="backend engineer",
        resume_text="",
        is_sample=True,
        created_at=now - timedelta(days=90),
    )
    db.add(user)
    db.flush()

    snapshots = [
        {
            "days_ago": 80,
            "text": (
                "Computer science student. Coursework in Python and HTML/CSS. "
                "Built a Streamlit dashboard for class. Familiar with Git and VS Code."
            ),
            "gaps": [
                ("REST APIs", "Job ads ask for API routes and status codes, which this early resume does not show.", 3),
                ("SQL", "Listings require relational queries; the resume only mentions dashboards.", 2),
                ("Docker", "Every backend posting mentions containers; none appear on this snapshot.", 2),
            ],
        },
        {
            "days_ago": 40,
            "text": (
                "Built Python APIs with FastAPI and REST endpoints for a campus project. "
                "Used SQLite and basic SQL. Uploaded PDFs and returned JSON. Git + pytest beginner."
            ),
            "gaps": [
                ("Docker", "Platform roles still require container images and Dockerfiles.", 3),
                ("Testing", "Postings want TestClient and regression tests, not just a pytest mention.", 2),
                ("Authentication", "Intern listings expect JWT or session auth around protected routes.", 1),
            ],
        },
        {
            "days_ago": 1,
            "text": (
                "Built Python APIs with FastAPI, SQLAlchemy, SQLite, React, Git, and PDF parsing. "
                "Created REST endpoints, added Pydantic validation, and connected a simple frontend. "
                "Wrote a few pytest cases for /health."
            ),
            "gaps": [
                ("Docker", "Northstar and Harbor Cloud both require containerizing FastAPI services.", 3),
                ("Kubernetes", "Platform internships expect orchestration after Docker is in place.", 2),
                ("CI/CD", "Listings mention GitHub Actions pipelines that this resume does not describe.", 1),
            ],
        },
    ]

    last_resume = None
    for snap in snapshots:
        created = now - timedelta(days=snap["days_ago"])
        resume = Resume(
            user_id=user.id,
            raw_text=snap["text"],
            parsed_skills=parse_resume_skills(snap["text"]),
            created_at=created,
        )
        db.add(resume)
        db.flush()
        last_resume = resume
        user.resume_text = snap["text"]

        batch_id = f"sample-{resume.id}"
        for job in SAMPLE_JOBS:
            db.add(
                JobPosting(
                    user_id=user.id,
                    resume_id=resume.id,
                    batch_id=batch_id,
                    role="backend engineer",
                    role_query="backend engineer",
                    location="United States",
                    title=job["title"],
                    company=job["company"],
                    description=job["description"],
                    source="seed",
                    created_at=created,
                )
            )

        gap_rows = []
        path_items = []
        for rank, (skill, reason, demand_cnt) in enumerate(snap["gaps"], start=1):
            gap = SkillGap(
                user_id=user.id,
                resume_id=resume.id,
                skill_name=skill,
                reason=reason,
                priority_rank=rank,
                demand_count=demand_cnt,
                status="open" if snap["days_ago"] == 1 else "practiced",
                created_at=created,
            )
            db.add(gap)
            db.flush()
            gap_rows.append(gap)
            path_items.append(
                {
                    "order": rank,
                    "skill": skill,
                    "minutes": 20 + rank * 10,
                    "why": reason,
                }
            )
            library = LESSON_LIBRARY.get(skill) or LESSON_LIBRARY.get("Docker")
            if library and snap["days_ago"] == 1 and rank == 1:
                lesson = Lesson(
                    skill_gap_id=gap.id,
                    skill_name=skill,
                    theory_markdown=library["theory_markdown"],
                    starter_code=library["starter_code"],
                    solution_code=library["solution_code"],
                    created_at=created,
                )
                db.add(lesson)
                db.flush()
                db.add(
                    PracticeAttempt(
                        lesson_id=lesson.id,
                        submitted_code=library["starter_code"],
                        hint="Check line 5: specify --host 0.0.0.0 so the server listens on all container network interfaces.",
                        passed=False,
                        score=68,
                        correctness=3,
                        code_quality=4,
                        concept_match=3,
                        evaluation_json={
                            "passed": False,
                            "score": 68,
                            "hint": "Check line 5: specify --host 0.0.0.0 so the server listens on all container interfaces.",
                            "rubric": {"correctness": 3, "code_quality": 4, "concept_match": 3},
                        },
                        created_at=created,
                    )
                )
                db.add(
                    ChatMessage(
                        skill_gap_id=gap.id,
                        role="user",
                        content="Why do I need to bind Uvicorn to 0.0.0.0 instead of 127.0.0.1 in Docker?",
                        created_at=created + timedelta(minutes=5),
                    )
                )
                db.add(
                    ChatMessage(
                        skill_gap_id=gap.id,
                        role="assistant",
                        content="Inside a container, 127.0.0.1 (localhost) refers strictly to the container's internal loopback interface. Binding to 0.0.0.0 tells Uvicorn to listen on all network interfaces, allowing traffic forwarded from the host machine to reach your FastAPI app.",
                        created_at=created + timedelta(minutes=6),
                    )
                )

        db.add(LearningPath(resume_id=resume.id, items=path_items, created_at=created))

    if last_resume:
        user.target_role = "backend engineer"
    return user
