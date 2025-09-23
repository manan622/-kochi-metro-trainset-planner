/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        metro: {
          primary: '#1e40af',
          secondary: '#3b82f6',
          accent: '#10b981',
          danger: '#ef4444',
          warning: '#f59e0b',
          info: '#06b6d4'
        }
      }
    },
  },
  plugins: [],
}