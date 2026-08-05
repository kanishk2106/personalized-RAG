import rateLimit from "express-rate-limit";
import { RATE_LIMIT_MAX, RATE_LIMIT_WINDOW_MS } from "../config.js";
/**
 * Per-IP request budget for /chat. Distinct from limiter.ts, which caps how many
 * requests run at once; this caps how many a single client may send over time.
 */
export const chatRateLimiter = rateLimit({
    windowMs: RATE_LIMIT_WINDOW_MS,
    limit: RATE_LIMIT_MAX,
    standardHeaders: "draft-7",
    legacyHeaders: false,
    message: { error: "rate_limited" },
});
//# sourceMappingURL=rateLimiter.js.map