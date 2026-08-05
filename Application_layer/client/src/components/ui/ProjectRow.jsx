import React from "react";
import { CardBody } from "./CardBody.jsx";
import { SkillChips } from "./SkillChips.jsx";

/** A card + its tech stack on the outer side (used by projects & education). */
export function ProjectRow({ item }) {
  return (
    <div className="flex gap-5 items-start max-[640px]:flex-col">
      <div className="scard pf-card flex-1" id={item.anchor}>
        <div className="inline-block font-mono text-[10.5px] tracking-[.16em] text-paper bg-green px-[9px] py-[3px] mb-3">{item.file}</div>
        <h3 className="font-pix font-normal text-[23px] leading-[1.08] m-0 mb-1">{item.title}</h3>
        <div className="font-mono text-[11px] text-amber mb-3">{item.date}</div>
        <CardBody item={item} />
      </div>
      <SkillChips
        tags={item.tags}
        className="basis-[150px] shrink-0 flex flex-col gap-2 pt-1.5 max-[640px]:basis-auto max-[640px]:flex-row max-[640px]:flex-wrap max-[640px]:pt-0"
      />
    </div>
  );
}
