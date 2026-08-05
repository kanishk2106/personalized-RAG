import { useState, useRef, useCallback, useEffect } from "react";
import { WARMUP_GIVEUP_MS } from "../config.js";
import { CONSOLE_LINES } from "../data/terminal.js";

const AWAKE = "awake — your token arrived, that's what woke me. I'm connected to the live RAG pipeline; ask me anything about Kanishk's work.";
const OFFLINE = "the model didn't return a first token in time — the GPU may still be cold or the server unreachable. you can still try a question.";

/** Plays the vintage boot console, then flips to "warm" once warmRef is set. */
export function useBoot({ warmRef, addBotMessage }) {
  const [bootState, setBootState] = useState("cold"); // cold | booting | warm
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [consoleStep, setConsoleStep] = useState(0);
  const [warming, setWarming] = useState(false);
  const [warmDots, setWarmDots] = useState("");
  const started = useRef(false);

  const boot = useCallback(() => {
    if (started.current) return;
    started.current = true;
    setBootState("booting");
    setConsoleOpen(true);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const step = reduce ? 60 : 520;
    CONSOLE_LINES.forEach((_, i) => setTimeout(() => {
      setConsoleStep(i + 1);
      if (i !== CONSOLE_LINES.length - 1) return;
      const goLive = () => {
        setWarming(false);
        setBootState("warm");
        addBotMessage(AWAKE);
        setTimeout(() => setConsoleOpen(false), 2600);
      };
      if (warmRef.current) return goLive();
      setWarming(true);
      const poll = setInterval(() => { if (warmRef.current) { clearInterval(poll); goLive(); } }, 400);
      setTimeout(() => {
        if (warmRef.current) return;
        clearInterval(poll);
        setWarming(false);
        setBootState("warm");
        setConsoleOpen(false);
        addBotMessage(OFFLINE);
      }, WARMUP_GIVEUP_MS);
    }, 300 + i * step));
  }, [warmRef, addBotMessage]);

  /* animate the "warming up" dots while we wait */
  useEffect(() => {
    if (!warming) { setWarmDots(""); return; }
    const id = setInterval(() => setWarmDots((d) => (d.length >= 6 ? "" : d + ".")), 260);
    return () => clearInterval(id);
  }, [warming]);

  return { bootState, consoleOpen, setConsoleOpen, consoleStep, warming, warmDots, boot };
}
