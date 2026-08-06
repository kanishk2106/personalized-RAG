import { promptpurify } from "promptpurify";
const REFUSAL = "I'm here to talk about Kanishk's work — feel free to ask about his projects, skills, or experience.";
/**
 * Reject prompt-injection attempts before they cost an embedding, a Pinecone
 * query, or GPU time.
 *
 * Replies as a normal SSE stream instead of an error status: the client treats
 * any non-2xx as "couldn't reach the server", so a refusal must look like an
 * ordinary answer to render correctly.
 */
export function injectionGuard(req, res, next) {
    const query = req.body?.query;
    if (typeof query !== "string")
        return next();
    // "blocked" is reserved for hard structural violations — untrusted text
    // trying to occupy an instruction channel. Softer "flagged" results pass
    // through, since the system prompt already handles off-topic questions.
    const { verdict, risks } = promptpurify.inspect(query);
    if (verdict !== "blocked")
        return next();
    console.warn(`blocked injection [${risks.map((r) => r.rule).join(", ")}]`);
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("X-Accel-Buffering", "no");
    res.write(`data: ${JSON.stringify({ token: REFUSAL })}\n\n`);
    res.write("data: [DONE]\n\n");
    res.end();
}
//# sourceMappingURL=injectionGuard.js.map