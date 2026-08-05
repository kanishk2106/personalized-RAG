import React, { useState } from "react";
import { PORTFOLIO } from "./data/portfolio.js";
import { useChat } from "./hooks/useChat.js";
import { useSectionReveal } from "./hooks/useSectionReveal.js";
import { TopNav } from "./components/TopNav.jsx";
import { Footer } from "./components/Footer.jsx";
import { ArchModal } from "./components/ArchModal.jsx";
import { Hero } from "./sections/Hero.jsx";
import { ProofBanner } from "./sections/ProofBanner.jsx";
import { Experience } from "./sections/Experience.jsx";
import { Projects } from "./sections/Projects.jsx";
import { Skills } from "./sections/Skills.jsx";
import { Education } from "./sections/Education.jsx";
import { Terminal } from "./sections/Terminal.jsx";
import { Artifacts } from "./sections/Artifacts.jsx";

const byId = (id) => PORTFOLIO.find((s) => s.id === id);

export default function App() {
  const chat = useChat();
  const [showArch, setShowArch] = useState(false);
  useSectionReveal(chat.boot);
  const openArch = () => setShowArch(true);

  return (
    <>
      <div className="vig" aria-hidden="true" />
      <div className="crt" aria-hidden="true" />

      <TopNav />

      <div className="wrap">
        <Hero />
        <ProofBanner onOpenArch={openArch} />
        <Experience data={byId("experience")} />
        <Projects data={byId("projects")} />
        <Skills />
        <Education data={byId("credentials")} />
        <Terminal chat={chat} onOpenArch={openArch} />
        <Artifacts />
        <Footer />
      </div>

      {showArch && <ArchModal onClose={() => setShowArch(false)} />}
    </>
  );
}
