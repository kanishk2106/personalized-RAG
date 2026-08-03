import { RAG_SERVICE_URL, WARMUP_MAX_WAIT_MS, WARMUP_INTERVAL_MS } from "../config.js";
import { getIdToken } from "../helpers/auth.js";


export let isReady = false;
export async function warmUpstream(): Promise<void> {
  console.log("Warming up Cloud Run upstream...");
  const deadline = Date.now() + WARMUP_MAX_WAIT_MS;

  while (Date.now() < deadline) {
    try {
      const token = await getIdToken();
      const res = await fetch(`${RAG_SERVICE_URL}/health`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: AbortSignal.timeout(10_000),
      });
      if (res.ok) {
        console.log("Upstream is ready");
        isReady = true;
        return;
      }
      console.log(`upstream returned ${res.status}, retrying...`);
    } catch (err: any) {
      console.log(`upstream not ready: ${err.message}, retrying...`);
    }
    await new Promise((r) => setTimeout(r, WARMUP_INTERVAL_MS));
  }

  console.warn("Warmup timed out — starting anyway (requests may be slow)");
  isReady = true;
}
