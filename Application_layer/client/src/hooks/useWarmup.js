import { useEffect, useRef, useState } from "react";
import { API_BASE, CHAT_PATH, WARMUP_RETRY_MS, WARMUP_GIVEUP_MS, COLD_START_ASK } from "../config.js";

/**
 * Fire one hidden /chat on mount; the first real token means the model is warm.
 * Gated to once per browser session. Returns { warmRef, perf }.
 */
export function useWarmup() {
  const warmRef = useRef(false);
  const started = useRef(false);
  const [perf, setPerf] = useState(null);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    if (sessionStorage.getItem("coldStarted") === "1") {
      warmRef.current = true;
      setPerf({
        coldStartMs: Number(sessionStorage.getItem("coldStartMs")) || 0,
        ttftMs: Number(sessionStorage.getItem("ttftMs")) || null,
        cached: true,
      });
      return;
    }

    let cancelled = false;
    const t0 = Date.now();
    const markWarm = (sendT) => {
      const now = Date.now();
      warmRef.current = true;
      setPerf({ coldStartMs: now - t0, ttftMs: now - sendT });
      sessionStorage.setItem("coldStarted", "1");
      sessionStorage.setItem("coldStartMs", String(now - t0));
      sessionStorage.setItem("ttftMs", String(now - sendT));
    };

    const attempt = async () => {
      const sendT = Date.now();
      const res = await fetch(`${API_BASE}${CHAT_PATH}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: COLD_START_ASK }),
      });
      if (!res.ok) return false;
      const reader = res.body?.getReader();
      if (!reader) return false;
      const dec = new TextDecoder();
      let buf = "", warmed = false;
      for (;;) {
        const { value, done } = await reader.read();
        if (value) {
          buf += dec.decode(value, { stream: true });
          const lines = buf.split("\n");
          buf = lines.pop();
          for (const line of lines) {
            if (!line.startsWith("data:")) continue;
            const p = line.slice(5).trim();
            if (!p || p === "[DONE]") continue;
            let isErr = false, isTok = false;
            try {
              const j = JSON.parse(p);
              if (j.error) isErr = true;
              else if ((j.token ?? j.delta ?? j.text ?? j.content) != null) isTok = true;
            } catch { isTok = true; }
            if (isErr) { reader.cancel().catch(() => {}); return false; }
            if (isTok && !warmed) { warmed = true; markWarm(sendT); }
          }
        }
        if (done) break;
      }
      return warmed;
    };

    (async () => {
      while (!cancelled && Date.now() - t0 < WARMUP_GIVEUP_MS) {
        try { if (await attempt()) return; } catch { /* retry */ }
        if (cancelled) return;
        await new Promise((r) => setTimeout(r, WARMUP_RETRY_MS));
      }
    })();

    return () => { cancelled = true; };
  }, []);

  return { warmRef, perf };
}
