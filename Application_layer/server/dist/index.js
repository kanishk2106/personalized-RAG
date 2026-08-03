import express from "express";
import cors from "cors";
import { PORT, CORS_ORIGIN } from "./config.js";
import { readinessGate } from "./middleware/readiness.js";
import routes from "./routes/index.js";
import { warmUpstream } from "./services/warmup.service.js";
const app = express();
app.use(cors({
    origin: CORS_ORIGIN.split(",").map((o) => o.trim()),
    methods: ["GET", "POST"],
}));
app.use(express.json());
app.use(readinessGate);
app.use(routes);
app.listen(PORT, async () => {
    console.log(`Initilized server`);
    await warmUpstream();
});
//# sourceMappingURL=index.js.map