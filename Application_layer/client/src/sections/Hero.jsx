import React from "react";
import { FaGithub, FaLinkedin, FaPhone } from "react-icons/fa6";
import profilePic from "../profile.jpg";
import { GITHUB_URL, GITHUB_USER, LINKEDIN_URL, LINKEDIN_USER, PHONE, PHONE_DISPLAY } from "../data/contact.js";

const socialLink =
  "inline-flex items-center gap-[7px] font-mono text-[12px] text-ink border-[1.5px] border-ink shadow-chip bg-paper px-[11px] py-1.5 transition hover:-translate-y-0.5 hover:bg-white [&>svg]:w-[15px] [&>svg]:h-[15px]";
const notch =
  "before:content-[''] before:absolute before:w-2.5 before:h-2.5 before:bg-paper before:border-[1.5px] before:border-ink before:-top-1.5 before:-left-1.5 " +
  "after:content-[''] after:absolute after:w-2.5 after:h-2.5 after:bg-paper after:border-[1.5px] after:border-ink after:-bottom-1.5 after:-right-1.5";

export function Hero() {
  return (
    <section className="flex flex-col items-center justify-start min-h-0 text-center pt-[9vh] pb-[5vh] relative">
      <div className="flex gap-[26px] items-start justify-center flex-wrap w-full max-w-[1060px] mx-auto">
        <div className={`relative flex-[1_1_460px] max-w-[640px] bg-paper/[.82] backdrop-blur-[6px] border-[1.5px] border-ink p-[30px_38px_26px] shadow-hard3 ${notch}`}>
          <div className="font-mono text-[11px] tracking-[.14em] text-green mb-3.5">Software Developer · Applied AI · USA </div>
          <h1 className="font-pix font-normal tracking-[.01em] text-[clamp(44px,6vw,80px)] leading-[.98] m-0 mb-3.5">
            About <em className="not-italic text-green">me</em>
            <span className="inline-block w-[.5em] bg-green animate-blink">&nbsp;</span>
          </h1>
          <p className="text-[18px] text-lede max-w-[56ch] mx-auto">
            Software Engineer focused on backend architecture and AI integration. I build applications using Node.js (TypeScript, JavaScript), FastAPI (Python) and React for frontend. For AI pipelines, I use vLLM for GPU acceleration and LLM serving
          </p>
          <div className="flex gap-2.5 flex-wrap mt-4">
            <a href={GITHUB_URL} target="_blank" rel="noreferrer" aria-label="GitHub" className={socialLink}><FaGithub /><span>{GITHUB_USER}</span></a>
            <a href={LINKEDIN_URL} target="_blank" rel="noreferrer" aria-label="LinkedIn" className={socialLink}><FaLinkedin /><span>{LINKEDIN_USER}</span></a>
            <a href={`tel:${PHONE}`} aria-label="Phone" className={socialLink}><FaPhone /><span>{PHONE_DISPLAY}</span></a>
          </div>
        </div>
        <aside className="basis-[234px] shrink-0 flex flex-col gap-3.5 max-[640px]:basis-full max-[640px]:max-w-[360px]">
          <div className="bg-paper/85 border-[1.5px] border-ink shadow-hard3 p-[7px] relative">
            <img src={profilePic} alt="Kanishk" className="block w-full h-auto [filter:grayscale(.12)_contrast(1.03)_sepia(.05)]" />
          </div>
          <div className="bg-paper/85 border-[1.5px] border-ink shadow-hard2 px-3.5 py-[11px] text-left">
            <b className="block font-mono text-[13px] font-semibold text-ink tracking-[.01em]">Software Engineer</b>
            <span className="font-mono text-[11px] text-faded">2+ years of experience</span>
          </div>
          <div className="bg-paper/85 border-[1.5px] border-ink shadow-hard2 px-3.5 py-[11px] text-left">
            <b className="block font-mono text-[13px] font-semibold text-ink tracking-[.01em]">M.S. Computer Science</b>
            <span className="font-mono text-[11px] text-faded">George Mason University</span>
          </div>
        </aside>
      </div>
    </section>
  );
}
