/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cm-dark-bg': '#2E2E2E',
        'cm-top-bar': '#252525',
        'cm-status-bg': '#3A3A3A',
        'cm-input-bg': '#3C3C3C',
        'cm-blue': '#0078D4',
        'cm-green': '#0D8319',
        'cm-warn': '#DF2622'
      }
    },
  },
  plugins: [],
}