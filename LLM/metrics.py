import csv
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RequestMetric:
    idx: int
    concurrency: int
    ttft_ms: float
    total_ms: float
    tpot_ms: float
    throughput_tok_s: float
    prompt_tokens: int
    completion_tokens: int
    status: str
    run_id: str = ""
    sent_at: float = 0.0         
    last_token_at: float = 0.0    
    prefix_tier: str = "unknown"  
    error: str = ""


def percentile(sorted_xs: list[float], p: float) -> float:
    if not sorted_xs:
        return float("nan")
    k = int(round((p / 100.0) * (len(sorted_xs) - 1)))
    return sorted_xs[max(0, min(k, len(sorted_xs) - 1))]


def summarize(metrics: list[RequestMetric], wall_total: float) -> None:
    ok = [m for m in metrics if m.status == "ok"]
    failed = len(metrics) - len(ok)
    if not ok:
        print(f"No successful requests. {failed} failed.")
        for m in metrics[:3]:
            if m.error:
                print(f"  example error: {m.error}")
        return

    ttfts = sorted(m.ttft_ms for m in ok)
    totals = sorted(m.total_ms for m in ok)
    tpots = sorted(m.tpot_ms for m in ok if m.tpot_ms > 0)
    prompt_lens = sorted(m.prompt_tokens for m in ok)
    total_completion = sum(m.completion_tokens for m in ok)
    overall_tok_s = total_completion / wall_total if wall_total > 0 else 0.0

    print()
    print(f"  successful   : {len(ok)}/{len(metrics)}  (failed={failed})")
    print(f"  wall time    : {wall_total:.2f}s")
    print(f"  prompt tokens: p50={percentile(prompt_lens, 50):.0f}  p95={percentile(prompt_lens, 95):.0f}  max={prompt_lens[-1]}")
    print(f"  TTFT  ms     : p50={percentile(ttfts, 50):.1f}  p95={percentile(ttfts, 95):.1f}  p99={percentile(ttfts, 99):.1f}")
    print(f"  total ms     : p50={percentile(totals, 50):.1f}  p95={percentile(totals, 95):.1f}  p99={percentile(totals, 99):.1f}")
    if tpots:
        print(
            f"  TPOT  ms     : p50={percentile(tpots, 50):.2f}  "
            f"p95={percentile(tpots, 95):.2f}  p99={percentile(tpots, 99):.2f}  "
            f"mean={statistics.mean(tpots):.2f}"
        )
    print(f"  throughput   : {overall_tok_s:.1f} tok/s  (completion_tokens={total_completion})")
    print()


def write_csv(metrics: list[RequestMetric], path: Path) -> None:
    if not metrics:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(metrics[0]).keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for m in metrics:
            w.writerow(asdict(m))
    print(f"wrote {path}")