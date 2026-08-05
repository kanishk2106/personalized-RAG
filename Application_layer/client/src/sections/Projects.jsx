import React from "react";
import { FaArrowUpRightFromSquare } from "react-icons/fa6";
import { PROJECT_CATS } from "../data/portfolio.js";
import { GITHUB_URL } from "../data/contact.js";
import { SectionHead } from "../components/ui/SectionHead.jsx";
import { ProjectRow } from "../components/ui/ProjectRow.jsx";

/** Projects grouped into collapsible categories, each card with its stack. */
export function Projects({ data }) {
  const items = data.groups[0].items;
  return (
    <section className="portfolio" id="projects">
      <SectionHead head={data.head} />
      {PROJECT_CATS.map((cat) => {
        const list = items.filter((it) => it.cat === cat);
        if (!list.length) return null;
        return (
          <details className="pf-cat" key={cat}>
            <summary>{cat}</summary>
            <div className="pf-catlist">
              {list.map((it) => <ProjectRow item={it} key={it.file} />)}
            </div>
          </details>
        );
      })}
      <a className="inline-flex items-center gap-2 mt-5 font-mono text-[13px] text-ink border-b-2 border-amber pb-0.5 transition-colors hover:text-amber [&>svg]:w-[13px] [&>svg]:h-[13px]"
         href={GITHUB_URL} target="_blank" rel="noreferrer">
        see more projects on GitHub <FaArrowUpRightFromSquare />
      </a>
    </section>
  );
}
