"""
GPU Server Admin Router
───────────────────────
API endpoints for HR to view LLM provider statistics and
vLLM health status. Modal handles auto-scaling (no manual start/stop needed).
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.services.container_manager import container_manager
from app.services.model_registry import model_registry

router = APIRouter(prefix="/api/admin/gpu", tags=["gpu-admin"])


@router.get("/status")
async def gpu_status(user: dict = Depends(get_current_user)):
    """Get vLLM status + LLM provider stats for HR dashboard."""
    if user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="HR access required")

    container_stats = container_manager.get_stats()
    status = await container_manager.get_status()

    return {
        "container": {
            **container_stats,
            "status": status,
        },
        "llm_stats": model_registry.get_stats(),
    }


@router.get("/health")
async def gpu_health(user: dict = Depends(get_current_user)):
    """Check if vLLM endpoint is alive and serving requests."""
    if user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="HR access required")

    healthy = await container_manager.health_check()
    return {"healthy": healthy}
