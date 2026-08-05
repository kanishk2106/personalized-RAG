import React from "react";
import { FaArrowUpRightFromSquare } from "react-icons/fa6";
import { SiMedium, SiDevpost } from "react-icons/si";
import {
  DEMO_VIDEO_URL, DEMO_VIDEO_THUMB, BLOG_URL,
  DEVPOST_AEGIS_URL, DEVPOST_ACTIONSENSE_URL,
} from "../data/contact.js";
import { SectionHead } from "../components/ui/SectionHead.jsx";

const LINKS = [
  {
    kind: "writing · blog",
    Icon: SiMedium,
    title: "I Tried to Put a Diffusion Model on a Mac. NumPy Had Other Plans.",
    blurb:
      "Debugging the PyTorch-to-CoreML export for SSD-1B — rank reshape issues, quantization, and the compiler graph degradation that came with them.",
    cta: "read on Medium",
    href: BLOG_URL,
    wide: true,
  },
  {
    kind: "hackathon · HackFax x PatriotHacks 2026",
    Icon: SiDevpost,
    title: "Aegis — an open-source firewall for AI agents",
    blurb:
      "Intercepts every tool call an autonomous agent attempts and enforces allow / block / human-review policies before it executes.",
    cta: "view on Devpost",
    href: DEVPOST_AEGIS_URL,
  },
  {
    kind: "hackathon · Chrome Built-in AI Challenge 2025",
    Icon: SiDevpost,
    title: "ActionSense — from page to progress",
    blurb:
      "A Chrome extension running on-device AI to summarize pages, suggest next actions, and auto-group related tabs. Nothing leaves the browser.",
    cta: "view on Devpost",
    href: DEVPOST_ACTIONSENSE_URL,
  },
];

export function Artifacts() {
  return (
    <section className="portfolio">
      <SectionHead snum="~/artifacts" head="Technical Artifacts" />
      <a href={DEMO_VIDEO_URL} target="_blank" rel="noreferrer"
         className="flex gap-[18px] items-stretch mt-1.5 mb-[26px] bg-paper/90 border-[1.5px] border-ink shadow-hard2 p-3 no-underline transition hover:-translate-y-0.5 hover:shadow-hard3 max-[600px]:flex-col">
        <span className="relative basis-[240px] shrink-0 overflow-hidden border-[1.5px] border-ink bg-black max-[600px]:basis-auto max-[600px]:h-[180px]">
          <img src={DEMO_VIDEO_THUMB} alt="Chrome Built-in AI Challenge demo" loading="lazy"
               className="block w-full h-full object-cover [filter:saturate(.95)_contrast(1.02)]" />
          <span className="absolute inset-0 m-auto w-11 h-11 grid place-items-center bg-amber/90 border-2 border-paper text-paper text-[16px] rounded-full shadow-[2px_2px_0_rgba(43,38,32,.5)]">▶</span>
        </span>
        <span className="flex flex-col justify-center gap-1.5 px-1.5 py-1">
          <span className="font-mono text-[10.5px] tracking-[.14em] uppercase text-amber">featured · demo</span>
          <b className="font-pix font-normal text-[22px] leading-[1.1] text-ink">Chrome Built-in AI Challenge — Demo Walkthrough</b>
          <span className="text-[13px] text-faded leading-[1.5]">A walkthrough of what I built for Google's Chrome Built-in AI hackathon.</span>
          <span className="inline-flex items-center gap-[7px] mt-1 font-mono text-[12.5px] text-ink border-b-2 border-amber w-max pb-0.5 [&>svg]:w-3 [&>svg]:h-3">watch on YouTube <FaArrowUpRightFromSquare /></span>
        </span>
      </a>

      <div className="grid grid-cols-2 gap-[18px] max-[600px]:grid-cols-1">
        {LINKS.map(({ kind, Icon, title, blurb, cta, href, wide }) => (
          <a key={href} href={href} target="_blank" rel="noreferrer"
             className={`flex flex-col gap-1.5 bg-paper/90 border-[1.5px] border-ink shadow-hard2 p-[14px] no-underline transition hover:-translate-y-0.5 hover:shadow-hard3 ${wide ? "col-span-2 max-[600px]:col-span-1" : ""}`}>
            <span className="flex items-center gap-2 font-mono text-[10.5px] tracking-[.14em] uppercase text-amber [&>svg]:w-3.5 [&>svg]:h-3.5">
              <Icon />{kind}
            </span>
            <b className="font-pix font-normal text-[18px] leading-[1.15] text-ink">{title}</b>
            <span className="text-[13px] text-faded leading-[1.5]">{blurb}</span>
            <span className="inline-flex items-center gap-[7px] mt-auto pt-1.5 font-mono text-[12.5px] text-ink border-b-2 border-amber w-max pb-0.5 [&>svg]:w-3 [&>svg]:h-3">
              {cta} <FaArrowUpRightFromSquare />
            </span>
          </a>
        ))}
      </div>
    </section>
  );
}
