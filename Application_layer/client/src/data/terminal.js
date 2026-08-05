/* vintage terminal boot lines + quick-ask suggestions */
export const CONSOLE_LINES = [
  { html: "$ modal deploy portfolio-bot", cls: "dim" },
  { html: 'provisioning gpu <span class="dim">........</span> <span class="ok">a10g</span>' },
  { html: 'loading qwen3-8b weights <span class="dim">....</span> <span class="ok">14.2 GB</span>' },
  { html: 'vllm engine <span class="flag">--enforce-eager</span> <span class="dim">·</span> skipping cudagraph capture' },
  { html: 'health poll <span class="dim">/healthz ....</span> <span class="ok">200 OK</span>' },
  { html: '<span class="ok">✓ warm</span> <span class="dim">— first token in 412 ms</span>' },
];

export const QUICK_ASKS = ["inference experience?", "show me a rag project", "why hire him?"];
