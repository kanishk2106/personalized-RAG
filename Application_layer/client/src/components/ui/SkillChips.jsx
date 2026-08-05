import React from "react";
import { TAG_ICON } from "../../data/skills.js";

/** A row/column of tech tags, each with its brand logo where one exists. */
export function SkillChips({ tags, className }) {
  return (
    <div className={className}>
      {tags.map((t) => {
        const ic = TAG_ICON[t];
        const Icon = ic && ic[0];
        return (
          <span
            className="inline-flex items-center gap-1.5 font-mono text-[10.5px] text-faded whitespace-nowrap"
            key={t}
          >
            {Icon && <Icon className="w-[14px] h-[14px] text-ink shrink-0" style={{ color: ic[1] }} aria-hidden="true" />}
            {t}
          </span>
        );
      })}
    </div>
  );
}
