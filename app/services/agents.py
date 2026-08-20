"""SkillBridge AI - Service Layer Agent Orchestration.

Provides high-level agent interfaces:
- extract_resume_skills
- analyze_skill_gaps_agent
- generate_lesson_agent
- evaluate_practice_attempt_agent
- generate_learning_path_agent
- gap_chat_agent
"""

from __future__ import annotations

import logging
from app.services.gemini import (
    analyze_skill_gaps,
    answer_gap_question,
    check_code,
    generate_learning_path,
    generate_lesson,
    parse_resume_skills,
)

logger = logging.getLogger("skillbridge.agents")


def extract_resume_skills(resume_text: str) -> list[str]:
    """Extract candidate skills from resume/syllabus text."""
    return parse_resume_skills(resume_text)


def analyze_skill_gaps_agent(resume_text: str, job_descriptions: list[str], target_role: str = "") -> list[dict]:
    """Agent finding top ranked missing skills compared against target jobs."""
    return analyze_skill_gaps(resume_text, job_descriptions, target_role=target_role)


def generate_lesson_agent(skill: str, gap_reason: str = "", job_context: str = "") -> dict:
    """Agent building micro-lesson theory, starter code, and solution."""
    return generate_lesson(skill, gap_reason=gap_reason)


def evaluate_practice_attempt_agent(
    submitted_code: str, solution_code: str, concept: str = ""
) -> dict:
    """Agent evaluating practice code with 0-100 rubric score and actionable hint."""
    return check_code(submitted_code, solution_code, concept=concept)


def generate_learning_path_agent(gaps: list[dict]) -> list[dict]:
    """Generate ordered study progression with time estimates."""
    return generate_learning_path(gaps)


def gap_chat_agent(
    skill: str, question: str, theory: str, job_context: str, history: list[dict]
) -> str:
    """Interactive grounded gap tutor agent."""
    return answer_gap_question(
        skill=skill,
        question=question,
        theory=theory,
        job_context=job_context,
        history=history,
    )
