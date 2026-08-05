/* app + API configuration */
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8080";
export const CHAT_PATH = "/chat";        // POST { query } → SSE stream (Node proxy → RAG)
export const WARMUP_RETRY_MS = 3000;     // gap between cold-start attempts while proxy/model wake
export const WARMUP_GIVEUP_MS = 180000;  // stop waiting for a cold GPU after 3 min
export const COLD_START_ASK = "why should I hire Kanishk?"; // the silent first question that warms vLLM
