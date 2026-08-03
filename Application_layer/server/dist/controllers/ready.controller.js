import { getInflight, getQueueLength } from "../helpers/limiter.js";
import { MAX_CONCURRENT, MAX_QUEUE } from "../config.js";
export function readyController(_req, res) {
    res.json({
        status: "ok",
        inflight: getInflight(),
        queued: getQueueLength(),
        maxConcurrent: MAX_CONCURRENT,
        maxQueue: MAX_QUEUE,
    });
}
//# sourceMappingURL=ready.controller.js.map