import { acquire, release } from "../helpers/limiter.js";
import { forwardRetrieve } from "../services/rag.service.js";
export async function retrieveController(req, res) {
    try {
        await acquire();
    }
    catch (err) {
        const status = err.message === "queue_full" ? 503 : 504;
        res.status(status).json({ error: err.message });
        return;
    }
    try {
        const upstream = await forwardRetrieve(req.body);
        const data = await upstream.json();
        res.status(upstream.status).json(data);
    }
    catch (err) {
        console.error("POST /retrieve error:", err.message);
        res.status(502).json({ error: "upstream_error" });
    }
    finally {
        release();
    }
}
//# sourceMappingURL=retrieve.controller.js.map