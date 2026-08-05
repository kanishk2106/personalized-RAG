import React from "react";

function renderInline(text, keyBase) {
  const nodes = [];
  const re = /\*\*(.+?)\*\*/g;
  let last = 0, m, k = 0;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    nodes.push(<strong key={`${keyBase}-b${k++}`}>{m[1]}</strong>);
    last = re.lastIndex;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

export function RichText({ text }) {
  const normalized = (text || "")
    .replace(/\s*\n\s*/g, "\n")          // tidy existing newlines
    .replace(/\s+(?=\d+\.\s)/g, "\n")    // break before "1. ", "2. " …
    .replace(/\s+(?=-\s\S)/g, "\n");     // break before "- " bullets
  const lines = normalized.split("\n").map((l) => l.trim()).filter(Boolean);
  return (
    <div className="rich">
      {lines.map((line, i) => {
        const num = line.match(/^(\d+)\.\s+(.*)$/);
        if (num) {
          return (
            <div className="rline li" key={i}>
              <span className="li-num">{num[1]}.</span>
              <span>{renderInline(num[2], i)}</span>
            </div>
          );
        }
        const bul = line.match(/^[-*•]\s+(.*)$/);
        if (bul) {
          return (
            <div className="rline bul" key={i}>
              <span className="li-dot">▸</span>
              <span>{renderInline(bul[1], i)}</span>
            </div>
          );
        }
        return <div className="rline" key={i}>{renderInline(line, i)}</div>;
      })}
    </div>
  );
}
