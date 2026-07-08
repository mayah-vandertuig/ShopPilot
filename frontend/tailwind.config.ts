import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "#E5E7EB",
        background: "#F8FAFC",
        foreground: "#0F172A",
        muted: "#F1F5F9",
        "muted-foreground": "#64748B",
        primary: "#2563EB",
        "primary-foreground": "#FFFFFF",
        card: "#FFFFFF",
        accent: "#F1F5F9",
        success: "#059669",
        warning: "#D97706",
        danger: "#DC2626",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
        "card-hover": "0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06)",
      },
      borderRadius: { lg: "0.75rem", md: "0.5rem", sm: "0.375rem" },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
export default config;
