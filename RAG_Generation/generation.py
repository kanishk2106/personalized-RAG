from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator

import httpx

VLLM_BASE_URL = os.environ.get(
    "VLLM_BASE_URL", "https://kanishkvardan--vllm-qwen3-v2-serve.modal.run"
)
VLLM_MODEL = os.environ.get("VLLM_MODEL", "qwen3-8b-vllm")
MAX_GENERATION_TOKENS = int(os.environ.get("MAX_GENERATION_TOKENS", "2048"))

MODAL_TOKEN_ID = os.environ.get("Modal_Token_ID", "")
MODAL_TOKEN_SECRET = os.environ.get("Modal_Token_Secret", "")

WARMUP_MAX_WAIT = float(os.environ.get("WARMUP_MAX_WAIT", "300"))
WARMUP_INTERVAL = float(os.environ.get("WARMUP_INTERVAL", "5"))

if not (MODAL_TOKEN_ID and MODAL_TOKEN_SECRET):
    raise RuntimeError("not authenticated")

_client = httpx.AsyncClient(
    base_url=VLLM_BASE_URL,
    timeout=httpx.Timeout(connect=10.0, read=600.0, write=30.0, pool=10.0),
   
    follow_redirects=False,
    headers={
        "Modal-Key": MODAL_TOKEN_ID,
        "Modal-Secret": MODAL_TOKEN_SECRET,
    },
)


async def aclose_client() -> None:
    await _client.aclose()


async def _wait_until_ready() -> bool:
    
    deadline = time.monotonic() + WARMUP_MAX_WAIT
    while time.monotonic() < deadline:
        try:
            resp = await _client.get("/health", timeout=10.0)
            if resp.status_code == 200:
                return True
        except Exception:
            pass 
        await asyncio.sleep(WARMUP_INTERVAL)
    return False


async def stream_chat(system: str, user: str) -> AsyncIterator[str]:
    payload = {
        "model": VLLM_MODEL,
        "max_tokens": MAX_GENERATION_TOKENS,
        "stream": True,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    try:
        
        ready = await _wait_until_ready()
        if not ready:
            yield f"data: {json.dumps({'error': 'model_warmup_timeout'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        async with _client.stream(
            "POST", "/v1/chat/completions", json=payload
        ) as resp:
            if resp.status_code == 303:
                yield f"data: {json.dumps({'error': 'model_warming_up'})}\n\n"
                yield "data: [DONE]\n\n"
                return
            resp.raise_for_status()

            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data == "[DONE]":
                    break
                try:
                    delta = json.loads(data)["choices"][0]["delta"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                token = delta.get("content")
                if token:
                    yield f"data: {json.dumps({'token': token})}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as llm_connection_err:
        print(f"LLM connection error: {llm_connection_err}")
        yield f"data: {json.dumps({'error': str(llm_connection_err)})}\n\n"
        yield "data: [DONE]\n\n"