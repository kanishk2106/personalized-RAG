export function normalizeResponse(data) {
  const answer =
    data.answer ?? data.response ?? data.text ?? data.message ?? data.output ??
    (typeof data === "string" ? data : JSON.stringify(data));
  const rawSources = data.sources ?? data.chunks ?? data.documents ?? [];
  const sources = rawSources.slice(0, 4).map((s) => ({
    name: s.name ?? s.source ?? s.file ?? s.id ?? "chunk",
    score: (s.score ?? s.relevance ?? s.similarity ?? 0).toFixed?.(2) ?? s.score,
  }));
  const trace = data.trace ?? data.meta ?? null;
  return { answer, sources, trace };
}
