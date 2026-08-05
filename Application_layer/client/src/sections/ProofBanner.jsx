import React from "react";
import { LIVE_STACK } from "../data/skills.js";

export function ProofBanner({ onOpenArch }) {
  return (
    <section className="block min-h-0 max-w-[920px] mx-auto py-[4vh] px-6 pb-[2vh] relative z-[2] text-center">
      <div className="flex gap-2.5 items-start text-left bg-term border-[1.5px] border-ink shadow-hard2 px-[18px] py-3.5 font-mono">
        <span className="text-amber text-[12px] font-semibold shrink-0 tracking-[.04em]">[SYSTEM_NOTE]</span>
        <span className="text-tbody text-[13px] leading-[1.6]">
          This site is a functional deployment. You are interacting with a live hybrid RAG
          pipeline built on my core stack — Navigate below to interact with the live RAG inference engine.
        </span>
      </div>
      <div className="font-mono text-[11px] tracking-[.14em] uppercase text-faded mt-5 mb-3"> Tech Stack used</div>
      <div className="flex flex-wrap justify-center gap-2.5">
        {LIVE_STACK.map(([Icon, label, color]) => (
          <div className="inline-flex items-center gap-2 bg-paper/85 border-[1.5px] border-ink shadow-chip px-3 py-[7px] font-mono text-[12px] text-ink transition hover:-translate-y-0.5" key={label}>
            {Icon
              ? <Icon className="w-[17px] h-[17px] shrink-0" style={{ color }} aria-hidden="true" />
              : <span className="w-2 h-2 bg-green shrink-0 rotate-45" aria-hidden="true" />}
            <span>{label}</span>
          </div>
        ))}
      </div>
      <a className="inline-block mt-[22px] font-mono text-[13px] text-ink border-b-2 border-amber pb-0.5 transition-colors hover:text-amber"
         href="#rag-chatbot" onClick={(e) => { e.preventDefault(); onOpenArch(); }}>
        → Know more about Website Architecture
      </a>
    </section>
  );
}
