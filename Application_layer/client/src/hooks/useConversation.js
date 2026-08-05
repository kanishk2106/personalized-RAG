import { useState, useRef, useCallback, useEffect } from "react";
import { API_BASE, CHAT_PATH } from "../config.js";
import { streamAnswer } from "../lib/stream.js";
import { normalizeResponse } from "../lib/response.js";

/** Owns the visible message thread + composer, and the ask() request. */
export function useConversation({ bootState, consoleStep, messages, setMessages, nextId }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const threadRef = useRef(null);
  const taRef = useRef(null);

  const ask = useCallback(async (text) => {
    const q = (text || "").trim();
    if (!q || bootState !== "warm" || busy) return;
    setBusy(true);
    setInput("");
    const botId = nextId.current + 1;
    setMessages((m) => [...m,
      { id: nextId.current++, role: "user", text: q },
      { id: nextId.current++, role: "bot", text: "", typing: true },
    ]);
    const set = (patch) => setMessages((m) => m.map((x) => (x.id === botId ? { ...x, ...patch } : x)));
    try {
      const res = await fetch(`${API_BASE}${CHAT_PATH}`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: q }),
      });
      if (!res.ok) throw new Error(`server ${res.status}`);
      const ct = res.headers.get("content-type") || "";
      if (ct.includes("text/event-stream") && res.body) {
        const acc = await streamAnswer(res, (a) => set({ typing: false, text: a }));
        if (!acc) set({ typing: false, text: "(empty stream from server)" });
      } else {
        const { answer, sources, trace } = normalizeResponse(await res.json());
        set({ typing: false, text: answer, sources, trace });
      }
    } catch (err) {
      set({ typing: false, text: `couldn't reach the server at ${API_BASE}${CHAT_PATH} — is it running? (${err.message})` });
    } finally {
      setBusy(false);
    }
  }, [bootState, busy, setMessages, nextId]);

  /* autoscroll the terminal as messages / console lines arrive */
  useEffect(() => {
    if (threadRef.current) threadRef.current.scrollTop = threadRef.current.scrollHeight;
  }, [messages, consoleStep]);

  /* auto-grow the composer textarea (caps, then scrolls) */
  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [input]);

  return { input, setInput, busy, ask, threadRef, taRef };
}
