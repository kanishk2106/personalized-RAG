import React from "react";

/** One box in the architecture diagram: icon (or diamond) + title + subtitle. */
export function ArchNode({ n }) {
  const Icon = n.I;
  return (
    <div className="w-full flex items-center gap-2.5 bg-paper/90 border-[1.5px] border-ink shadow-chip px-3 py-[9px]">
      {Icon
        ? <Icon className="w-5 h-5 shrink-0" style={{ color: n.c }} aria-hidden="true" />
        : <span className="w-[9px] h-[9px] bg-green rotate-45 shrink-0 mx-[5px]" aria-hidden="true" />}
      <div className="flex flex-col leading-[1.25]">
        <b className="font-mono text-[12.5px] text-ink font-semibold">{n.t}</b>
        <span className="font-mono text-[10.5px] text-faded">{n.s}</span>
      </div>
    </div>
  );
}
