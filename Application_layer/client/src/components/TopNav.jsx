import React from "react";

const link = "no-underline transition-colors hover:text-ink max-[900px]:hidden";

export function TopNav() {
  return (
    <nav className="fixed top-0 inset-x-0 z-[45] flex items-center justify-between py-3.5 px-7 bg-gradient-to-b from-paper/95 to-paper/0">
      <div className="font-pix text-[26px] tracking-[.02em] flex items-center gap-2.5">
        <span className="w-3 h-3 bg-green" />KANISHK.SYS
      </div>
      <div className="flex gap-[22px] font-mono text-[12.5px] text-faded items-center">
        <a href="#experience" className={link}>./experience</a>
        <a href="#projects" className={link}>./projects</a>
        <a href="#skills" className={link}>./skills</a>
        <a href="#answer" className={link}>./ask_bot</a>
      </div>
    </nav>
  );
}
