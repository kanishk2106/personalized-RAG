import { forwardHealth } from "../services/rag.service.js";
export async function healthController(_req, res) {
    try {
        const upstream = await forwardHealth();
        const data = await upstream.json();
        res.status(upstream.status).json(data);
    }
    catch (err) {
        console.error("GET /health error:", err.message);
        res.status(502).json({ error: "upstream_unreachable" });
    }
}
//# sourceMappingURL=health.controller.js.map