import { Router } from "express";
import { chatController } from "../controllers/chat.controller.js";
import { readyController } from "../controllers/ready.controller.js";
import { chatRateLimiter } from "../helpers/rateLimiter.js";
import { injectionGuard } from "../middleware/injectionGuard.js";


const router = Router();

router.post("/chat", chatRateLimiter, injectionGuard, chatController);
router.get("/ready", readyController);

export default router;
