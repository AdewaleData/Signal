import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        forest: {
          DEFAULT: "#0E4A38",
          dark: "#0A3328",
          mid: "#166447",
        },
        ink: "#14201B",
        muted: "#5C6B64",
        line: "#E4E8E5",
        paper: "#F6F5F1",
        clear: "#1F7A4D",
        caution: "#C47B14",
        avoid: "#C23B2E",
        unknown: "#6B7280",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(20, 32, 27, 0.04), 0 8px 24px rgba(20, 32, 27, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
