
import json
import sys
import os
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else "vllm_scrape.jsonl"

outdir = os.path.join(os.path.dirname(os.path.abspath(path)), "visualization_vllm")
os.makedirs(outdir, exist_ok=True)

snaps = []
for line in open(path):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    if r.get("samples"):
        snaps.append(r)
snaps.sort(key=lambda r: r["ts"])
t0 = snaps[0]["ts"]
t = [s["ts"] - t0 for s in snaps]
last = snaps[-1]["samples"]          

def get(samples, base):
    for k, v in samples.items():
        if k.split("{", 1)[0] == base:
            return v or 0
    return 0

def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, name + ".png"), dpi=120)
    plt.close()

def line_chart(base, title):
    y = [get(s["samples"], base) for s in snaps]
    plt.figure(figsize=(9, 4))
    plt.plot(t, y, marker=".")
    plt.title(title)
    plt.xlabel("seconds")
    plt.grid(alpha=.3)
    save(base.split(":")[-1])

def histogram(base, title):
    pat = re.compile(rf"^{re.escape(base)}_bucket\{{.*?le=([^,}}]+).*\}}$")
    buckets = {}
    for k, v in last.items():
        m = pat.match(k)
        if m:
            buckets[m.group(1)] = v
    if not buckets:
        return
    def le(x):
        return float("inf") if x in ("+Inf", "Inf") else float(x)
    items = sorted(buckets.items(), key=lambda kv: le(kv[0]))
    edges, counts, prev = [], [], 0.0
    for e, cum in items:          
        counts.append(cum - prev)
        edges.append(e)
        prev = cum
    plt.figure(figsize=(9, 4))
    plt.bar(range(len(edges)), counts, color="tab:orange")
    plt.xticks(range(len(edges)), edges, rotation=45, ha="right", fontsize=7)
    plt.title(title)
    plt.xlabel("bucket upper bound")
    plt.ylabel("count")
    plt.grid(axis="y", alpha=.3)
    save(base.split(":")[-1])

def reason_bar():
    reasons, counts = [], []
    for k, v in last.items():
        if k.split("{", 1)[0] == "vllm:request_success_total" and "finished_reason=" in k:
            reasons.append(k.split("finished_reason=")[1].split(",")[0].rstrip("}"))
            counts.append(v or 0)
    if not reasons:
        return
    plt.figure(figsize=(6, 4))
    plt.bar(reasons, counts, color="tab:green")
    plt.title("Requests by finish reason")
    plt.grid(axis="y", alpha=.3)
    save("request_success_by_reason")

line_chart("vllm:num_requests_running",      "Requests running (higher under load = batching)")
line_chart("vllm:num_requests_waiting",      "Requests waiting (want ~0)")
line_chart("vllm:kv_cache_usage_perc",       "KV cache usage (near 1.0 = saturated)")
line_chart("vllm:generation_tokens_total",   "Generation tokens (slope = tokens/sec)")
line_chart("vllm:num_preemptions_total",     "Preemptions (any rise = bad)")
line_chart("vllm:prompt_tokens_cached_total","Prompt tokens served from cache")
histogram("vllm:time_to_first_token_seconds",  "TTFT distribution (lower better)")
histogram("vllm:e2e_request_latency_seconds",  "E2E latency distribution (lower better)")
histogram("vllm:request_queue_time_seconds",   "Queue time distribution (want ~0)")
histogram("vllm:request_inference_time_seconds","Inference time distribution")
histogram("vllm:request_prefill_time_seconds", "Prefill time distribution")
histogram("vllm:iteration_tokens_total",       "Tokens per engine step (higher = better batching)")
reason_bar()

print("done")