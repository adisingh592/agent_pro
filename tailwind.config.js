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
        bg: {
          main: "#111210",
          secondary: "#181917",
          elevated: "#1E201E",
          hover: "#252824",
        },
        border: {
          subtle: "#2B2D2A",
          hover: "#3B3E39",
        },
        text: {
          primary: "#EAECE7",
          secondary: "#999E96",
          muted: "#686D66",
        },
        accent: {
          DEFAULT: "#D9A45B",
          hover: "#E7B66F",
          subtle: "rgba(217, 164, 91, 0.12)",
          border: "rgba(217, 164, 91, 0.28)",
        },
        status: {
          success: "#5A9E66",
          warning: "#D48B38",
          error: "#C45A55",
        }
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
