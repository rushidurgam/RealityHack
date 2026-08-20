# SkillBridge AI — Quickstart & Running Guide

SkillBridge AI matches candidate resumes/syllabi against live job postings, identifies concrete skill gaps, generates targeted micro-lessons, evaluates coding practice with 0–100 rubric scoring, and persists all history into PostgreSQL/Supabase (with local SQLite fallback).

---

## 1. Prerequisites

- **Python**: 3.11+ (Virtualenv in `.venv`)
- **Node.js**: 18+ and npm
- **Database**: SQLite (default, zero-config) or Supabase / PostgreSQL

---

## 2. Environment Variables (`.env`)

Copy `.env.example` to `.env` if you haven't already:

```powershell
copy .env.example .env
```

Key variables:
```env
# Google Gemini API Key (https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Adzuna Job Search API (https://developer.adzuna.com/)
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
ADZUNA_COUNTRY=us

# Database URL (Defaults to local SQLite; paste Supabase PostgreSQL URL to connect Supabase)
DATABASE_URL=sqlite:///./skillbridge.db
# Example Supabase Postgres URL:
# DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres

# Frontend CORS
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

---

## 3. Starting the Backend

Open a PowerShell terminal in the project root:

```powershell
cd "C:\Users\Rushi\skillbridge-ai"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify backend health:
```powershell
curl http://127.0.0.1:8000/health
```

---

## 4. Starting the Frontend

Open a second PowerShell terminal in `frontend`:

```powershell
cd "C:\Users\Rushi\skillbridge-ai\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
```

Open your browser at `http://127.0.0.1:5173`.

---

## 5. Supabase / PostgreSQL Setup

1. Create a project in [Supabase](https://supabase.com/).
2. In Supabase Dashboard, open the **SQL Editor**.
3. Open [`schema.sql`](./schema.sql) in this repository, paste the entire SQL script, and click **Run**.
4. In your Supabase Project Settings -> Database, copy the **Connection string (URI)**.
5. In `.env`, set:
   ```env
   DATABASE_URL=postgresql://postgres.xxxx:your_password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
6. Restart the backend. SQLAlchemy will automatically connect to Supabase with connection pooling!

---

## 6. Seed Demo Data & Verify Persistence

### Seed via Command Line:
```powershell
.\.venv\Scripts\python.exe scripts/seed_demo.py
```

### Seed & Load via Web UI:
- Click the **⚡ Load Sample Demo** button in the header.
- This loads **Jordan Chen's** 3-snapshot historical journey over 90 days, populated job postings, skill gaps, learning path, and active Docker sprint with pre-recorded rubric evaluation.

### Verify Persistence:
1. Fetch target jobs → note the database badge `Saved X jobs to database`.
2. Run Gap Analysis → note the badge `Saved Analysis & 3 Gaps (Resume #ID)`.
3. Check code submission → note the badge `Saved Practice Attempt #ID (Score: X/100)`.
4. Refresh the page in your browser → the application will automatically restore your complete session state via `GET /api/session/latest`.
5. Click **📊 History & Trends** in the header to view multi-resume progression over time.
6. Click **📄 PDF Report** in the setup panel to print or save a candidate report.

---

## 7. AI Agent Layer (`agents.py`)

The reusable AI multi-agent orchestration layer is implemented in:
- `C:\Users\Rushi\Downloads\agents\agents.py`
- `app/services/agents.py`

Functions exposed:
- `extract_resume_skills(resume_text)`: Extracts verified technical skills.
- `analyze_skill_gaps_agent(resume_text, job_descriptions)`: Compares demand vs resume.
- `generate_lesson_agent(skill, gap_reason, job_context)`: Generates theory, broken starter code, and solution.
- `evaluate_practice_attempt_agent(submitted_code, solution_code, concept)`: 0–100 rubric scoring without server-side execution.
