"""Comprehensive Verification Script for SkillBridge AI Transformation."""

import json
from fastapi.testclient import TestClient
from app.main import app
from app.services.countries import get_country_currency_info, COUNTRIES_DATA

client = TestClient(app)

print("=== 1. Testing Country to Currency Resolvers ===")
in_info = get_country_currency_info("India")
print(f"India -> {in_info}")
assert in_info["currency_code"] == "INR", "Failed India currency resolution"
assert in_info["currency_symbol"] == "₹", "Failed India symbol resolution"

us_info = get_country_currency_info("US")
print(f"US -> {us_info}")
assert us_info["currency_code"] == "USD"

de_info = get_country_currency_info("Germany")
print(f"Germany -> {de_info}")
assert de_info["currency_symbol"] == "€"

ae_info = get_country_currency_info("United Arab Emirates")
print(f"UAE -> {ae_info}")
assert ae_info["currency_code"] == "AED"
print("✓ Country resolution tests passed successfully!\n")

print("=== 2. Testing API Health Endpoint ===")
health_res = client.get("/health")
print(f"Health status: {health_res.status_code}, data: {health_res.json()}")
assert health_res.status_code == 200

print("=== 3. Testing Candidates List Endpoint ===")
users_res = client.get("/api/users")
print(f"List users status: {users_res.status_code}, count: {len(users_res.json())}")
assert users_res.status_code == 200
users = users_res.json()
assert len(users) > 0
print(f"First user: {users[0]['name']}, Country: {users[0].get('country')}, Currency: {users[0].get('currency_symbol')}")

print("=== 4. Testing Create Candidate JSON with Country ===")
create_payload = {
    "name": "Aarav Patel",
    "email": "aarav.patel@example.com",
    "target_role": "Senior Cloud AI Systems Engineer",
    "position": "Senior Cloud AI Systems Engineer",
    "country": "India",
    "location": "Bengaluru, India",
    "raw_text": "Experienced Python Engineer with 5 years in FastAPI, PostgreSQL, Redis, and Machine Learning pipelines.",
    "current_salary": "₹1,800,000",
    "target_salary": "₹3,500,000"
}
create_res = client.post("/api/users", json=create_payload)
print(f"Create user status: {create_res.status_code}")
assert create_res.status_code == 200
created_user = create_res.json()
print(f"Created candidate ID: {created_user['id']}, Country: {created_user['country']}, Symbol: {created_user['currency_symbol']}")
assert created_user["country"] == "India"
assert created_user["currency_code"] == "INR"
assert created_user["currency_symbol"] == "₹"

print("=== 5. Testing Candidate AI Analysis Structured Fields ===")
analysis = created_user.get("ai_analysis", {})
print("Keys in AI analysis:", list(analysis.keys()))
assert "career_readiness" in analysis, "Missing career_readiness in AI analysis"
assert "skill_gap_analysis" in analysis, "Missing skill_gap_analysis in AI analysis"
assert "career_roadmap" in analysis, "Missing career_roadmap in AI analysis"
assert "resume_strength_analysis" in analysis, "Missing resume_strength_analysis in AI analysis"
assert "interview_readiness" in analysis, "Missing interview_readiness in AI analysis"

print("Career Readiness Score:", analysis["career_readiness"])
print("Skill Gaps:", analysis["skill_gap_analysis"]["high_priority_gaps"])
print("Career Roadmap Next Role:", analysis["career_roadmap"]["recommended_next_role"])

print("=== 6. Testing Candidate Resume File Upload (Simulated Multipart) ===")
sample_resume_content = b"""
Rahul Verma
Senior Python & Distributed Systems Engineer
Experience: 4 years
Skills: Python, FastAPI, Docker, PostgreSQL, Redis, Git, Linux
Education: B.Tech in Computer Science, IIT Bombay
Projects: Built asynchronous event bus handling 50k req/sec with zero latency drift.
"""
files = {
    "file": ("resume_rahul.txt", sample_resume_content, "text/plain")
}
data = {
    "name": "Rahul Verma",
    "position": "Staff AI Platform Engineer",
    "country": "India",
    "location": "Mumbai, India",
    "current_salary": "₹2,200,000",
    "target_salary": "₹4,200,000"
}
upload_res = client.post("/api/users/upload", data=data, files=files)
print(f"Upload user status: {upload_res.status_code}")
assert upload_res.status_code == 200
uploaded_user = upload_res.json()
print(f"Uploaded User ID: {uploaded_user['id']}, Name: {uploaded_user['name']}, Country: {uploaded_user['country']}, Symbol: {uploaded_user['currency_symbol']}")
assert uploaded_user["country"] == "India"
assert uploaded_user["currency_symbol"] == "₹"

print("\n=======================================================")
print("ALL BACKEND TESTS AND TRANSFORMATION CHECKS PASSED 100%!")
print("=======================================================")
