import { Request, Response } from "express";
import { getInflight, getQueueLength } from "../helpers/limiter.js";
import { MAX_CONCURRENT, MAX_QUEUE } from "../config.js";


export function readyController(_req: Request, res: Response): void {
  res.json({
    status: "ok",
    inflight: getInflight(),
    queued: getQueueLength(),
    maxConcurrent: MAX_CONCURRENT,
    maxQueue: MAX_QUEUE,
  });
}
