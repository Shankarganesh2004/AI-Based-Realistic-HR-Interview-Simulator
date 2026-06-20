"""
Modal vLLM Deployment — AI Interview Platform Layer 3 Fallback
──────────────────────────────────────────────────────────────
Deploys Qwen2.5-7B-Instruct-AWQ (4-bit quantized) on a T4 GPU via Modal.
Scale-to-zero: $0 when idle, auto-starts on request (~30-60s cold start).

Setup:
  1. pip install modal
  2. modal setup                   # authenticate with your Modal account
  3. modal deploy modal_vllm.py    # deploy (first build ~5-10 min to download model)

After deployment, Modal prints your endpoint URL. Add it to backend/.env:
  VLLM_ENDPOINT=https://<your-username>--vllm-interview-serve.modal.run/v1
  VLLM_ENABLED=true

Cost: ~$0.59/hr T4 GPU, only while actively serving requests. $0 when idle.
      $5 free credit on sign-up (no card needed).
      $30/month free with payment method added.
"""

import modal  # pyright: ignore[reportMissingImports]

# ── Configuration ──────────────────────────────────────────────
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct-AWQ"
MODEL_REVISION = "main"
MODEL_MAX_LEN = 4096
GPU_TYPE = "T4"                # $0.59/hr, 16GB VRAM
IDLE_TIMEOUT = 60              # auto-stop after 1 min idle to save credits


# ── Container Image ───────────────────────────────────────────

vllm_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "vllm==0.6.6.post1",
        "transformers>=4.45.2,<5.0.0",
        "huggingface_hub[hf_transfer]",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

app = modal.App("vllm-interview")


# ── vLLM Server ───────────────────────────────────────────────

@app.function(
    image=vllm_image,
    gpu=GPU_TYPE,
    scaledown_window=IDLE_TIMEOUT,
    timeout=1800,
)
@modal.concurrent(max_inputs=10)
@modal.web_server(port=8000, startup_timeout=600)
def serve():
    """Run vLLM OpenAI-compatible API server on a T4 GPU."""
    import subprocess

    subprocess.Popen([
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL_NAME,
        "--revision", MODEL_REVISION,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--max-model-len", str(MODEL_MAX_LEN),
        "--dtype", "half",
        "--quantization", "awq",
        "--gpu-memory-utilization", "0.90",
        "--trust-remote-code",
        "--enforce-eager",
    ])
