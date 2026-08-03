import { Request, Response } from "express";
import { forwardHealth } from "../services/rag.service.js";


export async function healthController(_req: Request, res: Response): Promise<void> {
  try {
    const upstream = await forwardHealth();
    const data = await upstream.json();
    res.status(upstream.status).json(data);
  } catch (err: any) {
    console.error("GET /health error:", err.message);
    res.status(502).json({ error: "upstream_unreachable" });
  }
}
