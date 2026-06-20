"""
Practice Mode Router
────────────────────
API endpoints for the real-time practice mode with live metrics dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.security import get_current_user
from app.services.practice_mode_service import practice_mode_service

router = APIRouter(prefix="/api/practice", tags=["practice"])


# ── Request Models ────────────────────────────────

class StartPracticeRequest(BaseModel):
    topic: str = "behavioral"
    difficulty: str = "medium"


class SubmitAnswerRequest(BaseModel):
    answer_text: str


class UpdateMetricsRequest(BaseModel):
    partial_text: str = ""
    # video_frame and audio_chunk would be sent via WebSocket in production


# ── Endpoints ─────────────────────────────────────

@router.get("/topics")
async def get_practice_topics():
    """Get available practice topics."""
    return practice_mode_service.get_available_topics()


@router.post("/start")
async def start_practice(
    request: StartPracticeRequest,
    user: dict = Depends(get_current_user),
):
    """Start a new practice session."""
    result = practice_mode_service.start_practice_session(
        user_id=str(user["_id"]),
        topic=request.topic,
        difficulty=request.difficulty,
    )
    return result


@router.get("/{session_id}/question")
async def get_current_question(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Get the current practice question."""
    question = practice_mode_service.get_current_question(session_id)
    if not question:
        raise HTTPException(status_code=404, detail="No more questions or session not found")
    return question


@router.post("/{session_id}/metrics")
async def update_metrics(
    session_id: str,
    request: UpdateMetricsRequest,
    user: dict = Depends(get_current_user),
):
    """Update live metrics during practice (called frequently)."""
    result = practice_mode_service.update_live_metrics(
        session_id=session_id,
        partial_text=request.partial_text,
    )
    return result


@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    user: dict = Depends(get_current_user),
):
    """Submit an answer and get evaluation + next question."""
    result = await practice_mode_service.submit_answer(
        session_id=session_id,
        answer_text=request.answer_text,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{session_id}/end")
async def end_practice(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """End the practice session and get comprehensive summary."""
    result = await practice_mode_service.end_practice_session(session_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/{session_id}/status")
async def get_session_status(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Get current session metrics for the dashboard."""
    result = practice_mode_service.get_session_metrics(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.get("/history/me")
async def get_practice_history(
    user: dict = Depends(get_current_user),
):
    """Get practice session history for the current user."""
    return practice_mode_service.get_practice_history(str(user["_id"]))
