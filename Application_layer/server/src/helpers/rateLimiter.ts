import rateLimit from "express-rate-limit";

import { RATE_LIMIT_MAX, RATE_LIMIT_WINDOW_MS } from "../config.js";


export const chatRateLimiter = rateLimit({
  windowMs: RATE_LIMIT_WINDOW_MS,
  limit: RATE_LIMIT_MAX,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: "rate_limited" },
});
