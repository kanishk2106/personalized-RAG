import React from "react";
import { CONSOLE_LINES, QUICK_ASKS } from "../data/terminal.js";
import { splitThink } from "../lib/markdown.js";
import { fmtMs } from "../lib/format.js";
import { RichText } from "../components/RichText.jsx";
import { BotMessage } from "../components/BotMessage.jsx";

/** The chatbot terminal: boot log, warm-up strip, perf readout, thread, composer. */
export function Terminal({ chat, onOpenArch }) {
  const {
    bootState, consoleOpen, setConsoleOpen, consoleStep,
    messages, input, setInput, warming, warmDots, perf, ask, threadRef, taRef,
  } = chat;

  const panelCls = `panel ${bootState}`;

  return (
    <section className="botzone" id="answer">
      <div className="bot-intro">
        <div className="snum">~/ask-me</div>
        <h2>This bot can answer anything about me</h2>
        <p>Paste a job description or ask a question </p>
      </div>

      <div className="stage">
        <div className="rig">
          <div className={panelCls}>
            <div className="surge" />
            <div className="panel-head">
              <div className="who">
                <div className="winbtns"><i /><i /><i /></div>
                <div>
                  <h3>kanishk_bot — vllm@modal:~</h3>
                  <p>qwen3-8b · hybrid rag · sse</p>
                </div>
              </div>
              <div className="status">{bootState}</div>
            </div>

            <details className="bootlog" open={consoleOpen}
              onToggle={(e) => setConsoleOpen(e.currentTarget.open)}>
              <summary>
                <span className="bl-label">system boot</span>
                {bootState === "warm" && <span className="bl-tick">✓ done</span>}
              </summary>
              <div className="console open">
                {CONSOLE_LINES.map((ln, i) => (
                  <div key={i} className={`ln ${ln.cls || ""} ${i < consoleStep ? "show" : ""}`}
                    dangerouslySetInnerHTML={{ __html: ln.html }} />
                ))}
              </div>
            </details>

            {warming && (
              <div className="warmup" role="status" aria-live="polite">
                <span className="cursor" />
                <span className="wtxt">warming up the pipeline</span>
                <span className="wdots">{warmDots}</span>
                <span className="wtag">vintage cold-start · scaled from zero</span>
              </div>
            )}

            {!warming && perf && (
              <div className="perf">
                <div className="perf-head">system performance</div>
                <div className="perf-grid">
                  <span className="perf-k">cold start</span>
                  <span className="perf-v">{fmtMs(perf.coldStartMs)}</span>
                  <span className="perf-b">gpu 0 → 1 · first token{perf.cached ? " · cached" : ""}</span>
                  <span className="perf-k">model</span>
                  <span className="perf-v">qwen3-8b</span>
                  <span className="perf-b">vllm · hybrid rag · sse</span>
                </div>
              </div>
            )}

            <div className="thread" ref={threadRef}>
              {messages.map((m) =>
                m.role === "user" ? (
                  <div className="msg user" key={m.id}>
                    <span className="pr">visitor@kanishk:~$</span>{m.text}
                  </div>
                ) : (
                  <BotMessage key={m.id} m={m} splitThink={splitThink} RichText={RichText} />
                )
              )}
            </div>

            <div className="composer">
              <div className="asks">
                {QUICK_ASKS.map((qa) => (
                  <button className="ask" key={qa} onClick={() => ask(qa)}>{qa}</button>
                ))}
              </div>
              <div className="inputrow">
                <span className="prompt">&gt;</span>
                <textarea ref={taRef} rows={1} value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(input); } }}
                  placeholder={bootState === "warm" ? "ask about a project, a stack, a result…" : "powering up…"}
                  disabled={bootState !== "warm"} aria-label="Ask a question" />
                <button className="send" onClick={() => ask(input)} aria-label="Send question">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="hirebar">
        <a className="cta primary" href="#" onClick={(e) => { e.preventDefault(); onOpenArch(); }}>website architecture</a>
      </div>
    </section>
  );
}
