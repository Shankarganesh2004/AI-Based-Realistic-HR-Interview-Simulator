"""
Shared model registry — provides singleton instances of heavy ML models
to prevent duplicate loading across services.

Includes Gemini multi-key fallback + OpenRouter overflow + vLLM self-hosted GPU:
  Layer 1: gemini-2.5-flash across 4 Google API keys (round-robin distribution)
  Layer 2: OpenRouter free models (nemotron-3-nano-30b, step-3.5-flash, mistral-small-3.1, llama-3.3-70b)
  Layer 3: vLLM self-hosted on Modal GPU (auto scale-to-zero)

Usage:
    from app.services.model_registry import model_registry
    embedding = model_registry.embedding_model.encode("hello")
    text = await model_registry.llm_generate(prompt, system, fast=True)
"""

import time
import asyncio
import logging
import re
from typing import Optional, List

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Lazy-loading singleton registry for shared ML models.

    Gemini multi-key fallback + OpenRouter overflow + vLLM self-hosted GPU:
    - Layer 1: Try gemini-2.5-flash across all Google API keys (round-robin)
    - Layer 2: If ALL Gemini keys exhausted, fall back to OpenRouter free models
    - Layer 3: If OpenRouter exhausted, fall back to vLLM on Modal GPU (auto-scales)
    - Interview context is preserved across switches (stateless API calls)
    """

    # Error substrings that indicate quota / rate-limit exhaustion
    _QUOTA_ERROR_MARKERS = (
        "429", "resource_exhausted", "rate limit", "quota",
        "too many requests", "503", "overloaded", "capacity",
        "rate_limit_exceeded", "limit reached",
    )

    def __init__(self):
        self._embedding_model = None
        self._cross_encoder = None
        self._gemini_clients: List = []  # List of genai.Client instances
        self._openrouter_client = None   # OpenAI-compatible client for OpenRouter
        self._vllm_client = None         # OpenAI-compatible client for vLLM
        self._active_key_idx = 0

        # Round-robin counter for distributing requests across Gemini keys
        self._request_counter = 0

        # API call tracking
        self._api_call_count = 0
        self._api_call_success = 0
        self._api_call_fail = 0
        self._last_call_ts: Optional[float] = None
        self._last_error: Optional[str] = None
        self._last_error_type: Optional[str] = None
        self._last_provider: Optional[str] = None
        self._last_provider_model: Optional[str] = None

        # OpenRouter call tracking
        self._openrouter_call_count = 0
        self._openrouter_call_success = 0
        self._openrouter_call_fail = 0

        # vLLM call tracking
        self._vllm_call_count = 0
        self._vllm_call_success = 0
        self._vllm_call_fail = 0
        self._vllm_last_request_ts: Optional[float] = None

        # Build ordered Gemini model list: primary first, then fallbacks
        self._model_chain = [settings.GEMINI_MODEL]
        if settings.GEMINI_FALLBACK_MODELS:
            for m in settings.GEMINI_FALLBACK_MODELS.split(","):
                m = m.strip()
                if m and m not in self._model_chain:
                    self._model_chain.append(m)

        # Build ordered API key list: primary first, then fallbacks
        self._api_keys: List[str] = []
        if settings.GEMINI_API_KEY:
            self._api_keys.append(settings.GEMINI_API_KEY)
        if settings.GEMINI_FALLBACK_API_KEYS:
            for k in settings.GEMINI_FALLBACK_API_KEYS.split(","):
                k = k.strip()
                if k and k not in self._api_keys:
                    self._api_keys.append(k)

        # Build OpenRouter model list
        self._openrouter_models: List[str] = []
        if settings.OPENROUTER_FALLBACK_MODELS:
            for m in settings.OPENROUTER_FALLBACK_MODELS.split(","):
                m = m.strip()
                if m and m not in self._openrouter_models:
                    self._openrouter_models.append(m)

        # Track which model is currently active + cooldown per model per key
        self._active_model_idx = 0
        self._model_cooldowns: dict = {}  # (key_idx, model) -> timestamp
        self._key_cooldowns: dict = {}    # key_idx -> timestamp
        self._openrouter_cooldowns: dict = {}  # model_name -> timestamp
        self._cooldown_seconds = 60

    # ── SentenceTransformer (single instance, ~90 MB) ────────────
    @property
    def embedding_model(self):
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("ModelRegistry: SentenceTransformer loaded (shared)")
            except Exception as e:
                logger.warning(f"ModelRegistry: SentenceTransformer unavailable: {e}")
        return self._embedding_model

    # ── CrossEncoder (single instance) ────────────
    @property
    def cross_encoder(self):
        if self._cross_encoder is None:
            try:
                from sentence_transformers import CrossEncoder
                self._cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                logger.info("ModelRegistry: CrossEncoder loaded (shared)")
            except Exception as e:
                logger.warning(f"ModelRegistry: CrossEncoder unavailable: {e}")
        return self._cross_encoder

    # ── Gemini clients (one per API key) ─────────────────────────
    def _get_client(self, key_idx: int):
        """Get or create a Gemini client for the given key index."""
        while len(self._gemini_clients) <= key_idx:
            self._gemini_clients.append(None)

        if self._gemini_clients[key_idx] is None:
            api_key = self._api_keys[key_idx]
            try:
                print(f"[ModelRegistry] Creating Gemini client for key #{key_idx + 1} "
                      f"(prefix={api_key[:8]}...)")
                self._gemini_clients[key_idx] = genai.Client(api_key=api_key)
                print(f"[ModelRegistry] Gemini client #{key_idx + 1} created successfully")
                logger.info(f"ModelRegistry: Gemini client #{key_idx + 1} created")
            except Exception as e:
                print(f"[ModelRegistry] Gemini client #{key_idx + 1} creation FAILED: {e}")
                logger.warning(f"ModelRegistry: Gemini client #{key_idx + 1} unavailable: {e}")
        return self._gemini_clients[key_idx]

    @property
    def gemini_client(self):
        """Return the currently active Gemini client."""
        if not self._api_keys:
            print(f"[ModelRegistry] GEMINI_API_KEY is empty (len=0) — LLM calls will fail")
            logger.error(
                "ModelRegistry: GEMINI_API_KEY is empty — LLM calls will fail. "
                "Set GEMINI_API_KEY in backend/.env"
            )
            return None
        return self._get_client(self._active_key_idx)

    # ── OpenRouter client (OpenAI-compatible) ────────────────────
    def _get_openrouter_client(self):
        """Get or create an OpenRouter client using the openai library."""
        if self._openrouter_client is None and settings.OPENROUTER_API_KEY:
            try:
                from openai import OpenAI
                self._openrouter_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=settings.OPENROUTER_API_KEY,
                )
                print(f"[ModelRegistry] OpenRouter client created "
                      f"(key prefix={settings.OPENROUTER_API_KEY[:12]}...)")
                logger.info("ModelRegistry: OpenRouter client created")
            except Exception as e:
                print(f"[ModelRegistry] OpenRouter client creation FAILED: {e}")
                logger.warning(f"ModelRegistry: OpenRouter client unavailable: {e}")
        return self._openrouter_client

    @property
    def active_model(self) -> str:
        """Return the currently active model name."""
        return self._model_chain[self._active_model_idx]

    @property
    def last_provider(self) -> Optional[str]:
        """Return last successful provider name (gemini/openrouter/vllm)."""
        return self._last_provider

    @property
    def last_provider_model(self) -> Optional[str]:
        """Return last successful provider model name."""
        return self._last_provider_model

    # ── vLLM client (OpenAI-compatible, Modal GPU) ────────────
    def _get_vllm_client(self):
        """Get or create a vLLM client using the openai library."""
        if self._vllm_client is None and settings.VLLM_ENDPOINT:
            try:
                from openai import OpenAI
                self._vllm_client = OpenAI(
                    base_url=settings.VLLM_ENDPOINT,
                    api_key="not-needed",
                    timeout=180.0,  # Modal cold start can take 30-60s + generation
                )
                print(f"[ModelRegistry] vLLM client created "
                      f"(endpoint={settings.VLLM_ENDPOINT})")
                logger.info(f"ModelRegistry: vLLM client created "
                            f"(endpoint={settings.VLLM_ENDPOINT})")
            except Exception as e:
                print(f"[ModelRegistry] vLLM client creation FAILED: {e}")
                logger.warning(f"ModelRegistry: vLLM client unavailable: {e}")
        return self._vllm_client

    @property
    def active_key_index(self) -> int:
        """Return the index of the currently active API key (1-based for display)."""
        return self._active_key_idx + 1

    @property
    def total_keys(self) -> int:
        return len(self._api_keys)

    def _is_quota_error(self, error: Exception) -> bool:
        """Check if an exception indicates a quota / rate-limit problem."""
        err_str = str(error).lower()
        if any(marker in err_str for marker in self._QUOTA_ERROR_MARKERS):
            return True
        status = getattr(error, "status_code", None) or getattr(
            getattr(error, "response", None), "status_code", None
        )
        if status in (429, 503):
            return True
        return False

    def _is_auth_error(self, error: Exception) -> bool:
        """Check if an exception indicates an authentication failure (bad API key)."""
        status = getattr(error, "status_code", None) or getattr(
            getattr(error, "response", None), "status_code", None
        )
        if status == 401:
            return True
        err_str = str(error).lower()
        return any(m in err_str for m in ("401", "invalid api key", "invalid_api_key",
                                           "api_key_invalid", "authentication", "unauthorized"))

    def _extract_retry_delay_seconds(self, error: Exception, default_seconds: int) -> int:
        """Extract provider-suggested retry delay from error text; fallback to default."""
        text = str(error)

        # Gemini text often includes "Please retry in 41.42s"
        match = re.search(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", text, re.IGNORECASE)
        if match:
            try:
                return max(1, int(float(match.group(1))))
            except ValueError:
                pass

        # Gemini details may include "retryDelay': '41s'"
        match = re.search(r"retryDelay['\"]?\s*:\s*['\"]([0-9]+)s['\"]", text, re.IGNORECASE)
        if match:
            try:
                return max(1, int(match.group(1)))
            except ValueError:
                pass

        return default_seconds

    async def llm_generate(
        self,
        prompt: str,
        system: str = "",
        fast: bool = False,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Call LLM API with automatic Gemini multi-key + OpenRouter + vLLM fallback.

        Strategy:
        Layer 1 — Gemini (free tier, 4 keys × round-robin distribution):
          Distribute requests evenly across keys to avoid stampede
        Layer 2 — OpenRouter (free models):
          If ALL Gemini keys exhausted → try OpenRouter models in order
        Layer 3 — vLLM self-hosted GPU (Azure Container App):
          If OpenRouter exhausted → try vLLM (auto-starts container if needed)
        Returns empty string only if ALL providers fail.
        """
        if max_tokens is None:
            max_tokens = 512 if fast else 2048

        # ── Layer 1: Gemini ──────────────────────────────────────
        result = await self._try_gemini(prompt, system, max_tokens)
        if result:
            return result

        # ── Layer 2: OpenRouter ──────────────────────────────────
        if settings.OPENROUTER_API_KEY and self._openrouter_models:
            print(f"[llm_generate] All Gemini keys exhausted, falling back to OpenRouter")
            logger.info("All Gemini keys exhausted — falling back to OpenRouter")
            result = await self._try_openrouter(prompt, system, max_tokens)
            if result:
                return result

        # ── Layer 3: vLLM on Modal GPU (auto scale-to-zero) ────
        if settings.VLLM_ENABLED and settings.VLLM_ENDPOINT:
            print(f"[llm_generate] OpenRouter exhausted, falling back to vLLM (Modal)")
            logger.info("OpenRouter exhausted — falling back to vLLM on Modal GPU")
            result = await self._try_vllm(prompt, system, max_tokens)
            if result:
                return result

        print(f"[llm_generate] ALL providers exhausted (Gemini + OpenRouter + vLLM)")
        logger.error("All LLM providers exhausted (Gemini + OpenRouter + vLLM)")
        return ""

    async def _try_gemini(
        self, prompt: str, system: str, max_tokens: int
    ) -> str:
        """Try all Gemini keys × models. Returns text or empty string."""
        if not self._api_keys:
            print(f"[llm_generate] ABORT: No Gemini API keys configured")
            return ""

        # Round-robin: distribute requests across keys to prevent stampede
        self._request_counter += 1
        start_key = self._request_counter % len(self._api_keys)

        # Build key order: round-robin start, then wrap around
        key_order = []
        for i in range(len(self._api_keys)):
            key_order.append((start_key + i) % len(self._api_keys))

        now = time.time()
        last_error = None

        print(f"[llm_generate] Gemini: {len(self._api_keys)} keys, "
              f"{len(self._model_chain)} models, prompt_len={len(prompt)}")

        ready_keys = [k for k in key_order if time.time() >= self._key_cooldowns.get(k, 0)]
        if not ready_keys:
            next_ready_at = min(self._key_cooldowns.get(k, now) for k in key_order)
            wait_for = max(1, int(next_ready_at - now))
            print(f"[llm_generate] Gemini keys cooling down ({len(key_order)}/{len(key_order)}). "
                  f"Skipping Gemini and retrying fallback providers. Next key in ~{wait_for}s")
            return ""

        for key_idx in key_order:
            now = time.time()
            cooldown_until = self._key_cooldowns.get(key_idx, 0)
            if now < cooldown_until:
                continue

            client = self._get_client(key_idx)
            if client is None:
                continue

            # Build model order for this key
            models_to_try = []
            tried = set()
            active = self._model_chain[self._active_model_idx]
            cd_key = (key_idx, active)
            if now >= self._model_cooldowns.get(cd_key, 0):
                models_to_try.append(active)
                tried.add(active)
            for m in self._model_chain:
                if m not in tried:
                    cd_key = (key_idx, m)
                    if now >= self._model_cooldowns.get(cd_key, 0):
                        models_to_try.append(m)
                        tried.add(m)

            # If all models for this key are currently cooling down, skip the key entirely.
            if not models_to_try:
                self._key_cooldowns[key_idx] = max(
                    self._key_cooldowns.get(key_idx, 0),
                    now + 1,
                )
                continue

            all_models_failed = True
            for model_name in models_to_try:
                try:
                    self._api_call_count += 1
                    self._last_call_ts = time.time()
                    print(f"[llm_generate] Gemini Key #{key_idx + 1}, model={model_name}, "
                          f"max_tokens={max_tokens} (call #{self._api_call_count})")

                    contents = system + "\n\n" + prompt if system else prompt

                    response = await asyncio.to_thread(
                        client.models.generate_content,
                        model=model_name,
                        contents=contents,
                        config={
                            "temperature": 0.7,
                            "max_output_tokens": max_tokens,
                        },
                    )

                    text = response.text if response and response.text else ""
                    self._api_call_success += 1
                    print(f"[llm_generate] Gemini OK key=#{key_idx + 1} model={model_name} "
                          f"len={len(text)} (success #{self._api_call_success})")

                    if text:
                        self._active_key_idx = key_idx
                        idx = self._model_chain.index(model_name)
                        if idx != self._active_model_idx:
                            self._active_model_idx = idx
                        self._last_provider = "gemini"
                        self._last_provider_model = model_name
                    all_models_failed = False
                    return text

                except Exception as e:
                    self._api_call_fail += 1
                    last_error = e
                    self._last_error = str(e)[:500]
                    self._last_error_type = type(e).__name__
                    print(f"[llm_generate] EXCEPTION Gemini key=#{key_idx + 1} model={model_name}: "
                          f"{self._last_error_type}: {self._last_error}")

                    if self._is_auth_error(e):
                        logger.error(f"Gemini AUTH ERROR key #{key_idx + 1}: {e}")
                        break  # Try next key

                    elif self._is_quota_error(e) or getattr(e, 'status_code', None) in (403, 429, 503):
                        # 24-hour cooldown on quota exhausted
                        retry_delay = 86400 
                        logger.warning(f"Gemini quota/rate error key #{key_idx + 1} "
                                       f"model={model_name}: {e}")
                        cooldown_until = time.time() + retry_delay
                        self._model_cooldowns[(key_idx, model_name)] = cooldown_until
                        self._key_cooldowns[key_idx] = max(
                            self._key_cooldowns.get(key_idx, 0),
                            cooldown_until,
                        )
                        continue  # Try next model

                    elif "failed_precondition" in str(e).lower() or "not supported" in str(e).lower():
                        logger.warning(f"Gemini location error key #{key_idx + 1} "
                                       f"model={model_name}: {e}")
                        self._model_cooldowns[(key_idx, model_name)] = now + 3600
                        continue

                    else:
                        logger.error(f"Gemini error key #{key_idx + 1} model={model_name}: {e}")
                        continue

            if all_models_failed:
                next_model_ready = max(
                    now + 1,
                    min(self._model_cooldowns.get((key_idx, m), now + self._cooldown_seconds)
                        for m in self._model_chain),
                )
                self._key_cooldowns[key_idx] = max(
                    self._key_cooldowns.get(key_idx, 0),
                    next_model_ready,
                )
                print(f"[llm_generate] All Gemini models exhausted for key #{key_idx + 1}")

        return ""  # All Gemini keys exhausted

    async def _try_openrouter(
        self, prompt: str, system: str, max_tokens: int
    ) -> str:
        """Try OpenRouter models in order. Returns text or empty string."""
        client = self._get_openrouter_client()
        if client is None:
            print(f"[llm_generate] OpenRouter client unavailable")
            return ""

        now = time.time()
        # Reasoning models (nemotron, step-flash) consume output tokens on
        # internal "thinking" before producing content.  If max_tokens is too
        # low the thinking fills the budget and content comes back empty,
        # which makes us skip the model and fall through to vLLM.
        # Use a generous budget so the response always has room.
        or_max_tokens = max(max_tokens, 4096)

        for model_name in self._openrouter_models:
            # Skip models on cooldown
            if now < self._openrouter_cooldowns.get(model_name, 0):
                continue

            try:
                self._openrouter_call_count += 1
                self._last_call_ts = time.time()
                print(f"[llm_generate] OpenRouter model={model_name}, "
                      f"max_tokens={or_max_tokens} (OR call #{self._openrouter_call_count})")

                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=model_name,
                    messages=messages,
                    max_tokens=or_max_tokens,
                    temperature=0.7,
                )

                text = ""
                if response and response.choices and len(response.choices) > 0:
                    text = (response.choices[0].message.content or "").strip()

                if not text:
                    # Model returned empty/None content (e.g. reasoning model
                    # consumed all tokens on thinking). Try next model.
                    self._openrouter_call_fail += 1
                    finish = getattr(response.choices[0], "finish_reason", "unknown") if response and response.choices else "no_choices"
                    print(f"[llm_generate] OpenRouter model={model_name} returned EMPTY "
                          f"(finish_reason={finish}), trying next model")
                    logger.warning(f"OpenRouter empty response model={model_name} "
                                   f"finish_reason={finish}")
                    continue

                self._openrouter_call_success += 1
                self._last_provider = "openrouter"
                self._last_provider_model = model_name
                print(f"[llm_generate] OpenRouter OK model={model_name} "
                      f"len={len(text)} (OR success #{self._openrouter_call_success})")
                return text

            except Exception as e:
                self._openrouter_call_fail += 1
                self._last_error = str(e)[:500]
                self._last_error_type = type(e).__name__
                print(f"[llm_generate] EXCEPTION OpenRouter model={model_name}: "
                      f"{self._last_error_type}: {self._last_error}")

                if self._is_quota_error(e):
                    # 24-hour cooldown on quota exhausted
                    self._openrouter_cooldowns[model_name] = now + 86400
                    logger.warning(f"OpenRouter quota error model={model_name}: {e}")
                    continue  # Try next model
                else:
                    logger.error(f"OpenRouter error model={model_name}: {e}")
                    continue  # Try next model anyway

        return ""  # All OpenRouter models exhausted

    async def _try_vllm(
        self, prompt: str, system: str, max_tokens: int
    ) -> str:
        """Try vLLM on Modal GPU. Returns text or empty string.

        Modal handles scale-to-zero natively. If the container is cold,
        the first request triggers a warm-up (~30-60s). The OpenAI client
        timeout is set to 180s to accommodate this.
        """
        client = self._get_vllm_client()
        if client is None:
            print(f"[llm_generate] vLLM client unavailable")
            return ""

        try:
            self._vllm_call_count += 1
            self._last_call_ts = time.time()
            print(f"[llm_generate] vLLM model={settings.VLLM_MODEL}, "
                  f"max_tokens={max_tokens} (vLLM call #{self._vllm_call_count})")

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=settings.VLLM_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )

            text = ""
            if response and response.choices and len(response.choices) > 0:
                text = (response.choices[0].message.content or "").strip()

            if not text:
                self._vllm_call_fail += 1
                finish = getattr(response.choices[0], "finish_reason", "unknown") if response and response.choices else "no_choices"
                print(f"[llm_generate] vLLM returned EMPTY (finish_reason={finish})")
                logger.warning(f"vLLM empty response finish_reason={finish}")
                return ""

            self._vllm_call_success += 1
            self._vllm_last_request_ts = time.time()
            self._last_provider = "vllm"
            self._last_provider_model = settings.VLLM_MODEL
            print(f"[llm_generate] vLLM OK model={settings.VLLM_MODEL} "
                  f"len={len(text)} (vLLM success #{self._vllm_call_success})")
            return text

        except Exception as e:
            self._vllm_call_fail += 1
            self._last_error = str(e)[:500]
            self._last_error_type = type(e).__name__
            print(f"[llm_generate] EXCEPTION vLLM: {self._last_error_type}: {self._last_error}")
            logger.error(f"vLLM error: {e}")
            return ""

    def warm_up(self):
        """Eagerly load all models (call during app startup)."""
        _ = self.embedding_model
        _ = self.gemini_client
        if settings.OPENROUTER_API_KEY:
            _ = self._get_openrouter_client()
        if settings.VLLM_ENABLED and settings.VLLM_ENDPOINT:
            _ = self._get_vllm_client()
        logger.info(f"ModelRegistry: Gemini chain = {self._model_chain}, "
                     f"Gemini keys = {len(self._api_keys)}, "
                     f"OpenRouter models = {self._openrouter_models}, "
                     f"vLLM enabled = {settings.VLLM_ENABLED}")

    def get_stats(self) -> dict:
        """Return API call statistics for diagnostics."""
        import datetime as _dt
        return {
            "gemini_keys_configured": len(self._api_keys),
            "gemini_primary_key_set": bool(settings.GEMINI_API_KEY),
            "gemini_client_ready": self.gemini_client is not None,
            "active_model": self.active_model,
            "active_key_index": self.active_key_index,
            "total_keys": self.total_keys,
            "model_chain": self._model_chain,
            "api_calls_total": self._api_call_count,
            "api_calls_success": self._api_call_success,
            "api_calls_failed": self._api_call_fail,
            "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
            "openrouter_models": self._openrouter_models,
            "openrouter_calls_total": self._openrouter_call_count,
            "openrouter_calls_success": self._openrouter_call_success,
            "openrouter_calls_failed": self._openrouter_call_fail,
            "vllm_enabled": settings.VLLM_ENABLED,
            "vllm_endpoint": settings.VLLM_ENDPOINT or None,
            "vllm_model": settings.VLLM_MODEL,
            "vllm_calls_total": self._vllm_call_count,
            "vllm_calls_success": self._vllm_call_success,
            "vllm_calls_failed": self._vllm_call_fail,
            "last_call_at": (
                _dt.datetime.fromtimestamp(self._last_call_ts).isoformat()
                if self._last_call_ts else None
            ),
            "last_provider": self._last_provider,
            "last_provider_model": self._last_provider_model,
            "last_error": self._last_error,
            "last_error_type": self._last_error_type,
        }


model_registry = ModelRegistry()
