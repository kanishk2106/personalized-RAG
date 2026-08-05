import { useEffect } from "react";

/**
 * Reveal `.scard`s as they scroll into view, and fire the terminal `boot()`
 * once the answer section is near the viewport.
 */
export function useSectionReveal(boot) {
  useEffect(() => {
    let booted = false;
    const onScroll = () => {
      document.querySelectorAll(".scard").forEach((el) => {
        if (el.getBoundingClientRect().top < window.innerHeight * 0.78) el.classList.add("lit");
      });
      const ans = document.getElementById("answer");
      if (!booted && ans && ans.getBoundingClientRect().top < window.innerHeight * 0.6) {
        booted = true;
        boot();
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, [boot]);
}
