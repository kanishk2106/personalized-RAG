import modal
import subprocess
import time

APP_NAME = "vllm-qwen3-v2"
MODEL = "Qwen/Qwen3-8B"
MAX_MODEL_LEN = 8192
GPU = "A10G"
VLLM_PORT = 8000

bench_volume = modal.Volume.from_name("bench-runs", create_if_missing=True)
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
        "nvidia-ml-py",
    )
    .env({
        "HF_XET_HIGH_PERFORMANCE": "1",
    })
    .add_local_file("collectors/nvml_sampler.py", "/opt/nvml_sampler.py")
)

app = modal.App(APP_NAME)


@app.function(
    image=image,
    gpu=GPU,
    volumes={
        "/bench": bench_volume,
        "/root/.cache/huggingface": hf_cache,
    },
    timeout=60 * 60,
    scaledown_window=60 * 30,
    max_containers=1,
)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * 60)
def serve():
    container_run_id = f"container_{int(time.time())}"
    subprocess.Popen(
        [
            "python", "/opt/nvml_sampler.py",
            "--run-id", container_run_id,
            "--out", "/bench/nvml.jsonl",
            "--interval", "1.0",
        ]
    )
    time.sleep(2)

    cmd = [
        "vllm", "serve", MODEL,
        "--served-model-name", "qwen3-8b-vllm",
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--dtype", "bfloat16",
        "--max-model-len", str(MAX_MODEL_LEN),
        "--gpu-memory-utilization", "0.90",
        "--enforce-eager",
    ]
    subprocess.Popen(cmd)