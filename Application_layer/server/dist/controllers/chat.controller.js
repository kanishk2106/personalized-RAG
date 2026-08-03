import { acquire, release } from "../helpers/limiter.js";
import { forwardChat } from "../services/rag.service.js";
export async function chatController(req, res) {
    try {
        await acquire();
    }
    catch (err) {
        const status = err.message === "queue_full" ? 503 : 504;
        res.status(status).json({ error: err.message });
        return;
    }
    try {
        const upstream = await forwardChat(req.body);
        if (!upstream.ok) {
            res.status(upstream.status).json({ error: `upstream ${upstream.status}` });
            return;
        }
        res.setHeader("Content-Type", "text/event-stream");
        res.setHeader("Cache-Control", "no-cache");
        res.setHeader("X-Accel-Buffering", "no");
        res.setHeader("Connection", "keep-alive");
        res.flushHeaders();
        const reader = upstream.body?.getReader();
        if (!reader) {
            res.end();
            return;
        }
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done)
                break;
            res.write(decoder.decode(value, { stream: true }));
        }
        res.end();
    }
    catch (err) {
        console.error("POST /chat error:", err.message);
        if (!res.headersSent) {
            res.status(502).json({ error: "upstream_error" });
        }
        else {
            res.end();
        }
    }
    finally {
        release();
    }
}
//# sourceMappingURL=chat.controller.js.map