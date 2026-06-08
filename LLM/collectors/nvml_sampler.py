import argparse
import json
import signal
import time
from pathlib import Path
import pynvml
_stop = {"flag": False}
def _on_signal(signum, frame):
    _stop["flag"] = True
signal.signal(signal.SIGINT, _on_signal)
signal.signal(signal.SIGTERM, _on_signal)
_THROTTLE_FLAGS = [
    ("gpu_idle",        "nvmlClocksThrottleReasonGpuIdle"),
    ("sw_power_cap",    "nvmlClocksThrottleReasonSwPowerCap"),
    ("sw_thermal",      "nvmlClocksThrottleReasonSwThermalSlowdown"),
    ("hw_thermal",      "nvmlClocksThrottleReasonHwThermalSlowdown"),
    ("hw_power_brake",  "nvmlClocksThrottleReasonHwPowerBrakeSlowdown"),
]
def _throttle_reasons(handle) -> list[str]:
    try:
        bits = pynvml.nvmlDeviceGetCurrentClocksThrottleReasons(handle)
    except pynvml.NVMLError:
        return []
    out = []
    for name, attr in _THROTTLE_FLAGS:
        flag = getattr(pynvml, attr, None)
        if flag is not None and (bits & flag):
            out.append(name)
    return out
def sample_one(handle) -> dict:
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
    try:
        power_w = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
    except pynvml.NVMLError:
        power_w = -1.0
    try:
        temp_c = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    except pynvml.NVMLError:
        temp_c = -1
    return {
        "gpu_util_pct": util.gpu,
        "mem_util_pct": util.memory,
        "vram_used_mb": mem.used / 1024 / 1024,
        "vram_total_mb": mem.total / 1024 / 1024,
        "power_w": power_w,
        "temp_c": temp_c,
        "throttle_reasons": _throttle_reasons(handle),
    }
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True, help="output JSONL path")
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--device", type=int, default=0, help="GPU index")
    args = ap.parse_args()
    pynvml.nvmlInit()
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(args.device)
        name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):
            name = name.decode("utf-8", errors="replace")
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        f = out_path.open("w", buffering=1)
        print("analysing")
        try:
            while not _stop["flag"]:
                t0 = time.time()
                try:
                    rec = {"ts": t0, "run_id": args.run_id, **sample_one(handle)}
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
            print("[nvml_sampler] stopped.", flush=True)
    finally:
        pynvml.nvmlShutdown()
if __name__ == "__main__":
    main()