import express from "express";
import cors from "cors";

import { PORT, CORS_ORIGIN } from "./config.js";
import { readinessGate } from "./middleware/readiness.js";
import routes from "./routes/index.js";
import { warmUpstream } from "./services/warmup.service.js";


const app = express();

// Cloud Run terminates at a front-end proxy; without this req.ip is the LB address
// and every visitor would share a single rate-limit bucket.
app.set("trust proxy", 1);

app.use(
  cors({
    origin: CORS_ORIGIN.split(",").map((o) => o.trim()),
    methods: ["GET", "POST"],
  })
);
app.use(express.json());
app.use(readinessGate);
app.use(routes);

app.listen(PORT, async () => {
  console.log(`Initilized server`);
  await warmUpstream();
});
