import { Router } from "express";
import { chatController } from "../controllers/chat.controller.js";
import { retrieveController } from "../controllers/retrieve.controller.js";
import { healthController } from "../controllers/health.controller.js";
import { readyController } from "../controllers/ready.controller.js";


const router = Router();

router.post("/chat", chatController);
router.post("/retrieve", retrieveController);
router.get("/health", healthController);
router.get("/ready", readyController);

export default router;
