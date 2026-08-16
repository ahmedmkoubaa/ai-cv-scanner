/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        leadtech: {
          red: "#F00408",
          charcoal: "#303030",
          offwhite: "#EFEFEF",
          surface: "#F8F9FA",
        },
      },
      fontFamily: {
        sans: [
          "Helvetica Neue",
          "Arial",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 4px 24px rgba(48, 48, 48, 0.08)",
      },
    },
  },
  plugins: [],
};
