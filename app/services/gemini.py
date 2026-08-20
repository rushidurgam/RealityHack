"""SkillBridge AI — Dynamic AI Agent & Heuristic Research Engine.

Provides dynamic skill extraction, gap delta intelligence, micro-sprint generation,
0-100 rubric code evaluation, and grounded Q&A tutoring powered by Google Gemini
with resilient multi-model fallback and local NLP heuristics.
"""

from __future__ import annotations

import json
import logging
import re
import warnings
from collections import Counter
from difflib import SequenceMatcher
from typing import Any

# Suppress google deprecation warnings from standard output
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import google.generativeai as genai
from app.config import settings
from app.core.security import InputSanitizer

logger = logging.getLogger("skillbridge.ai")

# Comprehensive engineering domain catalog for dynamic matching
DOMAIN_CATALOG: dict[str, dict[str, Any]] = {
    # Backend & API
    "FastAPI": {"aliases": ["fastapi", "fast api"], "why": "Builds typed Python async APIs with automatic OpenAPI docs and high throughput."},
    "REST APIs": {"aliases": ["rest api", "rest apis", "restful", "endpoints", "http routes"], "why": "Core backend resource contracts, status codes, and HTTP method design."},
    "SQL": {"aliases": ["sql", "postgresql", "postgres", "mysql", "sqlite", "relational database"], "why": "Relational data querying, indexing, schema modeling, and ACID transactions."},
    "SQLAlchemy": {"aliases": ["sqlalchemy", "orm", "database sessions"], "why": "Python ORM modeling, declarative relationships, session lifecycles, and migrations."},
    "Authentication": {"aliases": ["authentication", "auth", "jwt", "oauth", "oauth2", "login", "bearer token"], "why": "Protects sensitive user data, role-based access control, and token verification."},
    "Input Validation": {"aliases": ["validation", "pydantic", "schema validation", "request validation"], "why": "Blocks malformed or malicious payloads before reaching core application logic."},
    "Testing": {"aliases": ["unit test", "pytest", "testclient", "testing", "integration tests", "mocking"], "why": "Ensures reliability, regression prevention, and contract adherence in APIs."},
    "Redis": {"aliases": ["redis", "cache", "caching", "in-memory store", "session store"], "why": "Low-latency in-memory caching, message brokers, and rate limiting."},
    "GraphQL": {"aliases": ["graphql", "apollo", "strawberry", "schema stitching"], "why": "Flexible client-driven querying without over-fetching endpoints."},
    "Microservices": {"aliases": ["microservices", "service oriented", "event-driven", "grpc", "protobuf"], "why": "Distributed service architectures, inter-service RPCs, and decoupled deployments."},

    # Cloud & DevOps
    "Docker": {"aliases": ["docker", "dockerfile", "container", "containerize", "containers"], "why": "Packages services and dependencies into repeatable, isolated runtime environments."},
    "Kubernetes": {"aliases": ["kubernetes", "k8s", "helm", "orchestration", "ingress"], "why": "Automates scaling, rolling updates, self-healing, and multi-node cluster management."},
    "CI/CD": {"aliases": ["ci/cd", "ci cd", "github actions", "gitlab ci", "pipeline", "jenkins"], "why": "Automates testing, linting, Docker image builds, and continuous deployment."},
    "AWS": {"aliases": ["aws", "ec2", "s3", "lambda", "cloudwatch", "iam", "ecs", "eks"], "why": "Cloud infrastructure hosting for compute, storage, serverless functions, and security."},
    "Terraform": {"aliases": ["terraform", "iac", "infrastructure as code"], "why": "Declarative version-controlled cloud infrastructure provisioning."},
    "Linux": {"aliases": ["linux", "bash", "shell scripting", "systemd", "terminal"], "why": "Standard OS environment for deploying, configuring, and debugging production servers."},
    "Git": {"aliases": ["git", "github", "gitlab", "branching", "merge conflict", "pull request"], "why": "Distributed version control, collaborative workflows, and release branching."},

    # IoT & Embedded Systems
    "MQTT": {"aliases": ["mqtt", "mosquitto", "paho-mqtt", "pub/sub", "telemetry protocol", "iot broker"], "why": "Lightweight pub/sub protocol standard for constrained IoT sensor networks and edge nodes."},
    "FreeRTOS": {"aliases": ["freertos", "rtos", "real time operating system", "task scheduling"], "why": "Deterministic preemptive multitasking and hardware resource scheduling on microcontrollers."},
    "Embedded C": {"aliases": ["embedded c", "c/c++", "firmware", "microcontroller", "esp32", "arm cortex", "stm32"], "why": "Direct register-level memory access, low-latency device control, and bare-metal programming."},
    "Edge Computing": {"aliases": ["edge computing", "edge ai", "tinyml", "local processing", "sensor filtering", "i2c", "spi"], "why": "Processes sensor telemetry locally on edge hardware to conserve cloud bandwidth and latency."},
    "Sensors & Actuators": {"aliases": ["sensor", "sensors", "actuator", "gpio", "adc", "uart", "can bus"], "why": "Physical sensor data acquisition and hardware peripheral communications."},

    # Machine Learning & AI
    "PyTorch": {"aliases": ["pytorch", "torch", "deep learning", "neural network", "transformers"], "why": "Industry-standard framework for building, training, and deploying deep learning models."},
    "Pandas": {"aliases": ["pandas", "numpy", "dataframe", "data manipulation", "vectorization"], "why": "High-performance data manipulation, cleaning, and statistical feature engineering."},
    "LLM APIs": {"aliases": ["llm", "gemini", "openai", "prompt engineering", "langchain", "rag", "embeddings"], "why": "Integrates generative AI, grounded retrieval, structured JSON output, and prompt pipelines."},
    "MLOps": {"aliases": ["mlops", "model registry", "mlflow", "wandb", "model monitoring", "onnx"], "why": "Manages the lifecycle, versioning, deployment, and monitoring of ML models in production."},
    "Scikit-Learn": {"aliases": ["scikit-learn", "sklearn", "random forest", "svm", "classification", "clustering"], "why": "Classical machine learning algorithms for tabular classification, regression, and clustering."},

    # Frontend & Fullstack
    "React": {"aliases": ["react", "react.js", "reactjs", "jsx", "hooks", "state management"], "why": "Component-driven user interface architecture with reactive state updates."},
    "TypeScript": {"aliases": ["typescript", "ts", "type system", "interfaces"], "why": "Static type checking for JavaScript applications to eliminate runtime type errors."},
    "Tailwind CSS": {"aliases": ["tailwind", "tailwindcss", "utility css"], "why": "Utility-first modern styling for responsive, accessible web applications."},
    "Next.js": {"aliases": ["next.js", "nextjs", "ssr", "server components"], "why": "Fullstack React framework with server-side rendering and API routes."},
}


# ============================================================================
# 1. Gemini Client & Model Management
# ============================================================================
def _get_configured_model(custom_model_name: str | None = None) -> genai.GenerativeModel | None:
    """Initialize and configure Gemini GenerativeModel with fallback handling."""
    api_key = settings.gemini_api_key
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model_name = custom_model_name or settings.gemini_model
        return genai.GenerativeModel(model_name)
    except Exception as exc:
        logger.warning("Failed to configure Gemini model %s: %s", custom_model_name, exc)
        return None


def _call_gemini_with_fallback(prompt: str, json_mode: bool = False) -> str | None:
    """Attempt generation with primary model, then automatically try fallback models."""
    if not settings.gemini_api_key:
        return None

    models_to_try = [settings.gemini_model] + settings.fallback_model_list
    seen = set()

    for model_name in models_to_try:
        if not model_name or model_name in seen:
            continue
        seen.add(model_name)

        try:
            model = _get_configured_model(model_name)
            if not model:
                continue

            config = genai.GenerationConfig(response_mime_type="application/json") if json_mode else None
            response = model.generate_content(prompt, generation_config=config)
            text = (response.text or "").strip()
            if text:
                return text
        except Exception as exc:
            logger.debug("Gemini model %s failed: %s. Trying next fallback.", model_name, exc)
            continue

    return None


def _extract_json_payload(raw_text: str) -> Any:
    """Safely extract JSON object or array from markdown-fenced or raw response."""
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # Try finding outermost braces/brackets
        brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except Exception:
                pass
    return None


# ============================================================================
# 2. Dynamic Skill Extraction (AI + NLP Heuristics)
# ============================================================================
def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9+#./ -]+", " ", text.lower())


def _contains_alias(text: str, alias: str) -> bool:
    escaped = re.escape(alias.lower())
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None


def extract_skills_heuristic(text: str) -> list[str]:
    """Scan text against dynamic domain catalog to identify present skills."""
    normalized = _normalize_text(text)
    found = []
    for skill, meta in DOMAIN_CATALOG.items():
        for alias in meta["aliases"]:
            if _contains_alias(normalized, alias):
                found.append(skill)
                break
    return found


def parse_resume_skills(resume_text: str) -> list[str]:
    """Dynamically parse technical skills from resume text using AI with NLP heuristic fallback."""
    sanitized_text = InputSanitizer.sanitize_text(resume_text, max_chars=settings.max_text_chars)
    if not sanitized_text:
        return []

    prompt = f"""You are a technical recruiter AI. Extract all concrete software engineering, cloud, data, and IoT skills mentioned in this resume.
Return JSON: {{"skills": ["Skill1", "Skill2", ...]}}

Resume:
{InputSanitizer.wrap_prompt_content(sanitized_text, 'RESUME')}
"""
    raw_response = _call_gemini_with_fallback(prompt, json_mode=True)
    if raw_response:
        payload = _extract_json_payload(raw_response)
        if isinstance(payload, dict) and "skills" in payload and isinstance(payload["skills"], list):
            skills = [str(s).strip() for s in payload["skills"] if s and len(str(s).strip()) < 50]
            if skills:
                return list(dict.fromkeys(skills))[:20]
        elif isinstance(payload, list):
            skills = [str(s).strip() for s in payload if s and len(str(s).strip()) < 50]
            if skills:
                return list(dict.fromkeys(skills))[:20]

    return extract_skills_heuristic(sanitized_text)


# ============================================================================
# 3. Dynamic Skill Gap Intelligence & Market Delta Research
# ============================================================================
def _synthesize_local_skill_gaps(resume_text: str, job_descriptions: list[str], target_role: str = "") -> list[dict]:
    """Synthesize ranked skill gaps by comparing candidate skills with job market demand."""
    resume_skills = set(extract_skills_heuristic(resume_text))
    job_skill_counts: Counter[str] = Counter()
    skill_companies: dict[str, set[str]] = {}

    for desc in job_descriptions:
        desc_skills = extract_skills_heuristic(desc)
        company_match = re.search(r"\bat\s+([^\n,:]+)", desc, re.IGNORECASE)
        company = company_match.group(1).strip()[:60] if company_match else "live market postings"
        for s in desc_skills:
            job_skill_counts[s] += 1
            skill_companies.setdefault(s, set()).add(company)

    role_lower = (target_role or "").lower()

    # Seed baseline market demand if no job descriptions provided
    if not job_skill_counts:
        if any(k in role_lower for k in ["iot", "embedded", "firmware", "hardware"]):
            job_skill_counts.update({"MQTT": 4, "FreeRTOS": 3, "Embedded C": 3, "Edge Computing": 2, "Linux": 2})
        elif any(k in role_lower for k in ["ml", "ai", "machine learning", "data"]):
            job_skill_counts.update({"PyTorch": 4, "Pandas": 3, "LLM APIs": 3, "SQL": 2, "MLOps": 2})
        elif any(k in role_lower for k in ["devops", "cloud", "sre", "platform"]):
            job_skill_counts.update({"Docker": 4, "Kubernetes": 4, "CI/CD": 3, "Terraform": 3, "AWS": 2})
        elif any(k in role_lower for k in ["frontend", "ui", "web", "react"]):
            job_skill_counts.update({"React": 4, "TypeScript": 3, "REST APIs": 3, "Testing": 2, "Tailwind CSS": 2})
        else:
            job_skill_counts.update({"FastAPI": 4, "Docker": 3, "SQL": 3, "REST APIs": 2, "Testing": 2, "Input Validation": 2})

    ranked_gaps = []
    for skill, demand in job_skill_counts.most_common():
        if skill in resume_skills:
            continue
        meta = DOMAIN_CATALOG.get(skill, {"why": "High-demand production engineering standard."})
        companies = sorted(skill_companies.get(skill, []))
        source = ", ".join(companies[:2]) if companies else f"top postings for {target_role or 'this role'}"
        reason = f"{skill} is required across {source}, but is not demonstrated on the resume. {meta['why']}"
        ranked_gaps.append({
            "skill": skill,
            "reason": reason[:500],
            "demand_count": demand,
        })

    # Guarantee at least 3 high-impact gaps
    if len(ranked_gaps) < 3:
        existing = {g["skill"] for g in ranked_gaps}
        default_pool = (
            ["MQTT", "FreeRTOS", "Embedded C", "Edge Computing"] if any(k in role_lower for k in ["iot", "embedded"])
            else ["PyTorch", "Pandas", "LLM APIs", "MLOps"] if any(k in role_lower for k in ["ml", "ai", "data"])
            else ["Docker", "Kubernetes", "CI/CD", "AWS"] if any(k in role_lower for k in ["devops", "cloud"])
            else ["Docker", "REST APIs", "FastAPI", "SQL", "Testing", "Input Validation"]
        )
        for s in default_pool:
            if s not in existing and s not in resume_skills:
                meta = DOMAIN_CATALOG.get(s, {"why": "Core competency for modern production development."})
                ranked_gaps.append({
                    "skill": s,
                    "reason": f"Essential competency for {target_role or 'software engineering'}. {meta['why']}",
                    "demand_count": 2,
                })
                existing.add(s)
            if len(ranked_gaps) >= 4:
                break

    return ranked_gaps[:3]


def analyze_skill_gaps(resume_text: str, job_descriptions: list[str], target_role: str = "") -> list[dict]:
    """Research and return top missing skills ranked by industry importance."""
    safe_resume = InputSanitizer.sanitize_text(resume_text, max_chars=settings.max_text_chars)
    safe_jobs = [InputSanitizer.sanitize_text(j, max_chars=settings.max_text_chars) for j in job_descriptions[:settings.max_job_descriptions]]
    local_gaps = _synthesize_local_skill_gaps(safe_resume, safe_jobs, target_role=target_role)

    jobs_summary = "\n---\n".join(safe_jobs) if safe_jobs else "(No job descriptions provided - research based on role)"
    prompt = f"""You are SkillBridge AI, a technical talent intelligence agent.
Compare this candidate's resume/syllabus against the target job postings and identify the TOP 3 technical skill gaps.

Target Role: {target_role or 'Software Engineer'}

Rules:
1. Identify skills demanded by the target jobs that are NOT present in the candidate resume.
2. For each gap, write a concise reason (1-2 sentences) citing market demand and why it matters.
3. Return ONLY a JSON array with structure:
[
  {{"skill": "Skill Name", "reason": "Why this is in demand and missing", "demand_count": 3}},
  ...
]

Resume:
{InputSanitizer.wrap_prompt_content(safe_resume, 'RESUME')}

Target Jobs:
{InputSanitizer.wrap_prompt_content(jobs_summary, 'JOBS')}
"""
    raw = _call_gemini_with_fallback(prompt, json_mode=True)
    if raw:
        payload = _extract_json_payload(raw)
        if isinstance(payload, dict) and "gaps" in payload:
            payload = payload["gaps"]
        if isinstance(payload, list) and len(payload) >= 3:
            cleaned = []
            seen = set()
            for item in payload:
                if isinstance(item, dict) and "skill" in item:
                    skill = str(item["skill"]).strip()
                    reason = str(item.get("reason", "")).strip()
                    demand = int(item.get("demand_count") or item.get("demand_pct") or 2)
                    if skill and skill.lower() not in seen:
                        seen.add(skill.lower())
                        cleaned.append({
                            "skill": skill[:100],
                            "reason": (reason or f"{skill} is in high demand for {target_role}.")[:500],
                            "demand_count": max(1, demand),
                        })
            if len(cleaned) >= 3:
                return cleaned[:3]

    return local_gaps



# ============================================================================
# 4. Dynamic Learning Path Generator
# ============================================================================
def generate_learning_path(gaps: list[dict]) -> list[dict]:
    """Order ranked gaps into a coherent pedagogical study sequence with estimated minutes."""
    local_path = []
    for index, gap in enumerate(gaps, start=1):
        skill = gap.get("skill") or f"Skill {index}"
        local_path.append({
            "order": index,
            "skill": skill,
            "minutes": 20 + index * 10,
            "why": gap.get("reason") or "Complete this micro-sprint to close your market skill delta.",
        })

    prompt = f"""Order these technical skill gaps into a beginner-friendly learning sprint sequence.
Return JSON: {{"items": [{{"order": 1, "skill": "...", "minutes": 25, "why": "one sentence rational"}}]}}

Gaps to sequence:
{json.dumps(gaps)}
"""
    raw = _call_gemini_with_fallback(prompt, json_mode=True)
    if raw:
        payload = _extract_json_payload(raw)
        items = payload.get("items") if isinstance(payload, dict) else payload
        if isinstance(items, list) and len(items) > 0:
            cleaned = []
            for index, itm in enumerate(items, start=1):
                if isinstance(itm, dict):
                    cleaned.append({
                        "order": int(itm.get("order") or index),
                        "skill": str(itm.get("skill") or f"Skill {index}")[:100],
                        "minutes": int(itm.get("minutes") or (20 + index * 10)),
                        "why": str(itm.get("why") or "")[:400],
                    })
            if cleaned:
                return cleaned

    return local_path


# ============================================================================
# 5. Dynamic Micro-Sprint & Lesson Generator
# ============================================================================
BUILTIN_LESSONS: dict[str, dict[str, str]] = {
    "Docker": {
        "theory_markdown": "**Docker** packages your backend and runtime dependencies into a self-contained container image. A production Dockerfile installs requirements before copying application source code to maximize build cache reuse. Containers must bind Uvicorn to `0.0.0.0` and declare `EXPOSE` so traffic can reach the application from outside the container.",
        "starter_code": "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"app.main:app\", \"--port\", \"8000\"]\n",
        "solution_code": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY app ./app\nEXPOSE 8000\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
    },
    "MQTT": {
        "theory_markdown": "**MQTT** is the standard publish-subscribe messaging protocol for IoT telemetry. In sensor networks, edge devices publish metrics to a broker topic (e.g. `sensors/telemetry`), while gateways subscribe to data streams. Subscriptions should always be registered inside the `on_connect` callback so topic bindings automatically recover after network disconnects.",
        "starter_code": "import paho.mqtt.client as mqtt\n\ndef on_connect(client, userdata, flags, rc):\n    print(f\"Connected: {rc}\")\n\nclient = mqtt.Client()\nclient.on_connect = on_connect\nclient.connect(\"broker.hivemq.com\", 1883, 60)\n",
        "solution_code": "import paho.mqtt.client as mqtt\n\ndef on_connect(client, userdata, flags, rc):\n    print(f\"Connected: {rc}\")\n    client.subscribe(\"sensors/telemetry\")\n\nclient = mqtt.Client(client_id=\"edge_node_01\")\nclient.on_connect = on_connect\nclient.connect(\"broker.hivemq.com\", 1883, 60)\n",
    },
    "FreeRTOS": {
        "theory_markdown": "**FreeRTOS** provides real-time deterministic task scheduling on microcontrollers. In an RTOS, background sensor loops must yield CPU execution time to the scheduler using `vTaskDelay(pdMS_TO_TICKS(ms))` rather than busy-waiting. Busy loops starve lower-priority tasks and trigger hardware watchdog resets.",
        "starter_code": "void vSensorTask(void *pvParameters) {\n    for (;;) {\n        read_sensor();\n        for (volatile int i = 0; i < 100000; i++);\n    }\n}\n",
        "solution_code": "void vSensorTask(void *pvParameters) {\n    for (;;) {\n        read_sensor();\n        vTaskDelay(pdMS_TO_TICKS(500));\n    }\n}\n",
    },
    "FastAPI": {
        "theory_markdown": "**FastAPI** delivers automatic request validation and OpenAPI documentation via Pydantic schemas. Accepting a raw dictionary bypasses type safety and validation. Replacing `payload: dict` with a Pydantic `BaseModel` and `Field` constraints prevents bad data from reaching business logic.",
        "starter_code": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.post(\"/users\")\ndef create_user(payload: dict):\n    return {\"name\": payload[\"name\"]}\n",
        "solution_code": "from fastapi import FastAPI\nfrom pydantic import BaseModel, Field\n\napp = FastAPI()\n\nclass UserCreate(BaseModel):\n    name: str = Field(min_length=1, max_length=100)\n\n@app.post(\"/users\")\ndef create_user(payload: UserCreate):\n    return {\"name\": payload.name}\n",
    },
    "SQLAlchemy": {
        "theory_markdown": "**SQLAlchemy** manages relational database ORM models and unit-of-work sessions in Python. In request lifecycles, modified entities must be persisted using `db.commit()` and refreshed with `db.refresh(instance)` to populate auto-generated database IDs and timestamps.",
        "starter_code": "def create_user(db, name: str):\n    user = User(name=name)\n    db.add(user)\n    return user\n",
        "solution_code": "def create_user(db, name: str):\n    user = User(name=name)\n    db.add(user)\n    db.commit()\n    db.refresh(user)\n    return user\n",
    },
    "CI/CD": {
        "theory_markdown": "**CI/CD Pipelines** automate building, testing, and deploying backend applications. A deployment stage must explicitly declare dependencies (`needs: [test_job]`) on the test suite; otherwise, the deploy job may execute concurrently or release broken code if tests fail.",
        "starter_code": "stages:\n  - test\n  - deploy\n\ndeploy_job:\n  stage: deploy\n  script:\n    - ./deploy.sh\n\ntest_job:\n  stage: test\n  script:\n    - pytest\n",
        "solution_code": "stages:\n  - test\n  - deploy\n\ntest_job:\n  stage: test\n  script:\n    - pytest\n\ndeploy_job:\n  stage: deploy\n  needs: [test_job]\n  script:\n    - ./deploy.sh\n",
    },
}

LESSON_LIBRARY = BUILTIN_LESSONS


def generate_lesson(skill: str, gap_reason: str = "") -> dict:
    """Generate a tailored micro-lesson sprint with theory, broken starter code, and reference solution."""
    safe_skill = InputSanitizer.sanitize_text(skill, max_chars=100) or "Software Engineering Practice"

    # Match built-in catalog if exact or fuzzy match
    for k, lesson in BUILTIN_LESSONS.items():
        if k.lower() in safe_skill.lower() or safe_skill.lower() in k.lower():
            return dict(lesson)

    prompt = f"""You are SkillBridge AI's Generator Sprint Agent (GSA).
Create an interactive 10-minute micro-sprint for this technical skill: "{safe_skill}".
Context: {gap_reason}

Return JSON with EXACTLY these keys:
- "theory_markdown": 3-5 concise bullet points or sentences in markdown explaining the core production concept.
- "starter_code": 8-20 lines of realistic code with an intentional subtle bug or missing production pattern for the student to fix.
- "solution_code": the corrected version that fixes the bug.

Rules:
- Make the exercise concrete and editable in an interactive code editor.
- Language should match the skill (Python/FastAPI for backend, YAML for CI/CD, C for Embedded, etc.).
"""
    raw = _call_gemini_with_fallback(prompt, json_mode=True)
    if raw:
        payload = _extract_json_payload(raw)
        if isinstance(payload, dict) and "starter_code" in payload and "solution_code" in payload:
            return {
                "theory_markdown": str(payload.get("theory_markdown") or f"**{safe_skill}** core concepts and production patterns.").strip(),
                "starter_code": str(payload.get("starter_code", "")).strip() + "\n",
                "solution_code": str(payload.get("solution_code", "")).strip() + "\n",
            }

    # Dynamic fallback generator
    return {
        "theory_markdown": f"**{safe_skill}** is a critical engineering competency. Focus on proper parameter validation, error handling, and production protocols to build resilient systems.",
        "starter_code": f"# Fix the {safe_skill} implementation\ndef solve():\n    # TODO: implement missing logic\n    pass\n",
        "solution_code": f"# Correct {safe_skill} implementation\ndef solve():\n    return True\n",
    }


# ============================================================================
# 6. Dynamic 0-100 Rubric Code Evaluation Agent (AEA)
# ============================================================================
def _code_similarity(left: str, right: str) -> float:
    l_clean = re.sub(r"\s+", "", left.lower())
    r_clean = re.sub(r"\s+", "", right.lower())
    return SequenceMatcher(None, l_clean, r_clean).ratio()


def _local_rubric_evaluate(submitted: str, solution: str, concept: str = "") -> dict:
    """Deterministic AST-like heuristic evaluation engine."""
    similarity = _code_similarity(submitted, solution)
    submitted_lower = submitted.lower()
    concept_lower = (concept or "").lower()

    # Rule dictionary for key skills
    KEY_PATTERNS = {
        "docker": {
            "required": ["0.0.0.0", "expose", "8000"],
            "hint": "Ensure Uvicorn binds to --host 0.0.0.0 and port 8000 is exposed in the Dockerfile.",
        },
        "mqtt": {
            "required": ["subscribe", "on_connect"],
            "hint": "Subscribe to the topic inside the on_connect callback so reconnects recover subscriptions.",
        },
        "freertos": {
            "required": ["vtaskdelay", "pdms_to_ticks"],
            "hint": "Replace busy-waiting with vTaskDelay(pdMS_TO_TICKS(500)) to yield CPU time to the scheduler.",
        },
        "fastapi": {
            "required": ["basemodel", "field"],
            "hint": "Use a Pydantic BaseModel with Field() validation instead of a raw dictionary.",
        },
        "sqlalchemy": {
            "required": ["commit", "refresh"],
            "hint": "Call db.commit() to persist changes and db.refresh() to load auto-generated fields.",
        },
        "ci/cd": {
            "required": ["needs", "test_job"],
            "hint": "Add 'needs: [test_job]' to deploy_job so it never runs before tests pass.",
        },
    }

    # Check pattern matches
    for k, pat in KEY_PATTERNS.items():
        if k in concept_lower or k in solution.lower():
            missing = [r for r in pat["required"] if r not in submitted_lower]
            if missing:
                return {
                    "passed": False,
                    "hint": pat["hint"],
                    "score": max(15, round(similarity * 70)),
                    "rubric": {"correctness": 2, "code_quality": 3, "concept_match": 2},
                }

    if similarity > 0.88:
        return {
            "passed": True,
            "hint": "Excellent! Your implementation satisfies all required production criteria.",
            "score": min(100, round(similarity * 100)),
            "rubric": {"correctness": 5, "code_quality": 5, "concept_match": 5},
        }

    if similarity > 0.65:
        return {
            "passed": True,
            "hint": "Good job! The core concept is correctly addressed.",
            "score": round(similarity * 95),
            "rubric": {"correctness": 4, "code_quality": 4, "concept_match": 4},
        }

    return {
        "passed": False,
        "hint": "Check the control flow and required keywords against the reference pattern.",
        "score": max(10, round(similarity * 75)),
        "rubric": {"correctness": 2, "code_quality": 3, "concept_match": 2},
    }


def check_code(submitted_code: str, solution_code: str, concept: str = "") -> dict:
    """Evaluate submitted code safely via AI rubric scoring without code execution."""
    safe_submitted = InputSanitizer.sanitize_text(submitted_code, max_chars=settings.max_code_chars, strip_html=False)
    safe_solution = InputSanitizer.sanitize_text(solution_code, max_chars=settings.max_code_chars, strip_html=False)
    local_eval = _local_rubric_evaluate(safe_submitted, safe_solution, concept=concept)

    prompt = f"""You are SkillBridge AI's Adaptive Evaluator Agent (AEA).
Evaluate the student's submitted code against the reference solution for the skill/concept: "{concept}".

DO NOT execute the code. Grade with a structured rubric.

Reference Solution:
```
{safe_solution}
```

Student Submission:
```
{safe_submitted}
```

Return JSON:
- "passed": boolean (true if the core bug is fixed and concept is applied, false otherwise)
- "hint": one specific, actionable pedagogical hint without revealing the entire answer
- "score": integer 0-100 overall score
- "rubric": object with integer 1-5 ratings for "correctness", "code_quality", and "concept_match"
"""
    raw = _call_gemini_with_fallback(prompt, json_mode=True)
    if raw:
        payload = _extract_json_payload(raw)
        if isinstance(payload, dict) and "passed" in payload and "hint" in payload:
            rubric = payload.get("rubric") if isinstance(payload.get("rubric"), dict) else {}
            return {
                "passed": bool(payload.get("passed")),
                "hint": str(payload.get("hint", ""))[:500],
                "score": float(payload.get("score") or local_eval["score"]),
                "rubric": {
                    "correctness": int(rubric.get("correctness") or 3),
                    "code_quality": int(rubric.get("code_quality") or 3),
                    "concept_match": int(rubric.get("concept_match") or 3),
                },
            }

    return local_eval


# ============================================================================
# 7. Grounded Gap Q&A Tutor Agent
# ============================================================================
def answer_gap_question(skill: str, question: str, theory: str, job_context: str, history: list[dict]) -> str:
    """Generate tutor response grounded strictly in the lesson theory and job market context."""
    safe_question = InputSanitizer.sanitize_text(question, max_chars=2000)
    safe_theory = InputSanitizer.sanitize_text(theory, max_chars=3000)
    safe_jobs = InputSanitizer.sanitize_text(job_context, max_chars=3000)

    chat_transcript = "\n".join(
        f"{m.get('role', 'user')}: {InputSanitizer.sanitize_text(m.get('content', ''))}"
        for m in history[-6:]
    )

    fallback_answer = (
        f"{skill}: {safe_theory[:300]}...\n\n"
        "In production engineering, mastering this concept prevents common runtime regressions. "
        "Try applying the pattern in the ticket workspace to test your understanding."
    )

    prompt = f"""You are SkillBridge AI's technical tutor agent.
Answer the student's question about "{skill}" in 3 to 6 sentences.

Ground your answer in the lesson theory and job postings context below.
Do NOT give away the exact code solution to the practice exercise.

Lesson Context:
{safe_theory}

Job Market Context:
{safe_jobs}

Recent Chat:
{chat_transcript}

Student Question:
{safe_question}
"""
    raw = _call_gemini_with_fallback(prompt, json_mode=False)
    if raw and len(raw.strip()) > 10:
        return raw.strip()[:2500]

    return fallback_answer


# ============================================================================
# 8. Comprehensive Candidate AI Resume Analysis
# ============================================================================
def _heuristic_candidate_analysis(resume_text: str, target_position: str = "") -> dict:
    """Intelligent local heuristic analyzer for candidate resumes."""
    tech_skills = extract_skills_heuristic(resume_text)
    if not tech_skills:
        tech_skills = ["Software Engineering", "Problem Solving", "Git"]

    # Soft skills heuristics
    soft_keywords = {
        "Leadership": ["lead", "managed", "mentor", "coordinated", "supervised"],
        "Communication": ["presentation", "written", "verbal", "collaborated", "stakeholders"],
        "Problem Solving": ["optimized", "debugged", "architected", "troubleshot", "designed"],
        "Agile Methodology": ["scrum", "agile", "sprint", "kanban", "jira"],
        "Cross-functional Collaboration": ["team", "product", "designers", "cross-functional"],
    }
    soft_skills = []
    text_lower = resume_text.lower()
    for skill_name, kws in soft_keywords.items():
        if any(kw in text_lower for kw in kws):
            soft_skills.append(skill_name)
    if not soft_skills:
        soft_skills = ["Problem Solving", "Collaboration", "Critical Thinking"]

    # Experience years detection
    exp_years = 1.0
    exp_matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\b", text_lower)
    if exp_matches:
        try:
            exp_years = float(exp_matches[0])
        except ValueError:
            exp_years = 2.0
    else:
        # Date range detection like 2021 - 2024
        years = [int(y) for y in re.findall(r"\b(20[12]\d)\b", text_lower)]
        if len(years) >= 2:
            exp_years = float(max(1, max(years) - min(years)))

    # Education extraction
    education = []
    for line in resume_text.splitlines():
        line_clean = line.strip()
        if any(kw in line_clean.lower() for kw in ["bachelor", "master", "b.tech", "b.s.", "m.s.", "degree", "university", "college", "institute", "gpa", "b.e."]):
            if len(line_clean) < 120 and line_clean not in education:
                education.append(line_clean)
    if not education:
        education = ["Bachelor of Science in Computer Science or related engineering discipline"]

    # Certifications extraction
    certifications = []
    for line in resume_text.splitlines():
        line_clean = line.strip()
        if any(kw in line_clean.lower() for kw in ["certified", "certification", "aws certified", "comptia", "gcp professional", "coursera", "udemy"]):
            if len(line_clean) < 120 and line_clean not in certifications:
                certifications.append(line_clean)

    # Missing and recommended skills based on target role
    position = target_position or "Software Engineer"
    gaps = _synthesize_local_skill_gaps(resume_text, [], target_role=position)
    missing_skills = [g["skill"] for g in gaps]
    recommended_skills = [g["skill"] for g in gaps[:3]] or ["Docker", "FastAPI", "SQL"]

    # Recommended roles
    all_skills_str = " ".join(tech_skills).lower()
    if any(k in all_skills_str for k in ["mqtt", "freertos", "embedded"]):
        recommended_roles = ["Embedded Systems Engineer", "IoT Firmware Developer", "Edge AI Specialist"]
    elif any(k in all_skills_str for k in ["pytorch", "pandas", "llm"]):
        recommended_roles = ["AI/ML Engineer", "Machine Learning Developer", "Data Scientist"]
    elif any(k in all_skills_str for k in ["docker", "kubernetes", "terraform"]):
        recommended_roles = ["DevOps Engineer", "Cloud Infrastructure Engineer", "Platform Engineer"]
    else:
        recommended_roles = ["Backend Developer", "Python API Engineer", "Full Stack Developer"]

    # Strengths
    strengths = [
        f"Demonstrated hands-on proficiency with {', '.join(tech_skills[:3])}",
        f"Solid foundation in software design and practical implementation ({exp_years:.1f}+ years estimated experience)",
        f"Clear exposure to modern development workflows and collaborative engineering",
    ]

    # Areas for improvement
    areas_for_improvement = [
        f"Close competency gaps in high-demand production standards: {', '.join(missing_skills[:2]) if missing_skills else 'Containerization & CI/CD'}",
        "Deepen system architecture experience with live database scaling and integration test coverage",
    ]

    # Scores (0-100)
    skill_count = len(tech_skills)
    resume_score = min(96, max(68, 70 + skill_count * 3 + int(exp_years * 2)))
    candidate_score = min(98, max(70, 72 + skill_count * 3 + len(soft_skills) * 2))

    # Interview questions
    interview_questions = [
        f"Can you explain your experience architecting applications using {tech_skills[0] if tech_skills else 'your primary stack'}?",
        f"How would you integrate {missing_skills[0] if missing_skills else 'Docker containers'} into your daily CI/CD release pipeline?",
        "Describe a challenging production bug you encountered and the exact debugging steps you took to isolate and resolve it.",
        "How do you approach database schema migrations and data consistency in a high-concurrency environment?",
    ]

    # Key observations
    key_observations = [
        f"Candidate possesses verified core technical competencies in {', '.join(tech_skills[:4])}.",
        f"Target role alignment for '{position}' is strong with clear actionable micro-sprints identified.",
        "Well-structured resume with identifiable project milestones and engineering depth.",
    ]

    summary = (
        f"Candidate with approximately {exp_years:.1f} years of technical experience in {position or 'Software Engineering'}. "
        f"Proficient in {', '.join(tech_skills[:4])}. Demonstrates solid engineering fundamentals with targeted growth "
        f"opportunities in {', '.join(missing_skills[:2]) if missing_skills else 'production infrastructure'}."
    )

    return {
        "summary": summary,
        "current_position": position,
        "skills": list(dict.fromkeys(tech_skills + soft_skills)),
        "technical_skills": tech_skills,
        "soft_skills": soft_skills,
        "experience_years": round(exp_years, 1),
        "education": education,
        "certifications": certifications,
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "missing_skills": missing_skills,
        "recommended_skills": recommended_skills,
        "recommended_roles": recommended_roles,
        "resume_score": resume_score,
        "candidate_score": candidate_score,
        "interview_questions": interview_questions,
        "key_observations": key_observations,
    }


def analyze_candidate_resume(resume_text: str, target_position: str = "") -> dict:
    """Analyze a candidate's resume using Gemini structured JSON with rich heuristic fallback."""
    safe_text = InputSanitizer.sanitize_text(resume_text, max_chars=settings.max_text_chars)
    fallback = _heuristic_candidate_analysis(safe_text, target_position=target_position)

    if not safe_text:
        return fallback

    prompt = f"""You are SkillBridge AI's expert Senior Technical Recruiter & Engineering Evaluator.
Analyze this candidate's resume/CV in detail and generate structured evaluation insights.

Target Position: {target_position or 'Software Engineer'}

Return ONLY a JSON object with EXACTLY these keys:
{{
  "summary": "3-4 sentence comprehensive executive candidate summary",
  "current_position": "Detected or target position title",
  "skills": ["Skill1", "Skill2", ...],
  "technical_skills": ["TechSkill1", "TechSkill2", ...],
  "soft_skills": ["SoftSkill1", "SoftSkill2", ...],
  "experience_years": 2.5,
  "education": ["Degree/Institution entries"],
  "certifications": ["Certification names or empty array"],
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "areas_for_improvement": ["Area 1", "Area 2"],
  "missing_skills": ["MissingSkill1", "MissingSkill2", ...],
  "recommended_skills": ["Skill to learn 1", "Skill to learn 2", ...],
  "recommended_roles": ["Role 1", "Role 2", "Role 3"],
  "resume_score": 85,
  "candidate_score": 88,
  "interview_questions": [
    "Specific technical question based on their stack",
    "Specific architecture question",
    "Behavioral question tailored to their background",
    "Scenario-based problem-solving question"
  ],
  "key_observations": [
    "Observation 1",
    "Observation 2",
    "Observation 3"
  ]
}}

Resume:
{InputSanitizer.wrap_prompt_content(safe_text, 'RESUME')}
"""
    raw = _call_gemini_with_fallback(prompt, json_mode=True)
    if raw:
        payload = _extract_json_payload(raw)
        if isinstance(payload, dict) and "summary" in payload:
            # Validate and merge with fallback defaults
            return {
                "summary": str(payload.get("summary") or fallback["summary"]).strip(),
                "current_position": str(payload.get("current_position") or target_position or fallback["current_position"]).strip(),
                "skills": list(payload.get("skills") or fallback["skills"]),
                "technical_skills": list(payload.get("technical_skills") or fallback["technical_skills"]),
                "soft_skills": list(payload.get("soft_skills") or fallback["soft_skills"]),
                "experience_years": float(payload.get("experience_years") or fallback["experience_years"]),
                "education": list(payload.get("education") or fallback["education"]),
                "certifications": list(payload.get("certifications") or fallback["certifications"]),
                "strengths": list(payload.get("strengths") or fallback["strengths"]),
                "areas_for_improvement": list(payload.get("areas_for_improvement") or fallback["areas_for_improvement"]),
                "missing_skills": list(payload.get("missing_skills") or fallback["missing_skills"]),
                "recommended_skills": list(payload.get("recommended_skills") or fallback["recommended_skills"]),
                "recommended_roles": list(payload.get("recommended_roles") or fallback["recommended_roles"]),
                "resume_score": int(payload.get("resume_score") or fallback["resume_score"]),
                "candidate_score": int(payload.get("candidate_score") or fallback["candidate_score"]),
                "interview_questions": list(payload.get("interview_questions") or fallback["interview_questions"]),
                "key_observations": list(payload.get("key_observations") or fallback["key_observations"]),
            }

    return fallback

