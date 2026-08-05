export function tokenFromSSE(line) {
  const payload = line.slice(5).trim();
  if (!payload || payload === "[DONE]") return null;
  try {
    const j = JSON.parse(payload);
    return j.token ?? j.delta ?? j.text ?? j.content ?? "";
  } catch {
    return payload;
  }
}
