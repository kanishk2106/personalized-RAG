import React from "react";
import { SKILL_GROUPS } from "../data/skills.js";
import { SectionHead } from "../components/ui/SectionHead.jsx";

/** Full tech stack, grouped, every item with its brand logo (or a marker). */
export function Skills() {
  return (
    <section className="portfolio" id="skills">
      <SectionHead snum="~/skills" head="skills" />
      {SKILL_GROUPS.map((g) => (
        <div className="mb-[22px]" key={g.label}>
          <div className="pf-label">{g.label}</div>
          <div className="flex flex-wrap gap-[10px]">
            {g.items.map(([label, Icon, color]) => (
              <span className="inline-flex items-center gap-2 font-mono text-[12.5px] text-ink bg-paper/90 border-[1.5px] border-ink shadow-chip px-3 py-[7px] transition-transform hover:-translate-y-0.5" key={label}>
                {Icon
                  ? <Icon className="w-[17px] h-[17px] shrink-0" style={{ color }} aria-hidden="true" />
                  : <span className="w-2 h-2 bg-green rotate-45 shrink-0 mx-1" aria-hidden="true" />}
                {label}
              </span>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}
