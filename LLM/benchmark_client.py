import argparse
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

import httpx

from prompts import PromptItem, load_hotpotqa_prompts
from metrics import RequestMetric, summarize, write_csv


async def one_request(
    client: httpx.AsyncClient,
    base_url: str,
    model: str,
    item: PromptItem,
    idx: int,
    concurrency: int,
    max_tokens: int,
    temperature: float,
    run_id: str,
) -> RequestMetric:
    body = {
        "model": model,
        "messages": item.messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.95,
        "stream": True,
        "stream_options": {"include_usage": True},
        "chat_template_kwargs": {"enable_thinking": False},  

    }
    sent_at = time.time()
    t0 = time.perf_counter()
    ttft: float | None = None
    first_token_perf: float | None = None
    last_token_perf: float | None = None
    last_token_at: float = sent_at
    prompt_tokens = 0
    completion_tokens = 0
    try:
        async with client.stream(
            "POST", f"{base_url}/v1/chat/completions", json=body
        ) as resp:
            if resp.status_code != 200:
                err_body = (await resp.aread()).decode("utf-8", errors="replace")[:500]
                raise RuntimeError(f"HTTP {resp.status_code}: {err_body}")
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                payload = line[len("data: "):].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices") or []
                if choices:
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")
                    if content:
                        now_perf = time.perf_counter()
                        if ttft is None:
                            ttft = (now_perf - t0) * 1000.0
                            first_token_perf = now_perf
                        last_token_perf = now_perf
                        last_token_at = time.time()
                usage = chunk.get("usage")
                if usage:
                    prompt_tokens = int(usage.get("prompt_tokens", 0))
                    completion_tokens = int(usage.get("completion_tokens", 0))

        total_ms = (time.perf_counter() - t0) * 1000.0
        if ttft is None or first_token_perf is None or last_token_perf is None:
            ttft = total_ms
            first_token_perf = last_token_perf = time.perf_counter()
            last_token_at = time.time()

        decode_ms = max((last_token_perf - first_token_perf) * 1000.0, 1e-3)
        if completion_tokens > 1:
            tpot_ms = decode_ms / (completion_tokens - 1)
            throughput = (completion_tokens - 1) / (decode_ms / 1000.0)
        else:
            tpot_ms = 0.0
            throughput = 0.0

        return RequestMetric(
            idx=idx,
            concurrency=concurrency,
            ttft_ms=ttft,
            total_ms=total_ms,
            tpot_ms=tpot_ms,
            throughput_tok_s=throughput,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status="ok",
            run_id=run_id,
            sent_at=sent_at,
            last_token_at=last_token_at,
            prefix_tier=item.prefix_tier,
        )
    except Exception as e:
        total_ms = (time.perf_counter() - t0) * 1000.0
        return RequestMetric(
            idx=idx,
            concurrency=concurrency,
            ttft_ms=-1.0,
            total_ms=total_ms,
            tpot_ms=-1.0,
            throughput_tok_s=0.0,
            prompt_tokens=0,
            completion_tokens=0,
            status="error",
            run_id=run_id,
            sent_at=sent_at,
            last_token_at=last_token_at,
            prefix_tier=item.prefix_tier,
            error=str(e),
        )


async def run_phase(
    base_url: str,
    model: str,
    prompts: list[PromptItem],
    concurrency: int,
    max_tokens: int,
    temperature: float,
    warmup: int,
    run_id: str,
) -> tuple[list[RequestMetric], float]:
    n_requests = len(prompts)
    timeout = httpx.Timeout(connect=30.0, read=600.0, write=30.0, pool=None)
    limits = httpx.Limits(
        max_connections=max(concurrency * 2, 16),
        max_keepalive_connections=concurrency,
    )

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        if warmup > 0:
            print("Warmup", flush=True)
            for i in range(warmup):
                await one_request(
                    client, base_url, model,
                    prompts[i % len(prompts)],
                    -1, 1, max_tokens, temperature, run_id,
                )

        print(
            f"Phase: run_id={run_id} concurrency={concurrency}, n={n_requests}, "
            f"max_tokens={max_tokens}, temperature={temperature}",
            flush=True,
        )
        sem = asyncio.Semaphore(concurrency)

        async def bounded(i: int) -> RequestMetric:
            async with sem:
                return await one_request(
                    client, base_url, model, prompts[i],
                    i, concurrency, max_tokens, temperature, run_id,
                )

        wall_t0 = time.perf_counter()
        results = await asyncio.gather(*[bounded(i) for i in range(n_requests)])
        wall_total = time.perf_counter() - wall_t0
    return results, wall_total


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--base-url", required=True,
                    help="e.g. https://<workspace>--llm-bench-hf-baseline-serve.modal.run/v1")
    ap.add_argument("--model", default="qwen3-8b-vllm")
    ap.add_argument("--concurrency", type=int, default=30)
    ap.add_argument("--n", type=int, default=50,
                    help="number of HotpotQA prompts to sample and measure")
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--temperature", type=float, default=0.0,
                    help="0.0 = greedy, for reproducible runs")
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42,
                    help="deterministic prompt sampling")
    ap.add_argument("--cache-dir", default=None,
                    help="HF datasets cache dir (defaults to ~/.cache/huggingface)")
    ap.add_argument("--output", required=True, help="CSV path for per-request rows")
    ap.add_argument("--run-id", default=None,
                    help="shared identifier joining client CSV with collector jsonl. "
                         "Defaults to run_YYYYMMDD_HHMMSS.")
    args = ap.parse_args()

    run_id = args.run_id or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    prompts = load_hotpotqa_prompts(n=args.n, seed=args.seed, cache_dir=args.cache_dir)

    metrics, wall = asyncio.run(run_phase(
        base_url=args.base_url.rstrip("/"),
        model=args.model,
        prompts=prompts,
        concurrency=args.concurrency,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        warmup=args.warmup,
        run_id=run_id,
    ))
    summarize(metrics, wall)
    write_csv(metrics, Path(args.output))


if __name__ == "__main__":
    main()