export function splitThink(text) {
  if (!text) return { think: null, answer: text || "", thinking: false };
  const open = text.indexOf("<think>");
  if (open === -1) return { think: null, answer: text, thinking: false };
  const before = text.slice(0, open);
  const close = text.indexOf("</think>", open);
  if (close === -1) {
    // reasoning still streaming — no answer yet
    return { think: text.slice(open + 7), answer: before, thinking: true };
  }
  const think = text.slice(open + 7, close);
  const answer = (before + text.slice(close + 8)).replace(/^\s+/, "");
  return { think, answer, thinking: false };
}
