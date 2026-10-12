/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sabha: {
          dark: '#0B0F19',
          navy: '#111827',
          surface: '#1A2234',
          card: '#1F293D',
          border: '#2E3A52',
          primary: '#6366F1',
          accent: '#14B8A6',
          gold: '#F59E0B',
          danger: '#EF4444',
          success: '#10B981',
          muted: '#94A3B8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
