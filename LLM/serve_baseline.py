import modal

MODEL_ID = "Qwen/Qwen3-8B"
MODEL_DIR = f"/models/{MODEL_ID}"
GPU = "A10G"
SERVED_NAME = "qwen3-8b-hf"
PORT = 8000

app = modal.App("llm-bench-hf-baseline")
volume = modal.Volume.from_name("llm-bench-models", create_if_missing=True)

hf_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
    "torch==2.4.1",
    "transformers==4.56.2",
    "huggingface_hub[hf_transfer]==0.34.4",
    "accelerate==1.1.1",
    "fastapi==0.115.5",
    "uvicorn[standard]==0.32.1",
    "sse-starlette==2.1.3",
)
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)


@app.function(
    image=hf_image,
    volumes={"/models": volume},
    timeout=60 * 60,
    cpu=4,
    memory=16 * 1024,
)
def download_model():
    import os
    from huggingface_hub import snapshot_download

    os.makedirs(MODEL_DIR, exist_ok=True)
    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=MODEL_DIR,
        ignore_patterns=["*.pt", "*.bin", "*.gguf"],
    )
    volume.commit()


@app.function(
    image=hf_image,
    gpu=GPU,
    volumes={"/models": volume},
    timeout=24 * 60 * 60,
    scaledown_window=10 * 60,
)
@modal.concurrent(max_inputs=64)
@modal.asgi_app()
def serve():
    import asyncio
    import json
    import queue
    import time
    import uuid
    from threading import Thread

    import torch
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TextIteratorStreamer,
    )

    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="sdpa",
    )
    model.eval()
    gpu_lock = asyncio.Lock()

    class ChatMessage(BaseModel):
        role: str
        content: str

    class ChatCompletionRequest(BaseModel):
        model: str = SERVED_NAME
        messages: list[ChatMessage]
        max_tokens: int | None = Field(default=256, ge=1, le=4096)
        temperature: float = Field(default=0.7, ge=0.0, le=2.0)
        top_p: float = Field(default=0.95, ge=0.0, le=1.0)
        stream: bool = False
        stream_options: dict | None = None

    web = FastAPI(title="qwen3-8b hf baseline")

    @web.get("/health")
    def health():
        gpu_ok = torch.cuda.is_available()
        allocated = torch.cuda.memory_allocated() / (1024 ** 3) if gpu_ok else 0
        return {
            "web_server": "ok",
            "model": SERVED_NAME,
            "gpu_available": gpu_ok,
            "gpu_vram_used_gb": round(allocated, 2),
        }

    def _build_inputs(messages: list[ChatMessage]):
        chat = [{"role": m.role, "content": m.content} for m in messages]
        prompt_ids = tokenizer.apply_chat_template(
            chat,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(model.device)
        return prompt_ids

    def _gen_kwargs(req: ChatCompletionRequest) -> dict:
        do_sample = req.temperature > 0.0
        return dict(
            max_new_tokens=req.max_tokens or 256,
            do_sample=do_sample,
            temperature=req.temperature if do_sample else 1.0,
            top_p=req.top_p,
            pad_token_id=tokenizer.eos_token_id,
        )

    @web.post("/v1/chat/completions")
    async def chat_completions(req: ChatCompletionRequest):
        return StreamingResponse(
            _stream_response(req),
            media_type="text/event-stream",
        )

    async def _stream_response(req: ChatCompletionRequest):
        cid = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created = int(time.time())
        model_name = SERVED_NAME

        def _chunk(delta: dict, finish: str | None = None, usage: dict | None = None) -> str:
            payload = {
                "id": cid,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "delta": delta,
                    "finish_reason": finish,
                }],
            }
            if usage is not None:
                payload["usage"] = usage
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        async with gpu_lock:
            input_ids = _build_inputs(req.messages)
            prompt_tokens = int(input_ids.shape[-1])

            streamer = TextIteratorStreamer(
                tokenizer,
                skip_prompt=True,
                skip_special_tokens=True,
                timeout=120.0,  
            )
            gen_kwargs = dict(_gen_kwargs(req), input_ids=input_ids, streamer=streamer)
            result: dict = {}
            thread = Thread(target=_run_generate, args=(model, gen_kwargs, result))
            thread.start()
            yield _chunk({"role": "assistant"})
            loop = asyncio.get_running_loop()
            it = iter(streamer)
            finish_reason = "stop"

            while True:
                try:
                    token_text = await loop.run_in_executor(None, _next_or_none, it)
                except queue.Empty:
                    finish_reason = "error"
                    break
                if token_text is None:
                    break
                if token_text == "":
                    continue
                yield _chunk({"content": token_text})

            thread.join()

            if result.get("error") is not None:
                finish_reason = "error"
            output_ids = result.get("output_ids")
            if output_ids is not None:
                completion_tokens = int(output_ids.shape[-1]) - prompt_tokens
            else:
                completion_tokens = 0

            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            }

            yield _chunk({}, finish=finish_reason, usage=usage)
            yield "data: [DONE]\n\n"

    return web


def _run_generate(model, gen_kwargs, result):
    import torch
    try:
        with torch.inference_mode():
            output = model.generate(**gen_kwargs)
        result["output_ids"] = output
    except Exception as e:
        result["error"] = e


def _next_or_none(it):
    try:
        return next(it)
    except StopIteration:
        return None