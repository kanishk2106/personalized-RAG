import { Request, Response, NextFunction } from "express";
import { promptpurify } from "promptpurify";


const REFUSAL =
  "I'm here to talk about Kanishk's work — feel free to ask about his projects, skills, or experience.";


export function injectionGuard(req: Request, res: Response, next: NextFunction): void {
  const query = req.body?.query;
  if (typeof query !== "string") return next();


  const { verdict, risks } = promptpurify.inspect(query);
  if (verdict !== "blocked") return next();

  console.warn(`blocked injection [${risks.map((r) => r.rule).join(", ")}]`);

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("X-Accel-Buffering", "no");
  res.write(`data: ${JSON.stringify({ token: REFUSAL })}\n\n`);
  res.write("data: [DONE]\n\n");
  res.end();
}
