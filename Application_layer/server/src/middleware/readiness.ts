import { Request, Response, NextFunction } from "express";
import { isReady } from "../services/warmup.service.js";


/** Reject every route except /ready with 503 until the upstream has warmed up. */
export function readinessGate(req: Request, res: Response, next: NextFunction): void {
  if (req.path === "/ready") return next();
  if (!isReady) {
    res.status(503).json({ error: "server_warming_up" });
    return;
  }
  next();
}
