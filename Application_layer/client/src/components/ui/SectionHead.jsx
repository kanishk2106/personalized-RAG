import React from "react";

/** The shared "~/path" chip + section title used atop every portfolio section. */
export function SectionHead({ snum = "~/portfolio", head }) {
  return (
    <div className="text-center mb-11">
      <div className="inline-block font-mono text-[10.5px] tracking-[.16em] text-paper bg-green px-[9px] py-[3px] mb-3">
        {snum}
      </div>
      <h2 className="font-pix font-normal text-[46px] leading-none mt-3 mb-2">{head}</h2>
    </div>
  );
}
