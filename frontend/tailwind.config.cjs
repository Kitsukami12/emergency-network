// tailwind.config.cjs
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B1020",
        panel: "#121A2E",
        border: "#1F2A44",
        accent: "#22D3EE",
        low: "#22C55E",
        medium: "#F59E0B",
        high: "#F97316",
        critical: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};