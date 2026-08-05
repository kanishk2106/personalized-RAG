import React from "react";
import { ArchNode } from "./ArchNode.jsx";
import { ARCH_INGEST, ARCH_STORE, ARCH_QUERY, ARCH_RETRIEVE, ARCH_SERVING, ARCH_INFRA } from "../data/architecture.js";

const Down = () => <div className="arch-arrow">↓</div>;

/** Architecture diagram overlay: ingestion → query → serving, tech/flow only. */
export function ArchModal({ onClose }) {
  return (
    <div className="arch-overlay" onClick={onClose}>
      <div className="arch-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Site architecture">
        <div className="arch-head">
          <span>this website · live architecture</span>
          <button className="arch-close" onClick={onClose} aria-label="Close">✕</button>
        </div>
        <div className="arch-body">
          <div className="arch-flow">
            <div className="arch-flowlabel">① ingestion — building the knowledge base</div>
            {ARCH_INGEST.map((n, i) => (
              <React.Fragment key={i}><ArchNode n={n} /><Down /></React.Fragment>
            ))}
            <div className="arch-split">{ARCH_STORE.map((n, i) => <ArchNode n={n} key={i} />)}</div>
          </div>

          <div className="arch-flow">
            <div className="arch-flowlabel">② query — live answer (what you're using now)</div>
            <ArchNode n={ARCH_QUERY[0]} /><Down />
            <ArchNode n={ARCH_QUERY[1]} /><Down />
            <ArchNode n={ARCH_QUERY[2]} />
            <div className="arch-split">{ARCH_RETRIEVE.map((n, i) => <ArchNode n={n} key={i} />)}</div>
            <Down />
            <ArchNode n={ARCH_QUERY[3]} />
            <div className="arch-arrow arch-back">↑ SSE tokens stream back to the browser</div>
          </div>

          <div className="arch-flow">
            <div className="arch-flowlabel">③ serving — vLLM under load</div>
            {ARCH_SERVING.map((n, i) => (
              <React.Fragment key={i}>
                <ArchNode n={n} />
                {i < ARCH_SERVING.length - 1 && <Down />}
              </React.Fragment>
            ))}
          </div>
        </div>
        <div className="arch-infra">
          <span>infra</span>
          {ARCH_INFRA.map((t) => <span className="arch-chip" key={t}>{t}</span>)}
        </div>
      </div>
    </div>
  );
}
