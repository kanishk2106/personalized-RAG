import modal
import subprocess

APP_NAME = "vllm-qwen3-v2"
MODEL = "Qwen/Qwen3-8B"
MAX_MODEL_LEN = 6096
GPU = "A10G"
VLLM_PORT = 8000
MAX_NUM_SEQS = 16

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.9.0-devel-ubuntu22.04",
        add_python="3.12",
    )
    .entrypoint([])
    .apt_install("git")
    .uv_pip_install(
        "vllm==0.21.0",
    )
    .env({
        "HF_XET_HIGH_PERFORMANCE": "1",
    })
)

app = modal.App(APP_NAME)


@app.function(
    image=image,
    gpu=GPU,
    volumes={
        "/root/.cache/huggingface": hf_cache,
    },
    timeout=60 * 60,
    scaledown_window=60 * 10,
    max_containers=1,
)
@modal.concurrent(max_inputs=MAX_NUM_SEQS)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * 60, requires_proxy_auth=True)
def serve():
    cmd = [
        "vllm", "serve", MODEL,
        "--served-model-name", "qwen3-8b-vllm",
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--dtype", "bfloat16",
        "--max-model-len", str(MAX_MODEL_LEN),
        "--kv-cache-dtype", "fp8",
        "--gpu-memory-utilization", "0.90",
        "--max-num-seqs", str(MAX_NUM_SEQS),
        "--enforce-eager",
    ]
    subprocess.Popen(cmd)