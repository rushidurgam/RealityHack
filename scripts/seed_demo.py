"""CLI script to initialize database tables and seed demo data for SkillBridge AI.

Run:
    python scripts/seed_demo.py
"""

import sys
import os

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import init_db, SessionLocal, engine
from app.models import User, Resume, JobPosting, SkillGap, Lesson, PracticeAttempt
from app.seed import get_or_seed_sample_user


def main():
    print("Initializing SkillBridge AI database...")
    init_db()
    
    db = SessionLocal()
    try:
        user = get_or_seed_sample_user(db)
        print(f"[OK] Seeded demo user: {user.name} (ID: {user.id})")
        
        resume_count = db.query(Resume).filter(Resume.user_id == user.id).count()
        job_count = db.query(JobPosting).filter(JobPosting.user_id == user.id).count()
        gap_count = db.query(SkillGap).filter(SkillGap.user_id == user.id).count()
        attempt_count = db.query(PracticeAttempt).count()
        
        print(f"     - Resumes in DB: {resume_count}")
        print(f"     - Jobs in DB: {job_count}")
        print(f"     - Skill Gaps in DB: {gap_count}")
        print(f"     - Practice Attempts in DB: {attempt_count}")
        print("\nDatabase is ready for hackathon demonstration!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
