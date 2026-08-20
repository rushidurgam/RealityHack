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
        if db.query(User).first():
            return
        _seed_default_personas(db)
        _seed_sample_user(db)
        db.commit()
    finally:
        db.close()


def _seed_default_personas(db: Session) -> None:
    """Seed initial rich personas into the database so all initial user profiles are DB-backed."""
    now = datetime.now(timezone.utc)

    # 1. Priya Sharma
    priya = User(
        name="Priya Sharma",
        email="priya.sharma@example.com",
        current_role="Customer Support Team Lead",
        target_role="AI Operations & Support Systems Specialist",
        position="AI Operations & Support Systems Specialist",
        location="Austin, TX (or Remote)",
        country="United States",
        country_code="US",
        currency="US Dollar",
        currency_code="USD",
        currency_symbol="$",
        avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        current_salary="$52,000",
        target_salary="$89,000",
        experience_years=4.0,
        automation_risk_score=78,
        shielded_risk_score=14,
        tasks_at_risk=[
            {"task": "Repetitive L1 ticket handling & chat response", "risk": 92, "status": "AI Replaced"},
            {"task": "Standard email templates & status tracking", "risk": 85, "status": "AI Replaced"},
            {"task": "Team scheduling and basic KPI reporting", "risk": 65, "status": "AI Augmented"},
            {"task": "Complex customer escalation & empathy bridge", "risk": 24, "status": "Human Moat"}
        ],
        skills_radar=[
            {"subject": "Customer Empathy & Comm", "current": 95, "target": 95, "fullMark": 100},
            {"subject": "SaaS Tooling & CRM", "current": 85, "target": 90, "fullMark": 100},
            {"subject": "AI Agent Prompting & Logic", "current": 35, "target": 85, "fullMark": 100},
            {"subject": "Knowledge Base Curation (RAG)", "current": 40, "target": 80, "fullMark": 100},
            {"subject": "Data Analytics & SQL", "current": 30, "target": 75, "fullMark": 100},
            {"subject": "Incident Escalation Mgmt", "current": 90, "target": 95, "fullMark": 100}
        ],
        salary_growth=[
            {"period": "Current", "baseline": 52, "reskilled": 52},
            {"period": "Month 3", "baseline": 52, "reskilled": 64},
            {"period": "Month 6", "baseline": 53, "reskilled": 76},
            {"period": "Month 12", "baseline": 54, "reskilled": 89},
            {"period": "Year 2", "baseline": 55, "reskilled": 105},
            {"period": "Year 3", "baseline": 56, "reskilled": 122}
        ],
        translated_skills=[
            {
                "legacy": "De-escalated angry customer calls in high stress queues",
                "modern": "Human-in-the-loop (HITL) Edge Case Resolution & Alignment Safety",
                "premium": "+35% Market Match",
                "badge": "AI Safety"
            },
            {
                "legacy": "Created FAQ docs and Zendesk macro templates",
                "modern": "Domain Knowledge Extraction for RAG LLM Context Grounding",
                "premium": "+42% Market Match",
                "badge": "RAG Systems"
            },
            {
                "legacy": "Monitored team CSAT and response times daily",
                "modern": "AI Agent Performance Telemetry & SLA Drift Monitoring",
                "premium": "+28% Market Match",
                "badge": "AI Ops"
            }
        ],
        resume_text="Customer Support Team Lead with 4 years managing tier 2 queues, Zendesk escalations, and cross-functional triage.",
        is_sample=True,
        created_at=now - timedelta(days=60),
    )
    db.add(priya)

    # 2. Carlos Mendez
    carlos = User(
        name="Carlos Mendez",
        email="carlos.mendez@example.com",
        current_role="Warehouse Logistics Supervisor",
        target_role="Automated Robotics & Supply Chain Coordinator",
        position="Automated Robotics & Supply Chain Coordinator",
        location="Chicago, IL",
        country="United States",
        country_code="US",
        currency="US Dollar",
        currency_code="USD",
        currency_symbol="$",
        avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        current_salary="$58,000",
        target_salary="$96,000",
        experience_years=6.0,
        automation_risk_score=84,
        shielded_risk_score=16,
        tasks_at_risk=[
            {"task": "Manual pallet barcode scanning & verification", "risk": 95, "status": "AI Replaced"},
            {"task": "Physical inventory cycle counting", "risk": 88, "status": "AI Replaced"},
            {"task": "Forklift dispatch & spatial route assignment", "risk": 72, "status": "AI Augmented"},
            {"task": "Cross-functional safety compliance & vendor resolution", "risk": 20, "status": "Human Moat"}
        ],
        skills_radar=[
            {"subject": "Supply Chain Operations", "current": 90, "target": 95, "fullMark": 100},
            {"subject": "OSHA & Safety Protocols", "current": 95, "target": 95, "fullMark": 100},
            {"subject": "Autonomous Fleet Telematics", "current": 25, "target": 85, "fullMark": 100},
            {"subject": "Warehouse Mgmt Systems (WMS)", "current": 80, "target": 90, "fullMark": 100},
            {"subject": "Predictive Inventory Logic", "current": 30, "target": 80, "fullMark": 100},
            {"subject": "Hardware Troubleshooting", "current": 65, "target": 85, "fullMark": 100}
        ],
        salary_growth=[
            {"period": "Current", "baseline": 58, "reskilled": 58},
            {"period": "Month 3", "baseline": 58, "reskilled": 70},
            {"period": "Month 6", "baseline": 59, "reskilled": 82},
            {"period": "Month 12", "baseline": 60, "reskilled": 96},
            {"period": "Year 2", "baseline": 61, "reskilled": 112},
            {"period": "Year 3", "baseline": 62, "reskilled": 128}
        ],
        translated_skills=[
            {
                "legacy": "Managed physical picking paths to reduce walking time",
                "modern": "Algorithmic Route Optimization & Spatial Fleet Efficiency Calibration",
                "premium": "+40% Market Match",
                "badge": "Spatial AI"
            },
            {
                "legacy": "Trained staff on heavy equipment safety standards",
                "modern": "Cobot (Collaborative Robot) Ergonomics & Human-Machine Protocol Lead",
                "premium": "+38% Market Match",
                "badge": "Robotics Safety"
            }
        ],
        resume_text="Warehouse supervisor with 6 years experience optimizing pallet flow, safety audits, and material dispatch.",
        is_sample=True,
        created_at=now - timedelta(days=45),
    )
    db.add(carlos)

    # 3. Maya Lin
    maya = User(
        name="Maya Lin",
        email="maya.lin@example.com",
        current_role="Graphic & Production Designer",
        target_role="Generative AI Creative Director",
        position="Generative AI Creative Director",
        location="Seattle, WA (Remote)",
        country="United States",
        country_code="US",
        currency="US Dollar",
        currency_code="USD",
        currency_symbol="$",
        avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        current_salary="$62,000",
        target_salary="$115,000",
        experience_years=5.0,
        automation_risk_score=82,
        shielded_risk_score=12,
        tasks_at_risk=[
            {"task": "Stock image clipping and background removals", "risk": 98, "status": "AI Replaced"},
            {"task": "Basic social media banner resizing & variants", "risk": 94, "status": "AI Replaced"},
            {"task": "Color grading and mockup generation", "risk": 76, "status": "AI Augmented"},
            {"task": "Brand identity strategy & emotive visual storytelling", "risk": 18, "status": "Human Moat"}
        ],
        skills_radar=[
            {"subject": "Visual Aesthetic & Art Direction", "current": 95, "target": 98, "fullMark": 100},
            {"subject": "Adobe Creative Suite", "current": 95, "target": 90, "fullMark": 100},
            {"subject": "Diffusion Models & ControlNet", "current": 40, "target": 92, "fullMark": 100},
            {"subject": "Consistent Character Prompting", "current": 45, "target": 88, "fullMark": 100},
            {"subject": "3D & Generative Video Pipelines", "current": 30, "target": 85, "fullMark": 100},
            {"subject": "Brand Governance & IP Safeguards", "current": 75, "target": 95, "fullMark": 100}
        ],
        salary_growth=[
            {"period": "Current", "baseline": 62, "reskilled": 62},
            {"period": "Month 3", "baseline": 63, "reskilled": 78},
            {"period": "Month 6", "baseline": 63, "reskilled": 94},
            {"period": "Month 12", "baseline": 64, "reskilled": 115},
            {"period": "Year 2", "baseline": 66, "reskilled": 135},
            {"period": "Year 3", "baseline": 68, "reskilled": 155}
        ],
        translated_skills=[
            {
                "legacy": "Retouched product photos and color-corrected batch files",
                "modern": "Custom LoRA Latent Weighting & High-Fidelity Diffusion Synthesis",
                "premium": "+48% Market Match",
                "badge": "GenAI Studio"
            },
            {
                "legacy": "Designed print brochures and client presentation decks",
                "modern": "Multimodal Generative Asset Pipeline Architect",
                "premium": "+52% Market Match",
                "badge": "Brand Architecture"
            }
        ],
        resume_text="Senior Graphic Designer specializing in brand identities, high-resolution rendering, and visual guidelines.",
        is_sample=True,
        created_at=now - timedelta(days=30),
    )
    db.add(maya)
    db.flush()


def get_or_seed_sample_user(db: Session) -> User:
    user = db.query(User).filter(User.is_sample.is_(True)).first()
    if user:
        return user
    _seed_default_personas(db)
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
