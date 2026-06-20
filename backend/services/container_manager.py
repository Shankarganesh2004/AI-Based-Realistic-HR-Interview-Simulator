"""
Modal vLLM Status Checker — Lightweight health-check for the Modal-hosted vLLM endpoint.

Modal handles scale-to-zero natively. No manual start/stop management needed.
This module provides health-check and status utilities for the HR dashboard.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ContainerManager:
    """Lightweight status checker for Modal-hosted vLLM."""

    def __init__(self):
        self._last_health: bool = False

    @property
    def is_configured(self) -> bool:
        """Check if vLLM is configured (endpoint set + enabled)."""
        return bool(settings.VLLM_ENABLED and settings.VLLM_ENDPOINT)

    async def health_check(self) -> bool:
        """Ping the vLLM /health endpoint on Modal."""
        if not settings.VLLM_ENDPOINT:
            return False
        try:
            base_url = settings.VLLM_ENDPOINT.rstrip("/v1").rstrip("/")
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{base_url}/health")
                self._last_health = response.status_code == 200
                return self._last_health
        except Exception:
            self._last_health = False
            return False

    async def get_status(self) -> str:
        """Get current status: 'running', 'sleeping', or 'not_configured'."""
        if not self.is_configured:
            return "not_configured"
        healthy = await self.health_check()
        return "running" if healthy else "sleeping"

    def get_stats(self) -> dict:
        """Return vLLM configuration stats for dashboard."""
        return {
            "configured": self.is_configured,
            "vllm_enabled": settings.VLLM_ENABLED,
            "vllm_endpoint": settings.VLLM_ENDPOINT or None,
            "vllm_model": settings.VLLM_MODEL,
            "platform": "modal",
            "auto_scaling": True,
            "cost_when_idle": "$0",
        }


# Singleton
container_manager = ContainerManager()
