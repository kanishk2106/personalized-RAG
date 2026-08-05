/* portfolio content — experience, projects, credentials */
export const PORTFOLIO = [
  {
    id: "experience", head: "experience",
    groups: [
      {
        label: "experience/",
        items: [
          {
            file: "2025_gmu_research_assistant_yao",
            title: "Research Assistant — Prof. Ziyu Yao",
            date: "George Mason University · USA · Sep 2025 – Dec 2025",
            bullets: [
              { k: "Inference", v: "Accelerated LLM inference with vLLM in a PyTorch and Hugging Face evaluation pipeline." },
              { k: "Evaluation", v: "Ran Agent-SafetyBench on Qwen2.5 agents to probe agent safety." },
              { k: "Safety", v: "Reduced prompt-injection risk through targeted system-prompt redesigns." },
            ],
            tags: ["vLLM", "Agent-SafetyBench", "PyTorch", "Qwen2.5"],
          },
          {
            file: "2025_gmu_research_assistant_chen",
            title: "Research Assistant — Prof. Chen Jing",
            date: "George Mason University · USA · Jan 2025 – Apr 2025",
            bullets: [
              { k: "Data Pipeline", v: "Built distributed PySpark pipelines on GCP Dataproc to process large-scale text for LLM hallucination analysis." },
              { k: "Analysis", v: "Applied FAISS embedding-based clustering to surface hallucination patterns." },
            ],
            tags: ["PySpark", "GCP Dataproc", "FAISS", "clustering"],
          },
          {
            file: "2022_2024_fidelity_swe",
            title: "Software Engineer",
            date: "Fidelity Information Services · Bengaluru, India · Jun 2022 – Aug 2024",
            bullets: [
              { k: "API", v: "Architected a sentiment analytics platform for credit analysts, serving FinBERT via FastAPI and routing requests through a Node.js REST API." },
              { k: "Database and Monitoring", v: "Designed an auditable PostgreSQL schema to retain source text, and established data-drift monitoring using Grafana and Prometheus" },
              { k: "Testing", v: "Ensured reliability through Jest and Supertest unit and integration test suites." },
              { k: "Deployment", v: "Secured the platform with JWT/OIDC role-based access control (RBAC) and automated deployment using Docker, Jenkins, CI/CD pipeline and AWS ECR" },
            ],
            tags: ["Node.js", "TypeScript", "FastAPI", "FinBERT", "PostgreSQL", "Jest", "Docker", "Jenkins", "AWS ECR"],
          },
          {
            file: "2021_vuram_dev_intern",
            title: "Software Developer Intern",
            date: "Vuram Technology Solutions · Bengaluru, India ·Aug 2021 – Feb 2022",
            bullets: [
              { k: "API", v: "Cut REST API latency with Redis caching and enforced request validation with Pydantic and OpenAPI schemas." },
              { k: "Database", v: "Improved SQL Server query performance through SQLAlchemy access patterns and indexing." },
            ],
            tags: ["Redis", "Pydantic", "OpenAPI", "SQLAlchemy"],
          },
        ],
      },
    ],
  },
  {
    id: "projects", head: "projects",
    groups: [
      {
        label: "projects/",
        items: [
          {
            file: "2026_rag_chatbot",
            anchor: "rag-chatbot",
            cat: "software development",
            title: "RAG Chatbot",
            date: "May 2026 – Jul 2026",
            bullets: [
              { k: "Frontend", v: "React 18 chat UI streaming LLM tokens over SSE with AbortController cancellation." },
              { k: "Backend", v: "Node/Express API with a promise-based concurrency limiter protecting the FastAPI vLLM service." },
              { k: "Ingestion", v: "Event-driven pipeline on Cloudflare R2/Queues and Cloud Run microservices for text extraction and chunking." },
              { k: "Data", v: "Arctic Embed S vectors in Pinecone, document chunks in PostgreSQL." },
              { k: "Inference", v: "Tuned vLLM serving for Qwen3-8B on an A10G GPU, provisioned with Terraform and GitHub Actions." },
            ],
            tags: ["React 18", "Node.js", "FastAPI", "Pinecone", "vLLM", "Terraform", "Cloudflare"],
          },
          {
            file: "2026_mar_diffusion_compression",
            cat: "ai inference",
            title: "On-Device ML: Diffusion Compression and Export",
            date: "March 2026",
            bullets: [
              { k: "Compression", v: "Compressed the SSD-1B diffusion UNet with mixed-precision quantization guided by per-block sensitivity analysis." },
              { k: "Validation", v: "Validated image quality with FID, CLIP Score and LPIPS on DrawBench." },
              { k: "Export", v: "Built a PyTorch to CoreML export pipeline with torch.jit tracing, fixing a rank-reshape that degraded the compiled graph." },
            ],
            tags: ["PyTorch", "CoreML", "SSD-1B", "Quantization", "LCM-LoRA"],
          },
          {
            file: "2026_feb_molecular_similarity",
            cat: "big data & distributed systems",
            title: "Distributed Molecular Similarity at Scale",
            date: "Feb 2026",
            bullets: [
              { k: "Pipeline", v: "Distributed PySpark pipeline on GCP Dataproc mining near-duplicate molecules with MinHash LSH over Morgan fingerprints." },
              { k: "Scale", v: "Ran approximate similarity joins across one million compounds." },
              { k: "Optimization", v: "Stabilized large shuffle stages with AQE and reduced skew through key salting." },
            ],
            tags: ["Apache Spark", "PySpark", "MinHash LSH", "GCP Dataproc"],
          },
          {
            file: "2026_feb_ai_governance",
            cat: "ai & agent governance",
            title: "Aegis — AI Agent Governance Platform",
            date: "Feb 2026",
            bullets: [
              { k: "Dashboard", v: "React dashboard with live audit feeds and a kill-switch toggle." },
              { k: "Policy Engine", v: "FastAPI three-tier policy engine (ALLOW / BLOCK / REVIEW) on MongoDB Atlas with audit logging." },
              { k: "SDK", v: "Published a pip-installable Python SDK enforcing real-time policy via decorators and tool-call guardrails, validated against LangChain and Gemini agents." },
            ],
            tags: ["React", "FastAPI", "MongoDB Atlas", "Python SDK", "LangChain"],
          },
          {
            file: "2025_dec_metaagent",
            cat: "ai & agent governance",
            title: "MetaAgent — Automated Meta-Tool Synthesis",
            date: "Dec 2025",
            bullets: [
              { k: "Agent", v: "LangChain and LangGraph agent that mines tool-call histories to synthesize reusable meta-tools." },
              { k: "Impact", v: "Cut agent workflow latency substantially by reusing the synthesized meta-tools." },
              { k: "Integration", v: "Integrated Gemini on Vertex AI with Google Cloud's remote MCP server to register tools." },
            ],
            tags: ["LangChain", "LangGraph", "Gemini", "Vertex AI", "MCP"],
          },
          {
            file: "langsmith_sdk_pr_31802",
            cat: "open source",
            title: "LangSmith SDK — Contributor",
            date: "LangChain#31802 · Oct 2025",
            bullets: [
              { k: "Contribution", v: "Contributed an OSS PR to the LangSmith SDK, improving the reliability of LLM evaluation pipelines." },
              { k: "Fix", v: "Eliminated silent feedback-config failures with stricter Pydantic schema validation." },
            ],
            tags: ["LangSmith", "Pydantic", "open source"],
          },
        ],
      },
    ],
  },
  {
    id: "credentials", head: "education",
    groups: [
      {
        label: "education/",
        items: [
          {
            file: "ms_george_mason",
            title: "M.S. Computer Science (Machine Learning)",
            date: "George Mason University · Aug 2024 – May 2026 · GPA 3.8",
            what: "Coursework: Advanced Natural Language Processing, Generative Deep Learning, Mining Massive Datasets, Systems Programming (C).",
            tags: ["MS CS", "Machine Learning", "GPA 3.8"],
          },
          {
            file: "be_kumaraguru",
            title: "B.E. Computer Science",
            date: "Kumaraguru College of Technology · Aug 2018 – May 2022",
            what: "Bachelor of Engineering in Computer Science.",
            tags: ["BE CS"],
          },
        ],
      },
    ],
  },
];

export const PROJECT_CATS = [
  "software development",
  "ai inference",
  "ai & agent governance",
  "big data & distributed systems",
  "open source",
];
