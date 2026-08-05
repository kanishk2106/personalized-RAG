import { useState, useRef, useCallback } from "react";
import { useWarmup } from "./useWarmup.js";
import { useBoot } from "./useBoot.js";
import { useConversation } from "./useConversation.js";

const COLD_MSG = { id: 0, role: "bot", cold: true,
  text: "…zzz. scaled to zero. your token is almost here — keep scrolling." };

/** Composes the terminal's warm-up, boot sequence, and conversation. */
export function useChat() {
  const [messages, setMessages] = useState([COLD_MSG]);
  const nextId = useRef(1);
  const addBotMessage = useCallback(
    (text) => setMessages((m) => [...m.filter((x) => !x.cold), { id: nextId.current++, role: "bot", text }]),
    [],
  );

  const { warmRef, perf } = useWarmup();
  const bootApi = useBoot({ warmRef, addBotMessage });
  const convo = useConversation({
    bootState: bootApi.bootState,
    consoleStep: bootApi.consoleStep,
    messages, setMessages, nextId,
  });

  return { messages, perf, ...bootApi, ...convo };
}
