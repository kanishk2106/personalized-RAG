import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../../..", ".env") });
export const PORT = parseInt(process.env.PORT ?? "8080", 10);
export const RAG_SERVICE_URL = process.env.RAG_SERVICE_URL;
export const CORS_ORIGIN = process.env.CORS_ORIGIN ?? "http://localhost:5173";
export const MAX_CONCURRENT = parseInt(process.env.MAX_CONCURRENT ?? "16", 10);
export const MAX_QUEUE = parseInt(process.env.MAX_QUEUE ?? "200", 10);
export const QUEUE_TIMEOUT_MS = parseInt(process.env.QUEUE_TIMEOUT_MS ?? "120000", 10);
export const RATE_LIMIT_WINDOW_MS = parseInt(process.env.RATE_LIMIT_WINDOW_MS ?? "60000", 10);
export const RATE_LIMIT_MAX = parseInt(process.env.RATE_LIMIT_MAX ?? "20", 10);
export const WARMUP_MAX_WAIT_MS = parseInt(process.env.WARMUP_MAX_WAIT_MS ?? "300000", 10);
export const WARMUP_INTERVAL_MS = parseInt(process.env.WARMUP_INTERVAL_MS ?? "5000", 10);
if (!RAG_SERVICE_URL) {
    console.error("RAG_SERVICE_URL is required");
    process.exit(1);
}
//# sourceMappingURL=config.js.map