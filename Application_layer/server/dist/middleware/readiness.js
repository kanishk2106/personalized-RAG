import { isReady } from "../services/warmup.service.js";
/** Reject every route except /ready with 503 until the upstream has warmed up. */
export function readinessGate(req, res, next) {
    if (req.path === "/ready")
        return next();
    if (!isReady) {
        res.status(503).json({ error: "server_warming_up" });
        return;
    }
    next();
}
//# sourceMappingURL=readiness.js.map