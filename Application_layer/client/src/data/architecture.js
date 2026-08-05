/* architecture-diagram nodes (tech/flow only — no secrets) */
import {
  SiCloudflare, SiFastapi, SiGooglecloud, SiNodedotjs, SiPostgresql, SiReact,
} from "react-icons/si";

export const ARCH_INGEST = [
  { t: "Manual document upload", s: "I add a PDF to storage" },
  { I: SiCloudflare, c: "#F38020", t: "Cloudflare R2", s: "object storage · fires an upload event" },
  { I: SiCloudflare, c: "#F38020", t: "Queue → Worker", s: "PDF_event · automatic trigger" },
  { I: SiGooglecloud, c: "#4285F4", t: "pdf_extractor · Cloud Run", s: "pdfplumber + PyTesseract OCR" },
  { I: SiCloudflare, c: "#F38020", t: "Queue → Worker", s: "Embedding_event · automatic trigger" },
  { I: SiGooglecloud, c: "#4285F4", t: "Embedding · Cloud Run", s: "Arctic Embed · page-aware chunking" },
];
/* ③ serving — how vLLM handles many users at once */
export const ARCH_SERVING = [
  { t: "Multiple users", s: "concurrent questions" },
  { I: SiNodedotjs, c: "#5FA04E", t: "Concurrency limiter", s: "≤16 in-flight · queue + warm-up" },
  { t: "vLLM on Modal", s: "connects to an A10G GPU · scales from zero" },
  { t: "Continuous batching", s: "many requests share each forward pass" },
  { t: "Paged KV cache", s: "reused across tokens & requests" },
  { t: "Qwen3-8B", s: "streams tokens back to each user" },
];
export const ARCH_STORE = [
  { t: "Pinecone", s: "dense vectors" },
  { I: SiPostgresql, c: "#4169E1", t: "PostgreSQL", s: "chunks + metadata · SQLAlchemy" },
];
export const ARCH_QUERY = [
  { I: SiReact, c: "#149ECA", t: "Browser · React 18 / Vite", s: "streams tokens over SSE" },
  { I: SiNodedotjs, c: "#5FA04E", t: "Node / Express proxy", s: "GCP auth · concurrency limiter · warm-up" },
  { I: SiFastapi, c: "#009688", t: "RAG_Generation · FastAPI", s: "embed query → hybrid retrieve → RRF fusion → rerank → prompt" },
  { t: "vLLM on Modal", s: "Qwen3-8B · A10G GPU · OpenAI-compatible" },
];
export const ARCH_RETRIEVE = [
  { t: "Pinecone", s: "dense search" },
  { I: SiPostgresql, c: "#4169E1", t: "PostgreSQL", s: "lexical search" },
  { t: "RRF + CrossEncoder", s: "fuse & rerank" },
];
export const ARCH_INFRA = ["Terraform", "GitHub Actions", "Docker", "Cloud Run", "Cloudflare"];
