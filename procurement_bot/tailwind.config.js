/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../ai-services/DesignSystem/**/*.{js,jsx}", // Inkludera designsystemet
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

