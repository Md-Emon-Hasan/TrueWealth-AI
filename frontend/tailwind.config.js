/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#4361ee",
        secondary: "#3f37c9",
        accent: "#4895ef",
        dark: "#2b2d42",
        light: "#f8f9fa",
        success: "#4cc9f0",
        warning: "#f72585",
        "bg-dark": "#1a1a2e",
        "card-dark": "#16213e",
        "input-dark": "#0f3460",
      },
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
      animation: {
        'bounce-slow': 'bounce 3s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark"],
  },
}
