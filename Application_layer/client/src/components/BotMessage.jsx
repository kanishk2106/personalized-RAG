import React from "react";

/** One bot bubble: typing dots, or reasoning (collapsible) + answer + sources + trace. */
export function BotMessage({ m, splitThink, RichText }) {
  if (m.typing && !m.text) {
    return <div className="msg bot"><div className="typing"><span /><span /><span /></div></div>;
  }
  const { think, answer, thinking } = splitThink(m.text);
  return (
    <div className="msg bot">
      {think != null && think.trim() !== "" && (
        <details className="think">
          <summary>{thinking ? "thinking…" : "thinking"}</summary>
          <div className="think-body">{think.trim()}</div>
        </details>
      )}
      {answer !== "" && (
        <div className="body" style={m.cold ? { color: "#6E6759" } : undefined}>
          <RichText text={answer} />
        </div>
      )}
      {m.sources?.length > 0 && (
        <div className="sources">
          {m.sources.map((s, i) => (
            <span className="chip" key={i}><b>{s.score}</b> {s.name}</span>
          ))}
        </div>
      )}
      {m.trace && (
        <div className="trace">
          <span>{typeof m.trace === "string" ? m.trace : JSON.stringify(m.trace)}</span>
        </div>
      )}
    </div>
  );
}
