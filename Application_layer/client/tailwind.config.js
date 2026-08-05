/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  corePlugins: { preflight: false }, // keep the existing reset while migrating
  theme: {
    extend: {
      colors: {
        paper: "#F2EDDF",
        paper2: "#EAE3D1",
        card: "#F7F3E8",
        ink: "#2B2620",
        faded: "#7A7160",
        rule: "#C8BDA3",
        green: "#2F7D46",
        greenb: "#3E9E5B",
        greens: "#E3EDDD",
        amber: "#C9821E",
        ambers: "#F5E8CC",
        red: "#C05B4D",
        cold: "#9A8F76",
        lede: "#544C3E",
        // terminal darks + greens
        term: "#1E1B16",
        term2: "#1A1712",
        term3: "#14110D",
        termInk: "#17140F",
        tgreen: "#5BC97A",
        tbody: "#9FD8AC",
        tinput: "#D8F0DC",
        tdim: "#6E6759",
        tdim2: "#5A5347",
        tline: "#4A443A",
        tmuted: "#8C8474",
      },
      fontFamily: {
        pix: ['"VT323"', "monospace"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
        sans: ['"IBM Plex Sans"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        hard1: "3px 3px 0 rgba(43,38,32,.10)",
        hard2: "5px 5px 0 rgba(43,38,32,.12)",
        hard3: "8px 8px 0 rgba(43,38,32,.14)",
        chip: "2px 2px 0 #2B2620",
      },
      keyframes: {
        blink: { "0%,49%": { opacity: 1 }, "50%,100%": { opacity: 0 } },
        typing: { "0%,40%": { opacity: ".9" }, "50%,100%": { opacity: ".2" } },
        surge: { "0%": { opacity: 0 }, "25%": { opacity: 1 }, "100%": { opacity: 0 } },
        rise: { from: { opacity: 0, transform: "translateY(6px)" }, to: { opacity: 1, transform: "none" } },
        archfade: { from: { opacity: 0 }, to: { opacity: 1 } },
      },
      animation: {
        blink: "blink 1.1s steps(1) infinite",
        typing: "typing 1s steps(1) infinite",
        surge: "surge 1s ease",
        rise: "rise .3s ease both",
        archfade: "archfade .2s ease",
      },
    },
  },
  plugins: [],
};
