import json
import sys
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else "nvml.jsonl"

outdir = os.path.join(os.path.dirname(os.path.abspath(path)), "visualization_nvml")
os.makedirs(outdir, exist_ok=True)

rows = []
for line in open(path):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    if "gpu_util_pct" in r:
        rows.append(r)
rows.sort(key=lambda r: r["ts"])
t0 = rows[0]["ts"]
t = [r["ts"] - t0 for r in rows]

def line_chart(key, title, fname):
    y = [r.get(key, 0) or 0 for r in rows]
    plt.figure(figsize=(9, 4))
    plt.plot(t, y, marker=".")
    plt.title(f"{title}  (peak={max(y):g})")
    plt.xlabel("seconds")
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, fname), dpi=120)
    plt.close()

line_chart("gpu_util_pct", "GPU utilization % (higher under load = good)", "gpu_util.png")
line_chart("mem_util_pct", "Memory-bandwidth % (high = mem bound)",        "mem_util.png")
line_chart("vram_used_mb", "VRAM used (MB)",                               "vram_used.png")
line_chart("power_w",      "Power draw (W)",                               "power.png")
line_chart("temp_c",       "Temperature (C)",                             "temp.png")

print("done")