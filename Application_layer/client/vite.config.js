import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// Single source of truth: read the repo-root .env (two levels up from client/),
// the same file the Node proxy in ../server uses. "" = load ALL vars, not just VITE_*.
export default defineConfig(({ mode }) => {
  const rootEnv = loadEnv(mode, "../..", "");

  // The Node proxy listens on PORT (root .env: PORT=8080). Derive the base from it
  // so the client always follows the server's port without a separate client .env.
  const apiBase = rootEnv.VITE_API_BASE || `http://localhost:${rootEnv.PORT || 8080}`;

  return {
    plugins: [react()],
    server: {
      // Must match CORS_ORIGIN in the root .env (http://localhost:5173).
      port: 5173,
    },
    define: {
      "import.meta.env.VITE_API_BASE": JSON.stringify(apiBase),
    },
  };
});
