import { tokenFromSSE } from "./sse.js";

/**
 * Read an SSE chat response, calling onText with the accumulated answer after
 * each token. Returns the final accumulated string.
 */
export async function streamAnswer(res, onText) {
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "", acc = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop();
    for (const line of lines) {
      if (!line.startsWith("data:")) continue;
      const tok = tokenFromSSE(line);
      if (tok == null) continue;
      acc += tok;
      onText(acc);
    }
  }
  return acc;
}
