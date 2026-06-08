import argparse
import json
import signal
import time
from pathlib import Path
from urllib.request import Request, urlopen
from prometheus_client.parser import text_string_to_metric_families
_stop = {"flag": False}
def _on_signal(signum, frame):
    _stop["flag"] = True
signal.signal(signal.SIGINT, _on_signal)
signal.signal(signal.SIGTERM, _on_signal)
def scrape_once(metrics_url: str, timeout: float = 5.0) -> dict:
    req = Request(metrics_url, headers={"Accept": "text/plain"})
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    out: dict = {}
    for fam in text_string_to_metric_families(body):
        for sample in fam.samples:
            key = sample.name
            if sample.labels:
                label_str = ",".join(
                    f"{k}={v}" for k, v in sorted(sample.labels.items())
                )
                key = f"{sample.name}{{{label_str}}}"
            out[key] = sample.value
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-url", required=True,
                    help="vLLM server base URL. /v1 suffix is stripped if present.")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True, help="output JSONL path")
    ap.add_argument("--interval", type=float, default=1.0, help="poll interval seconds")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    metrics_url = f"{base}/metrics"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    f = out_path.open("w", buffering=1)

    print(f"Started scrapper to store in {out_path}", flush=True)
    try:
        while not _stop["flag"]:
            t0 = time.time()
            try:
                samples = scrape_once(metrics_url)
                rec = {"ts": t0, "run_id": args.run_id, "samples": samples}
            except Exception as e:
                rec = {"ts": t0, "run_id": args.run_id, "error": str(e)}
            f.write(json.dumps(rec) + "\n")
            remaining = max(0.0, args.interval - (time.time() - t0))
            slept = 0.0
            while slept < remaining and not _stop["flag"]:
                step = min(0.1, remaining - slept)
                time.sleep(step)
                slept += step
    finally:
        f.close()
        print("done scrapping.", flush=True)


if __name__ == "__main__":
    main()