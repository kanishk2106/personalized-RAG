import React from "react";
import { SectionHead } from "../components/ui/SectionHead.jsx";
import { CardBody } from "../components/ui/CardBody.jsx";
import { SkillChips } from "../components/ui/SkillChips.jsx";

/** Experience as a retro timeline — cards alternate left / right, oldest first. */
export function Experience({ data }) {
  const items = data.groups[0].items.slice().reverse();
  return (
    <section className="portfolio" id="experience">
      <SectionHead head={data.head} />
      <div className="timeline">
        <div className="tl-start">2020</div>
        {items.map((it, i) => (
          <div className={`tl-item ${i % 2 === 0 ? "left" : "right"}`} key={it.file}>
            <span className="tl-node" />
            <div className="scard pf-card tl-card">
              <div className="inline-block font-mono text-[10.5px] tracking-[.16em] text-paper bg-green px-[9px] py-[3px] mb-3">{it.file}</div>
              <h3 className="font-pix font-normal text-[23px] leading-[1.08] m-0 mb-1">{it.title}</h3>
              <div className="font-mono text-[11px] text-amber mb-3">{it.date}</div>
              <CardBody item={it} />
            </div>
            <SkillChips tags={it.tags} className="tl-skills" />
          </div>
        ))}
      </div>
    </section>
  );
}
