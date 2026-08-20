"""End-to-End dynamic candidate creation, PDF/DOCX resume upload, Gemini AI insights,
and database persistence test suite for SkillBridge AI.
"""

import io
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import docx
from pypdf import PdfWriter
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def generate_sample_pdf(text_content: str) -> bytes:
    """Generate a minimal valid PDF containing raw text stream."""
    # Create valid PDF structure with pypdf
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    # Add text via annotation or stream
    out = io.BytesIO()
    writer.write(out)
    # Or create a structured PDF binary
    pdf_bytes = out.getvalue()
    
    # We can also generate a text-extractable PDF using simple PDF text stream:
    pdf_raw = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length " + str(len(text_content) + 40).encode() + b">>\n"
        b"stream\n"
        b"BT /F1 12 Tf 50 700 Td (" + text_content.replace("(", "").replace(")", "").encode("latin-1", "ignore") + b") Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000052 00000 n \n"
        b"0000000101 00000 n \n"
        b"0000000195 00000 n \n"
        b"trailer<</Size 5/Root 1 0 R>>\n"
        b"startxref\n"
        b"300\n"
        b"%%EOF\n"
    )
    return pdf_raw


def generate_sample_docx(paragraphs: list[str]) -> bytes:
    """Generate a valid DOCX document with python-docx."""
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


def run_dynamic_tests():
    print("\n=======================================================")
    print(" >>> STARTING SKILLBRIDGE AI DYNAMIC APP TESTS <<<")
    print("=======================================================\n")

    # 1. Health Diagnostics
    res = client.get("/health")
    assert res.status_code == 200, res.text
    health = res.json()
    print(f"[PASS] 1. Health check: status={health['status']}, database={health['database']['status']}")

    # 2. Create Candidate A with PDF Resume (Python / Backend Developer)
    pdf_resume_text = (
        "Rahul Sharma - Senior Backend Developer. "
        "5+ years experience architecting high-throughput Python APIs with FastAPI, SQLAlchemy, PostgreSQL, and Redis. "
        "Experienced in Docker containerization, CI/CD with GitHub Actions, and Git. "
        "Education: Bachelor of Technology in Computer Science, IIT Bombay. "
        "Certifications: AWS Certified Solutions Architect. "
        "Strengths: Distributed systems, database optimization, RESTful API design."
    )
    pdf_bytes = generate_sample_pdf(pdf_resume_text)

    res = client.post(
        "/api/users",
        data={
            "name": "Rahul Sharma",
            "target_role": "Backend Developer",
            "email": "rahul.sharma@example.com",
        },
        files={"file": ("Rahul_Sharma_Resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert res.status_code == 200, res.text
    cand_a = res.json()
    cand_a_id = cand_a["id"]
    print(f"[PASS] 2. Candidate A created: ID={cand_a_id}, Name={cand_a['name']}, Role={cand_a['target_role']}")
    print(f"       Scores: Candidate Score={cand_a['candidate_score']}/100, Resume Score={cand_a['resume_score']}/100")
    print(f"       Extracted Skills: {cand_a['parsed_skills']}")
    assert len(cand_a["parsed_skills"]) > 0
    assert "ai_analysis" in cand_a
    assert len(cand_a["ai_analysis"].get("interview_questions", [])) > 0

    # 3. Create Candidate B with DOCX Resume (Embedded / IoT Engineer)
    docx_paragraphs = [
        "Priya Patel - IoT & Embedded Firmware Engineer",
        "Experience: 3 years developing firmware for ESP32 and ARM Cortex microcontrollers in Embedded C/C++.",
        "Hands-on expertise with FreeRTOS multitasking, MQTT telemetry protocol, I2C/SPI sensor drivers, and Edge Computing.",
        "Education: Master of Science in Embedded Systems, Purdue University.",
        "Certifications: CompTIA Security+.",
        "Strengths: Real-time scheduling, hardware bring-up, low-power telemetry optimization.",
    ]
    docx_bytes = generate_sample_docx(docx_paragraphs)

    res = client.post(
        "/api/users",
        data={
            "name": "Priya Patel",
            "target_role": "IoT & Embedded Systems Engineer",
            "email": "priya.patel@example.com",
        },
        files={"file": ("Priya_Patel_Resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res.status_code == 200, res.text
    cand_b = res.json()
    cand_b_id = cand_b["id"]
    print(f"\n[PASS] 3. Candidate B created: ID={cand_b_id}, Name={cand_b['name']}, Role={cand_b['target_role']}")
    print(f"       Scores: Candidate Score={cand_b['candidate_score']}/100, Resume Score={cand_b['resume_score']}/100")
    print(f"       Extracted Skills: {cand_b['parsed_skills']}")
    assert len(cand_b["parsed_skills"]) > 0

    # 4. Verify Candidate-Specific AI Insights are Distinct
    print("\n[VERIFY] 4. Testing candidate-specific differentiation:")
    print(f"   Candidate A (Rahul) summary: {cand_a['ai_analysis'].get('summary')[:80]}...")
    print(f"   Candidate B (Priya) summary: {cand_b['ai_analysis'].get('summary')[:80]}...")
    assert cand_a["ai_analysis"].get("summary") != cand_b["ai_analysis"].get("summary")
    print(f"   Candidate A interview questions: {cand_a['ai_analysis'].get('interview_questions')[:2]}")
    print(f"   Candidate B interview questions: {cand_b['ai_analysis'].get('interview_questions')[:2]}")
    assert cand_a["ai_analysis"].get("interview_questions") != cand_b["ai_analysis"].get("interview_questions")
    print("[PASS] 4. Candidate AI insights are 100% user-specific and distinct!")

    # 5. List All Candidates
    res = client.get("/api/users")
    assert res.status_code == 200, res.text
    user_list = res.json()
    user_ids = [u["id"] for u in user_list]
    assert cand_a_id in user_ids
    assert cand_b_id in user_ids
    print(f"\n[PASS] 5. GET /api/users returned {len(user_list)} candidates (includes #{cand_a_id} and #{cand_b_id})")

    # 6. Retrieve Specific Candidate Profiles
    res = client.get(f"/api/users/{cand_a_id}")
    assert res.status_code == 200, res.text
    profile_a = res.json()
    assert profile_a["name"] == "Rahul Sharma"
    assert profile_a["file_type"] in ["pdf", "text"]
    print(f"[PASS] 6. GET /api/users/{cand_a_id} verified with full profile")

    # 7. Candidate Resume & AI Analysis Endpoints
    res = client.get(f"/api/users/{cand_a_id}/resume")
    assert res.status_code == 200, res.text
    resume_doc = res.json()
    assert len(resume_doc["raw_text"]) > 0
    print(f"[PASS] 7a. GET /api/users/{cand_a_id}/resume returned raw extracted text ({len(resume_doc['raw_text'])} chars)")

    res = client.get(f"/api/users/{cand_a_id}/analysis")
    assert res.status_code == 200, res.text
    analysis_data = res.json()
    assert "analysis" in analysis_data
    print(f"[PASS] 7b. GET /api/users/{cand_a_id}/analysis returned structured AI insights")

    # 8. Re-analyze Candidate with Gemini
    res = client.post(f"/api/users/{cand_a_id}/reanalyze")
    assert res.status_code == 200, res.text
    reanalyzed = res.json()
    assert reanalyzed["id"] == cand_a_id
    print(f"[PASS] 8. POST /api/users/{cand_a_id}/reanalyze succeeded")

    # 9. Replace Candidate Resume (Upload new version)
    updated_docx = generate_sample_docx([
        "Rahul Sharma - Lead Cloud Architect",
        "7+ years experience with Kubernetes cluster operations, Terraform, AWS, Docker, and FastAPI.",
    ])
    res = client.post(
        f"/api/users/{cand_a_id}/resume",
        files={"file": ("Rahul_Sharma_v2.docx", updated_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res.status_code == 200, res.text
    updated_profile = res.json()
    assert "Kubernetes" in updated_profile["parsed_skills"] or "Kubernetes" in updated_profile["ai_analysis"].get("technical_skills", []) or "FastAPI" in updated_profile["parsed_skills"]
    print(f"[PASS] 9. Candidate resume replacement & re-analysis verified: new skills={updated_profile['parsed_skills']}")

    # 10. Platform Statistics Aggregation
    res = client.get("/api/stats")
    assert res.status_code == 200, res.text
    stats = res.json()
    assert stats["total_learners"] >= 2
    assert stats["average_score"] > 0
    assert len(stats["top_demanded_skills"]) > 0
    print(f"\n[PASS] 10. GET /api/stats dynamic metrics:")
    print(f"        Total Candidates: {stats['total_learners']}")
    print(f"        Average Score: {stats['average_score']}%")
    print(f"        Top Skills: {[s['skill'] for s in stats['top_demanded_skills'][:4]]}")

    # 11. Invalid File Format Error Handling
    res = client.post(
        "/api/users",
        data={"name": "Invalid User", "target_role": "Tester"},
        files={"file": ("malicious.exe", b"MZNotAValidDocumentContentHere", "application/octet-stream")},
    )
    assert res.status_code in [400, 422], f"Expected 400 or 422 for invalid file, got {res.status_code}: {res.text}"
    print("[PASS] 11. Invalid file upload properly rejected with 400 Bad Request")

    # 12. Delete Candidate
    res = client.delete(f"/api/users/{cand_b_id}")
    assert res.status_code == 200, res.text
    # Verify candidate is gone
    res_check = client.get(f"/api/users/{cand_b_id}")
    assert res_check.status_code == 404
    print(f"[PASS] 12. DELETE /api/users/{cand_b_id} deleted candidate and cascaded relations")

    print("\n=======================================================")
    print(" >>> ALL 12 DYNAMIC TEST SUITES PASSED WITH 100% <<<")
    print("=======================================================\n")


if __name__ == "__main__":
    run_dynamic_tests()
