"""End-to-end API and database persistence test suite for SkillBridge AI."""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def run_tests():
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, res.text
    print("[PASS] 1. Health check OK")

    # 2. Demo sample loader
    res = client.post("/api/demo/load-sample")
    assert res.status_code == 200, res.text
    sample = res.json()
    user_id = sample["user_id"]
    resume_id = sample["resume_id"]
    print(f"[PASS] 2. Demo loaded: User #{user_id}, Resume #{resume_id}, Name: {sample['name']}")

    # 3. Session restore
    res = client.get(f"/api/session/latest?user_id={user_id}")
    assert res.status_code == 200, res.text
    session_data = res.json()
    assert len(session_data["jobs"]) > 0
    assert len(session_data["gaps"]) > 0
    print(f"[PASS] 3. Session restored: {len(session_data['gaps'])} gaps, coverage={session_data['coverage_percent']}%")

    # 4. Fetch jobs & persist
    res = client.get(f"/api/jobs?role=backend+engineer&location=United+States&user_id={user_id}")
    assert res.status_code == 200, res.text
    jobs = res.json()
    assert len(jobs) > 0
    print(f"[PASS] 4. Jobs fetched & persisted: {len(jobs)} jobs")

    # 5. Analyze gaps & learning path
    res = client.post("/api/analyze", json={
        "resume_text": "Proficient in Python, FastAPI, SQLite, and Git.",
        "job_descriptions": [j["description"] for j in jobs[:3]],
        "user_id": user_id,
        "name": "Jordan Chen",
        "target_role": "backend engineer"
    })
    assert res.status_code == 200, res.text
    analysis = res.json()
    assert len(analysis["gaps"]) == 3
    assert len(analysis["learning_path"]) == 3
    gap_id = analysis["gaps"][0]["id"]
    print(f"[PASS] 5. Gap analysis OK: {analysis['gaps'][0]['skill']} (Gap ID: {gap_id})")

    # 6. Generate lesson
    res = client.post("/api/generate-lesson", json={
        "skill": analysis["gaps"][0]["skill"],
        "skill_gap_id": gap_id
    })
    assert res.status_code == 200, res.text
    lesson = res.json()
    assert lesson["id"] is not None
    print(f"[PASS] 6. Lesson generated & persisted: ID={lesson['id']}")

    # 7. Check code with rubric
    res = client.post("/api/check-code", json={
        "submitted_code": lesson["starter_code"],
        "solution_code": lesson["solution_code"],
        "lesson_id": lesson["id"],
        "concept": lesson["skill_name"]
    })
    assert res.status_code == 200, res.text
    eval_res = res.json()
    assert "score" in eval_res
    assert "rubric" in eval_res
    attempt_id = eval_res["id"]
    print(f"[PASS] 7. Code graded: passed={eval_res['passed']}, score={eval_res['score']}/100, attempt_id={attempt_id}")

    # 8. Gap chat grounded tutor
    res = client.post("/api/gap-chat", json={
        "skill_gap_id": gap_id,
        "message": "Why is this skill critical in production systems?"
    })
    assert res.status_code == 200, res.text
    chat_res = res.json()
    assert len(chat_res["content"]) > 10
    print(f"[PASS] 8. Grounded gap chat OK: {chat_res['content'][:60]}...")

    # 9. History timeline
    res = client.get(f"/api/history?user_id={user_id}")
    assert res.status_code == 200, res.text
    hist = res.json()
    assert len(hist["resumes"]) >= 3
    print(f"[PASS] 9. History timeline OK: {len(hist['resumes'])} resumes tracked")

    print("\n=======================================================")
    print(" >>> ALL 9 TEST SUITES COMPLETED WITH 100% SUCCESS <<<")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
