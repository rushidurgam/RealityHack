"""POST /api/gap-chat — interactive grounded Q&A tutor for a specific skill gap."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import cached_lesson, get_chat_for_gap, persist_chat
from app.database import get_db
from app.models import JobPosting, SkillGap
from app.schemas import ChatRequest, ChatResponse
from app.services.agents import gap_chat_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/gap-chat", response_model=ChatResponse)
def ask_about_gap(payload: ChatRequest, db: Session = Depends(get_db)):
    """Answer a user question grounded in the selected skill gap, lesson theory, and job context."""
    gap = db.get(SkillGap, payload.skill_gap_id)
    if gap is None:
        raise HTTPException(status_code=404, detail="Skill gap not found")

    # Persist student question
    persist_chat(db=db, skill_gap_id=gap.id, role="user", content=payload.message)

    # Gather grounding context
    lesson = cached_lesson(db=db, skill_gap_id=gap.id)
    theory = lesson.theory_markdown if lesson else f"Focus area: {gap.skill_name}. {gap.reason}"

    # Get job context from user's jobs if available
    job_context = ""
    if gap.resume_id:
        job_rows = db.query(JobPosting).filter(JobPosting.resume_id == gap.resume_id).limit(3).all()
        job_context = "\n".join(f"{j.title} at {j.company}: {j.description[:200]}" for j in job_rows)

    chat_history_rows = get_chat_for_gap(db=db, skill_gap_id=gap.id)
    chat_history = [{"role": msg.role, "content": msg.content} for msg in chat_history_rows]

    # Generate grounded response
    answer_text = gap_chat_agent(
        skill=gap.skill_name,
        question=payload.message,
        theory=theory,
        job_context=job_context or gap.reason,
        history=chat_history,
    )

    # Persist assistant reply
    assistant_msg = persist_chat(db=db, skill_gap_id=gap.id, role="assistant", content=answer_text)

    return ChatResponse(
        id=assistant_msg.id,
        role="assistant",
        content=assistant_msg.content,
        created_at=assistant_msg.created_at.isoformat() if assistant_msg.created_at else None,
    )
