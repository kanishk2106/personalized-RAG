/* tech-stack data with brand icons */
import {
  SiApachespark, SiCloudflare, SiDocker, SiExpress, SiFastapi, SiGithubactions, SiGooglecloud, SiGooglegemini, SiGrafana, SiHuggingface, SiJavascript, SiJenkins, SiJest, SiKubernetes, SiLangchain, SiNodedotjs, SiOpenapiinitiative, SiOpentelemetry, SiPostgresql, SiPrometheus, SiPydantic, SiPytest, SiPython, SiPytorch, SiReact, SiRedis, SiScikitlearn, SiSqlalchemy, SiTailwindcss, SiTerraform, SiTypescript, SiVite,
} from "react-icons/si";

export const TAG_ICON = {
  "Python": [SiPython, "#3776AB"],
  "TypeScript": [SiTypescript, "#3178C6"],
  "React": [SiReact, "#149ECA"],
  "React 18": [SiReact, "#149ECA"],
  "Node.js": [SiNodedotjs, "#5FA04E"],
  "FastAPI": [SiFastapi, "#009688"],
  "PyTorch": [SiPytorch, "#EE4C2C"],
  "LangChain": [SiLangchain, "#1C3C3C"],
  "Hugging Face": [SiHuggingface, "#F09B0A"],
  "PySpark": [SiApachespark, "#E25A1C"],
  "Apache Spark": [SiApachespark, "#E25A1C"],
  "GCP Dataproc": [SiGooglecloud, "#4285F4"],
  "PostgreSQL": [SiPostgresql, "#4169E1"],
  "Docker": [SiDocker, "#2496ED"],
  "Kubernetes": [SiKubernetes, "#326CE5"],
  "Terraform": [SiTerraform, "#7B42BC"],
  "Jenkins": [SiJenkins, "#D33833"],
  "Jest": [SiJest, "#C21325"],
  "Redis": [SiRedis, "#DC382D"],
  "Pydantic": [SiPydantic, "#E92063"],
  "OpenAPI": [SiOpenapiinitiative, "#6BA539"],
  "SQLAlchemy": [SiSqlalchemy, "#D71F00"],
};

export const LIVE_STACK = [
  [SiReact, "React 18", "#149ECA"],
  [SiVite, "Vite", "#646CFF"],
  [SiNodedotjs, "Node.js", "#5FA04E"],
  [SiFastapi, "FastAPI", "#009688"],
  [null, "vLLM", null],
  [null, "Pinecone", null],
  [SiPostgresql, "PostgreSQL", "#4169E1"],
  [SiDocker, "Docker", "#2496ED"],
  [SiTerraform, "Terraform", "#7B42BC"],
  [SiGooglecloud, "GCP Cloud Run", "#4285F4"],
  [SiCloudflare, "Cloudflare", "#F38020"],
];

export const SKILL_GROUPS = [
  { label: "languages", items: [
    ["Python", SiPython, "#3776AB"], ["TypeScript", SiTypescript, "#3178C6"],
    ["JavaScript", SiJavascript, "#E8A400"], ["SQL", null, null],
  ]},
  { label: "frontend", items: [
    ["React", SiReact, "#149ECA"], ["Vite", SiVite, "#646CFF"],
    ["Tailwind CSS", SiTailwindcss, "#06B6D4"], ["Server-Sent Events", null, null],
  ]},
  { label: "backend & apis", items: [
    ["Node.js", SiNodedotjs, "#5FA04E"], ["Express", SiExpress, "#111111"],
    ["FastAPI", SiFastapi, "#009688"], ["Pydantic", SiPydantic, "#E92063"],
    ["OpenAPI", SiOpenapiinitiative, "#6BA539"], ["OIDC / JWT", null, null],
  ]},
  { label: "ai & llms", items: [
    ["PyTorch", SiPytorch, "#EE4C2C"], ["Hugging Face", SiHuggingface, "#F09B0A"],
    ["LangChain", SiLangchain, "#1C3C3C"], ["LangGraph", null, null],
    ["scikit-learn", SiScikitlearn, "#F7931E"],
    ["Gemini", SiGooglegemini, "#8E75B2"], ["vLLM", null, null],
    ["RAG", null, null], ["Quantization / LoRA", null, null],
  ]},
  { label: "data & distributed", items: [
    ["Apache Spark", SiApachespark, "#E25A1C"], ["Pinecone", null, null],
    ["PostgreSQL", SiPostgresql, "#4169E1"], ["SQLAlchemy", SiSqlalchemy, "#D71F00"],
    ["Redis", SiRedis, "#DC382D"],
  ]},
  { label: "cloud & devops", items: [
    ["AWS", null, null], ["GCP", SiGooglecloud, "#4285F4"], ["Cloudflare", SiCloudflare, "#F38020"],
    ["Docker", SiDocker, "#2496ED"],
    ["Terraform", SiTerraform, "#7B42BC"], ["GitHub Actions", SiGithubactions, "#2088FF"],
    ["Modal", null, null], ["Prometheus", SiPrometheus, "#E6522C"],
    ["Grafana", SiGrafana, "#F46800"], ["OpenTelemetry", SiOpentelemetry, "#425CC7"],
  ]},
  { label: "testing", items: [
    ["Jest", SiJest, "#C21325"], ["pytest", SiPytest, "#0A9EDC"], ["Supertest", null, null],
  ]},
];
