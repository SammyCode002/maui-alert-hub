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
        // Ocean blues
        ocean: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#0891b2',
          600: '#0e7490',
          700: '#155e75',
          800: '#164e63',
          900: '#0c3547',
        },
        // Volcanic earth tones
        lava: {
          50: '#fef7ee',
          100: '#fdecd3',
          200: '#fad5a5',
          300: '#f6b76d',
          400: '#f19133',
          500: '#ee7712',
          600: '#df5c08',
          700: '#b94309',
          800: '#93360f',
          900: '#772f10',
        },
        // Alert colors
        alert: {
          extreme: '#dc2626',
          severe: '#ea580c',
          moderate: '#d97706',
          minor: '#65a30d',
        },
        // Road status colors
        road: {
          open: '#16a34a',
          closed: '#dc2626',
          restricted: '#d97706',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        display: ['"Outfit"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
