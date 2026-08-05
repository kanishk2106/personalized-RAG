import React from "react";

export function Footer() {
  return (
    <footer className="relative z-[3] border-t-[1.5px] border-ink pt-[22px] px-8 pb-[30px] flex justify-between gap-5 flex-wrap font-mono text-[12px] text-faded bg-paper2">
      <span>© 2026 kanishk — this page runs the pipeline it describes. cold-starts included.</span>
      <div className="flex gap-5">
        <a href="#" className="no-underline hover:text-green">github</a>
        <a href="#" className="no-underline hover:text-green">linkedin</a>
        <a href="#" className="no-underline hover:text-green">email</a>
      </div>
    </footer>
  );
}
