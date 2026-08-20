"""Security & Hardening Verification Test Suite for SkillBridge AI."""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import generate_proof_hash, verify_proof_hash

client = TestClient(app)


def test_security_suite():
    print("=======================================================")
    print(" >>> STARTING SKILLBRIDGE AI SECURITY & HARDENING TESTS <<<")
    print("=======================================================\n")

    # -------------------------------------------------------------------------
    # 1. OWASP Security Headers Test
    # -------------------------------------------------------------------------
    res = client.get("/health")
    assert res.status_code == 200
    headers = res.headers
    assert headers.get("x-content-type-options") == "nosniff", "Missing X-Content-Type-Options"
    assert headers.get("x-frame-options") == "DENY", "Missing X-Frame-Options"
    assert headers.get("x-xss-protection") == "1; mode=block", "Missing X-XSS-Protection"
    assert "strict-origin-when-cross-origin" in headers.get("referrer-policy", ""), "Missing Referrer-Policy"
    assert "Content-Security-Policy" in headers or "content-security-policy" in headers, "Missing CSP"
    print("[PASS] 1. OWASP Security Headers verified on API responses")

    # -------------------------------------------------------------------------
    # 2. System Health & Database Diagnostics Test
    # -------------------------------------------------------------------------
    health_data = res.json()
    assert health_data["status"] in {"ok", "degraded"}
    assert "database" in health_data
    assert "latency_ms" in health_data["database"]
    assert "uptime_seconds" in health_data
    print(f"[PASS] 2. System Diagnostics verified: DB latency = {health_data['database']['latency_ms']}ms, tables = {health_data['database'].get('tables_count')}")

    # -------------------------------------------------------------------------
    # 3. PDF Upload Magic-Byte Rejection Test
    # -------------------------------------------------------------------------
    # Uploading an executable/text file renamed to .pdf
    fake_pdf = b"THIS_IS_NOT_A_REAL_PDF_HEADER_JUST_TEXT"
    res = client.post(
        "/api/upload",
        files={"file": ("fake_resume.pdf", fake_pdf, "application/pdf")},
        data={"name": "Test User", "target_role": "Backend Engineer"}
    )
    assert res.status_code == 400, f"Expected 400 for fake PDF, got {res.status_code}"
    err_detail = res.json().get("detail", "")
    assert "PDF" in err_detail or "format" in err_detail
    print(f"[PASS] 3. Magic-Byte Validation rejected fake PDF: '{err_detail}'")

    # Valid PDF with real magic header
    real_pdf_magic = b"%PDF-1.4\n1 0 obj\n<<\n>>\nendobj\ntrailer\n<<\n>>\n%%EOF"
    res = client.post(
        "/api/upload",
        files={"file": ("real_resume.pdf", real_pdf_magic, "application/pdf")},
        data={"name": "Alice Security", "target_role": "Security Engineer"}
    )
    assert res.status_code == 200, f"Expected 200 for valid PDF header, got {res.status_code}: {res.text}"
    user_id = res.json()["user_id"]
    print(f"[PASS] 3b. Genuine PDF magic-header accepted -> User #{user_id}")

    # -------------------------------------------------------------------------
    # 4. Input Sanitization & XSS Neutralization Test
    # -------------------------------------------------------------------------
    xss_payload = "<script>alert('pwned')</script>Developer in Python\x00 and FastAPI"
    res = client.post(
        "/api/resume/save",
        json={"raw_text": xss_payload, "name": "<script>Test</script>Bob", "target_role": "Engineer", "user_id": user_id}
    )
    assert res.status_code == 200
    saved = res.json()
    assert "<script>" not in saved["extracted_text"], "Script tag was not sanitized!"
    assert "\x00" not in saved["extracted_text"], "Null byte was not sanitized!"
    assert "<script>" not in saved["name"], "Name was not sanitized!"
    print("[PASS] 4. Input Sanitizer stripped XSS script tags and control characters")

    # -------------------------------------------------------------------------
    # 5. Verified Proof-of-Work & SHA-256 Hash Verification Test
    # -------------------------------------------------------------------------
    badges = ["Docker Verified", "FastAPI Verified", "SQL Verified"]
    hash_val = generate_proof_hash(user_id=user_id, completed_badges=badges, avg_score=94.5)
    assert len(hash_val) == 16
    assert verify_proof_hash(user_id=user_id, completed_badges=badges, avg_score=94.5, proof_hash=hash_val)
    assert not verify_proof_hash(user_id=user_id, completed_badges=badges, avg_score=70.0, proof_hash=hash_val)
    print(f"[PASS] 5. Cryptographic SHA-256 Telemetry Hash verified: {hash_val}")

    # -------------------------------------------------------------------------
    # 6. Public Proof-of-Work Profile Endpoint Test
    # -------------------------------------------------------------------------
    res = client.get(f"/api/proof/{user_id}")
    assert res.status_code == 200
    proof_data = res.json()
    assert proof_data["user_id"] == user_id
    assert "verified_hash" in proof_data
    assert "skills_radar" in proof_data
    print(f"[PASS] 6. Proof-of-Work Public Profile OK: {proof_data['verified_url']} (Hash: {proof_data['verified_hash']})")

    # -------------------------------------------------------------------------
    # 7. Platform Telemetry & Roles Endpoints Test
    # -------------------------------------------------------------------------
    res = client.get("/api/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_learners"] >= 1
    assert "top_demanded_skills" in stats
    print(f"[PASS] 7. Platform Telemetry Stats: {stats['total_learners']} learners, top skills: {[s['skill'] for s in stats['top_demanded_skills'][:3]]}")

    res = client.get("/api/roles")
    assert res.status_code == 200
    roles = res.json()
    assert len(roles) >= 4
    print(f"[PASS] 7b. Role taxonomies retrieved: {len(roles)} roles available")

    # -------------------------------------------------------------------------
    # 8. Standardized Error Masking & Schema Validation Test
    # -------------------------------------------------------------------------
    # Send malformed payload to verify structured 422 error envelope
    res = client.post("/api/analyze", json={"bad_field": 123})
    assert res.status_code == 422
    err_json = res.json()
    assert err_json.get("status") == "error"
    assert "detail" in err_json
    assert "errors" in err_json
    print(f"[PASS] 8. Safe standardized validation error envelope verified: '{err_json['detail']}'")

    print("\n=======================================================")
    print(" >>> ALL SECURITY & HARDENING TESTS PASSED (100%) <<<")
    print("=======================================================")


if __name__ == "__main__":
    test_security_suite()
