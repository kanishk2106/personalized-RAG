import { Router } from "express";
import { chatController } from "../controllers/chat.controller.js";
import { healthController } from "../controllers/health.controller.js";
import { readyController } from "../controllers/ready.controller.js";
import { chatRateLimiter } from "../helpers/rateLimiter.js";
const router = Router();
router.post("/chat", chatRateLimiter, chatController);
router.get("/health", healthController);
router.get("/ready", readyController);
export default router;
//# sourceMappingURL=index.js.map