import React from "react";
import { SectionHead } from "../components/ui/SectionHead.jsx";
import { ProjectRow } from "../components/ui/ProjectRow.jsx";

/** Education / credentials — same collapsible card layout as projects. */
export function Education({ data }) {
  return (
    <section className="portfolio" id="credentials">
      <SectionHead head={data.head} />
      {data.groups.map((g) => (
        <details className="pf-cat" key={g.label}>
          <summary>{g.label}</summary>
          <div className="pf-catlist">
            {g.items.map((it) => <ProjectRow item={it} key={it.file} />)}
          </div>
        </details>
      ))}
    </section>
  );
}
