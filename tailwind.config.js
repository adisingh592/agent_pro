/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        orbit: {
          bg: "#050907",
          surface: "#0A110D",
          card: "#111A14",
          cardHover: "#17241A",
          border: "rgba(156, 190, 153, 0.15)",
          borderHover: "rgba(155, 227, 74, 0.5)",
          lime: "#9BE34A",
          limeBright: "#C5FF67",
          limeDark: "#66B83D",
          limeGlow: "rgba(155, 227, 74, 0.25)",
          textPrimary: "#F1F5ED",
          textSecondary: "#A4ADA2",
          textMuted: "#6F796F",
        },
        bg: {
          main: "#050907",
          secondary: "#0A110D",
          elevated: "#111A14",
          hover: "#17241A",
        },
        border: {
          subtle: "rgba(156, 190, 153, 0.15)",
          hover: "rgba(155, 227, 74, 0.35)",
        },
        text: {
          primary: "#F1F5ED",
          secondary: "#A4ADA2",
          muted: "#6F796F",
        },
        accent: {
          DEFAULT: "#9BE34A",
          hover: "#C5FF67",
          subtle: "rgba(155, 227, 74, 0.12)",
          border: "rgba(155, 227, 74, 0.35)",
        },
        status: {
          success: "#9BE34A",
          warning: "#D48B38",
          error: "#C45A55",
        }
      },
      boxShadow: {
        'orbit-glow': '0 0 35px rgba(155, 227, 74, 0.28)',
        'orbit-glow-lg': '0 0 60px rgba(155, 227, 74, 0.35)',
        'orbit-core': '0 0 80px rgba(155, 227, 74, 0.3), inset 0 0 40px rgba(155, 227, 74, 0.15)',
        'orbit-input': '0 10px 40px -10px rgba(155, 227, 74, 0.35)',
      },
      fontFamily: {
        sans: [
          "Segoe UI Variable",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "system-ui",
          "sans-serif"
        ],
        mono: [
          "JetBrains Mono",
          "Cascadia Code",
          "Consolas",
          "monospace"
        ]
      }
    },
  },
  plugins: [],
}
